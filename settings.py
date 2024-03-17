import os
from typing import List

from pydantic import BaseModel, DirectoryPath, FilePath

from modals.config import ConfigSettings
from modals.users import UserSettings


class EnvConfig(BaseModel):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    user_settings: List[UserSettings] = [UserSettings()]
    config_settings: ConfigSettings = ConfigSettings()


class FileIO(BaseModel):
    base_dir: DirectoryPath = os.path.join('settings')
    config: FilePath = os.path.join(base_dir, 'config.json')
    users: FilePath = os.path.join(base_dir, 'users.json')


fileio = FileIO()

if not os.path.isdir(fileio.base_dir):
    os.mkdir(fileio.base_dir)
