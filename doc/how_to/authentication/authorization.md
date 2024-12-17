# Authorization callbacks

The OAuth providers integrated with Panel provide an easy way to enable authentication on your applications. This verifies the identity of a user and also provides some level of access control (i.e. authorization). However often times the OAuth configuration is controlled by a corporate IT department or is otherwise difficult to manage so its often easier to grant permissions to use the OAuth provider freely but then restrict access controls in the application itself. To manage access you can provide an `authorize_callback` as part of your applications.

The `authorize_callback` can be configured on `pn.config` or via the `pn.extension`:

```python
import panel as pn

def authorize(user_info):
    with open('users.txt') as f:
        valid_users = f.readlines()
    return user_info['username'] in valid_users

pn.config.authorize_callback = authorize # or pn.extension(..., authorize_callback=authorize)
```

The `authorize_callback` is given a dictionary containing the data in the OAuth provider's `id_token` and optionally the current endpoint that the user is trying to access. The example above checks whether the current user is in the list of users specified in a `user.txt` file. However you can implement whatever logic you want to either grant a user access or reject it.

You may return either a boolean `True`/`False` value OR a string, which will be used to redirect the user to a different URL or endpoint. As an example, you may redirect users to specific endpoints:

```python
def authorize(user_info, page):
    user = user_info['user']
    if page == "/":
        if user in ADMINS:
            return '/admin'
        else:
            return '/user'
    elif user in ADMINS:
        return True
    else:
        return page.startswith('/user')
```

The callback above would direct users visiting the root (`/`) to the appropriate endpoint depending on whether they are in the list of `ADMINS`. If the user is an admin they are granted access to both the `/user` and `/admin` endpoints while non-admin users will only be granted access to the `/user` endpoint.

If a user is not authorized, i.e. the callback returns `False`, they will be presented with an authorization error template which can be configured using the `--auth-template` commandline option or by setting `config.auth_template`.

<img src="../../_static/images/authorization.png" width="600" style="margin-left: auto; margin-right: auto; display: block;"></img>

The auth template must be a valid Jinja2 template and accepts a number of arguments:

- `{{ title }}`: The page title.
- `{{ error_type }}`: The type of error.
- `{{ error }}`: A short description of the error.
- `{{ error_msg }}`: A full description of the error.

The `authorize_callback` may also contain a second parameter, which is set by the
requested application path. You can use this extra parameter to check if a user is
authenticated _and_ has access to the application at the given path.

```python
from urllib import parse
import panel as pn

authorized_user_paths = {
    "user1": ["/app1", "/app2"],
    "user2": ["/app1"],
}

def authorize(user_info, request_path):
    if current_user := authorized_user_paths.get(user_info['username']):
        current_path = parse.urlparse(request_path).path
        current_user_paths = authorized_user_paths[current_user]
        return current_path in current_user_paths
    return False

pn.config.authorize_callback = authorize
```
