"""
Defines the PaneBase class defining the API for panes which convert
objects to a visual representation expressed as a bokeh model.
"""
from __future__ import absolute_import, division, unicode_literals

import param

from ..io import state
from ..layout import Panel, Row
from ..viewable import Viewable, Reactive, Layoutable
from ..util import param_reprs, push


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

    __abstract = True

    @classmethod
    def applies(cls, obj):
        """
        Given the object return a boolean indicating whether the Pane
        can render the object. If the priority of the pane is set to
        None, this method may also be used to define a priority
        depending on the object being rendered.
        """
        return None

    @classmethod
    def get_pane_type(cls, obj):
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

    def __init__(self, object, **params):
        applies = self.applies(object)
        if isinstance(applies, bool) and not applies:
            raise ValueError("%s pane does not support objects of type '%s'" %
                             (type(self).__name__, type(object).__name__))

        super(PaneBase, self).__init__(object=object, **params)
        kwargs = {k: v for k, v in params.items() if k in Layoutable.param}
        self.layout = self.default_layout(self, **kwargs)

    def __repr__(self, depth=0):
        cls = type(self).__name__
        params = param_reprs(self, ['object'])
        obj = type(self.object).__name__
        template = '{cls}({obj}, {params})' if params else '{cls}({obj})'
        return template.format(cls=cls, params=', '.join(params), obj=obj)

    def __getitem__(self, index):
        """
        Allows pane objects to behave like the underlying layout
        """
        return self.layout[index]

    def _get_root(self, doc, comm=None):
        if self._updates:
            root = self._get_model(doc, comm=comm)
        else:
            root = self.layout._get_model(doc, comm=comm)
        self._preprocess(root)
        return root

    def _cleanup(self, root=None, final=False):
        super(PaneBase, self)._cleanup(root, final)
        if final:
            self.object = None

    def _update(self, model):
        """
        If _updates=True this method is used to update an existing Bokeh
        model instead of replacing the model entirely. The supplied model
        should be updated with the current state.
        """
        raise NotImplementedError

    def _link_object(self, doc, root, parent, comm=None):
        """
        Links the object parameter to the rendered Bokeh model, triggering
        an update when the object changes.
        """
        ref = root.ref['id']

        def update_pane(change):
            old_model = self._models[ref]

            if self._updates:
                # Pane supports model updates
                def update_models():
                    self._update(old_model)
            else:
                # Otherwise replace the whole model
                new_model = self._get_model(doc, root, parent, comm)
                def update_models():
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

            if comm:
                update_models()
                push(doc, comm)
            elif state.curdoc:
                update_models()
            else:
                doc.add_next_tick_callback(update_models)

        if ref not in self._callbacks:
            self._callbacks[ref].append(self.param.watch(update_pane, 'object'))
