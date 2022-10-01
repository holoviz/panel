import pathlib
import tempfile
import time

from http.client import HTTPConnection
from subprocess import PIPE, Popen

import pytest

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui

from panel.config import config
from panel.io.convert import convert_apps

button_app = """
import panel as pn
button = pn.widgets.Button()
pn.Row(button, pn.bind(lambda c: c, button.param.clicks)).servable();
"""

slider_app = """
import panel as pn
slider = pn.widgets.FloatSlider()
pn.Row(slider, pn.bind(lambda v: v, slider)).servable();
"""

location_app = """
import panel as pn
slider = pn.widgets.FloatSlider(start=0, end=10)
pn.state.location.sync(slider, ['value'])
pn.Row(slider, pn.bind(lambda v: v, slider)).servable();
"""


def write_app(app):
    """
    Writes app to temporary file and returns path.
    """
    nf = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    nf.write(app)
    nf.flush()
    return nf

@pytest.fixture(scope="module")
def start_server():
    _PROCESSES = []

    def start(path):
        process = Popen(
            ["python", "-m", "http.server", "8123", "--directory", str(path.parent)], stdout=PIPE
        )
        retries = 5
        while retries > 0:
            conn = HTTPConnection("localhost:8123")
            try:
                conn.request("HEAD", str(path.name))
                response = conn.getresponse()
                if response is not None:
                    _PROCESSES.append(process)
                    break
            except ConnectionRefusedError:
                time.sleep(1)
                retries -= 1

        if not retries:
            raise RuntimeError("Failed to start http server")
    yield start
    for process in _PROCESSES:
        process.terminate()
        process.wait()


@pytest.mark.parametrize('runtime', ['pyodide', 'pyscript', 'pyodide-worker'])
def test_pyodide_test_convert_button_app(page, runtime, start_server):
    nf = write_app(button_app)
    app_path = pathlib.Path(nf.name)
    start_server(app_path)

    convert_apps([app_path], app_path.parent, runtime=runtime, build_pwa=False, build_index=False, prerender=False)

    page.goto(f"http://localhost:8123/{app_path.name[:-3]}.html")

    cls = f'bk pn-loading {config.loading_spinner}'
    expect(page.locator('body')).to_have_class(cls)
    expect(page.locator('body')).not_to_have_class(cls, timeout=30000)

    expect(page.locator(".bk.bk-clearfix")).to_have_text('0')

    page.click('.bk.bk-btn')

    expect(page.locator(".bk.bk-clearfix")).to_have_text('1')


@pytest.mark.parametrize('runtime', ['pyodide', 'pyscript', 'pyodide-worker'])
def test_pyodide_test_convert_slider_app(page, runtime, start_server):
    nf = write_app(slider_app)
    app_path = pathlib.Path(nf.name)
    start_server(app_path)

    convert_apps([app_path], app_path.parent, runtime=runtime, build_pwa=False, build_index=False, prerender=False)

    page.goto(f"http://localhost:8123/{app_path.name[:-3]}.html")

    cls = f'bk pn-loading {config.loading_spinner}'
    expect(page.locator('body')).to_have_class(cls)
    expect(page.locator('body')).not_to_have_class(cls, timeout=30000)

    expect(page.locator(".bk.bk-clearfix")).to_have_text('0.0')

    page.click('.noUi-handle')
    page.keyboard.press('ArrowRight')

    expect(page.locator(".bk.bk-clearfix")).to_have_text('0.1')


@pytest.mark.parametrize('runtime', ['pyodide-worker'])
def test_pyodide_test_convert_location_app(page, runtime, start_server):
    nf = write_app(location_app)
    app_path = pathlib.Path(nf.name)
    start_server(app_path)

    convert_apps([app_path], app_path.parent, runtime=runtime, build_pwa=False, build_index=False, prerender=False)

    app_url = f"http://localhost:8123/{app_path.name[:-3]}.html"
    page.goto(f"{app_url}?value=3.14")

    cls = f'bk pn-loading {config.loading_spinner}'
    expect(page.locator('body')).to_have_class(cls)
    expect(page.locator('body')).not_to_have_class(cls, timeout=30000)

    expect(page.locator(".bk.bk-clearfix")).to_have_text('3.14')

    page.click('.noUi-handle')
    page.keyboard.press('ArrowRight')

    expect(page.locator(".bk.bk-clearfix")).to_have_text('3.2')

    assert page.url == f"{app_url}?value=3.2"
