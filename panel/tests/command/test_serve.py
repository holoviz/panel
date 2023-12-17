import os
import tempfile

import pytest
import requests

from panel.tests.util import (
    run_panel_serve, unix_only, wait_for_port, write_file,
)


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
def test_serve_admin(py_file):
    app = "import panel as pn; pn.Row('# Example').servable(title='A')"
    write_file(app, py_file.file)

    with run_panel_serve(["--port", "0", '--admin', py_file.name]) as p:
        port = wait_for_port(p.stdout)
        r = requests.get(f"http://localhost:{port}/admin")
        assert r.status_code == 200
        assert "Admin" in r.content.decode('utf-8')

@unix_only
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
