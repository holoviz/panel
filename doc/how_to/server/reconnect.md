# Re-connecting to a Session

This guide walks you through configuring **automatic re-connection to Panel server sessions** when the connection is disrupted.

---

## Why re-connection matters

Whenever a user visits an endpoint, a new server session is created.
The session stays alive as long as the user remains connected.

However, in some scenarios—such as **poor internet connectivity** or **proxies interrupting WebSocket connections**—the connection between the server and the frontend may close.

By default, this **permanently disconnects** the application.
Recent versions of Panel introduce the ability to **automatically re-connect** to the server instead of dropping the session.

:::{note}
This feature requires Panel **≥1.8**.
If you are using an older version, you will need to upgrade.
:::

## Enabling re-connect

To enable automatic server re-connection, set the corresponding configuration option:

```python
import panel as pn

pn.config.reconnect = True

# or equivalently
pn.extension(reconnect=True)
```

When enabled, the following behavior is triggered if the WebSocket connection is lost:

1. An **exponential backoff loop** attempts to re-establish the connection (after 1, 2, 4, 8, 16, and 32 seconds).
   Users will see notifications during these attempts.

2. If all automatic attempts fail, a **final notification** is shown, offering the user a button to manually retry.

:::{tip}
You can customize the messages shown to the user—see [Configuring Notifications](#configuring-notifications).
:::


## Session management

Sessions are automatically managed by the server and periodically cleaned up if no active connection exists.

You can control session cleanup behavior via CLI flags or programmatically:

* **CLI (milliseconds):**

  ```bash
  panel serve app.py --unused-session-lifetime 30000 --check-unused-sessions 5000
  ```

* **Python:**

  ```python
  pn.serve(
      app,
      unused_session_lifetime_milliseconds=30000,
      check_unused_sessions_milliseconds=5000
  )
  ```

* `--unused-session-lifetime` / `unused_session_lifetime_milliseconds`
  How long to keep a disconnected session alive (default: **15s**).

* `--check-unused-sessions` / `check_unused_sessions_milliseconds`
  How often to check for unused sessions (default: **17s**).

### Blocking session expiration

Sometimes you may want to prevent a session from expiring—for example, if a **long-running computation** is in progress and you want the user to see the results even after re-connecting.

```python
pn.state.block_expiration()
# ... perform long-running task ...
pn.state.unblock_expiration()
```

:::{warning}
Blocking expiration indefinitely can cause **memory leaks**.
Always ensure you eventually call `pn.state.unblock_expiration()`, or schedule a timeout to release resources.
:::

---

## Configuring notifications

Panel provides options to customize the notifications shown when disconnection occurs:

* **`pn.config.disconnect_notification`**
  Message displayed when the server disconnects, along with information about automatic re-connect attempts.

:::{tip}
Use a short, user-friendly message like:
`pn.config.disconnect_notification = "Lost connection to server. Trying to reconnect..."`
:::

---

✅ With re-connection enabled, your Panel apps become **more resilient** to network issues, allowing users to continue their work without being forced to reload the page.
