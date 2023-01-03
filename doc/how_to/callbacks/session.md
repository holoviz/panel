# Session callbacks

Whenever a request is made to an endpoint that is serving a Panel application a new session is created. If you have to perform some setup or tear down tasks on session creation (e.g. logging) you can define `on_session_created` and `on_session_destroyed` callbacks. 

## pn.state.on_session_created

WIP

## pn.state.on_session_destroyed

In many cases it is useful to define on_session_destroyed callbacks to perform any custom cleanup that is required, e.g,  dispose  a database engine, or when a user is logged out. These callbacks can be registered with `pn.state.on_session_destroyed(callback)`