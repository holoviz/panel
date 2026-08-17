# Control Size

This guide addresses how to control the size of components.

---

Components can use either one of the responsive sizing modes or absolute sizing.

:class: important

Unlike other components, the size of a plot component is usually determined by the underlying plotting library, so it may be necessary to ensure that you set the size and aspect when declaring the plot.

:::

## Absolute Sizing

To set a fixed size on a component, it is usually sufficient to set a `width` or `height`, but in certain cases setting ``sizing_mode='fixed'`` explicitly may also be required.

Let's create a simple example that fixes the height or width of several components:

```python
import panel as pn
pn.extension() # for notebook

pn.Row(
    pn.pane.Markdown('ABCDE', styles={'background': '#f0f0f0'}, width=75, height=100),
    pn.widgets.FloatSlider(width=200, styles={'background': '#f0f0f0'}),
    pn.pane.PNG('https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png', width=300, styles={'background': '#f0f0f0'}),
)
```

Now let's use ``sizing_mode='fixed'`` to create a fixed-size component. This will retain the object's original width and height regardless of any subsequent browser window resize events. This is usually the default behavior and simply respects the provided width and height.

```python
pn.pane.PNG('https://upload.wikimedia.org/wikipedia/commons/8/89/PNG-Gradient.png', sizing_mode='fixed')
```

## Responsive Sizing

Most panel objects support reactive sizing which adjusts depending on the size of the visible area of a web page. Responsive sizing modes can be controlled using the ``sizing_mode`` parameter with the following options:

* **"stretch_width"**: Component will responsively resize to stretch to the available width, without maintaining any aspect ratio. The height of the component depends on the type of the component and may be fixed or fit to component's contents. To demonstrate this behavior we create a Row with a fixed height and responsive width to fill:

```python
pn.Row(
    pn.pane.Str(styles={'background': '#f0f0f0'}, height=100, sizing_mode='stretch_width'),
    width_policy='max', height=200
)
```

* **"stretch_height"**: Component will responsively resize to stretch to the available height, without maintaining any aspect ratio. The width of the component depends on the type of the component and may be fixed or fit to component's contents. To demonstrate the filling behavior in a document we declare a Column with a fixed height for the component to fill:

```python
pn.Column(
    pn.pane.Str(styles={'background': '#f0f0f0'}, sizing_mode='stretch_height', width=200),
    height=200
)
```

* **"stretch_both"**: Component is completely responsive, independently in width and height, and will occupy all the available horizontal and vertical space, even if this changes the aspect ratio of the component. To demonstrate this behavior we will declare a Column with a fixed height and responsive width for the component to fill:

```python
pn.Column(
    pn.pane.Str(styles={'background': '#f0f0f0'}, sizing_mode='stretch_both'),
    height=200, width_policy='max'
)
```

* **"scale_height"**: Component will responsively resize to stretch to the available height, while maintaining the original or provided aspect ratio.
* **"scale_width"**: Component will responsively resize to stretch to the available width, while maintaining the original or provided aspect ratio.
* **"scale_both"**: Component will responsively resize to both the available width and height, while maintaining the original or provided aspect ratio. For example:

```python
pn.Column(
    pn.pane.PNG(
        'https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png',
        sizing_mode='scale_both'
    ), height=400, width=500, styles={'background': '#f0f0f0'})
```

## Constrain Responsive Sizes

The `min_width`, `max_width`, `min_height`, and `max_height` parameters limit
how far a responsive component can shrink or grow. A bound only affects an
adjustable dimension, so pair `max_width` with a width-responsive sizing mode
and `max_height` with a height-responsive sizing mode.

For example, the pane below fills the available width until it reaches 500
pixels, and never shrinks below 200 pixels:

```python
pn.pane.Markdown(
    "Resize the browser to see the width change.",
    sizing_mode="stretch_width",
    min_width=200,
    max_width=500,
    styles={"background": "#f0f0f0", "padding": "1rem"},
)
```

The `width` and `height` parameters act as preferred sizes when the
corresponding dimension is responsive. The minimum and maximum bounds still
take precedence.

## Set a Default Sizing Mode

To avoid repeating the same `sizing_mode` on every component, set a default
when loading Panel:

```python
pn.extension(sizing_mode="stretch_width")
```

The equivalent configuration setting is useful when Panel has already been
loaded:

```python
pn.config.sizing_mode = "stretch_width"
```

These defaults apply to components created afterwards. A `sizing_mode`
specified directly on a component takes precedence.

## Fine-grained Width and Height Policies

The `width_policy` and `height_policy` parameters provide lower-level control
over each dimension. They take precedence over `sizing_mode` and accept the
same policy choices for the horizontal and vertical axes:

