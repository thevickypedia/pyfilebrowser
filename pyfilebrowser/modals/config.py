import os.path
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

    References:
        - A custom CSS file can be used to style the application. The file should be placed in the ``files`` directory.
            - `samples/custom.css <https://github.com/thevickypedia/pyfilebrowser/blob/main/samples/custom.css>`__

    Notes:
        - **name** - Instance name that will show up on login and signup pages.
        - **disableExternal** - This will disable any external links.
        - **disableUsedPercentage** - Disables the used volume percentage.
        - **files** - The path to the branding files.
            - custom.css, containing the styles you want to apply to your installation.
            - img a directory whose files can replace the default logotypes in the application
        - **theme** - The theme of the brand. Uses system default if not set.
        - **color** - The color of the brand.
    """

    name: Optional[str] = "PyFilebrowser"
    disableExternal: Optional[bool] = False
    disableUsedPercentage: Optional[bool] = False
    files: Optional[DirectoryPath] = ""
    theme: Optional[models.Theme] = models.Theme.blank
    color: Optional[str] = ""

    class Config:
        """Environment variables configuration."""

        env_prefix = "branding_"
        env_file = os.path.join(models.SECRETS_PATH, ".config.env")
        extra = "ignore"


class Tus(BaseSettings):
    """Configuration for the upload settings in the server.

    >>> Tus

    See Also:
        Environment variables should be prefixed with ``tus_``, and present in ``.config.env``

    Notes:
        - **chunkSize** - The size of the chunks to be uploaded.
        - **retryCount** - The number of retries to be made in case of a failure.
    """

    chunkSize: Optional[PositiveInt] = 10 * 1024 * 1024  # Defaults to 10 MB
    retryCount: Optional[PositiveInt] = 5

    class Config:
        """Environment variables configuration."""

        env_prefix = "tus_"
        env_file = os.path.join(models.SECRETS_PATH, ".config.env")
        extra = "ignore"


class Defaults(BaseSettings):
    """Configuration for all the default settings for the server.

    >>> Defaults

    See Also:
        Environment variables should be prefixed with ``defaults_``, and present in ``.config.env``

    Notes:
        - **scope** - The default scope for the users. Defaults to the root directory.
        - **locale** - The default locale for the users. Locale is an RFC 5646 language tag.
        - **viewMode** - The default view mode for the users.
        - **singleClick** - The default single click setting for the users.
        - **sorting** - The default sorting settings for the users.
        - **perm** - The default permission settings for the users.
        - **commands** - The default list of commands that can be executed by users.
        - **hideDotfiles** - The default setting to hide dotfiles.
        - **dateFormat** - The default setting to set the exact date format.
    """

    scope: Optional[str] = "."
    locale: Optional[str] = "en"
    viewMode: Optional[models.Listing] = models.Listing.list
    singleClick: Optional[bool] = False
    sorting: models.Sorting = models.Sorting()
    perm: models.Perm = models.default_perm()
    commands: Optional[List[str]] = []
    hideDotfiles: Optional[bool] = True
    dateFormat: Optional[bool] = False

    class Config:
        """Environment variables configuration."""

        env_prefix = "defaults_"
        env_file = os.path.join(models.SECRETS_PATH, ".config.env")
        extra = "ignore"


class Commands(BaseSettings):
    """Configuration for list of the commands to be executed before or after a certain event.

    >>> Commands

    See Also:
        The command runner is a feature that enables you to execute shell commands before or after a certain event.

    Notes:
        - **after_copy** - List of commands to be executed after copying a file.
        - **after_delete** - List of commands to be executed after deleting a file.
        - **after_rename** - List of commands to be executed after renaming a file.
        - **after_save** - List of commands to be executed after saving a file.
        - **after_upload** - List of commands to be executed after uploading a file.
        - **before_copy** - List of commands to be executed before copying a file.
        - **before_delete** - List of commands to be executed before deleting a file.
        - **before_rename** - List of commands to be executed before renaming a file.
        - **before_save** - List of commands to be executed before saving a file.
        - **before_upload** - List of commands to be executed before uploading a file.
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
        env_file = os.path.join(models.SECRETS_PATH, ".config.env")
        extra = "ignore"


