# Access Tokens

When an OAuth provider is configured it will obtain an access token for each user. This access token may be used to authenticate with the service, e.g. to make requests to the provider itself or to make requests to other applications that use the same OAuth provider.

## Using access tokens

The `access_token` can be accessed via the session variable `pn.state.access_token`. As the name suggests this token will allow you to access privileged resources on the users behalf. Generally it can be used by adding it as a Bearer token in the `Authorization` header to a request, e.g.:

```python
import requests

requests.get(..., headers={'Authorization': f'Bearer {pn.state.access_token}'})
```

## Refreshing access tokens

Depending on the OAuth provider you are using the `access_token` may eventually expire, e.g. Okta tokens generally expire after 30 days by default while Azure defaults to 60 minute expiry. Since the `access_token` is cached as a cookie a user may still be logged in even when the `access_token` has expired. To ensure that you have access to a non-expired `access_token` you may set `--oauth-refresh-tokens` on the commandline, `PANEL_OAUTH_REFRESH_TOKENS=1` as an environment variable or the `oauth_refresh_tokens` argument to the `pn.serve` function if you are starting a server dynamically. Enabling this option will do a few things:

1. When a user accesses the application with an expired `access_token` it will automatically fetch a new `access_token` using the available `refresh_token`, or if no `refresh_token` is available it will force the user to re-authenticate.
2. While a user session is running Panel will automatically schedule the `access_token` to be refreshed 10 seconds before it expires.

```{note}
Some OAuth providers require you to explicitly request a `refresh_token` either in the settings or by requesting `offline_access` in the list of scopes.
```
