"""
Defines callbacks to be executed on a thread or by scheduling it
on a running bokeh server.
"""
import asyncio
import inspect
import logging
import time

import param

from bokeh.io import curdoc as _curdoc

from ..util import edit_readonly, function_name
from .logging import LOG_PERIODIC_START, LOG_PERIODIC_END

from .state import state

log = logging.getLogger('panel.callbacks')
_periodic_logger = logging.getLogger(f'{__name__}.PeriodicCallback')

class PeriodicCallback(param.Parameterized):
    """
    Periodic encapsulates a periodic callback which will run both
    in tornado based notebook environments and on bokeh server. By
    default the callback will run until the stop method is called,
    but count and timeout values can be set to limit the number of
    executions or the maximum length of time for which the callback
    will run. The callback may also be started and stopped by setting
    the running parameter to True or False respectively.
    """

    callback = param.Callable(doc="""
        The callback to execute periodically.""")

    count = param.Integer(default=None, doc="""
        Number of times the callback will be executed, by default
        this is unlimited.""")

    log = param.Boolean(default=True, doc="""
        Whether the periodic callback should log its actions.""")

    period = param.Integer(default=500, doc="""
        Period in milliseconds at which the callback is executed.""")

    timeout = param.Integer(default=None, doc="""
        Timeout in milliseconds from the start time at which the callback
        expires.""")

    running = param.Boolean(default=False, doc="""
        Toggles whether the periodic callback is currently running.""")

    def __init__(self, **params):
        super().__init__(**params)
        self._counter = 0
        self._start_time = None
        self._cb = None
        self._updating = False
        self._doc = None

    @param.depends('running', watch=True)
    def _start(self):
        if not self.running or self._updating:
            return
        self.start()

    @param.depends('running', watch=True)
    def _stop(self):
        if self.running or self._updating:
            return
        self.stop()

    @param.depends('period', watch=True)
    def _update_period(self):
        if self._cb:
            self.stop()
            self.start()

    def _exec_callback(self, post=False):
        from .state import set_curdoc
        try:
            with set_curdoc(self._doc):
                cb = self.callback()
        except Exception:
            cb = None
        if post:
            self._post_callback()
        return cb

    def _post_callback(self):
        cbname = function_name(self.callback)
        if self._doc and self.log:
            _periodic_logger.info(
                LOG_PERIODIC_END, id(self._doc), cbname, self._counter
            )
        with edit_readonly(state):
            state.busy = False
        self._counter += 1
        if self.timeout is not None:
            dt = (time.time() - self._start_time) * 1000
            if dt > self.timeout:
                self.stop()
        if self._counter == self.count:
            self.stop()

    async def _periodic_callback(self):
        with edit_readonly(state):
            state.busy = True
        cbname = function_name(self.callback)
        if self._doc and self.log:
            _periodic_logger.info(
                LOG_PERIODIC_START, id(self._doc), cbname, self._counter
            )
        is_async = (
            inspect.isasyncgenfunction(self.callback) or
            inspect.iscoroutinefunction(self.callback)
        )
        if state._thread_pool and not is_async:
            state._thread_pool.submit(self._exec_callback, True)
            return
        try:
            cb = self._exec_callback()
            if inspect.isawaitable(cb):
                await cb
        except Exception:
            log.exception('Periodic callback failed.')
            raise
        finally:
            self._post_callback()

    @property
    def counter(self):
        """
        Returns the execution count of the periodic callback.
        """
        return self._counter

    async def _async_repeat(self, func):
        """
        Run func every interval seconds.

        If func has not finished before *interval*, will run again
        immediately when the previous iteration finished.
        """
        while True:
            start = time.monotonic()
            await func()
            timeout = (self.period/1000.) - (time.monotonic()-start)
            if timeout > 0:
                await asyncio.sleep(timeout)

    def _cleanup(self, session_context):
        self.stop()

    def start(self):
        """
        Starts running the periodic callback.
        """
        if self._cb is not None:
            raise RuntimeError('Periodic callback has already started.')
        if not self.running:
            try:
                self._updating = True
                self.running = True
            finally:
                self._updating = False
        self._start_time = time.time()
        if state._is_pyodide:
            self._cb = asyncio.create_task(
                self._async_repeat(self._periodic_callback)
            )
        elif state.curdoc:
            self._doc = state.curdoc
            self._cb = self._doc.add_periodic_callback(self._periodic_callback, self.period)
        else:
            from tornado.ioloop import PeriodicCallback
            self._cb = PeriodicCallback(lambda: asyncio.create_task(self._periodic_callback()), self.period)
            self._cb.start()

    def stop(self):
        """
        Stops running the periodic callback.
        """
        if self.running:
            try:
                self._updating = True
                self.running = False
            finally:
                self._updating = False
        self._counter = 0
        self._timeout = None
        if state._is_pyodide:
            self._cb.cancel()
        elif self._doc:
            if self._doc._session_context:
                self._doc.callbacks.remove_session_callback(self._cb)
            else:
                self._doc.callbacks._session_callbacks.remove(self._cb)
        elif self._cb:
            self._cb.stop()
        self._cb = None
        doc = self._doc or _curdoc()
        if doc:
            doc.callbacks.session_destroyed_callbacks = {
                cb for cb in doc.callbacks.session_destroyed_callbacks
                if cb is not self._cleanup
            }
            self._doc = None
