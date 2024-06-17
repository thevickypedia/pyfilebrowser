Release Notes
=============

v0.1.0 (06/17/2024)
-------------------
- Includes a new feature `extra_env` to load additional configuration settings
- Includes CLI compatibility
- Proxy displays a warning page for unsupported browsers
- Add support for `.env` files to load GitHub env vars and replace `env_prefix` with `AliasChoices`

v0.0.91 (06/05/2024)
--------------------
- Includes a bug fix on `content-length` mismatch after VideoJS plugin integration
- Fixes misinformed logging for forbidden list and auth counter

v0.0.9 (05/21/2024)
-------------------
- Includes a variety of security features
- Includes rate limiting and brute force protection
- Restricts server access to specified origins
- Improved response for forbidden requests
- Includes a password complexity checker
- Automatically refreshes allowed origins in the background
- Adds CORS protection for proxy server
- Moved proxy flag to object instantiation
- Removes redundant logging for files that are streamed
- Gracefully shutdown the proxy server
- Uses Jinja2 templated error messages

v0.0.8 (04/05/2024)
-------------------
- Includes a proxy server for enhanced web security using cryptographic encryption
- Proxy feature adds more visibility in traffic through server
- Includes a feature to specify custom source versioning
- Bug fixes for upload issues, multi-layered binary archive
- Improved logging across the application

v0.0.7 (03/25/2024)
-------------------
- Auto convert subtitles' format from `.srt` to `.vtt`
- Auto delete subtitles (created during startup) upon exit
- Avoid auto convert during object init

v0.0.4 (03/23/2024)
-------------------
- Includes support for Windows OS
- Supports logging to `*.log` files

v0.0.3 (03/19/2024)
-------------------
- Update pypi description

v0.0.2 (03/19/2024)
-------------------
- Standardize automatic asset download process
- Streamline custom source control option for releases

v0.0.1 (03/18/2024)
-------------------
- Upload `pyfilebrowser` to pypi, with restriction to GitHub token
