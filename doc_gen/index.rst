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

--------Proxy Server--------
============================
Engine
======

.. automodule:: pyfilebrowser.proxy.main

Templates
=========

.. automodule:: pyfilebrowser.proxy.templates.templates

Rate Limit
==========

.. automodule:: pyfilebrowser.proxy.rate_limit

Repeated Timer
==============

.. automodule:: pyfilebrowser.proxy.repeated_timer

Server
======

.. automodule:: pyfilebrowser.proxy.server

Squire
======

.. automodule:: pyfilebrowser.proxy.squire

Settings
========

.. autoclass:: pyfilebrowser.proxy.settings.Destination(pydantic.BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.proxy.settings.EnvConfig(pydantic_settings.BaseSettings)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.proxy.settings.RateLimit(pydantic.BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.proxy.settings.Session(pydantic.BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

--------PyFB API Client--------
===============================
Main Module
===========

.. automodule:: pyfilebrowser.main

Modals
======
Configuration
=============

.. autoclass:: pyfilebrowser.modals.config.Server(pydantic_settings.BaseSettings)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Branding(pydantic_settings.BaseSettings)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Tus(pydantic_settings.BaseSettings)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Defaults(pydantic_settings.BaseSettings)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Commands(pydantic_settings.BaseSettings)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Config(pydantic_settings.BaseSettings)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.ReCAPTCHA(pydantic.BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Auther(pydantic_settings.BaseSettings)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.ConfigSettings(pydantic.BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

Models
======

.. autoclass:: pyfilebrowser.modals.models.Log(StrEnum)

====

.. autoclass:: pyfilebrowser.modals.models.Listing(StrEnum)

====

.. autoclass:: pyfilebrowser.modals.models.SortBy(StrEnum)

====

.. autoclass:: pyfilebrowser.modals.models.Theme(StrEnum)

====

.. autoclass:: pyfilebrowser.modals.models.Sorting(pydantic.BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.models.Perm(pydantic.BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. automodule:: pyfilebrowser.modals.models
   :exclude-members: Log, Listing, Theme, SortBy, Sorting, Perm

Users
=====

.. autoclass:: pyfilebrowser.modals.users.Authentication(pydantic.BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.users.UserSettings(pydantic_settings.BaseSettings)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

Squire
======
Download
========

.. autoclass:: pyfilebrowser.squire.download.Executable(pydantic.BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.squire.download.GitHub(pydantic.BaseSettings)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. automodule:: pyfilebrowser.squire.download
   :exclude-members: GitHub, Executable

Steward
=======

.. autoclass:: pyfilebrowser.squire.steward.EnvConfig(pydantic.BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.squire.steward.FileIO(pydantic.BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. automodule:: pyfilebrowser.squire.steward
   :exclude-members: EnvConfig, FileIO

Struct
======

.. automodule:: pyfilebrowser.squire.struct

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
