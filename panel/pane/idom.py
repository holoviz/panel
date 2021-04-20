import sys
import shutil
import asyncio

from functools import partial
from threading import Thread
from queue import Queue as SyncQueue
from packaging.version import Version

from ..io.notebook import push_on_root
from ..io.resources import DIST_DIR, LOCAL_DIST
from ..io.state import state
from ..models import IDOM as _BkIDOM
from .base import PaneBase


_IDOM_MIN_VER = "0.23"
_IDOM_MAX_VER = "0.24"


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

    _updates = True

    _unpack = True

    _bokeh_model = _BkIDOM

    def __init__(self, object=None, **params):
        from idom import __version__ as idom_version
        if Version(_IDOM_MIN_VER) > Version(idom_version) >= Version(_IDOM_MAX_VER):
            raise RuntimeError(
                f"Expected idom>={_IDOM_MIN_VER},<{_IDOM_MAX_VER}, but found {idom_version}"
            )
        super().__init__(object, **params)
        self._idom_loop = None
        self._idom_model = {}
        self.param.watch(self._update_layout, 'object')

    def _update_layout(self, *args):
        self._idom_model = {}
        if self._idom_loop is None:
            return
        self._setup()

    def _setup(self):
        if self.object is None:
            return
        from idom.core.component import Component
        from idom.core.layout import Layout
        if isinstance(self.object, Layout):
            self._idom_layout = self.object
        elif isinstance(self.object, Component):
            self._idom_layout = Layout(self.object)
        else:
            self._idom_layout = Layout(self.object())
        self._idom_loop = _spawn_threaded_event_loop(self._idom_layout_render_loop())

    def _get_model(self, doc, root=None, parent=None, comm=None):
        from idom.core.layout import LayoutUpdate
        from idom.config import IDOM_CLIENT_IMPORT_SOURCE_URL

        # let the client determine import source location
        IDOM_CLIENT_IMPORT_SOURCE_URL.set("./")

        if comm:
            url = '/panel_dist/idom/build'
        else:
            url = '/'+LOCAL_DIST+'idom/build'

        if self._idom_loop is None:
            self._setup()

        update = LayoutUpdate.create_from({}, self._idom_model)
        props = self._init_params()
        model = self._bokeh_model(
            event=[update.path, update.changes], importSourceUrl=url, **props
        )
        if root is None:
            root = model
        self._link_props(model, ['msg'], doc, root, comm)

        if root is None:
            root = model
        self._models[root.ref['id']] = (model, parent)
        return model

    def _cleanup(self, root):
        super()._cleanup(root)
        if not self._models:
            # Clean up loop when no views are shown
            try:
                self._idom_loop.stop()
            finally:
                self._idom_loop = None
                self._idom_layout = None

    def _process_property_change(self, msg):
        if msg['msg'] is None:
            return {}
        from idom.core.layout import LayoutEvent
        dispatch = self._idom_layout.dispatch(LayoutEvent(**msg['msg']))
        asyncio.run_coroutine_threadsafe(dispatch, loop=self._idom_loop)
        for ref, (m, _) in self._models.items():
            m.msg = None
            push_on_root(ref)
        return {}

    async def _idom_layout_render_loop(self):
        async with self._idom_layout:
            while True:
                update = await self._idom_layout.render()
                self._idom_model = update.apply_to(self._idom_model)
                for ref, (model, _) in self._models.items():
                    doc = state._views[ref][2]
                    if doc.session_context:
                        doc.add_next_tick_callback(partial(model.update, event=update))
                    else:
                        model.event = update
                        push_on_root(ref)

    @classmethod
    def applies(self, object):
        if object is None:
            return None
        elif 'idom' in sys.modules:
            from idom.core.component import Component
            from idom.core.layout import Layout
            if isinstance(object, (Component, Layout)):
                return 0.8
            elif callable(object):
                return None
        return False

    @classmethod
    def install(cls, packages, ignore_installed=False, fallback=None):
        """
        Installs specified packages into application directory.

        Arguments
        ---------
        packages: list or tuple
          The packages to install from npm
        ignored_installed: boolean
          Whether to ignore if the package was previously installed.
        fallback: str or idom.component
          The fallback to display while the component is loading
        """
        import idom
        from idom.config import IDOM_CLIENT_BUILD_DIR
        idom_dist_dir = DIST_DIR / "idom"
        idom_build_dir = idom_dist_dir / "build"
        if not idom_build_dir.is_dir():
            idom_build_dir.mkdir()
            shutil.copyfile(idom_dist_dir / 'package.json', idom_build_dir / 'package.json')
        if IDOM_CLIENT_BUILD_DIR.get() != idom_build_dir:
            IDOM_CLIENT_BUILD_DIR.set(idom_build_dir)
            # just in case packages were already installed but the build hasn't been
            # copied over to DIST_DIR yet.
            ignore_installed = True
        return idom.install(packages, ignore_installed, fallback)

    @classmethod
    def use_param(cls, parameter):
        """
        Links parameter to some IDOM state value and returns the linked
        value.

        Arguments
        ---------
        parameter: param.Parameter
          The parameter to link to a idom state value.

        Returns
        -------
        An idom state value which is updated when the parameter changes.
        """
        import idom
        from ..depends import param_value_if_widget
        parameter = param_value_if_widget(parameter)
        initial = getattr(parameter.owner, parameter.name)
        value, set_value = idom.hooks.use_state(initial)
        def update(event):
            set_value(event.new)
        parameter.owner.param.watch(update, parameter.name)
        return value
