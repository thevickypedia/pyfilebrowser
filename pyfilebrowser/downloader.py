import gzip
import logging
import os
import platform
import shutil
import stat
import tarfile
import zipfile

import requests
from pydantic import BaseModel, FilePath


class Executable(BaseModel):
    """Executable object to load all the objects to download the executable from releases.

    >>> Executable

    """

    binary: FilePath = "filebrowser"
    database: FilePath = f"{binary}.db"
    extension: str = ".tar.gz"

    system: str = platform.system().lower()
    if system == "darwin":
        filemanager_os: str = "Darwin-x86_64"
    elif system == "linux":
        filemanager_os: str = "Linux-x86_64"
    elif system.startswith("win") or system == "msys":
        filemanager_os: str = "Windows-x86_64"
        extension: str = ".zip"
        binary += ".exe"
    else:
        raise Exception(f"Aborted, unsupported or unknown OS: {system}")
    filemanager_file: FilePath = f"FileBrowser-{filemanager_os}{extension}"


executable = Executable()


def download_asset(logger: logging.Logger) -> None:
    """Downloads the latest released asset.

    Args:
        logger: Bring your own logger.
    """
    git_token = os.environ.get("GIT_TOKEN")
    headers = {"Authorization": f"Bearer {git_token}"} if git_token else {}
    # Get the latest release
    response = requests.get("https://api.github.com/repos/thevickypedia/filebrowser/releases/latest",
                            headers=headers)
    response.raise_for_status()
    release_info = response.json()

    # Print the download URL, to download manually
    filemanager_url = f"https://github.com/thevickypedia/filebrowser/releases/download/" \
                      f"{release_info['tag_name']}/{executable.filemanager_file}"
    logger.info(f"Download URL: {filemanager_url}")

    # Get asset id
    for asset in release_info['assets']:
        if asset.get('name') == executable.filemanager_file:
            asset_id = asset['id']
            break
    else:
        raise Exception(f"Failed to get the asset id for {executable.filemanager_file}")

    # Download the asset
    headers['Accept'] = "application/octet-stream"
    response = requests.get(f"https://api.github.com/repos/thevickypedia/filebrowser/releases/assets/{asset_id}",
                            headers=headers)
    response.raise_for_status()
    with open(executable.filemanager_file, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    assert os.path.isfile(executable.filemanager_file), f"Failed to get the asset id for {executable.filemanager_file}"
    logger.info("Asset has been downloaded successfully")

    # Extract asset based on the file extension
    if executable.filemanager_file.endswith(".tar.gz"):
        tar_file = executable.filemanager_file.rstrip('.gz')
        # Read the gzipped file as bytes, and write as a tar file (.tar.gz -> .tar)
        with gzip.open(executable.filemanager_file, 'rb') as f_in:
            with open(tar_file, 'wb') as f_out:
                f_out.write(f_in.read())
                f_out.flush()
        assert os.path.isfile(tar_file), f"Failed to gunzip {executable.filemanager_file}"
        os.remove(executable.filemanager_file)

        # Read the tar file and extract it in the current working directory
        content_dir = tar_file.rstrip('.tar')
        with tarfile.open(tar_file, 'r') as tar:
            tar.extractall()
        assert os.path.isdir(content_dir) and os.path.isfile(os.path.join(content_dir, executable.binary)), \
            f"Failed to unarchive {tar_file}"
        os.remove(tar_file)
    elif executable.filemanager_file.endswith(".zip"):
        # Read the zip file and extract it in the current working directory
        content_dir = executable.filemanager_file.rstrip(".zip")
        with zipfile.ZipFile(executable.filemanager_file, 'r') as zip_ref:
            zip_ref.extractall()
        assert os.path.isdir(content_dir) and os.path.isfile(os.path.join(content_dir, executable.binary)), \
            f"Failed to unzip {executable.filemanager_file}"
        os.remove(executable.filemanager_file)
    else:
        raise OSError(
            f"Invalid filename: {executable.filemanager_file}"
        )

    # Copy the executable out of the extracted directory and remove the extraction directory
    shutil.copyfile(os.path.join(content_dir, executable.binary), os.path.join(os.getcwd(), executable.binary))
    shutil.rmtree(content_dir)

    # Change file permissions and set as executable
    # os.chmod(executable.binary, 0o755)
    # basically, chmod +x => -rwxr-xr-x
    os.chmod(executable.binary, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)

    logger.info(f"Asset {executable.binary!r} is ready to be used")
