# Construct Panes

There are two main ways to construct a pane - explicitly or automatically.

To explicitly construct a pane, use one of the pane types listed in the [reference gallery](../../reference/index.html#panes). For example, you can create a Markdown pane as follows:

```{pyodide}
pn.pane.Markdown('''
# H1
## H2
### H3
''')
```

Alternatively, you can create a pane using the `pn.panel()` utility to automatically infer the pane type from the object being passed as the argument. This utility resolves the appropriate representation for an object by checking all Pane object types available and then ranking them by priority. For example, when passing a string there are many representations, but the PNG pane takes precedence if the string is a valid URL or local file path ending in ".png":

```{pyodide}
png = pn.panel('https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png', width=500)

png
```

:::{admonition} Learn More
:class: info

Learn more about Panes in the (Background for Components)[../background/components/components_overview.md#Panes]
:::