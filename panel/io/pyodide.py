from __future__ import annotations

import asyncio
import functools
import io
import json
import os
import sys
import uuid

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

import bokeh
import js
import param

import pyodide # isort: split

from bokeh import __version__
from bokeh.core.serialization import Buffer, Serialized, Serializer
from bokeh.document import Document
from bokeh.document.json import PatchJson
from bokeh.embed.elements import script_for_render_items
from bokeh.embed.util import standalone_docs_json_and_render_items
from bokeh.embed.wrappers import wrap_in_script_tag
from bokeh.events import DocumentReady
from bokeh.io.doc import set_curdoc
from bokeh.model import Model
from bokeh.settings import settings as bk_settings
from js import JSON, XMLHttpRequest

from ..config import config
from ..util import edit_readonly, isurl
from . import resources
from .document import MockSessionContext
from .loading import LOADING_INDICATOR_CSS_CLASS
from .mime_render import WriteCallbackStream, exec_with_return, format_mime
from .state import state

resources.RESOURCE_MODE = 'CDN'
os.environ['BOKEH_RESOURCES'] = 'cdn'

if TYPE_CHECKING:
    from bokeh.core.types import ID

    from ..template.base import TemplateBase
    from ..viewable import Viewable

try:
    from js import document as js_document  # noqa
    try:
        # PyScript Next Worker now patches js.document by default
        from pyscript import RUNNING_IN_WORKER as _IN_PYSCRIPT_WORKER
        if _IN_PYSCRIPT_WORKER:
            from pyscript import window
            js.window = window
    except Exception:
        _IN_PYSCRIPT_WORKER = False
    _IN_WORKER = False
except Exception:
    try:
        # Initial version of PyScript Next Worker support did not patch js.document
        from pyscript import RUNNING_IN_WORKER as _IN_PYSCRIPT_WORKER
        if _IN_PYSCRIPT_WORKER:
            from pyscript import document, window
            js.document = document
            js.window = window
        _IN_WORKER = False
    except Exception:
        _IN_PYSCRIPT_WORKER = False
        _IN_WORKER = True

# Ensure we don't try to load MPL WASM backend in worker
if _IN_WORKER:
    os.environ['MPLBACKEND'] = 'agg'

try:
    import pyodide_http
    pyodide_http.patch_all()
except Exception:
    pyodide_http = None

try:
    # Patch fsspec with synchronous http support
    import fsspec.implementations.http_sync  # noqa
except Exception:
    pass

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

# Make bokeh sampledata available in pyolite kernel
if 'pyolite' in sys.modules and os.path.exists('/drive/assets/sampledata'):
    def _sampledata_dir(create=None):
        return '/drive/assets/sampledata'
    bokeh.util.sampledata.external_data_dir = _sampledata_dir

if pyodide_http is None:
    import pandas

    def _read_file(*args, **kwargs):
        if args and isurl(args[0]):
            args = (pyodide.http.open_url(args[0]),)+args[1:]
        elif isurl(kwargs.get('filepath_or_buffer')):
            kwargs['filepath_or_buffer'] = pyodide.http.open_url(kwargs['filepath_or_buffer'])
        return args, kwargs

    # Patch pandas.read_csv
    _read_csv_original = pandas.read_csv
    @functools.wraps(pandas.read_csv)
    def _read_csv(*args, **kwargs):
        args, kwargs = _read_file(*args, **kwargs)
        return _read_csv_original(*args, **kwargs)
    pandas.read_csv = _read_csv  # type: ignore

    # Patch pandas.read_json
    _read_json_original = pandas.read_json
    @functools.wraps(pandas.read_json)
    def _read_json(*args, **kwargs):
        args, kwargs = _read_file(*args, **kwargs)
        return _read_json_original(*args, **kwargs)
    pandas.read_json = _read_json  # type: ignore

_tasks = set()

def async_execute(func: Any):
    event_loop = asyncio.get_running_loop()
    if event_loop.is_running():
        task = asyncio.create_task(func())
        _tasks.add(task)
        task.add_done_callback(_tasks.discard)
    else:
        event_loop.run_until_complete(func())
    return

param.parameterized.async_executor = async_execute

