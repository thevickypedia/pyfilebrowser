import contextlib
import logging.config
from typing import Dict

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute

from pyfilebrowser.proxy import main, settings


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
        """
        uvicorn_error = logging.getLogger("uvicorn.error")
        uvicorn_error.disabled = True
        uvicorn_error.propagate = False
        uvicorn_access = logging.getLogger("uvicorn.access")
        uvicorn_access.disabled = True
        uvicorn_access.propagate = False
        assert logger.name == "proxy"
        self.run()


def proxy_server(server: str, log_config: dict, auth_map: Dict[str, str]) -> None:
    """Runs the proxy engine in parallel.

    Args:
        server: Server URL that has to be proxied.
        log_config: Server's logger object.
        auth_map: Server's authorization mapping.
    """
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('proxy')

    settings.destination.url = server
    settings.destination.auth_config = auth_map

    proxy_config = uvicorn.Config(
        host=settings.env_config.host,
        port=settings.env_config.port,
        workers=settings.env_config.workers,
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
                settings.env_config.host, settings.env_config.port, proxy_config.workers)
    ProxyServer(config=proxy_config).run_in_parallel(logger)
