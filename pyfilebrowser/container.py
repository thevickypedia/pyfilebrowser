import logging
import os
import threading

import docker

from pyfilebrowser.modals.settings import ContainerSettings
from pyfilebrowser.squire import steward


class ContainerEngine:
    """Container engine to manage Docker containers for PyFilebrowser.

    >>> ContainerEngine

    """

    def __init__(self, container_settings: ContainerSettings, logger: logging.Logger):
        self.logger = logger
        self.client = docker.from_env()
        self.settings = container_settings

    def pull_image(self) -> None:
        """Pull the Docker image from the registry."""
        pull_log = self.client.api.pull(
            repository=self.settings.image,
            tag=self.settings.tag,
            platform=self.settings.platform,
            auth_config=self.settings.credentials.model_dump(),
            stream=True,
            decode=True,
        )
        for log in pull_log:
            self.logger.info(log["status"])
        image = self.client.images.get(f"{self.settings.image}:{self.settings.tag}")
        assert (
            image is not None
        ), f"\n\tFailed to pull image [{self.settings.image}:{self.settings.tag}] from registry."
        self.logger.info(
            "Image pulled successfully: [%s] %s", image.short_id, image.tags
        )

    def remove_existing(self) -> None:
        """Remove docker container if it exists already."""
        try:
            container = self.client.containers.get(self.settings.name)
            container.stop()
            container.remove()
            self.logger.info(f"Removed existing container: {self.settings.name}")
        except docker.errors.NotFound:
            self.logger.info(
                "No existing container named %s found.", self.settings.name
            )

    def run_container(
        self,
        port: int,
        data_volume: str,
    ) -> None:
        """Run the Docker container for PyFilebrowser.

        Args:
            port: Host port to map to the container's port.
            data_volume: Root directory path to mount as data volume.
        """
        self.remove_existing()
        config_volume = steward.fileio.settings_dir
        assert os.path.exists(
            data_volume
        ), f"Data volume path does not exist: {data_volume}"
        assert os.path.exists(
            config_volume
        ), f"Config volume path does not exist: {config_volume}"
        assert os.path.isfile(
            steward.fileio.config
        ), f"Config file does not exist: {steward.fileio.config}"
        assert os.path.isfile(
            steward.fileio.users
        ), f"Users file does not exist: {steward.fileio.users}"
        container = self.client.containers.run(
            self.settings.image,
            name=self.settings.name,
            ports={f"{port}/tcp": port},
            volumes={
                data_volume: {
                    "bind": self.settings.data_volume,
                    "mode": self.settings.data_mode,
                },
                config_volume: {
                    "bind": self.settings.config_volume,
                    "mode": self.settings.config_mode,
                },
            },
            restart_policy={"Name": self.settings.restart},
            detach=True,
            environment={
                "CONFIG_FILE": os.path.basename(steward.fileio.config),
                "USERS_FILE": os.path.basename(steward.fileio.users),
            },
        )

        timer = threading.Timer(
            interval=10,
            function=steward.delete,
            kwargs=dict(files=(steward.fileio.config, steward.fileio.users)),
        )
        if self.settings.detach:
            self.logger.info(f"Container started in detached mode: {container.name}")
            timer.daemon = True
            timer.start()
            return

        timer.start()
        try:
            for log in container.logs(stream=True):
                self.logger.info(log.strip().decode("utf-8"))
        except KeyboardInterrupt:
            container.stop()
            self.logger.info("Container %s has stopped.", container.name)
            container.remove()
            self.logger.info("Container %s has been removed.", container.name)
            # Cancel future and run immediately
            if timer.is_alive():
                timer.cancel()
                kwargs = dict(timer.kwargs)
                kwargs.setdefault("logger", self.logger)
                timer.function(**kwargs)
            db_file = os.path.join(steward.fileio.settings_dir, "filebrowser.db")
            steward.delete((db_file,), self.logger)
