# Upgrade Guide

Welcome to the Upgrade Guide for Panel! When we make backward incompatible changes we will provide a detailed guide on how you can update your application to be compatible with the latest changes.

## Version 1.0

The 1.0 release brings with it a wealth of improvements, including significant changes to the layout engine and an improved approach to handling CSS for individual components. These improvements are thanks to the new Bokeh 3.x releases, which received a bottom up rewrite of layouts and CSS handling. These updates not only boost the performance but also elevate the customizability of your Panel apps.

As with any major update, it's important to understand the implications of these changes for your existing applications. This guide is designed to walk you through the key updates introduced in Panel 1.0, the rationale behind them, and the critical considerations to bear in mind while adapting your applications to this new version. We'll take you on a comprehensive journey, outlining how the new layout engine transforms the way you create and manage your Panel apps and the impact of the enhanced CSS handling on your components.

By the end of this guide, you will have a clear understanding of how to leverage the full potential of Panel 1.0's features and enhancements, ensuring a smooth transition for your applications. So, without further ado, let's dive into the exciting world of Panel 1.0 and explore the new possibilities it has to offer!

### The layout engine

Panel 1.0, built upon Bokeh 3.0, introduces a CSS-based layout engine that replaces the previous version, which was primarily optimized for plotting. This update results in improved performance, especially when handling a multitude of components on the page at the same time. This allows you to create more intricate applications without sacrificing speed and responsiveness.

Additionally, Panel 1.0 offers better sizing of components that are slow to render, such as images. By removing the need for explicit CSS size overrides, Panel 1.0 streamlines the customization process for your layouts. This added flexibility makes it easier to tailor your apps to fit your design goals and user needs.

However, it's important to note that the complete replacement of the layout implementation might not ensure identical behavior to previous versions. In the upcoming sections, we'll go through key points to consider when adapting to this new layout engine.

#### `sizing_mode`

The sizing_mode has been the primary way to configure responsiveness of components in Panel and that has not changed. However, previously the layout engine was quite forgiving in the way it interpreted combinations of the `sizing_mode` and explicit `width`/`height` settings that really did not make sense. Before we dive into some of these differences let's briefly go through the different `sizing_mode` options and what they actually mean:

![Container sizing_mode](sizing_modes.svg)

- `stretch_width`: Stretches content/container in width while height is determined by size of contents.
- `stretch_height`: Stretches content/container in height while width is determined by size of contents.
- `stretch_both`: Stretches content/container in both width and height.

Now let us explore what changed in this release. In the past any responsive content would force a container to also become responsive. In this release this is no longer guaranteed, i.e. you should generally set the `sizing_mode` on each container if you want your application to be responsive.

![Container sizing_mode](container_sizing_mode.svg)

:::{note}
To maintain backward compatibility Panel will still try to infer the appropriate sizing mode by inspecting the children of a container. It is however always best to be explicit.
:::

#### Ambiguous configurations

In the past Panel would happily accept ambiguous layout configurations, e.g. providing a fixed width while also setting a responsive `sizing_mode` along the same dimension. As an example take the following:

```python
pn.pane.Image(..., sizing_mode='stretch_both', width=500)
```

This specification is ambiguous. Did you want it to stretch the width or did you want to set a fixed width? In the past this would be resolved in favor of the fixed width, i.e. fixed sizing would take precedence over responsiveness, but in certain cases the behavior was completely undefined. This meant it was quite unpredictable what behavior you would actually get. In Panel 1.0 we will warn that this is not a supported configuration and turn the `width` into a `min_width`. In future this conflicting specification will simply error. To toggle these errors on instead of warning set `layout_compatibility` to `'error'`:

```python
pn.extension(layout_compatibility='error')
# OR
pn.config.layout_compatibility = 'error'
```

### CSS styling

The other major change in Panel 1.0 is in the CSS handling on components. Starting in Bokeh 3.0 each component is now rendered into the [Shadow DOM](https://developer.mozilla.org/en-US/docs/Web/API/Web_components/Using_shadow_DOM). While you don't have to understand the intricacies of how the shadow DOM works, know that each component is now encapsulated and therefore isolated from the rest of the page. This has big benefits because each component can be styled fully independently without the CSS leaking to other components but it also has significant backward compatibility implications.

#### Global vs. local stylesheets

While we never encouraged this, in the past it was possible to declare global stylesheets that could override the styles of all components on the page. As a backward compatibility measure any stylesheets defined using the `raw_css` and `css_files` config parameters will be injected on every single component. Therefore a setting like:

```python
pn.extension(raw_css=['div.widget-box { color: red; }'], css_files=['https://panel.holoviz.org/custom.css'])
```

is now strongly discouraged. This is because injecting stylesheets on every single component is highly inefficient.

:::{attention}
Usage of `pn.config.raw_css` and `pn.config.css_files` is now **strongly** discouraged.
:::

Depending on whether your custom CSS was controlling styling of individual components or the template you should now either use the `stylesheets` parameter on each component OR use the `raw_css` and `css_files` parameters on the template.

#### Component Stylesheets

Now that each component is isolated from the rest of the page it is possible to style each component separately by injecting `stylesheets`. This is what makes it possible for each component to be styled using the `design` frameworks ([see the how-to guide on applying designs](how_to/styling/design.md)). Instead of injecting global stylesheets you should now apply the stylesheets on the component.

Let us walk through a simple example. Let's say you had a global stylesheet that would change the style of a `FloatSlider` handle. Previously you would have injected this globally like this:

```python
import panel as pn

slider_css = """
.noUi-handle {
  border-radius: 100%;
  box-shadow: unset;
  background-color: #0081f3;
}
"""

pn.extension(raw_css=[slider_css])
```

Now you can inject it directly on the specific component you want to override like this:

```{pyodide}
import panel as pn

slider_css = """
.noUi-handle {
  border-radius: 100%;
  box-shadow: unset;
  background-color: #0081f3;
}
"""

pn.widgets.FloatSlider(name='Number', stylesheets=[slider_css])
```

Alternatively you can also modify the class default like this:

```python
pn.widgets.FloatSlider.stylesheets = [slider_css]
```

ensuring that all `FloatSlider` instances will use this stylesheet. For more details on applying CSS to components [see the corresponding how-to guide](how_to/styling/apply_css.md).

#### Template Stylesheets

Sometimes there is still a need to change the appearance of the overall template. Instead of injecting those options via the global `raw_css` and `css_files` config parameters you can inject them directly on a template, e.g.:

```python
pn.template.MaterialTemplate(
    raw_css=[...], css_files=[...]
)
```

or if you are using a global template:

```python
pn.state.template.param.update(
    raw_css=[...], css_files=[...]
)
```
