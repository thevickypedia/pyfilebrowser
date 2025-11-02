from pydantic_settings import BaseSettings


class PydanticEnvConfig(BaseSettings):
    """Pydantic BaseSettings with custom order for loading environment variables.

    >>> PydanticEnvConfig

    """

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """Order: dotenv, env, init, secrets files."""
        return dotenv_settings, env_settings, init_settings, file_secret_settings
