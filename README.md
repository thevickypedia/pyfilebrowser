# PyFileBrowser
Automatic initializer for `filebrowser`

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

[config]: https://filebrowser.org/cli/filebrowser-config-set
[users]: https://filebrowser.org/cli/filebrowser-users-add
