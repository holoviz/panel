"""
xarray-fancy-repr Example -- Interactive Dataset Viewer
========================================================

This example demonstrates using xarray-fancy-repr's XarrayWidget
with Panel's AnyWidget pane. The widget renders an interactive HTML
representation of an xarray.Dataset, identical to the rich repr
shown in Jupyter notebooks.

XarrayWidget is an anywidget that syncs the Dataset's metadata
(coordinates, data variables, attributes, dimensions) to the browser
as private traitlets and renders a collapsible HTML tree view.

GitHub: https://github.com/benbovy/xarray-fancy-repr
PyPI:   https://pypi.org/project/xarray-fancy-repr/

Key traitlets (all private / underscore-prefixed):
    - _coords (List): Serialized coordinate info
    - _data_vars (List): Serialized data variable info
    - _attrs (Dict): Dataset attributes
    - _dim_info (Dict): Dimension sizes
    - _obj_type (Enum): One of 'dataset', 'dataarray', 'coordinates', 'variable'
    - _filter_search (Unicode): Text filter for variables

Required packages:
    pip install xarray-fancy-repr xarray numpy

Run with:
    panel serve research/anywidget/examples/ext_xarray_repr.py

Testing Instructions:
    1. Run the app with the command above
    2. Verify the xarray Dataset HTML tree renders (collapsible sections)
    3. Click on dimension/variable headers to expand/collapse them
    4. Use the Panel "Switch Dataset" selector to load different datasets
    5. Verify that the widget re-renders with the new dataset
    6. Check the browser console for errors (F12)

Trait Name Collisions: NONE
    All user-facing synced traits are underscore-prefixed (private).
    No collisions with Bokeh reserved names or Panel params.
"""

import numpy as np
import xarray as xr

from xarray_fancy_repr import XarrayWidget

import panel as pn

pn.extension()

# ---------------------------------------------------------------------------
# 1. Create sample xarray Datasets
# ---------------------------------------------------------------------------

DATASETS = {}

# Weather dataset
DATASETS["Weather (3D)"] = xr.Dataset(
    {
        "temperature": xr.DataArray(
            np.random.randn(10, 20, 5) * 10 + 15,
            dims=["time", "latitude", "longitude"],
            attrs={"units": "degC", "long_name": "Air Temperature"},
        ),
        "pressure": xr.DataArray(
            np.random.randn(10, 20, 5) * 5 + 1013,
            dims=["time", "latitude", "longitude"],
            attrs={"units": "hPa", "long_name": "Surface Pressure"},
        ),
        "humidity": xr.DataArray(
            np.random.rand(10, 20, 5) * 100,
            dims=["time", "latitude", "longitude"],
            attrs={"units": "%", "long_name": "Relative Humidity"},
        ),
    },
    coords={
        "time": np.arange(10),
        "latitude": np.linspace(-90, 90, 20),
        "longitude": np.linspace(-180, 180, 5),
    },
    attrs={"title": "Synthetic Weather Data", "source": "Random generator"},
)

# Simple 2D dataset
DATASETS["Simple (2D)"] = xr.Dataset(
    {
        "elevation": xr.DataArray(
            np.random.randn(50, 50) * 500 + 1000,
            dims=["x", "y"],
            attrs={"units": "m", "long_name": "Terrain Elevation"},
        ),
    },
    coords={
        "x": np.arange(50),
        "y": np.arange(50),
    },
    attrs={"title": "Synthetic Elevation Data"},
)

# Time series dataset
DATASETS["Time Series (1D)"] = xr.Dataset(
    {
        "price": xr.DataArray(
            np.cumsum(np.random.randn(100)) + 100,
            dims=["time"],
            attrs={"units": "USD"},
        ),
        "volume": xr.DataArray(
            np.random.randint(100, 10000, size=100),
            dims=["time"],
            attrs={"units": "shares"},
        ),
    },
    coords={"time": np.arange(100)},
    attrs={"title": "Synthetic Stock Data"},
)

# Start with the weather dataset
current_ds = DATASETS["Weather (3D)"]
try:
    widget = XarrayWidget(current_ds)
    _xarray_repr_works = True
except TypeError:
    # xarray-fancy-repr 0.0.2 is incompatible with newer xarray versions
    # (inline_index_repr() signature changed). Fall back to empty widget.
    widget = XarrayWidget(xr.Dataset({"x": xr.DataArray([1])}))
    _xarray_repr_works = False

