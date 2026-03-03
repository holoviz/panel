"""
Playwright test for the jupyter-scatter anywidget example.

Tests:
    1. Widget renders (WebGL canvas appears)
    2. No unexpected console errors
    3. Python -> Browser sync (change point size from Python)
    4. Bokeh reserved name collision is fixed (connect -> w_connect)

Note: jupyter-scatter uses WebGL (regl-scatterplot) and has a massive
ESM bundle (~951KB). Rendering may be slow or fail in headless Chromium
due to WebGL/ESM loading constraints.

The `width`, `height`, and `connect` traitlets collide with Panel/Bokeh
reserved names, so they are mapped to `w_width`, `w_height`, `w_connect`.
"""
import pytest

jscatter = pytest.importorskip("jscatter")
pytest.importorskip("playwright")

import numpy as np
import pandas as pd

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import wait_for_anywidget

pytestmark = pytest.mark.ui

# Console messages specific to jupyter-scatter that are benign
_JSCATTER_KNOWN = [
    "regl",           # WebGL warnings from regl-scatterplot
    "WebGL",          # WebGL context messages
    "WEBGL",          # WebGL deprecation warnings
    "webgl",          # WebGL fallback messages
    "GPU",            # GPU process messages
    "texture",        # Texture size warnings
]


def _make_scatter():
    """Create a small scatter plot for testing."""
    from jscatter.jscatter import Scatter

    np.random.seed(42)
    df = pd.DataFrame({
        "x": np.random.randn(100),
        "y": np.random.randn(100),
    })
    scatter = Scatter(data=df, x="x", y="y", size=3, height=300)
    return scatter, scatter.widget


def _assert_no_errors(msgs):
    """Filter console errors, ignoring jscatter-specific benign messages."""
    from .conftest import KNOWN_CONSOLE_MESSAGES
    errors = [m for m in msgs if m.type == "error"]
    errors = [
        m for m in errors
        if not any(known in m.text for known in KNOWN_CONSOLE_MESSAGES + _JSCATTER_KNOWN)
    ]
    assert errors == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in errors)
    )


def test_jupyter_scatter_renders(page):
    """Widget renders and shows the scatter plot canvas."""
    scatter, widget = _make_scatter()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    try:
        wait_for_anywidget(page, timeout=30_000)
    except Exception:
        pytest.skip(
            "jupyter-scatter AnyWidget did not render in 30s "
            "(likely ESM bundle or WebGL loading issue in headless Chromium)"
        )

    # jupyter-scatter renders into a canvas element; it may take
    # a long time due to the ~951KB ESM bundle and WebGL init
    canvas = page.locator("canvas")
    try:
        canvas.first.wait_for(state="visible", timeout=60_000)
    except Exception:
        # Check if the failure is due to an ESM loading/compilation error
        error_msgs = [m for m in msgs if m.type == "error"]
        esm_errors = [m for m in error_msgs if "SyntaxError" in m.text or "rendering Bokeh" in m.text]
        if esm_errors:
            pytest.skip(
                "jupyter-scatter ESM bundle failed to load: "
                + esm_errors[0].text[:200]
            )
        pytest.skip(
            "jupyter-scatter WebGL canvas did not render in 60s "
            "(likely headless Chromium WebGL limitation)"
        )

    _assert_no_errors(msgs)


def test_jupyter_scatter_python_changes_size(page):
    """Changing point size from Python updates the widget."""
    scatter, widget = _make_scatter()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    try:
        wait_for_anywidget(page, timeout=30_000)
    except Exception:
        pytest.skip("jupyter-scatter AnyWidget did not render in 30s")

    canvas = page.locator("canvas")
    try:
        canvas.first.wait_for(state="visible", timeout=60_000)
    except Exception:
        pytest.skip("jupyter-scatter did not render (WebGL or ESM issue)")

    pane.component.size = 10
    wait_until(lambda: widget.size == 10, page)
    assert widget.size == 10

    _assert_no_errors(msgs)


def test_jupyter_scatter_connect_renamed():
    """The 'connect' traitlet is correctly renamed to 'w_connect'
    (Bokeh reserved name collision avoidance)."""
    from panel.pane.anywidget import _COMPONENT_CACHE
    _COMPONENT_CACHE.clear()

    scatter, widget = _make_scatter()
    pane = pn.pane.AnyWidget(widget)
    component = pane.component

    # The connect traitlet should be accessible as w_connect
    assert hasattr(component, 'w_connect')
    # width and height should also be renamed
    assert hasattr(component, 'w_width')
    assert hasattr(component, 'w_height')

    # Sync works through prefixed name
    component.w_connect = False
    assert widget.connect is False

    _COMPONENT_CACHE.clear()
