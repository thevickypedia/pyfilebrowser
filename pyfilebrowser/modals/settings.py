"""Module for PyFilebrowser settings."""

import os
from typing import List, Optional

from pydantic import DirectoryPath, Field, FilePath

from pyfilebrowser.modals import models
from pyfilebrowser.modals.pydantic_config import PydanticEnvConfig


class ServerSettings(PydanticEnvConfig):
    """Configuration settings for PyFilebrowser that are NOT propagated to the filebrowser config DB.

    >>> ServerSettings

        - **symlinks** - List of symlinks to be created in the root directory. Accepts file or directory paths.

    """

    # 0 to 10 attempts
    restart: int = Field(0, le=10, ge=0)
    symlinks: Optional[List[DirectoryPath | FilePath]] = []

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        vault_table = "pyfilebrowser.config"
        env_file = os.path.join(models.SECRETS_PATH, ".config.env")
        extra = "ignore"