def _doc_json(doc: Document, root_els=None) -> tuple[str, str, str]:
    """
    Serializes a Bokeh Document into JSON representations of the entire
    Document, the individual render_items and the ids of DOM nodes to
    render each item into.

    Parameters
    ----------
    doc: bokeh.document.Document
        The Bokeh document to serialize to JSON.
    root_els:
        A list of DOM nodes to render each root of the Document into.

    Returns
    -------
    docs_json: str
    render_items: str
    root_ids: str
    """
    docs_json, render_items = standalone_docs_json_and_render_items(
        doc.roots, suppress_callback_warning=True
    )
    render_items_json = [item.to_json() for item in render_items]
    root_ids = [m.id for m in doc.roots]
    if root_els:
        root_data = sorted([(el.getAttribute('data-root-id'), el.id) for el in root_els])
        render_items_json[0].update({
            'roots': {model_id: elid for (_, elid), model_id in zip(root_data, root_ids)},
            'root_ids': root_ids
        })
    return json.dumps(docs_json), json.dumps(render_items_json), json.dumps(root_ids)

def _model_json(viewable: Viewable | TemplateBase, target: str) -> tuple[Document, str]:
    """
    Renders a Bokeh Model to JSON representation given a particular
    DOM target and returns the Document and the serialized JSON string.

    Parameters
    ----------
    model: Viewable
        The bokeh model to render.
    target: str
        The id of the DOM node to render to.

    Returns
    -------
    viewable: The Viewable to render to JSON
        The viewable to render
    document: Document
        The bokeh Document containing the rendered Bokeh Model.
    model_json: str
        The serialized JSON representation of the Bokeh Model.
    """
    doc = Document()
    doc.hold()
    viewable.server_doc(doc=doc)
    model = doc.roots[0]
    docs_json, _ = standalone_docs_json_and_render_items(
        [model], suppress_callback_warning=True
    )
    doc_json = list(docs_json.values())[0]

    return doc, json.dumps(dict(
        target_id = target,
        root_id   = model.ref['id'],
        doc       = doc_json,
        version   = __version__,
    ))

def _serialize_buffers(obj, buffers={}):
    """
    Recursively iterates over a JSON patch and converts Buffer objects
    to a reference or base64 serialized representation.

    Parameters
    ----------
    obj: dict
        Dictionary containing events to patch the JS Document with.
    buffers: dict
        Binary array buffers.

    Returns
    --------
    Serialization safe version of the original object.
    """
    if isinstance(obj, dict):
        return {
            key: _serialize_buffers(o, buffers=buffers) for key, o in obj.items()
        }
    elif isinstance(obj, list):
        return [
            _serialize_buffers(o, buffers=buffers) for o in obj
        ]
    elif isinstance(obj, tuple):
        return tuple(
            _serialize_buffers(o, buffers=buffers) for o in obj
        )
    elif isinstance(obj, Buffer):
        if obj.id in buffers: # TODO: and len(obj.data) > _threshold:
            return obj.ref
        else:
            return obj.to_base64()
    return obj

def _process_document_events(doc: Document, events: list[Any]):
    serializer = Serializer(references=doc.models.synced_references)
    patch_json = PatchJson(events=serializer.encode(events))
    doc.models.flush_synced()

    buffer_map = {}
    for buffer in serializer.buffers:
        buffer_map[buffer.id] = pyodide.ffi.to_js(buffer.to_bytes()).buffer
    patch_json = _serialize_buffers(patch_json, buffers=buffer_map)
    return patch_json, buffer_map

# JS function to convert undefined -> null (workaround for https://github.com/pyodide/pyodide/issues/3968)
_dict_converter = pyodide.code.run_js("""
((entries) => {
  for (let entry of entries) {
    if (entry[1] === undefined) {
      entry[1] = null;
    }
  }
  return Object.fromEntries(entries);
})
""")

_current_buffers = []
_patching = False

def _bytes_converter(value, converter, other):
    if not hasattr(value, 'buffer'):
        return value
    value = dict(value.object_entries())
    uid = uuid.uuid4().hex
    _current_buffers.append(
        Buffer(id=uid, data=value['buffer'].to_bytes())
    )
    return {'id': uid}

def _convert_json_patch(json_patch):
    try:
        patch = json_patch.to_py(default_converter=_bytes_converter)
        serialized = Serialized(content=patch, buffers=list(_current_buffers))
    finally:
        _current_buffers.clear()
    return serialized

