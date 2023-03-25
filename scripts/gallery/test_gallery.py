"""The purpose of this script is to enable testing of a multi page Panel app by with an index page by

- Retrieving the list of pages from the index page
- Loading each page and running various tests

We use Playwright to run these tests

When the tests have run there will be screenshots in the 'screenshots' folder. Its very
quick to skim through these to identify obvious issues.

Usefull commands

- Run headed: pytest --headed scripts/gallery/test_gallery.py
"""
from pathlib import Path

import pytest

from gallery_utils import get_urls
from playwright.sync_api import Page, ConsoleMessage

INDEX_URL = "https://panel-gallery-dev.pyviz.demo.anaconda.com/"
RESPONSE_TIMEOUT = 10000  # ms
RENDER_TIMEOUT = 10000  # ms
PAGE_URLS = get_urls(INDEX_URL)

# PAGE_URLS = ["https://panel-gallery-dev.pyviz.demo.anaconda.com/deck_gl_global_power_plants"]

CONSOLE_ERRORS_TO_IGNORE = [
    "loaders.gl: The __VERSION__ variable is not injected using babel plugin. Latest unstable workers would be fetched from the CDN."
]


@pytest.fixture(params=PAGE_URLS)
def page_url(request) -> str:
    """Returns the url of a page to test"""
    yield request.param


@pytest.fixture(scope="session")
def screenshots():
    """Returns the path where all screenshots should be saved"""
    path = Path(__file__).parent / "screenshots"
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.fixture
def screenshot(page_url: str, screenshots: Path):
    """Returns the path where the specific screenshot should be saved"""
    path = screenshots / (page_url.split("/")[-1] + ".png")
    path.unlink(missing_ok=True)
    return path


def bokeh_document_idle(message: ConsoleMessage) -> bool:
    """Used to wait for the page to finish rendering"""
    return message.text.startswith("[bokeh] document idle")


def handle_console_error(message: ConsoleMessage) -> bool:
    if message.type == "error" and not message.text in CONSOLE_ERRORS_TO_IGNORE:
        raise ValueError(f"Console error: {message.text}")
    return True


def handle_page_error(error):
    raise ValueError(f"Page error: {error.text}")


def test_page(page_url: str, page: Page, screenshot: Path):
    """We load the page and run a lot of tests"""
    # Given
    page.on("console", handle_console_error)
    # For some unknown reason this does not catch the "Uncaught Error: [object Undefined] is not serializable" in https://panel-gallery-dev.pyviz.demo.anaconda.com/deck_gl_global_power_plants
    page.on("pageerror", handle_page_error)
    # When
    page.goto(page_url, timeout=RESPONSE_TIMEOUT)
    page.wait_for_event(
        event="console", predicate=bokeh_document_idle, timeout=RENDER_TIMEOUT
    ), "Page is empty. Never got '[bokeh] document idle...' message in console"
    page.screenshot(path=screenshot, full_page=True)
    # Then
    assert (
        page.locator("body").locator("div").all()
    ), "Page is empty. No divs found in body"

    # One day
    # - Test that there are no errors in the browser console
    # - Test that the page loads fast enough
    # - Test that each page is wrapped in a nice looking template
    # - Test that the page looks as expected. For example by comparing to reference screenshot.
    # - Test that the page works as expected when you interact with it
    # - Test that the page works for different devices, browsers and screen sizes
