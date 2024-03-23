from typing import List, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from pyfilebrowser.modals import models


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

    See Also:
        - **perm** - Permissions are set based on the admin flag for each ``Authentication`` model.
    """

    authentication: Optional[Authentication] = Authentication(username="admin", password="admin", admin=True)
    scope: Optional[str] = "/"
    locale: Optional[str] = "en"
    lockPassword: Optional[bool] = False
    viewMode: Optional[str] = "list"
    singleClick: Optional[bool] = False
    perm: Optional[models.Perm | None] = None
    commands: Optional[List[str]] = []
    sorting: Optional[models.Sorting] = models.Sorting()
    rules: Optional[List[str]] = []
    hideDotfiles: Optional[bool] = False
    dateFormat: Optional[bool] = False

    @classmethod
    def from_env_file(cls, env_file: Optional[str]) -> 'UserSettings':
        """Create UserSettings instance from environment file.

        Args:
            env_file: Name of the env file.

        Returns:
            UserSettings:
            Loads the ``UserSettings`` model.
        """
        return cls(_env_file=env_file)

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        extra = "ignore"
