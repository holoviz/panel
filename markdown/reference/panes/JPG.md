# JPG
---
```python
import panel as pn

pn.extension()
```

The ``JPG`` pane embeds a ``.jpg`` or ``.jpeg`` image file in a panel if provided a local path, or it will link to a remote image if provided a URL.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``alt_text``** (str, default=None): alt text to add to the image tag. The alt text is shown when a user cannot load or display the image.
* **``embed``** (boolean, default=False): If given a URL to an image this determines whether the image will be embedded as base64 or merely linked to.
* **``fixed_aspect``** (boolean, default=True): Whether the aspect ratio of the image should be forced to be equal.
* **``link_url``** (str, default=None): A link URL to make the image clickable and link to some other website.
* **``object``** (str or object): The JPEG file to display.  Can be a string pointing to a local or remote file, or an object with a ``_repr_jpeg_`` method.
* **``styles``** (dict): Dictionary specifying CSS styles
* **``target``** (str, default="_blank"): Where to open the document linked in the link_url.

___

The ``JPG`` pane can be pointed at any local or remote ``.jpg`` file.  If given a URL starting with ``http`` or ``https``, the ``embed`` parameter determines whether the image will be embedded or linked to:

```python
jpg_pane = pn.pane.JPG(
    'https://assets.holoviz.org/panel/samples/jpeg_sample.jpg',
    link_url='https://blog.holoviz.org/panel_0.13.0.html',
    width=800
)

jpg_pane
```

We can scale the size of the image by setting a specific fixed `width` or `height`:

```python
jpg_pane.clone(width=400)
```

Alternatively we can scale the width and height using the `sizing_mode`:

```python
pn.pane.JPG(
    'https://assets.holoviz.org/panel/samples/jpeg_sample2.jpg',
    link_url='https://blog.holoviz.org/panel_0.14.html',
    sizing_mode='scale_both'
)
```

Note that by default the aspect ratio of the image is fixed, and so there may be a gap beside or below the image even in responsive sizing modes. To override this behavior set `fixed_aspect=False` or provide fixed `width` and `height` values.

---
