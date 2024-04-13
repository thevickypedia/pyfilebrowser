import logging
import secrets
from collections.abc import Generator
from typing import Dict

from fastapi import Request

from pyfilebrowser.proxy import secure, settings

LOGGER = logging.getLogger('proxy')


def log_connection(request: Request) -> None:
    """Logs the connection information.

    See Also:
        - Only logs the first connection from a device.
        - This avoids multiple logs when same device is accessing different paths.
    """
    if request.client.host not in settings.session.info:
        settings.session.info[request.client.host] = None
        LOGGER.info("Connection received from client-host: %s, host-header: %s, x-fwd-host: %s",
                    request.client.host, request.headers.get('host'), request.headers.get('x-forwarded-host'))
        LOGGER.info("User agent: %s", request.headers.get('user-agent'))


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
