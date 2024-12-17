# Access the Bokeh Model

This guide addresses how to access the underlying Bokeh model of Panel objects.

---

Since Panel is built on top of Bokeh, all Panel objects can easily be converted to a Bokeh model. The ``get_root`` method returns a model representing the contents of a Panel:

```{pyodide}
import panel as pn

model = pn.Column('# Some markdown').get_root()
model
```

By default this model will be associated with Bokeh's ``curdoc()``, so if you want to associate the model with some other ``Document`` ensure you supply it explicitly as the first argument. Once you have access to the underlying Bokeh model you can use all the usual Bokeh utilities such as ``components``, ``file_html``, or ``show``

```{pyodide}
from bokeh.embed import components, file_html
from bokeh.io import show

script, html = components(model)

print(html)
```

## Related Resources
