# Markdown
---
```python
import panel as pn

pn.extension('mathjax')
```

The `Markdown` pane allows rendering arbitrary [Markdown](https://python-markdown.github.io) in a panel. It renders strings containing valid Markdown as well as objects with a `_repr_markdown_` method, and may define custom CSS styles.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **`dedent`** (bool, `default=True`): Whether to dedent common whitespace across all lines.
* **`disable_anchors`** (boolean, `default=False`): Whether to disable automatically adding anchors to headings.
* **`disable_math`** (boolean, `default=False`): Whether to disable MathJax math rendering for strings escaped with `$$` delimiters.
* **`enable_streaming`** (boolean, `default=False`): Whether to enable streaming of text snippets. This will diff the `object` when it is updated and only send the trailing chunk that was added.
* **`extensions`** (list): A list of [Python-Markdown extensions](https://python-markdown.github.io/extensions/) to use (does not apply for 'markdown-it' and 'myst' renderers).
* **`hard_line_break`** (bool, `default=False`): Whether simple new lines are rendered as hard line breaks. False by default to conform with the original Markdown spec. Not supported by the `'myst'` renderer.
* **`object`** (str or object): A string containing Markdown, or an object with a ``_repr_markdown_`` method.
* **`plugins`** (function): A list of additional markdown-it-py plugins to apply.
* **`renderer`** (literal: `'markdown-it'`, `'markdown'`, `'myst'`): Markdown renderer implementation.
* **`renderer_options`** (dict): Options to pass to the markdown renderer.

___

The `Markdown` pane accepts all *basic* Markdown syntax, including embedded HTML. It also supports most of the *extended* Markdown syntax.

````python
pn.pane.Markdown("""

# Markdown Sample

This sample text is from [The Markdown Guide](https://www.markdownguide.org)!

## Basic Syntax

These are the elements outlined in John Gruber’s original design document. All Markdown applications support these elements.

### Heading

# H1
## H2
### H3

### Bold

**bold text**

### Italic

*italicized text*

### Blockquote

> blockquote

### Ordered List

1. First item
2. Second item
3. Third item

### Unordered List

- First item
- Second item
- Third item

### Code

`code`

### Horizontal Rule

---

### Link

[Markdown Guide](https://www.markdownguide.org)

### Image

![alt text](https://www.markdownguide.org/assets/images/tux.png)

## Extended Syntax

These elements extend the basic syntax by adding additional features. Not all Markdown applications support these elements.

### Table

| Syntax | Description |
| ----------- | ----------- |
| Header | Title |
| Paragraph | Text |

### Fenced Code Block

```
{
  "firstName": "John",
  "lastName": "Smith",
  "age": 25
}
```

### Footnote

Here's a sentence with a footnote. [^1]

[^1]: This is the footnote.

### Definition List

term
: Some definition of the term goes here

### Strikethrough

~~The world is flat.~~

### Task List

- [x] Write the press release
- [ ] Update the website
- [ ] Contact the media

### Emoji

That is so funny! 😂

(See also [Copying and Pasting Emoji](https://www.markdownguide.org/extended-syntax/#copying-and-pasting-emoji))

""", width=500)
````

## Style

If you want to control the behavior of the HTML that is generated from the Markdown source, it is often possible to do that by passing parameters to the `styles` parameter of this pane.  For instance, you can add a blue border around a Markdown table as follows:

```python
pn.pane.Markdown("""
| Syntax | Description |
| ----------- | ----------- |
| Header | Title |
| Paragraph | Text |

""", styles={'border': "4px solid blue"})
```

However, styles specified in this way will only be applied to the outermost Div, and there is not currently any way to apply styling in this way to specific internal elements of the HTML.  In this case, we cannot use the `styles` parameter to control styling of the rows or headings of the generated table.

If we do want to change specific internal elements of the generated HTML, we can do so by providing an HTML/CSS &lt;style&gt; section. For instance, we can change the border thickness for headers and data as follows, but note that the changes will apply to subsequent Markdown as well, including other cells if in a notebook context:

(For this reason the code here saves the result to a separate HTML file, to avoid changing the style for all other tables).

````python
import panel as pn
from bokeh.resources import INLINE
SimpleTable = pn.pane.Markdown("""

| Syntax | Description |
| ----------- | ----------- |
| Header | Title |
| Paragraph | Text |

""")

SimpleTable.save('SimpleTable', resources=INLINE)
````

If you want to change styling only for a specific bit of Markdown text, you can easily do so by adding CSS classes that you can target with a stylesheet you pass to the component. Here we add the `special_table` class followed by the table use a red border:

```python
css = """
div.special_table + table * {
  border: 1px solid red;
}
"""

pn.panel("""

| Syntax | Description |
| ----------- | ----------- |
| Header | Title |
| Paragraph | Text |

""", stylesheets=[css])
```

## Code Highlighting

To enable code highlighting in code blocks, `pip install pygments`
:::

## Renderer

Since the 1.0 release Panel uses `markdown-it` as the the default markdown renderer. If you want to restore the previous default `'markdown'` or switch to `MyST` flavored Markdown you can set it via the `renderer` parameter. As an example here we render a task list using 'markdown-it' and 'markdown':

```python
tasklist = """
- [ ] Eggs
- [x] Flour
- [x] Milk
"""

pn.Row(
    pn.pane.Markdown(tasklist, renderer='markdown-it'),
    pn.pane.Markdown(tasklist, renderer='markdown')
)
```

## LaTeX Support

The `Markdown` pane also supports math rendering by encapsulating the string to be rendered with ``$$`` delimiters. To enable LaTeX rendering you must load the 'mathjax' extensions explicitly in the `pn.extension` call.

```python
pn.pane.Markdown(r"""
The Markdown pane supports math rendering for string encapsulated with double $ delimiters: $$\sum_{j}{\sum_{i}{a*w_{j, i}}}$$
""", width=800)
```

Please note the use of the `r` prefix to create the string as a *raw* strings. Python raw string treats the backslash character (\\) as a literal character. For example this won't work

```python
pn.pane.Markdown("$$\frac{1}{n}$$")
```

But prefixing with `r` will work

```python
pn.pane.Markdown(r"$$\frac{1}{n}$$")
```

## New Lines

Markdown renderers typically do not interpret new lines as hard line breaks. According to the Markdown standard, a hard line break requires the line to end with either *two spaces* or a *backslash*. Otherwise, it is treated as a soft line break. By default, Panel adheres to this standard, respecting the behavior where simple new lines are not displayed as hard line breaks.

```python
pn.pane.Markdown("""
Markdown displayed
on two lines.
""")
```

Rendering simple new lines as hard line breaks can be enabled for all renderers but `'myst'` by setting `hard_line_break` to `True`.

```python
pn.pane.Markdown("""
Markdown displayed
on one line.

Markdown displayed on multiple lines  
as each line ends with two spaces,  
despite hard_line_break=True
""", hard_line_break=True)
```

---
