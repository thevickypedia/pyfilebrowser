import logging
import math
import time
from http import HTTPStatus

from fastapi import HTTPException, Request

from pyfilebrowser.proxy import settings

LOGGER = logging.getLogger("proxy")


# noinspection PyUnresolvedReferences
class RateLimiter:
    """Object that implements the ``RateLimiter`` functionality.

    >>> RateLimiter

    """

    def __init__(self, rps: settings.RateLimit):
        """Instantiates the object with the necessary args.

        Args:
            rps: RateLimit object with ``max_requests`` and ``seconds``.

        Attributes:
            max_requests: Maximum requests to allow in a given time frame.
            seconds: Number of seconds after which the cache is set to expire.
        """
        self.max_requests = rps.max_requests
        self.seconds = rps.seconds
        self.start_time = time.time()
        self.exception = HTTPException(
            status_code=HTTPStatus.TOO_MANY_REQUESTS.value,
            detail=HTTPStatus.TOO_MANY_REQUESTS.phrase,
            # reset headers, which will invalidate auth token
            headers={"Retry-After": str(math.ceil(self.seconds))},
        )

    def init(self, request: Request) -> None:
        """Checks if the number of calls exceeds the rate limit for the given identifier.

        Args:
            request: The incoming request object.

        Raises:
            429: Too many requests.
        """
        if forwarded := request.headers.get("x-forwarded-for"):
            identifier = forwarded.split(",")[0]
        else:
            identifier = request.client.host
        identifier += ":" + request.url.path

        current_time = time.time()

        # Reset if the time window has passed
        if current_time - self.start_time > self.seconds:
            settings.session.rps[identifier] = 1
            self.start_time = current_time

        if settings.session.rps.get(identifier):
            if settings.session.rps[identifier] >= self.max_requests:
                raise self.exception
            else:
                settings.session.rps[identifier] += 1
        else:
            settings.session.rps[identifier] = 1
