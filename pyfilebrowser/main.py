import json
import logging
import multiprocessing
import os
import socket
import subprocess
import time
import warnings
from typing import Dict, List

import yaml

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
            proxy: Boolean flag to enable proxy.
            extra_env: JSON or YAML filename to load extra settings.

        See Also:
            - ``extra_env`` is a feature to load additional configuration settings to the filebrowser server.
            - This is useful when you want to load custom settings that are not available in the default configuration.
            - The file should be a JSON or YAML file with the following structure:
                - The key should be the same as the one in configuration settings of the filebrowser.
                  Options: (``server``, ``auther``, ``settings``)
                - The JSON/YAML structure should follow the same parent key-value mapping.
                - The file should be placed in the same directory as the script that invokes the filebrowser.
                - The filename should be passed as a keyword argument to the ``FileBrowser`` object.
                  (By default, searched for ``extra.json`` in the current directory)
        """
        self.env = steward.EnvConfig(**kwargs)
        self.logger = kwargs.get(
            "logger",
            steward.default_logger(
                self.env.config_settings.server.log == models.Log.file
            ),
        )
        # Reset to stdout, so the log output stream can be controlled with custom logging
        self.env.config_settings.server.log = models.Log.stdout
        github = download.GitHub(**kwargs)
        if not os.path.isfile(download.executable.filebrowser_bin):
            download.binary(logger=self.logger, github=github)
        self.proxy_engine: multiprocessing.Process | None = None
        self.proxy = kwargs.get("proxy")
        self.extra_env = kwargs.get("extra_env", "extra.json")
        assert self.proxy is None or isinstance(
            self.proxy, bool
        ), f"\n\tproxy flag should be a boolean value, received {type(self.proxy).__name__!r}"

    def cleanup(self, log: bool = True) -> None:
        """Removes the config and proxy database."""
        try:
            os.remove(download.executable.filebrowser_db)
            self.logger.info(
                "Removed config database %s", download.executable.filebrowser_db
            )
        except FileNotFoundError as warn:
            self.logger.warning(warn) if log else None
        try:
            os.remove(proxy_settings.database)
            self.logger.info("Removed proxy database %s", proxy_settings.database)
        except FileNotFoundError as warn:
            self.logger.warning(warn) if self.proxy_engine and log else None
        try:
            os.remove(steward.fileio.config)
            os.remove(steward.fileio.users)
            self.logger.info("Removed config and user profiles' JSON files")
        except FileNotFoundError as warn:
            self.logger.warning(warn) if log else None

    def exit_process(self) -> None:
        """Deletes the database file, and all the subtitles that were created by this application."""
        if self.proxy_engine:
            self.proxy_engine.join(timeout=3)  # Gracefully terminate the proxy server
            for i in range(1, 6):
                if self.proxy_engine.is_alive():
                    self.proxy_engine.terminate()
                else:
                    self.logger.debug(
                        "Daemon process terminated in %s attempt", steward.ordinal(i)
                    )
                    self.proxy_engine.close()
                    break
                time.sleep(1e-1)  # 0.1s
            else:
                warnings.warn(
                    f"Failed to terminate daemon process PID: [{self.proxy_engine.pid}] within 5 attempts",
                    RuntimeWarning,
                )
        self.cleanup()

    def run_subprocess(
        self, arguments: List[str] = None, failed_msg: str = None, stdout: bool = False
    ) -> None:
        """Run ``filebrowser`` commands as subprocess.

        Args:
            arguments: Arguments to pass to the binary.
            failed_msg: Failure message in case of bad return code.
            stdout: Boolean flag to show/hide standard output.
        """
        arguments.insert(0, "")
        command = os.path.join(
            os.getcwd(), download.executable.filebrowser_bin
        ) + " ".join(arguments)
        process = subprocess.Popen(
            command,
            shell=True,
            universal_newlines=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
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
        user_profiles = self.env.user_profiles or list(self.env.load_user_profiles())
        auth_map = {}
        for idx, profile in enumerate(user_profiles):
            if profile.authentication.admin:
                profile.perm = models.admin_perm()
            else:
                profile.perm = models.default_perm()
            auth_map[profile.authentication.username] = profile.authentication.password
            hashed_password = steward.hash_password(profile.authentication.password)
            assert steward.validate_password(
                profile.authentication.password, hashed_password
            ), "Validation failed!"
            profile.authentication.password = hashed_password
            model_settings = json.loads(profile.model_dump_json())
            user_settings = {"id": idx + 1}
            # remove custom 'admin' model within authentication
            model_settings["authentication"].pop("admin", None)
            # insert custom 'authentication' model into new dict
            user_settings.update(model_settings["authentication"])
            # remove custom 'authentication' model from 'model_settings'
            model_settings.pop("authentication", None)
            # insert cleaned 'model_settings' into new dict 'user_settings'
            user_settings.update(model_settings)
            final_settings.append(user_settings)
        with open(steward.fileio.users, "w") as file:
            json.dump(final_settings, file, indent=4)
            file.flush()
        return auth_map

    def create_config(self) -> None:
        """Creates the JSON file for configuration."""
        if self.proxy:
            self.env.config_settings.settings.authMethod = "json"
            self.env.config_settings.settings.authHeader = ""
        if str(self.env.config_settings.settings.branding.files) == ".":
            self.env.config_settings.settings.branding.files = ""
        self.env.config_settings.server.port = str(self.env.config_settings.server.port)
        with warnings.catch_warnings(action="ignore"):
            final_settings = steward.remove_trailing_underscore(
                json.loads(self.env.config_settings.model_dump_json())
            )
        if os.path.isfile(self.extra_env):
            if self.extra_env.endswith(".json"):
                with open(self.extra_env) as file:
                    extra_settings = json.load(file)
            elif self.extra_env.endswith(".yaml") or self.extra_env.endswith(".yml"):
                with open(self.extra_env) as file:
                    extra_settings = yaml.load(file, Loader=yaml.FullLoader)
            else:
                raise ValueError("Extra settings should be either a JSON or YAML file.")
            for key, value in extra_settings.items():
                if final_settings.get(key):
                    self.logger.info(
                        "Loading extra settings for '%s' from '%s'", key, self.extra_env
                    )
                    self.logger.debug("Extra settings - %s: %s", key, value)
                    final_settings[key].update(value)
        with open(steward.fileio.config, "w") as file:
            json.dump(final_settings, file, indent=4)
            file.flush()

    def import_config(self) -> None:
        """Imports the configuration file into filebrowser."""
        self.logger.info("Importing configuration from %s", steward.fileio.config)
        self.create_config()
        assert os.path.isfile(
            steward.fileio.config
        ), f"{steward.fileio.config!r} doesn't exist"
        self.run_subprocess(
            ["config", "import", steward.fileio.config],
            "Failed to import configuration",
        )

    def import_users(self) -> Dict[str, str]:
        """Imports the user profiles into filebrowser.

        Returns:
            Dict[str, str]:
            Authentication map provided as environment variables.
        """
        self.logger.info("Importing user profiles from %s", steward.fileio.users)
        auth_map = self.create_users()
        assert os.path.isfile(
            steward.fileio.users
        ), f"{steward.fileio.users!r} doesn't exist"
        self.run_subprocess(
            ["users", "import", steward.fileio.users], "Failed to import user profiles"
        )
        return auth_map

    def background_tasks(self, auth_map: Dict[str, str]) -> None:
        """Initiates the proxy engine and subtitles' format conversion as background tasks.

        Args:
            auth_map: Authentication map provided as environment variables.
        """
        if self.proxy:
            assert proxy_settings.port != int(
                self.env.config_settings.server.port
            ), f"\n\tProxy server can't run on the same port [{proxy_settings.port}] as the server!!"
            # This is to check if the port is available, before starting the proxy server in a dedicated process
            # If not for this, the proxy server will fail to initiate in the child process and become unmanageable
            try:
                with socket.socket() as sock:
                    sock.bind((proxy_settings.host, proxy_settings.port))
            except OSError as error:
                self.logger.error(error)
                self.logger.critical(
                    "Cannot initiate proxy server, retry after sometime or change the port number."
                )
                self.cleanup()
                raise
            log_config = struct.LoggerConfig(self.logger).get()
            if proxy_settings.debug:
                log_config = struct.update_log_level(log_config, logging.DEBUG)
            # noinspection HttpUrlsUsage
            self.proxy_engine = multiprocessing.Process(
                target=proxy_server,
                daemon=True,
                args=(
                    f"http://{self.env.config_settings.server.address}:{self.env.config_settings.server.port}",
                    log_config,
                    auth_map,
                ),
            )
            self.proxy_engine.start()

    def start(self) -> None:
        """Handler for all the functions above."""
        self.cleanup(False)
        self.import_config()
        self.background_tasks(self.import_users())
        self.run_subprocess([], "Failed to run the server", True)
