# Accessing User information

## User State

Once a user is authorized with the chosen OAuth provider certain user information and an `access_token` will be available to be used in the session to customize the user experience. Like all other session state this may be accessed on the `pn.state` object, specifically it makes four attributes available:

* **`pn.state.user`**: A unique name, email or ID that identifies the user.
* **`pn.state.access_token`**: The access token issued by the OAuth provider to authorize requests to its APIs.
* **`pn.state.refresh_token`**: The refresh token issued by the OAuth provider to authorize requests to its APIs (if available these are usually longer lived than the `access_token`).
* **`pn.state.user_info`**: Additional user information provided by the OAuth provider. This may include names, email, APIs to request further user information, IDs and more.

:::{note}

Please note that the user information above is only available to the users session. Its not shared across sessions.

:::

## Related Topics

- [Authorization Callbacks](authorization.md): Discover how to configure an authorization callback to perform custom authorization logic based on the user info such as redirects or error pages
