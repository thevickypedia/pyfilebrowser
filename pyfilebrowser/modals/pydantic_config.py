import json
import os
import warnings
from typing import Any, Dict, Tuple, Type

from pydantic.aliases import AliasChoices
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

vault_client = None
if os.environ.get("PRE_COMMIT", "false") != "true":
    try:
        import vaultapi_client

        vault_client = vaultapi_client.VaultAPIClient()
    except Exception as exc:
        warnings.warn(exc.__str__(), ImportWarning)


def normalize_vault_secrets(
    settings_cls: Type[BaseSettings], secrets: Dict[str, Any]
) -> Dict[str, Any]:
    """Normalize the vault secrets.

    Args:
        settings_cls: Pydantic settings class.
        secrets: Secrets retrieved from vault.

    Returns:
        Dict[str, Any]
        Returns the normalized vault secrets.
    """
    result = {}
    for field_name, field in settings_cls.model_fields.items():
        # Normalize the value
        alias = field.validation_alias
        if alias is None:
            env_names = [field_name.upper()]
        elif isinstance(alias, AliasChoices):
            env_names = alias.choices
        else:
            env_names = [alias]
        for env_name in env_names:
            if env_name in secrets:
                value = secrets[env_name]
                if isinstance(value, str):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        # Not JSON; leave as-is.
                        pass
                result[field_name] = value
    return result


class VaultSettings(PydanticBaseSettingsSource):
    """Pydantic BaseSettings with custom load vault secrets.

    >>> VaultSettings

    """

    def __init__(self, settings_cls: Type[BaseSettings]):
        super().__init__(settings_cls)
        self.config = settings_cls.model_config
        # noinspection PyTypedDict
        self.table = self.config["vault_table"]

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        """Get the value for the given field.

        Args:
            field: Field instance with information about the field.
            field_name: Name of the field.

        Returns:
            Tuple[Any, str, bool]
            A tuple containing the key, value and a flag to determine whether value is complex.
        """
        return None, field_name, False

    def __call__(self) -> Dict[str, Any]:
        """Retrieve and normalize the vault secrets.

        Returns:
            Dict[str, Any]
            Returns the normalized vault secrets.
        """
        # Check if vault client is usable
        if not vault_client:
            return {}

        # Check if table exists in the vault DB
        if self.table not in vault_client.list_tables():
            return {}

        return normalize_vault_secrets(
            self.settings_cls, vault_client.get_table(self.table)
        )


class PydanticEnvConfig(BaseSettings):
    """Pydantic BaseSettings with custom order for loading environment variables.

    >>> PydanticEnvConfig

    """

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        """Order: vault, dotenv, env, init, secrets files."""
        return (
            VaultSettings(settings_cls),
            dotenv_settings,
            env_settings,
            init_settings,
            file_secret_settings,
        )

    class Config:
        """Extra configuration for PydanticEnvConfig object."""

        hide_input_in_errors = True
