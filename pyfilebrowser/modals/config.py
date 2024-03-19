import os
import socket as sock
from enum import StrEnum
from typing import List, Optional, Union

from pydantic import BaseModel, DirectoryPath, FilePath, HttpUrl, PositiveInt
from pydantic_settings import BaseSettings

from pyfilebrowser.modals import models


class Defaults(BaseSettings):
    """Configuration for all the default settings for the server.

    >>> Defaults

    See Also:
        Environment variables should be prefixed with ``defaults_``, and present in ``.config.env``
    """

    scope: str = "."
    locale: str = "en"
    viewMode: str = "list"
    singleClick: bool = False
    sorting: models.Sorting = models.Sorting()
    perm: models.Perm = models.default_perm()
    commands: List = []
    hideDotfiles: bool = False
    dateFormat: bool = False

    class Config:
        """Environment variables configuration."""

        env_prefix = "defaults_"
        env_file = ".config.env"
        extra = "ignore"


class Theme(StrEnum):
    """Enum for different theme options.

    >>> Theme

    """

    light: str = "light"
    dark: str = "dark"
    blank: str = ""


class Branding(BaseSettings):
    """Configuration for the custom branding settings for the server.

    >>> Defaults

    See Also:
        Environment variables should be prefixed with ``branding_``, and present in ``.config.env``
    """

    name: str = ""
    disableExternal: bool = False
    disableUsedPercentage: bool = False
    files: Optional[DirectoryPath] = ""
    theme: Theme = Theme.blank
    color: str = ""

    class Config:
        """Environment variables configuration."""

        env_prefix = "branding_"
        env_file = ".config.env"
        extra = "ignore"


class Tus(BaseSettings):
    """Configuration for the upload settings in the server.

    >>> Defaults

    See Also:
        Environment variables should be prefixed with ``tus_``, and present in ``.config.env``
    """

    chunkSize: PositiveInt = 10 * 1024 * 1024  # Defaults to 10 MB
    retryCount: PositiveInt = 5

    class Config:
        """Environment variables configuration."""

        env_prefix = "tus_"
        env_file = ".config.env"
        extra = "ignore"


class Commands(BaseSettings):
    """Configuration for list of the commands to be executed before or after a certain event.

    >>> Commands

    See Also:
        The command runner is a feature that enables you to execute shell commands before or after a certain event.
    """

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
        env_file = ".config.env"
        extra = "ignore"


class Log(StrEnum):
    """Enum for different log options.

    >>> Log

    """

    stdout: str = "stdout"
    file: str = "file"


class Config(BaseSettings):
    """Configuration settings [``config`` section] for the server.

    >>> Config

    """

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
        env_file = ".config.env"
        extra = "ignore"


class Server(BaseSettings):
    """Configuration settings [``server`` section] for the server.

    >>> Server

    """

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


class ReCAPTCHA(BaseModel):
    """Settings for ReCaptcha.

    >>> ReCAPTCHA

    """

    host: HttpUrl
    key: str
    secret: str


class Auther(BaseSettings):
    """Configuration settings [``server`` section] for the server.

    >>> Server

    See Also:
        Environment variables should be prefixed with ``auth_``, and present in ``.config.env``
    """

    recaptcha: Optional[ReCAPTCHA] = None

    class Config:
        """Environment variables configuration."""

        env_prefix = "auth_"
        env_file = ".config.env"
        extra = "ignore"


class ConfigSettings(BaseModel):
    """Wrapper for all the configuration settings to form a nested JSON object.

    >>> ConfigSettings

    """

    settings: Config = Config()
    server: Server = Server()
    auther: Auther = Auther()
