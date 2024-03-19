from typing import List, Union

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from pyfilebrowser.modals import models


class Authentication(BaseModel):
    """Authentication settings for each user profile.

    >>> models.Perm

    """

    username: str
    password: str
    admin: bool = False


class UserSettings(BaseSettings):
    """Profile settings for each user.

    >>> UserSettings

    """

    authentication: Authentication = Authentication(username="admin", password="admin", admin=True)
    scope: str = "/"
    locale: str = "en"
    lockPassword: bool = False
    viewMode: str = "list"
    singleClick: bool = False
    perm: Union[models.Perm, None] = None
    commands: List[str] = []
    sorting: models.Sorting = models.Sorting()
    rules: List[str] = []
    hideDotfiles: bool = False
    dateFormat: bool = False

    @classmethod
    def from_env_file(cls, env_file: str):
        """Create UserSettings instance from environment file."""
        return cls(_env_file=env_file)

    class Config:
        """Environment variables configuration."""

        env_prefix = ""
        extra = "ignore"
