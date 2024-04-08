import logging
import math
import time
from contextlib import asynccontextmanager
from http import HTTPStatus

import redis
from fastapi import FastAPI, HTTPException, Request

from pyfilebrowser.proxy import settings

LOGGER = logging.getLogger('proxy')


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Uses a redis connection to initialize rate limiter.

    See Also:
        - Initiates the redis connection during API startup.
        - Closes the redis connection during API shutdown.

    References:
        `FastAPI LifeSpan <https://fastapi.tiangolo.com/advanced/events/#lifespan>`__
    """
    yield
    try:
        LOGGER.info("Closing redis connection")
        settings.RedisCache.pool.reset()
        settings.RedisCache.pool.close()
    except Exception as exc:
        LOGGER.critical(exc)


def ping_redis() -> bool:
    """Pings the redis server and returns the response.

    Returns:
        bool:
        Returns a boolean value to indicate the availability.
    """
    try:
        return redis.Redis(host=settings.env_config.redis_host,
                           port=settings.env_config.redis_port).ping()
    except redis.ConnectionError as exc:
        LOGGER.warning(exc)
        return False


class RateLimit:
    """Object that implements the ``RateLimit`` functionality.

    >>> RateLimit

    """

    def __init__(self, max_requests: int, seconds: int):
        """Instantiates the object with the necessary args.

        Args:
            max_requests: Maximum requests to allow in a given time frame.
            seconds: Number of seconds after which the cache is set to expire.
        """
        self.max_requests = max_requests
        self.seconds = seconds
        LOGGER.info("Initiating rate-limiter using redis")
        self.pool = redis.ConnectionPool(
            host=settings.env_config.redis_host, port=settings.env_config.redis_port
        )
        settings.RedisCache.pool = self.pool

    def decider(self, key: str) -> bool:
        """Decision engine to allow or restrict incoming request.

        Args:
            key: Key stored in the datastore.

        Returns:
            bool:
            Boolean value to indicate the decision.
        """
        current = time.time()
        window_start = current - self.seconds
        pipeline = redis.Redis(connection_pool=self.pool).pipeline()
        with pipeline as pipe:
            try:
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {str(current): current})
                pipe.expire(key, self.seconds)
                results = pipe.execute()
            except redis.RedisError as exc:
                LOGGER.error(exc)
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f"Redis error: {str(exc)}"
                ) from exc
        return results[1] + 1 > self.max_requests

    def rate_limit(self, request: Request) -> None:
        """Rate limit function to add as dependency.

        Args:
            request: Incoming request object.

        Raises:
            429: Too many requests.
        """
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            identifier = forwarded.split(",")[0]
        else:
            identifier = request.client.host
        if self.decider(f"rate_limit:{identifier}"):
            LOGGER.warning("Too many attempts from %s", request.client.host)
            raise HTTPException(
                status_code=HTTPStatus.TOO_MANY_REQUESTS.value,
                detail=HTTPStatus.TOO_MANY_REQUESTS.phrase,
                headers={"Retry-After": str(math.ceil(self.seconds))}
            )
