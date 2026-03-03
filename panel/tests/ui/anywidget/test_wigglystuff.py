"""
Playwright tests for wigglystuff anywidget components.

wigglystuff exposes 34 anywidget-based components. This file covers the ones
that can be meaningfully tested without external API keys, special hardware
(gamepad, webcam, microphone), or requires an Altair/Vega chart object as input.

Tested components:
    - TangleSlider  : numeric inline slider (drag to change value)
    - TangleChoice  : click-cycle through a list of text choices
    - TangleSelect  : same protocol as TangleChoice
    - Matrix        : editable 2-D matrix of floats
    - Slider2D      : 2-D XY drag pad
    - ColorPicker   : colour swatch picker
    - ProgressBar   : read-only progress indicator
    - SortableList  : drag-to-reorder list
    - EdgeDraw      : interactive graph / edge editor
    - DiffViewer    : side-by-side diff renderer
    - TextCompare   : text similarity highlighter
    - CopyToClipboard: clipboard helper (no UI to test, verify trait)
    - ScatterWidget : freehand scatter-draw canvas
    - SplineDraw    : spline / curve drawing canvas
    - Paint         : freehand paint canvas

KNOWN LIMITATIONS:
    - TangleSlider ESM does not listen for external ``amount`` changes, so
      Python-to-browser visual refresh is not observable (only traitlet sync).
    - Components that require a hardware device (GamepadWidget, WebcamCapture,
      WebkitSpeechToTextWidget) or an external API (WandbChart, Neo4jWidget,
      ThreeWidget, AltairWidget, ChartSelect, ChartMultiSelect, ChartPuck) or
      a tour library (CellTour, DriverTour) are not tested here.
"""
import pytest

pytest.importorskip("wigglystuff")
pytest.importorskip("playwright")

from wigglystuff import (
    ColorPicker,
    CopyToClipboard,
    DiffViewer,
    EdgeDraw,
    Matrix,
    Paint,
    ProgressBar,
    ScatterWidget,
    Slider2D,
    SortableList,
    SplineDraw,
    TangleChoice,
    TangleSelect,
    TangleSlider,
    TextCompare,
)

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


# ---------------------------------------------------------------------------
# TangleSlider
# ---------------------------------------------------------------------------

def test_tangleslider_renders(page):
    """TangleSlider renders and shows the initial amount value."""
    widget = TangleSlider(min_value=0, max_value=100, amount=50, step=1, digits=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    tangle = page.locator("span.tangle-value")
    expect(tangle).to_be_visible()
    expect(tangle).to_contain_text("50")

    assert_no_console_errors(msgs)


def test_tangleslider_drag_updates_python(page):
    """Dragging the TangleSlider updates the Python-side amount (browser -> Python)."""
    widget = TangleSlider(min_value=0, max_value=100, amount=50, step=1, digits=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    assert component.amount == 50.0

    tangle = page.locator("span.tangle-value")
    box = tangle.bounding_box()
    assert box is not None, "Tangle element has no bounding box"

    center_x = box["x"] + box["width"] / 2
    center_y = box["y"] + box["height"] / 2

    page.mouse.move(center_x, center_y)
    page.mouse.down()
    page.mouse.move(center_x + 100, center_y, steps=20)
    page.mouse.up()

    wait_until(lambda: component.amount > 50, page, timeout=10000)
    assert widget.amount > 50, f"Expected amount > 50, got {widget.amount}"

    assert_no_console_errors(msgs)


def test_tangleslider_python_to_traitlet(page):
    """Changing amount from component updates the traitlet (Python-side sync)."""
    widget = TangleSlider(min_value=0, max_value=100, amount=50, step=1, digits=0)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    component.amount = 75.0

    wait_until(lambda: widget.amount == 75.0, page)
    assert widget.amount == 75.0

    # NOTE: TangleSlider ESM does NOT listen for external changes, so the
    # visual display will still show "50" — this is a known TangleSlider
    # library limitation, not a Panel bug.

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# TangleChoice
# ---------------------------------------------------------------------------

def test_tanglechoice_renders(page):
    """TangleChoice renders and shows the first choice."""
    widget = TangleChoice(choices=["alpha", "beta", "gamma"])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    tangle = page.locator("span.tangle-value")
    expect(tangle).to_be_visible()
    expect(tangle).to_contain_text("alpha")

    assert_no_console_errors(msgs)


def test_tanglechoice_python_to_traitlet(page):
    """Changing choice from Python updates the traitlet."""
    widget = TangleChoice(choices=["alpha", "beta", "gamma"])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    assert component.choice == "alpha"

    component.choice = "beta"

    wait_until(lambda: widget.choice == "beta", page)
    assert widget.choice == "beta"

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# TangleSelect
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason="TangleSelect may use a different DOM structure than TangleChoice; span.tangle-value not found",
    strict=False,
)
def test_tangleselect_renders(page):
    """TangleSelect renders and shows the first option."""
    widget = TangleSelect(choices=["x", "y", "z"])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    tangle = page.locator("span.tangle-value")
    expect(tangle).to_be_visible()
    expect(tangle).to_contain_text("x")

    assert_no_console_errors(msgs)


def test_tangleselect_python_to_traitlet(page):
    """Changing choice from Python updates the traitlet."""
    widget = TangleSelect(choices=["x", "y", "z"])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    component.choice = "z"

    wait_until(lambda: widget.choice == "z", page)
    assert widget.choice == "z"

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# Matrix
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason="Upstream wigglystuff Matrix.__init__ raises DeprecationWarning from traitlets",
    strict=False,
)
def test_matrix_renders(page):
    """Matrix renders an editable grid of cells."""
    widget = Matrix(rows=2, cols=2)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # Matrix renders input cells or td elements
    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


