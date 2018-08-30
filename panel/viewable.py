"""
Defines the Viewable and Reactive baseclasses allow all panel objects
to display themselves, communicate with a Python process and react in
response to changes to parameters and the underlying bokeh models.
"""

from functools import partial
from collections import defaultdict

import param

from bokeh.document import Document
from bokeh.io import curdoc, show
from bokeh.models import CustomJS
from pyviz_comms import JS_CALLBACK, JupyterCommManager

from .util import render_mimebundle, add_to_doc, push


class Viewable(param.Parameterized):
    """
    Viewable is the baseclass all objects in the panel library are
    built on. It defines the interface for declaring any object that
    displays itself by transforming the object(s) being wrapped into
    models that can be served using bokeh's layout engine. The class
    also defines various methods that allow Viewable objects to be
    displayed in the notebook and on bokeh server.
    """

    __abstract = True

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
        Returns the root model

        doc: bokeh.Document
          Bokeh document the bokeh model will be attached to.

        comm: pyviz_comms.Comm
          Optional pyviz_comms when working in notebook
        """
        return self._get_model(doc, comm=comm)

    def _cleanup(self, model, final=False):
        """
        Clean up method which is called when a Viewable is destroyed.

        model: bokeh.model.Model
            Bokeh model for the view being cleaned up

        final: boolean
            Whether the Panel can be destroyed entirely
        """

    def _repr_mimebundle_(self, include=None, exclude=None):
        doc = Document()
        comm = JupyterCommManager.get_server_comm()
        model = self._get_root(doc, comm)
        return render_mimebundle(model, doc, comm)

    def server_doc(self, doc=None):
        doc = doc or curdoc()
        model = self._get_root(doc)
        add_to_doc(model, doc)
        return doc

    def _modify_doc(self, doc):
        return self.server_doc(doc)

    def app(self, notebook_url="localhost:8888"):
        """
        Displays a bokeh server app in the notebook.
        """
        show(self._modify_doc, notebook_url=notebook_url)



class Reactive(Viewable):
    """
    Reactive is a Viewable object that also supports syncing between
    the objects parameters and the underlying bokeh model either via
    the defined pyviz_comms.Comm type or when using bokeh server.

    In order to link parameters with bokeh model instances the
    _link_params and _link_props methods may be called in the
    _get_model method. Since there may not be a 1-to-1 mapping between
    parameter and the model property the _process_property_change and
    _process_param_change may be overridden to apply any necessary
    transformations.
    """

    # Timeout if a notebook comm message is swallowed
    _timeout = 20000

    # Timeout before the first event is processed
    _debounce = 50

    # Mapping from parameter name to bokeh model property name
    _renames = {}

    _callbacks = defaultdict(dict)

    def __init__(self, **params):
        super(Reactive, self).__init__(**params)
        self._active = False
        self._events = {}

    def link(self, obj, **links):
        """
        Links the parameters on this object to parameters on another
        object.

        obj: object

        links: dict
            Maps between parameters on this object to the parameters
            on the supplied object.
        """
        def link(change, _updating=[]):
            if change.attribute not in _updating:
                _updating.append(change.attribute)
                setattr(obj, links[change.attribute], change.new)
                _updating.pop(_updating.index(change.attribute))
        for param, other_param in links.items():
            self.param.watch(link, param)
            if not hasattr(obj, other_param):
                raise AttributeError('Linked object %s has no attribute %s.'
                                     % (obj, other_param))

    def _cleanup(self, model, final=False):
        super(Reactive, self)._cleanup(model, final)
        if model is None:
            return
        callbacks = self._callbacks[model.ref['id']]
        for p, cb in callbacks.items():
            self.param.unwatch(cb, p)

    def _process_property_change(self, msg):
        """
        Transform bokeh model property changes into parameter updates.
        Should be overridden to provide appropriate mapping between
        parameter value and bokeh model change. By default uses the
        _renames class level attribute to map between parameter and
        property names.
        """
        inverted = {v: k for k, v in self._renames}
        return {inverted.get(k, k): v for k, v in msg.items()}

    def _process_param_change(self, msg):
        """
        Transform parameter changes into bokeh model property updates.
        Should be overridden to provide appropriate mapping between
        parameter value and bokeh model change. By default uses the
        _renames class level attribute to map between parameter and
        property names.
        """
        return {self._renames.get(k, k): v for k, v in msg.items()}

    def _link_params(self, model, params, doc, root, comm=None):
        for p in params:
            def set_value(change, parameter=p):
                msg = self._process_param_change({parameter: change.new})
                def update_model():
                    model.update(**msg)
                if comm:
                    update_model()
                    push(doc, comm)
                else:
                    doc.add_next_tick_callback(update_model)
            self.param.watch(set_value, p)
            self._callbacks[model.ref['id']][p] = set_value

    def _link_props(self, model, properties, doc, root, comm=None):
        if comm is None:
            for p in properties:
                model.on_change(p, partial(self._server_change, doc))
        else:
            client_comm = JupyterCommManager.get_client_comm(on_msg=self._comm_change)
            for p in properties:
                customjs = self._get_customjs(p, client_comm, root.ref['id'])
                model.js_on_change(p, customjs)

    def _comm_change(self, msg):
        self._events.update(msg)
        self._change_event()

    def _server_change(self, doc, attr, old, new):
        self._events.update({attr: new})
        if not self._active:
            doc.add_timeout_callback(self._change_event, self._debounce)
            self._active = True

    def _change_event(self):
        self.set_param(**self._process_property_change(self._events))
        self._events = {}
        self._active = False

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
