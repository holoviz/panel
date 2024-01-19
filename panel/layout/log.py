from __future__ import annotations

from typing import (
    TYPE_CHECKING, ClassVar, List, Mapping, Optional, Type,
)

import param

from ..models import Log as PnLog
from ..models.log import ScrollButtonClick
from .base import Column

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm

    from ..viewable import Viewable


class Log(Column):

    load_buffer = param.Integer(default=50, bounds=(0, None), doc="""
        The number of objects loaded on each side of the visible objects.
        When scrolled halfway into the buffer, the log will automatically
        load additional objects while unloading objects on the opposite side.""")

    scroll = param.Boolean(default=True, doc="""
        Whether to add scrollbars if the content overflows the size
        of the container.""")

    visible_indices = param.List(constant=True, doc="""
        Read-only list of indices representing the currently visible log objects.
        This list is automatically updated based on scrolling.""")

    _bokeh_model: ClassVar[Type[Model]] = PnLog

    _direction = 'vertical'

    _rename: ClassVar[Mapping[str, str | None]] = {
        'objects': 'children', 'visible_indices': 'visible_objects',
        'load_buffer': None,
    }

    def __init__(self, *objects, **params):
        for height_param in ["height", "min_height", "max_height"]:
            if height_param in params:
                break
        else:
            # sets a default height to prevent infinite load
            params["height"] = 300

        super().__init__(*objects, **params)
        self._last_synced = None

    @param.depends("visible_indices", "load_buffer", watch=True)
    def _trigger_get_objects(self):
        # visible start, end / synced start, end
        vs, ve = min(self.visible_indices), max(self.visible_indices)
        ss, se = min(self._last_synced), max(self._last_synced)
        half_buffer = self.load_buffer // 2
        if (vs - ss) < half_buffer or (se - ve) < half_buffer:
            self.param.trigger("objects")

    @property
    def _synced_indices(self):
        n = len(self.objects)
        if self.visible_indices:
            return list(range(
                max(min(self.visible_indices) - self.load_buffer, 0),
                min(max(self.visible_indices) + self.load_buffer, n)
            ))
        elif self.view_latest:
            return list(range(max(n - self.load_buffer * 2, 0), n))
        else:
            return list(range(min(self.load_buffer, n)))

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        model = super()._get_model(doc, root, parent, comm)
        self._register_events('scroll_button_click', model=model, doc=doc, comm=comm)
        return model

    def _process_property_change(self, msg):
        if 'visible_objects' in msg:
            visible = msg.pop('visible_objects')
            for model, _ in self._models.values():
                refs = [c.ref['id'] for c in model.children]
                if visible and visible[0] in refs:
                    indexes = [refs.index(v) for v in visible if v in refs]
                    break
            else:
                return super()._process_property_change(msg)
            offset = min(self._synced_indices)
            msg['visible_indices'] = [offset+i for i in sorted(indexes)]
        return super()._process_property_change(msg)

    def _process_param_change(self, msg):
        msg.pop('visible_indices', None)
        return super()._process_param_change(msg)

    def _get_objects(
        self, model: Model, old_objects: List[Viewable], doc: Document,
        root: Model, comm: Optional[Comm] = None
    ):
        from ..pane.base import RerenderError, panel
        new_models, old_models = [], []
        self._last_synced = synced = self._synced_indices

        for i, pane in enumerate(self.objects):
            self.objects[i] = panel(pane)

        for obj in old_objects:
            if obj not in self.objects:
                obj._cleanup(root)

        current_objects = list(self.objects)
        ref = root.ref['id']
        for i in synced:
            pane = current_objects[i]
            if pane in old_objects and ref in pane._models:
                child, _ = pane._models[root.ref['id']]
                old_models.append(child)
            else:
                try:
                    child = pane._get_model(doc, root, model, comm)
                except RerenderError as e:
                    if e.layout is not None and e.layout is not self:
                        raise e
                    e.layout = None
                    return self._get_objects(model, current_objects[:i], doc, root, comm)
            new_models.append(child)
        return new_models, old_models

    def _process_event(self, event: ScrollButtonClick) -> None:
        """
        Process a scroll button click event.
        """
        if not self.visible_indices:
            return

        # need to get it all the way to the bottom rather
        # than the center of the buffer zone
        load_buffer = self.load_buffer
        with param.discard_events(self):
            self.load_buffer = 1

        n = len(self.objects)
        with param.edit_constant(self):
            # + 1 to keep the scroll bar visible
            self.visible_indices = list(
                range(max(n - len(self.visible_indices) + 1, 0), n)
            )

        with param.discard_events(self):
            # reset the buffers and loaded objects
            self.load_buffer = load_buffer
