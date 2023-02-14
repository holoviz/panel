# Apply CSS

This guide addresses how to apply custom CSS styling.

---

CSS styles can be embedded in raw form or by referencing an external .css file. All that is needed is to provide a list to the ``pn.config.raw_css`` or ``pn.config.js_files`` config parameters, respectively. Then, the ``css_classes`` parameter can be used to apply this CSS styling to a Panel component.

First, we define custom CSS classes:

```{pyodide}
import panel as pn

css_border = '''
.bk.panel-widget-box {
  border-radius: 5px;
  border: 1px black solid;
}
'''

css_bg = '''
.bk.panel-widget-background {
  background: #00aa41;
}
'''
```
Next, we pass the custom CSS classes to the panel config using the `raw_css` parameter:

```{pyodide}
pn.config.raw_css = [css_border, css_bg]

```

If we are working in a notebook, we can now activate the panel extension after having set the config parameters. Alternatively, we could have added the CSS using `pn.extension(raw_css=[])` for raw CSS or `pn.extension(css_files=[])` for external CSS files.

```{pyodide}

pn.extension() # for notebook

```

Finally, we can apply our custom CSS class to components using the `css_classes` parameter:

```{pyodide}
pn.Column(
    pn.widgets.FloatSlider(name='Number', margin=(10, 5, 5, 10)),
    pn.widgets.Select(name='Fruit', options=['Apple', 'Orange', 'Pear'], margin=(0, 5, 5, 10)),
    pn.widgets.Button(name='Run', margin=(5, 10, 10, 10)),
css_classes=['panel-widget-box', 'panel-widget-background'])
```

Here is the complete code in case you want to easily copy it:
```{pyodide}
import panel as pn

css_border = '''
.bk.panel-widget-box {
  border-radius: 5px;
  border: 1px black solid;
}
'''

css_bg = '''
.bk.panel-widget-background {
  background: #00aa41;
}
'''

pn.config.raw_css = [css_border, css_bg]

pn.Column(
    pn.widgets.FloatSlider(name='Number', margin=(10, 5, 5, 10)),
    pn.widgets.Select(name='Fruit', options=['Apple', 'Orange', 'Pear'], margin=(0, 5, 5, 10)),
    pn.widgets.Button(name='Run', margin=(5, 10, 10, 10)),
css_classes=['panel-widget-box', 'panel-widget-background'])
```


:::{admonition} Attention
:class: attention

Custom CSS styling may not appear to function properly on this page due to incompatibility with the tooling specific to the documentation.

:::


---

## Related Resources
