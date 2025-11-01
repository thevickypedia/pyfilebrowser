"""This module provides functionality for generating a QR code for TOTP (Time-based One-Time Password) setup.

.. note::

    To generate a QR code, run one of the following:

    **Option 1: Python snippet**

    .. code-block:: python

        import pyfilebrowser
        pyfilebrowser.otp.generate_qr(show_qr=True)

    **Option 2: CLI command**

    .. code-block:: bash

        pyfilebrowser --otp
"""

import os
import warnings
from dataclasses import dataclass

import pyotp
import qrcode


def getenv(key: str, default: str | None = None) -> str | None:
    """Gets an environment variable or returns a default value.

    Args:
        key: The environment variable key.
        default: The default value to return if the key is not found.
    Returns:
        The value of the environment variable or the default value.
    """
    return os.environ.get(key.upper()) or os.environ.get(key.lower()) or default


@dataclass
class OTPConfig:
    """Data class to hold OTP configuration.

    >>> OTPConfig

    """

    secret: str
    qr_filename: str
    authenticator_user: str
    authenticator_app: str


config = OTPConfig(
    secret="",
    qr_filename=getenv("authenticator_qr_filename", "totp_qr.png"),
    authenticator_user=getenv("authenticator_user", "thevickypedia"),
    authenticator_app=getenv("authenticator_app", "FileBrowser"),
)


def display_secret() -> None:
    """Displays the TOTP secret key."""
    try:
        term_size = os.get_terminal_size().columns
    except OSError:
        term_size = 120
    base = "*" * term_size
    print(
        f"\n{base}\n"
        f"\nYour TOTP secret key is: {config.secret}"
        f"\nStore this key as the environment variable `authenticator_token`\n"
        f"\nQR code saved as {config.qr_filename!r} (you can scan this with your Authenticator app).\n"
        f"\n{base}",
    )


def generate_qr(show_qr: bool = False) -> None:
    """Generates a QR code for TOTP setup.

    Args:
        - show_qr: If True, displays the QR code using the default image viewer.
    """
    if getenv("authenticator_token"):
        warnings.warn(
            "\n\nAuthenticator token already set — skipping OTP setup. "
            "To create a new one, remove the 'authenticator_token' environment variable.\n",
            UserWarning,
        )
        return

    # STEP 1: Generate a new secret key for the user (store this securely!)
    secret = pyotp.random_base32()

    # STEP 2: Create a provisioning URI (for the QR code)
    uri = pyotp.TOTP(secret).provisioning_uri(
        name=str(config.authenticator_user), issuer_name=config.authenticator_app
    )

    # STEP 3: Generate a QR code (scan this with your authenticator app)
    qr = qrcode.make(uri)
    if show_qr:
        qr.show()

    # Save the QR code
    qr.save(config.qr_filename)

    # STEP 4: Update the config with the new secret
    config.secret = secret
    display_secret()
