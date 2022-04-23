import asyncio
import json
import pyodide
import os

from js import JSON

import param

from bokeh import __version__
from bokeh.document import Document
from bokeh.embed.util import standalone_docs_json_and_render_items
from bokeh.protocol.messages.patch_doc import process_document_events

from . import resources

resources.RESOURCE_MODE = 'CDN'
os.environ['BOKEH_RESOURCES'] = 'cdn'


def async_execute(func):
    event_loop = asyncio.get_running_loop()
    if event_loop.is_running():
        event_loop.call_soon(func)
    else:
        event_loop.run_until_complete(func())
    return

param.parameterized.async_executor = async_execute


def serve(*args, **kwargs):
    """
    Stub to replace Tornado based serve function.
    """
    raise RuntimeError('Cannot serve application in pyodide context.')


def _doc_json(model, target):
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
    from js import Bokeh
    from ..pane import panel as as_panel

    obj = as_panel(obj)
    pydoc, model_json = _doc_json(obj, target)
    views = await Bokeh.embed.embed_item(JSON.parse(model_json))
    jsdoc = views[0].model.document
    _link_docs(pydoc, jsdoc)
