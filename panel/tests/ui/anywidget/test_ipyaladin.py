"""
Playwright test for the ipyaladin anywidget example.

Tests:
    1. Widget renders (Aladin Lite sky viewer canvas appears)
    2. No unexpected console errors
    3. Python -> Browser sync (change survey from Python, verify traitlet updates)
    4. Python -> Browser sync (change target from Python)

Note: ipyaladin loads a remote ESM module from esm.sh and fetches sky survey
tiles over the network, so we use generous timeouts.
"""
import pytest

ipyaladin = pytest.importorskip("ipyaladin")
pytest.importorskip("playwright")

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = [
    pytest.mark.ui,
    pytest.mark.filterwarnings(
        "ignore:Passing unrecognized arguments to super:DeprecationWarning"
    ),
]

# Additional known console messages specific to ipyaladin
_IPYALADIN_KNOWN = [
    "A]",  # Aladin Lite logs like "[Aladin Lite]"
    "aladin",
    "esm.sh",
    "Failed to load resource",  # HiPS tile 404s are normal
    "Error while getting",
    "net::ERR",
    "Could not load",
    "TypeError: Failed to fetch",
    "CORS policy",  # Cross-origin requests to sky survey servers
    "Access-Control-Allow-Origin",
    "irsa.ipac.caltech.edu",
    "alasky",
    "alaskybis",
    # Aladin Lite WASM (Rust/WebAssembly) internal panics — benign, do not affect sync
    "RuntimeError: unreachable",  # wasm rust_panic from aladin_lite.wasm
    "wasm",                       # any other WebAssembly-related error line
]


def _assert_no_errors(msgs):
    """Filter console errors, ignoring ipyaladin-specific benign messages."""
    from .conftest import KNOWN_CONSOLE_MESSAGES, console_errors
    errors = console_errors(msgs)
    # Additionally filter ipyaladin-specific messages
    errors = [
        m for m in errors
        if not any(known in m.text for known in _IPYALADIN_KNOWN)
    ]
    assert errors == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in errors)
    )


def test_ipyaladin_renders(page):
    """Widget renders and shows the Aladin Lite sky viewer."""
    from ipyaladin import Aladin

    widget = Aladin(
        target="M42",
        fov=10,
    )
    pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width")
    pane.component.height = 400
    pane.component.sizing_mode = "stretch_width"

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Aladin Lite renders into a div with class 'aladin-widget'
    aladin_div = page.locator(".aladin-widget")
    aladin_div.first.wait_for(state="visible", timeout=30_000)

    _assert_no_errors(msgs)


def test_ipyaladin_python_changes_survey(page):
    """Changing survey from Python updates the widget (Python -> browser sync)."""
    from ipyaladin import Aladin

    widget = Aladin(
        target="M42",
        fov=10,
    )
    pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width")
    pane.component.height = 400
    pane.component.sizing_mode = "stretch_width"

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    aladin_div = page.locator(".aladin-widget")
    aladin_div.first.wait_for(state="visible", timeout=30_000)

    # Change survey from Python
    new_survey = "https://alaskybis.unistra.fr/2MASS/Color"
    pane.component.survey = new_survey

    # Verify the traitlet value synced
    wait_until(lambda: widget.survey == new_survey, page)
    assert widget.survey == new_survey

    _assert_no_errors(msgs)


def test_ipyaladin_python_changes_fov(page):
    """Changing field of view from Python updates the widget (Python -> browser sync)."""
    from ipyaladin import Aladin

    widget = Aladin(
        target="M42",
        fov=10,
    )
    pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width")
    pane.component.height = 400
    pane.component.sizing_mode = "stretch_width"

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    aladin_div = page.locator(".aladin-widget")
    aladin_div.first.wait_for(state="visible", timeout=30_000)

    # Change fov from Python
    pane.component._fov = 5.0

    # Verify the traitlet value synced
    wait_until(lambda: widget._fov == 5.0, page)

    _assert_no_errors(msgs)
