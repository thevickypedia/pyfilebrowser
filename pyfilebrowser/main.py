import json
import os
import subprocess
import warnings
from multiprocessing.context import \
    TimeoutError as ThreadTimeoutError  # noqa: PyProtectedMember
from multiprocessing.pool import ThreadPool
from typing import List

from pyfilebrowser.modals import models
from pyfilebrowser.squire import download, steward, subtitles


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
        if self.env.config_settings.server.log == models.Log.file:
            # Reset to stdout, so the log output stream can be controlled with custom logging
            self.env.config_settings.server.log = models.Log.stdout
            self.logger = kwargs.get('logger', steward.default_logger(True))
        else:
            self.logger = kwargs.get('logger', steward.default_logger(False))
        github = download.GitHub(**kwargs)
        if not os.path.isfile(download.executable.filebrowser_bin):
            download.binary(logger=self.logger, github=github)
        self.converted = None

    def exit_process(self):
        """Deletes the database file, and all the subtitles that were created by this application."""
        if os.path.isfile(download.executable.filebrowser_db):
            self.logger.info(f"Removing database {download.executable.filebrowser_db}")
            os.remove(download.executable.filebrowser_db)
        if self.converted:
            try:
                files_removed = []
                for file in self.converted.get(timeout=5):
                    try:
                        os.remove(file)
                        files_removed.append(file.name)
                    except FileNotFoundError:
                        continue
                self.logger.info(f"Subtitles removed automatically [{len(files_removed)}]: {', '.join(files_removed)}")
            except ThreadTimeoutError as error:
                self.logger.error(error)

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
            self.logger.warning("Interrupted manually")
            if process.poll() is None:
                for line in process.stdout:
                    self.logger.info(steward.remove_prefix(line))
                process.terminate()
            self.exit_process()

    def create_users(self) -> None:
        """Creates the JSON file for user profiles."""
        final_settings = []
        user_profiles = self.env.user_profiles or self.env.load_user_profiles()
        for idx, profile in enumerate(user_profiles):
            if profile.authentication.admin:
                profile.perm = models.admin_perm()
            else:
                profile.perm = models.default_perm()
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

    def create_config(self) -> None:
        """Creates the JSON file for configuration."""
        config_settings = self.env.config_settings
        if str(config_settings.settings.branding.files) == ".":
            config_settings.settings.branding.files = ""
        config_settings.server.port = str(config_settings.server.port)
        with warnings.catch_warnings(action="ignore"):
            final_settings = steward.remove_trailing_underscore(json.loads(config_settings.model_dump_json()))
        with open(steward.fileio.config, 'w') as file:
            json.dump(final_settings, file, indent=4)
            file.flush()

    def import_config(self) -> None:
        """Imports the configuration file into filebrowser."""
        self.logger.info(f"Importing configuration from {steward.fileio.config!r}")
        self.create_config()
        assert os.path.isfile(steward.fileio.config), f"{steward.fileio.config!r} doesn't exist"
        self.run_subprocess(["config", "import", steward.fileio.config],
                            "Failed to import configuration")

    def import_users(self) -> None:
        """Imports the user profiles into filebrowser."""
        self.logger.info(f"Importing user profiles from {steward.fileio.users!r}")
        self.create_users()
        assert os.path.isfile(steward.fileio.users), f"{steward.fileio.users!r} doesn't exist"
        self.run_subprocess(["users", "import", steward.fileio.users],
                            "Failed to import user profiles")

    def start(self) -> None:
        """Handler for all the functions above."""
        if os.path.isfile(download.executable.filebrowser_db):
            os.remove(download.executable.filebrowser_db)
        self.import_config()
        self.import_users()
        # noinspection HttpUrlsUsage
        self.logger.info(f"Initiating filebrowser on "
                         f"http://{self.env.config_settings.server.address}:{self.env.config_settings.server.port}")
        self.converted = ThreadPool(processes=1).apply_async(func=subtitles.auto_convert,
                                                             kwds=dict(root=self.env.config_settings.server.root,
                                                                       logger=self.logger))
        self.run_subprocess([], "Failed to run the server", True)
