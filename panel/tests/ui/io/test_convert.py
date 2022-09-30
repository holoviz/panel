import pathlib
import tempfile
import time

import pytest

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui

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

def write_app(app):
    """
    Writes app to temporary file and returns path.
    """
    nf = tempfile.NamedTemporaryFile(mode='w', suffix='.py')
    nf.write(app)
    nf.flush()
    return nf


@pytest.mark.parametrize('runtime', ['pyodide', 'pyscript'])
@pytest.mark.xfail(
    reason='_link_docs mishandling setter id in 0.14.0rc2'
)
def test_pyodide_test_convert_button_app(page, runtime):
    nf = write_app(button_app)
    app_path = pathlib.Path(nf.name)
    convert_apps([app_path], app_path.parent, runtime=runtime, build_pwa=False, build_index=False, prerender=False)

    page.goto(f"file://{str(app_path)[:-3]}.html")

    expect(page.locator('body')).to_have_class('bk pn-loading arcs')
    expect(page.locator('body')).to_have_class("", timeout=20000)

    assert page.text_content(".bk.markdown") == '0'

    page.click('.bk.bk-btn')

    time.sleep(0.1)

    assert page.text_content(".bk.markdown") == '1'


@pytest.mark.parametrize('runtime', ['pyodide', 'pyscript'])
def test_pyodide_test_convert_slider_app(page, runtime):
    nf = write_app(slider_app)
    app_path = pathlib.Path(nf.name)
    convert_apps([app_path], app_path.parent, runtime=runtime, build_pwa=False, build_index=False, prerender=False)

    page.goto(f"file://{str(app_path)[:-3]}.html")

    expect(page.locator('body')).to_have_class('bk pn-loading arcs')
    expect(page.locator('body')).to_have_class("", timeout=20000)

    assert page.text_content(".bk.bk-clearfix") == '0.0'

    page.click('.noUi-handle')
    page.keyboard.press('ArrowRight')

    time.sleep(0.1)

    assert page.text_content(".bk.bk-clearfix") == '0.1'
