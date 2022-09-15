import sys

import pytest

from panel.tests.util import wait_until

pytestmark = pytest.mark.jupyter

not_windows = pytest.mark.skipif(sys.platform=='win32', reason="Does not work on Windows")

@not_windows
@pytest.mark.flaky(max_runs=3)
def test_jupyter_server(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py", timeout=30000)

    assert page.text_content('.bk.string') == '0'

    page.click('.bk.bk-btn')

    wait_until(lambda: page.text_content('.bk.string') == '1', page)

    page.click('.bk.bk-btn')

    wait_until(lambda: page.text_content('.bk.string') == '2', page)

@not_windows
@pytest.mark.flaky(max_runs=3)
def test_jupyter_server_kernel_error(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py?kernel=blah", timeout=30000)

    assert page.text_content('#subtitle') == "Kernel error: No such kernel 'blah'"

    page.select_option('select#kernel-select', 'python3')

    wait_until(lambda: page.text_content('.bk.string') == '0', page)

    page.click('.bk.bk-btn')

    wait_until(lambda: page.text_content('.bk.string') == '1', page)
