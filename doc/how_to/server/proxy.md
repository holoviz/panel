# Configuring a reverse proxy

If the goal is to serve an web application to the general Internet, it is often desirable to host the application on an internal network, and proxy connections to it through some dedicated HTTP server. For some basic configurations to set up a Bokeh server behind some common reverse proxies, including Nginx and Apache, refer to the [Bokeh documentation](https://docs.bokeh.org/en/latest/docs/user_guide/server/deploy.html#basic-reverse-proxy-setup).

Two important things that can cause issues when deploying a Panel app behind a reverse proxy are issues with large client headers and handling of the root path.

## Client Headers

To communicate cookies and headers across processes, Panel may include this information in a JSON web token, sending it via a WebSocket. In certain cases this token can grow very large causing Nginx (or another reverse proxy) to drop the request. You may have to work around this by overriding the default Nginx setting `large_client_header_buffers`:

```
large_client_header_buffers 4 24k;
```

### Proxy with a stripped path prefixes

Configuring a proxy with a stripped path prefix, which is one common use of a proxy, means that you might serve a Panel app on `/app`, but then configure the proxy to serve the app under a path prefix like `/api/v1`. Unless you configure the proxy to forward appropriate headers Panel will have no idea that it is being served on a path prefix and may incorrectly configure internal redirects. To avoid this provide `panel` with a `root_path` when serving:

```bash
panel serve app.py --root-path /proxy/
```

Additionally, should you have configured an OAuth provider you **must** also declare an explicit `--oauth-redirect-uri` that includes the proxied path, e.g.:

```bash
panel serve app.py --root-path /api/v1/ ... --oauth-redirect-uri https://<my-host>/api/v1/login
```
