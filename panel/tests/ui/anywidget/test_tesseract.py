"""
Playwright test for the Tesseract PDF.js anywidget example (WORKS).

Tesseract PDF.js provides a PDF viewer with OCR capabilities in the browser.

Tests:
    1. Widget loads (Bokeh root attached to DOM)
    2. Component has expected params (value)
"""
import pytest

pytest.importorskip("jupyter_anywidget_tesseract_pdfjs")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

from .conftest import (
    assert_no_console_errors,
    console_errors,
    wait_for_anywidget,
)

pytestmark = [
    pytest.mark.ui,
    pytest.mark.filterwarnings(
        "ignore:The `ipykernel.comm.Comm` class has been deprecated:DeprecationWarning"
    ),
]

# Tesseract WASM loading may produce network/resource warnings
_TESSERACT_KNOWN_ERRORS = [
    "Failed to load resource", "net::ERR",
    "ResizeObserver",
]


def _filter_tesseract_errors(msgs):
    errors = console_errors(msgs)
    return [
        e for e in errors
        if not any(known.lower() in e.text.lower() for known in _TESSERACT_KNOWN_ERRORS)
    ]


def _make_pane():
    from jupyter_anywidget_tesseract_pdfjs import Widget as TesseractWidget

    widget = TesseractWidget()
    pane = pn.pane.AnyWidget(widget, height=500)
    return pane, widget


def test_tesseract_renders(page):
    """Tesseract PDF.js widget renders without crashing."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    unexpected = _filter_tesseract_errors(msgs)
    assert unexpected == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in unexpected)
    )


def test_tesseract_has_expected_params(page):
    """Component exposes value param."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'value')
    assert isinstance(component.value, int)
