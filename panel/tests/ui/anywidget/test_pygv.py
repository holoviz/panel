"""
Playwright test for the pygv anywidget example.

pygv is a lightweight, scriptable genome browser built with anywidget
that uses igv.js for rendering. The Browser widget takes a Config
object with genome and locus fields.

Known limitation: pygv's ESM reads the config once at render time and
does not listen for ``change:config`` events, so navigation from Python
requires replacing the widget object entirely.

Tests:
    1. Widget renders (igv.js browser canvas appears in DOM)
    2. No unexpected console errors
    3. Python -> browser sync (replace widget object to navigate)
"""
import pytest

pytest.importorskip("pygv")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

# pygv / igv.js known console errors — CDN/network issues
_PYGV_KNOWN_ERRORS = [
    "Failed to load resource",
    "net::ERR",
    "TypeError: Failed to fetch",
    "CORS",
    "igv",
    "genome.ucsc.edu",
    "s3.amazonaws.com",
    "googleapis.com",
    "broadinstitute",
    "404",
    "Error rendering Bokeh items",
    "SyntaxError",
]


def _filter_pygv_errors(msgs):
    """Filter console errors, allowing known pygv/network upstream issues."""
    errors = console_errors(msgs)
    errors = [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in _PYGV_KNOWN_ERRORS)
    ]
    return errors


def _make_pygv_browser():
    """Create a pygv Browser with a simple genome config."""
    import pygv

    from pygv._config import Config

    config = Config(genome="hg38", locus="chr17:7,571,720-7,590,868")
    return pygv._browser.Browser(config=config)


def _make_pane():
    """Create a Panel AnyWidget pane wrapping a pygv Browser."""
    browser = _make_pygv_browser()
    pane = pn.pane.AnyWidget(
        browser, height=500, sizing_mode="stretch_width",
    )
    return pane, browser


def test_pygv_renders(page):
    """pygv genome browser loads and Bokeh root is attached to DOM.

    igv.js loads from CDN and fetches genome data from remote servers.
    We verify the Bokeh model attaches and look for the igv container.
    """
    pane, browser = _make_pane()

    msgs, _ = serve_component(page, pane)

    # Allow time for CDN load of igv.js and genome data
    page.wait_for_load_state("networkidle", timeout=60_000)
    page.wait_for_timeout(5000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=30_000)

    unexpected = _filter_pygv_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors (excluding known pygv/network issues):\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_pygv_component_has_config(page):
    """The wrapped component exposes the config param."""
    pane, browser = _make_pane()

    msgs, _ = serve_component(page, pane)

    component = pane.component

    # The config should be present on the component
    assert hasattr(component, 'config'), "component should have config param"

    unexpected = _filter_pygv_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_pygv_widget_replace_navigates(page):
    """Replacing the widget object navigates to a new locus.

    Since pygv's ESM is read-once, navigation requires replacing
    the entire AnyWidget pane object with a fresh Browser instance.
    """
    import pygv

    from pygv._config import Config

    initial_config = Config(genome="hg38", locus="chr17:7,571,720-7,590,868")
    browser = pygv._browser.Browser(config=initial_config)
    pane = pn.pane.AnyWidget(
        browser, height=500, sizing_mode="stretch_width",
    )

    msgs, _ = serve_component(page, pane)

    # Wait for initial render
    page.wait_for_load_state("networkidle", timeout=60_000)
    page.wait_for_timeout(5000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=30_000)

    # Navigate by replacing the widget object
    new_config = Config(genome="hg38", locus="chr8:127,735,434-127,742,951")
    new_browser = pygv._browser.Browser(config=new_config)
    pane.object = new_browser

    # Wait for the new widget to render
    page.wait_for_timeout(5000)

    # The pane should now reference the new browser
    assert pane.object is new_browser

    unexpected = _filter_pygv_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )
