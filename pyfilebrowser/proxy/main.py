import difflib
import json
import logging
import time
from datetime import datetime, timedelta
from http import HTTPStatus

import httpx
from fastapi import HTTPException, Request, Response
from fastapi.responses import HTMLResponse

from pyfilebrowser.proxy import database, error, settings, squire

LOGGER = logging.getLogger('proxy')
CLIENT = httpx.Client()
DIFFER = difflib.Differ()

epoch = lambda: int(time.time())  # noqa: E731


def refresh_allowed_origins() -> None:
    """Refresh all the allowed origins.

    See Also:
        - Triggered once during the proxy server starts up (by default).
        - Triggered repeatedly at given intervals as a background task (if ``origin_refresh`` is set).
        - | The background task runs only when the env vars, ``private_ip`` or ``public_ip`` is set to True,
          | as they are the only dynamic values.
    """
    allowed_origins = set()
    allowed_origins.update(settings.env_config.origins)
    allowed_origins.update(settings.allowance())

    # Extract elements that are only in one of the sets
    if difference := [item for item in list(DIFFER.compare(sorted(settings.session.allowed_origins),
                                                           sorted(allowed_origins)))
                      if item.startswith('- ') or item.startswith('+ ')]:
        LOGGER.warning("Changes in allowed origins: %s", difference)

    settings.session.allowed_origins.clear()
    settings.session.allowed_origins = allowed_origins
    LOGGER.debug("Refreshed allowed origins. Next refresh - %s",
                 (datetime.now() + timedelta(seconds=settings.env_config.origin_refresh)).strftime('%c'))


async def incrementer(attempt: int) -> int:
    """Increments block time for a host address based on the number of failed attempts.

    Args:
        attempt: Number of failed attempts.

    Returns:
        int:
        Returns the appropriate block time in minutes.
    """
    try:
        return {4: 5, 5: 10, 6: 20, 7: 40, 8: 80, 9: 160, 10: 220}[attempt]
    except KeyError:
        LOGGER.critical("Something went horribly wrong for %dth attempt", attempt)
        return 60  # defaults to 1 hour


async def handle_auth_error(request: Request) -> None:
    """Handle authentication errors from the filebrowser API.

    Args:
        request: The incoming request object.
    """
    if settings.session.auth_counter.get(request.client.host):
        settings.session.auth_counter[request.client.host] += 1
        LOGGER.warning("Failed auth, attempt #%d for %s",
                       settings.session.auth_counter[request.client.host], request.client.host)
        if settings.session.auth_counter[request.client.host] >= 10:
            until = epoch() + 2_592_000  # Block the host address for 1 month or until the server restarts
            LOGGER.warning("%s is blocked until %s",
                           request.client.host, datetime.fromtimestamp(until).strftime('%c'))
            database.remove_record(request.client.host)
            database.put_record(request.client.host, until)
        elif settings.session.auth_counter[request.client.host] > 3:  # Allows up to 3 failed login attempts
            settings.session.forbid.add(request.client.host)
            minutes = await incrementer(settings.session.auth_counter[request.client.host])
            until = epoch() + minutes * 60
            LOGGER.warning("%s is blocked (for %d minutes) until %s",
                           request.client.host, minutes, datetime.fromtimestamp(until).strftime('%c'))
            database.remove_record(request.client.host)
            database.put_record(request.client.host, until)
    else:
        LOGGER.warning("Failed auth, attempt #1 for %s", request.client.host)
        settings.session.auth_counter[request.client.host] = 1


async def proxy_engine(proxy_request: Request) -> Response:
    """Proxy handler function to forward incoming requests to a target URL.

    Args:
        proxy_request: The incoming request object.

    Returns:
        Response: The response object with the forwarded content and headers.
    """
    squire.log_connection(proxy_request)
    # Since host header can be overridden, always check with base_url
    if proxy_request.base_url.hostname not in settings.session.allowed_origins:
        LOGGER.warning("%s is blocked by firewall, since it is not set in allowed origins %s",
                       proxy_request.base_url, settings.session.allowed_origins)
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN.value,
                            detail=f"{proxy_request.base_url!r} is not allowed")
    if proxy_request.client.host in settings.session.forbid:  # placeholder list, to avoid DB search for every request
        # Get timestamp until which the host has to be forbidden
        if (timestamp := database.get_record(proxy_request.client.host)) and timestamp > epoch():
            LOGGER.warning("%s is forbidden until %s due to repeated login failures",
                           proxy_request.client.host, datetime.fromtimestamp(timestamp).strftime('%c'))
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN.value,
                                detail=f"{proxy_request.client.host!r} is not allowed")
    # following condition prevents long videos from spamming the logs
    if settings.session.info.get(proxy_request.client.host) != proxy_request.url.path:
        settings.session.info[proxy_request.client.host] = proxy_request.url.path
        LOGGER.info("%s %s", proxy_request.method, proxy_request.url.path)
    cookie = ""
    try:
        headers = dict(proxy_request.headers)
        body = await proxy_request.body()
        if proxy_request.url.path in ("/", "/login"):
            cookie = "set"  # set cookie only for login page
        if (proxy_request.url.path == "/api/login" and
                (auth_response := squire.proxy_auth(headers.get('authorization')))):
            cookie = "delete"  # delete cookie as soon as login has been successful
            headers['authorization'] = json.dumps(auth_response).encode()
        # noinspection PyTypeChecker
        server_response = CLIENT.request(
            method=proxy_request.method,
            url=settings.destination.url + proxy_request.url.path,
            headers=headers,
            cookies=proxy_request.cookies,
            params=dict(proxy_request.query_params),
            data=body,
        )
        if proxy_request.url.path == "/api/login":
            if server_response.status_code == 403:
                await handle_auth_error(proxy_request)
            elif (proxy_request.client in settings.session.forbid or
                  settings.session.auth_counter.get(proxy_request.client.host)):
                LOGGER.debug("Removing %s from forbidden list", proxy_request.client.host)
                settings.session.forbid.discard(proxy_request.client.host)

                LOGGER.debug("Resetting auth counter [%d] for %s to null",
                             settings.session.auth_counter.pop(proxy_request.client.host, 0),
                             proxy_request.client.host)

                LOGGER.debug("Removing %s from auth DB", proxy_request.client.host)
                database.remove_record(host=proxy_request.client.host)
        content_type = server_response.headers.get("content-type", "")
        if "text" in content_type:
            content = server_response.text
        else:
            content = server_response.content
        server_response.headers.pop("content-encoding", None)
        # fixme: there should be a better way to handle this
        if "javascript" in content_type:  # todo: not sure if this is solely because of VideoJS plugin
            server_response.headers.pop("content-length", None)
        proxy_response = Response(
            content=content,
            status_code=server_response.status_code,
            headers=server_response.headers,
            media_type=content_type
        )
        if cookie == "set":
            proxy_response.set_cookie(key="pyproxy", value="on")
        if cookie == "delete":
            proxy_response.delete_cookie(key="pyproxy")
        return proxy_response
    except httpx.RequestError as exc:
        LOGGER.error(exc)
        max_age = timedelta(minutes=5)
        expiration = datetime.utcnow() + max_age
        formatted_date = expiration.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return HTMLResponse(
            headers={"Cache-Control": f"max-age={max_age.seconds}", "Expires": formatted_date},
            content=error.service_unavailable(),
            status_code=HTTPStatus.SERVICE_UNAVAILABLE.value
        )
