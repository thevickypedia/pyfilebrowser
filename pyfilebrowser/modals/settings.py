"""Module for PyFilebrowser settings."""

import os

from pydantic import Field
from pydantic_settings import BaseSettings

from pyfilebrowser.modals import models


class ServerSettings(BaseSettings):
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
