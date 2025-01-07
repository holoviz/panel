"""
The ref_available tests verify that all of the panes, layouts, and widgets defined by panel are
represented in the reference gallery.

The doc_available tests check that python in markdown files can be run top to bottom.

"""
import ast
import runpy

from inspect import isclass
from pathlib import Path

import pytest

import panel as pn

pytestmark = pytest.mark.docs

REF_PATH = Path(__file__).parents[2] / "examples" / "reference"
ref_available = pytest.mark.skipif(not REF_PATH.is_dir(), reason="folder 'examples/reference' not found")

DOC_PATH = Path(__file__).parents[2] / "doc"
IGNORED = ['vtk']
doc_files = [df for df in sorted(DOC_PATH.rglob("*.md")) if not any(ig in str(df).lower() for ig in IGNORED)]
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
    exceptions = {"Ace", "CompositeWidget", "Widget", "ToggleGroup", "NumberInput", "Spinner"}
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
    exceptions = {
        "PaneBase", "Pane", "YT", "RGGPlot", "Interactive", "ICO", "Image",
        "IPyLeaflet", "ParamFunction", "ParamMethod", "ParamRef"
    }
    docs = {f.with_suffix("").name for f in (REF_PATH / "panes").iterdir()}

    def is_panel_pane(attr):
        pane = getattr(pn.pane, attr)
        return isclass(pane) and issubclass(pane, pn.pane.PaneBase)

    panes = set(filter(is_panel_pane, dir(pn.pane)))
    assert panes - exceptions - docs == set()


def find_indexed(index):
    indexed = []
    toctree = False
    for line in index.read_text(encoding="utf-8").split('\n'):
        if line == '```{toctree}':
            toctree = True
        elif not toctree:
            continue
        elif line.startswith('```'):
            toctree = False
        elif line and not line.startswith(':'):
            if '<' in line:
                line = line[line.index('<')+1:].rstrip('>')
            indexed.append(line)
    return indexed

@doc_available
@pytest.mark.parametrize(
    "doc_file", doc_files, ids=[str(f.relative_to(DOC_PATH)) for f in doc_files]
)
def test_markdown_indexed(doc_file):
    # Check all non-index and example files are indexed
    if str(doc_file).endswith('index.md') or doc_file.parent.name == 'examples':
        return
    index_page = doc_file.parent / 'index.md'
    filename = doc_file.name[:-3]
    if index_page.is_file():
        indexed = find_indexed(index_page)
        assert filename in indexed
    else:
        parent_name = doc_file.parent.name
        index_page = doc_file.parent.parent / f'{parent_name}.md'
        if not index_page.is_file():
            index_page = doc_file.parent.parent / 'index.md'
        indexed = find_indexed(index_page)
        assert f'{parent_name}/{filename}' in indexed

@doc_available
@pytest.mark.parametrize(
    "file", doc_files, ids=[str(f.relative_to(DOC_PATH)) for f in doc_files]
)
async def test_markdown_codeblocks(file, tmp_path):
    from markdown_it import MarkdownIt

    exceptions = ("await", "pn.serve", "django", "raise", "display(")

    md_ast = MarkdownIt().parse(file.read_text(encoding="utf-8"))
    lines = ""
    for n in md_ast:
        if n.tag == "code" and n.info is not None:
            if "pyodide" in n.info.lower():
                if ">>>" not in n.content:
                    lines += n.content
    if not lines:
        return

    ast.parse(lines)

    if any(w in lines for w in exceptions):
        return

    mod = tmp_path / f'{file.stem}.py'

    with open(mod, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    runpy.run_path(str(mod))


@doc_available
@pytest.mark.parametrize(
    "file", doc_files, ids=[str(f.relative_to(DOC_PATH)) for f in doc_files]
)
def test_colon_blocks_symmetric(file):
    stack = []
    for i, line in enumerate(file.read_text(encoding='utf-8').splitlines(), 1):
        if ':::::' in line:
            # Not checking triple nesting
            stack.clear()
            break
        elif '::::' in line:
            if stack:
                assert stack[-1] == '::::', f'Expected ::: on line {i}, found ::::'
                stack.pop()
            else:
                stack.append('::::')
        elif ':::' in line:
            if not stack or stack[-1] == '::::':
                stack.append(':::')
            else:
                stack.pop()
    assert not stack, 'Colon blocks were not symmetric, ensure all blocks were closed'
