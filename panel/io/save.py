"""
Defines utilities to save panel objects to files as HTML or PNG.
"""
from __future__ import absolute_import, division, unicode_literals

import io

from six import string_types

from bokeh.document.document import Document
from bokeh.embed import file_html
from bokeh.io.export import export_png, create_webdriver
from bokeh.resources import CDN
from bokeh.util.string import decode_utf8
from pyviz_comms import Comm

from ..config import config
from .embed import embed_state
from .model import add_to_doc
from .state import state


#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def save_png(model, filename):
    """
    Saves a bokeh model to png

    Arguments
    ---------
    model: bokeh.model.Model
      Model to save to png
    filename: str
      Filename to save to
    """
    if not state.webdriver:
        state.webdriver = create_webdriver()

    webdriver = state.webdriver
    export_png(model, filename, webdriver=webdriver)

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def save(panel, filename, title=None, resources=None, template=None,
         template_variables={}, embed=False, max_states=1000,
         max_opts=3, embed_json=False, save_path='./', load_path=None):
    """
    Saves Panel objects to file.

    Arguments
    ---------
    panel: Viewable
      The Panel Viewable to save to file
    filename: string or file-like object
      Filename to save the plot to
    title: string
      Optional title for the plot
    resources: bokeh resources
      One of the valid bokeh.resources (e.g. CDN or INLINE)
    embed: bool
      Whether the state space should be embedded in the saved file.
    max_states: int
      The maximum number of states to embed
    max_opts: int
      The maximum number of states for a single widget
    embed_json: boolean (default=True)
      Whether to export the data to json files
    save_path: str (default='./')
      The path to save json files to
    load_path: str (default=None)
      The path or URL the json files will be loaded from.
    """
    doc = Document()
    comm = Comm()
    with config.set(embed=embed):
        model = panel.get_root(doc, comm)
        if embed:
            embed_state(panel, model, doc, max_states, max_opts,
                        embed_json, save_path, load_path)
        else:
            add_to_doc(model, doc, True)

    if isinstance(filename, string_types):
        if filename.endswith('png'):
            save_png(model, filename=filename)
            return
        if not filename.endswith('.html'):
            filename = filename + '.html'

    kwargs = {}
    if title is None:
        title = 'Panel'
    if resources is None:
        resources = CDN
    if template:
        kwargs['template'] = template

    html = file_html(doc, resources, title, **kwargs)
    if hasattr(filename, 'write'):
        filename.write(decode_utf8(html))
        return
    with io.open(filename, mode="w", encoding="utf-8") as f:
        f.write(decode_utf8(html))