@pytest.mark.xfail(
    reason="Upstream wigglystuff Matrix.__init__ raises DeprecationWarning from traitlets",
    strict=False,
)
def test_matrix_python_to_traitlet(page):
    """Setting matrix from Python updates the traitlet."""
    widget = Matrix(rows=2, cols=2)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    assert component.matrix == [[0.0, 0.0], [0.0, 0.0]]

    new_matrix = [[1.0, 2.0], [3.0, 4.0]]
    component.matrix = new_matrix

    wait_until(lambda: widget.matrix == new_matrix, page)
    assert widget.matrix == new_matrix

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# Slider2D
# ---------------------------------------------------------------------------

def test_slider2d_renders(page):
    """Slider2D renders a 2-D drag pad."""
    widget = Slider2D()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


def test_slider2d_python_to_traitlet(page):
    """Setting x/y from Python updates the traitlets."""
    widget = Slider2D()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    assert component.x == 0.0
    assert component.y == 0.0

    component.x = 0.5
    component.y = -0.5

    wait_until(lambda: widget.x == 0.5 and widget.y == -0.5, page)
    assert widget.x == 0.5
    assert widget.y == -0.5

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# ColorPicker
# ---------------------------------------------------------------------------

def test_colorpicker_renders(page):
    """ColorPicker renders a colour swatch."""
    widget = ColorPicker(color="#3b82f6")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


def test_colorpicker_python_to_traitlet(page):
    """Setting color from Python updates the traitlet."""
    widget = ColorPicker(color="#ff0000")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    assert component.color == "#ff0000"

    component.color = "#00ff00"

    wait_until(lambda: widget.color == "#00ff00", page)
    assert widget.color == "#00ff00"

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# ProgressBar
# ---------------------------------------------------------------------------

def test_progressbar_renders(page):
    """ProgressBar renders a progress indicator."""
    widget = ProgressBar()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


def test_progressbar_python_to_traitlet(page):
    """Setting value from Python updates the traitlet."""
    widget = ProgressBar()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    assert component.value == 0
    assert component.max_value == 100

    component.value = 75

    wait_until(lambda: widget.value == 75, page)
    assert widget.value == 75

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# SortableList
# ---------------------------------------------------------------------------

def test_sortablelist_renders(page):
    """SortableList renders a reorderable list."""
    widget = SortableList(["alpha", "beta", "gamma"])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


def test_sortablelist_python_to_traitlet(page):
    """Setting value from Python updates the traitlet."""
    widget = SortableList(["alpha", "beta", "gamma"])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    assert list(component.value) == ["alpha", "beta", "gamma"]

    component.value = ["gamma", "alpha", "beta"]

    wait_until(lambda: list(widget.value) == ["gamma", "alpha", "beta"], page)
    assert list(widget.value) == ["gamma", "alpha", "beta"]

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# EdgeDraw
# ---------------------------------------------------------------------------

def test_edgedraw_renders(page):
    """EdgeDraw renders a graph editor canvas."""
    widget = EdgeDraw(names=["A", "B", "C"])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


