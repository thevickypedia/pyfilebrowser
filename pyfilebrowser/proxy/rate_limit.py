import logging
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
    LOGGER.info("Initiating rate-limiter using redis")
    try:
        settings.RedisCache.pool = redis.ConnectionPool(
            host=settings.env_config.redis_host, port=settings.env_config.redis_port
        )
        # settings.RedisCache.pipeline =
    except Exception as error:
        LOGGER.critical(error)
    yield
    try:
        LOGGER.info("Closing redis connection")
        settings.RedisCache.pool.reset()
        settings.RedisCache.pool.close()
    except Exception as error:
        LOGGER.critical(error)


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

    def decider(self, key: str) -> bool:
        """Decision engine to allow or restrict incoming request.

        Args:
            key: Key stored in the datastore.

        Returns:
            bool:
            Boolean value to indicate the decision.
        """
        current = int(time.time())
        window_start = current - self.seconds
        pipeline = redis.Redis(connection_pool=settings.RedisCache.pool).pipeline()
        with pipeline as pipe:
            try:
                pipe.zremrangebyscore(key, 0, window_start)
                pipe.zcard(key)
                pipe.zadd(key, {str(current): current})
                pipe.expire(key, self.seconds)
                results = pipe.execute()
            except redis.RedisError as error:
                LOGGER.error(error)
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f"Redis error: {str(error)}"
                ) from error
        return results[1] + 1 > self.max_requests

    def rate_limit(self, request: Request) -> None:
        """Rate limit function to add as dependency.

        Args:
            request: Incoming request object.

        Raises:
            429: Too many requests.
        """
        # todo: return a FileResponse with Jinja templated error page
        if self.decider(f"rate_limit:{request.client.host}"):
            LOGGER.warning("Too many attempts from %s", request.client.host)
            raise HTTPException(
                status_code=HTTPStatus.TOO_MANY_REQUESTS.real,
                detail=HTTPStatus.TOO_MANY_REQUESTS.phrase
            )