class ReCAPTCHA(BaseModel):
    """Settings for ReCaptcha.

    >>> ReCAPTCHA

    Notes:
        - **host** - The host for the ReCaptcha.
        - **key** - The key for the ReCaptcha.
        - **secret** - The secret for the ReCaptcha.
    """

    host: Optional[HttpUrl]
    key: Optional[str]
    secret: Optional[str]


class Server(BaseSettings):
    """Configuration settings [``server`` section] for the server.

    >>> Server

    Notes:
        - **root** - The root directory for the server. Contents of this directory will be served.
        - **baseURL** - The base URL for the server.
        - **socket** - Socket to listen to (cannot be used with ``address``, ``port`` or TLS settings)
        - **tlsKey** - The TLS key for the server.
        - **tlsCert** - The TLS certificate for the server.
        - **port** - The port for the server.
        - **address** - Address to listen on. Defaults to ``127.0.0.1``
        - **log** - The log settings for the server.
        - **enableThumbnails** - Enable thumbnails for the server.
        - **resizePreview** - Resize the preview for the server.
        - **enableExec** - Enable command execution for the server.
        - **typeDetectionByHeader** - Enable type detection by header for the server.
        - **authHook** - The authentication hook for the server.
        - **tokenExpirationTime** - The token expiration time for the server.
          A duration string is a signed sequence of decimal numbers, each with optional fraction and a unit suffix.
          Examples "300ms", "-1.5h" or "2h45m". Valid time units are "ns", "us" (or "µs"), "ms", "s", "m", "h".
    """

    root: DirectoryPath
    baseURL: Optional[str] = ""
    socket: Optional[str] = ""
    tlsKey: Optional[FilePath | str] = ""
    tlsCert: Optional[FilePath | str] = ""
    port: Optional[PositiveInt] = 8080
    address: Optional[str] = sock.gethostbyname("localhost")
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
        env_file = os.path.join(models.SECRETS_PATH, ".config.env")
        extra = "ignore"


class Config(BaseSettings):
    """Configuration settings [``config`` section] for the server.

    >>> Config

    Notes:
        - **signup** - Enable signup option for new users.
        - **createUserDir** - Auto create user home dir while adding new user.
        - **userHomeBasePath** - The base path for user home directories.
        - **defaults** - The default settings for the server.
        - **authMethod** - The authentication method for the server.
        - **authHeader** - The authentication header for the server.
        - **branding** - The branding settings for the server.
        - **tus** - The upload settings for the server.
        - **commands** - The command settings for the server.
        - **shell_** - The shell settings for the server.
        - **rules** - This is a global set of allow and disallow rules. They apply to every user.
          You can define specific rules on each user's settings to override these. Supports regex.
    """

    signup: Optional[bool] = False
    createUserDir: Optional[bool] = False
    userHomeBasePath: Optional[DirectoryPath] = None
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
        env_file = os.path.join(models.SECRETS_PATH, ".config.env")
        extra = "ignore"


class Auther(BaseSettings):
    """Configuration settings [``server`` section] for the server.

    >>> Auther

    See Also:
        Environment variables should be prefixed with ``auth_``, and present in ``.config.env``

    Notes:
        - **recaptcha** - ReCaptcha settings for the server.
    """

    recaptcha: Optional[ReCAPTCHA] = None

    class Config:
        """Environment variables configuration."""

        env_prefix = "auth_"
        env_file = os.path.join(models.SECRETS_PATH, ".config.env")
        extra = "ignore"


class ConfigSettings(BaseModel):
    """Wrapper for all the configuration settings to form a nested JSON object.

    >>> ConfigSettings

    """

    settings: Config = Config()
    server: Server = Server()
    auther: Auther = Auther()
