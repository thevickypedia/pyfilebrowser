import base64
import hashlib
import json
import logging
import secrets
from typing import Dict

import httpx
from fastapi import Request, Response
from fastapi.responses import FileResponse

from pyfilebrowser.proxy.settings import destination, env_config

logger = logging.getLogger('proxy')


def proxy_auth(authorization: bytes | None) -> Dict[str, str] | None:
    """Authenticate proxy request.

    Args:
        authorization: Authorization header value.

    Returns:
        Dict[str, str]:
        Returns a dict of username, password and recaptcha value.
    """
    if authorization:
        b64_decoded = base64.b64decode(authorization).decode("utf-8")
        username, client_hash, recaptcha = b64_decoded.split(',')
        password = destination.auth_config.get(username)
        server_hash = hashlib.sha512(bytes(username + password, "utf-8")).hexdigest()
        if password and secrets.compare_digest(client_hash, server_hash):
            logger.info("Authentication was successful! Setting auth header to plain text password")
            return dict(username=username, password=password, recaptcha=recaptcha)


async def proxy_engine(proxy_request: Request) -> Response:
    """Proxy handler function to forward incoming requests to a target URL.

    Args:
        proxy_request: The incoming request object.

    Returns:
        Response: The response object with the forwarded content and headers.
    """
    logger.debug("%s %s", proxy_request.method, proxy_request.url.path)
    cookie = ""
    try:
        headers = dict(proxy_request.headers)
        body = await proxy_request.body()
        if proxy_request.url.path == "/login":
            cookie = "set"  # set cookie only for login page
        if (proxy_request.method == "POST" and
                proxy_request.url.path == "/api/login" and
                (auth_response := proxy_auth(headers.get('authorization')))):
            cookie = "delete"  # delete cookie as soon as login has been successful
            headers['authorization'] = json.dumps(auth_response).encode()
        async with httpx.AsyncClient() as client:
            # noinspection PyTypeChecker
            server_response = await client.request(
                method=proxy_request.method,
                url=destination.url + proxy_request.url.path,
                headers=headers,
                params=dict(proxy_request.query_params),
                data=body,
            )
            content_type = server_response.headers.get("content-type", "")
            if "text/html" in content_type:
                content = server_response.text
                # Modify content if necessary (e.g., rewriting links)
                # content = modify_html_links(content)
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
        logger.error(exc)
        return FileResponse(
            path=env_config.error_page, headers=None, media_type="text/html"
        )