| Policy | Behavior |
| --- | --- |
| `"auto"` | Use the component's preferred policy. |
| `"fixed"` | Use exactly `width` or `height`; the component may overflow its container. |
| `"fit"` | Prefer `width` or `height`, but fit within the available space and any minimum or maximum bounds. |
| `"min"` | Use as little space as possible without crossing the minimum bound. |
| `"max"` | Use as much space as possible without crossing the maximum bound. |

For example, `width_policy="max"` makes this row use the available horizontal
space, while `max_width` prevents it from becoming wider than 600 pixels:

```python
pn.Row(
    pn.widgets.TextInput(label="Name", width_policy="max"),
    pn.widgets.Button(label="Submit"),
    width_policy="max",
    max_width=600,
)
```

## Sizing Mode Inference on Layouts

Layouts do not only use their own `sizing_mode`; they also inspect their
children and may upgrade themselves to be responsive along an axis where a
child is responsive. This exists so that dropping a responsive component into a
plain `Row` or `Column` does something sensible without having to set
`sizing_mode` on every level of the layout hierarchy. The rules are:

- If any child is responsive in width, the layout becomes width-responsive,
  unless the layout has a fixed `width`.
- If a vertical layout (e.g. a `Column`) has any height-responsive child, the
  layout becomes height-responsive, unless the layout has a fixed `height`.
- If a horizontal layout (e.g. a `Row`) has children that are *all*
  height-responsive, the layout becomes height-responsive. This is
  asymmetrical with width because there is not always vertical space to expand
  into, and matching the height of the other children is usually preferable.
- Any children with a fixed `width` or `height` contribute a `min_width` or
  `min_height` to the layout so sufficient space is allocated.

`FlexBox` is an exception: it picks a `sizing_mode` from its `flex_direction`
instead of inspecting its children, so these rules do not apply to it.

In the example below the `Column` was never given a `sizing_mode`, but its
background fills the available width because it inherited `stretch_width` from
its child:

```python
pn.Column(
    pn.pane.Markdown('Responsive child', sizing_mode='stretch_width'),
    styles={'background': '#f0f0f0'},
)
```

The inferred value is applied when the layout is rendered, so it is not
reflected in the layout's `sizing_mode` parameter, which stays at whatever you
set it to (or `None`).

### When inference overrides an explicit setting

Because inference looks at children, it can end up contradicting a
`sizing_mode` you set on the layout yourself. If a layout is declared
`sizing_mode='stretch_height'` but contains a width-responsive child, the
inferred `'stretch_width'` wins and your setting is dropped. Panel warns when
this happens:

```python
pn.Column(
    pn.pane.Markdown('...', sizing_mode='stretch_width'),
    sizing_mode='stretch_height',
)
# WARNING: sizing_mode='stretch_height' on Column is being overridden to
# 'stretch_width' by a child's sizing.
```

The warning means the layout is not sized the way the code says it is, which is
usually a bug in the sizing specification rather than something to silence. The
two ways to resolve it are to correct the `sizing_mode` so it matches what the
children need, or to pin the axis with a policy as described below.

Note that inference never *reduces* responsiveness. A layout declared
`sizing_mode='stretch_both'` whose children only expand in width stays
`stretch_both`, because the explicit setting already covers the inferred one.

### Pinning an axis with a policy

Since `width_policy` and `height_policy` take precedence over `sizing_mode`,
setting a policy on an axis keeps that axis under your control regardless of
what the children ask for, and never produces an override warning. In the
example below the layout still reports an inferred `stretch_width`, but
`width_policy='min'` is what actually governs the horizontal axis, so the
column shrinks to its contents:

```python
pn.Column(
    pn.pane.Markdown('Responsive child', sizing_mode='stretch_width'),
    styles={'background': '#f0f0f0'},
    width_policy='min',
)
```

Setting a fixed `width` or `height` on the layout also suppresses inference on
that axis, since a fixed size is unambiguous:

```python
pn.Column(
    pn.pane.Markdown('Responsive child', sizing_mode='stretch_width'),
    styles={'background': '#f0f0f0'},
    width=300,
)
```

### Disabling inference entirely

To make explicitly set sizing parameters authoritative everywhere, enable
`respect_explicit_sizing`:

```python
pn.extension(respect_explicit_sizing=True)
# OR
pn.config.respect_explicit_sizing = True
```

With this enabled, a `sizing_mode`, `width_policy`, or `height_policy` you set
on a layout is never overridden by its children, and no override warnings are
emitted. Layouts that were not given an explicit setting still infer one from
their children, so responsive content continues to work without annotating
every container.

This defaults to `False` to preserve the pre-existing behavior, since apps that
relied on inference winning would otherwise change layout.

---

## Related Resources
