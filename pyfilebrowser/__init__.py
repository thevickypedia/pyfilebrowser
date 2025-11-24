"""Module for packaging."""

import sys

from pyfilebrowser.main import FileBrowser  # noqa: F401
from pyfilebrowser.squire import otp  # noqa: F401

version = "0.2.3"


def _cli() -> None:
    """Starter function to invoke the file browser via CLI commands.

    **Flags**
        - ``--version | -V``: Prints the version.
        - ``--proxy | -P``: Initiates PyFileBrowser with proxy server enabled.
        - ``--help | -H``: Prints the help section.
        - ``--otp | -O``: Generates a one-time password (OTP) QR code for secure access.
        - ``--extra | -E <path>``: Specifies an extra environment YAML file to load additional configurations.

    **Commands**
        ``start``: Initiates the PyFilebrowser as a regular script.
        ``start-service``: Initiates the PyFilebrowser as a service.
        ``start-container``: Initiates the PyFilebrowser as a containerized application.
    """
    assert sys.argv[0].endswith("pyfilebrowser"), "Invalid commandline trigger!!"
    options = {
        "--proxy | -P": "Initiates PyFileBrowser with proxy server enabled.",
        "--version | -V": "Prints the version.",
        "--help | -H": "Prints the help section.",
        "--otp | -O": "Generates a one-time password (OTP) QR code for secure access.",
        "--extra | -E <path>": "Specifies an extra environment YAML file to load additional configurations.",
        "start": "Initiates the PyFilebrowser as a regular script.",
        "start-service": "Initiates the PyFilebrowser as a service.",
        "start-container": "Initiates the PyFilebrowser as a containerized application.",
    }
    # weird way to increase spacing to keep all values monotonic
    _longest_key = len(max(options.keys()))
    _pretext = "\n\t* "
    choices = _pretext + _pretext.join(
        f"{k} {'·' * (_longest_key - len(k) + 8)}→ {v}".expandtabs()
        for k, v in options.items()
    )
    args = [arg.lower() for arg in sys.argv[1:]]
    try:
        assert len(args) > 1
    except (IndexError, AttributeError, AssertionError):
        print(
            f"Cannot proceed without a valid arbitrary command. Please choose from {choices}"
        )
        exit(1)
    # Set the proxy flag to False by default
    proxy_flag = False
    extra_env = None
    if any(arg in args for arg in ["version", "--version", "-v"]):
        print(f"PyFileBrowser: {version}")
        exit(0)
    elif any(arg in args for arg in ["proxy", "--proxy", "-p"]):
        proxy_flag = True
    elif any(arg in args for arg in ["help", "--help", "-h"]):
        print(
            f"Usage: pyfilebrowser [arbitrary-command]\nOptions (and corresponding behavior):{choices}"
        )
        exit(0)
    elif any(arg in args for arg in ["generate-otp", "otp", "--otp", "-o"]):
        otp.generate_qr(show_qr=True)
        exit(0)
    elif any(arg in args for arg in ["extra", "--extra", "E", "-e"]):
        extra_index = next(
            (
                index
                for index, arg in enumerate(args)
                if arg in ["extra", "--extra", "E", "-e"]
            ),
            None,
        )
        try:
            extra_env = sys.argv[extra_index + 2]
        except IndexError:
            print("Cannot proceed without a valid extra environment file path.")
            exit(1)
    elif any(
        arg in args
        for arg in (
            "start",
            "start-server",
            "start_server",
            "start-service",
            "start_service",
            "start-container",
            "start_container",
        )
    ):
        pass
    else:
        print(
            f"Unknown Option: {sys.argv[1]}\nArbitrary commands must be one of {choices}"
        )
        exit(1)
    if any(arg in args for arg in ("start", "start-server", "start_server")):
        FileBrowser(proxy=proxy_flag, extra_env=extra_env).start_server()
    elif any(arg in args for arg in ("start-service", "start_service")):
        FileBrowser(proxy=proxy_flag, extra_env=extra_env).start_service()
    elif any(arg in args for arg in ("start-container", "start_container")):
        FileBrowser(proxy=proxy_flag, extra_env=extra_env).start_container()
    else:
        print(
            "Insufficient Arguments:\n\tNo command received to initiate the PyFileBrowser. "
            f"Please choose from {choices}"
        )
        exit(1)
