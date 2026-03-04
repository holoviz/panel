"""
Parametrized Playwright test for AnyWidgetComponent doc examples.

Each example in anywidget_component_examples/ defines a `component` variable.
This test imports each, serves it, waits for render, and checks for console errors.

CDN-dependent examples get a longer timeout.
"""
from __future__ import annotations

import importlib
import pathlib
import sys

import pytest

import panel as pn

pytest.importorskip("playwright")

from panel.tests.util import serve_component

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui

EXAMPLES_DIR = pathlib.Path(__file__).parents[4] / "anywidget_component_examples"

# Examples that load external CDN resources and need longer timeout
CDN_EXAMPLES = {
    "confetti_direct",
    "confetti_importmap",
    "react_counter",
    "split_layout",
    "grid_layout",
    "chartjs",
    "cytoscape",
    "image_button",
}

# Collect all .py example files
EXAMPLE_FILES = sorted(EXAMPLES_DIR.glob("*.py"))
EXAMPLE_IDS = [f.stem for f in EXAMPLE_FILES]


def _import_example(py_file: pathlib.Path):
    """Dynamically import an example module and return its `component`."""
    module_name = f"_anywidget_example_{py_file.stem}"
    spec = importlib.util.spec_from_file_location(module_name, py_file)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return getattr(mod, "component", None)


@pytest.mark.parametrize("example_file", EXAMPLE_FILES, ids=EXAMPLE_IDS)
def test_anywidget_component_example(page, example_file):
    """Each AnyWidgetComponent example renders without console errors."""
    component = _import_example(example_file)
    assert component is not None, f"Example {example_file.name} has no 'component' variable"

    # Wrap in a pane if not already a Panel object
    if not isinstance(component, pn.viewable.Viewable):
        component = pn.panel(component)

    is_cdn = example_file.stem in CDN_EXAMPLES
    timeout = 15000 if is_cdn else 10000

    msgs, _ = serve_component(page, component)
    wait_for_anywidget(page, timeout=timeout)

    assert_no_console_errors(msgs)
