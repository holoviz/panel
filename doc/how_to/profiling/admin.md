# Enable the admin panel

This guide addresses how to enable the admin Panel to begin monitoring resource usage and user behavior.

---

The `/admin` panel provides an overview of the current application and provides tools for debugging and profiling. It can be enabled by passing the ``--admin`` argument to the `panel serve` command.

```bash
panel serve my-app.py --admin
```

When you have successfully enabled it you should be able to visit the `/admin` endpoint of your application, e.g. if you are serving locally on port 5006, visit `http://localhost:5006/admin`. You should now be greeted with the overview page, which provides some details about currently active sessions, running versions and resource usage (if `psutil` is installed):

<img src="../../_static/images/admin_overview.png" width="70%"></img>

## Changing the admin panel endpoint

You can change the endpoint that the admin page is rendered at by using the flag `--admin-endpoint="/my-new-admin-endpoint"`. This will change where the admin endpoint is in the Bokeh server, and cause a `404: Not Found` page to be shown if you navigate to the default `/admin` path discussed above. As an example, using the following command to start your Panel app

```bash
panel serve my-app.py --admin --admin-endpoint="/my-new-admin-endpoint"
```

and navigating to [http://localhost:5006/admin](http://localhost:5006/admin) will result in a 404 page, however, navigating to [http://localhost:5006/my-new-admin-endpoint](http://localhost:5006/my-new-admin-endpoint) will result in the admin panel.

## Related Resources
