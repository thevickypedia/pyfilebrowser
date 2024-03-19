import json
import os
import subprocess
import warnings

from pyfilebrowser.modals import models
from pyfilebrowser.squire import downloader, steward


class FileBrowser:
    """Object to handle the filebrowser streaming.

    >>> FileBrowser

    """

    def __init__(self, **kwargs):
        """Instantiates the object.

        Keyword Args:
            logger: Bring your own logger.
        """
        self.logger = kwargs.get('logger', steward.default_logger())
        if not os.path.isfile(downloader.executable.binary):
            downloader.download_asset(logger=self.logger)
        self.env = steward.EnvConfig(**kwargs)

    def __del__(self):
        """Deletes the database file."""
        if os.path.isfile(downloader.executable.database):
            os.remove(downloader.executable.database)

    def run_subprocess(self, command: str, failed_msg: str, stdout: bool = False) -> None:
        """Run ``filebrowser`` commands as subprocess.

        Args:
            command: Command to run.
            failed_msg: Failure message in case of bad return code.
            stdout: Boolean flag to show/hide standard output.
        """
        process = subprocess.Popen(command, shell=True,
                                   universal_newlines=True,
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
            model_settings['authentication'].pop('admin', None)  # remove custom values inserted
            user_settings.update(model_settings['authentication'])
            model_settings.pop('authentication', None)  # remove custom values inserted
            user_settings.update(model_settings)
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
        self.run_subprocess(f"./{downloader.executable.binary} config import {steward.fileio.config}",
                            "Failed to import configuration")

    def import_users(self) -> None:
        """Imports the user profiles into filebrowser."""
        self.logger.info(f"Importing user profiles from {steward.fileio.users!r}")
        self.create_users()
        assert os.path.isfile(steward.fileio.users), f"{steward.fileio.users!r} doesn't exist"
        self.run_subprocess(f"./{downloader.executable.binary} users import {steward.fileio.users}",
                            "Failed to import user profiles")

    def kickoff(self) -> None:
        """Handler for all the functions above."""
        if os.path.isfile(downloader.executable.database):
            os.remove(downloader.executable.database)
        self.import_config()
        self.import_users()
        # noinspection HttpUrlsUsage
        self.logger.info(f"Initiating filebrowser on "
                         f"http://{self.env.config_settings.server.address}:{self.env.config_settings.server.port}")
        self.run_subprocess(f"./{downloader.executable.binary}",
                            "Failed to run the server", True)
