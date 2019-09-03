"""
Defines callbacks to be executed on a thread or by scheduling it
on a running bokeh server.
"""
from __future__ import absolute_import, division, unicode_literals


import time
import param

from bokeh.io import curdoc as _curdoc


class PeriodicCallback(param.Parameterized):
    """
    Periodic encapsulates a periodic callback which will run both
    in tornado based notebook environments and on bokeh server. By
    default the callback will run until the stop method is called,
    but count and timeout values can be set to limit the number of
    executions or the maximum length of time for which the callback
    will run.
    """

    callback = param.Callable(doc="""
       The callback to execute periodically.""")

    count = param.Integer(default=None, doc="""
        Number of times the callback will be executed, by default
        this is unlimited.""")

    period = param.Integer(default=500, doc="""
        Period in milliseconds at which the callback is executed.""")

    timeout = param.Integer(default=None, doc="""
        Timeout in seconds from the start time at which the callback
        expires""")

    def __init__(self, **params):
        super(PeriodicCallback, self).__init__(**params)
        self._counter = 0
        self._start_time = None
        self._timeout = None
        self._cb = None
        self._doc = None

    def start(self):
        if self._cb is not None:
            raise RuntimeError('Periodic callback has already started.')
        self._start_time = time.time()
        if _curdoc().session_context:
            self._doc = _curdoc()
            self._cb = self._doc.add_periodic_callback(self._periodic_callback, self.period)
        else:
            from tornado.ioloop import PeriodicCallback
            self._cb = PeriodicCallback(self._periodic_callback, self.period)
            self._cb.start()

    @param.depends('period', watch=True)
    def _update_period(self):
        if self._cb:
            self.stop()
            self.start()

    def _periodic_callback(self):
        self.callback()
        self._counter += 1
        if self._timeout is not None:
            dt = (time.time() - self._start_time)
            if dt > self._timeout:
                self.stop()
        if self._counter == self.count:
            self.stop()

    def stop(self):
        self._counter = 0
        self._timeout = None
        if self._doc:
            self._doc.remove_periodic_callback(self._cb)
        else:
            self._cb.stop()
        self._cb = None

