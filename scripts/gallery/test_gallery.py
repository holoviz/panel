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
from playwright.sync_api import Page

INDEX_URL = "https://panel-gallery-dev.pyviz.demo.anaconda.com/"
PAGE_TIMEOUT = 10000  # ms
PAGE_URLS = get_urls(INDEX_URL)

# PAGE_URLS = ["https://panel-gallery-dev.pyviz.demo.anaconda.com/altair_choropleth"]


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
    return screenshots / (page_url.split("/")[-1] + ".png")


def bokeh_items_rendered(message) -> bool:
    """Used to wait for the page to finish rendering"""
    return message.text == "Bokeh items were rendered successfully"


def test_page(page_url: str, page: Page, screenshot: Path):
    """We load the page and run a lot of tests"""
    # When
    page.goto(page_url, timeout=PAGE_TIMEOUT)
    page.wait_for_event(
        event="console", predicate=bokeh_items_rendered
    ), "Page is empty. Never got 'Bokeh items rendered' message in console"
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
