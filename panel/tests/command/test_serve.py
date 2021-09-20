import contextlib
import os
import re
import subprocess
import sys

import pytest
import requests

from queue import Empty, Queue
from threading import Thread

not_windows = pytest.mark.skipif(sys.platform == 'win32', reason="Does not work on Windows")


@contextlib.contextmanager
def run_panel_serve(args):
    cmd = [sys.executable, "-m", "panel", "serve"] + args
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
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

            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    break

        self._t = Thread(target = _populateQueue,
                args = (self._s, self._q))
        self._t.daemon = True
        self._t.start() #start collecting lines from the stream

    def readline(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None,
                    timeout = timeout)
        except Empty:
            return None


@not_windows
def test_autoreload_app(py_file):
    app = "import panel as pn; pn.Row('# Example').servable(title='A')"
    app2 = "import panel as pn; pn.Row('# Example 2').servable(title='B')"
    py_file.file.write(app)
    py_file.file.flush()
    os.fsync(py_file.file)

    py_file.file.seek(0)

    app_name = os.path.basename(py_file.name)[:-3]
    pat = re.compile(r'Bokeh app running at: http://localhost:(\d+)/' + app_name)
    m = None

    with run_panel_serve(["--port", "0", '--autoreload', py_file.name]) as p:
        nbsr = NBSR(p.stdout)
        m = None
        for i in range(20):
            o = nbsr.readline(0.5)
            if not o:
                continue
            m = pat.search(o.decode())
            if m is not None:
                break
        if m is None:
            pytest.fail("no matching log line in process output")
        port = int(m.group(1))

        r = requests.get(f"http://localhost:{port}/{app_name}")
        assert r.status_code == 200
        assert "<title>A</title>" in r.content.decode('utf-8')

        py_file.file.write(app2)
        py_file.file.flush()
        os.fsync(py_file.file)

        r2 = requests.get(f"http://localhost:{port}/{app_name}")
        assert r2.status_code == 200
        assert "<title>B</title>" in r2.content.decode('utf-8')

