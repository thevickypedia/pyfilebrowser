from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class Log(StrEnum):
    """Enum for different log options.

    >>> Log

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

    by: str = "name"
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
    return Perm(**{
        "admin": True,
        "execute": True,
        "create": True,
        "rename": True,
        "modify": True,
        "delete": True,
        "share": True,
        "download": True
    })


def default_perm() -> Perm:
    """Permission settings for (non-admin) users.

    Returns:
        Perm:
        Returns the ``Perm`` object for the default users.
    """
    return Perm(**{
        "admin": False,
        "execute": True,
        "create": True,
        "rename": False,
        "modify": False,
        "delete": False,
        "share": True,
        "download": True
    })
