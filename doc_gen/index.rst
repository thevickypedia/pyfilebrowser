.. PyFileBrowser documentation master file, created by
   sphinx-quickstart on Mon Mar 18 17:31:07 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyFileBrowser's documentation!
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Read Me:

   README

Main Module
===========

.. automodule:: pyfilebrowser.main
   :members:
   :undoc-members:

Modals
======
Configuration
=============

.. autoclass:: pyfilebrowser.modals.config.Server(pydantic_settings.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Branding(pydantic_settings.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Tus(pydantic_settings.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Defaults(pydantic_settings.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Commands(pydantic_settings.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Config(pydantic_settings.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.ReCAPTCHA(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Auther(pydantic_settings.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.ConfigSettings(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

Models
======

.. autoclass:: pyfilebrowser.modals.models.Log(StrEnum)
   :members:
   :exclude-members:

====

.. autoclass:: pyfilebrowser.modals.models.Theme(StrEnum)
   :members:
   :exclude-members:

====

.. autoclass:: pyfilebrowser.modals.models.SortBy(StrEnum)
   :members:
   :exclude-members:

====

.. autoclass:: pyfilebrowser.modals.models.Sorting(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.models.Perm(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. automodule:: pyfilebrowser.modals.models
   :members:
   :exclude-members: Log, Theme, SortBy, Sorting, Perm

Users
=====

.. autoclass:: pyfilebrowser.modals.users.Authentication(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.users.UserSettings(pydantic_settings.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

Squire
======
Download
========

.. autoclass:: pyfilebrowser.squire.download.Executable(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.squire.download.ExtendedEnvSettingsSource(pydantic_settings.EnvSettingsSource)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.squire.download.ExtendedSettingsConfigDict(pydantic_settings.SettingsConfigDict)
   :members:
   :exclude-members: _abc_impl, model_computed_fields, model_config, model_fields, env_prefixes, title, str_to_lower, str_to_upper, str_strip_whitespace, str_min_length, str_max_length, extra, frozen, populate_by_name, use_enum_values, validate_assignment, arbitrary_types_allowed, from_attributes, loc_by_alias, alias_generator, ignored_types, allow_inf_nan, json_schema_extra, json_encoders, strict, revalidate_instances, ser_json_timedelta, ser_json_bytes, ser_json_inf_nan, validate_default, validate_return, protected_namespaces, hide_input_in_errors, defer_build, plugin_settings, schema_generator, json_schema_serialization_defaults_required, json_schema_mode_override, coerce_numbers_to_str, regex_engine, validation_error_cause, case_sensitive, env_prefix, env_file, env_file_encoding, env_ignore_empty, env_nested_delimiter, env_parse_none_str, secrets_dir, json_file, json_file_encoding, yaml_file, yaml_file_encoding, toml_file

====

.. autoclass:: pyfilebrowser.squire.download.ExtendedBaseSettings(pydantic_settings.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_computed_fields, model_config, model_fields, env_prefixes, title, str_to_lower, str_to_upper, str_strip_whitespace, str_min_length, str_max_length, extra, frozen, populate_by_name, use_enum_values, validate_assignment, arbitrary_types_allowed, from_attributes, loc_by_alias, alias_generator, ignored_types, allow_inf_nan, json_schema_extra, json_encoders, strict, revalidate_instances, ser_json_timedelta, ser_json_bytes, ser_json_inf_nan, validate_default, validate_return, protected_namespaces, hide_input_in_errors, defer_build, plugin_settings, schema_generator, json_schema_serialization_defaults_required, json_schema_mode_override, coerce_numbers_to_str, regex_engine, validation_error_cause, case_sensitive, env_prefix, env_file, env_file_encoding, env_ignore_empty, env_nested_delimiter, env_parse_none_str, secrets_dir, json_file, json_file_encoding, yaml_file, yaml_file_encoding, toml_file
   :noindex:

====

.. autoclass:: pyfilebrowser.squire.download.GitHub(ExtendedBaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. automodule:: pyfilebrowser.squire.download
   :members:
   :exclude-members: ExtendedEnvSettingsSource, ExtendedSettingsConfigDict, ExtendedBaseSettings, GitHub, Executable

Steward
=======

.. autoclass:: pyfilebrowser.squire.steward.EnvConfig(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.squire.steward.FileIO(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. automodule:: pyfilebrowser.squire.steward
   :members:
   :exclude-members: EnvConfig, FileIO

Subtitles
=========

.. automodule:: pyfilebrowser.squire.subtitles
   :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
