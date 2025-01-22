"""
Defines callbacks to be executed on a thread or by scheduling it
on a running bokeh server.
"""
import asyncio
import inspect
import logging
import time

from functools import partial

import param

from ..util import edit_readonly, function_name
from .logging import LOG_PERIODIC_END, LOG_PERIODIC_START
from .state import curdoc_locked, set_curdoc, state

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

    callback = param.Callable(allow_refs=False, doc="""
        The callback to execute periodically.""")

    counter = param.Integer(default=0, doc="""
        Counts the number of executions.""")

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
        self._background = params.pop('background', False)
        super().__init__(**params)
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
        try:
            with set_curdoc(self._doc):
                if self.running:
                    self.counter += 1
                    if self.count is not None and self.counter > self.count:
                        self.stop()
                cb = self.callback() if self.running else None
        except Exception:
            cb = None
        if post:
            self._post_callback()
        return cb

    def _post_callback(self):
        cbname = function_name(self.callback)
        if self._doc and self.log:
            _periodic_logger.info(
                LOG_PERIODIC_END, id(self._doc), cbname, self.counter
            )
        if not self._background:
            with edit_readonly(state):
                state._busy_counter -= 1
        if self.timeout is not None:
            dt = (time.time() - self._start_time) * 1000
            if dt > self.timeout:
                self.stop()
        if self.counter == self.count:
            self.stop()

    async def _periodic_callback(self):
        if not self._background:
            with edit_readonly(state):
                state._busy_counter += 1
        cbname = function_name(self.callback)
        if self._doc and self.log:
            _periodic_logger.info(
                LOG_PERIODIC_START, id(self._doc), cbname, self.counter
            )
        is_async = (
            inspect.isasyncgenfunction(self.callback) or
            inspect.iscoroutinefunction(self.callback)
        )
        if state._thread_pool and not is_async:
            future = state._thread_pool.submit(self._exec_callback, True)
            future.add_done_callback(partial(state._handle_future_exception, doc=self._doc))
            return
        try:
            cb = self._exec_callback()
            if inspect.isawaitable(cb):
                if self._doc:
                    with set_curdoc(self._doc):
                        await cb
                else:
                    await cb
        except Exception:
            log.exception('Periodic callback failed.')
            raise
        finally:
            self._post_callback()

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
        if state.curdoc and state.curdoc.session_context and not state._is_pyodide:
            self._doc = state.curdoc
            if state._unblocked(state.curdoc):
                self._cb = self._doc.add_periodic_callback(self._periodic_callback, self.period)
            else:
                self._doc.add_next_tick_callback(self.start)
        else:
            self._cb = asyncio.create_task(
                self._async_repeat(self._periodic_callback)
            )

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
        with param.discard_events(self):
            self.counter = 0
        self._timeout = None
        if self._doc and self._cb and not state._is_pyodide:
            if self._doc._session_context:
                self._doc.callbacks.remove_session_callback(self._cb)
            elif self._cb in self._doc.callbacks.session_callbacks:
                self._doc.callbacks._session_callbacks.remove(self._cb)
        elif self._cb:
            self._cb.cancel()
        self._cb = None
        doc = self._doc or curdoc_locked()
        if doc:
            doc.callbacks.session_destroyed_callbacks = {
                cb for cb in doc.callbacks.session_destroyed_callbacks
                if cb is not self._cleanup
            }
            self._doc = None
