import json
import logging
import secrets
from collections.abc import Generator
from typing import Dict

import httpx
from fastapi import Request, Response
from fastapi.responses import FileResponse

from pyfilebrowser.proxy import secure, settings

LOGGER = logging.getLogger('proxy')
CLIENT = httpx.Client()


def extract_credentials(authorization: bytes) -> Generator[str]:
    r"""Extract the credentials from ``Authorization`` headers and decode it before returning as a list of strings.

    Args:
        authorization: Authorization header value.

    See Also:
        - Decodes the base64-encoded value (JavaScript's built-in encoding ``btoa``)
        - Converts hex encoded value to string

        .. code-block:: javascript

            // Converts a string into a hex
            async function ConvertStringToHex(str) {
                let arr = [];
                for (let i = 0; i < str.length; i++) {
                    arr[i] = ("00" + str.charCodeAt(i).toString(16)).slice(-4);
                }
                return "\\u" + arr.join("\\u");
            }

            // Expected encryption and encoding for authorization header
            let hex_user = await ConvertStringToHex(username);
            let signature = await CalculateHash(password);
            let hex_recaptcha = await ConvertStringToHex(recaptcha);
            let authHeader = btoa(hex_user + "," + signature + "," + hex_recaptcha) // eslint-disable-line

    Yields:
        Generator[str]:
        Yields parts of the extracted credentials.
    """
    # Decode the Base64-encoded ASCII string (JavaScript's built-in encoding btoa)
    decoded_auth = secure.base64_decode(authorization)
    # Convert hex to a string
    for part in decoded_auth.split(','):
        yield secure.hex_decode(part)


def proxy_auth(authorization: bytes | None) -> Dict[str, str] | None:
    """Authenticate proxy request.

    Args:
        authorization: Authorization header value.

    See Also:
        - Creates a hash of the password with cryptographic encryption and compares with the received hash

        .. code-block:: javascript

            // Converts a string into a hash using cryptographic encryption
            async function CalculateHash(message) {
                const encoder = new TextEncoder();
                const data = encoder.encode(message);
                if (crypto.subtle === undefined) {
                    const wordArray = CryptoJS.lib.WordArray.create(data);
                    const hash = CryptoJS.SHA512(wordArray);
                    return hash.toString(CryptoJS.enc.Hex);
                } else {
                    const hashBuffer = await crypto.subtle.digest("SHA-512", data);
                    const hashArray = Array.from(new Uint8Array(hashBuffer));
                    return hashArray.map((byte) => byte.toString(16).padStart(2, "0")).join("");
                }
            }

    Returns:
        Dict[str, str]:
        Returns a dict of username, password and recaptcha value.
    """
    if authorization:
        try:
            username, signature, recaptcha = list(extract_credentials(authorization))
        except ValueError:
            LOGGER.error("Authentication header is malformed")
            return
        password = settings.destination.auth_config.get(username, "")
        expected_signature = secure.calculate_hash(password)
        if password and secrets.compare_digest(expected_signature, signature):
            LOGGER.info("Authentication was successful! Setting auth header to plain text password")
            return dict(username=username, password=password, recaptcha=recaptcha)


async def proxy_engine(proxy_request: Request) -> Response:
    """Proxy handler function to forward incoming requests to a target URL.

    Args:
        proxy_request: The incoming request object.

    Returns:
        Response: The response object with the forwarded content and headers.
    """
    LOGGER.debug("%s %s", proxy_request.method, proxy_request.url.path)
    cookie = ""
    try:
        headers = dict(proxy_request.headers)
        body = await proxy_request.body()
        if proxy_request.url.path in ("/", "/login"):
            cookie = "set"  # set cookie only for login page
        if (proxy_request.url.path == "/api/login" and
                (auth_response := proxy_auth(headers.get('authorization')))):
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
