# Change Background

Panel components have a `styles` parameter that takes a dictionary of CSS styles to apply to the component. To customize the background you can set the [background](https://developer.mozilla.org/en-US/docs/Web/CSS/background) property  with a CSS [color](https://developer.mozilla.org/en-US/docs/Web/CSS/color_value), or really any value that is accepted by the `background` property.

First, define a simple HTML pane with a default *skyblue* color. Set the width and height to make it visible.

```{pyodide}
import panel as pn
pn.extension() # for notebook

block = pn.pane.HTML(width=100, height=100, styles=dict(background='skyblue'))
block
```

Now, update the background to *crimson* by re-setting the `styles` parameter.

```{pyodide}
block.styles = dict(background='crimson')
```

Let's be more creative and set a CSS radial-gradient background, radiating from *crimson* in the center to *skyblue*.

```{pyodide}
block.styles = dict(background='radial-gradient(crimson, skyblue)')
```
