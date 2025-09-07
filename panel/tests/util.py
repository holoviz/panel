from __future__ import annotations

import asyncio
import contextlib
import http.server
import json
import os
import platform
import re
import socket
import subprocess
import sys
import time
import uuid

from functools import partial
from queue import Empty, Queue
from threading import Thread

import numpy as np
import pytest
import requests

from packaging.version import Version

import panel as pn

from panel.io.compile import check_cli_tool
from panel.io.server import serve
from panel.io.state import state

# Ignore tests which are not yet working with Bokeh 3.
# Will begin to fail again when the first rc is released.
pnv = Version(pn.__version__)

not_osx = pytest.mark.skipif(sys.platform == 'darwin', reason="Sometimes fails on OSX")
not_windows = pytest.mark.skipif(sys.platform == 'win32', reason="Does not work on Windows")

try:
    import holoviews as hv
    hv_version: Version | None = Version(hv.__version__)
except Exception:
    hv, hv_version = None, None  # type: ignore
hv_available = pytest.mark.skipif(hv_version is None or hv_version < Version('1.13.0a23'),
                                  reason="requires holoviews")

try:
    import matplotlib as mpl
    mpl.use('Agg')
except Exception:
    mpl = None  # type: ignore
mpl_available = pytest.mark.skipif(mpl is None, reason="requires matplotlib")

try:
    import streamz
except Exception:
    streamz = None  # type: ignore
streamz_available = pytest.mark.skipif(streamz is None, reason="requires streamz")

try:
    import jupyter_bokeh
except Exception:
    jupyter_bokeh = None  # type: ignore
jb_available = pytest.mark.skipif(jupyter_bokeh is None, reason="requires jupyter_bokeh")

APP_PATTERN = re.compile(r'Bokeh app running at: http://localhost:(\d+)/')
ON_POSIX = 'posix' in sys.builtin_module_names

linux_only = pytest.mark.skipif(platform.system() != 'Linux', reason="Only supported on Linux")
unix_only = pytest.mark.skipif(platform.system() == 'Windows', reason="Only supported on unix-like systems")
reverse_proxy_available = pytest.mark.skipif(not check_cli_tool('caddy'), reason="No reverse proxy available")

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

    layoutable.css_classes = ['custom_class']
    if isinstance(layoutable, Alert):
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
    Exercise a test function in a loop until it evaluates to True
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

    if page:
        page.wait_for_load_state('networkidle')

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
                raise TimeoutError(f"{timeout_msg}: {e}") from e
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


