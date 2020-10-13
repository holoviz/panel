"""
Declares Syncable and Reactive classes which provides baseclasses
for Panel components which sync their state with one or more bokeh
models rendered on the frontend. 
"""

import difflib
import threading

from collections import namedtuple
from functools import partial

from bokeh.models import LayoutDOM
from tornado import gen

from .config import config
from .io.callbacks import PeriodicCallback
from .io.model import hold
from .io.notebook import push
from .io.server import unlocked
from .io.state import state
from .util import edit_readonly
from .viewable import Layoutable, Renderable, Viewable

LinkWatcher = namedtuple("Watcher","inst cls fn mode onlychanged parameter_names what queued target links transformed bidirectional_watcher")


class Syncable(Renderable):
    """
    Syncable is an extension of the Renderable object which can not
    only render to a bokeh model but also sync the parameters on the
    object with the properties on the model.

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

    __abstract = True

    events = []

    def __init__(self, **params):
        super(Syncable, self).__init__(**params)
        self._processing = False
        self._events = {}
        self._callbacks = []
        self._links = []
        self._link_params()
        self._changing = {}

    # Allows defining a mapping from model property name to a JS code
    # snippet that transforms the object before serialization
    _js_transforms = {}

    # Transforms from input value to bokeh property value
    _source_transforms = {}
    _target_transforms = {}

    #----------------------------------------------------------------
    # Model API
    #----------------------------------------------------------------

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

    def _link_params(self):
        params = self._synced_params()
        if params:
            watcher = self.param.watch(self._param_change, params)
            self._callbacks.append(watcher)

    def _link_props(self, model, properties, doc, root, comm=None):
        ref = root.ref['id']
        if config.embed:
            return

        for p in properties:
            if isinstance(p, tuple):
                _, p = p
            if comm:
                model.on_change(p, partial(self._comm_change, doc, ref, comm))
            else:
                model.on_change(p, partial(self._server_change, doc, ref))

    @property
    def _linkable_params(self):
        return [p for p in self._synced_params()
                if self._source_transforms.get(p, False) is not None]

    def _synced_params(self):
        return list(self.param)

    def _update_model(self, events, msg, root, model, doc, comm):
        self._changing[root.ref['id']] = [
            attr for attr, value in msg.items()
            if not model.lookup(attr).property.matches(getattr(model, attr), value)
        ]
        try:
            model.update(**msg)
        finally:
            del self._changing[root.ref['id']]

    def _cleanup(self, root):
        super(Syncable, self)._cleanup(root)
        ref = root.ref['id']
        self._models.pop(ref, None)
        comm, client_comm = self._comms.pop(ref, (None, None))
        if comm:
            try:
                comm.close()
            except Exception:
                pass
        if client_comm:
            try:
                client_comm.close()
            except Exception:
                pass

    def _param_change(self, *events):
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
            if ref not in state._views or ref in state._fake_roots:
                continue
            viewable, root, doc, comm = state._views[ref]
            if comm or not doc.session_context or state._unblocked(doc):
                with unlocked():
                    self._update_model(events, msg, root, model, doc, comm)
                if comm and 'embedded' not in root.tags:
                    push(doc, comm)
            else:
                cb = partial(self._update_model, events, msg, root, model, doc, comm)
                doc.add_next_tick_callback(cb)

    def _process_events(self, events):
        with edit_readonly(state):
            state.busy = True
        try:
            with edit_readonly(self):
                self.param.set_param(**self._process_property_change(events))
        finally:
            with edit_readonly(state):
                state.busy = False

    @gen.coroutine
    def _change_coroutine(self, doc=None):
        self._change_event(doc)

    def _change_event(self, doc=None):
        try:
            state.curdoc = doc
            thread = threading.current_thread()
            thread_id = thread.ident if thread else None
            state._thread_id = thread_id
            events = self._events
            self._events = {}
            self._process_events(events)
        finally:
            self._processing = False
            state.curdoc = None
            state._thread_id = None

    def _comm_change(self, doc, ref, comm, attr, old, new):
        if attr in self._changing.get(ref, []):
            self._changing[ref].remove(attr)
            return

        with hold(doc, comm=comm):
            self._process_events({attr: new})

    def _server_change(self, doc, ref, attr, old, new):
        if attr in self._changing.get(ref, []):
            self._changing[ref].remove(attr)
            return

        state._locks.clear()
        self._events.update({attr: new})
        if not self._processing:
            self._processing = True
            if doc.session_context:
                doc.add_timeout_callback(partial(self._change_coroutine, doc), self._debounce)
            else:
                self._change_event(doc)


class Reactive(Syncable, Viewable):
    """
    Reactive is a Viewable object that also supports syncing between
    the objects parameters and the underlying bokeh model either via
    the defined pyviz_comms.Comm type or using bokeh server.

    In addition it defines various methods which make it easy to link
    the parameters to other objects.
    """

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

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
        self.param.warning(
            "Calling add_periodic_callback on a Panel component is "
            "deprecated and will be removed in the next minor release. "
            "Use the pn.state.add_periodic_callback API instead."
        )
        cb = PeriodicCallback(callback=callback, period=period,
                              count=count, timeout=timeout)
        if start:
            cb.start()
        return cb

    def link(self, target, callbacks=None, bidirectional=False,  **links):
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
        bidirectional: boolean
          Whether to link source and target bi-directionally
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
        elif callbacks and bidirectional:
            raise ValueError('Bidirectional linking not supported for '
                             'explicit callbacks. You must define '
                             'separate callbacks for each direction.')

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
                finally:
                    _updating.pop(_updating.index(event.name))
        params = list(callbacks) if callbacks else list(links)
        cb = self.param.watch(link, params)

        bidirectional_watcher = None
        if bidirectional:
            _reverse_updating = []
            reverse_links = {v: k for k, v in links.items()}
            def reverse_link(*events):
                for event in events:
                    if event.name in _reverse_updating: continue
                    _reverse_updating.append(event.name)
                    try:
                        setattr(self, reverse_links[event.name], event.new)
                    finally:
                        _reverse_updating.remove(event.name)
            bidirectional_watcher = target.param.watch(reverse_link, list(reverse_links))

        link = LinkWatcher(*tuple(cb)+(target, links, callbacks is not None, bidirectional_watcher))
        self._links.append(link)
        return cb

    def controls(self, parameters=[], jslink=True):
        """
        Creates a set of widgets which allow manipulating the parameters
        on this instance. By default all parameters which support
        linking are exposed, but an explicit list of parameters can
        be provided.

        Arguments
        ---------
        parameters: list(str)
           An explicit list of parameters to return controls for.
        jslink: bool
           Whether to use jslinks instead of Python based links.
           This does not allow using all types of parameters.

        Returns
        -------
        A layout of the controls
        """
        from .param import Param
        from .layout import Tabs, WidgetBox
        from .widgets import LiteralInput

        if parameters:
            linkable = parameters
        elif jslink:
            linkable = self._linkable_params
        else:
            linkable = list(self.param)

        params = [p for p in linkable if p not in Layoutable.param]
        controls = Param(self.param, parameters=params, default_layout=WidgetBox,
                         name='Controls')
        layout_params = [p for p in linkable if p in Layoutable.param]
        if 'name' not in layout_params and self._rename.get('name', False) is not None and not parameters:
            layout_params.insert(0, 'name')
        style = Param(self.param, parameters=layout_params, default_layout=WidgetBox,
                      name='Layout')
        if jslink:
            for p in params:
                widget = controls._widgets[p]
                widget.jslink(self, value=p, bidirectional=True)
                if isinstance(widget, LiteralInput):
                    widget.serializer = 'json'
            for p in layout_params:
                widget = style._widgets[p]
                widget.jslink(self, value=p, bidirectional=True)
                if isinstance(widget, LiteralInput):
                    widget.serializer = 'json'

        if params and layout_params:
            return Tabs(controls.layout[0], style.layout[0])
        elif params:
            return controls.layout[0]
        return style.layout[0]

    def jscallback(self, args={}, **callbacks):
        """
        Allows defining a JS callback to be triggered when a property
        changes on the source object. The keyword arguments define the
        properties that trigger a callback and the JS code that gets
        executed.

        Arguments
        ----------
        args: dict
          A mapping of objects to make available to the JS callback
        **callbacks: dict
          A mapping between properties on the source model and the code
          to execute when that property changes

        Returns
        -------
        callback: Callback
          The Callback which can be used to disable the callback.
        """

        from .links import Callback
        for k, v in list(callbacks.items()):
            callbacks[k] = self._rename.get(v, v)
        return Callback(self, code=callbacks, args=args)

    def jslink(self, target, code=None, args=None, bidirectional=False, **links):
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
        bidirectional: boolean
          Whether to link source and target bi-directionally
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
        if args is None:
            args = {}

        mapping = code or links
        for k in mapping:
            if k.startswith('event:'):
                continue
            elif hasattr(self, 'object') and isinstance(self.object, LayoutDOM):
                current = self.object
                for attr in k.split('.'):
                    if not hasattr(current, attr):
                        raise ValueError(f"Could not resolve {k} on "
                                         f"{self.object} model. Ensure "
                                         "you jslink an attribute that "
                                         "exists on the bokeh model.")
                    current = getattr(current, attr)
            elif (k not in self.param and k not in list(self._rename.values())):
                matches = difflib.get_close_matches(k, list(self.param))
                if matches:
                    matches = ' Similar parameters include: %r' % matches
                else:
                    matches = ''
                raise ValueError("Could not jslink %r parameter (or property) "
                                 "on %s object because it was not found.%s"
                                 % (k, type(self).__name__, matches))
            elif (self._source_transforms.get(k, False) is None or
                  self._rename.get(k, False) is None):
                raise ValueError("Cannot jslink %r parameter on %s object, "
                                 "the parameter requires a live Python kernel "
                                 "to have an effect." % (k, type(self).__name__))

        if isinstance(target, Syncable) and code is None:
            for k, p in mapping.items():
                if k.startswith('event:'):
                    continue
                elif p not in target.param and p not in list(target._rename.values()):
                    matches = difflib.get_close_matches(p, list(target.param))
                    if matches:
                        matches = ' Similar parameters include: %r' % matches
                    else:
                        matches = ''
                    raise ValueError("Could not jslink %r parameter (or property) "
                                     "on %s object because it was not found.%s"
                                    % (p, type(self).__name__, matches))
                elif (target._source_transforms.get(p, False) is None or
                      target._rename.get(p, False) is None):
                    raise ValueError("Cannot jslink %r parameter on %s object "
                                     "to %r parameter on %s object. It requires "
                                     "a live Python kernel to have an effect."
                                     % (k, type(self).__name__, p, type(target).__name__))

        from .links import Link
        return Link(self, target, properties=links, code=code, args=args,
                    bidirectional=bidirectional)
