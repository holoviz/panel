import sys
import time

from http.client import HTTPConnection
from subprocess import PIPE, Popen

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

pytestmark = pytest.mark.jupyter


@pytest.fixture()
def launch_jupyterlite():
    process = Popen(
        [sys.executable, "-m", "http.server", "8123", "--directory", 'lite/dist/'], stdout=PIPE
    )
    retries = 5
    while retries > 0:
        conn = HTTPConnection("localhost:8123")
        try:
            conn.request("HEAD", 'index.html')
            response = conn.getresponse()
            if response is not None:
                conn.close()
                break
        except ConnectionRefusedError:
            time.sleep(1)
            retries -= 1

    if not retries:
        process.terminate()
        process.wait()
        raise RuntimeError("Failed to start http server")
    try:
        yield
    finally:
        process.terminate()
        process.wait()


@pytest.mark.filterwarnings("ignore::ResourceWarning")
def test_jupyterlite_execution(launch_jupyterlite, page):
    # INFO: Needs TS changes uploaded to CDN. Relevant when
    # testing a new version of Bokeh.
    page.goto("http://localhost:8123/index.html")

    page.locator('text="Getting_Started.ipynb"').first.dblclick()

    # Select the kernel
    if page.locator('.jp-Dialog').count() == 1:
        page.locator('.jp-select-wrapper > select').select_option('Python (Pyodide)')
        page.locator('.jp-Dialog-footer > button').nth(1).click()

    for _ in range(6):
        page.locator('jp-button[data-command="notebook:run-cell-and-select-next"]').click()
        page.wait_for_timeout(500)

    page.locator('.noUi-handle').click(timeout=120 * 1000)

    page.keyboard.press('ArrowRight')

    expect(page.locator('.bk-panel-models-markup-HTML').locator('div').locator('pre')).to_have_text('0.1')
