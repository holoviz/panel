"""
Utilities for manipulating bokeh models.
"""
from __future__ import annotations

import textwrap

from contextlib import contextmanager
from typing import (
    TYPE_CHECKING, Any, Iterable, List, Optional,
)

import numpy as np

from bokeh.document import Document
from bokeh.document.events import (
    ColumnDataChangedEvent, DocumentPatchedEvent, ModelChangedEvent,
)
from bokeh.model import DataModel
from bokeh.models import Box, ColumnDataSource, Model
from bokeh.protocol import Protocol
from typing_extensions import Literal

from .state import state

if TYPE_CHECKING:
    from bokeh.core.enums import HoldPolicyType
    from bokeh.document.events import DocumentChangedEvent
    from bokeh.protocol.message import Message
    from pyviz_comms import Comm

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

class comparable_array(np.ndarray):
    """
    Array subclass that allows comparisons.
    """

    def __eq__(self, other: Any) -> bool:
        return super().__eq__(other).all().item()

    def __ne__(self, other: Any) -> bool:
        return super().__ne__(other).all().item()

def monkeypatch_events(events: List['DocumentChangedEvent']) -> None:
    """
    Patch events applies patches to events that are to be dispatched
    avoiding various issues in Bokeh.
    """
    for e in events:
        # Patch ColumnDataChangedEvents which reference non-existing columns
        if isinstance(getattr(e, 'hint', None), ColumnDataChangedEvent):
            e.hint.cols = None # type: ignore
        # Patch ModelChangedEvents which change an array property (see https://github.com/bokeh/bokeh/issues/11735)
        elif (isinstance(e, ModelChangedEvent) and isinstance(e.model, DataModel) and
              isinstance(e.new, np.ndarray)):
                new_array = comparable_array(e.new.shape, e.new.dtype, e.new)
                e.new = new_array
                e.serializable_new = new_array

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def diff(
    doc: 'Document', binary: bool = True, events: Optional[List['DocumentChangedEvent']] = None
) -> Message[Any] | None:
    """
    Returns a json diff required to update an existing plot with
    the latest plot data.
    """
    if events is None:
        events = list(doc.callbacks._held_events)
    if not events or state._hold:
        return None

    patch_events = [event for event in events if isinstance(event, DocumentPatchedEvent)]
    if not patch_events:
        return
    monkeypatch_events(events)
    msg_type: Literal["PATCH-DOC"] = "PATCH-DOC"
    msg = Protocol().create(msg_type, patch_events, use_buffers=binary)
    doc.callbacks._held_events = [e for e in doc.callbacks._held_events if e not in events]
    return msg

def remove_root(obj: 'Model', replace: Optional['Document'] = None) -> None:
    """
    Removes the document from any previously displayed bokeh object
    """
    for model in obj.select({'type': Model}):
        prev_doc = model.document
        model._document = None
        if prev_doc:
            prev_doc.remove_root(model)
        if replace:
            model._document = replace

def add_to_doc(obj: 'Model', doc: 'Document', hold: bool = False):
    """
    Adds a model to the supplied Document removing it from any existing Documents.
    """
    # Add new root
    remove_root(obj)
    doc.add_root(obj)
    if doc.callbacks.hold_value is None and hold:
        doc.hold()

@contextmanager
def hold(doc: 'Document', policy: 'HoldPolicyType' = 'combine', comm: Optional['Comm'] = None):
    held = doc.callbacks.hold_value
    try:
        if policy is None:
            doc.unhold()
        else:
            doc.hold(policy)
        yield
    finally:
        if held:
            doc.callbacks._hold = held
        else:
            if comm is not None:
                from .notebook import push
                push(doc, comm)
            doc.unhold()

def patch_cds_msg(model, msg):
    """
    Required for handling messages containing JSON serialized typed
    array from the frontend.
    """
    for event in msg.get('content', {}).get('events', []):
        if event.get('kind') != 'ModelChanged' or event.get('attr') != 'data':
            continue
        cds = model.select_one({'id': event.get('model').get('id')})
        if not isinstance(cds, ColumnDataSource):
            continue
        for col, values in event.get('new', {}).items():
            if isinstance(values, dict):
                event['new'][col] = [v for _, v in sorted(values.items())]

_DEFAULT_IGNORED_REPR = frozenset(['children', 'text', 'name', 'toolbar', 'renderers', 'below', 'center', 'left', 'right'])

def bokeh_repr(obj: 'Model', depth: int = 0, ignored: Optional[Iterable[str]] = None) -> str:
    """
    Returns a string repr for a bokeh model, useful for recreating
    panel objects using pure bokeh.
    """
    if ignored is None:
        ignored = _DEFAULT_IGNORED_REPR

    from ..viewable import Viewable
    if isinstance(obj, Viewable):
        obj = obj.get_root(Document())

    r = ""
    cls = type(obj).__name__
    properties = sorted(obj.properties_with_values(include_defaults=False).items())
    props = []
    for k, v in properties:
        if k in ignored:
            continue
        if isinstance(v, Model):
            v = '%s()' % type(v).__name__
        else:
            v = repr(v)
        if len(v) > 30:
            v = v[:30] + '...'
        props.append('%s=%s' % (k, v))
    props_repr = ', '.join(props)
    if isinstance(obj, Box):
        r += '{cls}(children=[\n'.format(cls=cls)
        for obj in obj.children: # type: ignore
            r += textwrap.indent(bokeh_repr(obj, depth=depth+1) + ',\n', '  ')
        r += '], %s)' % props_repr
    else:
        r += '{cls}({props})'.format(cls=cls, props=props_repr)
    return r
