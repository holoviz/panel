# CodeEditor
---
```python
import panel as pn
import param

pn.extension('codeeditor')
```

The ``CodeEditor`` widget allows embedding a code editor based on [Ace](https://ace.c9.io/).

Only a small subset of Ace functionality is currently enabled:

 - **syntax highlighting** for several languages
 - **themes**
 - basic **completion** support via `ctrl+space` (using only static analysis of the code)
 - **annotations**
 - **readonly** mode

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``annotations``** (list): list of annotations. An annotation is a dict with the following keys:
    - `'row'`: row in the editor of the annotation
    - `'column'`: column of the annotation
    - `'text'`: text displayed when hovering over the annotation
    - `'type'`: type of annotation and the icon displayed {`warning` | `error`}
* **``filename``** (str): If filename is provided the file extension will be used to determine the language
* **``indent``** (int): Number of spaces to use for default indentation.
* **``language``** (str): A string declaring which language to use for code syntax highlighting (default: 'text')
* **``on_keyup``** (bool): Whether to update the value on every key press or only upon loss of focus / hotkeys.
* **``print_margin``** (boolean): Whether to show a print margin in the editor
* **``soft_tabs``** (boolean): Whether to use spaces instead of tabs for indentation.
* **``theme``** (str): If no value is provided, it defaults to the current theme set by pn.config.theme, as specified in the CodeEditor.THEME_CONFIGURATION dictionary. If not defined there, it falls back to the default parameter value ('chrome').
* **``readonly``** (boolean): Whether the editor should be opened in read-only mode
* **``value``** (str): State of the current code in the editor if `on_keyup`. Otherwise, only upon loss of focus, i.e. clicking outside the editor, or pressing <Ctrl+Enter> or <Cmd+Enter>.
* **``value_input``** (str): State of the current code updated on every key press. Identical to `value` if `on_keyup`.

##### Display

* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

To construct an `Ace` widget we must define it explicitly using `pn.widgets.Ace`. We can add some text as initial code.
Code inserted in the editor is automatically reflected in the `value_input` and `value`.

```python
py_code = "import sys"
editor = pn.widgets.CodeEditor(value=py_code, sizing_mode='stretch_width', language='python', height=300)
editor
```

we can add some code in it

```python
editor.value += """
import Math

x = Math.cos(x)**2 + Math.cos(y)**2
"""
```

By default, the code editor will update the `value` on every key press, but you can set `on_keyup=False` to only update the `value` when the editor loses focus or pressing `<Ctrl+Enter>`/ `<Cmd+Enter>`. Here, the code is printed when `value` is changed.

```python
def print_code(value):
    print(value)

editor = pn.widgets.CodeEditor(value=py_code, on_keyup=False)
pn.bind(print_code, editor.param.value)
```

We can change language and theme of the editor

```python
html_code = r"""<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <title>`substitute(Filename('', 'Page Title'), '^.', '\u&', '')`</title>
    </head>
    <body>
        <h1>Title1</h1>
        <h2>Title2</h2>
        Paragraph
    </body>
</html>
"""
editor.language = "html"
editor.theme = "monokai"
editor.value = html_code
```

We can add some annotations to the editor

```python
editor.annotations = [
    dict(row=1, column=0, text='an error', type='error'),
    dict(row=2, column=0, text='a warning', type='warning')
]
```

If we want just to display editor content but not edit it we can set the `readonly` property to `True`

```python
#editor.readonly = True
```

If instead of setting the language explicitly we want to set the filename and automatically detect the language based on the file extension we can do that too:

```python
editor.filename = 'test.html'
```

### Including the CodeEditor editor in a parameterized class

You can view the Ace widget as part of a `param.Parameterized` class:

```python
from panel.viewable import Viewer

class CodeEditorTest(Viewer):
    
    editor = param.String('Hello World')
    
    def __panel__(self):
        """ Map the string to appear as an Ace editor. """
        return pn.Param(
            self.param,
            widgets=dict(
                editor=dict(
                    type=pn.widgets.CodeEditor,
                    language='python',
                )
            )
        )
    
edit = CodeEditorTest()

edit
```

### Controls

The `CodeEditor` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
widget = pn.widgets.CodeEditor(label='CodeEditor', value=py_code, language='python', sizing_mode='stretch_both', min_height=300)

pn.Row(widget.controls(jslink=True), widget, sizing_mode='stretch_both')
```

Try changing the filename including a file extension and watch the language automatically update.

---
