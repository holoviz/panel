"""
Defines the Viewable and Reactive baseclasses allow all panel objects
to display themselves, communicate with a Python process and react in
response to changes to parameters and the underlying bokeh models.
"""
from __future__ import absolute_import, division, unicode_literals

import re
import sys
import threading

from functools import partial

import param

from bokeh.document.document import Document as _Document, _combine_document_events
from bokeh.document.events import ModelChangedEvent
from bokeh.io import curdoc as _curdoc
from bokeh.models import CustomJS
from pyviz_comms import JupyterCommManager

from .callbacks import PeriodicCallback
from .config import config, panel_extension
from .io.embed import embed_state
from .io.model import add_to_doc
from .io.notebook import (get_comm_customjs, push, render_mimebundle,
                          render_model, show_embed, show_server)
from .io.save import save
from .io.state import state
from .io.server import StoppableThread, get_server
from .util import param_reprs


class Layoutable(param.Parameterized):

    align = param.ObjectSelector(default='start',
                                 objects=['start', 'end', 'center'], doc="""
        Whether the object should be aligned with the start, end or
        center of its container""")

    aspect_ratio = param.Parameter(default=None, doc="""
        Describes the proportional relationship between component's
        width and height.  This works if any of component's dimensions
        are flexible in size. If set to a number, ``width / height =
        aspect_ratio`` relationship will be maintained.  Otherwise, if
        set to ``"auto"``, component's preferred width and height will
        be used to determine the aspect (if not set, no aspect will be
        preserved).
    """)

    background = param.Parameter(default=None, doc="""
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

    margin = param.Parameter(default=5, doc="""
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

        Arguments
        ----------
        doc: bokeh.Document
          Bokeh document the bokeh model will be attached to.
        root: bokeh.Model
          The root layout the viewable will become part of.
        parent: bokeh.Model
          The parent layout the viewable will become part of.
        comm: pyviz_comms.Comm
          Optional pyviz_comms when working in notebook

        Returns
        -------
        model: bokeh.Model
        """
        raise NotImplementedError

    def _cleanup(self, model):
        """
        Clean up method which is called when a Viewable is destroyed.

        Arguments
        ---------
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
        loaded = panel_extension._loaded
        if not loaded and 'holoviews' in sys.modules:
            import holoviews as hv
            loaded = hv.extension._loaded
        if not loaded:
            self.param.warning('Displaying Panel objects in the notebook '
                               'requires the panel extension to be loaded. '
                               'Ensure you run pn.extension() before '
                               'displaying objects in the notebook.')
            return None

        state._comm_manager = JupyterCommManager
        doc = _Document()
        comm = state._comm_manager.get_server_comm()
        model = self.get_root(doc, comm)
        if config.embed:
            embed_state(self, model, doc,
                        json=config.embed_json,
                        save_path=config.embed_save_path,
                        load_path=config.embed_load_path)
            return render_model(model)
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

    def _get_server(self, port=0, websocket_origin=None, loop=None,
                   show=False, start=False, **kwargs):
        return get_server(self, port, websocket_origin, loop, show,
                          start, **kwargs)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def clone(self, **params):
        """
        Makes a copy of the object sharing the same parameters.

        Arguments
        ---------
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned Viewable object
        """
        return type(self)(**dict(self.param.get_param_values(), **params))

    def pprint(self):
        """
        Prints a compositional repr of the class.
        """
        print(self)

    def select(self, selector=None):
        """
        Iterates over the Viewable and any potential children in the
        applying the Selector.

        Arguments
        ---------
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

        Arguments
        ---------
        notebook_url: str
          URL to the notebook server
        port: int (optional, default=0)
          Allows specifying a specific port
        """
        return show_server(self, notebook_url, port)

    def embed(self, max_states=1000, max_opts=3, json=False,
              save_path='./', load_path=None):
        """
        Renders a static version of a panel in a notebook by evaluating
        the set of states defined by the widgets in the model. Note
        this will only work well for simple apps with a relatively
        small state space.

        Arguments
        ---------
        max_states: int
          The maximum number of states to embed
        max_opts: int
          The maximum number of states for a single widget
        json: boolean (default=True)
          Whether to export the data to json files
        save_path: str (default='./')
          The path to save json files to
        load_path: str (default=None)
          The path or URL the json files will be loaded from.
        """
        show_embed(self, max_states, max_opts, json, save_path, load_path)

    def get_root(self, doc=None, comm=None):
        """
        Returns the root model and applies pre-processing hooks

        Arguments
        ---------
        doc: bokeh.Document
          Bokeh document the bokeh model will be attached to.
        comm: pyviz_comms.Comm
          Optional pyviz_comms when working in notebook

        Returns
        -------
        Returns the bokeh model corresponding to this panel object
        """
        doc = doc or _curdoc()
        root = self._get_model(doc, comm=comm)
        self._preprocess(root)
        ref = root.ref['id']
        state._views[ref] = (self, root, doc, comm)
        return root

    def save(self, filename, title=None, resources=None, template=None,
             template_variables={}, embed=False, max_states=1000,
             max_opts=3, embed_json=False, save_path='./', load_path=None):
        """
        Saves Panel objects to file.

        Arguments
        ---------
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
        return save(self, filename, title, resources, template,
                    template_variables, embed, max_states, max_opts,
                    embed_json, save_path, load_path)

    def server_doc(self, doc=None, title=None):
        """
        Returns a serveable bokeh Document with the panel attached

        Arguments
        ---------
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
        model = self.get_root(doc)
        if hasattr(doc, 'on_session_destroyed'):
            doc.on_session_destroyed(self._server_destroy)
            self._documents[doc] = model
        add_to_doc(model, doc)
        return doc

    def servable(self, title=None):
        """
        Serves the object if in a `panel serve` context and returns
        the panel object to allow it to display itself in a notebook
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
        Starts a bokeh server and displays the Viewable in a new tab

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
          Returns the bokeh server instance or the thread the server
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
        super(Reactive, self).__init__(**params)
        self._processing = False
        self._events = {}
        self._changing = {}
        self._callbacks = []
        self._link_params()

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    def _update_model(self, events, msg, root, model, doc, comm=None):
        if comm:
            filtered = {}
            for k, v in msg.items():
                try:
                    change = (k not in self._changing or
                              self._changing[k] != v or
                              self._changing['id'] != model.ref['id'])
                except:
                    change = True
                if change:
                    filtered[k] = v
            for attr, new in filtered.items():
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
                if comm or state._unblocked(doc):
                    self._update_model(events, msg, root, model, doc, comm)
                    if comm and 'embedded' not in root.tags:
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
        elif config.embed:
            pass
        else:
            client_comm = state._comm_manager.get_client_comm(on_msg=self._comm_change)
            for p in properties:
                customjs = self._get_customjs(p, client_comm, root.ref['id'])
                model.js_on_change(p, customjs)

    def _comm_change(self, msg):
        if not msg:
            return
        self._changing.update(msg)
        msg.pop('id', None)
        self._events.update(msg)
        try:
            self._change_event()
        finally:
            self._changing = {}

    def _server_change(self, doc, attr, old, new):
        self._events.update({attr: new})
        if not self._processing:
            self._processing = True
            doc.add_timeout_callback(partial(self._change_event, doc), self._debounce)

    def _change_event(self, doc=None):
        try:
            state.curdoc = doc
            thread = threading.current_thread()
            thread_id = thread.ident if thread else None
            state._thread_id = thread_id
            events = self._events
            self._events = {}
            self.set_param(**self._process_property_change(events))
        finally:
            self._processing = False
            state.curdoc = None
            state._thread_id = None

    def _get_customjs(self, change, client_comm, plot_id):
        """
        Returns a CustomJS callback that can be attached to send the
        model state across the notebook comms.
        """
        return get_comm_customjs(change, client_comm, plot_id,
                                 self._timeout, self._debounce)

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None}

    def _synced_params(self):
        return list(self.param)

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

        Arguments
        ---------
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

    def add_periodic_callback(self, callback, period=500, count=None,
                              timeout=None, start=True):
        """
        Schedules a periodic callback to be run at an interval set by
        the period. Returns a PeriodicCallback object with the option
        to stop and start the callback.

        Arguments
        ---------
        callback: callable
          Callable function to be executed at periodic interval.
        period: int
          Interval in milliseconds at which callback will be executed.
        count: int
          Maximum number of times callback will be invoked.
        timeout: int
          Timeout in seconds when the callback should be stopped.
        start: boolean (default=True)
          Whether to start callback immediately.

        Returns
        -------
        Return a PeriodicCallback object with start and stop methods.
        """
        cb = PeriodicCallback(callback=callback, period=period,
                              count=count, timeout=timeout)
        if start:
            cb.start()
        return cb

    def jslink(self, target, code=None, **links):
        """
        Links properties on the source object to those on the target
        object in JS code. Supports two modes, either specify a
        mapping between the source and target model properties as
        keywords or provide a dictionary of JS code snippets which
        maps from the source parameter to a JS code snippet which is
        executed when the property changes.

        Arguments
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
