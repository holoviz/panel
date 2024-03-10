import pathlib
import time

import pytest

try:
    from playwright.sync_api import expect

    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip("playwright not available")

from panel.io.state import state
from panel.tests.util import serve_component

CURPATH = pathlib.Path(__file__).parent

@pytest.mark.parametrize('app', [
    str(CURPATH / 'app.py'),
    str(CURPATH / 'app.md'),
    str(CURPATH / 'app.ipynb'),
])
def test_reload_app_on_touch(page, autoreload, server_id, app):
    if 'num' in state.cache:
        del state.cache['num']

    path = pathlib.Path(app)

    autoreload(path)

    serve_component(page, path, server_id=server_id)

    expect(page.locator('.counter')).to_have_text('0')

    path.touch()

    expect(page.locator('.counter')).to_have_text('1')


def test_reload_app_with_error(page, autoreload, server_id, py_file):
    py_file.write("import panel as pn; pn.panel('foo').servable();")
    py_file.flush()
    time.sleep(0.1) # Give the filesystem time to execute the write

    path = pathlib.Path(py_file.name)

    autoreload(path)
    serve_component(page, path, server_id=server_id)

    expect(page.locator('.markdown')).to_have_text('foo')

    py_file.write("foo+bar")
    py_file.flush()
    path.touch()

    expect(page.locator('.alert')).to_have_count(1)
