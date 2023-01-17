# Change Background

Many components have a `background` argument that can take a color either as a hex string or color name. See the list of available color names for modern browsers in the [bokeh docs](https://docs.bokeh.org/en/latest/docs/reference/colors.html#bokeh-colors-groups).

First, define a simple HTML pane, set the width and height, and then change the background color to '#f307eb'.

```{pyodide}
import panel as pn
pn.extension() # for notebook

block1 = pn.pane.HTML(width=100, height=100)
block1.background='#f307eb'
block1
```

Now, create another block with the color of 'mediumseagreen':

```{pyodide}
pn.pane.HTML(background='mediumseagreen', width=200, height=100)
```
