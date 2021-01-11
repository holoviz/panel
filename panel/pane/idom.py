import sys
import asyncio

from functools import partial
from threading import Thread
from queue import Queue as SyncQueue

from ..io.notebook import push_on_root
from ..io.state import state
from ..models import IDOM as _BkIDOM
from .base import PaneBase


def _spawn_threaded_event_loop(coro):
    loop_q = SyncQueue()

    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop_q.put(loop)
        loop.run_until_complete(coro)

    thread = Thread(target=run_in_thread, daemon=True)
    thread.start()

    return loop_q.get()


class IDOM(PaneBase):
    
    priority = None
    
    _bokeh_model = _BkIDOM
   
    def __init__(self, object=None, **params):
        super().__init__(object, **params)
        self._update_layout()
        self._idom_loop = _spawn_threaded_event_loop(self._idom_layout_render_loop())
        self.param.watch(self._update_layout, 'object')

    def _update_layout(self, *args):
        from idom.core.layout import Layout 
        from idom.core.element import Element
        self._idom_model = {}
        if isinstance(self.object, Layout):
            self._idom_layout = self.object
        elif isinstance(self.object, Element):
            self._idom_layout = Layout(self.object)
        else:
            self._idom_layout = Layout(self.object())
        
    @classmethod
    def applies(self, object):
        from idom.core.layout import Layout 
        from idom.core.element import Element
        if 'idom' in sys.modules:
            if isinstance(object, (Layout, Element)):
                return 0.8
            elif callable(object) and isinstance(object(), (Layout, Element)):
                return 0.8
        return False

    def _get_model(self, doc, root=None, parent=None, comm=None):
        from idom.core.layout import LayoutUpdate

        update = LayoutUpdate.create_from({}, self._idom_model)
        model = self._bokeh_model(event={'data': update._asdict()})
        self._link_props(model, ['msg'], doc, root, comm)

        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model
    
    def _process_property_change(self, msg):
        from idom.core.layout import LayoutEvent
        #print(msg)
        dispatch = self._idom_layout.dispatch(LayoutEvent(**msg['msg']))
        asyncio.run_coroutine_threadsafe(dispatch, loop=self._idom_loop)
        return {}
    
    async def _idom_layout_render_loop(self):
        async with self._idom_layout:
            while True:
                update = await self._idom_layout.render()
                self._idom_model = update.apply_to(self._idom_model)
                event = {"data": update._asdict()}
                for ref, (model, _) in self._models.items():
                    doc = state._views[ref][2]
                    if doc.session_context:
                        doc.add_next_tick_callback(partial(model.update, event=event))
                    else:
                        model.event = event
                        push_on_root(ref)
    
