# Modify Bokeh Models

This guide addresses how to safely modify Bokeh models to avoid running into issues with the Bokeh `Document` lock.

---

The Bokeh server that Panel builds on is designed to be thread safe which requires a set of locks to avoid multiple threads modifying the Bokeh models simultaneously.  Panel being a high-level wrapper around Bokeh handles this locking for you. However, when you update Bokeh components directly you may need to schedule a callback to get around Bokeh's document lock to avoid errors like this:

```
RuntimeError: _pending_writes should be non-None when we have a document lock, and we should have the lock when the document changes
```

In the example below we will launch an application on a thread using `pn.serve` and make the Bokeh plot (in practice you may provide handles to this object on a class). To schedule a callback which updates the `y_range` by using the `pn.state.execute` method. This pattern will ensure that the update to the Bokeh model is executed on the correct thread:

```python
import time
import panel as pn

from bokeh.plotting import figure

def app():
    p = figure()
    p.line([1, 2, 3], [1, 2, 3])
    return p

pn.serve(app, threaded=True)

pn.state.execute(lambda: p.y_range.update(start=0, end=4))
```

## Related Resources
