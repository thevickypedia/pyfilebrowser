"""Module for PyFilebrowser settings."""

import os
import platform
from enum import StrEnum

from pydantic import BaseModel, Field

from pyfilebrowser.modals import models
from pyfilebrowser.modals.pydantic_config import PydanticEnvConfig


class ServerSettings(PydanticEnvConfig):
    """Configuration settings for PyFilebrowser.

    >>> ServerSettings

    """

    # 0 to 10 attempts
    restart: int = Field(0, le=10, ge=0)

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = os.path.join(models.SECRETS_PATH, ".config.env")
        extra = "ignore"


class RestartPolicy(StrEnum):
    """Restart policy options for Docker containers."""

    NO = "no"
    ALWAYS = "always"
    UNLESS_STOPPED = "unless-stopped"
    ON_FAILURE = "on-failure"


class ReadWriteMode(StrEnum):
    """Read/Write mode options for Docker volumes."""

    READ_ONLY = "ro"
    READ_WRITE = "rw"


class Credentials(BaseModel):
    """Credentials for container registry authentication.

    >>> Credentials

    """

    username: str = ""
    password: str = ""

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = os.path.join(models.SECRETS_PATH, ".container.env")
        extra = "ignore"


class ContainerSettings(PydanticEnvConfig):
    """Container settings for PyFilebrowser.

    >>> ContainerSettings

    """

    detach: bool = False
    name: str = "filebrowser"
    image: str = "thevickypedia/filebrowser"
    tag: str = "latest"
    platform: str = "linux/amd64" if platform.machine() == "x86_64" else "linux/arm64"
    credentials: Credentials = Credentials()
    data_volume: str = "/data"
    config_volume: str = "/config"
    data_mode: ReadWriteMode = ReadWriteMode.READ_WRITE
    config_mode: ReadWriteMode = ReadWriteMode.READ_WRITE
    restart: RestartPolicy = RestartPolicy.UNLESS_STOPPED

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = os.path.join(models.SECRETS_PATH, ".container.env")
        extra = "ignore"
