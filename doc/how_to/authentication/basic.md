# Configuring Basic Authentication

For simple uses cases it may be totally sufficient to enable a basic Auth provider, which simply compares the provided login credentials against a master password or credentials stored in a file.

## Setting up basic authentication

Basic authentication can be set up simply by providing the `--basic-auth` commandline argument (or the `PANEL_BASIC_AUTH` environment variable):

```bash
panel serve app.py --basic-auth my_password --cookie-secret my_super_safe_cookie_secret
```

When loading the application you should now see a very simple login form:

![Panel Pyodide App](../../_static/images/basic_auth.png)

In this mode the username is not authenticated and will simply be provided as part of the [user info](user_info.md).

## User credentials

If you want a slightly more complex setup with a number of different users with potentially different access controls you can also provide a path to a file containing user credentials, e.g. let's say we have a file called `credentials.json` containing:

```json
{
    "user1": "my_password",
	"admin": "my_super_safe_password"
}
```

We can now configure the basic authentication with:

```bash
panel serve app.py --basic-auth credentials.json --cookie-secret my_super_safe_cookie_secret
```

The basic auth provider will now check the provided credentials against the credentials declared in this file.

## Custom templates

If you want to customize the authentication template you can provide a custom template with the `--basic-login-template` CLI argument. The template needs to submit `username` and `password` to the `/login` endpoint of the Panel server, e.g. the form of the default template looks like this:

```html
<form class="login-form" action="/login" method="post">
    <div class="form-header">
        <h3><img src="https://panel.holoviz.org/_images/logo_stacked.png" width="150" height="120"></h3>
        <p> Login to access your application</p>
    </div>
    <div class="form-group">
        <span style="color:rgb(255, 0, 0);font-weight:bold" class="errormessage">{{errormessage}}</span>
    </div>
    <p></p>
    <!--Email Input-->
    <div class="form-group">
        <input name="username" type="text" class="form-input" autocapitalize="off" autocorrect="off" placeholder="username">
    </div>
    <!--Password Input-->
    <div class="form-group">
        <input name="password" type="password" class="form-input" placeholder="password">
    </div>
    <!--Login Button-->
    <div class="form-group">
        <button class="form-button" type="submit">Login</button>
    </div>
    <div><small>
    <p><a href="https://panel.holoviz.org/how_to/authentication/index.html">See the documentation</a> for a full discussion.</p>
    </small></div>
</form>
```
