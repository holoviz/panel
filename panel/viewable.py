"""
Defines the baseclasses that make a component render to a bokeh model
and become viewable including:

* Layoutable: Defines parameters concerned with layout and style
* ServableMixin: Mixin class that defines methods to serve object on server
* Renderable: Defines methods to render a component as a bokeh model
* Viewable: Defines methods to view the component in the
  notebook, on the server or in static exports
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import threading
import traceback
import uuid

from functools import partial
from typing import (
    IO, TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Mapping, Optional,
)

import param  # type: ignore

from bokeh.core.serialization import DeserializationError
from bokeh.document import Document
from bokeh.resources import Resources
from jinja2 import Template
from pyviz_comms import Comm  # type: ignore

from ._param import Align, Aspect, Margin
from .config import config, panel_extension
from .io import serve
from .io.document import create_doc_if_none_exists, init_doc
from .io.embed import embed_state
from .io.loading import start_loading_spinner, stop_loading_spinner
from .io.model import add_to_doc, patch_cds_msg
from .io.notebook import (
    JupyterCommManagerBinary as JupyterCommManager, ipywidget, render_embed,
    render_mimebundle, render_model, show_server,
)
from .io.save import save
from .io.state import curdoc_locked, state
from .util import escape, param_reprs
from .util.warnings import deprecated

if TYPE_CHECKING:
    from bokeh.model import Model
    from bokeh.server.contexts import BokehSessionContext
    from bokeh.server.server import Server

    from .io.location import Location
    from .io.server import StoppableThread


class Layoutable(param.Parameterized):
    """
    Layoutable defines shared style and layout related parameters
    for all Panel components with a visual representation.
    """

    align = Align(default='start', doc="""
        Whether the object should be aligned with the start, end or
        center of its container. If set as a tuple it will declare
        (vertical, horizontal) alignment.""")

    aspect_ratio = Aspect(default=None, doc="""
        Describes the proportional relationship between component's
        width and height.  This works if any of component's dimensions
        are flexible in size. If set to a number, ``width / height =
        aspect_ratio`` relationship will be maintained.  Otherwise, if
        set to ``"auto"``, component's preferred width and height will
        be used to determine the aspect (if not set, no aspect will be
        preserved).""")

    background = param.Parameter(default=None, doc="""
        Background color of the component.""")

    css_classes = param.List(default=[], doc="""
        CSS classes to apply to the layout.""")

    design = param.ObjectSelector(default=None, objects=[], doc="""
        The design system to use to style components.""")

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

    margin = Margin(default=0, doc="""
        Allows to create additional space around the component. May
        be specified as a two-tuple of the form (vertical, horizontal)
        or a four-tuple (top, right, bottom, left).""")

    styles = param.Dict(default={}, doc="""
        Dictionary of CSS rules to apply to DOM node wrapping the
        component.""")

    stylesheets = param.List(default=[], doc="""
        List of stylesheets defined as URLs pointing to .css files
        or raw CSS defined as a string.""")

    tags = param.List(default=[], doc="""
        List of arbitrary tags to add to the component.
        Can be useful for templating or for storing metadata on
        the model.""")

    width = param.Integer(default=None, bounds=(0, None), doc="""
        The width of the component (in pixels). This can be either
        fixed or preferred width, depending on width sizing policy.""")

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

    visible = param.Boolean(default=True, doc="""
        Whether the component is visible. Setting visible to false will
        hide the component entirely.""")

    __abstract = True

    def __init__(self, **params):
        sizing_mode = params.get('sizing_mode')
        if (sizing_mode in ('stretch_width', 'scale_width', 'stretch_both', 'scale_both') and
            params.get('width') is not None):
            error = (
                f"Providing a width-responsive sizing_mode ({params['sizing_mode']!r}) "
                "and a fixed width is not supported. Converting fixed width to min_width. "
                "If you intended the component to be fully width-responsive remove the height"
                "setting, otherwise change it to min_height."
            )
            if config.layout_compatibility == 'warn':
                error += ' To error on the incorrect specification disable the config.layout_compatibility option.'
                self.param.warning(error)
            else:
                raise ValueError(error)
            params['min_width'] = params.pop('width')
        if (sizing_mode in ('stretch_height', 'scale_height', 'stretch_both', 'scale_both') and
            params.get('height') is not None):
            error = (
                f"Providing a height-responsive sizing_mode ({params['sizing_mode']!r}) "
                "and a fixed height is not supported. Converting fixed height to min_height. "
                "If you intended the component to be fully height-responsive remove the height "
                "setting, otherwise change it to min_height."
            )
            if config.layout_compatibility == 'warn':
                error += ' To error on the incorrect specification disable the config.layout_compatibility option.'
                self.param.warning(error)
            else:
                raise ValueError(error)
            params['min_height'] = params.pop('height')
        if (params.get('width') is not None and
            params.get('height') is not None and
            params.get('width_policy') is None and
            params.get('height_policy') is None and
            'sizing_mode' not in params):
            params['sizing_mode'] = 'fixed'
        elif (not (self.param.sizing_mode.constant or self.param.sizing_mode.readonly) and
              type(self).sizing_mode is None and 'sizing_mode' not in params):
            if config.sizing_mode == 'stretch_both':
                if params.get('height') is not None:
                    params['sizing_mode'] = 'stretch_width'
                elif params.get('width') is not None:
                    params['sizing_mode'] = 'stretch_height'
                else:
                    params['sizing_mode'] = config.sizing_mode
            elif config.sizing_mode == 'stretch_width' and 'width' not in params:
                params['sizing_mode'] = config.sizing_mode
            elif config.sizing_mode == 'stretch_height' and 'height' not in params:
                params['sizing_mode'] = config.sizing_mode
        if 'design' not in params and self.param.design.default is None:
            params['design'] = config.design
        super().__init__(**params)



class ServableMixin:
    """
    Mixin to define methods shared by objects which can served.
    """

    def _modify_doc(
        self, server_id: str, title: str, doc: Document, location: Optional['Location']
    ) -> Document:
        """
        Callback to handle FunctionHandler document creation.
        """
        if server_id:
            state._servers[server_id][2].append(doc)
        return self.server_doc(doc, title, location) # type: ignore

    def _add_location(
        self, doc: Document, location: Optional['Location' | bool],
        root: Optional['Model'] = None
    ) -> 'Location':
        from .io.location import Location
        if isinstance(location, Location):
            loc = location
        elif doc in state._locations:
            loc = state._locations[doc]
        else:
            loc = Location()
        state._locations[doc] = loc
        if root is None:
            loc_model = loc.get_root(doc)
        else:
            loc_model = loc._get_model(doc, root)
        loc_model.name = 'location'
        doc.on_session_destroyed(loc._server_destroy) # type: ignore
        doc.add_root(loc_model)
        return loc

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def servable(
        self, title: Optional[str] = None, location: bool | 'Location' = True,
        area: str = 'main', target: Optional[str] = None
    ) -> 'ServableMixin':
        """
        Serves the object or adds it to the configured
        pn.state.template if in a `panel serve` context, writes to the
        DOM if in a pyodide context and returns the Panel object to
        allow it to display itself in a notebook context.

        Arguments
        ---------
        title : str
          A string title to give the Document (if served as an app)
        location : boolean or panel.io.location.Location
          Whether to create a Location component to observe and
          set the URL location.
        area: str (deprecated)
          The area of a template to add the component too. Only has an
          effect if pn.config.template has been set.
        target: str
          Target area to write to. If a template has been configured
          on pn.config.template this refers to the target area in the
          template while in pyodide this refers to the ID of the DOM
          node to write to.

        Returns
        -------
        The Panel object itself
        """
        if curdoc_locked().session_context:
            logger = logging.getLogger('bokeh')
            for handler in logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(logging.WARN)
            if config.template:
                area = target or area or 'main'
                template = state.template
                assert template is not None
                if template.title == template.param.title.default and title:
                    template.title = title
                if area == 'main':
                    template.main.append(self)
                elif area == 'sidebar':
                    template.sidebar.append(self)
                elif area == 'modal':
                    template.modal.append(self)
                elif area == 'header':
                    template.header.append(self)
            else:
                self.server_doc(title=title, location=location) # type: ignore
        elif state._is_pyodide and 'pyodide_kernel' not in sys.modules:
            from .io.pyodide import _IN_WORKER, _get_pyscript_target, write
            if _IN_WORKER:
                return self
            try:
                target = target or _get_pyscript_target()
            except Exception:
                target = None
            if target is not None:
                asyncio.create_task(write(target, self))
        return self

    def show(
        self, title: Optional[str] = None, port: int = 0, address: Optional[str] = None,
        websocket_origin: Optional[str] = None, threaded: bool = False, verbose: bool = True,
        open: bool = True, location: bool | 'Location' = True, **kwargs
    ) -> 'StoppableThread' | 'Server':
        """
        Starts a Bokeh server and displays the Viewable in a new tab.

        Arguments
        ---------
        title : str | None
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
        server: bokeh.server.Server or panel.io.server.StoppableThread
          Returns the Bokeh server instance or the thread the server
          was launched on (if threaded=True)
        """
        return serve(
            self, port=port, address=address, websocket_origin=websocket_origin,
            show=open, start=True, title=title, verbose=verbose,
            location=location, threaded=threaded, **kwargs
        )


class MimeRenderMixin:
    """
    Mixin class to allow rendering and syncing objects in notebook
    contexts.
    """

    def _on_msg(self, ref: str, manager, msg) -> None:
        """
        Handles Protocol messages arriving from the client comm.
        """
        root, doc, comm = state._views[ref][1:]
        patch_cds_msg(root, msg)
        held = doc.callbacks.hold_value
        patch = manager.assemble(msg)
        doc.hold()
        try:
            patch.apply_to_document(doc, comm.id if comm else None)
        except DeserializationError:
            self.param.warning(
                "Comm received message that could not be deserialized."
            )
        finally:
            doc.unhold()
            if held:
                doc.hold(held)

    def _on_error(self, ref: str, error: Exception) -> None:
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

    def _on_stdout(self, ref: str, stdout: Any) -> None:
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

    def _render_mimebundle(self, model: Model, doc: Document, comm: Comm, location: Location | None = None):
        from .models.comm_manager import CommManager

        ref = model.ref['id']
        manager = CommManager(comm_id=comm.id, plot_id=ref)
        client_comm = state._comm_manager.get_client_comm(
            on_msg=partial(self._on_msg, ref, manager),
            on_error=partial(self._on_error, ref),
            on_stdout=partial(self._on_stdout, ref)
        )
        self._comms[ref] = (comm, client_comm)
        manager.client_comm_id = client_comm.id
        return render_mimebundle(model, doc, comm, manager, location)


class Renderable(param.Parameterized, MimeRenderMixin):
    """
    Baseclass for objects which can be rendered to a Bokeh model.

    It therefore declare APIs for initializing the models from
    parameter values.
    """

    __abstract = True

    def __init__(self, **params):
        self._internal_callbacks = []
        self._documents = {}
        self._models = {}
        self._comms = {}
        self._kernels = {}
        super().__init__(**params)
        self._found_links = set()
        self._logger = logging.getLogger(f'{__name__}.{type(self).__name__}')

    def _log(self, msg: str, *args, level: str = 'debug') -> None:
        getattr(self._logger, level)(f'Session %s {msg}', id(state.curdoc), *args)

    def _get_model(
        self, doc: Document, root: Optional['Model'] = None,
        parent: Optional['Model'] = None, comm: Optional[Comm] = None
    ) -> 'Model':
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

    def _cleanup(self, root: Model | None = None) -> None:
        """
        Clean up method which is called when a Viewable is destroyed.

        Arguments
        ---------
        root: bokeh.model.Model
          Bokeh model for the view being cleaned up
        """
        if root is None:
            return
        ref = root.ref['id']
        if ref in state._handles:
            del state._handles[ref]

    def _preprocess(self, root: 'Model', changed=None, old_models=None) -> None:
        """
        Applies preprocessing hooks to the root model.

        Some preprocessors have to always iterate over the entire
        model tree but others only have to update newly added models.
        To support the optimized case we optionally provide the
        Panel object that was changed and any old, unchanged models
        so they can be skipped (see https://github.com/holoviz/panel/pull/4989)
        """
        changed = self if changed is None else changed
        hooks = self._preprocessing_hooks+self._hooks
        for hook in hooks:
            try:
                hook(self, root, changed, old_models)
            except TypeError:
                hook(self, root)

    def _render_model(self, doc: Optional[Document] = None, comm: Optional[Comm] = None) -> 'Model':
        if doc is None:
            doc = Document()
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

    def _init_params(self) -> Mapping[str, Any]:
        return {k: v for k, v in self.param.values().items() if v is not None}

    def _server_destroy(self, session_context: 'BokehSessionContext') -> None:
        """
        Server lifecycle hook triggered when session is destroyed.
        """
        doc = session_context._document
        if doc not in self._documents:
            return
        root = self._documents[doc]
        ref = root.ref['id']
        self._cleanup(root)
        del self._documents[doc]
        if ref in state._views:
            del state._views[ref]

    def __repr__(self, depth: int = 0) -> str:
        return '{cls}({params})'.format(cls=type(self).__name__,
                                        params=', '.join(param_reprs(self)))

    def get_root(
        self, doc: Optional[Document] = None, comm: Optional[Comm] = None,
        preprocess: bool = True
    ) -> Model:
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
        doc = create_doc_if_none_exists(doc)
        if self._design and (comm or (state._is_pyodide and not doc.session_context)):
            wrapper = self._design._wrapper(self)
            if wrapper is self:
                root = self._get_model(doc, comm=comm)
                if preprocess:
                    self._preprocess(root)
            else:
                root = wrapper.get_root(doc, comm, preprocess)
            root_view = wrapper
        else:
            root = self._get_model(doc, comm=comm)
            root_view = self
            if preprocess:
                self._preprocess(root)
        ref = root.ref['id']
        state._views[ref] = (root_view, root, doc, comm)
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

    _preprocessing_hooks: ClassVar[List[Callable[['Viewable', 'Model'], None]]] = []

    def __init__(self, **params):
        hooks = params.pop('hooks', [])
        super().__init__(**params)
        self._hooks = hooks

        self._update_loading()
        self._update_background()
        self._update_design()
        self._internal_callbacks.extend([
            self.param.watch(self._update_background, 'background'),
            self.param.watch(self._update_design, 'design'),
            self.param.watch(self._update_loading, 'loading')
        ])

    def _update_design(self, *_):
        from .theme import Design
        from .theme.native import Native
        if isinstance(self.design, Design):
            self._design = self.design
        elif self.design:
            self._design = self.design(theme=config.theme)
        else:
            self._design = Native(theme=config.theme)

    def _update_loading(self, *_) -> None:
        if self.loading:
            start_loading_spinner(self)
        else:
            stop_loading_spinner(self)

    def _update_background(self, *_) -> None:
        if self.background == self.styles.get("background", None) or self.background is None:
            return

        # Warning
        prev = f'{type(self).name}(..., background={self.background!r})'
        new = f"{type(self).name}(..., styles={{'background': {self.background!r}}})"
        deprecated("1.3", prev, new)

        self.styles = dict(self.styles, background=self.background)

    def _render_model(self, doc: Optional[Document] = None, comm: Optional[Comm] = None) -> 'Model':
        if doc is None:
            doc = Document()
        if comm is None:
            comm = state._comm_manager.get_server_comm()
        model = self.get_root(doc, comm)

        if self._design and self._design.theme.bokeh_theme:
            doc.theme = self._design.theme.bokeh_theme

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

    def _repr_mimebundle_(self, include=None, exclude=None):
        if state._is_pyodide:
            from .io.pyodide import (
                _IN_WORKER, _get_pyscript_target, render_script,
            )

            # If in pyodide and not in a worker we are probably in
            # PyScript otherwise we are probabably in JupyterLite
            if not _IN_WORKER:
                target = _get_pyscript_target()
                return {'text/html': render_script(self, target)}, {}

        loaded = panel_extension._loaded
        if not loaded and 'holoviews' in sys.modules:
            import holoviews as hv  # type: ignore
            loaded = hv.extension._loaded

        if config.comms in ('vscode', 'ipywidgets'):
            widget = ipywidget(self)
            if hasattr(widget, '_repr_mimebundle_'):
                return widget._repr_mimebundle_(include=include, exclude=exclude), {}
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
                from IPython.display import display  # type: ignore
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
            from IPython import get_ipython  # type: ignore
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

        doc = Document()
        comm = state._comm_manager.get_server_comm()
        model = self._render_model(doc, comm)
        if config.embed:
            return render_model(model)

        bundle, meta = self._render_mimebundle(model, doc, comm, location)

        if config.console_output != 'disable' and not state._is_pyodide:
            from IPython.display import display

            ref = model.ref['id']
            handle = display(display_id=uuid.uuid4().hex)
            state._handles[ref] = (handle, [])

        return bundle, meta

    def __str__(self) -> str:
        return self.__repr__()

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def clone(self, **params) -> 'Viewable':
        """
        Makes a copy of the object sharing the same parameters.

        Arguments
        ---------
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned Viewable object
        """
        inherited = {
            p: v for p, v in self.param.values().items()
            if not self.param[p].readonly and v is not self.param[p].default
            and not (v is None and not self.param[p].allow_None)
        }
        return type(self)(**dict(inherited, **params))

    def pprint(self) -> None:
        """
        Prints a compositional repr of the class.
        """
        deprecated('1.3', f'{type(self).__name__}.pprint', 'print')
        print(self)

    def select(
        self, selector: Optional[type | Callable[['Viewable'], bool]] = None
    ) -> List['Viewable']:
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

    def app(self, notebook_url: str = "localhost:8888", port: int = 0) -> 'Server':
        """
        Displays a bokeh server app inline in the notebook.

        Arguments
        ---------
        notebook_url: str
          URL to the notebook server
        port: int (optional, default=0)
          Allows specifying a specific port
        """
        deprecated('1.3', f'{type(self).__name__}.app', 'panel.io.notebook.show_server')
        return show_server(self, notebook_url, port)

    def embed(
        self, max_states: int = 1000, max_opts: int = 3, json: bool = False,
        json_prefix: str = '', save_path: str = './', load_path: Optional[str] = None,
        progress: bool = False, states={}
    ) -> None:
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
        return render_embed(
            self, max_states, max_opts, json, json_prefix, save_path,
            load_path, progress, states
        )

    def save(
        self, filename: str | os.PathLike | IO, title: Optional[str] = None,
        resources: Resources | None = None, template: str | Template | None = None,
        template_variables: Dict[str, Any] = {}, embed: bool = False,
        max_states: int = 1000, max_opts: int = 3, embed_json: bool = False,
        json_prefix: str='', save_path: str='./', load_path: Optional[str] = None,
        progress: bool = True, embed_states: Dict[Any, Any] = {},
        as_png: bool | None = None, **kwargs
    ) -> None:
        """
        Saves Panel objects to file.

        Arguments
        ---------
        filename: str or file-like object
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
        as_png: boolean (default=None)
          To save as a .png. If None save_png will be true if filename is
          string and ends with png.
        """
        return save(
            self, filename, title, resources, template,
            template_variables, embed, max_states, max_opts,
            embed_json, json_prefix, save_path, load_path, progress,
            embed_states, as_png, **kwargs
        )

    def server_doc(
        self, doc: Optional[Document] = None, title: Optional[str] = None,
        location: bool | 'Location' = True
    ) -> Document:
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
        if title or doc.title == 'Bokeh Application':
            title = title or 'Panel Application'
            doc.title = title

        if self._design:
            wrapper = self._design._wrapper(self)
            if wrapper is self:
                model = self.get_root(doc)
            else:
                model = wrapper.get_root(doc)
                ref = model.ref['id']
                state._views[ref] = (wrapper, model, doc, None)
        else:
            model = self.get_root(doc)

        doc.on_session_destroyed(state._destroy_session)
        doc.on_session_destroyed(self._server_destroy) # type: ignore
        self._documents[doc] = model
        add_to_doc(model, doc)
        if location:
            self._add_location(doc, location, model)
        if config.notifications and doc is state.curdoc:
            notification_model = state.notifications.get_root(doc)
            notification_model.name = 'notifications'
            doc.add_root(notification_model)
        if config.browser_info and doc is state.curdoc:
            browser_model = state.browser_info._get_model(doc, model)
            browser_model.name = 'browser_info'
            doc.add_root(browser_model)
        return doc


class Viewer(param.Parameterized):
    """
    A baseclass for custom components that behave like a Panel object.
    By implementing __panel__ method an instance of this class will
    behave like the returned Panel component when placed in a layout,
    render itself in a notebook and provide show and servable methods.
    """

    def __panel__(self) -> Viewable:
        """
        Subclasses should return a Panel component to be rendered.
        """
        raise NotImplementedError

    def _create_view(self):
        from .pane import panel
        from .param import ParamMethod

        if hasattr(self.__panel__, "_dinfo"):
            view = ParamMethod(self.__panel__, lazy=True)
        else:
            view = panel(self.__panel__())

        return view

    def servable(
        self, title: Optional[str]=None, location: bool | 'Location' = True,
        area: str = 'main', target: Optional[str] = None
    ) -> Viewable:
        return self._create_view().servable(title, location, area, target)

    servable.__doc__ = ServableMixin.servable.__doc__

    def show(
        self, title: Optional[str] = None, port: int = 0, address: Optional[str] = None,
        websocket_origin: Optional[str] = None, threaded: bool = False, verbose: bool = True,
        open: bool = True, location: bool | 'Location' = True, **kwargs
    ) -> threading.Thread | 'Server':
        return self._create_view().show(
            title, port, address, websocket_origin, threaded,
            verbose, open, location, **kwargs
        )

    show.__doc__ = ServableMixin.show.__doc__

    def _repr_mimebundle_(self, include=None, exclude=None):
        return self._create_view()._repr_mimebundle_(include, exclude)


__all__ = (
    "Layoutable",
    "Viewable",
    "Viewer"
)
