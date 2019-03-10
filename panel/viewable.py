"""
Defines the Viewable and Reactive baseclasses allow all panel objects
to display themselves, communicate with a Python process and react in
response to changes to parameters and the underlying bokeh models.
"""
from __future__ import absolute_import, division, unicode_literals

import re
import signal
import uuid
from functools import partial

import param

from bokeh.document.document import Document as _Document, _combine_document_events
from bokeh.document.events import ModelChangedEvent
from bokeh.io import curdoc as _curdoc, export_png as _export_png, save as _save
from bokeh.resources import CDN as _CDN
from bokeh.models import CustomJS
from bokeh.server.server import Server
from pyviz_comms import JS_CALLBACK, JupyterCommManager

from .io import state
from .util import (render_mimebundle, add_to_doc, push, param_reprs,
                   _origin_url, show_server)


class Layoutable(param.Parameterized):

    aspect_ratio = param.Parameter(default=None, doc="""
        Describes the proportional relationship between component's
        width and height.  This works if any of component's dimensions
        are flexible in size. If set to a number, ``width / height =
        aspect_ratio`` relationship will be maintained.  Otherwise, if
        set to ``"auto"``, component's preferred width and height will
        be used to determine the aspect (if not set, no aspect will be
        preserved).
    """)

    background = param.Color(default=None, doc="""
        Background color of the component.""")

    css_classes = param.List(default=None, doc="""
        CSS classes to apply to the layout.""")

    width = param.Integer(default=None, bounds=(0, None), doc="""
        The width of the component (in pixels). This can be either
        fixed or preferred width, depending on width sizing policy.""")

    height = param.Integer(default=None, bounds=(0, None), doc="""
        The height of the component (in pixels).  This can be either
        fixed or preferred height, depending on height sizing policy.""")

    min_width = param.Integer(default=None, bounds=(0, None), doc="""
        Minimal width of the component (in pixels) if width is adjustable.""")

    min_height = param.Integer(default=None, bounds=(0, None), doc="""
        Minimal height of the component (in pixels) if height is adjustable.""")

    max_width = param.Integer(default=None, bounds=(0, None), doc="""
        Minimal width of the component (in pixels) if width is adjustable.""")

    max_height = param.Integer(default=None, bounds=(0, None), doc="""
        Minimal height of the component (in pixels) if height is adjustable.""")

    margin = param.Parameter(default=None, doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    width_policy = param.ObjectSelector(
        default="auto", objects=['auto', 'fixed', 'fit', 'min', 'max'], doc="""
        Describes how the component should maintain its width.

        * "auto"
          Use component's preferred sizing policy.
        * "fixed"
          Use exactly ``width`` pixels. Component will overflow if it
          can't fit in the available horizontal space.
        * "fit"
          Use component's preferred width (if set) and allow it to fit
          into the available horizontal space within the minimum and
          maximum width bounds (if set). Component's width neither
          will be aggressively minimized nor maximized.
        * "min"
          Use as little horizontal space as possible, not less than
          the minimum width (if set).  The starting point is the
          preferred width (if set). The width of the component may
          shrink or grow depending on the parent layout, aspect
          management and other factors.
        * "max"
          Use as much horizontal space as possible, not more than the
          maximum width (if set).  The starting point is the preferred
          width (if set). The width of the component may shrink or
          grow depending on the parent layout, aspect management and
          other factors.
    """)

    height_policy = param.ObjectSelector(
        default="auto", objects=['auto', 'fixed', 'fit', 'min', 'max'], doc="""
        Describes how the component should maintain its height.

        * "auto"
          Use component's preferred sizing policy.
        * "fixed"
          Use exactly ``width`` pixels. Component will overflow if it
          can't fit in the available horizontal space.
        * "fit"
          Use component's preferred width (if set) and allow it to fit
          into the available horizontal space within the minimum and
          maximum width bounds (if set). Component's width neither
          will be aggressively minimized nor maximized.
        * "min"
          Use as little horizontal space as possible, not less than
          the minimum width (if set).  The starting point is the
          preferred width (if set). The width of the component may
          shrink or grow depending on the parent layout, aspect
          management and other factors.
        * "max"
          Use as much horizontal space as possible, not more than the
          maximum width (if set).  The starting point is the preferred
          width (if set). The width of the component may shrink or
          grow depending on the parent layout, aspect management and
          other factors.
    """)

    sizing_mode = param.ObjectSelector(default=None, objects=[
        'fixed', 'stretch_width', 'stretch_height', 'stretch_both',
        'scale_width', 'scale_height', 'scale_both', None], doc="""

        How the component should size itself.

        This is a high-level setting for maintaining width and height
        of the component. To gain more fine grained control over
        sizing, use ``width_policy``, ``height_policy`` and
        ``aspect_ratio`` instead (those take precedence over
        ``sizing_mode``).

        * "fixed"
          Component is not responsive. It will retain its original
          width and height regardless of any subsequent browser window
          resize events.
        * "stretch_width"
          Component will responsively resize to stretch to the
          available width, without maintaining any aspect ratio. The
          height of the component depends on the type of the component
          and may be fixed or fit to component's contents.
        * "stretch_height"
          Component will responsively resize to stretch to the
          available height, without maintaining any aspect ratio. The
          width of the component depends on the type of the component
          and may be fixed or fit to component's contents.
        * "stretch_both"
          Component is completely responsive, independently in width
          and height, and will occupy all the available horizontal and
          vertical space, even if this changes the aspect ratio of the
          component.
        * "scale_width"
          Component will responsively resize to stretch to the
          available width, while maintaining the original or provided
          aspect ratio.
        * "scale_height"
          Component will responsively resize to stretch to the
          available height, while maintaining the original or provided
          aspect ratio.
        * "scale_both"
          Component will responsively resize to both the available
          width and height, while maintaining the original or provided
          aspect ratio.
    """)

    def __init__(self, **params):
        if (params.get('width', None) is not None and
            params.get('height', None) is not None and
            'sizing_mode' not in params):
            params['sizing_mode'] = 'fixed'
        super(Layoutable, self).__init__(**params)



class Viewable(Layoutable):
    """
    Viewable is the baseclass all objects in the panel library are
    built on. It defines the interface for declaring any object that
    displays itself by transforming the object(s) being wrapped into
    models that can be served using bokeh's layout engine. The class
    also defines various methods that allow Viewable objects to be
    displayed in the notebook and on bokeh server.
    """

    __abstract = True

    _preprocessing_hooks = []

    def __init__(self, **params):
        super(Viewable, self).__init__(**params)
        self._documents = {}
        self._models = {}
        self._found_links = set()

    def __repr__(self, depth=0):
        return '{cls}({params})'.format(cls=type(self).__name__,
                                        params=', '.join(param_reprs(self)))

    def __str__(self):
        return self.__repr__()

    def _get_model(self, doc, root=None, parent=None, comm=None):
        """
        Converts the objects being wrapped by the viewable into a
        bokeh model that can be composed in a bokeh layout.

        doc: bokeh.Document
          Bokeh document the bokeh model will be attached to.

        root: bokeh.Model
          The root layout the viewable will become part of.

        parent: bokeh.Model
          The parent layout the viewable will become part of.

        comm: pyviz_comms.Comm
          Optional pyviz_comms when working in notebook
        """

    def _get_root(self, doc, comm=None):
        """
        Returns the root model and applies pre-processing hooks

        Parameters
        ----------
        doc: bokeh.Document
          Bokeh document the bokeh model will be attached to.
        comm: pyviz_comms.Comm
          Optional pyviz_comms when working in notebook
        """
        root = self._get_model(doc, comm=comm)
        self._preprocess(root)
        ref = root.ref['id']
        state._views[ref] = (self, root, doc, comm)
        return root

    def _cleanup(self, model):
        """
        Clean up method which is called when a Viewable is destroyed.

        Parameters
        ----------
        model: bokeh.model.Model
          Bokeh model for the view being cleaned up
        """

    def _preprocess(self, root):
        """
        Applies preprocessing hooks to the model.
        """
        for hook in self._preprocessing_hooks:
            hook(self, root)

    def _repr_mimebundle_(self, include=None, exclude=None):
        state._comm_manager = JupyterCommManager
        doc = _Document()
        comm = state._comm_manager.get_server_comm()
        model = self._get_root(doc, comm)
        return render_mimebundle(model, doc, comm)

    def _server_destroy(self, session_context):
        """
        Server lifecycle hook triggered when session is destroyed.
        """
        doc = session_context._document
        self._cleanup(self._documents[doc])
        del self._documents[doc]

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

    def pprint(self):
        """
        Prints a compositional repr of the class.
        """
        print(self)

    def select(self, selector=None):
        """
        Iterates over the Viewable and any potential children in the
        applying the Selector.

        Parameters
        ----------
        selector: type or callable or None
            The selector allows selecting a subset of Viewables by
            declaring a type or callable function to filter by.

        Returns
        -------
        viewables: list(Viewable)
        """
        if (selector is None or
            (isinstance(selector, type) and isinstance(self, selector)) or
            (callable(selector) and not isinstance(selector, type) and selector(self))):
            return [self]
        else:
            return []

    def app(self, notebook_url="localhost:8888", port=0):
        """
        Displays a bokeh server app inline in the notebook.

        Parameters
        ----------
        notebook_url: str
            URL to the notebook server
        port: int (optional, default=0)
           Allows specifying a specific port
        """
        if callable(notebook_url):
            origin = notebook_url(None)
        else:
            origin = _origin_url(notebook_url)
        server_id = uuid.uuid4().hex
        server = self.get_server(port, origin, start=True, show=False,
                                 server_id=server_id)
        show_server(server, notebook_url, server_id)
        return server

    def get_server(self, port=0, websocket_origin=None, loop=None,
                   show=False, start=False, **kwargs):
        """
        Returns a Server instance with this panel attached as the root
        app.

        Parameters
        ----------
        port: int (optional, default=0)
           Allows specifying a specific port
        websocket_origin: str or list(str) (optional)
           A list of hosts that can connect to the websocket.

           This is typically required when embedding a server app in
           an external web site.

           If None, "localhost" is used.
        loop : tornado.ioloop.IOLoop (optional, default=IOLoop.current())
           The tornado IOLoop to run the Server on
        show : boolean (optional, default=False)
           Whether to open the server in a new browser tab on start
        start : boolean(optional, default=False)
           Whether to start the Server
        kwargs: dict
           Additional keyword arguments to pass to Server instance

        Returns
        -------
        server : bokeh.server.server.Server
           Bokeh Server instance running this panel
        """
        from tornado.ioloop import IOLoop
        opts = dict(kwargs)
        if loop:
            loop.make_current()
            opts['io_loop'] = loop
        else:
            opts['io_loop'] = IOLoop.current()

        if websocket_origin:
            if not isinstance(websocket_origin, list):
                websocket_origin = [websocket_origin]
            opts['allow_websocket_origin'] = websocket_origin

        server_id = kwargs.pop('server_id', None)
        server = Server({'/': partial(self._modify_doc, server_id)}, port=port, **opts)
        if server_id:
            state._servers[server_id] = (server, self, [])

        if show:
            def show_callback():
                server.show('/')
            server.io_loop.add_callback(show_callback)

        if start:
            server.start()
            try:
                server.io_loop.start()
            except RuntimeError:
                pass
        return server

    def save(self, filename, title=None, resources=None):
        """
        Saves Panel objects to file.

        Parameters
        ----------
        filename : string
           Filename to save the plot to
        title : string
           Optional title for the plot
        resources: bokeh resources
           One of the valid bokeh.resources (e.g. CDN or INLINE)
        """
        plot = self._get_root(_Document())
        if filename.endswith('png'):
            _export_png(plot, filename=filename)
            return
        if not filename.endswith('.html'):
            filename = filename + '.html'

        if title is None:
            title = 'Panel'
        if resources is None:
            resources = _CDN

        _save(plot, filename, title=title, resources=resources)

    def server_doc(self, doc=None, title=None):
        """
        Returns a serveable bokeh Document with the panel attached

        Parameters
        ----------
        doc : bokeh.Document (optional)
           The bokeh Document to attach the panel to as a root,
           defaults to bokeh.io.curdoc()
        title : str
           A string title to give the Document

        Returns
        -------
        doc : bokeh.Document
           The bokeh document the panel was attached to
        """
        doc = doc or _curdoc()
        if title is not None:
            doc.title = title
        model = self._get_root(doc)
        if hasattr(doc, 'on_session_destroyed'):
            doc.on_session_destroyed(self._server_destroy)
            self._documents[doc] = model
        add_to_doc(model, doc)
        return doc

    def servable(self):
        """
        Serves the object if in a `panel serve` context and returns
        the panel object to allow it to display itself in a notebook
        context.

        Returns
        -------
        The Panel object itself
        """
        if _curdoc().session_context:
            self.server_doc()
        return self

    def show(self, port=0, websocket_origin=None, threaded=False):
        """
        Starts a bokeh server and displays the Viewable in a new tab

        Parameters
        ----------
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
           Returns the bokeh server instance or the thread the server
           was launched on (if threaded=True)
        """
        if threaded:
            from tornado.ioloop import IOLoop
            from .util import StoppableThread
            loop = IOLoop()
            server = StoppableThread(
                target=self.get_server, io_loop=loop,
                args=(port, websocket_origin, loop, True, True))
            server.start()
        else:
            server = self.get_server(port, websocket_origin, show=True, start=True)
            def sig_exit(*args, **kwargs):
                server.io_loop.add_callback_from_signal(do_stop)

            def do_stop(*args, **kwargs):
                server.io_loop.stop()
            signal.signal(signal.SIGINT, sig_exit)

        return server



class Reactive(Viewable):
    """
    Reactive is a Viewable object that also supports syncing between
    the objects parameters and the underlying bokeh model either via
    the defined pyviz_comms.Comm type or when using bokeh server.

    In order to bi-directionally link parameters with bokeh model
    instances the _link_params and _link_props methods define
    callbacks triggered when either the parameter or bokeh property
    values change. Since there may not be a 1-to-1 mapping between
    parameter and the model property the _process_property_change and
    _process_param_change may be overridden to apply any necessary
    transformations.
    """

    # Timeout if a notebook comm message is swallowed
    _timeout = 20000

    # Timeout before the first event is processed
    _debounce = 50

    # Mapping from parameter name to bokeh model property name
    _rename = {}

    def __init__(self, **params):
        # temporary flag denotes panes created for temporary, internal
        # use which should be garbage collected once they have been used
        self._temporary = params.pop('_temporary', False)
        super(Reactive, self).__init__(**params)
        self._processing = False
        self._events = {}
        self._callbacks = []
        self._link_params()

    def _cleanup(self, root):
        super(Reactive, self)._cleanup(root)

        # Clean up comms
        model, _ = self._models.pop(root.ref['id'], (None, None))
        if model is None:
            return

        customjs = model.select({'type': CustomJS})
        pattern = "data\['comm_id'\] = \"(.*)\""
        for js in customjs:
            comm_ids = list(re.findall(pattern, js.code))
            if not comm_ids:
                continue
            comm_id = comm_ids[0]
            comm = state._comm_manager._comms.pop(comm_id, None)
            if comm:
                try:
                    comm.close()
                except:
                    pass

    def _update_model(self, events, msg, root, model, doc, comm=None):
        if comm:
            for attr, new in msg.items():
                setattr(model, attr, new)
                event = doc._held_events[-1] if doc._held_events else None
                if (event and event.model is model and event.attr == attr and
                    event.new is new):
                    continue
                # If change did not trigger event trigger it manually
                old = getattr(model, attr)
                serializable_new = model.lookup(attr).serializable_value(model)
                event = ModelChangedEvent(doc, model, attr, old, new, serializable_new)
                _combine_document_events(event, doc._held_events)
        else:
            model.update(**msg)

    def _synced_params(self):
        return list(self.param)

    def _link_params(self):
        def param_change(*events):
            msgs = []
            for event in events:
                msg = self._process_param_change({event.name: event.new})
                if msg:
                    msgs.append(msg)

            events = {event.name: event for event in events}
            msg = {k: v for msg in msgs for k, v in msg.items()}
            if not msg:
                return

            for ref, (model, parent) in self._models.items():
                if ref not in state._views:
                    continue
                viewable, root, doc, comm = state._views[ref]
                if comm or state.curdoc:
                    self._update_model(events, msg, root, model, doc, comm)
                    if comm:
                        push(doc, comm)
                else:
                    cb = partial(self._update_model, events, msg, root, model, doc, comm)
                    doc.add_next_tick_callback(cb)

        params = self._synced_params()
        if params:
            watcher = self.param.watch(param_change, params)
            self._callbacks.append(watcher)

    def _link_props(self, model, properties, doc, root, comm=None):
        if comm is None:
            for p in properties:
                model.on_change(p, partial(self._server_change, doc))
        else:
            client_comm = state._comm_manager.get_client_comm(on_msg=self._comm_change)
            for p in properties:
                customjs = self._get_customjs(p, client_comm, root.ref['id'])
                model.js_on_change(p, customjs)

    def _comm_change(self, msg):
        if not msg:
            return
        self._events.update(msg)
        self._change_event()

    def _server_change(self, doc, attr, old, new):
        self._events.update({attr: new})
        if not self._processing:
            self._processing = True
            doc.add_timeout_callback(partial(self._change_event, doc), self._debounce)

    def _change_event(self, doc=None):
        try:
            state.curdoc = doc
            events = self._events
            self._events = {}
            self.set_param(**self._process_property_change(events))
        except:
            raise
        else:
            if self._events:
                if doc:
                    doc.add_timeout_callback(partial(self._change_event, doc), self._debounce)
                else:
                    self._change_event()
        finally:
            self._processing = False
            state.curdoc = None

    def _get_customjs(self, change, client_comm, plot_id):
        """
        Returns a CustomJS callback that can be attached to send the
        model state across the notebook comms.
        """
        data_template = "data = {{{change}: cb_obj['{change}']}};"
        fetch_data = data_template.format(change=change)
        self_callback = JS_CALLBACK.format(comm_id=client_comm.id,
                                           timeout=self._timeout,
                                           debounce=self._debounce,
                                           plot_id=plot_id)
        js_callback = CustomJS(code='\n'.join([fetch_data,
                                               self_callback]))
        return js_callback

    #----------------------------------------------------------------
    # Developer API
    #----------------------------------------------------------------

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None}

    def _process_property_change(self, msg):
        """
        Transform bokeh model property changes into parameter updates.
        Should be overridden to provide appropriate mapping between
        parameter value and bokeh model change. By default uses the
        _rename class level attribute to map between parameter and
        property names.
        """
        inverted = {v: k for k, v in self._rename.items()}
        return {inverted.get(k, k): v for k, v in msg.items()}

    def _process_param_change(self, msg):
        """
        Transform parameter changes into bokeh model property updates.
        Should be overridden to provide appropriate mapping between
        parameter value and bokeh model change. By default uses the
        _rename class level attribute to map between parameter and
        property names.
        """
        properties = {self._rename.get(k, k): v for k, v in msg.items()
                      if self._rename.get(k, False) is not None}
        if 'width' in properties and self.sizing_mode is None:
            properties['min_width'] = properties['width']
        if 'height' in properties and self.sizing_mode is None:
            properties['min_height'] = properties['height']
        return properties

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def link(self, target, callbacks=None, **links):
        """
        Links the parameters on this object to attributes on another
        object in Python. Supports two modes, either specify a mapping
        between the source and target object parameters as keywords or
        provide a dictionary of callbacks which maps from the source
        parameter to a callback which is triggered when the parameter
        changes.

        Parameters
        ----------
        target: object
            The target object of the link.
        callbacks: dict
            Maps from a parameter in the source object to a callback.
        **links: dict
            Maps between parameters on this object to the parameters
            on the supplied object.
        """
        if links and callbacks:
            raise ValueError('Either supply a set of parameters to '
                             'link as keywords or a set of callbacks, '
                             'not both.')
        elif not links and not callbacks:
            raise ValueError('Declare parameters to link or a set of '
                             'callbacks, neither was defined.')

        _updating = []
        def link(*events):
            for event in events:
                if event.name in _updating: continue
                _updating.append(event.name)
                try:
                    if callbacks:
                        callbacks[event.name](target, event)
                    else:
                        setattr(target, links[event.name], event.new)
                except:
                    raise
                finally:
                    _updating.pop(_updating.index(event.name))
        params = list(callbacks) if callbacks else list(links)
        cb = self.param.watch(link, params)
        self._callbacks.append(cb)
        return cb

    def jslink(self, target, code=None, **links):
        """
        Links properties on the source object to those on the target
        object in JS code. Supports two modes, either specify a
        mapping between the source and target model properties as
        keywords or provide a dictionary of JS code snippets which
        maps from the source parameter to a JS code snippet which is
        executed when the property changes.

        Parameters
        ----------
        target: HoloViews object or bokeh Model or panel Viewable
            The target to link the value to.
        code: dict
            Custom code which will be executed when the widget value
            changes.
        **links: dict
            A mapping between properties on the source model and the
            target model property to link it to.

        Returns
        -------
        link: GenericLink
            The GenericLink which can be used unlink the widget and
            the target model.
        """
        if links and code:
            raise ValueError('Either supply a set of properties to '
                             'link as keywords or a set of JS code '
                             'callbacks, not both.')
        elif not links and not code:
            raise ValueError('Declare parameters to link or a set of '
                             'callbacks, neither was defined.')

        from .links import GenericLink
        if isinstance(target, Reactive):
            mapping = code or links
            for k, v in list(mapping.items()):
                mapping[k] = target._rename.get(v, v)
        return GenericLink(self, target, properties=links, code=code)
