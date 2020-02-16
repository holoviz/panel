"""
Defines utilities to save panel objects to files as HTML or PNG.
"""
from __future__ import absolute_import, division, unicode_literals

import io

from contextlib import contextmanager
from six import string_types

import param

from bokeh.document.document import Document
from bokeh.embed import file_html
from bokeh.io.export import export_png, create_webdriver
from bokeh.models import Div
from bokeh.resources import CDN
from bokeh.util.string import decode_utf8
from pyviz_comms import Comm

from ..config import config
from ..models import HTML
from .embed import embed_state
from .model import add_to_doc
from .state import state


#---------------------------------------------------------------------
# Private API
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


@contextmanager
def swap_html_model():
    """
    Temporary fix to swap HTML model for Div model during png export
    to avoid issues with DOMParser compatibility in PhantomJS.

    Can be removed when switching to chromedriver.
    """

    from ..viewable import Viewable

    state._html_escape = False
    swapped = []
    for viewable in param.concrete_descendents(Viewable).values():
        model = getattr(viewable, '_bokeh_model', None)
        try:
            swap_model = issubclass(model, HTML)
            assert swap_model
        except Exception:
            continue
        else:
            viewable._bokeh_model = Div
            swapped.append(viewable)
    try:
        yield
    finally:
        state._html_escape = True
        for viewable in swapped:
            viewable._bokeh_model = HTML

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def save(panel, filename, title=None, resources=None, template=None,
         template_variables=None, embed=False, max_states=1000,
         max_opts=3, embed_json=False, json_prefix='', save_path='./',
         load_path=None, progress=True):
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
    template:
      template file, as used by bokeh.file_html. If None will use bokeh defaults
    template_variables:
      template_variables file dict, as used by bokeh.file_html
    embed: bool
      Whether the state space should be embedded in the saved file.
    max_states: int
      The maximum number of states to embed
    max_opts: int
      The maximum number of states for a single widget
    embed_json: boolean (default=True)
      Whether to export the data to json files
    json_prefix: str (default='')
      Prefix for the randomly json directory
    save_path: str (default='./')
      The path to save json files to
    load_path: str (default=None)
      The path or URL the json files will be loaded from.
    progress: boolean (default=True)
      Whether to report progress
    """
    from ..pane import PaneBase

    if isinstance(panel, PaneBase) and len(panel.layout) > 1:
        panel = panel.layout

    as_png = isinstance(filename, string_types) and filename.endswith('png')

    doc = Document()
    comm = Comm()
    with config.set(embed=embed):
        with swap_html_model():
            model = panel.get_root(doc, comm)
        if embed:
            embed_state(
                panel, model, doc, max_states, max_opts, embed_json,
                json_prefix, save_path, load_path, progress
            )
        else:
            add_to_doc(model, doc, True)

    if as_png:
        save_png(model, filename=filename)
        return
    elif isinstance(filename, string_types) and not filename.endswith('.html'):
        filename = filename + '.html'

    kwargs = {}
    if title is None:
        title = 'Panel'
    if resources is None:
        resources = CDN
    if template:
        kwargs['template'] = template
    if template_variables:
        kwargs['template_variables'] = template_variables

    html = file_html(doc, resources, title, **kwargs)
    if hasattr(filename, 'write'):
        html = decode_utf8(html)
        if isinstance(filename, io.BytesIO):
            html = html.encode('utf-8')
        filename.write(html)
        return
    with io.open(filename, mode="w", encoding="utf-8") as f:
        f.write(decode_utf8(html))
