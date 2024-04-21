import os
import pathlib
import re
import socket
from typing import Dict, List, Set

import requests
from pydantic import (BaseModel, Field, FilePath, HttpUrl, PositiveInt,
                      field_validator)
from pydantic_settings import BaseSettings

# noinspection LongLine
IP_REGEX = re.compile(
    r"""^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])$"""  # noqa: E501
)
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
ALLOWED_HEADERS = ['content-length', 'dnt', 'cookie', 'authorization', 'accept', 'sec-fetch-user', 'sec-fetch-site',
                   'connection', 'user-agent', 'origin', 'sec-ch-ua-mobile', 'tus-resumable', 'content-type',
                   'cache-control', 'sec-ch-ua-platform', 'accept-language', 'sec-fetch-mode', 'referer', 'host',
                   'upload-offset', 'if-range', 'sec-ch-ua', 'accept-encoding', 'range', 'upgrade-insecure-requests',
                   'sec-fetch-dest', 'x-auth', 'x-forwarded-host']


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
    base_origins = set()
    base_origins.add(env_config.host)
    if env_config.host == socket.gethostbyname('localhost'):
        base_origins.add("localhost")
        base_origins.add("0.0.0.0")
    if env_config.private_ip and (pri_ip_addr := private_ip_address()):
        base_origins.add(pri_ip_addr)
    if env_config.public_ip and (pub_ip_addr := public_ip_address()):
        base_origins.add(pub_ip_addr)
    return list(base_origins)


class Destination(BaseModel):
    """Server's destination settings.

    >>> Destination

    """

    url: HttpUrl
    auth_config: Dict[str, str]


class Session(BaseModel):
    """Object to store session information.

    >>> Session

    """

    auth_counter: Dict[str, int] = {}
    forbid: Set[str] = set()

    info: Dict[str, str] = {}
    rps: Dict[str, int] = {}
    allowed_origins: Set[str] = set()


class RateLimit(BaseModel):
    """Object to store the rate limit settings.

    >>> RateLimit

    """

    max_requests: PositiveInt
    seconds: PositiveInt


class EnvConfig(BaseSettings):
    """Configure all env vars and validate using ``pydantic`` to share across modules.

    >>> EnvConfig

    """

    host: str = socket.gethostbyname('localhost')
    port: PositiveInt = 8000
    workers: PositiveInt = 1
    debug: bool = False
    origins: List[HttpUrl] = []
    database: str = Field("auth.db", pattern=".*.db$")
    public_ip: bool = False
    private_ip: bool = False
    origin_refresh: PositiveInt | None = None
    rate_limit: RateLimit | List[RateLimit] = []
    error_page: FilePath = os.path.join(pathlib.PosixPath(__file__).parent, 'error.html')

    # noinspection PyMethodParameters,PyUnusedLocal
    @field_validator('origins', mode='after', check_fields=True)
    def origins_url_checker(cls, v: List[HttpUrl]) -> List[str] | List:
        """Validate origins' input as a URL, and stores only the host part of the URL."""
        if v:
            return list(set([i.host for i in v]))
        return []

    # noinspection PyMethodParameters,PyUnusedLocal
    @field_validator('rate_limit', mode='after', check_fields=True)
    def rate_limit_checker(cls, v: RateLimit | List[RateLimit], values, **kwargs) -> List[RateLimit] | List:
        """Validate origins' input as a URL, and convert as string when stored."""
        if not isinstance(v, list):
            v = [v]
        return v

    class Config:
        """Environment variables configuration."""

        env_file = ".proxy.env"
        extra = "ignore"


env_config = EnvConfig()
session = Session()
destination = Destination
