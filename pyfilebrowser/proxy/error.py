from http import HTTPStatus

import jinja2

from pyfilebrowser.proxy import settings


def service_unavailable() -> str:
    """Constructs an error page using jina template for service unavailable.

    Returns:
        str:
        HTML content as string.
    """
    with open(settings.env_config.error_page) as file:
        error_template = file.read()
    return jinja2.Template(error_template).render(
        title=HTTPStatus.SERVICE_UNAVAILABLE.phrase,
        summary=r"Unable to connect to the server ¯\_(ツ)_/¯",
        help="Nothing to do here!!\n\nSit back and relax while the server is napping.",
        refresh_interval=60
    )


def forbidden(origin: str) -> str:
    """Constructs an error page using jina template for forbidden response.

    Args:
        origin: Origin that is forbidden.

    Returns:
        str:
        HTML content as string.
    """
    with open(settings.env_config.error_page) as file:
        error_template = file.read()
    return jinja2.Template(error_template).render(
        title=HTTPStatus.FORBIDDEN.phrase,
        summary=HTTPStatus.FORBIDDEN.description,
        help=f"Requests from {origin!r} is not allowed",
        refresh_interval=86_400
    )
