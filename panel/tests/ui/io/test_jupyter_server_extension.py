import sys
import time

import pytest

pytestmark = pytest.mark.ui

not_windows = pytest.mark.skipif(sys.platform=='win32', reason="Does not work on Windows")

@not_windows
def test_jupyter_server(page, jupyter_server):
    page.goto(f"{jupyter_server}/panel-preview/render/app.py", wait_until='domcontentloaded')

    assert page.text_content('.bk.string') == '0'

    page.click('.bk.bk-btn')
    time.sleep(0.2)

    assert page.text_content('.bk.string') == '1'

    page.click('.bk.bk-btn')
    time.sleep(0.2)

    assert page.text_content('.bk.string') == '2'

@not_windows
def test_jupyter_server_kernel_error(page, jupyter_server):
    page.goto(f"{jupyter_server}/panel-preview/render/app.py?kernel=blah", wait_until='domcontentloaded')

    assert page.text_content('#subtitle') == "Kernel error: No such kernel 'blah'"

    page.select_option('select#kernel-select', 'python3')

    time.sleep(0.5)

    assert page.text_content('.bk.string') == '0'
    page.click('.bk.bk-btn')
    time.sleep(0.2)

    assert page.text_content('.bk.string') == '1'
