import logging
import os
import re
from datetime import datetime
from typing import List

import bcrypt
from pydantic import BaseModel, DirectoryPath, FilePath

from pyfilebrowser.modals import config, users

DATETIME_PATTERN = re.compile(r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} ')


def ordinal(n: int) -> str:
    """Returns the ordinal representation of a given number.

    Args:
        n: The number for which the ordinal representation is to be determined.

    Returns:
        str:
        The ordinal representation of the input number.
    """
    if 10 < n % 100 < 20:
        suffix = "th"
    else:
        suffixes = {1: "st", 2: "nd", 3: "rd"}
        suffix = suffixes.get(n % 10, "th")
    return f"{n}{suffix}"


def default_logger(log_to_file: bool) -> logging.Logger:
    """Generates a default console logger.

    Args:
        log_to_file: Boolean flag to stream logs to a file.

    Returns:
        logging.Logger:
        Logger object.
    """
    if log_to_file:
        if not os.path.isdir('logs'):
            os.mkdir('logs')
        logfile: str = datetime.now().strftime(os.path.join('logs', 'pyfilebrowser_%d-%m-%Y.log'))
        handler = logging.FileHandler(filename=logfile)
    else:
        handler = logging.StreamHandler()
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler.setFormatter(
        fmt=logging.Formatter(
            fmt='%(asctime)s - %(levelname)-8s - [%(funcName)s:%(lineno)d] - %(message)s'
        )
    )
    logger.addHandler(hdlr=handler)
    return logger


def hash_password(password: str) -> str:
    """Returns a salted hash for the given text.

    Args:
        password: Password as plain text.

    Returns:
        str:
        Decoded hashed password as a string.
    """
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')


def validate_password(password: str, hashed_password: str) -> bool:
    """Validates whether the hashed password matches the text version.

    Args:
        password: Password as plain text.
        hashed_password: Hashed password.

    Returns:
        bool:
        Returns a boolean flag to indicate whether the password matches.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def remove_trailing_underscore(dictionary: dict) -> dict:
    """Iterates through the dictionary and removes any key ending with an '_' underscore.

    Args:
        dictionary: Any nested dictionary.

    Returns:
        dict:
        Returns the same nested dictionary, removing trailing underscore in the keys.
    """
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


def remove_prefix(text: str) -> str:
    """Returns the message part from the default log output from filebrowser."""
    return DATETIME_PATTERN.sub('', text).strip().capitalize()


class EnvConfig(BaseModel):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    user_profiles: List[users.UserSettings] = []
    config_settings: config.ConfigSettings = config.ConfigSettings()

    @classmethod
    def load_user_profiles(cls) -> List[users.UserSettings]:
        """Load UserSettings instances from .env files in the current directory.

        Returns:
            List[users.UserSettings]:
            Returns a list of ``UserSettings`` objects.
        """
        profiles = []
        for file in os.listdir(os.getcwd()):
            if 'user' in file and file.endswith('.env'):
                profiles.append(users.UserSettings.from_env_file(file))
        return profiles


class FileIO(BaseModel):
    """FileIO object to load the JSON files.

    >>> FileIO

    """

    settings_dir: DirectoryPath = os.path.join(os.getcwd(), 'settings')
    config: FilePath = os.path.join(settings_dir, 'config.json')
    users: FilePath = os.path.join(settings_dir, 'users.json')


fileio = FileIO()

if not os.path.isdir(fileio.settings_dir):
    os.mkdir(fileio.settings_dir)
