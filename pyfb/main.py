import json
import os
import re
import shutil
import subprocess
import warnings

from pyfb.modals.models import admin_perm, default_perm
from pyfb.squire import EnvConfig, hash_password, validate_password, fileio, remove_trailing_underscore, default_logger

DATETIME_PATTERN = re.compile(r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} ')


def remove_prefix(text: str) -> str:
    """Returns the message part from the default log output from filebrowser."""
    return DATETIME_PATTERN.sub('', text).strip()


class FileBrowser:
    """Object to handle the filebrowser streaming.

    >>> FileBrowser

    """

    def __init__(self, **kwargs):
        """Instantiates the object.

        Keyword Args:
            logger: Bring your own logger.
            # todo: fill the rest
        """
        if not shutil.which("filebrowser"):
            raise EnvironmentError(
                "'filebrowser' should be installed beforehand. Please check README.md for instructions"
            )
        self.env = EnvConfig(**kwargs)
        self.logger = kwargs.get('logger', default_logger())

    def __del__(self):
        """Deletes the filebrowser.db."""
        if os.path.isfile('filebrowser.db'):
            os.remove('filebrowser.db')

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
                    self.logger.info(remove_prefix(line))
            process.wait()
            for line in process.stderr:
                self.logger.error(remove_prefix(line))
            assert process.returncode == 0, failed_msg
        except KeyboardInterrupt:
            if process.poll() is None:
                for line in process.stdout:
                    self.logger.info(remove_prefix(line))
                process.terminate()

    def create_users(self) -> None:
        """Creates the JSON file for user profiles."""
        final_settings = []
        user_profiles = self.env.user_profiles or self.env.load_user_profiles()
        for idx, profile in enumerate(user_profiles):
            if profile.authentication.admin:
                profile.perm = admin_perm()
            else:
                profile.perm = default_perm()
            hashed_password = hash_password(profile.authentication.password)
            assert validate_password(profile.authentication.password, hashed_password), "Validation failed!"
            profile.authentication.password = hashed_password
            model_settings = json.loads(profile.model_dump_json())
            user_settings = {'id': idx + 1}
            model_settings['authentication'].pop('admin', None)  # remove custom values inserted
            user_settings.update(model_settings['authentication'])
            model_settings.pop('authentication', None)  # remove custom values inserted
            user_settings.update(model_settings)
            final_settings.append(user_settings)
        with open(fileio.users, 'w') as file:
            json.dump(final_settings, file, indent=4)
            file.flush()

    def create_config(self):
        """Creates the JSON file for configuration."""
        config_settings = self.env.config_settings
        if str(config_settings.settings.branding.files) == ".":
            config_settings.settings.branding.files = ""
        config_settings.server.port = str(config_settings.server.port)
        with warnings.catch_warnings(action="ignore"):
            final_settings = remove_trailing_underscore(json.loads(config_settings.model_dump_json()))
        with open(fileio.config, 'w') as file:
            json.dump(final_settings, file, indent=4)
            file.flush()

    def import_config(self):
        """Imports the configuration file into filebrowser."""
        self.logger.info(f"Importing configuration from {fileio.config!r}")
        self.create_config()
        assert os.path.isfile(fileio.config), f"{fileio.config!r} doesn't exist"
        self.run_subprocess(f"filebrowser config import {fileio.config}", "Failed to import configuration")

    def import_users(self):
        """Imports the user profiles into filebrowser."""
        self.logger.info(f"Importing user profiles from {fileio.users!r}")
        self.create_users()
        assert os.path.isfile(fileio.users), f"{fileio.users!r} doesn't exist"
        self.run_subprocess(f"filebrowser users import {fileio.users}", "Failed to import user profiles")

    def kickoff(self):
        """Handler for all the functions above."""
        if os.path.isfile('filebrowser.db'):
            os.remove('filebrowser.db')
        self.import_config()
        self.import_users()
        # noinspection HttpUrlsUsage
        self.logger.info(f"Initiating filebrowser on "
                         f"http://{self.env.config_settings.server.address}:{self.env.config_settings.server.port}")
        self.run_subprocess("filebrowser", "Failed to run the server", True)