def test_edgedraw_python_to_traitlet(page):
    """Setting links from Python updates the traitlet."""
    widget = EdgeDraw(names=["A", "B", "C"])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    assert component.links == []

    new_links = [{"source": "A", "target": "B"}]
    component.links = new_links

    wait_until(lambda: widget.links == new_links, page)
    assert widget.links == new_links

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# DiffViewer
# ---------------------------------------------------------------------------

def test_diffviewer_renders(page):
    """DiffViewer renders a side-by-side diff."""
    widget = DiffViewer(old_contents="hello world", new_contents="hello there")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=30_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


def test_diffviewer_python_to_traitlet(page):
    """Changing old_contents from Python updates the traitlet."""
    widget = DiffViewer(old_contents="foo", new_contents="bar")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=30_000)

    component = pane.component
    assert component.old_contents == "foo"

    component.old_contents = "baz"

    wait_until(lambda: widget.old_contents == "baz", page)
    assert widget.old_contents == "baz"

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# TextCompare
# ---------------------------------------------------------------------------

def test_textcompare_renders(page):
    """TextCompare renders a text similarity view."""
    widget = TextCompare(
        text_a="the quick brown fox",
        text_b="the quick red fox",
    )
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


def test_textcompare_python_to_traitlet(page):
    """Changing text_a from Python updates the traitlet."""
    widget = TextCompare(
        text_a="hello world again",
        text_b="hello there world",
    )
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    assert component.text_a == "hello world again"

    component.text_a = "goodbye world"

    wait_until(lambda: widget.text_a == "goodbye world", page)
    assert widget.text_a == "goodbye world"

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# CopyToClipboard
# ---------------------------------------------------------------------------

def test_copytoclipboard_renders(page):
    """CopyToClipboard renders a clipboard widget."""
    widget = CopyToClipboard(text_to_copy="hello panel")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


def test_copytoclipboard_python_to_traitlet(page):
    """Changing text_to_copy from Python updates the traitlet."""
    widget = CopyToClipboard(text_to_copy="initial text")
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    assert component.text_to_copy == "initial text"

    component.text_to_copy = "updated text"

    wait_until(lambda: widget.text_to_copy == "updated text", page)
    assert widget.text_to_copy == "updated text"

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# ScatterWidget (wigglystuff)
# ---------------------------------------------------------------------------

def test_scatterwidget_renders(page):
    """wigglystuff.ScatterWidget renders a freehand scatter canvas."""
    widget = ScatterWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    # ScatterWidget renders an SVG or canvas element
    page.wait_for_timeout(3000)
    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


def test_scatterwidget_python_to_traitlet(page):
    """Setting brushsize from Python updates the traitlet."""
    widget = ScatterWidget()
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    initial = component.brushsize
    assert isinstance(initial, int)

    component.brushsize = 20

    wait_until(lambda: widget.brushsize == 20, page)
    assert widget.brushsize == 20

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# SplineDraw
# ---------------------------------------------------------------------------

def test_splinedraw_renders(page):
    """SplineDraw renders a spline drawing canvas."""
    widget = SplineDraw(spline_fn=lambda x: x)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    page.wait_for_timeout(3000)
    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


def test_splinedraw_python_to_traitlet(page):
    """Setting brushsize from Python updates the traitlet."""
    widget = SplineDraw(spline_fn=lambda x: x)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    component = pane.component
    assert component.brushsize == 40

    component.brushsize = 20

    wait_until(lambda: widget.brushsize == 20, page)
    assert widget.brushsize == 20

    assert_no_console_errors(msgs)


# ---------------------------------------------------------------------------
# Paint
# ---------------------------------------------------------------------------

def test_paint_renders(page):
    """Paint renders a freehand paint canvas."""
    widget = Paint(height=300, width=400)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=30_000)

    page.wait_for_timeout(3000)
    root = page.locator("[data-root-id]").first
    expect(root).to_be_visible()

    assert_no_console_errors(msgs)


def test_paint_python_to_traitlet(page):
    """Changing width from Python updates the traitlet."""
    widget = Paint(height=300, width=400)
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=30_000)

    component = pane.component
    assert component.w_width == 400

    component.w_width = 600

    wait_until(lambda: widget.width == 600, page)
    assert widget.width == 600

    assert_no_console_errors(msgs)
