# Configuring OAuth

The OAuth component will stop any user from accessing the application before first logging into the selected provider. The configuration to set up OAuth is all handled via the global `pn.config` object, which has a number of OAuth related parameters. When launching the application via the `panel serve` CLI command these config options can be set as CLI arguments or environment variables, when using the `pn.serve` function on the other hand these variables can be passed in as arguments.

## `oauth_provider`

The first step in configuring a OAuth is to specify a specific OAuth provider. Panel ships with a number of providers by default:

* `azure`: Azure Active Directory
* `bitbucket`: Bitbucket
* `github`: GitHub
* `gitlab`: GitLab
* `google`: Google
* `okta`: Okta
* `generic`: Generic OAuth Provider with configurable endpoints
* `password`: Generic password grant based OAuth Provider with configurable endpoints
* `auth_code`: Generic code challenge grant based OAuth Provider with configurable endpoints

We will go through the process of configuring each of these individually in [Providers](./providers.md) but for now all we need to know that the `oauth_provider` can be set on the commandline using the `--oauth-provider` CLI argument to `panel serve` or the `PANEL_OAUTH_PROVIDER` environment variable.

Examples:

```
panel serve oauth_example.py --oauth-provider=...

PANEL_OAUTH_PROVIDER=... panel serve oauth_example.py
```

or in Python:

```python
pn.serve(app, oauth_provider=...)
```

## Endpoints

The login and logout endpoints are configurable:

```
panel serve oauth_example.py --login-endpoint="/signin" --logout-endpoint="/signoff"
```

or in Python:

```python
pn.serve(app, login_endpoint="/signin", logout_endpoint="/signoff", ...)
```

or in Python:


## `oauth_key` and `oauth_secret`

To authenticate with a OAuth provider we generally require two pieces of information (although some providers will require more customization):

1. The Client ID is a public identifier for apps.
2. The Client Secret is a secret known only to the application and the authorization server.

These can be configured in a number of ways the client ID and client secret can be supplied to the `panel serve` command as `--oauth-key` and `--oauth-secret` CLI arguments or `PANEL_OAUTH_KEY` and `PANEL_OAUTH_SECRET` environment variables respectively.

Examples:

```
panel serve oauth_example.py --oauth-key=... --oauth-secret=...

PANEL_OAUTH_KEY=... PANEL_OAUTH_KEY=... panel serve oauth_example.py ...
```

or in Python:

```python
pn.serve(app, oauth_key=..., oauth_secret=..., ...)
```

The only exception to authenticating with a `oauth_secret` are the generic password and code challenge based OAuth providers. If you picked one of these then you must only provide the client ID using the `--oauth-key` CLI argument or `PANEL_OAUTH_KEY` environment variable.

## `oauth_extra_params`

Some OAuth providers will require some additional configuration options which will become part of the OAuth URLs. The `oauth_extra_params` configuration variable allows providing this additional information and can be set using the `--oauth-extra-params` CLI argument or `PANEL_OAUTH_EXTRA_PARAMS`.

Examples:

```
panel serve oauth_example.py --oauth-extra-params={'tenant_id': ...}

PANEL_OAUTH_EXTRA_PARAMS={'tenant_id': ...} panel serve oauth_example.py ...
```

or in Python:

```python
pn.serve(app, oauth_extra_params={'tenant_id': ...}, ...)
```

