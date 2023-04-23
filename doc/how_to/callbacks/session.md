# Run Tasks at Session Start or End

This guide addresses how to set up callbacks when a session is created and destroyed.

---

Whenever a request is made to an endpoint that is serving a Panel application a new session is created. If you have to perform some setup or tear down tasks on session creation (e.g. logging) you can define `on_session_created` and `on_session_destroyed` callbacks.

## pn.state.on_session_created

WIP

## pn.state.on_session_destroyed

In many cases it is useful to define `on_session_destroyed` callbacks to perform any custom cleanup that is required, e.g,  dispose  a database engine, log out a user etc.

The callbacks must have the signature

```python
def callback(session_context):
    ...
```

and can be registered with `pn.state.on_session_destroyed(callback)`.

## Related Resources
