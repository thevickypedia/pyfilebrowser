import contextlib
import logging.config

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from pyfilebrowser.proxy import main, rate_limit, repeated_timer, settings


class ProxyServer(uvicorn.Server):
    """Shared ProxyServer state that is available between all protocol instances.

    >>> ProxyServer

    References:
        https://github.com/encode/uvicorn/issues/742#issuecomment-674411676
    """

    @contextlib.contextmanager
    def run_in_parallel(self, logger: logging.Logger) -> None:
        """Initiates the server in a dedicated process.

        Args:
            logger: Server's original logger.

        See Also:
            - Initiates a background task to refresh the allowed origins at given interval.
        """
        uvicorn_error = logging.getLogger("uvicorn.error")
        uvicorn_error.disabled = True
        uvicorn_error.propagate = False
        uvicorn_access = logging.getLogger("uvicorn.access")
        uvicorn_access.disabled = True
        uvicorn_access.propagate = False
        assert logger.name == "proxy"
        timer = None
        if settings.env_config.origin_refresh and (
            settings.env_config.allow_private_ip or settings.env_config.allow_public_ip
        ):
            timer = repeated_timer.RepeatedTimer(
                function=main.refresh_allowed_origins,
                interval=settings.env_config.origin_refresh,
            )
            logger.info(
                "Initiating the background task '%s' with interval %d seconds",
                timer.function.__name__,
                timer.interval.real,
            )
            timer.start()
        try:
            self.run()
        except KeyboardInterrupt:
            if timer:
                logger.info(
                    "Stopping the background task '%s'", timer.function.__name__
                )
                timer.stop()
        finally:
            logger.info("Proxy service terminated")


def proxy_server(server: str, log_config: dict) -> None:
    """Triggers the proxy engine in parallel.

    Args:
        server: Server URL that has to be proxied.
        log_config: Server's logger object.

    See Also:
        - Creates a logging configuration similar to the main logger.
        - Adds the rate limit dependency, per the user's selection.
        - Adds CORS Middleware settings, and loads the uvicorn config.
    """
    logging.config.dictConfig(log_config)
    logger = logging.getLogger("proxy")

    settings.destination.url = server
    settings.session.allowed_origins.update(settings.env_config.origins)
    settings.session.allowed_origins.update(settings.allowance())

    # noinspection HttpUrlsUsage
    logger.info(
        "Starting proxy engine on http://%s:%s with %s workers",
        settings.env_config.host,
        settings.env_config.port,
        settings.env_config.workers,
    )
    logger.warning(
        "\n\n%s\n\nONLY CONNECTIONS FROM THE FOLLOWING ORIGINS WILL BE ALLOWED\n\t- %s\n\n%s\n",
        "".join("*" for _ in range(80)),
        "\n\t- ".join(settings.session.allowed_origins),
        "".join("*" for _ in range(80)),
    )
    dependencies = []
    for each_rate_limit in settings.env_config.rate_limit:
        logger.info("Adding rate limit: %s", each_rate_limit)
        dependencies.append(
            Depends(dependency=rate_limit.RateLimiter(each_rate_limit).init)
        )
    app = FastAPI(
        routes=[
            APIRoute(
                path="/{_:path}",
                endpoint=main.proxy_engine,
                methods=settings.ALLOWED_METHODS,
                dependencies=dependencies,
            )
        ],
    )
    # noinspection PyTypeChecker
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.env_config.origins,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
        max_age=300,  # maximum time in seconds for browsers to cache CORS responses
    )
    proxy_config = uvicorn.Config(
        host=settings.env_config.host,
        port=settings.env_config.port,
        workers=settings.env_config.workers,
        app=app,
    )
    ProxyServer(config=proxy_config).run_in_parallel(logger)
