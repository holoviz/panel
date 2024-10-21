# Perspective Analysis

## The Problem

Panel has its own [Panel Perspective Widget](https://panel.holoviz.org/reference/index.html).

This widget wraps the `perspective-viewer` web component. Its does not import `perspective` or use other features of Perspective as described in the [Perspective Python User Guide](https://perspective.finos.org/docs/python/) or provided by the Jupyter Perspective widget.

I.e. the Panel Perspective Widget does not scale in the same way as the Juyter Perspective Widget or as a *best practice* solution based on a Tornado or FastAPI backend.

## How it works today

See [app_as_is.py](app_is_is.py).

```bash
panel serve analysis/app_as_is.py --dev
```

You can check out the typescript implementation [here](https://github.com/holoviz/panel/blob/main/panel/models/perspective.ts).

## How it could work in the future

### Use Externally Hosted Tables

We could ask the user to setup and deploy an externally hosted Perspective server and then in the Panel app the user can just do

```python
from panel.widgets import Perspective

pn.extension("perspective")

Perspective(
        value="name-of-table",
        websocket="wss://some-path/websocket",
        height=500, sizing_mode="stretch_width"
).servable()
```

This solution might perform and scale the best. But developing and managing the external server can also be very difficult for less technical users. And its not easily possible to dynamically update the perspective tables from the Panel apps - for example based on user input.

---

There is a POC of this concept in [app_external_server.py](app_external_server.py).

You can start the Perspective server with

```bash
python analysis/app_external_server.py
```

and the Panel server with

```bash
panel serve analysis/app_external_server.py --dev
```

As a minimum lots of documentation and examples is needed. While developing this solution I found the Perspective documentation is not updated to work with the latest version of Perspective this would scare most users of. I had to navigate the internal implementation of Perspective to create a working example.

### Use Internally Hosted Tables

We could integrate the Perspective server with the Panel/ Bokeh/ Tornado server. This would make things a lot easier for datascience users at the cost of for example scaling. And it would enable datascience developers to dynamically update the tables managed by perspective for example based on user interactions.

But we would probably have to have some if statements to figure out if Panel is running in Tornado, FastAPI, Pyodide or PY.CAFE environment and support that environment.

---

There is a POC of this concept in [app_internal_server.py](app_internal_server.py).

You can start the server with

```bash
python analysis/app_internal_server.py
```

We can later continue work on this solution to enable users to start this with `panel serve ...` which is the normal way for users to start the panel server.

We could maybe add a flag `--perspective` to signal to the panel server that it should add the perspective websocket end point and then enable the existing Perspective widget to take a table name as input. Or maybe it could be even simpler that the first time a named table is given as an argument to the Perspective widget, the websocket endpoint is started.

### Use Existing Communication Channels

Here we use the communication built into the [AnyWidget AFM Specification](https://anywidget.dev/en/afm/):

```typescript
/**
 * Send a custom message to the backend
 * @param content The content of the message
 * @param callbacks Optional callbacks for the message
 * @param buffers Optional binary buffers to send with the message
 */
send(content: any, callbacks?: any, buffers?: ArrayBuffer[] | ArrayBufferView[]): void;
```

instead of the `perspective.websocket` connection.

This could simplify things further as we don't need to add an endpoint. If it performs and scales well would have to be tested.

---

POC coming up ...
