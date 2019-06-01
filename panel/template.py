"""
Templates allow multiple Panel objects to be embedded into custom HTML
documents.
"""
import os
import sys

import param

from bokeh.io import curdoc as _curdoc
from bokeh.document.document import Document as _Document
from jinja2 import Environment, Markup, FileSystemLoader
from jinja2.environment import Template as _Template
from pyviz_comms import JupyterCommManager
from six import string_types

from .io.model import add_to_doc
from .io.notebook import render_mimebundle, render_model
from .io.server import StoppableThread, get_server
from .io.state import state


def get_env():
    """
    Get the correct Jinja2 Environment, also for frozen scripts.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller uses _MEIPASS and only works with jinja2.FileSystemLoader
        templates_path = join(sys._MEIPASS, 'panel', '_templates')
    else:
        # Non-frozen Python and cx_Freeze can use __file__ directly
        templates_path = osjoin(os.dirname(__file__), '_templates')

    return Environment(loader=FileSystemLoader(templates_path))

_env = get_env()


class Template(object):
    """
    A Template is a high-level component to render multiple Panel
    objects into a single HTML document. The Template object should be
    given a string or Jinja2 Template object in the constructor and
    can then be populated with Panel objects. When adding panels to
    the Template a unique name must be provided, making it possible to
    refer to them uniquely in the template. For instance, two panels added like
    this:

        template.add_panel('A', pn.panel('A'))
        template.add_panel('B', pn.panel('B'))

    May then be referenced in the template using the `embed` macro:

        <div> {{ embed(roots.A) }} </div>
        <div> {{ embed(roots.B) }} </div>

    Once a template has been fully populated it can be rendered using
    the same API as other Panel objects.
    """

    def __init__(self, template=None, items=None):
        if isinstance(template, string_types):
            template = _Template(template)
        self.template = template
        self._render_items = {}
        items = {} if items is None else items
        for name, item in items.items():
            self.add_panel(name, item)

    def _get_server(self, port=0, websocket_origin=None, loop=None,
                   show=False, start=False, **kwargs):
        return get_server(self, port, websocket_origin, loop, show,
                          start, **kwargs)

    def _modify_doc(self, server_id, doc):
        """
        Callback to handle FunctionHandler document creation.
        """
        if server_id:
            state._servers[server_id][2].append(doc)
        return self.server_doc(doc)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------
    
    def add_panel(self, name, panel):
        """
        Add panels to the Template, which may then be referenced by
        the given name using the jinja2 embed macro.

        Arguments
        ---------
        name : str
          The name to refer to the panel by in the template
        panel : panel.Viewable
          A Panel component to embed in the template.
        """
        
        if name in self._render_items:
            raise ValueError('The name %s has already been used for '
                             'another panel. Ensure each panel '
                             'has a unique name by which it can be '
                             'referenced in the template.' % name)
        self._render_items[name] = panel

    def server_doc(self, doc=None, title=None):
        """
        Returns a servable bokeh Document with the panel attached

        Arguments
        ---------
        doc : bokeh.Document (optional)
          The Bokeh Document to attach the panel to as a root,
          defaults to bokeh.io.curdoc()
        title : str
          A string title to give the Document

        Returns
        -------
        doc : bokeh.Document
          The Bokeh document the panel was attached to
        """
        doc = doc or _curdoc()
        if title is not None:
            doc.title = title
        for name, obj in self._render_items:
            model = obj.get_root(doc)
            model.name = name
            if hasattr(doc, 'on_session_destroyed'):
                doc.on_session_destroyed(obj._server_destroy)
                obj._documents[doc] = model
            add_to_doc(model, doc)
        doc.template = self.template
        return doc

    def servable(self, title=None):
        """
        Serves the object if in a `panel serve` context and returns
        the Panel object to allow it to display itself in a notebook
        context.

        Arguments
        ---------
        title : str
          A string title to give the Document (if served as an app)

        Returns
        -------
        The Panel object itself
        """
        doc = self.server_doc(title=title)
        return doc

    def show(self, port=0, websocket_origin=None, threaded=False):
        """
        Starts a Bokeh server and displays the Viewable in a new tab

        Arguments
        ---------
        port: int (optional, default=0)
          Allows specifying a specific port
        websocket_origin: str or list(str) (optional)
          A list of hosts that can connect to the websocket.

          This is typically required when embedding a server app in
          an external web site.

          If None, "localhost" is used.
        threaded: boolean (optional, default=False)
          Whether to launch the Server on a separate thread, allowing
          interactive use.

        Returns
        -------
        server: bokeh.server.Server or threading.Thread
          Returns the Bokeh server instance or the thread the server
          was launched on (if threaded=True)
        """
        if threaded:
            from tornado.ioloop import IOLoop
            loop = IOLoop()
            server = StoppableThread(
                target=self._get_server, io_loop=loop,
                args=(port, websocket_origin, loop, True, True))
            server.start()
        else:
            server = self._get_server(port, websocket_origin, show=True, start=True)

        return server
