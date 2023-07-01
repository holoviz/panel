# Develop Apps in an Editor

This guide addresses how to rapidly develop a Panel application in your favorite IDE or editor.

---

You can edit your Panel code as a ``.py`` file in any text editor, marking the objects you want to render as ``.servable()``. For example:

:::{card} app.py
```{code-block} python
:emphasize-lines: 14

import panel as pn
import hvplot.pandas
from bokeh.sampledata.autompg import autompg

columns = list(autompg.columns[:-2])

x = pn.widgets.Select(value='mpg', options=columns, name='x')
y = pn.widgets.Select(value='hp', options=columns, name='y')
color = pn.widgets.ColorPicker(name='Color', value='#AA0505')

pn.Row(
    pn.Column('## MPG Explorer', x, y, color),
    pn.bind(autompg.hvplot.scatter, x, y, c=color)
).servable()
```
:::

Then, from the command line, launch a server with:

```bash
panel serve app.py --show --autoreload
```

:::{admonition} Note
The `--show` flag will open a browser tab with the live app and the ``--autoreload`` flag ensures that the app reloads whenever you make a change to the Python source.
:::

![App Developed in an Editor](../../_static/editor_server_app.png)

## Debugging

The simplest way to debug is to insert a `breakpoint()` in your code and then serve your app from a terminal. Type `help` in the debugger to see the available *commands*.

<img src="../../_static/terminal-breakpoint.png" styles="max-height:300px;max-width:100%"></img>

If your editor or IDE provides *integrated debugging* you can also use that. You can do that in one of two ways

- Use `.show()` on a single Panel component or
- Use `.servable()` and configure your editor to start debugging using the command `python -m panel serve <name-of-script.py>`.

## Related Resources

- [VS Code Guide](vscode.md)
