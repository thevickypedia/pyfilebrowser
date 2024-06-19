import logging
from http import HTTPStatus

import user_agents
from fastapi import Request
from fastapi.responses import HTMLResponse

from pyfilebrowser.proxy import settings, templates

LOGGER = logging.getLogger("proxy")


def log_connection(request: Request) -> HTMLResponse | None:
    """Logs the connection information and returns an HTML response if the browser is unsupported for video/audio.

    See Also:
        - Only logs the first connection from a device.
        - This avoids multiple logs when same device is accessing different paths.

    Returns:
        HTMLResponse:
        Returns an HTML response if the browser is unsupported for video/audio rendering.
    """
    if request.client.host not in settings.session.info:
        settings.session.info[request.client.host] = None
        LOGGER.info(
            "Connection received from client-host: %s, host-header: %s, x-fwd-host: %s",
            request.client.host,
            request.headers.get("host"),
            request.headers.get("x-forwarded-host"),
        )
        if user_agent := request.headers.get("user-agent"):
            LOGGER.info("User agent: %s", user_agent)
            try:
                parsed = user_agents.parse(user_agent)
            except Exception as error:
                LOGGER.critical("Failed to parse user-agent: %s", error)
                return
            if parsed.browser.family == "Chrome":
                return HTMLResponse(
                    content=templates.unsupported_browser(parsed),
                    status_code=HTTPStatus.OK.value,
                )
