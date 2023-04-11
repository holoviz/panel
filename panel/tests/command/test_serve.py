import contextlib
import os
import platform
import re
import subprocess
import sys
import tempfile

from queue import Empty, Queue
from threading import Thread

import pytest
import requests

unix_only = pytest.mark.skipif(platform.system() != 'Linux', reason="Only supported on Linux")

APP_PATTERN = re.compile(r'Bokeh app running at: http://localhost:(\d+)/')
ON_POSIX = 'posix' in sys.builtin_module_names

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

@unix_only
def test_autoreload_app(py_file):
    app = "import panel as pn; pn.Row('# Example').servable(title='A')"
    app2 = "import panel as pn; pn.Row('# Example 2').servable(title='B')"
    write_file(app, py_file.file)

    app_name = os.path.basename(py_file.name)[:-3]

    with run_panel_serve(["--port", "0", '--autoreload', py_file.name]) as p:
        port = wait_for_port(p.stdout)
        r = requests.get(f"http://localhost:{port}/{app_name}")
        assert r.status_code == 200
        assert "<title>A</title>" in r.content.decode('utf-8')

        write_file(app2, py_file.file)

        r2 = requests.get(f"http://localhost:{port}/{app_name}")
        assert r2.status_code == 200
        assert "<title>B</title>" in r2.content.decode('utf-8')

@unix_only
@pytest.mark.parametrize('relative', [True, False])
def test_custom_html_index(relative, html_file):
    index = '<html><body>Foo</body></html>'
    write_file(index, html_file.file)
    app = "import panel as pn; pn.Row('# Example').servable(title='A')"
    app2 = "import panel as pn; pn.Row('# Example 2').servable(title='B')"
    py1 = tempfile.NamedTemporaryFile(mode='w', suffix='.py')
    py2 = tempfile.NamedTemporaryFile(mode='w', suffix='.py')
    write_file(app, py1.file)
    write_file(app2, py2.file)

    if relative:
        index_path = os.path.basename(html_file.name)
        cwd = os.path.dirname(html_file.name)
    else:
        index_path = html_file.name
        cwd = None

    with run_panel_serve(["--port", "0", "--index", index_path, py1.name, py2.name], cwd=cwd) as p:
        port = wait_for_port(p.stdout)
        r = requests.get(f"http://localhost:{port}/")
        assert r.status_code == 200
        assert r.content.decode('utf-8') == index

md_app = """
# My app

```python
import panel as pn
pn.extension(template='fast')
```

A description

```python
pn.Row('# Example').servable()
```
"""

@unix_only
def test_serve_markdown():
    md = tempfile.NamedTemporaryFile(mode='w', suffix='.md')
    write_file(md_app, md.file)

    with run_panel_serve(["--port", "0", md.name]) as p:
        port = wait_for_port(p.stdout)
        r = requests.get(f"http://localhost:{port}/")
        assert r.status_code == 200
        assert '<title>My app</title>' in r.content.decode('utf-8')