def _link_docs(pydoc: Document, jsdoc: Any) -> None:
    """
    Links Python and JS documents in Pyodide ensuring that messages
    are passed between them.

    Parameters
    ----------
    pydoc: bokeh.document.Document
        The Python Bokeh Document instance to sync.
    jsdoc: Javascript Document
        The Javascript Bokeh Document instance to sync.
    """

    def jssync(event):
        setter_id = getattr(event, 'setter_id', None)
        if (setter_id is not None and setter_id == 'python') or _patching:
            return
        json_patch = jsdoc.create_json_patch(pyodide.ffi.to_js([event]))
        patch = _convert_json_patch(json_patch)
        pydoc.apply_json_patch(patch, setter='js')

    jsdoc.on_change(pyodide.ffi.create_proxy(jssync), pyodide.ffi.to_js(False))

    def pysync(event):
        global _patching
        setter = getattr(event, 'setter', None)
        if setter is not None and setter == 'js':
            return
        json_patch, buffer_map = _process_document_events(pydoc, [event])
        json_patch = pyodide.ffi.to_js(json_patch, dict_converter=_dict_converter)
        buffer_map = pyodide.ffi.to_js(buffer_map)
        _patching = True
        try:
            jsdoc.apply_json_patch(json_patch, buffer_map)
        finally:
            _patching = False

    pydoc.on_change(pysync)

    try:
        pydoc.unhold()
        pydoc.callbacks.trigger_event(DocumentReady())
    except Exception as e:
        print(f'Error raised while processing Document events: {e}')  # noqa: T201

def _link_docs_worker(doc: Document, dispatch_fn: Any, msg_id: str | None = None, setter: str | None = None):
    """
    Links the Python document to a dispatch_fn which can be used to
    sync messages between a WebWorker and the main thread in the
    browser.

    Parameters
    ----------
    doc: bokeh.document.Document
        The document to dispatch messages from.
    dispatch_fn: JS function
        The Javascript function to dispatch messages to.
    setter: str
        Setter ID used for suppressing events.
    msg_id: str | None
        An optional message ID to pass through to the dispatch_fn.
    """
    def pysync(event):
        if setter is not None and getattr(event, 'setter', None) == setter:
            return
        json_patch, buffer_map = _process_document_events(doc, [event])
        json_patch = pyodide.ffi.to_js(json_patch, dict_converter=_dict_converter)
        buffers = js.Map.new(pyodide.ffi.to_js(buffer_map))
        dispatch_fn(json_patch, buffers, msg_id)

    doc.on_change(pysync)
    doc.unhold()
    doc.callbacks.trigger_event(DocumentReady())

async def _link_model(ref: str, doc: Document) -> None:
    """
    Links a rendered Bokeh model on the frontend to a Python Document
    in Python.

    Parameters
    ----------
    ref: str
        The ID of the rendered bokeh Model
    doc: bokeh.document.Document
        The bokeh Document to sync the rendered Model with.
    """
    rendered = js.window.Bokeh.index.object_keys()
    if ref not in rendered:
        await asyncio.sleep(0.1)
        await _link_model(ref, doc)
        return
    views = js.window.Bokeh.index.object_values()
    view = views[rendered.indexOf(ref)]
    _link_docs(doc, view.model.document)

def _get_pyscript_target():
    if '__main__' in sys.modules and hasattr(sys.modules['__main__'], 'get_current_display_target'):
        # pyscript >= 2022.10.01
        return sys.modules['__main__'].get_current_display_target()
    elif hasattr(sys.stdout, '_out'):
        # pyscript <= 2022.09.01
        return sys.stdout._out # type: ignore
    elif not _IN_WORKER:
        raise ValueError("Could not determine target node to write to.")

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def fetch_binary(url):
    if not _IN_WORKER:
        raise RuntimeError("Cannot make synchronous binary request in main thread.")
    xhr = XMLHttpRequest.new()
    xhr.responseType = "arraybuffer"
    xhr.open('get', url, False)
    xhr.send()
    return io.BytesIO(xhr.response.to_py().tobytes())

def render_script(obj: Any, target: ID) -> str:
    """
    Generates a script to render the supplied object to the target.

    Parameters
    ----------
    obj: Viewable
        Object to render into the DOM node
    target: str
        Target ID of the DOM node to render the object into.
    """
    from js import document

    from ..pane import panel as as_panel

    doc = Document()
    as_panel(obj).server_doc(doc, location=False)
    docs_json, [render_item,] = standalone_docs_json_and_render_items(
        doc.roots, suppress_callback_warning=True
    )
    for root in doc.roots:
        render_item.roots._roots[root] = target
    document.getElementById(target).classList.add('bk-root')
    script = script_for_render_items(docs_json, [render_item])
    task = asyncio.create_task(_link_model(doc.roots[0].ref['id'], doc))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)
    return wrap_in_script_tag(script)

def serve(*args, **kwargs):
    """
    Stub to replace Tornado based serve function.
    """
    raise RuntimeError('Cannot serve application in pyodide context.')

def init_doc() -> None:
    """
    Creates a Document mocking a server context for embedded Pyodide apps.
    """
    bk_settings.simple_ids.set_value(False)
    doc = Document()
    set_curdoc(doc)
    doc.hold()
    doc._session_context = lambda: MockSessionContext(document=doc)  # type: ignore
    state.curdoc = doc

