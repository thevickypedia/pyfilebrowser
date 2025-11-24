import logging

import docker

from pyfilebrowser.modals.settings import ContainerSettings


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
        config_volume: str,
        config_filename: str,
    ) -> None:
        """Run the Docker container for PyFilebrowser.

        Args:
            port: Host port to map to the container's port.
            data_volume: Root directory path to mount as data volume.
            config_volume: Config directory path to mount as config volume.
            config_filename: Configuration filename inside the config volume.
        """
        self.remove_existing()
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
            restart_policy={"Name": "no"},  # self.settings.restart},
            detach=True,
            environment={"CONFIG_FILE": config_filename},
        )

        if self.settings.detach:
            self.logger.info(f"Container started in detached mode: {container.name}")
            return

        try:
            for log in container.logs(stream=True):
                self.logger.info(log.strip().decode("utf-8"))
        except KeyboardInterrupt:
            container.stop()
            self.logger.info("Container %s has stopped.", container.name)
            container.remove()
            self.logger.info("Container %s has been removed.", container.name)
