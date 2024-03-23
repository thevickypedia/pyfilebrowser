**Deployments**

![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue)

[![book][gha_pages_badge]][gha_pages]
[![pypi][gha_pypi_badge]][gha_pypi]

[![none-shall-pass][gha_none_shall_pass_badge]][gha_none_shall_pass]
[![Delete old workflow runs][gha_cleanup_workflows_badge]][gha_cleanup_workflows]

[![PyPI version shields.io](https://img.shields.io/pypi/v/pyfilebrowser)][pypi]
[![Pypi-format](https://img.shields.io/pypi/format/pyfilebrowser)](https://pypi.org/project/pyfilebrowser/#files)
[![Pypi-status](https://img.shields.io/pypi/status/pyfilebrowser)][pypi]

# PyFileBrowser
Introducing [`pyfilebrowser`][repo], a Python library designed to streamline interactions with [filebrowser][home]<br>

This wrapper simplifies integration and automation tasks, enabling seamless interaction with your local file system via
filebrowser's web interface.

All the required configuration, settings, and user profiles are loaded using `.env` files. This provides a more centralized
way of handling the configuration and initialization.

[`pyfilebrowser`][repo] automatically downloads the system specific executable during startup.

<details>
<summary><strong>Download custom-built executables</strong></summary>
<br>

Additionally, custom source _(to download binaries)_ can be configured by specifying the environment variables,
`GIT_OWNER` and `GIT_REPO`<br>
For this custom source feature to work, the executable should be uploaded to releases as assets,
and follow the naming convention below.

> **asset naming convention:** `${operating system}-{architecture}-filebrowser-{extension}`<br>
> **example:** `darwin-amd64-filebrowser.tar.gz`

</details>

## Kick Off
**Install**
```shell
python -m pip install pyfilebrowser
```

**Initiate**
```python
import pyfilebrowser


if __name__ == '__main__':
    browser = pyfilebrowser.FileBrowser()
    browser.start()
```

## Environment Variables
Env vars can either be loaded from `.env` files or directly passed during object init.

#### `.env` files

- `.config.env` - Loads the server's default configuration. Reference: [config]
- `.user*.env` - Loads each user's profile specific configuration. Reference: [users]

Multiple user profiles can be loaded using `.user1.env`, `.user2.env` and so on.<br>
User profile's permissions are automatically set based on the `admin` flag.

Refer [samples] directory for sample `.env` files. For nested configuration settings, refer the [runbook]

> Any configuration changes made in the UI will be lost, unless backed up manually.<br>
> Changes should always go through the `.env` files.

**[OR]**

```python
from pyfilebrowser import FileBrowser

if __name__ == '__main__':
    file_browser = FileBrowser(
        user_profiles=[
            {"authentication": {"username": "admin", "password": "admin", "admin": True}},
            {"authentication": {"username": "user123", "password": "pwd456", "admin": False}}
        ]
    )
    file_browser.start()
```

> Object level instantiation might be complex for configuration settings. So it is better to use `.env` files instead.

## Coding Standards
Docstring format: [`Google`][google-docs] <br>
Styling conventions: [`PEP 8`][pep8] and [`isort`][isort]

## [Release Notes][release-notes]
**Requirement**
```shell
pip install gitverse
```

**Usage**
```shell
gitverse-release reverse -f release_notes.rst -t 'Release Notes'
```

## Linting
`pre-commit` will ensure linting, and generate runbook

**Requirement**
```shell
pip install sphinx==5.1.1 pre-commit recommonmark
```

**Usage**
```shell
pre-commit run --all-files
```

## Pypi Package
[![pypi-module](https://img.shields.io/badge/Software%20Repository-pypi-1f425f.svg)][pypi-repo]

[https://pypi.org/project/pyfilebrowser/][pypi]

## Runbook
[![made-with-sphinx-doc](https://img.shields.io/badge/Code%20Docs-Sphinx-1f425f.svg)][sphinx]

[https://thevickypedia.github.io/pyfilebrowser/][runbook]

## License & copyright

&copy; Vignesh Rao

Licensed under the [MIT License][license]

[repo]: https://github.com/thevickypedia/pyfilebrowser
[samples]: https://github.com/thevickypedia/pyfilebrowser/tree/main/samples
[license]: https://github.com/thevickypedia/pyfilebrowser/blob/main/LICENSE
[config]: https://thevickypedia.github.io/pyfilebrowser/#configuration
[users]: https://thevickypedia.github.io/pyfilebrowser/#users
[home]: https://filebrowser.org/
[pypi]: https://pypi.org/project/pyfilebrowser
[pypi-repo]: https://packaging.python.org/tutorials/packaging-projects/
[sphinx]: https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html
[runbook]: https://thevickypedia.github.io/pyfilebrowser/
[gha_pages]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/pages/pages-build-deployment
[gha_pages_badge]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/pages/pages-build-deployment/badge.svg
[gha_pypi]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/python-publish.yml
[gha_pypi_badge]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/python-publish.yml/badge.svg
[gha_none_shall_pass]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/markdown.yml
[gha_none_shall_pass_badge]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/markdown.yml/badge.svg
[gha_cleanup_workflows]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/cleanup.yml
[gha_cleanup_workflows_badge]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/cleanup.yml/badge.svg
[release-notes]: https://github.com/thevickypedia/pyfilebrowser/blob/main/release_notes.rst
[google-docs]: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings
[pep8]: https://www.python.org/dev/peps/pep-0008/
[isort]: https://pycqa.github.io/isort/
