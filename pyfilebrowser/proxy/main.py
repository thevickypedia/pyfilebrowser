import json
import logging

import httpx
from fastapi import HTTPException, Request, Response, status
from fastapi.responses import FileResponse

from pyfilebrowser.proxy import settings, squire

LOGGER = logging.getLogger('proxy')
CLIENT = httpx.Client()


async def proxy_engine(proxy_request: Request) -> Response:
    """Proxy handler function to forward incoming requests to a target URL.

    Args:
        proxy_request: The incoming request object.

    Returns:
        Response: The response object with the forwarded content and headers.
    """
    squire.log_connection(proxy_request)
    # todo: make sure base_url is always caught and also verify x-forwarded-host and host headers
    if proxy_request.base_url not in settings.env_config.origins:
        LOGGER.warning("%s is not allowed since it is not set in CORS %s",
                       proxy_request.base_url, settings.env_config.origins)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN.real,
                            detail=f"{proxy_request.base_url!r} is not allowed")
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
        content_type = server_response.headers.get("content-type", "")
        if "text/html" in content_type:
            content = server_response.text
        else:
            content = server_response.content
        server_response.headers.pop("content-encoding", None)
        proxy_response = Response(content, server_response.status_code, server_response.headers, content_type)
        if cookie == "set":
            proxy_response.set_cookie(key="pyproxy", value="on")
        if cookie == "delete":
            proxy_response.delete_cookie(key="pyproxy")
        return proxy_response
    except httpx.RequestError as exc:
        LOGGER.error(exc)
        return FileResponse(path=settings.env_config.error_page, headers=None, media_type="text/html")
