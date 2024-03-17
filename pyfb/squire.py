import logging
import os
from typing import List

import bcrypt
from pydantic import BaseModel, DirectoryPath, FilePath

from pyfb.modals.config import ConfigSettings
from pyfb.modals.users import UserSettings


def default_logger() -> logging.Logger:
    """Generates a default console logger.

    Returns:
        logging.Logger:
        Logger object.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(
        fmt=logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - [%(processName)s:%(module)s:%(lineno)d] - %(funcName)s - %(message)s'
        )
    )
    logger.addHandler(hdlr=handler)
    return logger


def hash_password(password: str) -> str:
    """Returns a salted hash for the given text."""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def validate_password(password: str, hashed_password: str) -> bool:
    """Validates whether the hashed password matches the text version."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def remove_trailing_underscore(dictionary: dict) -> dict:
    """Iterates through the dictionary and removes any key ending with an '_' underscore."""
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


class EnvConfig(BaseModel):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    user_profiles: List[UserSettings] = []
    config_settings: ConfigSettings = ConfigSettings()

    @classmethod
    def load_user_profiles(cls):
        """Load UserSettings instances from .env files in the current directory."""
        profiles = []
        for file in os.listdir(os.getcwd()):
            if 'user' in file and file.endswith('.env'):
                profiles.append(UserSettings.from_env_file(file))
        return profiles


class FileIO(BaseModel):
    """FileIO object to load the JSON files.

    >>> FileIO

    """

    base_dir: DirectoryPath = os.path.join('../settings')
    config: FilePath = os.path.join(base_dir, 'config.json')
    users: FilePath = os.path.join(base_dir, 'users.json')


fileio = FileIO()

if not os.path.isdir(fileio.base_dir):
    os.mkdir(fileio.base_dir)
