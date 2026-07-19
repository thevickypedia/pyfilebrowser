import re
from typing import List, Optional, Tuple, Type

from pydantic import field_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from pyfilebrowser.modals import models, pydantic_config


def complexity_checker(password: str) -> None:
    """Verifies the strength of a secret/password.

    See Also:
        A password is considered strong if it at least has:

        - 8 characters
        - 1 digit
        - 1 symbol
        - 1 uppercase letter
        - 1 lowercase letter
    """
    # calculates the length
    assert (
        len(password) >= 8
    ), f"Minimum password length is 8, received: {len(password)}"

    # searches for digits
    assert re.search(r"\d", password), "Password must include an integer"

    # searches for uppercase
    assert re.search(
        r"[A-Z]", password
    ), "Password must include at least one uppercase letter"

    # searches for lowercase
    assert re.search(
        r"[a-z]", password
    ), "Password must include at least one lowercase letter"

    # searches for symbols
    assert re.search(
        r"[ !@#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password
    ), "Password must contain at least one special character"


class UserSettings(BaseSettings):
    """Profile settings for each user.

    >>> UserSettings

    Notes:
        - **id** - The id of the user.
        - **username** - Plain text username.
        - **password** - Plain text password.
        - **admin** - Boolean flag to indicate admin status. Permissions are set automatically based on this flag.
        - **scope** - The default scope for the users. Defaults to the root directory.
        - **locale** - The default locale for the users. Locale is an RFC 5646 language tag.
        - **lockPassword** - Default setting to prevent the user from changing the password.
        - **viewMode** - Default view mode for the users.
        - **singleClick** - Use single clicks to open files and directories.
        - **redirectAfterCopyMove** - Boolean flag to redirect after a copy/move operation.
        - **perm** - Permissions are set based on the admin flag for each user profile.
        - **commands** - List of commands that can be executed by the user.
        - **sorting** - Default sorting settings for the user.
        - **rules** - List of allow and disallow rules. This overrides the server's default rules.
        - **hideDotfiles** - Default setting to hide dotfiles.
        - **dateFormat** - Default setting to set the exact date format.
        - **aceEditorTheme** - The default setting to set the ace editor theme.
    """

    id: Optional[int] = None
    username: str
    password: str
    admin: Optional[bool] = False
    scope: Optional[str] = "/"
    locale: Optional[str] = "en"
    lockPassword: Optional[bool] = False
    viewMode: Optional[models.Listing] = models.Listing.list
    singleClick: Optional[bool] = False
    redirectAfterCopyMove: Optional[bool] = False
    perm: Optional[models.Perm | None] = None
    commands: Optional[List[str]] = []
    sorting: Optional[models.Sorting] = models.Sorting()
    rules: Optional[List[str]] = []
    hideDotfiles: Optional[bool] = False
    dateFormat: Optional[bool] = False
    aceEditorTheme: Optional[str] = ""

    @classmethod
    def from_vault(cls, table):
        """Create UserSettings object from vault table.

        Args:
            table: Vault tablename.

        Returns:
            UserSettings:
            Loads the ``UserSettings`` model.
        """
        # noinspection PyUnresolvedReferences
        return cls(
            **pydantic_config.normalize_vault_secrets(
                cls, pydantic_config.vault_client.get_table(table)
            )
        )

    @classmethod
    def from_env_file(cls, env_file: Optional[str]) -> "UserSettings":
        """Create UserSettings instance from environment file.

        Args:
            env_file: Name of the env file.

        Returns:
            UserSettings:
            Loads the ``UserSettings`` model.
        """
        return cls(_env_file=env_file)

    # noinspection PyMethodParameters
    @field_validator("password", mode="before")
    def validate_password(cls, value: str) -> str:
        """Field validator for password.

        Args:
            value: Value as entered by the user.

        Returns:
            str:
            Returns the validated password.
        """
        try:
            complexity_checker(value)
        except AssertionError as error:
            raise ValueError(error)
        return value

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[
        PydanticBaseSettingsSource,
        PydanticBaseSettingsSource,
        PydanticBaseSettingsSource,
    ]:
        """Customize order of settings' source.

        Args:
            settings_cls: Type of BaseSettings to customize.
            init_settings: Initialization settings.
            env_settings: Environment settings.
            dotenv_settings: Dotenv file settings.
            file_secret_settings: File secret settings.

        Returns:
            Tuple[PydanticBaseSettingsSource, PydanticBaseSettingsSource, PydanticBaseSettingsSource]:
            Returns a tuple of ordered settings.
        """
        # Exclude env_settings so only the .env file is used
        return (
            init_settings,
            dotenv_settings,
            file_secret_settings,
        )

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        extra = "ignore"
        hide_input_in_errors = True
