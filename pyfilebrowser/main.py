import json
import logging
import multiprocessing
import os
import signal
import socket
import subprocess
import threading
import time
import warnings
from datetime import datetime
from types import FrameType
from typing import Any, Dict, List, Optional

import pyotp
import yaml

from pyfilebrowser.modals import models, settings
from pyfilebrowser.proxy import proxy_server, proxy_settings
from pyfilebrowser.squire import download, steward, struct


class FileBrowser:
    """Object to handle the filebrowser streaming.

    >>> FileBrowser

    """

    def __init__(self, **kwargs):
        """Instantiates the object.

        Keyword Args:
            logger: Bring your own logger.
            proxy: Boolean flag to enable proxy.
            extra_env: JSON or YAML filename to load extra settings.

        See Also:
            - ``extra_env`` is a feature to load additional configuration settings to the filebrowser server.
            - This is useful when you want to load custom settings that are not available in the default configuration.
            - The file should be a JSON or YAML file with the following structure:
                - The key should be the same as the one in configuration settings of the filebrowser.
                  Options: (``server``, ``auther``, ``settings``)
                - The JSON/YAML structure should follow the same parent key-value mapping.
                - The file should be placed in the same directory as the script that invokes the filebrowser.
                - The filename should be passed as a keyword argument to the ``FileBrowser`` object.
                  (By default, searched for ``extra.json`` in the current directory)
        """
        self.env = steward.EnvConfig(**kwargs)
        self.github = download.GitHub(**kwargs)
        self.settings = settings.ServerSettings(**kwargs)

        self.logger: logging.Logger = kwargs.get(
            "logger",
            steward.default_logger(
                self.env.config_settings.server.log == models.Log.file
            ),
        )
        # Reset to stdout, so the log output stream can be controlled with custom logging
        self.env.config_settings.server.log = models.Log.stdout
        self.proxy_engine: multiprocessing.Process | None = None
        self.proxy = kwargs.get("proxy") or steward.get_env(
            "pyfb_proxy", convert_to=bool
        )
        self.extra_env = kwargs.get("extra_env") or steward.get_env("pyfb_extra_env")
        assert self.proxy is None or isinstance(
            self.proxy, bool
        ), f"\n\tproxy flag should be a boolean value, received {type(self.proxy).__name__!r}"
        self.shutdown_flag = threading.Event()
        self.is_docker = os.path.isfile(os.path.join("/", ".dockerenv"))

    def register_signal_handlers(self) -> None:
        """Register signals (cross-platform) to handle graceful shutdown on various levels."""
        # Ctrl+C / KeyboardInterrupt
        signal.signal(signal.SIGINT, self.handle_shutdown)
        # Service stop / kill
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def cleanup(self, log: bool = True) -> None:
        """Removes the config and proxy database."""
        self.unlink()
        steward.delete(
            (
                steward.fileio.users,
                steward.fileio.config,
                proxy_settings.database,
                download.executable.filebrowser_db,
            ),
            logger=self.logger if log else None,
        )

    def exit_process(self) -> None:
        """Deletes the database file, and all the subtitles that were created by this application."""
        if self.proxy_engine:
            self.proxy_engine.join(timeout=3)  # Gracefully terminate the proxy server
            for i in range(1, 6):
                if self.proxy_engine.is_alive():
                    self.proxy_engine.terminate()
                else:
                    self.logger.debug(
                        "Daemon process terminated in %s attempt", steward.ordinal(i)
                    )
                    self.proxy_engine.close()
                    break
                time.sleep(1e-1)  # 0.1s
            else:
                warnings.warn(
                    f"Failed to terminate daemon process PID: [{self.proxy_engine.pid}] within 5 attempts",
                    RuntimeWarning,
                )
        self.cleanup()

    def run_subprocess(
        self, arguments: List[str] = None, failed_msg: str = None, stdout: bool = True
    ) -> None:
        """Run ``filebrowser`` commands as subprocess.

        Args:
            arguments: Arguments to pass to the binary.
            failed_msg: Failure message in case of bad return code.
            stdout: Boolean flag to show/hide standard output.
        """
        command = os.path.join(os.getcwd(), download.executable.filebrowser_bin)
        if arguments:
            arguments.insert(0, "")
            command += " ".join(arguments)
        process = subprocess.Popen(
            command,
            shell=True,
            universal_newlines=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            if stdout:
                for line in process.stdout:
                    self.logger.info(steward.remove_prefix(line))
            process.wait()
            for line in process.stderr:
                self.logger.warning(steward.remove_prefix(line))
            assert process.returncode == 0, (
                failed_msg or f"filebrowser returned an exit code {process.returncode}"
            )
        except KeyboardInterrupt:
            if process.poll() is None:
                for line in process.stdout:
                    self.logger.info(steward.remove_prefix(line))
                process.terminate()
            raise

    def create_users(self) -> None:
        """Creates the JSON file(s) for user profiles."""
        final_settings = []
        for idx, profile in enumerate(self.env.user_profiles):
            if profile.perm:
                self.logger.info("Setting custom permissions for: %s", profile.username)
                self.logger.debug(profile.perm.model_dump_json())
            elif profile.admin:
                profile.perm = models.admin_perm()
            else:
                profile.perm = models.default_perm()
            hashed_password = steward.hash_password(profile.password)
            assert steward.validate_password(
                profile.password, hashed_password
            ), "Validation failed!"
            profile.password = hashed_password
            profile.id = idx + 1
            user_settings = json.loads(profile.model_dump_json())
            final_settings.append(user_settings)
        with open(steward.fileio.users, "w") as file:
            json.dump(final_settings, file, indent=4)
            file.flush()

    def load_extra_env(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Load extra env settings from a yaml or json file.

        Args:
            settings: Base settings.

        Returns:
            Dict[str, Any]:
            Returns the final settings after patching the extra config values.
        """
        if self.extra_env and os.path.isfile(self.extra_env):
            self.logger.debug("Extra configuration file found: %s", self.extra_env)
            if self.extra_env.endswith(".json"):
                with open(self.extra_env) as file:
                    extra_env = json.load(file)
            elif self.extra_env.endswith(".yaml") or self.extra_env.endswith(".yml"):
                with open(self.extra_env) as file:
                    extra_env = yaml.load(file, Loader=yaml.FullLoader)
            else:
                raise ValueError("Extra settings should be either a JSON or YAML file.")
        elif self.extra_env:
            raise FileNotFoundError(
                "Received '%s' for 'extra_env', but file not found.", self.extra_env
            )
        else:
            self.logger.debug("No extra configuration to be added")
            return settings
        if not isinstance(extra_env, dict):
            raise ValueError(
                "Invalid configuration received for extra_env. Expected dict, received %s",
                type(extra_env),
            )
        valid_keys = list(settings.keys())
        for key, value in extra_env.items():
            if key in valid_keys:
                self.logger.info(
                    "Loading extra settings for '%s' from '%s'", key, self.extra_env
                )
                self.logger.debug("Extra settings - %s: %s", key, value)
                settings[key].update(value)
            else:
                raise ValueError(
                    f"Updates are allowed only for existing keys: {valid_keys!r}. Received: {key!r}"
                )
        return settings

    def create_config(self) -> None:
        """Creates the JSON file for configuration."""
        if self.proxy:
            self.env.config_settings.settings.authMethod = "json"
            self.env.config_settings.settings.authHeader = ""
        if str(self.env.config_settings.settings.branding.files) == ".":
            self.env.config_settings.settings.branding.files = ""
        self.env.config_settings.server.port = str(self.env.config_settings.server.port)
        with warnings.catch_warnings(action="ignore"):
            base_settings = steward.remove_trailing_underscore(
                json.loads(self.env.config_settings.model_dump_json())
            )
        self.logger.info("Loaded the base settings for: %s", base_settings.keys())
        final_settings = self.load_extra_env(base_settings)
        if self.env.config_settings.auther.authenticatorToken:
            totp = pyotp.TOTP(self.env.config_settings.auther.authenticatorToken)
            # Sampler can also be generated with totp.now()
            now = datetime.now()
            sampler = totp.generate_otp(totp.timecode(now))
            assert totp.verify(sampler, for_time=now), "Invalid authenticatorToken!"
        else:
            final_settings["auther"].pop("authenticatorToken")
        # Remove symlinks from the final settings
        final_settings["server"].pop("symlinks")
        with open(steward.fileio.config, "w") as file:
            json.dump(final_settings, file, indent=4)
            file.flush()

    def import_config(self) -> None:
        """Imports the configuration file into filebrowser."""
        self.logger.info("Importing configuration from %s", steward.fileio.config)
        self.create_config()
        assert os.path.isfile(
            steward.fileio.config
        ), f"{steward.fileio.config!r} doesn't exist"
        self.run_subprocess(
            ["config", "import", steward.fileio.config],
            "Failed to import configuration",
            False,
        )

    def import_users(self) -> None:
        """Imports the user profile(s) into filebrowser."""
        self.logger.info("Importing user profiles from %s", steward.fileio.users)
        self.create_users()
        assert os.path.isfile(
            steward.fileio.users
        ), f"{steward.fileio.users!r} doesn't exist"
        self.run_subprocess(
            ["users", "import", steward.fileio.users],
            "Failed to import user profiles",
            False,
        )

    def background_tasks(self) -> None:
        """Initiates the proxy engine and subtitles' format conversion as background tasks."""
        assert proxy_settings.port != int(
            self.env.config_settings.server.port
        ), f"\n\tProxy server can't run on the same port [{proxy_settings.port}] as the server!!"
        # This is to check if the port is available, before starting the proxy server in a dedicated process
        # If not for this, the proxy server will fail to initiate in the child process and become unmanageable
        try:
            with socket.socket() as sock:
                sock.bind((proxy_settings.host, proxy_settings.port))
        except OSError as error:
            self.logger.error(error)
            self.logger.critical(
                "Cannot initiate proxy server, retry after sometime or change the port number."
            )
            self.cleanup()
            raise
        log_config = struct.LoggerConfig(self.logger).get()
        if proxy_settings.debug:
            log_config = struct.update_log_level(log_config, logging.DEBUG)
        # noinspection HttpUrlsUsage
        self.proxy_engine = multiprocessing.Process(
            target=proxy_server,
            daemon=True,
            args=(
                f"http://{self.env.config_settings.server.address}:{self.env.config_settings.server.port}",
                log_config,
            ),
        )
        self.proxy_engine.start()

    def link(self) -> None:
        """Creates symlinks for the directories specified in the configuration."""
        if self.is_docker and self.env.config_settings.server.symlinks:
            msg = "Symlinks are not supported, when running in Docker context. Please mount volumes instead."
            self.logger.warning(msg)
            warnings.warn(msg)
            return
        for source_path in self.env.config_settings.server.symlinks:
            target_path = os.path.join(
                self.env.config_settings.server.root, source_path.name
            )
            if os.path.lexists(target_path):
                self.logger.warning("Symbolic link already exists: %s", target_path)
            else:
                os.symlink(source_path, target_path)
                self.logger.info("Symbolic created: %s -> %s", source_path, target_path)

    def unlink(self) -> None:
        """Removes the symbolic links created in the server root directory."""
        if self.is_docker:
            return
        for source_path in self.env.config_settings.server.symlinks:
            target_path = os.path.join(
                self.env.config_settings.server.root, source_path.name
            )
            if os.path.lexists(target_path):
                self.logger.info("Removing symbolic link: %s", target_path)
                os.unlink(target_path)
            else:
                self.logger.warning("No symbolic link found to remove: %s", target_path)

    def handle_shutdown(self, signum: int, frame: Optional[FrameType]) -> None:
        """Handles shutdown signals (e.g., SIGINT, SIGTERM) to initiate a graceful shutdown.

        This function is intended to be registered with the `signal` module and will be
        triggered when the process receives a termination signal. It logs relevant
        information and sets a shutdown flag to allow the main process to exit cleanly.

        Args:
            signum: The signal number received (e.g., signal.SIGINT).
            frame: The current stack frame when the signal was received.
        """
        for atr in dir(frame):
            if atr.startswith("f_"):
                self.logger.debug(f"frame.{atr}: {getattr(frame, atr)}")
        self.logger.info("Received signal %d, setting shutdown flag", signum)
        self.shutdown_flag.set()

    def start_service(self) -> None:
        """Starts the filebrowser server as a service with graceful shutdown handling."""
        self.register_signal_handlers()
        if not os.path.isfile(download.executable.filebrowser_bin):
            download.binary(logger=self.logger, github=self.github)
        try:
            while not self.shutdown_flag.is_set():
                self.start_server()
            self.logger.info("Cleanup complete. Exiting.")
        except Exception as error:
            self.logger.error("Unexpected [%s]: %s", type(error).__name__, error)
            self.exit_process()

    def start_server(self) -> None:
        """Starts the filebrowser server as a regular script with automatic restarts."""
        self.cleanup(False)
        if not os.path.isfile(download.executable.filebrowser_bin):
            download.binary(logger=self.logger, github=self.github)
        self.import_config()
        self.import_users()
        self.link()
        steward.delete((steward.fileio.users, steward.fileio.config))
        if self.proxy:
            self.background_tasks()
        for idx in range(self.settings.restart + 1):
            idx += 1
            self.logger.info("Initiating filebrowser API")
            try:
                self.run_subprocess()
            except AssertionError as error:
                if self.settings.restart > idx:
                    self.logger.error(error)
                    self.logger.info("Attempt #%d failed, restarting server", idx)
                    # Give some breathing room for port to be free
                    time.sleep(3)
                elif self.settings.restart:
                    self.logger.error("All %d restart attempts failed. Exiting.", idx)
                else:
                    break
            except KeyboardInterrupt:
                self.logger.info("Stopped by user, shutting down.")
                break
        self.exit_process()