The `oauth_extra_params` can also be used to provide the authentication URLs for the `'generic'`, `'password'`, and `'code'` OAuth providers. Specifically you can provide a `'AUTHORIZE_URL'`, `'TOKEN_URL'` and `'USER_URL'` as extra parameters. Lastly it may be used to define the [scopes](#Scopes).

## `cookie_secret`

Once authenticated the user information and authorization token will be set as secure cookies. Cookies are not secure and can easily be modified by clients. A secure cookie ensures that the user information cannot be interfered with or forged by the client by signing it with a secret key. Note that secure cookies guarantee integrity but not confidentiality. That is, the cookie cannot be modified but its contents can be seen by the user. To generate a `cookie_secret` use the `panel secret` CLI argument or generate some other random non-guessable string, ideally with at least 256-bits of entropy.

To set the `cookie_secret` supply `--cookie-secret` as a CLI argument or set the `PANEL_COOKIE_SECRET` environment variable.

Examples:

```
panel serve oauth_example.py --cookie-secret=...

PANEL_COOKIE_SECRET=... panel serve oauth_example.py ...
```

or in Python:

```python
pn.serve(app, cookie_secret="my-super-secret-secret", ...)
```

## `oauth_expiry`

The OAuth expiry configuration value determines for how long an OAuth token will be valid once it has been issued. By default it is valid for 1 day, but may be overwritten by providing the duration in the number of days (decimal values are allowed).

To set the `oauth_expiry` supply `--oauth-expiry-days` as a CLI argument or set the `PANEL_OAUTH_EXPIRY` environment variable.

Examples:

```
panel serve oauth_example.py --oauth-expiry-days=...

PANEL_OAUTH_EXPIRY=... panel serve oauth_example.py ...
```

## Encryption

The architecture of the Bokeh/Panel server means that credentials stored as cookies can be leak in a number of ways. On the initial HTTP(S) request the server will respond with the HTML document that renders the application and this will include an unencrypted token containing the OAuth information. To ensure that the user information and access token are properly encrypted we rely on the Fernet encryption in the `cryptography` library. You can install it with `pip install cryptography` or `conda install cryptography`.

Once installed you will be able to generate a encryption key with `panel oauth-secret`. This will generate a secret you can pass to the `panel serve` CLI command using the ``--oauth-encryption-key`` argument or `PANEL_OAUTH_ENCRYPTION` environment variable.

Examples:

```
panel serve oauth_example.py --oauth-encryption-key=...

PANEL_OAUTH_ENCRYPTION=... panel serve oauth_example.py ...
```

or in Python:

```python
pn.serve(app, oauth_encryption_key=...)
```

## Redirect URI

Once the OAuth provider has authenticated a user it has to redirect them back to the application, this is what is known as the redirect URI. For security reasons this has to match the URL registered with the OAuth provider exactly. By default Panel will redirect the user straight back to the original URL of your app, e.g. when you're hosting your app at `https://myapp.myprovider.com` Panel will use that as the redirect URI. However in certain scenarios you may override this to provide a specific redirect URI. This can be achieved with the `--oauth-redirect-uri` CLI argument or the `PANEL_OAUTH_REDIRECT_URI` environment variable.

Examples:

```
panel serve oauth_example.py --oauth-redirect-uri=...

PANEL_OAUTH_REDIRECT_URI=... panel serve oauth_example.py
```

## Scopes

OAuth allows the application to request specific scopes to perform certain actions when authenticating with the provider. To set the scopes you may set the `PANEL_OAUTH_SCOPE` environment variable or provide it as an argument using the `--oauth-extra-params {'scope': ...}` CLI argument.

Examples:

```
panel serve oauth_example.py --oauth-extra-params {'scope': 'openid'}

PANEL_OAUTH_SCOPE=openid panel serve oauth_example.py
```

or in Python:

```python
pn.serve(app, ..., oauth_extra_params={'scope': 'openid'})
```

## Summary

A fully configured OAuth configuration may look like this:

```
panel serve oauth_example.py --oauth-provider=github --oauth-key=... --oauth-secret=... --cookie-secret=... --oauth-encryption-key=...

PANEL_OAUTH_PROVIDER=... PANEL_OAUTH_KEY=... PANEL_OAUTH_SECRET=... PANEL_COOKIE_SECRET=... PANEL_OAUTH_ENCRYPTION=... panel serve oauth_example.py ...`
```

or in Python:

```python
pn.serve(app, oauth_provider='github', oauth_key=..., oauth_secret=..., cookie_secret=..., oauth_encryption_key=...)
```

For a generic, password, or code provider you may also have to provide the `TOKEN_URL`, `AUTHORIZE_URL` and `USER_URL` via the `--oauth-extra-params` CLI argument, `OAUTH_EXTRA_PARAMS` environment variable or in Python using the `oauth_extra_params` keyword argument.
