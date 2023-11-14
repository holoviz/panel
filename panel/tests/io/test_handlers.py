from io import StringIO

from panel.io.handlers import capture_code_cell, extract_code

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
    assert capture_code_cell({'id': 'foo', 'source': code_loop}) == ['', 'for i in range(10):', '    print(i)']

def test_capture_code_cell_expression_semicolon():
    assert capture_code_cell({'id': 'foo', 'source': code_expr_semicolon}) == ['', '1+1;']

def test_capture_code_cell_expression():
    assert capture_code_cell({'id': 'foo', 'source': code_expr}) == [
        '', """
_pn__state._cell_outputs['foo'].append((1+1))
for _cell__out in _CELL__DISPLAY:
    _pn__state._cell_outputs['foo'].append(_cell__out)
_CELL__DISPLAY.clear()
_fig__out = _get__figure()
if _fig__out:
    _pn__state._cell_outputs['foo'].append(_fig__out)
"""]

def test_capture_code_cell_expression_with_comment():
    assert capture_code_cell({'id': 'foo', 'source': code_expr_comment}) == [
        '', """
_pn__state._cell_outputs['foo'].append((1+1))
for _cell__out in _CELL__DISPLAY:
    _pn__state._cell_outputs['foo'].append(_cell__out)
_CELL__DISPLAY.clear()
_fig__out = _get__figure()
if _fig__out:
    _pn__state._cell_outputs['foo'].append(_fig__out)
"""]
