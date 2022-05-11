import asyncio
import json
import pyodide
import os

from js import JSON
from typing import Optional

import param

from bokeh import __version__
from bokeh.document import Document
from bokeh.io.doc import set_curdoc
from bokeh.embed.util import standalone_docs_json_and_render_items
from bokeh.protocol.messages.patch_doc import process_document_events

from ..config import config
from . import resources
from .document import MockSessionContext
from .state import state

resources.RESOURCE_MODE = 'CDN'
os.environ['BOKEH_RESOURCES'] = 'cdn'


#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

def async_execute(func):
    event_loop = asyncio.get_running_loop()
    if event_loop.is_running():
        asyncio.create_task(func())
    else:
        event_loop.run_until_complete(func())
    return

param.parameterized.async_executor = async_execute

def _model_json(model, target):
    doc = Document()
    model.server_doc(doc=doc)
    model = doc.roots[0]
    docs_json, _ = standalone_docs_json_and_render_items(
        [model], suppress_callback_warning=True
    )

    doc_json = list(docs_json.values())[0]
    root_id = doc_json['roots']['root_ids'][0]

    return doc, json.dumps(dict(
        target_id = target,
        root_id   = root_id,
        doc       = doc_json,
        version   = __version__,
    ))

def _doc_json(doc):
    from js import document
    docs_json, render_items = standalone_docs_json_and_render_items(
        doc.roots, suppress_callback_warning=True
    )
    render_items = [item.to_json() for item in render_items]
    root_ids = [m.id for m in doc.roots]
    root_els = document.getElementsByClassName('bk-root')
    for el in root_els:
        el.innerHTML = ''
    root_data = sorted([(int(el.getAttribute('data-root-id')), el.id) for el in root_els])
    render_items[0].update({
        'roots': {model_id: elid for (_, elid), model_id in zip(root_data, root_ids)},
        'root_ids': root_ids
    })

    return json.dumps(docs_json), json.dumps(render_items)

def _link_docs(pydoc, jsdoc):
    def jssync(event):
        if (getattr(event, 'setter_id', None) is not None):
            return
        events = [event]
        json_patch = jsdoc.create_json_patch_string(pyodide.to_js(events))
        pydoc.apply_json_patch(json.loads(json_patch))

    jsdoc.on_change(pyodide.create_proxy(jssync), pyodide.to_js(False))

    def pysync(event):
        json_patch, buffers = process_document_events([event], use_buffers=True)
        buffer_map = {}
        for (ref, buffer) in buffers:
            buffer_map[ref['id']] = pyodide.to_js(buffer).buffer
        jsdoc.apply_json_patch(JSON.parse(json_patch), pyodide.to_js(buffer_map), setter_id='js')

    pydoc.on_change(pysync)

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def serve(*args, **kwargs):
    """
    Stub to replace Tornado based serve function.
    """
    raise RuntimeError('Cannot serve application in pyodide context.')

def init_doc() -> None:
    """
    Creates a Document mocking a server context for embedded Pyodide apps.
    """
    doc = Document()
    set_curdoc(doc)
    doc._session_context = lambda: MockSessionContext(document=doc)
    state._curdoc = doc

async def show(obj, target):
    """
    Renders the object into a DOM node specified by the target.

    Arguments
    ---------
    obj: Viewable
        Object to render into the DOM node
    target: str
        Target ID of the DOM node to render the object into.
    """
    from js import console
    console.log('panel.io.pyodide.show is deprecated in favor of panel.io.pyodide.write')
    await write(target, obj)

async def write(target, obj):
    """
    Renders the object into a DOM node specified by the target.

    Arguments
    ---------
    target: str
        Target ID of the DOM node to render the object into.
    obj: Viewable
        Object to render into the DOM node
    """

    from js import Bokeh
    from ..pane import panel as as_panel

    obj = as_panel(obj)
    pydoc, model_json = _model_json(obj, target)
    views = await Bokeh.embed.embed_item(JSON.parse(model_json))
    jsdoc = views[0].model.document
    _link_docs(pydoc, jsdoc)

async def write_doc(doc: Optional['Document'] = None) -> None:
    """
    Renders the contents of the Document into an existing template.
    Note that this assumes that the HTML file this function runs in
    was itself generated from the code being run.

    Arguments
    ---------
    doc: Document
    """
    from js import Bokeh, document

    body = document.getElementsByTagName('body')[0]
    body.classList.remove("bk", "pn-loading", config.loading_spinner)

    doc = doc or state.curdoc
    docs_json, render_items = _doc_json(doc)
    views = await Bokeh.embed.embed_items(JSON.parse(docs_json), JSON.parse(render_items))
    jsdoc = views[0][0].model.document
    doc._session_context = None
    _link_docs(doc, jsdoc)
