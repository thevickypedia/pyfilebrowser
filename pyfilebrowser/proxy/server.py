import contextlib
import logging.config

import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute


class APIServer(uvicorn.Server):
    """Shared servers state that is available between all protocol instances.

    >>> APIServer

    References:
        https://github.com/encode/uvicorn/issues/742#issuecomment-674411676
    """

    def install_signal_handlers(self) -> None:
        """Overrides ``install_signal_handlers`` in ``uvicorn.Server`` module."""
        pass

    @contextlib.contextmanager
    def run_in_parallel(self, logger: logging.Logger) -> None:
        """Initiates ``Server.run`` in a dedicated process.

        Args:
            logger: Server's original logger.
        """
        uvicorn_error = logging.getLogger("uvicorn.error")
        uvicorn_error.disabled = True
        uvicorn_access = logging.getLogger("uvicorn.access")
        uvicorn_access.disabled = True
        assert logger.name == "proxy"
        self.run()


def proxy_server(server: str, log_config: dict) -> None:
    """Runs the proxy engine in parallel.

    Args:
        server: Server URL that has to be proxied.
        log_config: Server's logger object.
    """
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('proxy')

    from pyfilebrowser.proxy import main
    main.destination.url = server

    proxy_config = uvicorn.Config(
        host=main.env_config.host,
        port=main.env_config.port,
        workers=main.env_config.workers,
        app=FastAPI(
            routes=[
                APIRoute(path="/{_:path}",
                         endpoint=main.proxy_engine,
                         methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
            ]
        ),
    )
    # noinspection HttpUrlsUsage
    logger.info("Starting proxy engine on http://%s:%s with %s workers",
                main.env_config.host, main.env_config.port, proxy_config.workers)
    APIServer(config=proxy_config).run_in_parallel(logger)
