# SVG
---
```python
import panel as pn

pn.extension()
```

The ``SVG`` pane embeds an ``.svg`` image file in a panel if provided a local path, or will link to a remote image if provided a URL.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``alt_text``** (str, default=None): alt text to add to the image tag. The alt text is shown when a user cannot load or display the image.
* **``embed``** (boolean, default=False): If given a URL to an image this determines whether the image will be embedded as base64 or merely linked to.
* **``fixed_aspect``** (boolean, default=True): Whether the aspect ratio of the image should be forced to be equal.
* **``link_url``** (str, default=None): A link URL to make the image clickable and link to some other website.
* **``encode``** (bool, default=True): Whether to base64 encode the SVG, when enabled SVG links may not work while disabling encoding will prevent image scaling from working.
* **``object``** (str or object): The svg file to display. Can be a string pointing to a local or remote file, or an object with a ``_repr_svg_`` method.
* **``styles``** (dict): Dictionary specifying CSS styles
* **``target``** (str, default="_blank"): Where to open the document linked in the link_url.

___

The ``SVG`` pane can be pointed at any local or remote ``.svg`` file. If given a URL starting with ``http`` or ``https``, the ``embed`` parameter determines whether the image will be embedded or linked to:

```python
pn.pane.SVG('https://panel.holoviz.org/_static/logo_stacked.svg', link_url = "https://panel.holoviz.org", width=300)
```

We can scale the size of the image by setting a specific fixed `width` or `height`:

```python
svg_pane = pn.pane.SVG('https://panel.holoviz.org/_static/logo_stacked.svg', width=150)
svg_pane
```

Like any other pane, the ``SVG`` pane can be updated by setting the ``object`` parameter:

```python
svg_pane.object = "https://panel.holoviz.org/_static/jupyterlite.svg"
```

You can also use a *responsive* `sizing_mode` like `'stretch_width'`.

```python
pn.pane.SVG('https://assets.holoviz.org/panel/samples/svg_sample2.svg', sizing_mode='stretch_width')
```

Note that by default the aspect ratio of the image is fixed, to override this behavior set `fixed_aspect=False` or provide fixed `width` and `height` values.

---
