import glob
import os
import pathlib
import shutil
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
from panel.io.convert import BOKEH_LOCAL_WHL, PANEL_LOCAL_WHL, convert_apps

if not (PANEL_LOCAL_WHL.is_file() and BOKEH_LOCAL_WHL.is_file()):
    pytest.skip(
        "Skipped because pyodide wheels are not available for current "
        "version. Build wheels for pyodide using `python scripts/build_pyodide_wheels.py`.",
        allow_module_level=True
    )

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

tabulator_app = """
import panel as pn
import pandas as pd
tabulator = pn.widgets.Tabulator(pd._testing.makeMixedDataFrame())

def on_click(e):
    tabulator.theme = 'fast'

button = pn.widgets.Button()
button.on_click(on_click)

pn.Row(button, tabulator).servable();
"""

csv_app = """
import pandas as pd
import panel as pn

df = pd.read_csv('https://raw.githubusercontent.com/holoviz/panel/master/examples/assets/occupancy.csv')
tabulator = pn.widgets.Tabulator(df)

tabulator.servable()
"""

png_app = """
import panel as pn

png = pn.pane.PNG('https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png', width=200)

png.servable()
"""

error_app = """
import panel as pn

button = pn.widgets.Button()

button.servable()

if pn.state._is_pyodide:
    raise RuntimeError('This app is broken')
"""


def write_app(app):
    """
    Writes app to temporary file and returns path.
    """
    nf = tempfile.NamedTemporaryFile(mode='w', suffix='.py', encoding='utf-8', delete=False)
    nf.write(app)
    nf.flush()
    dest = pathlib.Path(nf.name).parent
    try:
        shutil.copy(PANEL_LOCAL_WHL, dest / PANEL_LOCAL_WHL.name)
    except shutil.SameFileError:
        pass
    try:
        shutil.copy(BOKEH_LOCAL_WHL, dest / BOKEH_LOCAL_WHL.name)
    except shutil.SameFileError:
        pass
    return nf

@pytest.fixture(scope="module")
def launch_app():
    _PROCESSES = []

    def start(code):
        nf = write_app(code)
        app_path = pathlib.Path(nf.name)
        process = Popen(
            ["python", "-m", "http.server", "8123", "--directory", str(app_path.parent)], stdout=PIPE
        )
        retries = 5
        while retries > 0:
            conn = HTTPConnection("localhost:8123")
            try:
                conn.request("HEAD", str(app_path.name))
                response = conn.getresponse()
                if response is not None:
                    _PROCESSES.append((process, nf.name))
                    break
            except ConnectionRefusedError:
                time.sleep(1)
                retries -= 1

        if not retries:
            raise RuntimeError("Failed to start http server")
        return app_path
    yield start
    for process, name in _PROCESSES:
        process.terminate()
        process.wait()
        for f in glob.glob(f'{name[:-3]}*'):
            os.remove(f)


def wait_for_app(launch_app, app, page, runtime, wait=True, **kwargs):
    app_path = launch_app(app)

    convert_apps(
        [app_path], app_path.parent, runtime=runtime, build_pwa=False,
        prerender=False, panel_version='local', **kwargs
    )

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    page.goto(f"http://localhost:8123/{app_path.name[:-3]}.html")

    cls = f'bk pn-loading {config.loading_spinner}'
    expect(page.locator('body')).to_have_class(cls)
    if wait:
        expect(page.locator('body')).not_to_have_class(cls, timeout=90 * 1000)

    return msgs


def test_pyodide_test_error_handling_worker(page, launch_app):
    wait_for_app(launch_app, error_app, page, 'pyodide-worker', wait=False)

    expect(page.locator('.pn-loading-msg')).to_have_text('RuntimeError: This app is broken', timeout=90 * 1000)

@pytest.mark.parametrize('runtime', ['pyodide', 'pyscript', 'pyodide-worker'])
def test_pyodide_test_convert_button_app(page, runtime, launch_app):
    msgs = wait_for_app(launch_app, button_app, page, runtime)

    expect(page.locator(".bk.bk-clearfix")).to_have_text('0')

    page.click('.bk.bk-btn')

    expect(page.locator(".bk.bk-clearfix")).to_have_text('1')

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []

@pytest.mark.parametrize('runtime', ['pyodide', 'pyscript', 'pyodide-worker'])
def test_pyodide_test_convert_slider_app(page, runtime, launch_app):
    msgs = wait_for_app(launch_app, slider_app, page, runtime)

    expect(page.locator(".bk.bk-clearfix")).to_have_text('0.0')

    page.click('.noUi-handle')
    page.keyboard.press('ArrowRight')

    expect(page.locator(".bk.bk-clearfix")).to_have_text('0.1')

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []

@pytest.mark.parametrize('runtime', ['pyodide', 'pyodide-worker'])
def test_pyodide_test_convert_tabulator_app(page, runtime, launch_app):
    msgs = wait_for_app(launch_app, tabulator_app, page, runtime)

    page.click('.bk.bk-btn')

    time.sleep(1)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []

@pytest.mark.parametrize(
    'runtime, http_patch', [
        ('pyodide', False),
        ('pyodide', True),
        ('pyodide-worker', False),
        ('pyodide-worker', True)
    ]
)
def test_pyodide_test_convert_csv_app(page, runtime, http_patch, launch_app):
    msgs = wait_for_app(launch_app, csv_app, page, runtime, http_patch=http_patch)

    titles = page.locator('.tabulator-col-title').all_text_contents()

    assert titles[1:] == ['index', 'date', 'Temperature', 'Humidity', 'Light', 'CO2', 'HumidityRatio', 'Occupancy']

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []

@pytest.mark.parametrize('runtime', ['pyodide', 'pyodide-worker'])
def test_pyodide_test_convert_png_app(page, runtime, launch_app):
    msgs = wait_for_app(launch_app, png_app, page, runtime)

    assert page.locator('img').count() == 1

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []
