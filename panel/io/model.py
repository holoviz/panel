"""
Utilities for manipulating bokeh models.
"""
import textwrap
from contextlib import contextmanager

from bokeh.document import Document
from bokeh.document.events import ColumnDataChangedEvent
from bokeh.models import Box, ColumnDataSource, Model
from bokeh.protocol import Protocol

from .state import state

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def diff(doc, binary=True, events=None):
    """
    Returns a json diff required to update an existing plot with
    the latest plot data.
    """
    events = list(doc._held_events) if events is None else events
    if not events or state._hold:
        return None

    # Patch ColumnDataChangedEvents which reference non-existing columns
    for e in events:
        if (hasattr(e, 'hint') and isinstance(e.hint, ColumnDataChangedEvent)
            and e.hint.cols is not None):
            e.hint.cols = None
    msg = Protocol().create("PATCH-DOC", events, use_buffers=binary)
    doc._held_events = [e for e in doc._held_events if e not in events]
    return msg


def remove_root(obj, replace=None):
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


def add_to_doc(obj, doc, hold=False):
    """
    Adds a model to the supplied Document removing it from any existing Documents.
    """
    # Add new root
    remove_root(obj)
    doc.add_root(obj)
    if doc._hold is None and hold:
        doc.hold()

@contextmanager
def hold(doc, policy='combine', comm=None):
    held = doc._hold
    try:
        if policy is None:
            doc.unhold()
        else:
            doc.hold(policy)
        yield
    finally:
        if held:
            doc._hold = held
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

def bokeh_repr(obj, depth=0, ignored=None):
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
    properties = sorted(obj.properties_with_values(False).items())
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
    props = ', '.join(props)
    if isinstance(obj, Box):
        r += '{cls}(children=[\n'.format(cls=cls)
        for obj in obj.children:
            r += textwrap.indent(bokeh_repr(obj, depth=depth+1) + ',\n', '  ')
        r += '], %s)' % props
    else:
        r += '{cls}({props})'.format(cls=cls,  props=props)
    return r
