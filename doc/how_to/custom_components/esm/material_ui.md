# Build Material UI Components

The `pn.ui` components are built on [Material UI](https://mui.com/material-ui/), and sometimes you need a component that the library does not provide. `MaterialUIComponent` is the entry point for building your own: it is a [`ReactComponent`](../../../reference/classic/custom_components/ReactComponent.md) that renders with the same Material UI library, React instance and theme as the built-in `pn.ui` components, so your component inherits `theme_config`, `dark_theme` and `sx` handling without any extra work.

This guide assumes you are familiar with the basics of `ReactComponent`. If you are not, start with [Create Custom Widgets using ESM Components](./custom_widgets.md).

## Import the base class

`MaterialUIComponent` lives in `panel.ui.base` alongside the other base classes of the `pn.ui` components:

```python
from panel.ui.base import MaterialUIComponent
```

Inside the ESM code you can then import Material UI components either one at a time or several at once, and they resolve to the copy that ships with Panel rather than being downloaded again:

```javascript
import Button from "@mui/material/Button";
import {Stack, Typography} from "@mui/material";
```

The default import name has to match the name of the Material UI component, i.e. `import Button from "@mui/material/Button"` works but `import MyButton from "@mui/material/Button"` does not.

## Build a rainbow button

Let us build a `RainbowButton` that cycles through the colors of the rainbow while you hover over it (or each time you click it), fires off some confetti on click and reports the number of clicks back to Python.

```{pyodide}
import param
import panel as pn

from panel.ui.base import MaterialUIComponent

pn.extension()

RAINBOW = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]

class RainbowButton(MaterialUIComponent):
    """
    A Button that cycles through rainbow colors.
    """

    clicks = param.Integer(default=0, doc="""
        Number of times the button has been clicked.""")

    colors = param.List(default=RAINBOW, doc="""
        The colors to cycle through.""")

    label = param.String(default="Click me!", doc="""
        The label shown on the button.""")

    size = param.Selector(default="medium", objects=["small", "medium", "large"], doc="""
        Material UI button size.""")

    mode = param.Selector(default="hover", objects=["hover", "click"], doc="""
        When to cycle: on hover or on click.""")

    interval = param.Integer(default=200, doc="""
        Time in ms between color changes.""")

    _importmap = {
        "imports": {
            "canvas-confetti": "https://esm.sh/canvas-confetti@1.6.0"
        }
    }

    _esm = """
import Button from "@mui/material/Button";
import confetti from "canvas-confetti";

export function render({ model }) {
  const [clicks, setClicks] = model.useState("clicks");
  const [colors] = model.useState("colors");
  const [label] = model.useState("label");
  const [size] = model.useState("size");
  const [mode] = model.useState("mode");
  const [interval] = model.useState("interval");

  const [index, setIndex] = React.useState(0);
  const hoverTimer = React.useRef(null);

  const nextColor = () => setIndex(i => (i + 1) % colors.length);

  const handleClick = () => {
    confetti();
    setClicks(clicks + 1);
    if (mode === "click") nextColor();
  };

  const handleMouseEnter = () => {
    if (mode === "hover") {
      hoverTimer.current = setInterval(nextColor, interval);
    }
  };

  const handleMouseLeave = () => {
    clearInterval(hoverTimer.current);
  };

  return (
    <Button
      variant="contained"
      size={size}
      onClick={handleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      sx={{backgroundColor: colors[index % colors.length], color: "white", textTransform: "none"}}
    >
      {label}
    </Button>
  );
}
"""

button = RainbowButton(label="Unicorn Power!", interval=150)

pn.ui.Column(
    button,
    pn.bind(lambda c: f"Clicked {c} times", button.param.clicks),
).servable()
```

Hover over the button to watch it cycle through the colors and click it to see the confetti and the click count update.

Let us walk through what is happening:

- On the Python side we declare the parameters of the component. Every parameter is synced to the frontend, including parameters whose name starts with an underscore, so a leading `_` only marks a parameter as private API, it does not keep it out of the browser.
- `model.useState("<parameter>")` returns the current value and a setter. Calling `setClicks` in the browser updates `button.clicks` in Python, which re-renders the text bound to it.
- `React.useState` and `React.useRef` hold state that only exists in the browser, here the index of the current color and the hover timer.
- The `_importmap` adds `canvas-confetti` from [esm.sh](https://esm.sh). The React and Material UI imports are configured for you, so the import map only needs the extra libraries you use. See [Compile and Bundle ESM Components](./build.md) for more on import maps.

:::{warning}
Do not redeclare a parameter that the component inherits from Panel with a different type. Declaring `margin = param.Integer(10)`, for instance, turns `margin` into a property of the component's data model and the actual layout margin is lost. To change the default, set `RainbowButton.param.margin.default = 10` or pass `margin=10` to the constructor.
:::

## Theming

Because the component renders inside the shared Material UI theme, `color="primary"` and friends follow the theme of your app, and a component level `theme_config` works exactly like it does for the built-in components:

```python
RainbowButton(theme_config={"palette": {"primary": {"main": "#e91e63"}}})
```

See [Customize Themes and Styles](../../styling/ui_themes_and_styles.md) for the full set of options.

## Use icons

The Material Icons font is loaded together with the component, so the simplest way to add an icon is the `Icon` component with the icon name as its text. Set the font family explicitly so that the icon resolves inside the component's shadow DOM; use `"Material Icons Outlined"` for the outlined variants. Here is a like button that toggles a `liked` parameter:

```{pyodide}
import param
import panel as pn

from panel.ui.base import MaterialUIComponent

pn.extension()

class LikeButton(MaterialUIComponent):

    liked = param.Boolean(default=False)

    _esm = """
import IconButton from "@mui/material/IconButton";
import Icon from "@mui/material/Icon";

export function render({ model }) {
  const [liked, setLiked] = model.useState("liked");
  return (
    <IconButton color="primary" onClick={() => setLiked(!liked)}>
      <Icon fontSize="large" style={{fontFamily: "Material Icons"}}>
        {liked ? "favorite" : "favorite_border"}
      </Icon>
    </IconButton>
  );
}
"""

like = LikeButton()

pn.Row(like, pn.bind(lambda liked: f"Liked: {liked}", like.param.liked))
```

If you prefer the SVG icons of [`@mui/icons-material`](https://mui.com/material-ui/material-icons/), add an explicit import map entry for each icon you use and mark React as external with `?external=react`, so the icon shares the React instance of the other components. The icon brings its own copy of the Material UI styles, which are not applied inside the component, so give it its dimensions and fill with inline styles:

```{pyodide}
import panel as pn

from panel.ui.base import MaterialUIComponent

pn.extension()

class DeleteButton(MaterialUIComponent):

    _importmap = {
        "imports": {
            "@mui/icons-material/Delete": "https://esm.sh/@mui/icons-material@9.0.1/Delete?external=react",
        }
    }

    _esm = """
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";

export function render({ model }) {
  return (
    <IconButton color="primary">
      <DeleteIcon style={{width: 35, height: 35, fill: "currentColor"}} />
    </IconButton>
  );
}
"""

DeleteButton()
```

Import map entries are global to the page, so two components that map the same icon to different URLs conflict. Keep the URL for each icon identical across your components.

## Move the code into a separate file

Once a component grows beyond a few lines, move the JSX into its own file next to the Python module. `MaterialUIComponent` reads the source of a file from `_esm_base`, given as a string path relative to the Python file:

```python
class RainbowButton(MaterialUIComponent):

    ...

    _esm_base = "rainbow_button.jsx"
```

```javascript
// rainbow_button.jsx
import Button from "@mui/material/Button";
import confetti from "canvas-confetti";

export function render({ model }) {
  ...
}
```

Then serve the app as usual with `panel serve app.py`.

## Distribute your component

When your component is ready to share, package it as a Python extension as described in [Publish a Panel Extension](../publish_extension.md). The [panel-extensions](https://github.com/orgs/panel-extensions/repositories) organization on GitHub has examples of published extensions built on this pattern.
