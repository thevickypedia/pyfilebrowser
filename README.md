**Deployments**

[![book][gha_pages_badge]][gha_pages]
[![pypi][gha_pypi_badge]][gha_pypi]
[![none-shall-pass][gha_none_shall_pass_badge]][gha_none_shall_pass]

[![PyPI version shields.io](https://img.shields.io/pypi/v/stream-localhost)][pypi]
[![Pypi-format](https://img.shields.io/pypi/format/stream-localhost)](https://pypi.org/project/stream-localhost/#files)
[![Pypi-status](https://img.shields.io/pypi/status/stream-localhost)][pypi]

# PyFileBrowser
Automatic initializer for [`filebrowser`][home]

The primary purpose of this repository is to make the installation and configuration of [`filebrowser`][home] painless.
<br>
All the required configuration, settings, and user profiles are loaded using `.env` files.

## Environment Variables
Env vars can either be loaded from `.env` files or directly passed during object init.

#### `.env` files

- `.config.env` - Loads the server's default configuration. Reference: [config vars][config]
- `.user*.env` - Loads each user's profile specific configuration. Reference: [user vars][users]

Multiple user profiles can be loaded using `.user1.env`, `.user2.env` and so on.<br>
User profile's permissions are automatically set based on the `admin` flag.

> :warning:&nbsp;&nbsp;Any configuration changes made in the UI will be lost, unless backed up manually.<br>
Changes should always go through the `.env` files.

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
    file_browser.kickoff()
```

> :bulb:&nbsp;&nbsp;Object level instantiation might be complex for configuration settings. So it is better to use `.env` files instead.

## Linting
`pre-commit` will ensure linting, run pytest, generate runbook & release notes, and validate hyperlinks in ALL
markdown files (including Wiki pages)

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

[https://pypi.org/project/stream-localhost/][pypi]

## Runbook
[![made-with-sphinx-doc](https://img.shields.io/badge/Code%20Docs-Sphinx-1f425f.svg)][sphinx]

[https://thevickypedia.github.io/pyfilebrowser/][runbook]

## License & copyright

&copy; Vignesh Rao

Licensed under the [MIT License][license]

[license]: https://github.com/thevickypedia/pyfilebrowser/blob/main/LICENSE
[config]: https://filebrowser.org/cli/filebrowser-config-set
[users]: https://filebrowser.org/cli/filebrowser-users-add
[home]: https://filebrowser.org/
[pypi]: https://pypi.org/project/stream-localhost
[pypi-repo]: https://packaging.python.org/tutorials/packaging-projects/
[sphinx]: https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html
[runbook]: https://thevickypedia.github.io/pyfilebrowser/
[gha_pages]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/pages/pages-build-deployment
[gha_pages_badge]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/pages/pages-build-deployment/badge.svg
[gha_pypi]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/python-publish.yml
[gha_pypi_badge]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/python-publish.yml/badge.svg
[gha_none_shall_pass]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/markdown.yml
[gha_none_shall_pass_badge]: https://github.com/thevickypedia/pyfilebrowser/actions/workflows/markdown.yml/badge.svg
