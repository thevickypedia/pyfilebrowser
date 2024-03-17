import json
import os.path

import bcrypt

from settings import EnvConfig, admin_perm, default_perm


def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def validate_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


class Generator:
    def __init__(self, **kwargs):
        self.env = EnvConfig(**kwargs)

    def handle_users(self):
        final_settings = []
        for idx, setting in enumerate(self.env.user_settings):
            if setting.authentication.admin:
                setting.authentication.perm = admin_perm()
            else:
                setting.authentication.perm = default_perm()
            hashed_password = hash_password(setting.authentication.password)
            assert validate_password(setting.authentication.password, hashed_password), "Validation failed!"
            setting.authentication.password = hashed_password
            user_settings = json.loads(setting.model_dump_json())
            user_settings['id'] = idx + 1
            user_settings['authentication'].pop('admin', None)  # remove custom values inserted
            user_settings.update(user_settings['authentication'])
            user_settings.pop('authentication', None)  # remove custom values inserted
            final_settings.append(user_settings)
        with open(os.path.join('settings', 'config.json'), 'w') as file:
            json.dump(final_settings, file)


if __name__ == '__main__':
    generator = Generator()
    generator.handle_users()
