"""
Defines the PaneBase class defining the API for panes which convert
objects to a visual representation expressed as a bokeh model.
"""
from functools import partial

import param

from bokeh.models.layouts import GridBox as _BkGridBox

from ..io import init_doc, push, state, unlocked
from ..layout import Panel, Row
from ..links import Link
from ..models import ReactiveHTML as _BkReactiveHTML
from ..reactive import Reactive
from ..viewable import Layoutable, Viewable
from ..util import param_reprs


def Pane(obj, **kwargs):
    """
    Converts any object to a Pane if a matching Pane class exists.
    """
    if isinstance(obj, Viewable):
        return obj
    return PaneBase.get_pane_type(obj, **kwargs)(obj, **kwargs)


def panel(obj, **kwargs):
    """
    Creates a panel from any supplied object by wrapping it in a pane
    and returning a corresponding Panel.

    Arguments
    ---------
    obj: object
       Any object to be turned into a Panel
    **kwargs: dict
       Any keyword arguments to be passed to the applicable Pane

    Returns
    -------
    layout: Viewable
       A Viewable representation of the input object
    """
    if isinstance(obj, Viewable):
        return obj
    elif hasattr(obj, '__panel__'):
        return panel(obj.__panel__())
    if kwargs.get('name', False) is None:
        kwargs.pop('name')
    pane = PaneBase.get_pane_type(obj, **kwargs)(obj, **kwargs)
    if len(pane.layout) == 1 and pane._unpack:
        return pane.layout[0]
    return pane.layout


class RerenderError(RuntimeError):
    """
    Error raised when a pane requests re-rendering during initial render.
    """


