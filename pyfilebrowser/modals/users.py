import re
from typing import Dict, List, Optional

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings

from pyfilebrowser.modals import models


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
    assert len(password) >= 8, "Minimum password length is 8"

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
        r"[ !#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password
    ), "Password must contain at least one special character"


class Authentication(BaseModel):
    """Authentication settings for each user profile.

    >>> models.Perm

    """

    username: Optional[str]
    password: Optional[str]
    admin: Optional[bool] = False


class UserSettings(BaseSettings):
    """Profile settings for each user.

    >>> UserSettings

    Notes:
        - **authentication** - Authentication settings for each user profile.
        - **scope** - The default scope for the users. Defaults to the root directory.
        - **locale** - The default locale for the users. Locale is an RFC 5646 language tag.
        - **lockPassword** - Default setting to prevent the user from changing the password.
        - **viewMode** - Default view mode for the users.
        - **singleClick** - Use single clicks to open files and directories.
        - **perm** - Permissions are set based on the admin flag for each ``Authentication`` model.
        - **commands** - List of commands that can be executed by the user.
        - **sorting** - Default sorting settings for the user.
        - **rules** - List of allow and disallow rules. This overrides the server's default rules.
        - **hideDotfiles** - Default setting to hide dotfiles.
        - **dateFormat** - Default setting to set the exact date format.
    """

    authentication: Optional[Authentication] = Authentication(
        username="admin", password="admin", admin=True
    )
    scope: Optional[str] = "/"
    locale: Optional[str] = "en"
    lockPassword: Optional[bool] = False
    viewMode: Optional[models.Listing] = models.Listing.list
    singleClick: Optional[bool] = False
    perm: Optional[models.Perm | None] = None
    commands: Optional[List[str]] = []
    sorting: Optional[models.Sorting] = models.Sorting()
    rules: Optional[List[str]] = []
    hideDotfiles: Optional[bool] = False
    dateFormat: Optional[bool] = False

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
    @field_validator("authentication", mode="before")
    def validate_password_complexity(
        cls, value: Authentication
    ) -> Authentication | Dict:
        """Field validator for password.

        Args:
            value: Value as entered by the user.

        Returns:
            Authentication | Dict:
            Returns an ``Authentication`` object or a dictionary with the authentication payload.
        """
        if isinstance(value, Authentication):
            passwd = value.password
        elif isinstance(value, dict):
            passwd = value.get("password")
        else:
            raise ValueError(f"unknown type ({type(value)})")
        try:
            complexity_checker(passwd)
        except AssertionError as error:
            raise ValueError(error)
        return value

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        extra = "ignore"
