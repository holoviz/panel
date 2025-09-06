import os
import pathlib
import time

import pytest

try:
    from playwright.sync_api import expect

    pytestmark = [pytest.mark.ui, pytest.mark.flaky(reruns=3, reason="Writing files can sometimes be unpredictable")]
except ImportError:
    pytestmark = [pytest.mark.skip("playwright not available")]

from panel.io.state import state
from panel.tests.util import serve_component, wait_until

CURPATH = pathlib.Path(__file__).parent

@pytest.mark.parametrize('app', [
    str(CURPATH / 'app.py'),
    str(CURPATH / 'app.md'),
    str(CURPATH / 'app.ipynb'),
], ids=['py', 'md', 'ipynb'])
def test_reload_app_on_touch(page, autoreload, app):
    path = pathlib.Path(app)

    autoreload(path)

    state.cache['num'] = 0
    serve_component(page, path)

    expect(page.locator('.counter')).to_have_text('0')

    state.cache['num'] = 1
    path.touch()

    expect(page.locator('.counter')).to_have_text('1')

def test_reload_app_with_error(page, autoreload, py_file):
    py_file.write("import panel as pn; pn.panel('foo').servable();")
    py_file.close()

    path = pathlib.Path(py_file.name)

    autoreload(path)
    serve_component(page, path)

    expect(page.locator('.markdown')).to_have_text('foo')

    with open(py_file.name, 'w') as f:
        f.write("foo+bar")
        os.fsync(f)

    expect(page.locator('.alert')).to_have_count(1)

def test_reload_app_with_syntax_error(page, autoreload, py_file):
    py_file.write("import panel as pn; pn.panel('foo').servable();")
    py_file.close()

    path = pathlib.Path(py_file.name)

    autoreload(path)
    serve_component(page, path)

    expect(page.locator('.markdown')).to_have_text('foo')

    with open(py_file.name, 'w') as f:
        f.write("foo?bar")
        os.fsync(f)

    expect(page.locator('.alert')).to_have_count(1)

def test_load_app_with_no_content(page, autoreload, py_file):
    py_file.write("import panel as pn; pn.panel('foo')")
    py_file.close()

    path = pathlib.Path(py_file.name)

    serve_component(page, path)

    expect(page.locator('.alert')).to_have_count(1)

def test_reload_app_on_local_module_change(page, autoreload, py_files):
    py_file, module = py_files
    import_name = pathlib.Path(module.name).stem

    # Write and close (on windows the file handle cannot be reopened for reading otherwise)
    module.write("var = 'foo';")
    module.close()
    py_file.write(f"import panel as pn; from {import_name} import var; print(var); pn.panel(var).servable();")
    py_file.close()

    path = pathlib.Path(py_file.name)

    autoreload(path)
    serve_component(page, path, warm=True)

    expect(page.locator('.markdown')).to_have_text('foo')

    time.sleep(0.1)
    with open(module.name, 'w') as f:
        f.write("var = 'bar';")
    pathlib.Path(module.name).touch()
    time.sleep(0.1)

    wait_until(lambda: expect(page.locator('.markdown')).to_have_text('bar'), page)
