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

.. autoclass:: pyfilebrowser.modals.config.Defaults(pydantic.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Branding(pydantic.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Tus(pydantic.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Commands(pydantic.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Config(pydantic.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Server(pydantic.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.ReCAPTCHA(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Auther(pydantic.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.ConfigSettings(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.config.Theme(StrEnum)
   :members:
   :exclude-members:

====

.. autoclass:: pyfilebrowser.modals.config.Log(StrEnum)
   :members:
   :exclude-members:

Models
======

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
   :exclude-members: SortBy, Sorting, Perm

Users
=====

.. autoclass:: pyfilebrowser.modals.users.Authentication(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: pyfilebrowser.modals.users.UserSettings(pydantic.BaseSettings)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

Squire
======
Downloader
==========

.. autoclass:: pyfilebrowser.squire.downloader.Executable(pydantic.BaseModel)
   :members:
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. automodule:: pyfilebrowser.squire.downloader
   :members:
   :exclude-members: Executable

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

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
