# Accessing the Bokeh model

Since Panel is built on top of Bokeh, all Panel objects can easily be converted to a Bokeh model. The ``get_root`` method returns a model representing the contents of a Panel:

```python
model = pn.Column('# Some markdown').get_root()
model
```

By default this model will be associated with Bokeh's ``curdoc()``, so if you want to associate the model with some other ``Document`` ensure you supply it explictly as the first argument. Once you have access to the underlying bokeh model you can use all the usual bokeh utilities such as ``components``, ``file_html``, or ``show``

```python
from bokeh.embed import components, file_html
from bokeh.io import show

script, html = components(model)
```