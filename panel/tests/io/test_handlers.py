from io import StringIO

import pytest

from panel.io.handlers import (
    _create_copy_button, capture_code_cell, extract_code, parse_notebook,
)
from panel.widgets import ButtonIcon

try:
    import nbformat
except Exception:
    nbformat = None  # type: ignore
nbformat_available = pytest.mark.skipif(nbformat is None, reason="requires nbformat")


md1 = """
```python
import panel as pn

pn.Row(1, 2, 3).servable()
```
"""

md2 = """
```{pyodide}
import panel as pn

pn.Row(1, 2, 3).servable()
```
"""

md3 = """
```python
import panel as pn
pn.extension()
```

My description

```python
pn.Row(1, 2, 3).servable()
```
"""

md4 = """
# My app

```python
import panel as pn
pn.extension(template='fast')

pn.Row(1, 2, 3).servable()
```
"""

code_statement = """
import panel"""

code_loop = """
for i in range(10):
    print(i)"""

code_expr_semicolon = """
1+1;"""

code_expr = """
1+1"""

code_expr_comment = """
1+1 # Some comment"""

code_multi_line = """
pd.read_csv(
    'test.csv'
)"""

code_function = """
def foo():
    # Comment
    return 1+1
"""

code_expr_multi_line_with_comment = """
(
  1 + 1 # Comment
)
"""

def test_extract_panel_block():
    f = StringIO(md1)
    assert extract_code(f) == "import panel as pn\n\n\n\npn.Row(1, 2, 3).servable()\n"

def test_extract_pyodide_block():
    f = StringIO(md2)
    assert extract_code(f) == "import panel as pn\n\n\n\npn.Row(1, 2, 3).servable()\n"

def test_extract_description_block():
    f = StringIO(md3)
    assert extract_code(f) == "import panel as pn\n\npn.extension()\n\npn.pane.Markdown('\\nMy description\\n\\n').servable()\n\npn.Row(1, 2, 3).servable()\n"

def test_extract_title_block():
    f = StringIO(md4)
    assert extract_code(f) == "import panel as pn\n\npn.extension(template='fast')\n\n\n\npn.Row(1, 2, 3).servable()\n\npn.state.template.title = 'My app'"

def test_capture_code_cell_statement():
    assert capture_code_cell({'id': 'foo', 'source': code_statement}) == ['', 'import panel']

def test_capture_code_cell_loop():
    assert capture_code_cell({'id': 'foo', 'source': code_loop}) == ['', 'for i in range(10):\n    print(i)']

def test_capture_code_cell_expression_semicolon():
    assert capture_code_cell({'id': 'foo', 'source': code_expr_semicolon}) == ['', '1+1;']

def test_capture_code_cell_expression():
    assert capture_code_cell({'id': 'foo', 'source': code_expr}) == [
        '', """\
_pn__state._cell_outputs['foo'].append((1+1))
for _cell__out in _CELL__DISPLAY:
    _pn__state._cell_outputs['foo'].append(_cell__out)
_CELL__DISPLAY.clear()
_fig__out = _get__figure()
if _fig__out:
    _pn__state._cell_outputs['foo'].append(_fig__out)
"""]

def test_capture_code_cell_function():
    assert capture_code_cell({'id': 'foo', 'source': code_function}) == [
        '', 'def foo():\n    # Comment\n    return 1+1\n'
   ]

def test_capture_code_expression_multi_line_with_comment():
    assert capture_code_cell({'id': 'foo', 'source': code_expr_multi_line_with_comment}) == [
        '', """\
_pn__state._cell_outputs['foo'].append(((
  1 + 1 # Comment
)
))
for _cell__out in _CELL__DISPLAY:
    _pn__state._cell_outputs['foo'].append(_cell__out)
_CELL__DISPLAY.clear()
_fig__out = _get__figure()
if _fig__out:
    _pn__state._cell_outputs['foo'].append(_fig__out)
"""]


def test_capture_code_cell_multi_line_expression():
    assert capture_code_cell({'id': 'foo', 'source': code_multi_line}) == [
        '', """\
_pn__state._cell_outputs['foo'].append((pd.read_csv(
    'test.csv'
)))
for _cell__out in _CELL__DISPLAY:
    _pn__state._cell_outputs['foo'].append(_cell__out)
_CELL__DISPLAY.clear()
_fig__out = _get__figure()
if _fig__out:
    _pn__state._cell_outputs['foo'].append(_fig__out)
"""]

def test_capture_code_cell_expression_with_comment():
    assert capture_code_cell({'id': 'foo', 'source': code_expr_comment}) == [
        '', """\
_pn__state._cell_outputs['foo'].append((1+1))
for _cell__out in _CELL__DISPLAY:
    _pn__state._cell_outputs['foo'].append(_cell__out)
_CELL__DISPLAY.clear()
_fig__out = _get__figure()
if _fig__out:
    _pn__state._cell_outputs['foo'].append(_fig__out)
"""]


@nbformat_available
def test_parse_notebook_loads_layout():
    cell = nbformat.v4.new_code_cell('1+1', metadata={'panel-layout': 'foo'})
    nb = nbformat.v4.new_notebook(cells=[cell])
    sio = StringIO(nbformat.v4.writes(nb))
    nb, code, layout = parse_notebook(sio)

    assert layout == {cell.id: 'foo'}
    assert code.startswith(f"_pn__state._cell_outputs['{cell.id}'].append((1+1))")

@nbformat_available
def test_parse_notebook_markdown_escaped():
    cell = nbformat.v4.new_markdown_cell('This is a test of markdown terminated by a quote"')
    nb = nbformat.v4.new_notebook(cells=[cell])
    sio = StringIO(nbformat.v4.writes(nb))
    nb, code, layout = parse_notebook(sio)

    assert code == f"_pn__state._cell_outputs['{cell.id}'].append(\"\"\"This is a test of markdown terminated by a quote\\\"\"\"\")"

def test_create_copy_button():
    """Test that _create_copy_button creates a ButtonIcon with correct properties."""


    # Full error text from the user's example
    full_error_text = """Exception: bla bla bla."""

    # Create the copy button
    copy_button = _create_copy_button(full_error_text)

    # Test that it's a ButtonIcon widget
    assert isinstance(copy_button, ButtonIcon)

    # Test the button properties
    assert copy_button.icon == "clipboard"

    # Test the styling
    styles = copy_button.styles
    assert styles['position'] == 'absolute'
