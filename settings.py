import os
import socket
from enum import StrEnum
from typing import List, Optional

from pydantic import DirectoryPath, PositiveInt, field_validator, BaseModel
from pydantic_settings import BaseSettings

if not os.path.isdir('settings'):
    os.mkdir('settings')


class Perm(BaseModel):
    admin: bool
    execute: bool
    create: bool
    rename: bool
    modify: bool
    delete: bool
    share: bool
    download: bool


def admin_perm():
    return Perm(**{
        "admin": True,
        "execute": True,
        "create": True,
        "rename": True,
        "modify": True,
        "delete": True,
        "share": True,
        "download": True
    })


def default_perm():
    return Perm(**{
        "admin": False,
        "execute": True,
        "create": True,
        "rename": False,
        "modify": False,
        "delete": False,
        "share": True,
        "download": True
    })


class Authentication(BaseModel):
    username: str
    password: str
    admin: bool = False
    perm: Perm = None


class SortBy(StrEnum):
    name: str = "name"
    size: str = "size"
    modified: str = "modified"


class Sorting(BaseModel):
    by: str = "name"
    asc: bool = False


class UserSettings(BaseSettings):
    authentication: Authentication = Authentication(**{"username": "admin", "password": "admin", "admin": True})
    scope: str = "/"
    locale: str = "en"
    lockPassword: bool = False
    viewMode: str = "list"
    singleClick: bool = False
    commands: List[str] = []
    sorting: Sorting = Sorting()
    rules: List[str] = []
    hideDotfiles: bool = False
    dateFormat: bool = False

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".env"))
        extra = "ignore"


class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    user_settings: List[UserSettings] = [UserSettings()]

    server_path: DirectoryPath

    # General settings
    theme: Optional[str] = ""
    log: Optional[str] = ""

    port: PositiveInt = 8080
    address: str = socket.gethostbyname('localhost')

    # Upload settings
    chunk_size: PositiveInt = 10 * 1024 * 1024  # Defaults to 10 MB
    retry_count: int = 5

    # Branding settings
    branding_name: Optional[str] = ""
    branding_path: Optional[DirectoryPath] = ""

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".env"))
        extra = "allow"

    @field_validator('theme', mode='before', check_fields=True)
    def check_theme(cls, v, values, **kwargs):  # noqa
        """Validate task field in tasks."""
        if v in ("light", "dark"):
            return v
        elif v:
            raise ValueError('bad value')

    @field_validator('log', mode='before', check_fields=True)
    def check_log(cls, v, values, **kwargs):  # noqa
        """Validate task field in tasks."""
        if v in ("file", "stdout"):
            return v
        elif v:
            raise ValueError('bad value')
