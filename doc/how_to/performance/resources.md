# Control when resources load

This guide addresses how Panel loads the JavaScript and CSS a component needs, and when you should declare those resources up front with `pn.extension`.

---

Many Panel components are thin wrappers around a JavaScript library: `Tabulator` needs tabulator-tables, `Plotly` needs plotly.js, `Perspective` needs perspective-viewer. Those libraries are not part of Panel itself, they are fetched by the browser.

## The default: load on demand

By default a component ships the list of libraries it needs alongside itself, and the browser fetches whatever is missing the first time the component renders. You do not have to tell Panel in advance:

```python
import panel as pn

pn.extension()

pn.widgets.Tabulator(df).servable()
```

The same holds for components created long after the page loaded, e.g. in a callback:

```python
def show_table(event):
    layout[:] = [pn.widgets.Tabulator(df)]

pn.widgets.Button(name='Show', on_click=show_table)
```

A library is fetched at most once per page no matter how many components ask for it, and components that share a library share the download. If a library cannot be fetched the component renders an error message in place of itself and the rest of the page is unaffected.

## Declaring extensions up front

Passing an extension to `pn.extension` still does something useful: it puts the `<script>` and `<link>` tags for that library directly into the page, so the browser starts fetching them while it is still parsing the HTML rather than after Panel has booted.

```python
pn.extension('tabulator', 'plotly')
```

Declare your extensions when:

- **Initial render latency matters.** An undeclared library costs one extra round trip after Panel has initialized. On a slow connection that is visible.
- **You are exporting self-contained HTML.** `pn.panel(...).save('out.html', resources=INLINE)` and `panel convert` embed the libraries in the output. There is nothing to embed for a component Panel did not know about, so an undeclared component in an `INLINE` export falls back to the CDN, and Panel warns about it.
- **The deployment has no internet access.** In `server` mode the libraries are served from the Panel server either way, but declaring them means the page does not depend on a runtime decision.

Conversely, leave them out when page weight matters: a dashboard that declares eight extensions loads eight libraries whether or not the user ever sees the components that need them.

:::{note}
Declaring an extension is a preloading hint, not a correctness requirement. Whether a library was preloaded or fetched on demand, it is registered in the same place on the client, so the two paths never load it twice.
:::

## Components that must be declared

Loading a *library* on demand works because libraries are just files. Loading a *Bokeh model definition* on demand does not, because the model has to exist before the document referencing it can be parsed. The `ipywidgets` extension registers such models, so it still has to be declared:

```python
pn.extension('ipywidgets')
```

## Configuration

`pn.config.lazy_resources` (default `True`) switches on-demand loading off entirely. With it disabled, a component whose extension was not declared cannot load its libraries and warns, which is the pre-1.10 behaviour.

`pn.config.resource_timeout` (default `15000`, in milliseconds) is how long a component waits for its libraries before it gives up and renders an error. Raise it for large libraries on slow connections, or set it to `0` to wait indefinitely.

```python
pn.extension()

pn.config.resource_timeout = 30000
```

## Authoring components

A custom component declares its resources as class attributes and gets on-demand loading for free:

```python
import panel as pn

class Confetti(pn.custom.JSComponent):

    __javascript__ = ['https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js']

    __css__ = ['https://example.com/confetti.css']

    _esm = """
    export function render() {
      confetti()
    }
    """
```

If several of your urls provide separate globals, declare `__js_skip__` so Panel can tell them apart and skip the ones the page already has:

```python
    __js_skip__ = {'confetti': __javascript__}
```

## Related resources

- [Reuse sessions](reuse_sessions.md)
- [Build custom components](../custom_components/index.md)
