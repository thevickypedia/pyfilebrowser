import os
import socket as sock
from enum import StrEnum
from typing import List, Optional, Union

from pydantic import DirectoryPath, PositiveInt, BaseModel, FilePath
from pydantic_settings import BaseSettings

from filebrowser.modals.models import Sorting, Perm, default_perm


class Defaults(BaseSettings):
    scope: str = "."
    locale: str = "en"
    viewMode: str = "list"
    singleClick: bool = False
    sorting: Sorting = Sorting()
    perm: Perm = default_perm()
    commands: List = []
    hideDotfiles: bool = False
    dateFormat: bool = False

    class Config:
        """Environment variables configuration."""

        env_prefix = "defaults_"
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".config.env"))
        extra = "ignore"


class Theme(StrEnum):
    light: str = "light"
    dark: str = "dark"
    blank: str = ""


class Branding(BaseSettings):
    name: str = ""
    disableExternal: bool = False
    disableUsedPercentage: bool = False
    files: Optional[DirectoryPath] = ""
    theme: Theme = Theme.blank
    color: str = ""

    class Config:
        """Environment variables configuration."""

        env_prefix = "branding_"
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".config.env"))
        extra = "ignore"


class Tus(BaseSettings):
    chunkSize: PositiveInt = 10 * 1024 * 1024  # Defaults to 10 MB
    retryCount: PositiveInt = 5

    class Config:
        """Environment variables configuration."""

        env_prefix = "tus_"
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".config.env"))
        extra = "ignore"


class Commands(BaseSettings):
    after_copy: List[str] = []
    after_delete: List[str] = []
    after_rename: List[str] = []
    after_save: List[str] = []
    after_upload: List[str] = []
    before_copy: List[str] = []
    before_delete: List[str] = []
    before_rename: List[str] = []
    before_save: List[str] = []
    before_upload: List[str] = []

    class Config:
        """Environment variables configuration."""

        env_prefix = "commands_"
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".config.env"))
        extra = "ignore"


class Log(StrEnum):
    stdout: str = "stdout"
    file: str = "file"


class Config(BaseSettings):
    signup: bool = False
    createUserDir: bool = False
    userHomeBasePath: str = os.path.join(os.path.expanduser('~'), 'users')
    defaults: Defaults = Defaults()
    authMethod: str = "json"
    branding: Branding = Branding()
    tus: Tus = Tus()
    commands: Commands = Commands()
    shell_: List[str] = []
    rules: List[str] = []

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".config.env"))
        extra = "ignore"


class Server(BaseSettings):
    root: DirectoryPath
    baseURL: str = ""
    socket: str = ""
    tlsKey: Union[FilePath, str] = ""
    tlsCert: Union[FilePath, str] = ""
    port: PositiveInt = 8080
    address: str = sock.gethostbyname('localhost')
    log: Log = Log.stdout
    enableThumbnails: bool = False
    resizePreview: bool = False
    enableExec: bool = False
    typeDetectionByHeader: bool = False
    authHook: str = ""
    tokenExpirationTime: str = ""

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".config.env"))
        extra = "ignore"


class Auther(BaseSettings):
    recaptcha: Optional[str] = None

    class Config:
        """Environment variables configuration."""

        env_prefix = "auth_"
        env_file = os.environ.get("env_file", os.environ.get("ENV_FILE", ".config.env"))
        extra = "ignore"


class ConfigSettings(BaseModel):
    settings: Config = Config()
    server: Server = Server()
    auther: Auther = Auther()
