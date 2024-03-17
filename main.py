import json

import bcrypt

from modals.models import admin_perm, default_perm
from settings import EnvConfig, fileio


def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def validate_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def remove_trailing_underscore(dictionary):
    if isinstance(dictionary, dict):
        for key in list(dictionary.keys()):
            if isinstance(dictionary[key], dict):
                dictionary[key] = remove_trailing_underscore(dictionary[key])
            if key.endswith('_'):
                new_key = key.rstrip('_')
                dictionary[new_key] = dictionary.pop(key)
    elif isinstance(dictionary, list):
        for i, item in enumerate(dictionary):
            dictionary[i] = remove_trailing_underscore(item)
    return dictionary


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
        if str(self.env.config_settings.settings.branding.files) == ".":
            self.env.config_settings.settings.branding.files = ""
        final_settings = remove_trailing_underscore(json.loads(self.env.config_settings.model_dump_json()))
        with open(fileio.config, 'w') as file:
            json.dump(final_settings, file, indent=4)
            file.flush()


if __name__ == '__main__':
    file_browser = FileBrowser()
    file_browser.create_users()
    file_browser.create_config()
