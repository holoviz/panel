"""
Playwright test for the xarray-fancy-repr anywidget example (WORKS WITH CAVEATS).

XarrayWidget renders an interactive HTML representation of an xarray Dataset.
May fail with newer xarray versions due to inline_index_repr() signature change.

Tests:
    1. Widget loads (Bokeh root attached to DOM)
    2. Component has expected private params (_coords, _data_vars, _attrs)
"""
import pytest

pytest.importorskip("xarray_fancy_repr")
pytest.importorskip("xarray")
pytest.importorskip("playwright")

from playwright.sync_api import expect

import panel as pn

from panel.tests.util import serve_component

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


def _make_pane():
    import numpy as np
    import xarray as xr

    from xarray_fancy_repr import XarrayWidget

    ds = xr.Dataset({
        "temperature": xr.DataArray(
            np.random.randn(5, 3),
            dims=["x", "y"],
            attrs={"units": "degC"},
        ),
    })
    try:
        widget = XarrayWidget(ds)
    except TypeError:
        pytest.skip("xarray-fancy-repr incompatible with installed xarray version")
    return pn.pane.AnyWidget(widget, sizing_mode="stretch_width"), widget


def test_xarray_repr_renders(page):
    """XarrayWidget renders without crashing."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page, timeout=15_000)

    root = page.locator("[data-root-id]").first
    expect(root).to_be_attached(timeout=10_000)

    assert_no_console_errors(msgs)


def test_xarray_repr_component_has_expected_params(page):
    """The wrapped component exposes private params for dataset structure."""
    pane, _ = _make_pane()
    msgs, _ = serve_component(page, pane)

    component = pane.component
    # All user-facing traits are underscore-prefixed
    assert hasattr(component, '_data_vars')
    assert hasattr(component, '_attrs')
    assert hasattr(component, '_obj_type')

    assert_no_console_errors(msgs)
