"""
Defines utilities to save panel objects to files as HTML or PNG.
"""
import io

from six import string_types

import bokeh

from bokeh.document.document import Document
from bokeh.embed.bundle import bundle_for_objs_and_resources
from bokeh.embed.elements import html_page_for_render_items
from bokeh.embed.util import OutputDocumentFor, standalone_docs_json_and_render_items
from bokeh.io.export import get_screenshot_as_png
from bokeh.model import Model
from bokeh.resources import CDN, INLINE, Resources as BkResources
from pyviz_comms import Comm

from ..config import config
from .embed import embed_state
from .model import add_to_doc
from .resources import BASE_TEMPLATE, DEFAULT_TITLE, Bundle, Resources, set_resource_mode
from .state import state

#---------------------------------------------------------------------
# Private API
#---------------------------------------------------------------------

_WAIT_SCRIPT = """
// add private window prop to check that render is complete
window._bokeh_render_complete = false;
function done() {
  setTimeout(() => { window._bokeh_render_complete = true; }, 500);
}

var doc = Bokeh.documents[0];

if (doc.is_idle)
  done();
else
  doc.idle.connect(done);
"""

bokeh.io.export._WAIT_SCRIPT = _WAIT_SCRIPT

def save_png(model, filename, resources=CDN, template=None, template_variables=None, timeout=5):
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
    timeout: int
      The maximum amount of time (in seconds) to wait for
    """
    from bokeh.io.webdriver import webdriver_control
    if not state.webdriver:
        state.webdriver = webdriver_control.create()

    webdriver = state.webdriver

    if template is None:
        template = r"""\
        {% block preamble %}
        <style>
        html, body {
        box-sizing: border-box;
            width: 100%;
            height: 100%;
            margin: 0;
            border: 0;
            padding: 0;
            overflow: hidden;
        }
        </style>
        {% endblock %}
        """

    try:
        def get_layout_html(obj, resources, width, height, **kwargs):
            resources = Resources.from_bokeh(resources)
            return file_html(
                obj, resources, title="", template=template,
                template_variables=template_variables or {},
                _always_new=True
            )
        old_layout_fn = bokeh.io.export.get_layout_html
        bokeh.io.export.get_layout_html = get_layout_html
        img = get_screenshot_as_png(model, driver=webdriver, timeout=timeout, resources=resources)

        if img.width == 0 or img.height == 0:
            raise ValueError("unable to save an empty image")

        img.save(filename)
    except Exception:
        raise
    finally:
        if template:
            bokeh.io.export.get_layout_html = old_layout_fn

def _title_from_models(models, title):
    if title is not None:
        return title

    for p in models:
        if isinstance(p, Document):
            return p.title

    for p in models:
        if p.document is not None:
            return p.document.title

    return DEFAULT_TITLE

def file_html(models, resources, title=None, template=BASE_TEMPLATE,
              template_variables={}, theme=None, _always_new=False):
    models_seq = []
    if isinstance(models, Model):
        models_seq = [models]
    elif isinstance(models, Document):
        models_seq = models.roots
    else:
        models_seq = models

    with OutputDocumentFor(models_seq, apply_theme=theme, always_new=_always_new):
        (docs_json, render_items) = standalone_docs_json_and_render_items(
            models_seq, suppress_callback_warning=True
        )
        title = _title_from_models(models_seq, title)
        bundle = bundle_for_objs_and_resources(None, resources)
        bundle = Bundle.from_bokeh(bundle)
        return html_page_for_render_items(
            bundle, docs_json, render_items, title=title, template=template,
            template_variables=template_variables
        )

#---------------------------------------------------------------------
# Public API
#---------------------------------------------------------------------

def save(panel, filename, title=None, resources=None, template=None,
         template_variables=None, embed=False, max_states=1000,
         max_opts=3, embed_json=False, json_prefix='', save_path='./',
         load_path=None, progress=True, embed_states={}, **kwargs):
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
    from ..template import BaseTemplate

    if isinstance(panel, PaneBase) and len(panel.layout) > 1:
        panel = panel.layout

    as_png = isinstance(filename, string_types) and filename.endswith('png')

    if isinstance(panel, Document):
        doc = panel
    else:
        doc = Document()
        
    if resources is None:
        resources = CDN
        mode = 'cdn'
    elif isinstance(resources, str):
        if resources.lower() == 'cdn':
            resources = CDN
            mode = 'cdn'
        elif resources.lower() == 'inline':
            resources = INLINE
            mode = 'inline'
        else:
            raise ValueError("Resources %r not recognized, specify one "
                             "of 'CDN' or 'INLINE'." % resources)
    elif isinstance(resources, BkResources):
        mode = resources.mode

    comm = Comm()
    with config.set(embed=embed):
        if isinstance(panel, Document):
            model = panel
        elif isinstance(panel, BaseTemplate):
            with set_resource_mode(mode):
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
        return save_png(
            model, resources=resources, filename=filename, template=template,
            template_variables=template_variables, **kwargs
        )
    elif isinstance(filename, string_types) and not filename.endswith('.html'):
        filename = filename + '.html'

    kwargs = {}
    if title is None:
        title = 'Panel'

    if template:
        kwargs['template'] = template
    if template_variables:
        kwargs['template_variables'] = template_variables

    resources = Resources.from_bokeh(resources)

    # Set resource mode
    with set_resource_mode(mode):
        html = file_html(doc, resources, title, **kwargs)
    if hasattr(filename, 'write'):
        if isinstance(filename, io.BytesIO):
            html = html.encode('utf-8')
        filename.write(html)
    else:
        with io.open(filename, mode="w", encoding="utf-8") as f:
            f.write(html)
