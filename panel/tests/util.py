import contextlib
import os
import platform
import re
import subprocess
import sys
import time
import warnings

from queue import Empty, Queue
from threading import Thread

import numpy as np
import pytest

from packaging.version import Version

import panel as pn

from panel.io.server import serve

# Ignore tests which are not yet working with Bokeh 3.
# Will begin to fail again when the first rc is released.
pnv = Version(pn.__version__)

try:
    import holoviews as hv
    hv_version = Version(hv.__version__)
except Exception:
    hv, hv_version = None, None
hv_available = pytest.mark.skipif(hv is None or hv_version < Version('1.13.0a23'),
                                  reason="requires holoviews")

try:
    import matplotlib as mpl
    mpl.use('Agg')
except Exception:
    mpl = None
mpl_available = pytest.mark.skipif(mpl is None, reason="requires matplotlib")

try:
    import streamz
except Exception:
    streamz = None
streamz_available = pytest.mark.skipif(streamz is None, reason="requires streamz")

try:
    import jupyter_bokeh
except Exception:
    jupyter_bokeh = None
jb_available = pytest.mark.skipif(jupyter_bokeh is None, reason="requires jupyter_bokeh")

APP_PATTERN = re.compile(r'Bokeh app running at: http://localhost:(\d+)/')
ON_POSIX = 'posix' in sys.builtin_module_names

unix_only = pytest.mark.skipif(platform.system() != 'Linux', reason="Only supported on Linux")

from panel.pane.alert import Alert
from panel.pane.markup import Markdown
from panel.widgets.button import _ButtonBase


def mpl_figure():
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(np.random.rand(10, 2))
    plt.close(fig)
    return fig


def check_layoutable_properties(layoutable, model):
    layoutable.styles = {"background": '#fffff0'}
    assert model.styles["background"] == '#fffff0'

    # Is deprecated, but we still support it for now.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        layoutable.background = '#ffffff'
    assert model.styles["background"] == '#ffffff'

    layoutable.css_classes = ['custom_class']
    if isinstance(layoutable, Alert):
        print(model.css_classes)
        assert model.css_classes == ['markdown', 'custom_class', 'alert', 'alert-primary']
    elif isinstance(layoutable, Markdown):
        assert model.css_classes == ['markdown', 'custom_class']
    elif isinstance(layoutable, _ButtonBase):
        assert model.css_classes == ['solid', 'custom_class']
    else:
        assert model.css_classes == ['custom_class']

    layoutable.width = 500
    assert model.width == 500

    layoutable.height = 450
    assert model.height == 450

    layoutable.min_height = 300
    assert model.min_height == 300

    layoutable.min_width = 250
    assert model.min_width == 250

    layoutable.max_height = 600
    assert model.max_height == 600

    layoutable.max_width = 550
    assert model.max_width == 550

    layoutable.margin = 10
    assert model.margin == 10

    layoutable.sizing_mode = 'stretch_width'
    assert model.sizing_mode == 'stretch_width'

    layoutable.width_policy = 'max'
    assert model.width_policy == 'max'

    layoutable.height_policy = 'min'
    assert model.height_policy == 'min'


def wait_until(fn, page=None, timeout=5000, interval=100):
    """
    Exercice a test function in a loop until it evaluates to True
    or times out.

    The function can either be a simple lambda that returns True or False:
    >>> wait_until(lambda: x.values() == ['x'])

    Or a defined function with an assert:
    >>> def _()
    >>>    assert x.values() == ['x']
    >>> wait_until(_)

    In a Playwright context test you should pass the page fixture:
    >>> wait_until(lambda: x.values() == ['x'], page)

    Parameters
    ----------
    fn : callable
        Callback
    page : playwright.sync_api.Page, optional
        Playwright page
    timeout : int, optional
        Total timeout in milliseconds, by default 5000
    interval : int, optional
        Waiting interval, by default 100

    Adapted from pytest-qt.
    """
    # Hide this function traceback from the pytest output if the test fails
    __tracebackhide__ = True

    start = time.time()

    def timed_out():
        elapsed = time.time() - start
        elapsed_ms = elapsed * 1000
        return elapsed_ms > timeout

    timeout_msg = f"wait_until timed out in {timeout} milliseconds"

    while True:
        try:
            result = fn()
        except AssertionError as e:
            if timed_out():
                raise TimeoutError(timeout_msg) from e
        else:
            if result not in (None, True, False):
                raise ValueError(
                    "`wait_until` callback must return None, True or "
                    f"False, returned {result!r}"
                )
            # None is returned when the function has an assert
            if result is None:
                return
            # When the function returns True or False
            if result:
                return
            if timed_out():
                raise TimeoutError(timeout_msg)
        if page:
            # Playwright recommends against using time.sleep
            # https://playwright.dev/python/docs/intro#timesleep-leads-to-outdated-state
            page.wait_for_timeout(interval)
        else:
            time.sleep(interval / 1000)


def get_ctrl_modifier():
    """
    Get the CTRL modifier on the current platform.
    """
    if sys.platform in ['linux', 'win32']:
        return 'Control'
    elif sys.platform == 'darwin':
        return 'Meta'
    else:
        raise ValueError(f'No control modifier defined for platform {sys.platform}')


def serve_panel_widget(page, port, pn_widget, sleep=0.5):
    serve(pn_widget, port=port, threaded=True, show=False)
    time.sleep(sleep)
    page.goto(f"http://localhost:{port}")


@contextlib.contextmanager
def run_panel_serve(args, cwd=None):
    cmd = [sys.executable, "-m", "panel", "serve"] + args
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, cwd=cwd, close_fds=ON_POSIX)
    try:
        yield p
    except Exception as e:
        p.terminate()
        p.wait()
        print("An error occurred: %s", e)
        try:
            out = p.stdout.read().decode()
            print("\n---- subprocess stdout follows ----\n")
            print(out)
        except Exception:
            pass
        raise
    else:
        p.terminate()
        p.wait()


class NBSR:
    def __init__(self, stream) -> None:
        '''
        NonBlockingStreamReader

        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''

        self._s = stream
        self._q = Queue()

        def _populateQueue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'queue'.
            '''
            for line in iter(stream.readline, b''):
                queue.put(line)
            stream.close()

        self._t = Thread(target = _populateQueue,
                args = (self._s, self._q))
        self._t.daemon = True
        self._t.start() #start collecting lines from the stream

    def readline(self, timeout=None):
        try:
            return self._q.get(
                block=timeout is not None,
                timeout=timeout
            )
        except Empty:
            return None

def wait_for_port(stdout):
    nbsr = NBSR(stdout)
    m = None
    for i in range(20):
        o = nbsr.readline(0.5)
        if not o:
            continue
        m = APP_PATTERN.search(o.decode('utf-8'))
        if m is not None:
            break
    if m is None:
        pytest.fail("no matching log line in process output")
    return int(m.group(1))

def write_file(content, file_obj):
    file_obj.write(content)
    file_obj.flush()
    os.fsync(file_obj)
    file_obj.seek(0)
