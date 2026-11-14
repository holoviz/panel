# Configuring a reverse proxy

If the goal is to serve an web application to the general Internet, it is often desirable to host the application on an internal network, and proxy connections to it through some dedicated HTTP server. For some basic configurations to set up a Bokeh server behind some common reverse proxies, including Nginx and Apache, refer to the [Bokeh documentation](https://docs.bokeh.org/en/latest/docs/user_guide/server/deploy.html#basic-reverse-proxy-setup).

Three things can cause issues when deploying a Panel app behind a reverse proxy: WebSocket connections, large client headers and the path the proxy serves the app on.

## WebSockets

A Panel app talks to the server over a WebSocket, so the proxy has to forward the `Upgrade` and `Connection` headers, and the server has to accept connections that originate from the public host:

```bash
panel serve app.py --allow-websocket-origin example.org
```

## Client Headers

To communicate cookies and headers across processes, Panel may include this information in a JSON web token, sending it via a WebSocket. In certain cases this token can grow very large causing Nginx (or another reverse proxy) to drop the request. You may have to work around this by overriding the default Nginx setting `large_client_header_buffers`:

```
large_client_header_buffers 4 24k;
```

## Serving on a path prefix

A proxy frequently serves an app on a sub-path of a host, e.g. `https://example.org/myapp/`. The pages Panel renders load their resources and open their WebSocket using URLs relative to the page, so they work on any path without configuration. Redirects are different: to send a user to the login page, back to the app after logging in, or to tell an OAuth provider where to return to, Panel has to know the public URL of the server. There are two ways to set this up.

### The proxy strips the prefix

The proxy removes the prefix before forwarding the request, so that `https://example.org/myapp/app` reaches Panel as `/app`. Panel then has to be told about the prefix, which can be done by the proxy itself or on the command line.

**Let the proxy declare it.** Start Panel with `--use-xheaders` and have the proxy set the standard forwarding headers:

```bash
panel serve app.py --use-xheaders --allow-websocket-origin example.org
```

```nginx
location /myapp/ {
    proxy_pass http://127.0.0.1:5006/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Prefix /myapp;
    proxy_buffering off;
}
```

With `--use-xheaders` Panel reads the following headers:

| Header | Used for |
| --- | --- |
| `X-Forwarded-Proto` | The protocol, `http` or `https` |
| `X-Forwarded-Host` | The public host, if the proxy does not pass on the `Host` header |
| `X-Forwarded-Prefix` (or `X-Script-Name`) | The path prefix the proxy stripped |
| `X-Forwarded-For` | The address of the client |

Some proxies set these on their own, e.g. the `StripPrefix` middleware of Traefik adds `X-Forwarded-Prefix`.

:::{warning}
Only enable `--use-xheaders` if the server can exclusively be reached through a proxy which sets or removes these headers. Otherwise a client can send them itself. Without the flag the headers are ignored.
:::

**Declare it on the command line.** If you cannot change the headers the proxy sets, provide the prefix with `--root-path`:

```bash
panel serve app.py --root-path /myapp --allow-websocket-origin example.org
```

An explicit `--root-path` takes precedence over the `X-Forwarded-Prefix` header.

### The proxy keeps the prefix

The proxy forwards the request unchanged and Panel serves everything below the prefix itself:

```bash
panel serve app.py --prefix /myapp --allow-websocket-origin example.org
```

```nginx
location /myapp/ {
    proxy_pass http://127.0.0.1:5006;
    ...
}
```

`--prefix` and `--root-path` may be combined if the proxy strips only part of the path.

## OAuth behind a proxy

The redirect URI Panel sends to the OAuth provider is the public URL of the server root, built from the protocol and host of the request, the root path and the prefix. In the examples above it is `https://example.org/myapp`, which is the URL you have to register with the provider. For this to work the protocol and host have to reach Panel, so either let the proxy pass on the `Host` header or set `X-Forwarded-Host`, and set `X-Forwarded-Proto` if the proxy terminates TLS, together with `--use-xheaders`.

If the public URL cannot be derived from the request, e.g. because the proxy listens on a non-standard port it does not report, declare the redirect URI explicitly. It has to point at the server root or at its login endpoint:

```bash
panel serve app.py --root-path /myapp ... --oauth-redirect-uri https://example.org/myapp/login
```

`--oauth-redirect-uri` only determines where the provider sends the user. Where Panel sends the user afterwards is determined by the root path, so a proxy which strips a prefix still needs `--root-path` or the `X-Forwarded-Prefix` header.
