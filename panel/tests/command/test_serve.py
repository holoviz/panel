import os
import re
import tempfile
import time

from textwrap import dedent

import pytest
import requests

from panel.tests.util import (
    NBSR, linux_only, run_panel_serve, unix_only, wait_for_port,
    wait_for_regex, write_file,
)


@linux_only
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


@linux_only
def test_autoreload_app_local_module(py_files):
    py_file1, py_file2 = py_files
    app_name = os.path.basename(py_file1.name)[:-3]
    mod_name = os.path.basename(py_file2.name)[:-3]
    app = f"import panel as pn; from {mod_name} import title; pn.Row('# Example').servable(title=title)"
    write_file(app, py_file1.file)
    write_file("title = 'A'", py_file2.file)

    with run_panel_serve(["--port", "0", '--autoreload', py_file1.name]) as p:
        port = wait_for_port(p.stdout)
        r = requests.get(f"http://localhost:{port}/{app_name}")
        assert r.status_code == 200
        assert "<title>A</title>" in r.content.decode('utf-8')

        write_file("title = 'B'", py_file2.file)
        py_file2.file.close()
        time.sleep(1)

        r2 = requests.get(f"http://localhost:{port}/{app_name}")
        assert r2.status_code == 200
        assert "<title>B</title>" in r2.content.decode('utf-8')


@linux_only
def test_serve_admin(py_file):
    app = "import panel as pn; pn.Row('# Example').servable(title='A')"
    write_file(app, py_file.file)

    with run_panel_serve(["--port", "0", '--admin', py_file.name]) as p:
        port = wait_for_port(p.stdout)
        r = requests.get(f"http://localhost:{port}/admin")
        assert r.status_code == 200
        assert "Admin" in r.content.decode('utf-8')

@linux_only
def test_serve_admin_custom_endpoint(py_file):
    app = "import panel as pn; pn.Row('# Example').servable(title='A')"
    write_file(app, py_file.file)

    with run_panel_serve(["--port", "0", '--admin', '--admin-endpoint', 'foo', py_file.name]) as p:
        port = wait_for_port(p.stdout)
        r = requests.get(f"http://localhost:{port}/foo")
        assert r.status_code == 200
        assert "Admin" in r.content.decode('utf-8')
        r2 = requests.get(f"http://localhost:{port}/admin")
        assert r2.status_code == 404

@linux_only
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

@linux_only
def test_serve_markdown():
    md = tempfile.NamedTemporaryFile(mode='w', suffix='.md')
    write_file(md_app, md.file)

    with run_panel_serve(["--port", "0", md.name]) as p:
        port = wait_for_port(p.stdout)
        r = requests.get(f"http://localhost:{port}/")
        assert r.status_code == 200
        assert '<title>My app</title>' in r.content.decode('utf-8')


@unix_only
@pytest.mark.parametrize("arg", ["--warm", "--autoreload"])
def test_serve_num_procs(arg, tmp_path):
    app = "import panel as pn; pn.panel('Hello').servable()"
    py = tmp_path / "app.py"
    py.write_text(app)

    regex = re.compile(r'Starting Bokeh server with process id: (\d+)')
    with run_panel_serve(["--port", "0", py, "--num-procs", 2, arg], cwd=tmp_path) as p:
        pid1, pid2 = wait_for_regex(p.stdout, regex=regex, count=2)
        assert pid1 != pid2


@unix_only
def test_serve_num_procs_setup(tmp_path):
    app = "import panel as pn; pn.panel('Hello').servable()"
    py = tmp_path / "app.py"
    py.write_text(app)

    setup_app = 'import os; print(f"Setup PID {os.getpid()}", flush=True)'
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(setup_app)

    regex = re.compile(r'Setup PID (\d+)')
    with run_panel_serve(["--port", "0", py, "--num-procs", 2, "--setup", setup_py], cwd=tmp_path) as p:
        pid1, pid2 = wait_for_regex(p.stdout, regex=regex, count=2)
        assert pid1 != pid2


def test_serve_setup(tmp_path):
    app = "import panel as pn; pn.panel('Hello').servable()"
    py = tmp_path / "app.py"
    py.write_text(app)

    setup_app = 'print(f"Setup running before", flush=True)'
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(setup_app)

    regex = re.compile('(Setup running before)')
    with run_panel_serve(["--port", "0", py, "--setup", setup_py], cwd=tmp_path) as p:
        _, output = wait_for_regex(p.stdout, regex=regex, return_output=True)
        assert output[0].strip() == "Setup running before"


def test_serve_authorize_callback_exception(tmp_path):
    app = "import panel as pn; pn.panel('Hello').servable()"
    py = tmp_path / "app.py"
    py.write_text(app)

    setup_app = """\
        import panel as pn
        def auth(userinfo):
            raise ValueError("This is an error")
        pn.config.authorize_callback = auth"""
    setup_py = tmp_path / "setup.py"
    setup_py.write_text(dedent(setup_app))

    regex = re.compile('(Authorization callback errored)')
    with run_panel_serve(["--port", "0", py, "--setup", setup_py], cwd=tmp_path) as p:
        nsbr = NBSR(p.stdout)
        port = wait_for_port(nsbr)
        resp = requests.get(f"http://localhost:{port}/")
        wait_for_regex(nsbr, regex=regex)
        assert resp.status_code == 403
