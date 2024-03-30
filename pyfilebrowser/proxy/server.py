import contextlib
import logging.config
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute


def update_log_level(data: dict, new_value: Any) -> dict:
    """Recursively update the value where any key equals "level", for loggers and handlers.

    Parameters:
        data: The nested dictionary to traverse.
        new_value: The new value to set where the key equals "level".

    Returns:
        dict:
        The updated nested dictionary.
    """
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = update_log_level(value, new_value)
        elif key == "level":
            data[key] = new_value
    return data


class APIServer(uvicorn.Server):
    """Shared servers state that is available between all protocol instances.

    >>> APIServer

    References:
        https://github.com/encode/uvicorn/issues/742#issuecomment-674411676
    """

    @contextlib.contextmanager
    def run_in_parallel(self, logger: logging.Logger) -> None:
        """Initiates ``Server.run`` in a dedicated process.

        Args:
            logger: Server's original logger.
        """
        uvicorn_error = logging.getLogger("uvicorn.error")
        uvicorn_error.disabled = True
        uvicorn_error.propagate = False
        uvicorn_access = logging.getLogger("uvicorn.access")
        uvicorn_access.disabled = True
        uvicorn_access.propagate = False
        assert logger.name == "proxy"
        self.run()


def proxy_server(server: str, log_config: dict) -> None:
    """Runs the proxy engine in parallel.

    Args:
        server: Server URL that has to be proxied.
        log_config: Server's logger object.
    """
    from pyfilebrowser.proxy import main
    if main.env_config.debug:
        logging.config.dictConfig(update_log_level(log_config, logging.DEBUG))
    else:
        logging.config.dictConfig(log_config)
    logger = logging.getLogger('proxy')

    main.destination.url = server

    proxy_config = uvicorn.Config(
        host=main.env_config.host,
        port=main.env_config.port,
        workers=main.env_config.workers,
        app=FastAPI(
            routes=[
                APIRoute(path="/{_:path}",
                         endpoint=main.proxy_engine,
                         methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
            ]
        ),
    )
    # noinspection HttpUrlsUsage
    logger.info("Starting proxy engine on http://%s:%s with %s workers",
                main.env_config.host, main.env_config.port, proxy_config.workers)
    APIServer(config=proxy_config).run_in_parallel(logger)
