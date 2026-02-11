import panel as pn

pn.extension(sizing_mode="stretch_width")

SAMPLE = """# Hello Markdown

This is a **live preview** editor.

- Item one
- Item two
- Item three

> Blockquotes work too!

`inline code` and:

```python
print("Hello, world!")
```
"""

editor = pn.widgets.TextAreaInput(name="Markdown Source", value=SAMPLE, height=350)

pn.Row(
    pn.Card(editor, title="Editor", width=450),
    pn.Card(pn.bind(lambda md: pn.pane.Markdown(md), editor), title="Preview"),
).servable()
