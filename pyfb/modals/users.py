from typing import List, Union

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from pyfb.modals.models import Perm, Sorting


class Authentication(BaseModel):
    username: str
    password: str
    admin: bool = False


class UserSettings(BaseSettings):
    authentication: Authentication = Authentication(username="admin", password="admin", admin=True)
    scope: str = "/"
    locale: str = "en"
    lockPassword: bool = False
    viewMode: str = "list"
    singleClick: bool = False
    perm: Union[Perm, None] = None
    commands: List[str] = []
    sorting: Sorting = Sorting()
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
