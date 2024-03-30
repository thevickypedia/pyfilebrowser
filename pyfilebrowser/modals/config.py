import os
import socket as sock
from typing import List, Optional

from pydantic import BaseModel, DirectoryPath, FilePath, HttpUrl, PositiveInt
from pydantic_settings import BaseSettings

from pyfilebrowser.modals import models


class Branding(BaseSettings):
    """Configuration for the custom branding settings for the server.

    >>> Branding

    See Also:
        Environment variables should be prefixed with ``branding_``, and present in ``.config.env``
    """

    name: Optional[str] = ""
    disableExternal: Optional[bool] = False
    disableUsedPercentage: Optional[bool] = False
    files: Optional[DirectoryPath] = ""
    theme: Optional[models.Theme] = models.Theme.blank
    color: Optional[str] = ""

    class Config:
        """Environment variables configuration."""

        env_prefix = "branding_"
        env_file = ".config.env"
        extra = "ignore"


class Tus(BaseSettings):
    """Configuration for the upload settings in the server.

    >>> Tus

    See Also:
        Environment variables should be prefixed with ``tus_``, and present in ``.config.env``
    """

    chunkSize: Optional[PositiveInt] = 10 * 1024 * 1024  # Defaults to 10 MB
    retryCount: Optional[PositiveInt] = 5

    class Config:
        """Environment variables configuration."""

        env_prefix = "tus_"
        env_file = ".config.env"
        extra = "ignore"


class Defaults(BaseSettings):
    """Configuration for all the default settings for the server.

    >>> Defaults

    See Also:
        Environment variables should be prefixed with ``defaults_``, and present in ``.config.env``
    """

    scope: Optional[str] = "."
    locale: Optional[str] = "en"
    viewMode: Optional[str] = "list"
    singleClick: Optional[bool] = False
    sorting: models.Sorting = models.Sorting()
    perm: models.Perm = models.default_perm()
    commands: Optional[List[str]] = []
    hideDotfiles: Optional[bool] = False
    dateFormat: Optional[bool] = False

    class Config:
        """Environment variables configuration."""

        env_prefix = "defaults_"
        env_file = ".config.env"
        extra = "ignore"


class Commands(BaseSettings):
    """Configuration for list of the commands to be executed before or after a certain event.

    >>> Commands

    See Also:
        The command runner is a feature that enables you to execute shell commands before or after a certain event.
    """

    after_copy: Optional[List[str]] = []
    after_delete: Optional[List[str]] = []
    after_rename: Optional[List[str]] = []
    after_save: Optional[List[str]] = []
    after_upload: Optional[List[str]] = []
    before_copy: Optional[List[str]] = []
    before_delete: Optional[List[str]] = []
    before_rename: Optional[List[str]] = []
    before_save: Optional[List[str]] = []
    before_upload: Optional[List[str]] = []

    class Config:
        """Environment variables configuration."""

        env_prefix = "commands_"
        env_file = ".config.env"
        extra = "ignore"


class ReCAPTCHA(BaseModel):
    """Settings for ReCaptcha.

    >>> ReCAPTCHA

    """

    host: Optional[HttpUrl]
    key: Optional[str]
    secret: Optional[str]


class Server(BaseSettings):
    """Configuration settings [``server`` section] for the server.

    >>> Server

    """

    root: DirectoryPath
    baseURL: Optional[str] = ""
    socket: Optional[str] = ""
    tlsKey: Optional[FilePath | str] = ""
    tlsCert: Optional[FilePath | str] = ""
    port: Optional[PositiveInt] = 8080
    address: Optional[str] = sock.gethostbyname('localhost')
    log: Optional[models.Log] = models.Log.stdout
    enableThumbnails: Optional[bool] = False
    resizePreview: Optional[bool] = False
    enableExec: Optional[bool] = False
    typeDetectionByHeader: Optional[bool] = False
    authHook: Optional[str] = ""
    tokenExpirationTime: Optional[str] = ""

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = ".config.env"
        extra = "ignore"


class Config(BaseSettings):
    """Configuration settings [``config`` section] for the server.

    >>> Config

    """

    signup: Optional[bool] = False
    createUserDir: Optional[bool] = False
    userHomeBasePath: Optional[str] = os.path.join(os.path.expanduser('~'), 'users')
    defaults: Optional[Defaults] = Defaults()
    authMethod: Optional[str] = "json"
    authHeader: Optional[str] = ""
    branding: Optional[Branding] = Branding()
    tus: Optional[Tus] = Tus()
    commands: Optional[Commands] = Commands()
    shell_: Optional[List[str]] = []
    rules: Optional[List[str]] = []

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        env_file = ".config.env"
        extra = "ignore"


class Auther(BaseSettings):
    """Configuration settings [``server`` section] for the server.

    >>> Auther

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
