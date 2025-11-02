## Server Configuration
Filebrowser's server configuration.

File source: `.config.env`

#### Branding
Configuration for the custom branding settings for the server.

- **branding_name** - Instance name that will show up on login and signup pages.
- **branding_disableExternal** - This will disable any external links.
- **branding_disableUsedPercentage** - Disables the used volume percentage.
- **branding_files** - The path to the branding files.
    - custom.css: Containing the styles you want to apply to your installation.
    - img: A directory whose files can replace the default logotypes in the application.
- **branding_theme** - The theme of the brand. Uses system default if not set.
- **branding_color** - The color of the brand.

#### TUS
Configuration for the upload settings in the server.

- **tus_chunkSize** - The size of the chunks to be uploaded.
- **tus_retryCount** - The number of retries to be made in case of a failure.

#### Defaults
Configuration for all the default settings for the server.

- **defaults_scope** - The default scope for the users. Defaults to the root directory.
- **defaults_locale** - The default locale for the users. Locale is an RFC 5646 language tag.
- **defaults_viewMode** - The default view mode for the users.
- **defaults_singleClick** - The default single click setting for the users.
- **defaults_sorting** - The default sorting settings for the users.
- **defaults_perm** - The default permission settings for the users.
- **defaults_commands** - The default list of commands that can be executed by users.
- **defaults_hideDotfiles** - The default setting to hide dotfiles.
- **defaults_dateFormat** - The default setting to set the exact date format.

#### Commands
Configuration for list of the commands to be executed before or after a certain event.

- **commands_after_copy** - List of commands to be executed after copying a file.
- **commands_after_delete** - List of commands to be executed after deleting a file.
- **commands_after_rename** - List of commands to be executed after renaming a file.
- **commands_after_save** - List of commands to be executed after saving a file.
- **commands_after_upload** - List of commands to be executed after uploading a file.
- **commands_before_copy** - List of commands to be executed before copying a file.
- **commands_before_delete** - List of commands to be executed before deleting a file.
- **commands_before_rename** - List of commands to be executed before renaming a file.
- **commands_before_save** - List of commands to be executed before saving a file.
- **commands_before_upload** - List of commands to be executed before uploading a file.

#### Server
Configuration for the server.

- **root** - The root directory for the server. Contents of this directory will be served.
- **symlinks** - List of symlinks to be created in the root directory. Accepts file or directory paths.
- **baseURL** - The base URL for the server.
- **socket** - Socket to listen to (cannot be used with ``address``, ``port`` or TLS settings)
- **tlsKey** - The TLS key for the server.
- **tlsCert** - The TLS certificate for the server.
- **port** - The port for the server.
- **address** - Address to listen on. Defaults to ``127.0.0.1``
- **log** - The log settings for the server.
- **enableThumbnails** - Enable thumbnails for the server.
- **resizePreview** - Resize the preview for the server.
- **enableExec** - Enable command execution for the server.
- **typeDetectionByHeader** - Enable type detection by header for the server.
- **authHook** - The authentication hook for the server.
- **tokenExpirationTime** - The token expiration time for the server.

#### Config
Configuration for the user authentication.

- **signup** - Enable signup option for new users.
- **createUserDir** - Auto create user home dir while adding new user.
- **userHomeBasePath** - The base path for user home directories.
- **authMethod** - The authentication method for the server.
- **authHeader** - The authentication header for the server.
- **shell_** - The shell settings for the server.
- **rules** - This is a global set of allow and disallow rules. They apply to every user.

#### Auther
Configuration for server security.

- **auth_recaptcha** - ReCaptcha settings for the server.
- **auth_token** - The authenticator token for TOTP.

## User Profiles
Configuration for user profiles.

File source: `.user*.env`

> Since there can be multiple user profiles for a server, each user profile has to have it's own `.env` file. Ex: (`.user_1.env`, `.user_2.env`, `.user_3.env` etc..)

- **authentication** - Authentication settings for each user profile.
- **scope** - The default scope for the users. Defaults to the root directory.
- **locale** - The default locale for the users. Locale is an RFC 5646 language tag.
- **lockPassword** - Default setting to prevent the user from changing the password.
- **viewMode** - Default view mode for the users.
- **singleClick** - Use single clicks to open files and directories.
- **commands** - List of commands that can be executed by the user.
- **sorting** - Default sorting settings for the user.
- **rules** - List of allow and disallow rules. This overrides the server's default rules.
- **hideDotfiles** - Default setting to hide dotfiles.
- **dateFormat** - Default setting to set the exact date format.

## GitHub
Configuration to download the `filebrowser` executable from GitHub.

File source: `.github.env`

- **owner** - GitHub account username or organization name.
- **repo** - Repository name where the executable is stored in the releases.
- **token** - GitHub account PAT.
- **version** - Release version to download the asset.

## Extra (specific for [thevickypedia/filebrowser])
Extra configuration that needs to be added for the server.

File source: `extra.yaml` or `extra.json`

## Proxy
Proxy server configuration.

File source: `.proxy.env`

> Use proxy server only after reading [proxy-readme] and [proxy-runbook]

- **host**: The host address for the server.
- **port**: The port number for the server.
- **workers**: The number of worker processes for handling requests.
- **debug**: Enable or disable debug mode.
- **origins**: A list of allowed origins for CORS.
- **database**: The path to the database file.
- **allow_public_ip**: Allow access from public IP address.
- **allow_private_ip**: Allow access from private IP address.
- **origin_refresh**: Time interval to refresh allowed origins.
- **rate_limit**: Rate limiting settings for incoming requests.
- **unsupported_browsers**: List of unsupported browsers. _This is a **beta** feature_
- **warn_page**: Path to the custom warning page HTML file.
- **error_page**: Path to the custom error page HTML file.

[thevickypedia/filebrowser]: https://github.com/thevickypedia/filebrowser
[proxy-runbook]: https://thevickypedia.github.io/pyfilebrowser/index.html#proxy-server
[proxy-readme]: https://thevickypedia.github.io/pyfilebrowser/README.html#proxy-server
