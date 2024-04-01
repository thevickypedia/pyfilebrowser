import os
import pathlib
import socket
from typing import Dict

from pydantic import BaseModel, FilePath, HttpUrl
from pydantic_settings import BaseSettings


# noinspection PyPep8Naming
class destination(BaseModel):
    """Server's destination settings.

    >>> destination

    """

    url: HttpUrl
    auth_config: Dict[str, str]


class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    host: str = socket.gethostbyname('localhost')
    port: int = 8000
    workers: int = 1
    debug: bool = False
    error_page: FilePath = os.path.join(pathlib.PosixPath(__file__).parent, 'error.html')

    class Config:
        """Environment variables configuration."""

        env_file = ".proxy.env"
        extra = "ignore"


env_config = EnvConfig()
