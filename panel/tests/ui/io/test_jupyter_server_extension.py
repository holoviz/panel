import sys

from pathlib import Path

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import wait_until

pytestmark = [pytest.mark.jupyter, pytest.mark.flaky(max_runs=3)]


def test_jupyter_server(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py", timeout=30000)

    assert page.text_content('pre') == '0'

    page.click('button')

    wait_until(lambda: page.text_content('pre') == '1', page)

    page.click('button')

    wait_until(lambda: page.text_content('pre') == '2', page)


def test_jupyter_server_custom_resources(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py", timeout=30000)

    assert page.locator('.bk-Row').evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(128, 0, 128)'


def test_jupyter_server_kernel_error(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py?kernel=blah", timeout=30000)

    expect(page.locator('#error-type')).to_have_text("Kernel Error")
    expect(page.locator('#error')).to_have_text("No such kernel 'blah'")

    page.select_option('select#kernel-select', 'python3')

    wait_until(lambda: page.text_content('pre') == '0', page)

    page.click('button')

    wait_until(lambda: page.text_content('pre') == '1', page)


def test_jupyter_server_session_arg_theme(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py?theme=dark", timeout=30000)

    expect(page.locator('body')).to_have_css('color', 'rgb(0, 0, 0)')


def test_jupyter_config():
    # If this test fails, run `pip install -e .` again
    jp_files = (Path(sys.prefix) / 'etc' / 'jupyter').rglob('panel-client-jupyter.json')
    assert len(list(jp_files)) == 2
