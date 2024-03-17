import json
import os.path
import warnings

from modals.models import admin_perm, default_perm
from squire import EnvConfig, hash_password, validate_password, fileio, remove_trailing_underscore


class FileBrowser:
    def __init__(self, **kwargs):
        self.env = EnvConfig(**kwargs)

    def create_users(self):
        final_settings = []
        for idx, setting in enumerate(self.env.user_settings):
            if setting.authentication.admin:
                setting.perm = admin_perm()
            else:
                setting.perm = default_perm()
            hashed_password = hash_password(setting.authentication.password)
            assert validate_password(setting.authentication.password, hashed_password), "Validation failed!"
            setting.authentication.password = hashed_password
            model_settings = json.loads(setting.model_dump_json())
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
        self.create_config()
        assert os.path.isfile(fileio.config), f"{fileio.config!r} doesn't exist"
        os.system(f"filebrowser config import {fileio.config}")

    def import_users(self):
        self.create_users()
        assert os.path.isfile(fileio.users), f"{fileio.users!r} doesn't exist"
        os.system(f"filebrowser users import {fileio.users}")

    def kickoff(self):
        if os.path.isfile('filebrowser.db'):
            os.remove('filebrowser.db')
        self.import_config()
        self.import_users()
        os.system("filebrowser")


if __name__ == '__main__':
    file_browser = FileBrowser()
    file_browser.kickoff()
