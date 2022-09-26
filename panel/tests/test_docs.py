"""
The ref_available tests verify that all of the panes, layouts, and widgets defined by panel are
represented in the reference gallery.

The doc_available tests check that python in markdown files can be run top to bottom.

"""
import ast

from inspect import isclass
from pathlib import Path
from subprocess import run

import pytest

import panel as pn

REF_PATH = Path(__file__).parents[2] / "examples" / "reference"
ref_available = pytest.mark.skipif(not REF_PATH.is_dir(), reason="folder 'examples/reference' not found")

DOC_PATH = Path(__file__).parents[2] / "doc"
doc_files = sorted(DOC_PATH.rglob("*.md"))
doc_available = pytest.mark.skipif(not DOC_PATH.is_dir(), reason="folder 'doc' not found")


@ref_available
def test_layouts_are_in_reference_gallery():
    exceptions = {"ListPanel", "Panel"}
    docs = {f.with_suffix("").name for f in (REF_PATH / "layouts").iterdir()}

    def is_panel_layout(attr):
        layout = getattr(pn.layout, attr)
        return isclass(layout) and issubclass(layout, pn.layout.Panel)

    layouts = set(filter(is_panel_layout, dir(pn.layout)))
    assert layouts - exceptions - docs == set()


@ref_available
def test_widgets_are_in_reference_gallery():
    exceptions = {"CompositeWidget", "Widget", "ToggleGroup", "NumberInput", "Spinner"}
    docs = {
        f.with_suffix("").name
        for g in ("indicators", "widgets")
        for f in (REF_PATH / g).iterdir()
    }

    def is_panel_widget(attr):
        widget = getattr(pn.widgets, attr)
        return isclass(widget) and issubclass(widget, pn.widgets.Widget)

    widgets = set(filter(is_panel_widget, dir(pn.widgets)))
    assert widgets - exceptions - docs == set()


@ref_available
def test_panes_are_in_reference_gallery():
    exceptions = {"PaneBase", "YT", "RGGPlot", "Interactive", "ICO"}
    docs = {f.with_suffix("").name for f in (REF_PATH / "panes").iterdir()}

    def is_panel_pane(attr):
        pane = getattr(pn.pane, attr)
        return isclass(pane) and issubclass(pane, pn.pane.PaneBase)

    panes = set(filter(is_panel_pane, dir(pn.pane)))
    assert panes - exceptions - docs == set()


@doc_available
@pytest.mark.parametrize(
    "file", doc_files, ids=[str(f.relative_to(DOC_PATH)) for f in doc_files]
)
def test_markdown_codeblocks(file):
    from markdown_it import MarkdownIt

    exceptions = ("await", "pn.serve", "django")

    md_ast = MarkdownIt().parse(file.read_text(encoding="utf-8"))
    lines = ""
    for n in md_ast:
        if n.tag == "code" and n.info is not None:
            if "pyodide" in n.info.lower() or "python" in n.info.lower():
                if ">>>" not in n.content:
                    lines += n.content
    if lines:
        ast.parse(lines)

    if lines and not any(w in lines for w in exceptions):
        run(["python", "-c", lines], timeout=30, check=True)
