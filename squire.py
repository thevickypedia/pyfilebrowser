import logging
import os
from typing import List

import bcrypt
from pydantic import BaseModel, DirectoryPath, FilePath

from modals.config import ConfigSettings
from modals.users import UserSettings


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


class EnvConfig(BaseModel):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    user_settings: List[UserSettings] = [UserSettings()]
    config_settings: ConfigSettings = ConfigSettings()


class FileIO(BaseModel):
    base_dir: DirectoryPath = os.path.join('settings')
    config: FilePath = os.path.join(base_dir, 'config.json')
    users: FilePath = os.path.join(base_dir, 'users.json')


fileio = FileIO()

if not os.path.isdir(fileio.base_dir):
    os.mkdir(fileio.base_dir)
