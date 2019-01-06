"""
"""
import param
import weakref

from collections import defaultdict
from functools import partial

from .viewable import Viewable
from .holoviews import find_links


class Link(param.Parameterized):
    """
    A Link defines some connection between a source and target object
    in their visualization. It is quite similar to a Stream as it
    allows defining callbacks in response to some change or event on
    the source object, however, unlike a Stream, it does not transfer
    data and make it available to user defined subscribers. Instead
    a Link directly causes some action to occur on the target, for JS
    based backends this usually means that a corresponding JS callback
    will effect some change on the target in response to a change on
    the source.

    A Link must define a source object which is what triggers events,
    but must not define a target. It is also possible to define bi-
    directional links between the source and target object.
    """

    # Mapping from a source id to a Link instance
    registry = weakref.WeakKeyDictionary()

    # Mapping to define callbacks by backend and Link type.
    # e.g. Link._callbacks['bokeh'][Stream] = Callback
    _callbacks = defaultdict(dict)

    # Whether the link requires a target
    _requires_target = False

    def __init__(self, source, target=None, **params):
        if source is None:
            raise ValueError('%s must define a source' % type(self).__name__)
        if self._requires_target and target is None:
            raise ValueError('%s must define a target.' % type(self).__name__)

        # Source is stored as a weakref to allow it to be garbage collected
        self._source = None if source is None else weakref.ref(source)
        self._target = None if target is None else weakref.ref(target)
        super(Link, self).__init__(**params)
        self.link()

    @classmethod
    def register_callback(cls, backend, callback):
        """
        Register a LinkCallback providing the implementation for
        the Link for a particular backend.
        """
        cls._callbacks[backend][cls] = callback

    @property
    def source(self):
        return self._source() if self._source else None

    @property
    def target(self):
        return self._target() if self._target else None

    def link(self):
        """
        Registers the Link
        """
        if self.source in self.registry:
            links = self.registry[self.source]
            params = {
                k: v for k, v in self.get_param_values() if k != 'name'}
            for link in links:
                link_params = {
                    k: v for k, v in link.get_param_values() if k != 'name'}
                if (type(link) is type(self) and link.source is self.source
                    and link.target is self.target and params == link_params):
                    return
            self.registry[self.source].append(self)
        else:
            self.registry[self.source] = [self]

    def unlink(self):
        """
        Unregisters the Link
        """
        links = self.registry.get(self.source)
        if self in links:
            links.pop(links.index(self))


class PanelLink(Link):
    """
    Link between HoloViews elements containing Bokeh plots
    """
    
    registry = weakref.WeakKeyDictionary()    


class RangeAxesLink(PanelLink):
    """
    The RangeAxesLink sets up a link between the axes of the source
    plot and the axes on the target plot. By default it will
    link along the x-axis but using the axes parameter both axes may
    be linked to the tool.
    """

    axes = param.ListSelector(default=['x', 'y'], objects=['x', 'y'], doc="""
        Which axes to link the tool to.""")


class RangeAxesLinkCallback(param.Parameterized):
    """
    Links source plot axes to the specified axes on the target plot
    """

    def __init__(self, root_model, link, source_plot, target_plot):
        if target_plot is None:
            return
        if 'x' in link.axes:
            target_plot.handles['plot'].x_range = source_plot.handles['plot'].x_range
        if 'y' in link.axes:
            target_plot.handles['plot'].y_range = source_plot.handles['plot'].y_range


RangeAxesLink.register_callback(backend='bokeh',
                                callback = RangeAxesLinkCallback)

Viewable._preprocessing_hooks.append(partial(find_links, Link=PanelLink))
