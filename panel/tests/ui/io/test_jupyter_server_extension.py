import sys
import time

import pytest

pytestmark = pytest.mark.jupyter

not_windows = pytest.mark.skipif(sys.platform=='win32', reason="Does not work on Windows")

@not_windows
@pytest.mark.flaky(max_runs=3)
def test_jupyter_server(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py", timeout=30000)

    assert page.text_content('.bk.string') == '0'

    page.click('.bk.bk-btn')
    time.sleep(0.5)

    assert page.text_content('.bk.string') == '1'

    page.click('.bk.bk-btn')
    time.sleep(0.5)

    assert page.text_content('.bk.string') == '2'

@not_windows
@pytest.mark.flaky(max_runs=3)
def test_jupyter_server_kernel_error(page, jupyter_preview):
    page.goto(f"{jupyter_preview}/app.py?kernel=blah", timeout=30000)

    assert page.text_content('#subtitle') == "Kernel error: No such kernel 'blah'"

    page.select_option('select#kernel-select', 'python3')

    time.sleep(0.5)

    assert page.text_content('.bk.string') == '0'
    page.click('.bk.bk-btn')
    time.sleep(0.5)

    assert page.text_content('.bk.string') == '1'
