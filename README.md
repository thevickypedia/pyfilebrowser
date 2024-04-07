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
    # browser.proxy = True  # [Optional] Enables proxy server to run in parallel
    browser.start()
```

## Environment Variables
Env vars can either be loaded from `.env` files or directly passed during object init.

#### `.env` files

<details>
<summary><strong>proxy server</strong></summary>

> `.proxy.env` - Loads the proxy server's configuration.

- `host` - Hostname/IP for the proxy server. _Defaults to `socket.gethostbyname('localhost')`_
- `port` - Port number for the proxy server. _Defaults to `8000`_
- `workers` - Number of workers used to run the proxy server. _Defaults to `1`_
- `debug` - Boolean flag to enable debug level logging. _Defaults to `False`_
- `origins` - Origins to allow connections through proxy server. _Defaults to `host`_ ***
- `public_ip` - Boolean flag to include public IP address of the host. _Defaults to `False`_
- `private_ip` - Boolean flag to include private IP address of the host. _Defaults to `False`_
- `error_page` - Error page to serve when filebrowser API is down. _Defaults to_ [error.html]
- `redis_host` - Hostname/IP for the redis server. _Defaults to `socket.gethostbyname('localhost')`_
- `redis_port` - Port number for the redis server. _Defaults to `6379`_
- `rate_limit` - `Dict/List[Dict]` with the rate limit for the proxy server. _Defaults to `None`_

</details>

<details>
<summary><strong>filebrowser configuration</strong></summary>

> `.config.env` - Loads the server's default configuration. Reference: [config]

</details>

<details>
<summary><strong>filebrowser user profiles</strong></summary>

>`.user*.env` - Loads each user's profile specific configuration. Reference: [users]

Multiple user profiles can be loaded using `.user1.env`, `.user2.env` and so on.<br>
User profile's permissions are automatically set based on the `admin` flag set in the env-var `authentication`

</details>

Refer [samples] directory for sample `.env` files. For nested configuration settings, refer the [runbook]

> Any configuration changes made in the UI will be lost, unless backed up manually.<br>
> Changes should always go through the `.env` files.

<details>
<summary><strong>Object level instantiation is also possible, but not recommended</strong></summary>

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

</details>

## Proxy Server
`pyfilebrowser` allows you to run a proxy server in parallel, which helps the user with much more logging information,
and secured connections.

The proxy server is pretty restrictive in nature, and doesn't like connections from outside the grid.

While CORS may solve the purpose at the webpage level, `pyfilebrowser`'s inbuilt proxy restricts connections
from any origin regardless of the tool used to connect (PostMan, curl, wget etc.)

Due to this behavior, please make sure to specify **ALL** the origins that are supposed to be allowed
(including but not limited to reverse-proxy, CDN, redirect servers etc.)

> Enabling proxy server increases an inconspicuous latency to the connections,
> but due to asynchronous functionality, and the rendered payload size it is hardly noticeable.

### Rate Limiter
`pyfilebrowser`'s built-in proxy service allows you to implement a rate limiter.<br>
[Rate limiting] allows you to prevent [DDoS] attacks and maintain server stability and performance.

> This feature requires a [redis] server running on the host machine.

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
[error.html]: https://github.com/thevickypedia/pyfilebrowser/blob/main/pyfilebrowser/proxy/error.html
[redis]: https://redis.io/docs/install/install-redis/
[Rate limiting]: https://www.cloudflare.com/learning/bots/what-is-rate-limiting/
[DDoS]: https://www.cloudflare.com/learning/ddos/glossary/denial-of-service/