async def async_wait_until(fn, page=None, timeout=5000, interval=100):
    """
    Exercise a test function in a loop until it evaluates to True
    or times out.

    The function can either be a simple lambda that returns True or False:
    >>> await async_wait_until(lambda: x.values() == ['x'])

    Or a defined function with an assert:
    >>> async def _()
    >>>    assert x.values() == ['x']
    >>> await async_wait_until(_)

    In a Playwright context test, you should pass the page fixture:
    >>> await async_wait_until(lambda: x.values() == ['x'], page)

    Parameters
    ----------
    fn : callable
        Callback
    page : playwright.async_api.Page, optional
        Playwright page
    timeout : int, optional
        Total timeout in milliseconds, by default 5000
    interval : int, optional
        Waiting interval, by default 100

    Adapted from pytest-qt.
    """
    # Hide this function traceback from the pytest output if the test fails
    __tracebackhide__ = True

    if page:
        await page.wait_for_load_state('networkidle')

    start = time.time()

    def timed_out():
        elapsed = time.time() - start
        elapsed_ms = elapsed * 1000
        return elapsed_ms > timeout

    timeout_msg = f"async_wait_until timed out in {timeout} milliseconds"

    while True:
        try:
            result = fn()
            if asyncio.iscoroutine(result):
                result = await result
        except AssertionError as e:
            if timed_out():
                raise TimeoutError(timeout_msg) from e
            raise e
        else:
            if result not in (None, True, False):
                raise ValueError(
                    "`async_wait_until` callback must return None, True, or "
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
            await page.wait_for_timeout(interval)
        else:
            await asyncio.sleep(interval / 1000)


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


def get_open_ports(n=1):
    sockets,ports = [], []
    for _ in range(n):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        ports.append(s.getsockname()[1])
        sockets.append(s)
    for s in sockets:
        s.close()
    return tuple(ports)


def serve_and_wait(app, page=None, prefix=None, port=None, proxy=None, **kwargs):
    server_id = kwargs.pop('server_id', uuid.uuid4().hex)
    if serve_and_wait.server_implementation == 'fastapi':
        from panel.io.fastapi import serve as serve_app
        port = port or get_open_ports()[0]
    else:
        serve_app = serve
    if proxy:
        kwargs['websocket_origin'] = [f'localhost:{proxy}']
    serve_app(app, port=port or 0, threaded=True, show=False, liveness=True, server_id=server_id, prefix=prefix or "", **kwargs)
    wait_until(lambda: server_id in state._servers, page)
    server = state._servers[server_id][0]
    if proxy:
        port = proxy
    elif serve_and_wait.server_implementation == 'fastapi':
        port = port
    else:
        port = server.port
    wait_for_server(port, prefix=prefix)
    if page:
        page.wait_for_function("document.readyState === 'complete'", timeout=5000)
        page.wait_for_load_state('networkidle')
    return port

serve_and_wait.server_implementation = 'tornado'

def serve_component(page, app, suffix='', wait=True, **kwargs):
    msgs = []
    page.on("console", lambda msg: msgs.append(msg))
    port = serve_and_wait(app, page, **kwargs)
    page.goto(f"http://localhost:{port}{suffix}", wait_until="domcontentloaded")

    if wait:
        wait_until(lambda: any("Websocket connection 0 is now open" in str(msg) for msg in msgs), page, interval=10)

    if page and wait:
        page.wait_for_function("document.readyState === 'complete'", timeout=5000)
        page.wait_for_load_state('networkidle')
    return msgs, port


def serve_and_request(app, suffix="", n=1, port=None, proxy=None, **kwargs):
    port = serve_and_wait(app, port=port, proxy=proxy, **kwargs)
    if proxy:
        port = proxy
    reqs = [r for _ in range(n) if (r := requests.get(f"http://localhost:{port}{suffix}")).ok]
    assert len(reqs) == n, "Not all requests were successful"
    return reqs[0] if n == 1 else reqs


def wait_for_server(port, prefix=None, timeout=3):
    start = time.time()
    prefix = prefix or ""
    if not prefix.endswith('/'):
        prefix += '/'
    url = f"http://localhost:{port}{prefix}liveness"
    while True:
        try:
            if requests.get(url).ok:
                return
        except Exception:
            pass
        time.sleep(0.05)
        if (time.time()-start) > timeout:
            raise RuntimeError(f'{url} did not respond before timeout.')


@contextlib.contextmanager
def run_panel_serve(args, cwd=None):
    cmd = [sys.executable, "-m", "panel", "serve", *map(str, args)]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, cwd=cwd, close_fds=ON_POSIX)
    try:
        yield p
    except BaseException as e:
        p.terminate()
        p.wait()
        print("An error occurred: %s", e)  # noqa: T201
        try:
            out = p.stdout.read().decode()
            print("\n---- subprocess stdout follows ----\n")  # noqa: T201
            print(out)  # noqa: T201
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
        self._q: Queue = Queue()

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

def wait_for_regex(stdout, regex, count=1, return_output=False):
    if isinstance(stdout, NBSR):
        nbsr = stdout
    else:
        nbsr = NBSR(stdout)
    m = None
    output, found = [], []
    for _ in range(30):
        o = nbsr.readline(0.5)
        if not o:
            continue
        out = o.decode('utf-8')
        output.append(out)
        m = regex.search(out)
        if m is not None:
            found.append(m.group(1))
        if len(found) == count:
            break
    if len(found) < count:
        output = '\n    '.join(output)
        pytest.fail(
            "No matching log line in process output, following output "
            f"was captured:\n\n   {output}"
        )
    return (found, output) if return_output else found

