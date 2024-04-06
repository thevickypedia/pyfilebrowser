import os
import pathlib
import re
import socket
from typing import Dict, List

import requests
from pydantic import BaseModel, FilePath, HttpUrl, field_validator
from pydantic_settings import BaseSettings

# noinspection LongLine
IP_REGEX = re.compile(
    r"""^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$"""  # noqa: E501
)


def public_ip_address() -> str:
    """Gets public IP address of the host using different endpoints.

    Returns:
        str:
        Public IP address.
    """
    opt1 = lambda fa: fa.text.strip()  # noqa: E731
    opt2 = lambda fa: fa.json()["origin"].strip()  # noqa: E731
    mapping = {
        'https://checkip.amazonaws.com/': opt1,
        'https://api.ipify.org/': opt1,
        'https://ipinfo.io/ip/': opt1,
        'https://v4.ident.me/': opt1,
        'https://httpbin.org/ip': opt2,
        'https://myip.dnsomatic.com/': opt1
    }
    for url, func in mapping.items():
        try:
            with requests.get(url) as response:
                return IP_REGEX.findall(func(response))[0]
        except (requests.RequestException, re.error, IndexError):
            continue


def private_ip_address() -> str | None:
    """Uses simple check on network id to see if it is connected to local host or not.

    Returns:
        str:
        Private IP address of host machine.
    """
    socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        socket_.connect(("8.8.8.8", 80))
    except OSError:
        return
    ip_address_ = socket_.getsockname()[0]
    socket_.close()
    return ip_address_


# noinspection HttpUrlsUsage
def allowance() -> List[HttpUrl]:
    """Gathers all the URLs that have to be allowed by the proxy server.

    Returns:
        List[HttpUrl]:
        Returns the list of allowable URLs.
    """
    base_origins = [f"http://{env_config.host}:{env_config.port}/"]
    if env_config.host == socket.gethostbyname('localhost'):
        base_origins.append(f"http://localhost:{env_config.port}/")
    if env_config.private_ip and (pri_ip_addr := private_ip_address()):
        base_origins.append(f"http://{pri_ip_addr}:{env_config.port}/")
    if env_config.public_ip and (pub_ip_addr := public_ip_address()):
        base_origins.append(f"http://{pub_ip_addr}:{env_config.port}/")
    return list(set(base_origins))  # If hosted on private ip and private_ip flag is set to true, then there'll be dupes


# noinspection PyPep8Naming
class destination(BaseModel):
    """Server's destination settings.

    >>> destination

    """

    url: HttpUrl
    auth_config: Dict[str, str]


class Session(BaseModel):
    """Object to store session information.

    >>> Session

    """

    info: dict = {}


class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    host: str = socket.gethostbyname('localhost')
    port: int = 8000
    workers: int = 1
    debug: bool = False
    origins: List[HttpUrl] = []
    public_ip: bool = False
    private_ip: bool = False
    error_page: FilePath = os.path.join(pathlib.PosixPath(__file__).parent, 'error.html')

    @field_validator('origins', mode='after', check_fields=True)
    def convert_to_string(cls, v, values, **kwargs):  # noqa
        """Validate origins' input as a URL, and convert as string when stored."""
        if v:
            return [str(i) for i in v]

    class Config:
        """Environment variables configuration."""

        env_file = ".proxy.env"
        extra = "ignore"


env_config = EnvConfig()
session = Session()
