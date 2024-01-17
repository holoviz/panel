# Styling

:::{note} Tutorial 7. **Styling**
:icon: false

#### How to leverage designs, stylesheets and CSS

Panel does not require frontend developer experience, instead providing high-level primitives called `Design` components to style your applications. If however, you want to take control over the precise styling of individual components you can write custom templates and CSS stylesheets to modify the look and feel of components.

:::

## Designs & Themes

A `Design` in Panel is a unified system for styling components across your applications. They were introduced in Panel 1.0 and we are still in the process of improving them to achieve a consistent look and feel.

Applying different design systems in Panel can be achieved globally or per component. To select a `design` globally set it via the extension:

```{pyodide}
import panel as pn

pn.extension(design='material')
```

Alternatively you can also explicitly import and set a `design` on the config:

```{pyodide}
from panel.theme import Material

pn.config.design = Material
```

The available `Design` systems include:

- `Material`: Based on Material Design
- `Bootstrap`: Based on the Bootstrap library
- `Fast`: Based on the Microsoft Fast Design library
- `Native`: The default styling inherited from Bokeh.

```{pyodide}
from panel.theme import Bootstrap, Material, Fast

def components(design=None):
    design = design or pn.config.design
    return pn.Column(
        pn.widgets.FloatSlider(name='Slider', design=design),
        pn.widgets.TextInput(name='TextInput', design=design),
        pn.widgets.Select(
            name='Select', options=['Biology', 'Chemistry', 'Physics'], design=design
        ),
        pn.widgets.Button(
            name='Click me!', icon='hand-click', button_type='primary', design=design
        )
    )

components()
```

If you want to style a specific component you can also explicitly pass in the `design` parameter:

```{pyodide}
components(Bootstrap)
```

We can also switch the theme from 'default' to 'dark' by setting it in the `extension` or on the `config`:

```{pyodide}
with pn.config.set(theme = 'dark'):
    display(components())
```

:::{note}
In the notebook the theme adapts to the current JupyterLab theme. Try switching to dark mode to observe this.
:::

## CSS & Stylesheets

Panel components are rendered into the [shadow DOM](https://developer.mozilla.org/en-US/docs/Web/Web_Components/Using_shadow_DOM), if you are not familiar with the concept just know that it means that each component is isolated from all others meaning that we can easily apply CSS rules for specific components.

To set CSS styles we can use one of two parameters, the `styles` and the `stylesheets` parameter. The former is a dictionary of CSS styles that are applied to the container wrapping the component while stylesheets can contain entire CSS files or inline CSS rules.

## `styles`

Applying `styles` allows us to style the **container** in a straightforward manner, e.g. here we apply a background and a border around a widget:


```{pyodide}
custom_style = {
    'background': '#f9f9f9',
    'border': '1px solid black',
    'padding': '10px',
    'box-shadow': '5px 5px 5px #bcbcbc',
    'font-size': '14pt'
}

pn.widgets.FloatSlider(name='Number', styles=custom_style)
```

## `stylesheets`

Since `styles` only applies to the `<div>` that holds the component we cannot use it to directly modify the styling of the **contents** of the component. This is where `stylesheets` come in, allowing us to provide CSS rules that affect each part of the component. This can be done in one of two ways, either we modify CSS variables or we target the specific DOM node that we want to modify using CSS rules.

:::{warning} 1.0.0
Note that `styles` and `stylesheets` are new in Panel 1.0.0. As we continue to build on this functionality we will provide ways of modifying the styling of components using CSS variables.
:::

### CSS Variables

In the case of the `FloatSlider` we can modify the dimensions of the handle and the slider using CSS variables like `--handle-width`, `--handle-height` and `--slider-size`. In future we aim to provide a comprehensive list of CSS variables for each component.


```{pyodide}
stylesheet = """
:host {
  --handle-width: 15px;
  --handle-height: 25px;
  --slider-size: 5px;
}
"""

pn.widgets.FloatSlider(
    name='Number', styles=custom_style, stylesheets=[stylesheet]
)
```

### CSS rules

If we need full control over the precise styling of a component we can target specific parts of a component using standard CSS rules, e.g. by identifying the CSS classes applied to each component.

:::{tip}
To discover how exactly a component is structured and how to target specific parts of a component use the inspect functionality of your browser. For example in Chrome right click on the component, then select inspect and look at the DOM structure, e.g. here is the DOM structure of the `FloatSlider`:

```html
<div class="bk-input-group">
  <div class="bk-slider-title">Number: <span class="bk-slider-value">0</span></div>
  <div class="noUi-target noUi-ltr noUi-horizontal noUi-txt-dir-ltr">
    <div class="noUi-base">
      <div class="noUi-connects">
        <div class="noUi-connect" style="transform: translate(0%, 0px) scale(0, 1); background-color: rgb(230, 230, 230);"></div>
      </div>
      <div class="noUi-origin" style="transform: translate(-100%, 0px); z-index: 4;">
        <div class="noUi-handle noUi-handle-lower" data-handle="0" tabindex="0" role="slider" aria-orientation="horizontal" aria-valuemin="0.0" aria-valuemax="1.0" aria-valuenow="0.0" aria-valuetext="0.00">
	<div class="noUi-touch-area">
      </div>
      <div class="noUi-tooltip">0</div>
    </div>
  </div>
</div>
```

Using the styles pane in the developer console you can then try out various styles before you translate them into specific CSS rules.
:::

Let's say we want to make the slider handle circular and change its color. Inspecting the HTML we can see that the handle is defined with the CSS class `noUi-handle`. Now we can define a CSS rule with that class that sets a `border-radius` and `background-color`, additionally we unset the `box-shadow`:

```{pyodide}
stylesheet = """
:host {
  --slider-size: 5px;
  --handle-width: 16px;
  --handle-height: 16px;
}

.noUi-handle {
  border-radius: 100%;
  box-shadow: unset;
  background-color: #0081f3;
}
"""

pn.widgets.FloatSlider(
    name='Number', styles=custom_style, stylesheets=[stylesheet]
)
```

### External stylesheets

Inlining stylesheets provides a quick way to override the style of a component but it also means we are sending the stylesheet to the frontend as a string. This can add up when we want to apply this stylesheet to multiple components. Therefore it is recommended that once you move to production the styles are served as an external stylesheet you reference.

You can either provide a full URL to the stylesheet and host it yourself or you can [serve static assets alongside your application](../server/static_files.md). Here we load the stylesheet from an external URL:

```{pyodide}
pn.widgets.FloatSlider(
    name='Number', stylesheets=['https://assets.holoviz.org/panel/how_to/styling/noUi.css']
)
```

### CSS Classes

When building complex stylesheets you will sometimes want to have multiple styles for one component. While it is possible to include a separate stylesheet for each you can also use CSS classes to distinguish between different components. The `css_classes` parameter will apply the CSS class to the shadow root (or container). Let us create two sliders with different CSS classes:


```{pyodide}
color_stylesheet = """
:host(.red) .noUi-handle {
  background-color: red
}

:host(.green) .noUi-handle {
  background-color: green
}

:host(.blue) .noUi-handle {
  background-color: blue
}
"""

pn.Column(
    *(pn.widgets.FloatSlider(name='Number', stylesheets=[stylesheet, color_stylesheet], css_classes=[cls])
      for cls in ('red', 'green', 'blue'))
)

```