class PaneBase(Reactive):
    """
    PaneBase is the abstract baseclass for all atomic displayable units
    in the panel library. Pane defines an extensible interface for
    wrapping arbitrary objects and transforming them into Bokeh models.

    Panes are reactive in the sense that when the object they are
    wrapping is changed any dashboard containing the pane will update
    in response.

    To define a concrete Pane type subclass this class and implement
    the applies classmethod and the _get_model private method.
    """

    default_layout = param.ClassSelector(default=Row, class_=(Panel),
                                         is_instance=False, doc="""
        Defines the layout the model(s) returned by the pane will
        be placed in.""")

    object = param.Parameter(default=None, doc="""
        The object being wrapped, which will be converted to a
        Bokeh model.""")

    # When multiple Panes apply to an object, the one with the highest
    # numerical priority is selected. The default is an intermediate value.
    # If set to None, applies method will be called to get a priority
    # value for a specific object type.
    priority = 0.5

    # Whether applies requires full set of keywords
    _applies_kw = False

    # Whether the Pane layout can be safely unpacked
    _unpack = True

    # Declares whether Pane supports updates to the Bokeh model
    _updates = False

    # List of parameters that trigger a rerender of the Bokeh model
    _rerender_params = ['object']

    __abstract = True

    def __init__(self, object=None, **params):
        applies = self.applies(object, **(params if self._applies_kw else {}))
        if (isinstance(applies, bool) and not applies) and object is not None :
            self._type_error(object)

        super().__init__(object=object, **params)
        kwargs = {k: v for k, v in params.items() if k in Layoutable.param}
        self.layout = self.default_layout(self, **kwargs)
        watcher = self.param.watch(self._update_pane, self._rerender_params)
        self._callbacks.append(watcher)

    def _type_error(self, object):
        raise ValueError("%s pane does not support objects of type '%s'." %
                         (type(self).__name__, type(object).__name__))

    def __repr__(self, depth=0):
        cls = type(self).__name__
        params = param_reprs(self, ['object'])
        obj = 'None' if self.object is None else type(self.object).__name__
        template = '{cls}({obj}, {params})' if params else '{cls}({obj})'
        return template.format(cls=cls, params=', '.join(params), obj=obj)

    def __getitem__(self, index):
        """
        Allows pane objects to behave like the underlying layout
        """
        return self.layout[index]

    #----------------------------------------------------------------
    # Callback API
    #----------------------------------------------------------------

    @property
    def _linkable_params(self):
        return [p for p in self._synced_params if self._rename.get(p, False) is not None]

    @property
    def _synced_params(self):
        ignored_params = ['name', 'default_layout', 'loading']+self._rerender_params
        return [p for p in self.param if p not in ignored_params]

    def _update_object(self, ref, doc, root, parent, comm):
        old_model = self._models[ref][0]
        if self._updates:
            self._update(ref, old_model)
        else:
            new_model = self._get_model(doc, root, parent, comm)
            try:
                if isinstance(parent, _BkGridBox):
                    indexes = [i for i, child in enumerate(parent.children)
                               if child[0] is old_model]
                    if indexes:
                        index = indexes[0]
                    else:
                        raise ValueError
                    new_model = (new_model,) + parent.children[index][1:]
                elif isinstance(parent, _BkReactiveHTML):
                    for node, children in parent.children.items():
                        if old_model in children:
                            index = children.index(old_model)
                            new_models = list(children)
                            new_models[index] = new_model
                            break
                else:
                    index = parent.children.index(old_model)
            except ValueError:
                self.warning('%s pane model %s could not be replaced '
                             'with new model %s, ensure that the '
                             'parent is not modified at the same '
                             'time the panel is being updated.' %
                             (type(self).__name__, old_model, new_model))
            else:
                if isinstance(parent, _BkReactiveHTML):
                    parent.children[node] = new_models
                else:
                    parent.children[index] = new_model

        from ..io import state
        ref = root.ref['id']
        if ref in state._views:
            state._views[ref][0]._preprocess(root)

    def _update_pane(self, *events):
        for ref, (_, parent) in self._models.items():
            if ref not in state._views or ref in state._fake_roots:
                continue
            viewable, root, doc, comm = state._views[ref]
            if comm or state._unblocked(doc):
                with unlocked():
                    self._update_object(ref, doc, root, parent, comm)
                if comm and 'embedded' not in root.tags:
                    push(doc, comm)
            else:
                cb = partial(self._update_object, ref, doc, root, parent, comm)
                if doc.session_context:
                    doc.add_next_tick_callback(cb)
                else:
                    cb()

    def _update(self, ref=None, model=None):
        """
        If _updates=True this method is used to update an existing
        Bokeh model instead of replacing the model entirely. The
        supplied model should be updated with the current state.
        """
        raise NotImplementedError

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    @classmethod
    def applies(cls, obj):
        """
        Given the object return a boolean indicating whether the Pane
        can render the object. If the priority of the pane is set to
        None, this method may also be used to define a priority
        depending on the object being rendered.
        """
        return None

    def clone(self, object=None, **params):
        """
        Makes a copy of the Pane sharing the same parameters.

        Arguments
        ---------
        params: Keyword arguments override the parameters on the clone.

        Returns
        -------
        Cloned Pane object
        """
        params = dict(self.param.get_param_values(), **params)
        old_object = params.pop('object')
        if object is None:
            object = old_object
        return type(self)(object, **params)

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
        if self._updates:
            root = self._get_model(doc, comm=comm)
        else:
            root = self.layout._get_model(doc, comm=comm)
        if preprocess:
            self._preprocess(root)
        ref = root.ref['id']
        state._views[ref] = (self, root, doc, comm)
        return root

    @classmethod
    def get_pane_type(cls, obj, **kwargs):
        """
        Returns the applicable Pane type given an object by resolving
        the precedence of all types whose applies method declares that
        the object is supported.

        Arguments
        ---------
        obj (object): The object type to return a Pane for

        Returns
        -------
        The applicable Pane type with the highest precedence.
        """
        if isinstance(obj, Viewable):
            return type(obj)
        descendents = []
        for p in param.concrete_descendents(PaneBase).values():
            if p.priority is None:
                applies = True
                try:
                    priority = p.applies(obj, **(kwargs if p._applies_kw else {}))
                except Exception:
                    priority = False
            else:
                applies = None
                priority = p.priority
            if isinstance(priority, bool) and priority:
                raise ValueError('If a Pane declares no priority '
                                 'the applies method should return a '
                                 'priority value specific to the '
                                 'object type or False, but the %s pane '
                                 'declares no priority.' % p.__name__)
            elif priority is None or priority is False:
                continue
            descendents.append((priority, applies, p))
        pane_types = reversed(sorted(descendents, key=lambda x: x[0]))
        for _, applies, pane_type in pane_types:
            if applies is None:
                try:
                    applies = pane_type.applies(obj, **(kwargs if pane_type._applies_kw else {}))
                except Exception:
                    applies = False
            if not applies:
                continue
            return pane_type
        raise TypeError('%s type could not be rendered.' % type(obj).__name__)



