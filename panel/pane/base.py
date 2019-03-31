"""
Defines the PaneBase class defining the API for panes which convert
objects to a visual representation expressed as a bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

from functools import partial

import param

from bokeh.io import curdoc as _curdoc

from ..io import push, state
from ..layout import Panel, Row
from ..viewable import Viewable, Reactive, Layoutable
from ..util import param_reprs


def Pane(obj, **kwargs):
    """
    Converts any object to a Pane if a matching Pane class exists.
    """
    if isinstance(obj, Viewable):
        return obj
    return PaneBase.get_pane_type(obj)(obj, **kwargs)


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
        The object being wrapped, which will be converted to a Bokeh model.""")

    # When multiple Panes apply to an object, the one with the highest
    # numerical priority is selected. The default is an intermediate value.
    # If set to None, applies method will be called to get a priority
    # value for a specific object type.
    priority = 0.5

    # Declares whether Pane supports updates to the Bokeh model
    _updates = False

    # Whether the Pane layout can be safely unpacked
    _unpack = True

    # List of parameters that trigger a rerender of the Bokeh model
    _rerender_params = ['object']

    __abstract = True

    def __init__(self, object=None, **params):
        applies = self.applies(object)
        if (isinstance(applies, bool) and not applies) and object is not None :
            raise ValueError("%s pane does not support objects of type '%s'" %
                             (type(self).__name__, type(object).__name__))

        super(PaneBase, self).__init__(object=object, **params)
        kwargs = {k: v for k, v in params.items() if k in Layoutable.param}
        self.layout = self.default_layout(self, **kwargs)
        self.param.watch(self._update_pane, self._rerender_params)

    def __repr__(self, depth=0):
        cls = type(self).__name__
        params = param_reprs(self, ['object'])
        obj = 'Empty' if self.object is None else type(self.object).__name__ 
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

    def _synced_params(self):
        ignored_params = ['name', 'default_layout']+self._rerender_params
        return [p for p in self.param if p not in ignored_params]

    def _init_properties(self):
        return {k: v for k, v in self.param.get_param_values()
                if v is not None and k not in ['default_layout', 'object']}

    def _update_object(self, old_model, doc, root, parent, comm):
        if self._updates:
            self._update(old_model)
        else:
            new_model = self._get_model(doc, root, parent, comm)
            try:
                index = parent.children.index(old_model)
            except IndexError:
                self.warning('%s pane model %s could not be replaced '
                             'with new model %s, ensure that the '
                             'parent is not modified at the same '
                             'time the panel is being updated.' %
                             (type(self).__name__, old_model, new_model))
            else:
                parent.children[index] = new_model

    def _update_pane(self, event):
        for ref, (model, parent) in self._models.items():
            viewable, root, doc, comm = state._views[ref]
            if comm or state._unblocked(doc):
                self._update_object(model, doc, root, parent, comm)
                if comm and 'embedded' not in root.tags:
                    push(doc, comm)
            else:
                cb = partial(self._update_object, model, doc, root, parent, comm)
                doc.add_next_tick_callback(cb)

    def _update(self, model):
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
        if self._updates:
            root = self._get_model(doc, comm=comm)
        else:
            root = self.layout._get_model(doc, comm=comm)
        self._preprocess(root)
        ref = root.ref['id']
        state._views[ref] = (self, root, doc, comm)
        return root

    @classmethod
    def get_pane_type(cls, obj):
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
            priority = p.applies(obj) if p.priority is None else p.priority
            if isinstance(priority, bool) and priority:
                raise ValueError('If a Pane declares no priority '
                                 'the applies method should return a '
                                 'priority value specific to the '
                                 'object type or False, but the %s pane '
                                 'declares no priority.' % p.__name__)
            elif priority is None or priority is False:
                continue
            descendents.append((priority, p))
        pane_types = reversed(sorted(descendents, key=lambda x: x[0]))
        for _, pane_type in pane_types:
            applies = pane_type.applies(obj)
            if isinstance(applies, bool) and not applies: continue
            return pane_type
        raise TypeError('%s type could not be rendered.' % type(obj).__name__)
