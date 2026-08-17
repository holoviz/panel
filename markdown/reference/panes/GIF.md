# GIF
---
```python
import panel as pn

pn.extension()
```

The ``GIF`` pane embeds a ``.gif`` image file in a panel if provided a local path, or will link to a remote image if provided a URL.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``alt_text``** (str, default=None): alt text to add to the image tag. The alt text is shown when a user cannot load or display the image.
* **``embed``** (boolean, default=False): If given a URL to an image this determines whether the image will be embedded as base64 or merely linked to.
* **``fixed_aspect``** (boolean, default=True): Whether the aspect ratio of the image should be forced to be equal.
* **``link_url``** (str, default=None): A link URL to make the image clickable and link to some other website.
* **``object``** (str or object): The string to display. If a non-string type is supplied the repr is displayed.
* **``styles``** (dict): Dictionary specifying CSS styles

___

The ``GIF`` pane can be pointed at any local or remote ``.gif`` file. If given a URL starting with ``http`` or ``https``, the ``embed`` parameter determines whether the image will be embedded or linked to:

```python
gif_pane = pn.pane.GIF('https://upload.wikimedia.org/wikipedia/commons/d/de/Ajax-loader.gif')

gif_pane
```

We can scale the size of the image by setting a specific fixed `width` or `height`:

```python
gif_pane.clone(width=100)
```

Alternatively we can scale the width and height using the `sizing_mode`:

```python
pn.pane.GIF('https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif', sizing_mode='stretch_width')
```

Note that by default the aspect ratio of the image is fixed, and so there may be a gap beside or below the image even in responsive sizing modes. To override this behavior set `fixed_aspect=False` or provide fixed `width` and `height` values.

---
