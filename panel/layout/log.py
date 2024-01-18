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

    loaded_entries = param.Integer(default=20, doc="""
        Minimum number of visible log entries shown initially.""")

    load_buffer = param.Integer(default=20, bounds=(0, None), doc="""
        Number of log entries to load each time the user scrolls
        past the scroll_load_threshold.""")

    scroll = param.Boolean(default=True, doc="""
        Whether to add scrollbars if the content overflows the size
        of the container.""")

    view_latest = param.Boolean(default=True, doc="""
        Whether to scroll to the latest object on init. If not
        enabled the view will be on the first object.""")

    visible_objects = param.List(doc="""
        Indices of visible objects.""")

    _bokeh_model: ClassVar[Type[Model]] = PnLog

    _direction = 'vertical'

    _rename: ClassVar[Mapping[str, str | None]] = {
        'objects': 'children', 'load_buffer': None, 'loaded_entries': None
    }

    def __init__(self, *objects, **params):
        super().__init__(*objects, **params)
        self._last_synced = None

    @param.depends("visible_objects", watch=True)
    def _trigger_get_objects(self):
        # visible start, end / synced start, end
        vs, ve = min(self.visible_objects), max(self.visible_objects)
        ss, se = min(self._last_synced), max(self._last_synced)
        half_buffer = self.load_buffer // 2
        if (vs - ss) < half_buffer or (se - ve) < half_buffer:
            self.param.trigger("objects")

    @property
    def _synced_indices(self):
        n = len(self.objects)
        if self.visible_objects:
            return list(range(
                max(min(self.visible_objects)-self.load_buffer, 0),
                min(max(self.visible_objects)+self.load_buffer, n)
            ))
        elif self.view_latest:
            return list(range(max(n-self.loaded_entries-self.load_buffer, 0), n))
        else:
            return list(range(min(self.loaded_entries+self.load_buffer, n)))

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
            msg['visible_objects'] = [offset+i for i in sorted(indexes)]
        return super()._process_property_change(msg)

    def _process_param_change(self, msg):
        msg.pop('visible_objects', None)
        return super()._process_param_change(msg)

    def _get_objects(
        self, model: Model, old_objects: List[Viewable], doc: Document,
        root: Model, comm: Optional[Comm] = None
    ):
        from ..pane.base import RerenderError, panel
        new_models, old_models = [], []
        self._last_synced = synced = self._synced_indices
        for i, pane in enumerate(self.objects):
            if i not in synced:
                continue
            pane = panel(pane)
            self.objects[i] = pane

        for obj in old_objects:
            if obj not in self.objects:
                obj._cleanup(root)

        current_objects = list(self.objects)
        ref = root.ref['id']
        for i, pane in enumerate(current_objects):
            if i not in synced:
                continue
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
        n = len(self.objects)
        # need to get it all the way to the bottom rather
        # than the center of the buffer zone
        load_buffer = self.load_buffer
        loaded_entries = self.loaded_entries
        with param.discard_events(self):
            self.load_buffer = self.loaded_entries = 0
        self.visible_objects = list(range(max(n - 2, 0), n))
        with param.discard_events(self):
            # reset the buffers and loaded entries
            self.load_buffer = load_buffer
            self.loaded_entries = loaded_entries

        self._trigger_get_objects()
