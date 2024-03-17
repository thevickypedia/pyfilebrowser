# filebrowser
Startup settings for `filebrowser` (without Docker)

> :warning:&nbsp;&nbsp;Any configuration changes made in the UI will be lost, unless backed up manually.<br>
Changes should always go through the `.env` files.

## Environment Variables
Env vars can either be loaded from `.env` files or directly passed during object init.

#### `.env` files

- `.config.env` - Loads the server's default configuration.
- `.user*.env` - Loads each user's profile specific configuration.

Multiple user profiles can be loaded using `.user1.env`, `.user2.env` and so on.

**[OR]**

```python
from pyfb import FileBrowser

if __name__ == '__main__':
    file_browser = FileBrowser(
        user_profiles=[
            {"authentication": {"username": "admin", "password": "admin", "admin": True}},
            {"authentication": {"username": "user123", "password": "pwd456", "admin": False}}
        ]
    )
    file_browser.kickoff()
```
