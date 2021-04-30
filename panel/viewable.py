"""
Defines the baseclasses that make a component render to a bokeh model
and become viewable including:

* Layoutable: Defines parameters concerned with layout and style
* ServableMixin: Mixin class that defines methods to serve object on server
* Renderable: Defines methods to render a component as a bokeh model
* Viewable: Defines methods to view the component in the
  notebook, on the server or in static exports
"""
import datetime as dt
import logging
import sys
import traceback
import uuid

from functools import partial

import param

from bokeh.document.document import Document as _Document
from bokeh.io import curdoc as _curdoc
from pyviz_comms import JupyterCommManager

from .config import config, panel_extension
from .io.embed import embed_state
from .io.loading import start_loading_spinner, stop_loading_spinner
from .io.model import add_to_doc, patch_cds_msg
from .io.notebook import (
    ipywidget, render_mimebundle, render_model, show_embed, show_server
)
from .io.save import save
from .io.state import state
from .io.server import init_doc, serve
from .util import escape, param_reprs


class Layoutable(param.Parameterized):
    """
    Layoutable defines shared style and layout related parameters
    for all Panel components with a visual representation.
    """

    align = param.ClassSelector(default='start',
                                class_=(str, tuple), doc="""
        Whether the object should be aligned with the start, end or
        center of its container. If set as a tuple it will declare
        (vertical, horizontal) alignment.""")

    aspect_ratio = param.Parameter(default=None, doc="""
        Describes the proportional relationship between component's
        width and height.  This works if any of component's dimensions
        are flexible in size. If set to a number, ``width / height =
        aspect_ratio`` relationship will be maintained.  Otherwise, if
        set to ``"auto"``, component's preferred width and height will
        be used to determine the aspect (if not set, no aspect will be
        preserved).""")

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

        ``"auto"``
            Use component's preferred sizing policy.

        ``"fixed"``
            Use exactly ``width`` pixels. Component will overflow if
            it can't fit in the available horizontal space.

        ``"fit"``
            Use component's preferred width (if set) and allow it to
            fit into the available horizontal space within the minimum
            and maximum width bounds (if set). Component's width
            neither will be aggressively minimized nor maximized.

        ``"min"``
            Use as little horizontal space as possible, not less than
            the minimum width (if set).  The starting point is the
            preferred width (if set). The width of the component may
            shrink or grow depending on the parent layout, aspect
            management and other factors.

        ``"max"``
            Use as much horizontal space as possible, not more than
            the maximum width (if set).  The starting point is the
            preferred width (if set). The width of the component may
            shrink or grow depending on the parent layout, aspect
            management and other factors.
    """)

    height_policy = param.ObjectSelector(
        default="auto", objects=['auto', 'fixed', 'fit', 'min', 'max'], doc="""
        Describes how the component should maintain its height.

        ``"auto"``
            Use component's preferred sizing policy.

        ``"fixed"``
            Use exactly ``height`` pixels. Component will overflow if
            it can't fit in the available vertical space.

        ``"fit"``
            Use component's preferred height (if set) and allow to fit
            into the available vertical space within the minimum and
            maximum height bounds (if set). Component's height neither
            will be aggressively minimized nor maximized.

        ``"min"``
            Use as little vertical space as possible, not less than
            the minimum height (if set).  The starting point is the
            preferred height (if set). The height of the component may
            shrink or grow depending on the parent layout, aspect
            management and other factors.

        ``"max"``
            Use as much vertical space as possible, not more than the
            maximum height (if set).  The starting point is the
            preferred height (if set). The height of the component may
            shrink or grow depending on the parent layout, aspect
            management and other factors.
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

        ``"fixed"``
            Component is not responsive. It will retain its original
            width and height regardless of any subsequent browser
            window resize events.

        ``"stretch_width"``
            Component will responsively resize to stretch to the
            available width, without maintaining any aspect ratio. The
            height of the component depends on the type of the
            component and may be fixed or fit to component's contents.

        ``"stretch_height"``
            Component will responsively resize to stretch to the
            available height, without maintaining any aspect
            ratio. The width of the component depends on the type of
            the component and may be fixed or fit to component's
            contents.

        ``"stretch_both"``
            Component is completely responsive, independently in width
            and height, and will occupy all the available horizontal
            and vertical space, even if this changes the aspect ratio
            of the component.

        ``"scale_width"``
            Component will responsively resize to stretch to the
            available width, while maintaining the original or
            provided aspect ratio.

        ``"scale_height"``
            Component will responsively resize to stretch to the
            available height, while maintaining the original or
            provided aspect ratio.

        ``"scale_both"``
            Component will responsively resize to both the available
            width and height, while maintaining the original or
            provided aspect ratio.
    """)

    __abstract = True

    def __init__(self, **params):
        if (params.get('width', None) is not None and
            params.get('height', None) is not None and
            params.get('width_policy') is None and
            params.get('height_policy') is None and
            'sizing_mode' not in params):
            params['sizing_mode'] = 'fixed'
        elif (not (self.param.sizing_mode.constant or self.param.sizing_mode.readonly) and
              type(self).sizing_mode is None):
            params['sizing_mode'] = params.get('sizing_mode', config.sizing_mode)
        super().__init__(**params)


class ServableMixin(object):
    """
    Mixin to define methods shared by objects which can served.
    """

    def _modify_doc(self, server_id, title, doc, location):
        """
        Callback to handle FunctionHandler document creation.
        """
        if server_id:
            state._servers[server_id][2].append(doc)
        return self.server_doc(doc, title, location)

    def _add_location(self, doc, location, root=None):
        from .io.location import Location
        if isinstance(location, Location):
            loc = location
        elif doc in state._locations:
            loc = state._locations[doc]
        else:
            loc = Location()
        state._locations[doc] = loc
        if root is None:
            loc_model = loc._get_root(doc)
        else:
            loc_model = loc._get_model(doc, root)
        loc_model.name = 'location'
        doc.add_root(loc_model)
        return loc

    def _on_msg(self, ref, manager, msg):
        """
        Handles Protocol messages arriving from the client comm.
        """
        root, doc, comm = state._views[ref][1:]
        patch_cds_msg(root, msg)
        held = doc._hold
        patch = manager.assemble(msg)
        doc.hold()
        patch.apply_to_document(doc, comm.id)
        doc.unhold()
        if held:
            doc.hold(held)

    def _on_error(self, ref, error):
        if ref not in state._handles or config.console_output in [None, 'disable']:
            return
        handle, accumulator = state._handles[ref]
        formatted = '\n<pre>'+escape(traceback.format_exc())+'</pre>\n'
        if config.console_output == 'accumulate':
            accumulator.append(formatted)
        elif config.console_output == 'replace':
            accumulator[:] = [formatted]
        if accumulator:
            handle.update({'text/html': '\n'.join(accumulator)}, raw=True)

    def _on_stdout(self, ref, stdout):
        if ref not in state._handles or config.console_output is [None, 'disable']:
            return
        handle, accumulator = state._handles[ref]
        formatted = ["%s</br>" % o for o in stdout]
        if config.console_output == 'accumulate':
            accumulator.extend(formatted)
        elif config.console_output == 'replace':
            accumulator[:] = formatted
        if accumulator:
            handle.update({'text/html': '\n'.join(accumulator)}, raw=True)

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def servable(self, title=None, location=True, area='main'):
        """
        Serves the object if in a `panel serve` context and returns
        the Panel object to allow it to display itself in a notebook
        context.
        Arguments
        ---------
        title : str
          A string title to give the Document (if served as an app)
        location : boolean or panel.io.location.Location
          Whether to create a Location component to observe and
          set the URL location.
        area: str
          The area of a template to add the component too. Only has an
          effect if pn.config.template has been set.

        Returns
        -------
        The Panel object itself
        """
        if _curdoc().session_context:
            logger = logging.getLogger('bokeh')
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(logging.WARN)
            if config.template:
                if state.template:
                    template = state.template
                    if template.title is None:
                        template.title  = title
                else:
                    params = {'title': title} if title else {}
                    state.template = template = config.template(**params)
                if area == 'main':
                    template.main.append(self)
                elif area == 'sidebar':
                    template.sidebar.append(self)
                elif area == 'modal':
                    template.modal.append(self)
                elif area == 'header':
                    template.header.append(self)
                print(state.curdoc)
            else:
                self.server_doc(title=title, location=location)
        return self

    def show(self, title=None, port=0, address=None, websocket_origin=None,
             threaded=False, verbose=True, open=True, location=True, **kwargs):
        """
        Starts a Bokeh server and displays the Viewable in a new tab.

        Arguments
        ---------
        title : str
          A string title to give the Document (if served as an app)
        port: int (optional, default=0)
          Allows specifying a specific port
        address : str
          The address the server should listen on for HTTP requests.
        websocket_origin: str or list(str) (optional)
          A list of hosts that can connect to the websocket.
          This is typically required when embedding a server app in
          an external web site.
          If None, "localhost" is used.
        threaded: boolean (optional, default=False)
          Whether to launch the Server on a separate thread, allowing
          interactive use.
        verbose: boolean (optional, default=True)
          Whether to print the address and port
        open : boolean (optional, default=True)
          Whether to open the server in a new browser tab
        location : boolean or panel.io.location.Location
          Whether to create a Location component to observe and
          set the URL location.

        Returns
        -------
        server: bokeh.server.Server or threading.Thread
          Returns the Bokeh server instance or the thread the server
          was launched on (if threaded=True)
        """
        return serve(
            self, port=port, address=address, websocket_origin=websocket_origin,
            show=open, start=True, title=title, verbose=verbose,
            location=location, threaded=threaded, **kwargs
        )


class Renderable(param.Parameterized):
    """
    Baseclass for objects which can be rendered to a Bokeh model.

    It therefore declare APIs for initializing the models from
    parameter values.
    """

    __abstract = True

    def __init__(self, **params):
        super().__init__(**params)
        self._callbacks = []
        self._documents = {}
        self._models = {}
        self._comms = {}
        self._kernels = {}
        self._found_links = set()

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

    def _cleanup(self, root):
        """
        Clean up method which is called when a Viewable is destroyed.

        Arguments
        ---------
        root: bokeh.model.Model
          Bokeh model for the view being cleaned up
        """
        ref = root.ref['id']
        if ref in state._handles:
            del state._handles[ref]

    def _preprocess(self, root):
        """
        Applies preprocessing hooks to the model.
        """
        hooks = self._preprocessing_hooks+self._hooks
        for hook in hooks:
            hook(self, root)

    def _render_model(self, doc=None, comm=None):
        if doc is None:
            doc = _Document()
        if comm is None:
            comm = state._comm_manager.get_server_comm()
        model = self.get_root(doc, comm)

        if config.embed:
            embed_state(self, model, doc,
                        json=config.embed_json,
                        json_prefix=config.embed_json_prefix,
                        save_path=config.embed_save_path,
                        load_path=config.embed_load_path,
                        progress=False)
        else:
            add_to_doc(model, doc)
        return model

    def _init_params(self):
        return {k: v for k, v in self.param.get_param_values() if v is not None}

    def _server_destroy(self, session_context):
        """
        Server lifecycle hook triggered when session is destroyed.
        """
        session_id = session_context.id
        sessions = state.session_info['sessions']
        if session_id in sessions and sessions[session_id]['ended'] is None:
            session = sessions[session_id]
            if session['rendered'] is not None:
                state.session_info['live'] -= 1
            session['ended'] = dt.datetime.now().timestamp()
        doc = session_context._document
        root = self._documents[doc]
        ref = root.ref['id']
        self._cleanup(root)
        del self._documents[doc]
        if ref in state._views:
            del state._views[ref]
        if doc in state._locations:
            loc = state._locations[doc]
            loc._cleanup(root)
            del state._locations[doc]

    def get_root(self, doc=None, comm=None, preprocess=True):
        """
        Returns the root model and applies pre-processing hooks

        Arguments
        ---------
        doc: bokeh.Document
          Bokeh document the bokeh model will be attached to.
        comm: pyviz_comms.Comm
          Optional pyviz_comms when working in notebook
        preprocess: boolean (default=True)
          Whether to run preprocessing hooks

        Returns
        -------
        Returns the bokeh model corresponding to this panel object
        """
        doc = init_doc(doc)
        root = self._get_model(doc, comm=comm)
        if preprocess:
            self._preprocess(root)
        ref = root.ref['id']
        state._views[ref] = (self, root, doc, comm)
        return root


class Viewable(Renderable, Layoutable, ServableMixin):
    """
    Viewable is the baseclass all visual components in the panel
    library are built on. It defines the interface for declaring any
    object that displays itself by transforming the object(s) being
    wrapped into models that can be served using bokeh's layout
    engine. The class also defines various methods that allow Viewable
    objects to be displayed in the notebook and on bokeh server.
    """

    loading = param.Boolean(doc="""
        Whether or not the Viewable is loading. If True a loading spinner
        is shown on top of the Viewable.""")

    _preprocessing_hooks = []

    def __init__(self, **params):
        hooks = params.pop('hooks', [])
        super().__init__(**params)
        self._hooks = hooks
        self._update_loading()
        watcher = self.param.watch(self._update_loading, 'loading')
        self._callbacks.append(watcher)

    def _update_loading(self, *_):
        if self.loading:
            start_loading_spinner(self)
        else:
            stop_loading_spinner(self)

    def __repr__(self, depth=0):
        return '{cls}({params})'.format(cls=type(self).__name__,
                                        params=', '.join(param_reprs(self)))

    def __str__(self):
        return self.__repr__()

    def _repr_mimebundle_(self, include=None, exclude=None):
        loaded = panel_extension._loaded
        if not loaded and 'holoviews' in sys.modules:
            import holoviews as hv
            loaded = hv.extension._loaded


        if config.comms in ('vscode', 'ipywidgets'):
            widget = ipywidget(self)
            if hasattr(widget, '_repr_mimebundle_'):
                return widget._repr_mimebundle_(include, exclude)
            plaintext = repr(widget)
            if len(plaintext) > 110:
                plaintext = plaintext[:110] + '…'
            data = {
                'text/plain': plaintext,
            }
            if widget._view_name is not None:
                data['application/vnd.jupyter.widget-view+json'] = {
                    'version_major': 2,
                    'version_minor': 0,
                    'model_id': widget._model_id
                }
            if config.comms == 'vscode':
                from IPython.display import display
                display(data, raw=True)
                return {'text/html': '<div style="display: none"></div>'}, {}
            return data, {}

        if not loaded:
            self.param.warning('Displaying Panel objects in the notebook '
                               'requires the panel extension to be loaded. '
                               'Ensure you run pn.extension() before '
                               'displaying objects in the notebook.')
            return None

        if config.comms == 'colab':
            from .io.notebook import load_notebook
            load_notebook(config.inline)

        try:
            from IPython import get_ipython
            assert get_ipython().kernel is not None
            state._comm_manager = JupyterCommManager
        except Exception:
            pass

        if not state._views:
            # Initialize the global Location
            from .io.location import Location
            state._location = location = Location()
        else:
            location = None

        from IPython.display import display
        from .models.comm_manager import CommManager

        doc = _Document()
        comm = state._comm_manager.get_server_comm()
        model = self._render_model(doc, comm)
        ref = model.ref['id']
        manager = CommManager(comm_id=comm.id, plot_id=ref)
        client_comm = state._comm_manager.get_client_comm(
            on_msg=partial(self._on_msg, ref, manager),
            on_error=partial(self._on_error, ref),
            on_stdout=partial(self._on_stdout, ref)
        )
        self._comms[ref] = (comm, client_comm)
        manager.client_comm_id = client_comm.id

        if config.console_output != 'disable':
            handle = display(display_id=uuid.uuid4().hex)
            state._handles[ref] = (handle, [])

        if config.embed:
            return render_model(model)
        return render_mimebundle(model, doc, comm, manager, location)

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
        inherited = {p: v for p, v in self.param.get_param_values()
                     if not self.param[p].readonly}
        return type(self)(**dict(inherited, **params))

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

    def embed(self, max_states=1000, max_opts=3, json=False, json_prefix='',
              save_path='./', load_path=None, progress=False, states={}):
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
        json_prefix: str (default='')
          Prefix for JSON filename
        save_path: str (default='./')
          The path to save json files to
        load_path: str (default=None)
          The path or URL the json files will be loaded from.
        progress: boolean (default=False)
          Whether to report progress
        states: dict (default={})
          A dictionary specifying the widget values to embed for each widget
        """
        show_embed(
            self, max_states, max_opts, json, json_prefix, save_path,
            load_path, progress, states
        )

    def save(self, filename, title=None, resources=None, template=None,
             template_variables=None, embed=False, max_states=1000,
             max_opts=3, embed_json=False, json_prefix='', save_path='./',
             load_path=None, progress=True, embed_states={}, **kwargs):
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
        template:
           passed to underlying io.save
        template_variables:
           passed to underlying io.save
        embed: bool
           Whether the state space should be embedded in the saved file.
        max_states: int
           The maximum number of states to embed
        max_opts: int
           The maximum number of states for a single widget
        embed_json: boolean (default=True)
           Whether to export the data to json files
        json_prefix: str (default='')
           Prefix for the auto-generated json directory
        save_path: str (default='./')
           The path to save json files to
        load_path: str (default=None)
           The path or URL the json files will be loaded from.
        progress: boolean (default=True)
          Whether to report progress
        embed_states: dict (default={})
          A dictionary specifying the widget values to embed for each widget
        """
        return save(self, filename, title, resources, template,
                    template_variables, embed, max_states, max_opts,
                    embed_json, json_prefix, save_path, load_path,
                    progress, embed_states, **kwargs)

    def server_doc(self, doc=None, title=None, location=True):
        """
        Returns a serveable bokeh Document with the panel attached

        Arguments
        ---------
        doc : bokeh.Document (optional)
          The bokeh Document to attach the panel to as a root,
          defaults to bokeh.io.curdoc()
        title : str
          A string title to give the Document
        location : boolean or panel.io.location.Location
          Whether to create a Location component to observe and
          set the URL location.

        Returns
        -------
        doc : bokeh.Document
          The bokeh document the panel was attached to
        """
        doc = init_doc(doc)
        title = title or 'Panel Application'
        doc.title = title
        model = self.get_root(doc)
        if hasattr(doc, 'on_session_destroyed'):
            doc.on_session_destroyed(self._server_destroy)
            self._documents[doc] = model
        add_to_doc(model, doc)
        if location: self._add_location(doc, location, model)
        return doc


class Viewer(param.Parameterized):
    """
    A baseclass for custom components that behave like a Panel object.
    By implementing __panel__ method an instance of this class will
    behave like the returned Panel component when placed in a layout,
    render itself in a notebook and provide show and servable methods.
    """

    def __panel__(self):
        """
        Subclasses should return a Panel component to be rendered.
        """
        raise NotImplementedError

    def servable(self, title=None, location=True):
        return self.__panel__().servable(title, location)

    servable.__doc__ = ServableMixin.servable.__doc__

    def show(self, title=None, port=0, address=None, websocket_origin=None,
             threaded=False, verbose=True, open=True, location=True, **kwargs):
        return self.__panel__().show(
            title, port, address, websocket_origin, threaded,
            verbose, open, location, **kwargs
        )

    show.__doc__ = ServableMixin.show.__doc__

    def _repr_mimebundle_(self, include=None, exclude=None):
        return self.__panel__()._repr_mimebundle_(include, exclude)
