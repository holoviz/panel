import sys
import time

import pytest

pytestmark = pytest.mark.ui

not_windows = pytest.mark.skipif(sys.platform=='win32', reason="Does not work on Windows")

@not_windows
def test_jupyter_server(page, jupyter_server):
    port = jupyter_server.args[-1]

    page.goto(f"http://localhost:{port}/panel-preview/render/app.py")

    assert page.text_content('.bk.string') == '0'

    page.click('.bk.bk-btn')
    time.sleep(0.1)

    assert page.text_content('.bk.string') == '1'

    page.click('.bk.bk-btn')
    time.sleep(0.1)

    assert page.text_content('.bk.string') == '2'

@not_windows
def test_jupyter_server_kernel_error(page, jupyter_server):
    port = jupyter_server.args[-1]

    page.goto(f"http://localhost:{port}/panel-preview/render/app.py?kernel=blah")

    assert page.text_content('h1') == 'Kernel Error: No such kernel blah'

    page.select_option('select#kernel-select', 'python3')

    assert page.text_content('.bk.string') == '0'
    page.click('.bk.bk-btn')
    time.sleep(0.1)

    assert page.text_content('.bk.string') == '1'
