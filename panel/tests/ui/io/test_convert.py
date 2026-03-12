import os
import pathlib
import re
import shutil
import tempfile
import time
import uuid

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.config import config
from panel.io.convert import BOKEH_LOCAL_WHL, PANEL_LOCAL_WHL, convert_apps
from panel.tests.util import http_serve_directory

if not (PANEL_LOCAL_WHL.is_file() and BOKEH_LOCAL_WHL.is_file()):
    pytest.skip(
        "Skipped because pyodide wheels are not available for current "
        "version. Build wheels for pyodide using `python scripts/build_pyodide_wheels.py`.",
        allow_module_level=True
    )

pytestmark = [pytest.mark.ui, pytest.mark.flaky(max_runs=3)]


if os.name == "nt":
    TIMEOUT = 200_000
else:
    TIMEOUT = 90_000

_worker_id = os.environ.get("PYTEST_XDIST_WORKER", "0")
HTTP_PORT = 50000 + int(re.sub(r"\D", "", _worker_id))
HTTP_URL = f"http://localhost:{HTTP_PORT}/"
RUNTIMES = ['pyodide', 'pyscript', 'pyodide-worker', 'pyscript-worker']

button_app = """
import panel as pn
button = pn.widgets.Button()
pn.Row(button, pn.bind(lambda c: c, button.param.clicks)).servable();
"""

template_button_app = """
import panel as pn
pn.extension(template='bootstrap')
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
tabulator = pn.widgets.Tabulator(pd.DataFrame({'a': [1, 2, 3]}))

def on_click(e):
    tabulator.theme = 'fast'

button = pn.widgets.Button()
button.on_click(on_click)

pn.Row(button, tabulator).servable();
"""

csv_app = """
import pandas as pd
import sys
import panel as pn

df = pd.read_csv('https://raw.githubusercontent.com/holoviz/panel/main/examples/assets/occupancy.csv')
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

config_app = """
import panel as pn
pn.config.raw_css = ['body { background-color: blue; }']
pn.Row('Output').servable();
"""

onload_app = """
import panel as pn

row = pn.Row('Foo')

def onload():
    row[:] = ['Bar']

pn.state.onload(onload)

row.servable()
"""

resources_app = """
import os
import panel as pn

row = pn.Row()

if os.path.isfile('./app.md'):
    with open('./app.md') as f:
        row[:] = [f.read()]