async def show(obj: Any, target: str) -> None:
    """
    Renders the object into a DOM node specified by the target.

    Parameters
    ----------
    obj: Viewable
        Object to render into the DOM node
    target: str
        Target ID of the DOM node to render the object into.
    """
    from js import console
    console.log('panel.io.pyodide.show is deprecated in favor of panel.io.pyodide.write')
    await write(target, obj)

async def write(target: str, obj: Any) -> None:
    """
    Renders the object into a DOM node specified by the target.

    Parameters
    ----------
    target: str
        Target ID of the DOM node to render the object into.
    obj: Viewable
        Object to render into the DOM node
    """
    from ..pane import panel as as_panel

    obj = as_panel(obj)
    pydoc, model_json = _model_json(obj, target)
    views = await js.window.Bokeh.embed.embed_item(JSON.parse(model_json))
    jsdoc = list(views.roots)[0].model.document
    _link_docs(pydoc, jsdoc)
    pydoc.unhold()

def hide_loader() -> None:
    """
    Hides the global loading spinner.
    """
    from js import document

    body = document.getElementsByTagName('body')[0]
    body.classList.remove(LOADING_INDICATOR_CSS_CLASS, f'pn-{config.loading_spinner}')

def sync_location():
    """
    Syncs the JS window.location with the Panel Location component.
    """
    if not state.location:
        return
    try:
        loc_string = JSON.stringify(js.window.location)
    except Exception:
        return
    loc_data = json.loads(loc_string)
    with edit_readonly(state.location):
        state.location.param.update({
            k: v for k, v in loc_data.items() if k in state.location.param
        })

async def write_doc(doc: Document | None = None) -> tuple[str, str, str]:
    """
    Renders the contents of the Document into an existing template.
    Note that this assumes that the HTML file this function runs in
    was itself generated from the code being run. This function may
    be used in the main browser thread or from within a WebWorker.
    If invoked by a WebWorker the JSON return values can be sent
    to the main thread for rendering.

    Parameters
    ----------
    doc: Document
       The document to render to JSON.

    Returns
    -------
    docs_json: str
    render_items: str
    root_ids: str
    """
    pydoc: Document | None = doc or state.curdoc
    if not pydoc:
        raise ValueError('Cannot write contents of non-existent Document.')
    if pydoc in state._templates and pydoc not in state._templates[pydoc]._documents:
        template = state._templates[pydoc]
        template.server_doc(title=template.title, location=True, doc=pydoc)

    # Test whether we have access to DOM
    try:
        root_els = js.document.querySelectorAll('[data-root-id]')
        for el in root_els:
            el.innerHTML = ''
    except Exception:
        root_els = None
    docs_json, render_items, root_ids = _doc_json(pydoc, root_els)
    pydoc._session_context = None

    # If we have DOM access render and sync the document
    if root_els is not None:
        views = await js.window.Bokeh.embed.embed_items(JSON.parse(docs_json), JSON.parse(render_items))
        jsdoc = list(views[0].roots)[0].model.document
        _link_docs(pydoc, jsdoc)
        sync_location()
        hide_loader()
    return docs_json, render_items, root_ids

def pyrender(
    code: str,
    stdout_callback: Callable[[str], None] | None,
    stderr_callback: Callable[[str], None] | None,
    target: str
):
    """
    Executes Python code and returns a MIME representation of the
    return value.

    Parameters
    ----------
    code: str
        Python code to execute
    stdout_callback: Callable[[str, str], None] | None
        Callback executed with output written to stdout.
    stderr_callback: Callable[[str, str], None] | None
        Callback executed with output written to stderr.
    target: str
        The ID of the DOM node to write the output into.

    Returns
    -------
    Returns an JS Map containing the content, mime_type, stdout and stderr.
    """
    from ..pane import HoloViews, Interactive, panel as as_panel
    from ..param import ReactiveExpr
    from ..viewable import Viewable, Viewer
    PANES = (HoloViews, Interactive, ReactiveExpr)
    stdout = WriteCallbackStream(stdout_callback) if stdout_callback else None
    stderr = WriteCallbackStream(stderr_callback) if stderr_callback else None
    out = exec_with_return(code, stdout=stdout, stderr=stderr)
    ret = {}
    if isinstance(out, (Model, Viewable, Viewer)) or any(pane.applies(out) for pane in PANES):
        doc, model_json = _model_json(as_panel(out), target)
        state.cache[target] = doc
        ret['content'], ret['mime_type'] = model_json, 'application/bokeh'
    elif out is not None:
        ret['content'], ret['mime_type'] = format_mime(out)
    return pyodide.ffi.to_js(ret)
