import json
import logging
import multiprocessing
import os
import subprocess
import time
import warnings
from typing import Dict, List

from pyfilebrowser.modals import models
from pyfilebrowser.proxy import proxy_server, proxy_settings
from pyfilebrowser.squire import download, steward, struct


class FileBrowser:
    """Object to handle the filebrowser streaming.

    >>> FileBrowser

    """

    def __init__(self, **kwargs):
        """Instantiates the object.

        Keyword Args:
            logger: Bring your own logger.
        """
        self.env = steward.EnvConfig(**kwargs)
        # Reset to stdout, so the log output stream can be controlled with custom logging
        self.env.config_settings.server.log = models.Log.stdout
        self.logger = kwargs.get('logger',
                                 steward.default_logger(self.env.config_settings.server.log == models.Log.file))
        github = download.GitHub(**kwargs)
        if not os.path.isfile(download.executable.filebrowser_bin):
            download.binary(logger=self.logger, github=github)
        self.proxy_engine: multiprocessing.Process | None = None

    def exit_process(self) -> None:
        """Deletes the database file, and all the subtitles that were created by this application."""
        if os.path.isfile(download.executable.filebrowser_db):
            self.logger.info("Removing database %s", download.executable.filebrowser_db)
            os.remove(download.executable.filebrowser_db)
        if self.proxy_engine:
            self.logger.info("Stopping proxy service")
            self.proxy_engine.terminate()
            for i in range(5):
                if self.proxy_engine.is_alive():
                    self.proxy_engine.kill()
                else:
                    self.logger.info("Daemon process terminated in %s attempt", steward.ordinal(i))
                    self.proxy_engine.close()
                    break
                time.sleep(1e-1)  # 0.1s
            else:
                warnings.warn(
                    f"Failed to terminate daemon process PID: [{self.proxy_engine.pid}] within 5 attempts",
                    RuntimeWarning
                )

    def run_subprocess(self, arguments: List[str] = None, failed_msg: str = None, stdout: bool = False) -> None:
        """Run ``filebrowser`` commands as subprocess.

        Args:
            arguments: Arguments to pass to the binary.
            failed_msg: Failure message in case of bad return code.
            stdout: Boolean flag to show/hide standard output.
        """
        arguments.insert(0, "")
        command = os.path.join(os.getcwd(), download.executable.filebrowser_bin) + " ".join(arguments)
        process = subprocess.Popen(command, shell=True,
                                   universal_newlines=True, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            if stdout:
                for line in process.stdout:
                    self.logger.info(steward.remove_prefix(line))
            process.wait()
            for line in process.stderr:
                self.logger.warning(steward.remove_prefix(line))
            assert process.returncode == 0, failed_msg
        except KeyboardInterrupt:
            if process.poll() is None:
                for line in process.stdout:
                    self.logger.info(steward.remove_prefix(line))
                process.terminate()
            self.exit_process()

    def create_users(self) -> Dict[str, str]:
        """Creates the JSON file for user profiles.

        Returns:
            Dict[str, str]:
            Authentication map provided as environment variables.
        """
        final_settings = []
        user_profiles = self.env.user_profiles or self.env.load_user_profiles()
        auth_map = {}
        for idx, profile in enumerate(user_profiles):
            if profile.authentication.admin:
                profile.perm = models.admin_perm()
            else:
                profile.perm = models.default_perm()
            auth_map[profile.authentication.username] = profile.authentication.password
            hashed_password = steward.hash_password(profile.authentication.password)
            assert steward.validate_password(profile.authentication.password, hashed_password), "Validation failed!"
            profile.authentication.password = hashed_password
            model_settings = json.loads(profile.model_dump_json())
            user_settings = {'id': idx + 1}
            model_settings['authentication'].pop('admin', None)  # remove custom 'admin' model within authentication
            user_settings.update(model_settings['authentication'])  # insert custom 'authentication' model into new dict
            model_settings.pop('authentication', None)  # remove custom 'authentication' model from 'model_settings'
            user_settings.update(model_settings)  # insert cleaned 'model_settings' into new dict 'user_settings'
            final_settings.append(user_settings)
        with open(steward.fileio.users, 'w') as file:
            json.dump(final_settings, file, indent=4)
            file.flush()
        return auth_map

    def create_config(self, proxy: bool) -> None:
        """Creates the JSON file for configuration.

        Args:
            proxy: Boolean flag to enable proxy.
        """
        if proxy:
            self.env.config_settings.settings.authMethod = "json"
            self.env.config_settings.settings.authHeader = ""
        if str(self.env.config_settings.settings.branding.files) == ".":
            self.env.config_settings.settings.branding.files = ""
        self.env.config_settings.server.port = str(self.env.config_settings.server.port)
        with warnings.catch_warnings(action="ignore"):
            final_settings = steward.remove_trailing_underscore(json.loads(self.env.config_settings.model_dump_json()))
        with open(steward.fileio.config, 'w') as file:
            json.dump(final_settings, file, indent=4)
            file.flush()

    def import_config(self, proxy: bool) -> None:
        """Imports the configuration file into filebrowser.

        Args:
            proxy: Boolean flag to enable proxy.
        """
        self.logger.info("Importing configuration from %s", steward.fileio.config)
        self.create_config(proxy)
        assert os.path.isfile(steward.fileio.config), f"{steward.fileio.config!r} doesn't exist"
        self.run_subprocess(["config", "import", steward.fileio.config],
                            "Failed to import configuration")

    def import_users(self) -> Dict[str, str]:
        """Imports the user profiles into filebrowser.

        Returns:
            Dict[str, str]:
            Authentication map provided as environment variables.
        """
        self.logger.info("Importing user profiles from %s", steward.fileio.users)
        auth_map = self.create_users()
        assert os.path.isfile(steward.fileio.users), f"{steward.fileio.users!r} doesn't exist"
        self.run_subprocess(["users", "import", steward.fileio.users],
                            "Failed to import user profiles")
        return auth_map

    def background_tasks(self, auth_map: Dict[str, str], proxy: bool) -> None:
        """Initiates the proxy engine and subtitles' format conversion as background tasks.

        Args:
            auth_map: Authentication map provided as environment variables.
            proxy: Boolean flag to enable proxy.
        """
        if proxy:
            assert proxy_settings.port != int(self.env.config_settings.server.port), \
                f"\n\tProxy server can't run on the same port [{proxy_settings.port}] as the server!!"
            log_config = struct.LoggerConfig(self.logger).get()
            if proxy_settings.debug:
                log_config = struct.update_log_level(log_config, logging.DEBUG)
            # noinspection HttpUrlsUsage
            self.proxy_engine = multiprocessing.Process(
                target=proxy_server, daemon=True,
                args=(f"http://{self.env.config_settings.server.address}:{self.env.config_settings.server.port}",
                      log_config, auth_map)
            )
            self.proxy_engine.start()

    def start(self, proxy: bool = False) -> None:
        """Handler for all the functions above.

        Args:
            proxy: Boolean flag to enable proxy.
        """
        if os.path.isfile(download.executable.filebrowser_db):
            os.remove(download.executable.filebrowser_db)
        self.import_config(proxy)
        self.background_tasks(self.import_users(), proxy)
        self.run_subprocess([], "Failed to run the server", True)