# ---------------------------------------------------------------------------
# 2. Wrap with Panel's AnyWidget pane
# ---------------------------------------------------------------------------

anywidget_pane = pn.pane.AnyWidget(widget, sizing_mode="stretch_width")

# ---------------------------------------------------------------------------
# 3. Panel controls for switching datasets
# ---------------------------------------------------------------------------

dataset_selector = pn.widgets.Select(
    name="Switch Dataset",
    options=list(DATASETS.keys()),
    value="Weather (3D)",
    width=300,
)

dataset_info = pn.pane.Markdown("", sizing_mode="stretch_width")


def update_info(ds_name):
    ds = DATASETS[ds_name]
    dims = ", ".join(f"{k}: {v}" for k, v in ds.dims.items())
    dvars = ", ".join(ds.data_vars)
    return (
        f"**Dimensions:** {dims}\n\n"
        f"**Variables:** {dvars}\n\n"
        f"**Attributes:** {ds.attrs.get('title', 'N/A')}"
    )


dataset_info.object = update_info("Weather (3D)")


def on_dataset_change(event):
    ds = DATASETS[event.new]
    try:
        new_widget = XarrayWidget(ds)
        anywidget_pane.object = new_widget
    except TypeError:
        pass  # xarray version incompatibility
    dataset_info.object = update_info(event.new)


dataset_selector.param.watch(on_dataset_change, "value")

# ---------------------------------------------------------------------------
# 4. Layout
# ---------------------------------------------------------------------------

if _xarray_repr_works:
    status_banner = pn.pane.Markdown("""
<div style="background-color: #d4edda; border: 2px solid #28a745; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #155724; font-size: 20px; font-weight: bold; margin: 0;">
WORKS
</p>
<p style="color: #155724; font-size: 15px; margin: 8px 0 0 0;">
The xarray Dataset HTML tree view renders correctly with collapsible sections.
Switching datasets re-creates the widget and re-renders.
All synced traits are private (underscore-prefixed), so no trait name collisions.
</p>
</div>
""", sizing_mode="stretch_width")
else:
    status_banner = pn.pane.Markdown("""
<div style="background-color: #fff3cd; border: 2px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0;">
<p style="color: #856404; font-size: 20px; font-weight: bold; margin: 0;">
WORKS WITH CAVEATS
</p>
<p style="color: #856404; font-size: 15px; margin: 8px 0 0 0;">
<code>xarray-fancy-repr==0.0.2</code> has an upstream compatibility issue with
newer xarray versions: <code>inline_index_repr()</code> signature changed,
causing a <code>TypeError</code> when creating widgets with indexed coordinates.
Simple datasets (no coordinates) render correctly. The AnyWidget pane integration
itself works fine.
</p>
</div>
""", sizing_mode="stretch_width")

header = pn.pane.Markdown("""
# xarray-fancy-repr -- Interactive Dataset Viewer

**[xarray-fancy-repr](https://github.com/benbovy/xarray-fancy-repr)** provides a
rich, interactive HTML representation of xarray Datasets and DataArrays as an
anywidget. It renders the same collapsible tree view you see in Jupyter notebooks.

## How to Use

1. **Explore the tree:** Click on dimension and variable headers to
   expand or collapse sections in the dataset viewer.
2. **Switch datasets:** Use the dropdown on the right to load a
   different sample dataset.
3. The widget re-creates when the dataset changes.

## Notes

- All synced traitlets are underscore-prefixed (private), so there
  are no trait name collisions with Panel or Bokeh.
- The widget communicates dataset structure (dims, coords, data vars,
  attributes) to the browser, not the raw array data.
""", sizing_mode="stretch_width")

controls = pn.Column(
    pn.pane.Markdown("## Controls"),
    dataset_selector,
    pn.pane.Markdown("## Dataset Info"),
    dataset_info,
    width=350,
)

pn.Column(
    status_banner,
    header,
    pn.Row(
        pn.Column(
            pn.pane.Markdown("### Dataset Viewer"),
            anywidget_pane,
            min_width=500,
        ),
        controls,
    ),
    sizing_mode="stretch_width",
    max_width=1000,
).servable()
