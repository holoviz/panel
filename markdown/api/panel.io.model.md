# panel.io.model module

Utilities for manipulating bokeh models.

panel.io.model.add_to_doc(obj: Model, doc: Document, hold: bool = False, skip: set\[Model\] \| None = None)
Adds a model to the supplied Document removing it from any existing
Documents.

panel.io.model.bokeh_repr(obj: Model, depth: int = 0, ignored: Iterable\[str\] \| None = None) → str
Returns a string repr for a bokeh model, useful for recreating panel
objects using pure bokeh.

class panel.io.model.comparable_array
Bases: `ndarray`

Array subclass that allows comparisons.

panel.io.model.diff(doc: Document, binary: bool = True, events: list\[DocumentChangedEvent\] \| None = None) → Message\[t.Any\] \| None
Returns a json diff required to update an existing plot with the latest
plot data.

panel.io.model.monkeypatch_events(events: Sequence\[DocumentChangedEvent\]) → None
Patch events applies patches to events that are to be dispatched
avoiding various issues in Bokeh.

panel.io.model.patch_cds_msg(model, msg)
Required for handling messages containing JSON serialized typed array
from the frontend.

panel.io.model.remove_root(obj: Model, replace: Document \| None = None, skip: set\[Model\] \| None = None) → set\[Model\]
Removes the document from any previously displayed bokeh object

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
