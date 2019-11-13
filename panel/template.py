"""
Templates allow multiple Panel objects to be embedded into custom HTML
documents.
"""
from __future__ import absolute_import, division, unicode_literals

import sys

import param

from bokeh.document.document import Document as _Document
from bokeh.io import curdoc as _curdoc
from bokeh.models import Row as _BkRow
from jinja2.environment import Template as _Template
from six import string_types
from pyviz_comms import JupyterCommManager as _JupyterCommManager

from .config import panel_extension
from .io.model import add_to_doc
from .io.notebook import render_template
from .io.server import StoppableThread, get_server
from .io.state import state
from .layout import Column
from .pane import panel as _panel, PaneBase, HTML, Str
from .widgets import Button

_server_info = (
    '<b>Running server:</b> <a target="_blank" href="https://localhost:{port}">'
    'https://localhost:{port}</a>')


class Template(param.Parameterized):
    """
    A Template is a high-level component to render multiple Panel
    objects into a single HTML document defined through a Jinja2
    template. The Template object is given a Jinja2 template and then
    allows populating this template by adding Panel objects, which are
    given unique names. These unique names may then be referenced in
    the template to insert the rendered Panel object at a specific
    location. For instance, given a Jinja2 template that defines roots
    A and B like this:

        <div> {{ embed(roots.A) }} </div>
        <div> {{ embed(roots.B) }} </div>

    We can then populate the template by adding panel 'A' and 'B' to
    the Template object:

        template.add_panel('A', pn.panel('A'))
        template.add_panel('B', pn.panel('B'))

    Once a template has been fully populated it can be rendered using
    the same API as other Panel objects. Note that all roots that have
    been declared using the {{ embed(roots.A) }} syntax in the Jinja2
    template must be defined when rendered.

    Since embedding complex CSS frameworks inside a notebook can have
    undesirable side-effects and a notebook does not afford the same
    amount of screen space a Template may given separate template
    and nb_template objects. This allows for different layouts when
    served as a standalone server and when used in the notebook.
    """

    def __init__(self, template=None, items=None, nb_template=None, **params):
        super(Template, self).__init__(**params)
        if isinstance(template, string_types):
            template = _Template(template)
        self.template = template
        if isinstance(nb_template, string_types):
            nb_template = _Template(nb_template)
        self.nb_template = nb_template or template
        self._render_items = {}
        self._server = None
        self._layout = self._build_layout()
        items = {} if items is None else items
        for name, item in items.items():
            self.add_panel(name, item)

    def _build_layout(self):
        str_repr = Str(repr(self))
        server_info = HTML('')
        button = Button(name='Launch server')
        def launch(event):
            if self._server:
                button.name = 'Launch server'
                server_info.object = ''
                self._server.stop()
                self._server = None
            else:
                button.name = 'Stop server'
                self._server = self._get_server(start=True, show=True)
                server_info.object = _server_info.format(port=self._server.port)
        button.param.watch(launch, 'clicks')
        return Column(str_repr, server_info, button)

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

    def __repr__(self):
        cls = type(self).__name__
        spacer = '\n    '
        objs = ['[%s] %s' % (name, obj[0].__repr__(1))
                for name, obj in self._render_items.items()
                if not name.startswith('_')]
        template = '{cls}{spacer}{objs}'
        return template.format(
            cls=cls, objs=('%s' % spacer).join(objs), spacer=spacer)

    def _init_doc(self, doc=None, comm=None, title=None, notebook=False):
        doc = doc or _curdoc()
        if title is not None:
            doc.title = title

        root = None
        preprocess_root = _BkRow()
        ref = preprocess_root.ref['id']
        for name, (obj, tags) in self._render_items.items():
            if root is None:
                root = model = obj.get_root(doc, comm)
            elif isinstance(obj, PaneBase):
                if obj._updates:
                    model = obj._get_model(doc, root, root, comm=comm)
                else:
                    model = obj.layout._get_model(doc, root, root, comm=comm)
            else:
                model = obj._get_model(doc, root, root, comm)
            obj._models[ref] = obj._models[root.ref['id']]
            preprocess_root.children.append(model)
            model.name = name
            model.tags = tags
            if hasattr(doc, 'on_session_destroyed'):
                doc.on_session_destroyed(obj._server_destroy)
                obj._documents[doc] = model
            add_to_doc(model, doc, hold=bool(comm))

        for (obj, _) in self._render_items.values():
            obj._preprocess(preprocess_root)

        if notebook:
            doc.template = self.nb_template
        else:
            doc.template = self.template
        return doc

    def _repr_mimebundle_(self, include=None, exclude=None):
        loaded = panel_extension._loaded
        if not loaded and 'holoviews' in sys.modules:
            import holoviews as hv
            loaded = hv.extension._loaded
        if not loaded:
            param.main.warning('Displaying Panel objects in the notebook '
                               'requires the panel extension to be loaded. '
                               'Ensure you run pn.extension() before '
                               'displaying objects in the notebook.')
            return None

        try:
            assert get_ipython().kernel is not None # noqa
            state._comm_manager = _JupyterCommManager
        except:
            pass
        doc = _Document()
        comm = state._comm_manager.get_server_comm()
        self._init_doc(doc, comm, notebook=True)
        return render_template(doc, comm)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def add_panel(self, name, panel, tags=[]):
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
        self._render_items[name] = (_panel(panel), tags)
        self._layout[0].object = repr(self)

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
        return self._init_doc(doc, title=title)

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
        if _curdoc().session_context:
            self.server_doc(title=title)
        return self

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