row.servable()
"""

@pytest.fixture(scope="module")
def http_serve():
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = pathlib.Path(temp_dir.name)

    test_file = (temp_path / 'test.html')
    test_file.write_text('<html><body>Test</body></html>')

    try:
        shutil.copy(PANEL_LOCAL_WHL, temp_path / PANEL_LOCAL_WHL.name)
    except shutil.SameFileError:
        pass
    try:
        shutil.copy(BOKEH_LOCAL_WHL, temp_path / BOKEH_LOCAL_WHL.name)
    except shutil.SameFileError:
        pass

    httpd, _ = http_serve_directory(str(temp_path), port=HTTP_PORT)

    time.sleep(1)

    def write(app):
        app_name = uuid.uuid4().hex
        app_path = temp_path / f'{app_name}.py'
        with open(app_path, 'w') as f:
            f.write(app)
        return app_path

    try:
        yield write
    finally:
        httpd.shutdown()
        temp_dir.cleanup()


def wait_for_app(http_serve, app, page, runtime, wait=True, resources=None, **kwargs):
    app_path = http_serve(app)

    resource_paths = []
    for resource in (resources or []):
        resource_path = app_path.parent / pathlib.Path(resource).name
        try:
            shutil.copy(resource, resource_path)
        except shutil.SameFileError:
            pass
        resource_paths.append(resource_path)

    convert_apps(
        [app_path], app_path.parent, runtime=runtime, build_pwa=False,
        prerender=False, panel_version='local', inline=True,
        local_prefix=HTTP_URL, resources=resource_paths, **kwargs
    )

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    page.goto(f"{HTTP_URL}{app_path.name[:-3]}.html")

    cls = f'pn-loading pn-{config.loading_spinner}'
    expect(page.locator('body')).to_have_class(cls)
    if wait:
        expect(page.locator('body')).not_to_have_class(cls, timeout=TIMEOUT)

    return msgs



def test_pyodide_test_error_handling_worker(http_serve, page):
    wait_for_app(http_serve, error_app, page, 'pyodide-worker', wait=False)

    expect(page.locator('.pn-loading-msg')).to_have_text('RuntimeError: This app is broken', timeout=TIMEOUT)


@pytest.mark.parametrize('runtime', RUNTIMES)
def test_pyodide_test_convert_button_app(http_serve, page, runtime):
    msgs = wait_for_app(http_serve, button_app, page, runtime)

    expect(page.locator('pre:not([class])')).to_have_text('0')

    page.click('.bk-btn')

    expect(page.locator('pre:not([class])')).to_have_text('1')

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


@pytest.mark.parametrize('runtime', RUNTIMES)
def test_pyodide_test_convert_template_button_app(http_serve, page, runtime):
    msgs = wait_for_app(http_serve, button_app, page, runtime)

    expect(page.locator('pre:not([class])')).to_have_text('0')

    page.click('.bk-btn')

    expect(page.locator('pre:not([class])')).to_have_text('1')

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


@pytest.mark.parametrize('runtime', RUNTIMES)
def test_pyodide_test_convert_slider_app(http_serve, page, runtime):
    msgs = wait_for_app(http_serve, slider_app, page, runtime)

    expect(page.locator('pre:not([class])')).to_have_text('0.0')

    page.click('.noUi-handle')
    page.keyboard.press('ArrowRight')

    expect(page.locator('pre:not([class])')).to_have_text('0.1')

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


@pytest.mark.parametrize('runtime', RUNTIMES)
def test_pyodide_test_convert_custom_config(http_serve, page, runtime):
    wait_for_app(http_serve, config_app, page, runtime)

    assert page.locator("body").evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(0, 0, 255)'


@pytest.mark.parametrize('runtime', ['pyodide', 'pyodide-worker'])
def test_pyodide_test_convert_tabulator_app(http_serve, page, runtime):
    msgs = wait_for_app(http_serve, tabulator_app, page, runtime)

    page.click('.bk-btn')

    page.wait_for_timeout(1)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


@pytest.mark.parametrize(
    'runtime, http_patch', [
        ('pyodide', False),
        ('pyodide', True),
        ('pyodide-worker', False),
        ('pyodide-worker', True)
    ]
)
def test_pyodide_test_convert_csv_app(http_serve, page, runtime, http_patch):
    msgs = wait_for_app(http_serve, csv_app, page, runtime, http_patch=http_patch)

    expected_titles = ['index', 'date', 'Temperature', 'Humidity', 'Light', 'CO2', 'HumidityRatio', 'Occupancy']

    titles = page.locator('.tabulator-col-title')
    expect(titles).to_have_count(2 + len(expected_titles), timeout=60 * 1000)
    titles = titles.all_text_contents()
    assert titles[1:-1] == expected_titles

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


@pytest.mark.parametrize('runtime', ['pyodide', 'pyodide-worker'])
def test_pyodide_test_convert_png_app(http_serve, page, runtime):
    msgs = wait_for_app(http_serve, png_app, page, runtime)

    expect(page.locator('img')).to_have_count(1)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


@pytest.mark.parametrize('runtime', ['pyodide', 'pyodide-worker'])
def test_pyodide_test_convert_onload_app(http_serve, page, runtime):
    msgs = wait_for_app(http_serve, onload_app, page, runtime)

    expect(page.locator('.markdown')).to_have_text('Bar')

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


@pytest.mark.parametrize('runtime', ['pyodide', 'pyodide-worker'])
def test_pyodide_test_convert_resources_app(http_serve, page, runtime):
    resource_path = pathlib.Path(__file__).parent / 'app.md'
    msgs = wait_for_app(
        http_serve, resources_app, page, runtime, resources=[resource_path]
    )

    expect(page.locator('.markdown')).to_have_text(resource_path.read_text().replace('```', '').replace('{pyodide}', ''))

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []
