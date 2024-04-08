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
