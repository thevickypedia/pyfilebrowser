import gzip
import logging
import os
import platform
import shutil
import stat
import tarfile
import zipfile
from typing import Any, List, Tuple, Type

import requests
from pydantic import BaseModel, FilePath
from pydantic.fields import FieldInfo
from pydantic_settings import (BaseSettings, EnvSettingsSource,
                               PydanticBaseSettingsSource, SettingsConfigDict)


class ExtendedEnvSettingsSource(EnvSettingsSource):
    """Customized environment settings source that allows specifying multiple prefixes for environmental variables.

    >>> ExtendedEnvSettingsSource

    """

    def get_field_value(self, field: FieldInfo, field_name: str) -> Tuple[Any, str, bool]:
        """Retrieves the field value from the environment with support for multiple prefixes.

        Args:
            field: Information about the field.
            field_name: Name of the field.

        Returns:
            Tuple[Any, str, bool]:
            Retrieved value, field key, and a boolean indicating whether the value is complex.
        """
        # noinspection PyTypedDict
        if prefixes := self.config.get("env_prefixes", []):
            for prefix in prefixes:
                self.env_prefix = prefix
                env_val, field_key, value_is_complex = super().get_field_value(field, field_name)
                if env_val is not None:
                    return env_val, field_key, value_is_complex

        return super().get_field_value(field, field_name)


class ExtendedSettingsConfigDict(SettingsConfigDict, total=False):
    """Configuration dictionary extension to support additional settings.

    >>> ExtendedSettingsConfigDict

    Attributes:
        env_prefixes (List[str] | None): List of environment variable prefixes to consider.
    """

    env_prefixes: List[str] | None


