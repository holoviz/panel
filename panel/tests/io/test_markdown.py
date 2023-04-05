from io import StringIO

from panel.io.markdown import extract_code

md1 = """
```panel
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
```panel
import panel as pn
pn.extension()
```

My description

```panel
pn.Row(1, 2, 3).servable()
```
"""

md4 = """
# My app

```panel
import panel as pn
pn.extension(template='fast')

pn.Row(1, 2, 3).servable()
```
"""

def test_extract_panel_block():
    f = StringIO(md1)
    assert extract_code(f) == "import panel as pn\n\npn.Row(1, 2, 3).servable()\n"

def test_extract_pyodide_block():
    f = StringIO(md2)
    assert extract_code(f) == "import panel as pn\n\npn.Row(1, 2, 3).servable()\n"

def test_extract_description_block():
    f = StringIO(md3)
    assert extract_code(f) == "import panel as pn\n\npn.extension()\n\npn.pane.Markdown('My description\\n').servable()\n\npn.Row(1, 2, 3).servable()\n"

def test_extract_title_block():
    f = StringIO(md4)
    assert extract_code(f) == "import panel as pn\n\npn.extension(template='fast')\n\npn.Row(1, 2, 3).servable()\n\npn.state.template.title = 'My app'"
