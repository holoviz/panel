"""
Defines utilities to save panel objects to files as HTML or PNG.
"""
from __future__ import absolute_import, division, unicode_literals

import io

from six import string_types

import bokeh

from bokeh.document.document import Document
from bokeh.embed import file_html
from bokeh.io.export import export_png
from bokeh.resources import CDN, INLINE
from pyviz_comms import Comm

from ..config import config
from .embed import embed_state
from .model import add_to_doc
from .state import state


#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

def save_png(model, filename, template=None, template_variables=None):
    """
    Saves a bokeh model to png

    Arguments
    ---------
    model: bokeh.model.Model
      Model to save to png
    filename: str
      Filename to save to
    template:
      template file, as used by bokeh.file_html. If None will use bokeh defaults
    template_variables:
      template_variables file dict, as used by bokeh.file_html
    """
    from bokeh.io.webdriver import webdriver_control
    if not state.webdriver:
        state.webdriver = webdriver_control.create()

    webdriver = state.webdriver

    try:
        if template:
            def get_layout_html(obj, resources, width, height):
                return file_html(
                    obj, resources, title="", template=template,
                    template_variables=template_variables,
                    suppress_callback_warning=True, _always_new=True
                )
            old_layout_fn = bokeh.io.export.get_layout_html
            bokeh.io.export.get_layout_html = get_layout_html
        export_png(model, filename=filename, webdriver=webdriver)
    except Exception:
        raise
    finally:
        if template:
            bokeh.io.export.get_layout_html = old_layout_fn


#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def save(panel, filename, title=None, resources=None, template=None,
         template_variables=None, embed=False, max_states=1000,
         max_opts=3, embed_json=False, json_prefix='', save_path='./',
         load_path=None, progress=True, embed_states={}):
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
    embed_states: dict (default={})
      A dictionary specifying the widget values to embed for each widget
    """
    from ..pane import PaneBase
    from ..template import Template

    if isinstance(panel, PaneBase) and len(panel.layout) > 1:
        panel = panel.layout

    as_png = isinstance(filename, string_types) and filename.endswith('png')

    if isinstance(panel, Document):
        doc = panel
    else:
        doc = Document()

    comm = Comm()
    with config.set(embed=embed):
        if isinstance(panel, Document):
            model = panel
        elif isinstance(panel, Template):
            panel._init_doc(doc, title=title)
            model = doc
        else:
            model = panel.get_root(doc, comm)
            if embed:
                embed_state(
                    panel, model, doc, max_states, max_opts, embed_json,
                    json_prefix, save_path, load_path, progress, embed_states
                )
            else:
                add_to_doc(model, doc, True)

    if as_png:
        return save_png(model, filename=filename, template=template,
                        template_variables=template_variables)
    elif isinstance(filename, string_types) and not filename.endswith('.html'):
        filename = filename + '.html'

    kwargs = {}
    if title is None:
        title = 'Panel'
    if resources is None:
        resources = CDN
    elif isinstance(resources, str):
        if resources.lower() == 'cdn':
            resources = CDN
        elif resources.lower() == 'inline':
            resources = INLINE
        else:
            raise ValueError("Resources %r not recognized, specify one "
                             "of 'CDN' or 'INLINE'." % resources)
        
    if template:
        kwargs['template'] = template
    if template_variables:
        kwargs['template_variables'] = template_variables

    html = file_html(doc, resources, title, **kwargs)
    if hasattr(filename, 'write'):
        if isinstance(filename, io.BytesIO):
            html = html.encode('utf-8')
        filename.write(html)
    else:
        with io.open(filename, mode="w", encoding="utf-8") as f:
            f.write(html)
