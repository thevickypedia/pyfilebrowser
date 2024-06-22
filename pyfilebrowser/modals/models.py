import os
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel

SECRETS_PATH = (
    os.environ.get("SECRETS_PATH") or os.environ.get("secrets_path") or os.getcwd()
)


class Log(StrEnum):
    """Enum for different log options.

    >>> Log

    See Also:
        - Options are valid only for default/built-in logger.
        - Any custom logger passed during PyFilebrowser object init, will take precedence.
    """

    stdout: Optional[str] = "stdout"
    file: Optional[str] = "file"


class Theme(StrEnum):
    """Enum for different theme options.

    >>> Theme

    """

    light: Optional[str] = "light"
    dark: Optional[str] = "dark"
    blank: Optional[str] = ""


class Listing(StrEnum):
    """Enum for different listing options.

    >>> Listing

    """

    list: Optional[str] = "list"
    mosaic: Optional[str] = "mosaic"
    gallery: Optional[str] = "gallery"


class SortBy(StrEnum):
    """Enum for different sort-by options.

    >>> SortBy

    """

    name: str = "name"
    size: str = "size"
    modified: str = "modified"


class Sorting(BaseModel):
    """Enum for different sorting options.

    >>> Sorting

    """

    by: SortBy = SortBy.name
    asc: bool = False


class Perm(BaseModel):
    """Permission settings for each user profile.

    >>> Perm

    """

    admin: bool
    execute: bool
    create: bool
    rename: bool
    modify: bool
    delete: bool
    share: bool
    download: bool


def admin_perm() -> Perm:
    """Permission settings for the administrator.

    Returns:
        Perm:
        Returns the ``Perm`` object for the administrator.
    """
    return Perm(
        **{
            "admin": True,
            "execute": True,
            "create": True,
            "rename": True,
            "modify": True,
            "delete": True,
            "share": True,
            "download": True,
        }
    )


def default_perm() -> Perm:
    """Permission settings for (non-admin) users.

    Returns:
        Perm:
        Returns the ``Perm`` object for the default users.
    """
    return Perm(
        **{
            "admin": False,
            "execute": True,
            "create": True,
            "rename": False,
            "modify": False,
            "delete": False,
            "share": False,
            "download": True,
        }
    )
