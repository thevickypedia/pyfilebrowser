"""Module for packaging."""

import sys

from pyfilebrowser.main import FileBrowser  # noqa: F401

version = "0.1.2"


def _cli() -> None:
    """Starter function to invoke the file browser via CLI commands.

    **Flags**
        - ``--version | -V``: Prints the version.
        - ``--proxy | -P``: Initiates PyFileBrowser with proxy server enabled.
        - ``--help | -H``: Prints the help section.

    **Commands**
        ``start | run``: Initiates the PyFilebrowser.
    """
    assert sys.argv[0].endswith("pyfilebrowser"), "Invalid commandline trigger!!"
    options = {
        "--proxy | -P": "Initiates PyFileBrowser with proxy server enabled.",
        "--version | -V": "Prints the version.",
        "--help | -H": "Prints the help section.",
        "start | run": "Initiates the PyFilebrowser.",
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
        assert len(args) in (1, 2)
    except (IndexError, AttributeError, AssertionError):
        print(
            f"Cannot proceed without a valid arbitrary command. Please choose from {choices}"
        )
        exit(1)
    # Set the proxy flag to False by default
    proxy_flag = False
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
    elif any(arg in args for arg in ["start", "run"]):
        pass
    else:
        print(
            f"Unknown Option: {sys.argv[1]}\nArbitrary commands must be one of {choices}"
        )
        exit(1)
    if any(arg in args for arg in ["start", "run"]):
        FileBrowser(proxy=proxy_flag).start()
    else:
        raise ValueError(
            "\n\tNo 'start' or 'run' command received to initiate the PyFileBrowser"
        )
