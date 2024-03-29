import logging

import httpx
from fastapi import Request, Response
from fastapi.responses import FileResponse

from pyfilebrowser.proxy.settings import destination, env_config

logger = logging.getLogger('proxy')


async def proxy_engine(request: Request) -> Response:
    """Proxy handler function to forward incoming requests to a target URL.

    Args:
        request: The incoming request object.

    Returns:
        Response: The response object with the forwarded content and headers.
    """
    logger.debug("%s %s", request.method, request.url.path)
    try:
        async with httpx.AsyncClient() as client:
            body = await request.body()
            # noinspection PyTypeChecker
            response = await client.request(
                method=request.method,
                url=destination.url + request.url.path,
                headers=dict(request.headers),
                params=dict(request.query_params),
                data=body.decode(),
            )
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                content = response.text
                # Modify content if necessary (e.g., rewriting links)
                # content = modify_html_links(content)
            else:
                content = response.content
            response.headers.pop("content-encoding", None)
            return Response(content, response.status_code, response.headers, content_type)
    except httpx.RequestError as exc:
        logger.error(exc)
        return FileResponse(
            path=env_config.error_page, headers=None, media_type="text/html"
        )
