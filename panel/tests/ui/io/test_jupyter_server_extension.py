import pytest

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

from panel.tests.util import wait_until

pytestmark = pytest.mark.jupyter

@pytest.mark.flaky(max_runs=3)
def test_jupyter_server(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py", timeout=30000)

    assert page.text_content('pre') == '0'

    page.click('button')

    wait_until(lambda: page.text_content('pre') == '1', page)

    page.click('button')

    wait_until(lambda: page.text_content('pre') == '2', page)

@pytest.mark.flaky(max_runs=3)
def test_jupyter_server_custom_resources(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py", timeout=30000)

    assert page.locator('.bk-Row').evaluate("""(element) =>
        window.getComputedStyle(element).getPropertyValue('background-color')""") == 'rgb(128, 0, 128)'

@pytest.mark.flaky(max_runs=3)
def test_jupyter_server_kernel_error(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py?kernel=blah", timeout=30000)

    assert page.text_content('#subtitle') == "Kernel error: No such kernel 'blah'"

    page.select_option('select#kernel-select', 'python3')

    wait_until(lambda: page.text_content('pre') == '0', page)

    page.click('button')

    wait_until(lambda: page.text_content('pre') == '1', page)

@pytest.mark.flaky(max_runs=3)
def test_jupyter_server_session_arg_theme(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py?theme=dark", timeout=30000)

    expect(page.locator('body')).to_have_css('color', 'rgb(0, 0, 0)')
