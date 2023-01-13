import time

import pytest

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.pane import PDF


def test_pdf_embed(page, port):
    url = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
    pdf_pane = PDF(url)

    serve(pdf_pane, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    src = page.locator("embed").get_attribute('src')

    assert src.startswith(f"blob:http://localhost:{port}")
    assert src.endswith("#page=1")


def test_pdf_embed_start_page(page, port):
    # The pdf does not have 2 pages just to verify #page is set
    url = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
    pdf_pane = PDF(url, start_page=22)

    serve(pdf_pane, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    src = page.locator("embed").get_attribute('src')

    assert src.startswith(f"blob:http://localhost:{port}")
    assert src.endswith("#page=22")


def test_pdf_no_embed_start_page(page, port):
    # The pdf does not have 2 pages just to verify #page is set
    url = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
    pdf_pane = PDF(url, start_page=22, embed=False)

    serve(pdf_pane, port=port, threaded=True, show=False)
    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    src = page.locator("embed").get_attribute('src')
    assert src == url + "#page=22"
