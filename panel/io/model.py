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

from bokeh.core.serialization import Serializer
from bokeh.document import Document
from bokeh.document.events import (
    ColumnDataChangedEvent, DocumentPatchedEvent, ModelChangedEvent,
)
from bokeh.document.json import PatchJson
from bokeh.model import DataModel
from bokeh.models import ColumnDataSource, FlexBox, Model
from bokeh.protocol.messages.patch_doc import patch_doc

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
        return np.array_equal(self, other, equal_nan=True)

    def __ne__(self, other: Any) -> bool:
        return not np.array_equal(self, other, equal_nan=True)

def monkeypatch_events(events: List[DocumentChangedEvent]) -> None:
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
    doc: Document, binary: bool = True, events: Optional[List[DocumentChangedEvent]] = None
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
    monkeypatch_events(patch_events)
    serializer = Serializer(references=doc.models.synced_references, deferred=binary)
    patch_json = PatchJson(events=serializer.encode(patch_events))
    header = patch_doc.create_header()
    msg = patch_doc(header, {'use_buffers': binary}, patch_json)
    doc.callbacks._held_events = [e for e in doc.callbacks._held_events if e not in patch_events]
    doc.models.flush_synced(lambda model: not serializer.has_ref(model))
    if binary:
        for buffer in serializer.buffers:
            msg.add_buffer(buffer)
    return msg

def remove_root(obj: Model, replace: Document | None = None) -> None:
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

def add_to_doc(obj: Model, doc: Document, hold: bool = False):
    """
    Adds a model to the supplied Document removing it from any existing Documents.
    """
    # Add new root
    remove_root(obj)
    doc.add_root(obj)
    if doc.callbacks.hold_value is None and hold:
        doc.hold()

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

def bokeh_repr(obj: Model, depth: int = 0, ignored: Optional[Iterable[str]] = None) -> str:
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
    if isinstance(obj, FlexBox):
        r += '{cls}(children=[\n'.format(cls=cls)
        for obj in obj.children: # type: ignore
            r += textwrap.indent(bokeh_repr(obj, depth=depth+1) + ',\n', '  ')
        r += '], %s)' % props_repr
    else:
        r += '{cls}({props})'.format(cls=cls, props=props_repr)
    return r

@contextmanager
def hold(doc: Document, policy: HoldPolicyType = 'combine', comm: Comm | None = None):
    """
    Context manager that holds events on a particular Document
    allowing them all to be collected and dispatched when the context
    manager exits. This allows multiple events on the same object to
    be combined if the policy is set to 'combine'.

    Arguments
    ---------
    doc: Document
        The Bokeh Document to hold events on.
    policy: HoldPolicyType
        One of 'combine', 'collect' or None determining whether events
        setting the same property are combined or accumulated to be
        dispatched when the context manager exits.
    comm: Comm
        The Comm to dispatch events on when the context manager exits.
    """
    doc = doc or state.curdoc
    if doc is None:
        yield
        return
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
