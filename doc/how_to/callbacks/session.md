# Run Tasks at Session Start or End

This guide addresses how to set up callbacks when a session is created and destroyed.

---

Whenever a request is made to an endpoint that is serving a Panel application a new session is created. If you have to perform some setup or tear down tasks on session creation (e.g. logging) you can define `on_session_created` and `on_session_destroyed` callbacks.

```{note}
`on_session_destroyed` callbacks can be registered globally or from within a session, while `on_session_created` callbacks can only be created globally.
```

## pn.state.on_session_created

A session creation callback can be registered globally using the `pn.state.on_session_created` method. When we are already in a session it is not possible to set up such a callback. This means that to set up session creation callbacks when using `panel serve` on the commandline you must provide a `--setup` script, that will run before the server is started. In the case of a dynamically started server using `pn.serve` you can set the callback up before starting the server.

The callback must accept a `BokehSessionContext` as the first and only argument:

```python
def session_created(session_context: BokehSessionContext):
    print(f'Created a session running at the {session_context.request.uri} endpoint')

pn.state.on_session_created(session_created)
```

## pn.state.on_session_destroyed

In many cases it is useful to define `on_session_destroyed` callbacks to perform any custom cleanup that is required, e.g. dispose a database engine, log out a user etc. This can also be done globally in the `--setup` script or before launching the server but you may also register a session destroyed callback for a particular session by setting it up from inside a session. The callback must have the same signature as session creation callbacks:

```python
def session_destroyed(session_context):
    ...
```

and can be registered with `pn.state.on_session_destroyed(session_destroyed)`.

## Related Resources
