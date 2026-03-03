"""
Playwright test for the widget-bandsplot anywidget example.

Tests:
    1. Widget renders (Bokeh root attached to DOM)
    2. Component has expected params (bands, energy_range, format_settings)
    3. Python -> browser sync (change energy_range from Python)
"""
import pytest

pytest.importorskip("widget_bandsplot")
pytest.importorskip("playwright")

import numpy as np
from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


def _make_bands_data():
    """Generate minimal synthetic band structure data."""
    segments = [("GAMMA", "X", 0.0, 1.0)]
    paths = []
    for seg_from, seg_to, x_start, x_end in segments:
        x = np.linspace(x_start, x_end, 20).tolist()
        values = [
            (np.linspace(-2, -1, 20)).tolist(),
            (np.linspace(1, 2, 20)).tolist(),
        ]
        paths.append({
            "length": 20,
            "from": seg_from,
            "to": seg_to,
            "values": values,
            "x": x,
            "two_band_types": False,
        })
    return [{"paths": paths, "path": [["GAMMA", "X"]], "fermi_level": 0.0}]


def _make_pane():
    from widget_bandsplot import BandsPlotWidget
    bands = _make_bands_data()
    widget = BandsPlotWidget(
        bands=bands,
        energy_range=[-5.0, 5.0],
        format_settings={"showFermi": True, "showLegend": False},
    )
    return pn.pane.AnyWidget(widget, height=400, sizing_mode="stretch_width")


def test_bandsplot_renders(page):
    """BandsPlotWidget renders without crashing."""
    pane = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    assert_no_console_errors(msgs)


def test_bandsplot_component_has_expected_params(page):
    """The wrapped component exposes bands, energy_range, format_settings."""
    pane = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    assert hasattr(component, 'bands')
    assert hasattr(component, 'energy_range')
    assert hasattr(component, 'format_settings')
    assert component.energy_range == [-5.0, 5.0]

    assert_no_console_errors(msgs)


def test_bandsplot_python_changes_energy_range(page):
    """Changing energy_range from Python updates the widget."""
    from widget_bandsplot import BandsPlotWidget
    bands = _make_bands_data()
    widget = BandsPlotWidget(
        bands=bands,
        energy_range=[-5.0, 5.0],
    )
    pane = pn.pane.AnyWidget(widget, height=400)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    pane.component.energy_range = [-3.0, 3.0]
    wait_until(lambda: widget.energy_range == [-3.0, 3.0], page, timeout=10_000)

    assert_no_console_errors(msgs)
