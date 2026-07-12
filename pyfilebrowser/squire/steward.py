import logging
import os
import re
import warnings
from collections.abc import Generator
from datetime import datetime
from typing import Callable, Iterable, List

import bcrypt
from pydantic import BaseModel, DirectoryPath, FilePath

from pyfilebrowser.modals import config, models, pydantic_config, users

DATETIME_PATTERN = re.compile(r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} ")
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def get_env(key: str, default: str = None, convert_to: Callable = None) -> str | None:
    """Get case agnostic environment variable based on the key with an optional default value."""
    value = os.getenv(key.lower()) or os.getenv(key.upper()) or default
    if value and convert_to:
        if convert_to is bool:
            return value.lower() in ("1", "true")
        return convert_to(value)
    return value


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
        if not os.path.isdir("logs"):
            os.mkdir("logs")
        logfile: str = datetime.now().strftime(
            os.path.join("logs", "pyfilebrowser_%d-%m-%Y.log")
        )
        handler = logging.FileHandler(filename=logfile)
    else:
        handler = logging.StreamHandler()
    logger = logging.getLogger(__name__)
    log_level = get_env("log_level") or get_env("pyfb_log_level") or "INFO"
    assert (
        log_level in LOG_LEVELS
    ), f"Log level must be set to one of {LOG_LEVELS}, received {log_level}"
    logger.setLevel(level=log_level)
    handler.setFormatter(
        fmt=logging.Formatter(
            fmt="%(asctime)s - %(levelname)-8s - [%(funcName)s:%(lineno)d] - %(message)s"
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
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password.decode("utf-8")


def validate_password(password: str, hashed_password: str) -> bool:
    """Validates whether the hashed password matches the text version.

    Args:
        password: Password as plain text.
        hashed_password: Hashed password.

    Returns:
        bool:
        Returns a boolean flag to indicate whether the password matches.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


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
            if key.endswith("_"):
                new_key = key.rstrip("_")
                dictionary[new_key] = dictionary.pop(key)
    elif isinstance(dictionary, list):
        for i, item in enumerate(dictionary):
            dictionary[i] = remove_trailing_underscore(item)
    return dictionary


def delete(files: Iterable[str], logger: logging.Logger = None) -> None:
    """Deletes the provided list of files.

    Args:
        files: List or tuple of files to delete.
        logger: Custom logger object.
    """
    for file in files:
        try:
            os.remove(file)
            logger.info("Removed %s", file) if logger else None
        except FileNotFoundError as warn:
            logger.warning(warn) if logger else None


def remove_prefix(text: str) -> str:
    """Returns the message part from the default log output from filebrowser."""
    return DATETIME_PATTERN.sub("", text).strip()


def get_user_settings() -> Generator[users.UserSettings]:
    """Get user profile settings.

    Yields:
        users.UserSettings:
        Yields the normalized and loaded user profile settings.
    """
    if pydantic_config.vault_client:
        for table in pydantic_config.vault_client.list_tables():
            if "user" in table:
                yield users.UserSettings.from_vault(table)
    if os.path.isdir(models.SECRETS_PATH):
        for file in os.listdir(models.SECRETS_PATH):
            if "user" in file and file.endswith(".env"):
                yield users.UserSettings.from_env_file(
                    str(os.path.join(models.SECRETS_PATH, file))
                )


def load_user_profiles() -> Generator[users.UserSettings]:
    """Load UserSettings instances from .env files in the current directory.

    Yields:
        Generator[users.UserSettings]:
        A generator of ``UserSettings`` object.
    """
    for user_settings in get_user_settings():
        if not user_settings.perm and not user_settings.admin:
            user_settings.lockPassword = True
            user_settings.hideDotfiles = True
            if user_settings.scope == "/":
                warnings.warn(
                    f"User {user_settings.username!r} is not an admin, "
                    "but has permissions to the root directory.",
                    UserWarning,
                )
        yield user_settings


class EnvConfig(BaseModel):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    user_profiles: List[users.UserSettings] = list(load_user_profiles())
    config_settings: config.ConfigSettings = config.ConfigSettings()
    if (
        config_settings.settings.createUserDir
        and not config_settings.settings.userHomeBasePath
    ):
        user_home_base: DirectoryPath = os.path.join(
            config_settings.server.root, "users"
        )
        os.makedirs(user_home_base, exist_ok=True)
        config_settings.settings.userHomeBasePath = user_home_base


class FileIO(BaseModel):
    """FileIO object to load the JSON files.

    >>> FileIO

    """

    settings_dir: DirectoryPath = os.path.join(os.getcwd(), "settings")
    config: FilePath = os.path.join(settings_dir, "config.json")
    users: FilePath = os.path.join(settings_dir, "users.json")


fileio = FileIO()

if not os.path.isdir(fileio.settings_dir):
    os.mkdir(fileio.settings_dir)
