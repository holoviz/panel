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
    import pandas as pd
    import polars as pl
else:
    pd = optional_dependencies("pandas")
    pl = optional_dependencies("polars")


_skip = lambda module, name: pytest.mark.skipif(module is None, reason=f"{name} is not installed")
pd_skip = _skip(pd, "pandas")
pl_skip = _skip(pl, "polars")