class ReplacementPane(PaneBase):
    """
    A Pane type which allows for complete replacement of the underlying
    bokeh model by creating an internal layout to replace the children
    on.
    """

    _updates = True

    __abstract = True

    def __init__(self, object=None, **params):
        self._kwargs =  {p: params.pop(p) for p in list(params)
                         if p not in self.param}
        super().__init__(object, **params)
        self._pane = Pane(None)
        self._internal = True
        self._inner_layout = Row(self._pane, **{k: v for k, v in params.items() if k in Row.param})
        self.param.watch(self._update_inner_layout, list(Layoutable.param))

    def _update_inner_layout(self, *events):
        for event in events:
            setattr(self._pane, event.name, event.new)
            if event.name in ['sizing_mode', 'width_policy', 'height_policy']:
                setattr(self._inner_layout, event.name, event.new)

    def _update_pane(self, *events):
        """
        Updating of the object should be handled manually.
        """

    @classmethod
    def _update_from_object(cls, object, old_object, was_internal, **kwargs):
        pane_type = cls.get_pane_type(object)
        try:
            links = Link.registry.get(object)
        except TypeError:
            links = []
        custom_watchers = False
        if isinstance(object, Reactive):
            watchers = [
                w for pwatchers in object._param_watchers.values()
                for awatchers in pwatchers.values() for w in awatchers
            ]
            custom_watchers = [wfn for wfn in watchers if wfn not in object._callbacks]

        pane, internal = None, was_internal
        if type(old_object) is pane_type and not links and not custom_watchers and was_internal:
            # If the object has not external referrers we can update
            # it inplace instead of replacing it
            if isinstance(object, Reactive):
                pvals = dict(old_object.param.get_param_values())
                new_params = {k: v for k, v in object.param.get_param_values()
                              if k != 'name' and v is not pvals[k]}
                old_object.param.set_param(**new_params)
            else:
                old_object.object = object
        else:
            # Replace pane entirely
            pane = panel(object, **{k: v for k, v in kwargs.items()
                                    if k in pane_type.param})
            if pane is object:
                # If all watchers on the object are internal watchers
                # we can make a clone of the object and update this
                # clone going forward, otherwise we have replace the
                # model entirely which is more expensive.
                if not (custom_watchers or links):
                    pane = object.clone()
                    internal = True
                else:
                    internal = False
            else:
                internal = object is not old_object
        return pane, internal

    def _update_inner(self, new_object):
        kwargs = dict(self.param.get_param_values(), **self._kwargs)
        del kwargs['object']
        new_pane, internal = self._update_from_object(
            new_object, self._pane, self._internal, **kwargs
        )
        if new_pane is None:
            return

        self._pane = new_pane
        self._inner_layout[0] = self._pane
        self._internal = internal

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if root:
            ref = root.ref['id']
            if ref in self._models:
                self._cleanup(root)
        model = self._inner_layout._get_model(doc, root, parent, comm)
        if root is None:
            ref = model.ref['id']
        self._models[ref] = (model, parent)
        return model

    def _cleanup(self, root=None):
        self._inner_layout._cleanup(root)
        super()._cleanup(root)

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
        selected = super().select(selector)
        selected += self._inner_layout.select(selector)
        return selected
