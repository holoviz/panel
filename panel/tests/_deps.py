from __future__ import annotations

import importlib

from importlib.util import find_spec
from typing import TYPE_CHECKING

import pytest


def _is_installed(module_name: str) -> bool:
    # So we don't accidentally import it
    module_name, *_ = module_name.split(".")
    return find_spec(module_name) is not None

def optional_dependencies(*names: str):
    """Check if a dependency is installed and return the module and a fixture that skips test."""
    if all(map(_is_installed, names)):
        return importlib.import_module(names[0])

if TYPE_CHECKING:
    import holoviews as hv
    import jupyter_bokeh
    import matplotlib as mpl
    import pandas as pd
    import polars as pl
    import streamz
else:
    hv = optional_dependencies("holoviews")
    jupyter_bokeh = optional_dependencies("jupyter_bokeh")
    mpl = optional_dependencies("matplotlib")
    pd = optional_dependencies("pandas")
    pl = optional_dependencies("polars")
    streamz = optional_dependencies("streamz", "pandas")


_skip = lambda module, name: pytest.mark.skipif(module is None, reason=f"{name} is not installed")
hv_skip = _skip(hv, "holoviews")
jupyter_bokeh_skip = _skip(jupyter_bokeh, "jupyter_bokeh")
mpl_skip = _skip(mpl, "matplotlib")
pd_skip = _skip(pd, "pandas")
pl_skip = _skip(pl, "polars")
streamz_skip = _skip(streamz, "streamz")

if mpl:
    mpl.use("Agg")