def wait_for_port(stdout):
    return int(wait_for_regex(stdout, APP_PATTERN)[0])

def write_file(content, file_obj):
    file_obj.write(content)
    file_obj.flush()
    os.fsync(file_obj)
    file_obj.seek(0)


def http_serve_directory(directory=".", port=0):
    """Spawns an http.server.HTTPServer in a separate thread on the given port.
    The server serves files from the given *directory*. The port listening on
    will automatically be picked by the operating system to avoid race
    conditions when trying to bind to an open port that turns out not to be
    free after all. The hostname is always "localhost".

    Parameters
    -----------
    directory : str, optional
        The directory to server files from. Defaults to the current directory.
    port : int, optional
        Port to serve on, defaults to zero which assigns a random port.

    Returns
    -------
    http.server.HTTPServer
        The HTTP server which is serving files from a separate thread.
        It is not super necessary but you might want to call shutdown() on the
        returned HTTP server object. This will stop the infinite request loop
        running in the thread which in turn will then exit. The reason why this
        is only optional is that the thread in which the server runs is a daemon
        thread which will be terminated when the main thread ends.
        By calling shutdown() you'll get a cleaner shutdown because the socket
        is properly closed.
    str
        The address of the server as a string, e.g. "http://localhost:1234".
    """
    hostname = "localhost"
    directory = os.path.abspath(directory)
    handler = partial(_SimpleRequestHandler, directory=directory)
    httpd = http.server.HTTPServer((hostname, port), handler, False)
    # Block only for 0.5 seconds max
    httpd.timeout = 0.5
    httpd.server_bind()

    address = f"http://{httpd.server_name}:{httpd.server_port}"

    httpd.server_activate()

    def serve_forever(httpd):
        with httpd:
            httpd.serve_forever()

    thread = Thread(target=serve_forever, args=(httpd, ), daemon=True)
    thread.start()

    return httpd, address

class _SimpleRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Same as SimpleHTTPRequestHandler with adjusted logging."""

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Embedder-Policy', 'credentialless')
        http.server.SimpleHTTPRequestHandler.end_headers(self)


@contextlib.contextmanager
def reverse_proxy(port=None, proxy_port=None):
    if port is None and proxy_port is None:
        port, proxy_port = get_open_ports(2)
    elif proxy_port is None:
        proxy_port, = get_open_ports(1)
    elif port is None:
        port, = get_open_ports(1)
    headers = {
        "request": {
            "set": {
                "Connection": ["Upgrade"],
                "Upgrade": ["websocket"]
            }
        }
    }
    route_config = {
        "match": [
            {"path": ["/proxy/*"]},
            {"path_regexp": {
                "name": "proxy_path",
                "pattern": "^/proxy/([^/]+)"
            }}
        ],
        "handle": [
            {"handler": "rewrite", "strip_path_prefix": "/proxy"},
            {"handler": "reverse_proxy", "upstreams": [{"dial": f"localhost:{port}"}]}
        ]
    }
    ws_config = {
        "match": [
            {"path_regexp": {
                "name": "ws_path",
                "pattern": "^/proxy/([^/]+)/ws"
            }}
        ],
        "handle": [
            {"handler": "rewrite", "strip_path_prefix": "/proxy"},
            {"handler": "reverse_proxy", "upstreams": [{"dial": f"localhost:{port}"}], "headers": headers}
        ]
    }
    proxy_config = {
        "listen": [f":{proxy_port}"],
        "routes": [route_config, ws_config]
    }
    config = {
        "admin": {"disabled": True},
        "apps": {"http": {"servers": {"srv0": proxy_config}}},
    }
    process = subprocess.Popen(
        ['caddy', 'run', '--config', '-'],
        stdin=subprocess.PIPE, close_fds=ON_POSIX, text=True
    )
    process.stdin.write(json.dumps(config))
    process.stdin.close()
    try:
        yield port, proxy_port
    finally:
        process.terminate()
        process.wait()