class ExtendedBaseSettings(BaseSettings):
    """Base settings class extension to customize settings sources.

    >>> ExtendedBaseSettings

    Methods:
        settings_customise_sources: Customizes settings sources for the extended settings class.
    """

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Customizes the settings sources for the extended settings class.

        Args:
            settings_cls: The extended settings class.
            init_settings: Settings source for initialization.
            env_settings: Settings source for environment variables.
            dotenv_settings: Settings source for dotenv files.
            file_secret_settings: Settings source for secret files.

        Returns:
            Tuple[PydanticBaseSettingsSource, ...]:
            Tuple of customized settings sources.
        """
        return (ExtendedEnvSettingsSource(settings_cls),)


class GitHub(ExtendedBaseSettings):
    """Custom GitHub account information loaded using multiple env prefixes.

    >>> GitHub

    References:
        https://github.com/pydantic/pydantic/discussions/4319

    See Also:
        - This model is to load GitHub arguments, which is used to download the appropriate asset from source control.
        - Dot env ``(.env)`` files are not supported. Regular env variables are required.
    """

    model_config = ExtendedSettingsConfigDict(
        env_prefixes=["git_", "github_", "filebrowser_"]
    )

    owner: str = "filebrowser"
    repo: str = "filebrowser"
    token: str | None = None
    version: str = "latest"


class Executable(BaseModel):
    """Executable object to load all the objects to download the executable from releases.

    >>> Executable

    """

    filebrowser_bin: FilePath = "filebrowser"
    filebrowser_dl_ext: str = ".tar.gz"

    # Detect OS and architecture
    system: str = platform.system().lower()
    machine: str = platform.machine().lower()
    if system == "darwin":
        filebrowser_os: str = "darwin"
    elif system == "linux":
        filebrowser_os: str = "linux"
    elif system == "freebsd":
        filebrowser_os: str = "freebsd"
    elif system == "netbsd":
        filebrowser_os: str = "netbsd"
    elif system == "openbsd":
        filebrowser_os: str = "openbsd"
    elif system.startswith("win") or system == "msys":
        filebrowser_os: str = "windows"
        filebrowser_bin: FilePath = "filebrowser.exe"
        filebrowser_dl_ext: str = ".zip"
    else:
        raise OSError(
            f"Aborted, unsupported or unknown OS: {system}"
        )

    if "aarch64" in machine:
        filebrowser_arch: str = "arm64"
    elif "64" in machine:
        filebrowser_arch: str = "amd64"
    elif "86" in machine:
        filebrowser_arch: str = "386"
    elif "armv5" in machine:
        filebrowser_arch: str = "armv5"
    elif "armv6" in machine:
        filebrowser_arch: str = "armv6"
    elif "armv7" in machine:
        filebrowser_arch: str = "armv7"
    else:
        raise OSError(
            f"Aborted, unsupported or unknown architecture: {machine}"
        )

    filebrowser_file: FilePath = f"{filebrowser_os}-{filebrowser_arch}-filebrowser{filebrowser_dl_ext}"
    filebrowser_db: FilePath = f"{filebrowser_bin}.db"


executable = Executable()


def binary(logger: logging.Logger, github: GitHub) -> None:
    """Downloads the latest released binary asset.

    Args:
        logger: Bring your own logger.
        github: Custom GitHub source configuration.
    """
    logger.info("Source Repository: 'https://github.com/%s/%s'", github.owner, github.repo)
    logger.info("Targeted Asset: '%s'", executable.filebrowser_file)
    headers = {"Authorization": f"Bearer {github.token}"} if github.token else {}
    # Get the release from the specified version
    if github.version == "latest":
        release_url = f"https://api.github.com/repos/{github.owner}/{github.repo}/releases/{github.version}"
    else:
        release_url = f"https://api.github.com/repos/{github.owner}/{github.repo}/releases/tags/{github.version}"
    response = requests.get(release_url, headers=headers)
    response.raise_for_status()
    release_info = response.json()

    # Log the download URL
    filebrowser_url = f"https://github.com/{github.owner}/{github.repo}/releases/download/" \
                      f"{release_info['tag_name']}/{executable.filebrowser_file}"
    logger.info("Download URL: %s", filebrowser_url)

    # Get asset id
    existing = []
    for asset in release_info['assets']:
        if asset.get('name') == executable.filebrowser_file:
            asset_id = asset['id']
            break
        elif asset.get('name'):
            existing.append(asset['name'])
    else:
        existing = '\n\t'.join(existing)
        raise Exception(
            f"\n\tFailed to get the asset id for {executable.filebrowser_file!r}\n\n"
            f"Available asset names:\n\t{existing}"
        )

    # Download the asset
    headers['Accept'] = "application/octet-stream"
    response = requests.get(f"https://api.github.com/repos/{github.owner}/{github.repo}/releases/assets/{asset_id}",
                            headers=headers)
    response.raise_for_status()
    with open(executable.filebrowser_file, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    assert os.path.isfile(executable.filebrowser_file), f"Failed to get the asset id for {executable.filebrowser_file}"
    logger.info("Asset has been downloaded successfully")

    # Extract asset based on the file extension
    if executable.filebrowser_file.endswith(".tar.gz"):
        tar_file = executable.filebrowser_file.removesuffix('.gz')
        # Read the gzipped file as bytes, and write as a tar file (.tar.gz -> .tar)
        with gzip.open(executable.filebrowser_file, 'rb') as f_in:
            with open(tar_file, 'wb') as f_out:
                f_out.write(f_in.read())
                f_out.flush()
        assert os.path.isfile(tar_file), f"Failed to gunzip {executable.filebrowser_file}"
        os.remove(executable.filebrowser_file)

        # Read the tar file and extract its content
        with tarfile.open(tar_file, 'r') as tar:
            tar.extractall()
        # Catches the use case where binary might be directly archived
        if os.path.isfile(executable.filebrowser_bin):
            return
        content_dir = tar_file.removesuffix('.tar')
        assert os.path.isdir(content_dir) and os.path.isfile(os.path.join(content_dir, executable.filebrowser_bin)), \
            f"Failed to unarchive {tar_file}"
        os.remove(tar_file)
    elif executable.filebrowser_file.endswith(".zip"):
        # Read the zip file and extract its content
        with zipfile.ZipFile(executable.filebrowser_file, 'r') as zip_ref:
            zip_ref.extractall()
        # Catches the use case where binary might be directly zipped
        if os.path.isfile(executable.filebrowser_bin):
            return
        content_dir = executable.filebrowser_file.removesuffix(".zip")
        assert os.path.isdir(content_dir) and os.path.isfile(os.path.join(content_dir, executable.filebrowser_bin)), \
            f"Failed to unzip {executable.filebrowser_file}"
        os.remove(executable.filebrowser_file)
    else:
        raise OSError(
            f"Invalid filename: {executable.filebrowser_file}"
        )

    # Copy the executable out of the extracted directory and remove the extraction directory
    shutil.copyfile(os.path.join(content_dir, executable.filebrowser_bin),
                    os.path.join(os.getcwd(), executable.filebrowser_bin))
    shutil.rmtree(content_dir)

    # Change file permissions and set as executable
    # os.chmod(executable.filebrowser_bin, 0o755)
    # basically, chmod +x => -rwxr-xr-x
    os.chmod(executable.filebrowser_bin, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    logger.info("Asset %s is ready to be used", executable.filebrowser_bin)
