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


@pytest.mark.flaky(reruns=3, reruns_delay=5)
@pytest.mark.filterwarnings("ignore::ResourceWarning")
def test_jupyterlite_execution(launch_jupyterlite, page):
    # INFO: Needs TS changes uploaded to CDN. Relevant when
    # testing a new version of Bokeh.
    page.goto("http://localhost:8123/index.html")
    page.wait_for_load_state('networkidle')

    page.locator('text="Getting_Started.ipynb"').first.dblclick()
    page.wait_for_load_state('networkidle')

    for _ in range(6):
        page.locator('jp-button[data-command="notebook:run-cell-and-select-next"]').click()
        if page.locator('.jp-Dialog').count() == 1: # Select the kernel if pop-up
            page.locator('.jp-select-wrapper > select').select_option('Python (Pyodide)')
            page.locator('.jp-Dialog-footer > button').nth(1).click()
        page.wait_for_load_state('networkidle')
        expect(page.locator('.jp-Notebook-ExecutionIndicator')).to_have_attribute('data-status', 'idle', timeout=60_000)

    page.locator('.noUi-handle').click()

    page.keyboard.press('ArrowRight')

    expect(page.locator('.bk-panel-models-markup-HTML').locator('div').locator('pre')).to_have_text('0.1')
