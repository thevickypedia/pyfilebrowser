from enum import StrEnum

from pydantic import BaseModel


class SortBy(StrEnum):
    name: str = "name"
    size: str = "size"
    modified: str = "modified"


class Sorting(BaseModel):
    by: str = "name"
    asc: bool = False


class Perm(BaseModel):
    admin: bool
    execute: bool
    create: bool
    rename: bool
    modify: bool
    delete: bool
    share: bool
    download: bool


def admin_perm():
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


def default_perm():
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
