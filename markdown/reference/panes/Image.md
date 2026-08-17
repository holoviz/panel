# Image
---
```python
import panel as pn

pn.extension()
```

The ``Image`` pane embeds any known image format file in panel if provided a local path, or will link to a remote image if provided with a URL.

The ``Image`` pane functions as a sort of macro pane that selects one of the more specific image panes to display the image (whichever one first recognizes this particular image format).

Please refer to the [API](https://panel.holoviz.org/api/panel.pane.html#image-module) and [source code](https://github.com/holoviz/panel/blob/main/panel/pane/image.py).

The classmethod get_pane_type returns the pane_type that was selected.

Please consult the documentation of each specific pane (JPG, PNG, SVG, etc.) for the options that particular pane will support.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``alt_text``** (str, default=None): alt text to add to the image tag. The alt text is shown when a user cannot load or display the image.
* **``embed``** (boolean, default=False): If given a URL to an image this determines whether the image will be embedded as base64 or merely linked to.
* **``fixed_aspect``** (boolean, default=True): Whether the aspect ratio of the image should be forced to be equal.
* **``link_url``** (str, default=None): A link URL to make the image clickable and link to some other website.
* **``object``** (str or object): The Image file to display. Can be a string pointing to a local or remote file, or an object with a ``_repr_extension_`` method, where extension is an image file extension.
* **``styles``** (dict): Dictionary specifying CSS styles

___

The ``Image`` pane can be pointed at any local or remote image file. If given a URL starting with ``http`` or ``https``, the ``embed`` parameter determines whether the image will be embedded or linked to:

```python
jpg_pane = pn.pane.Image('https://assets.holoviz.org/panel/samples/jpeg_sample.jpeg')
png_pane = pn.pane.Image('https://assets.holoviz.org/panel/samples/png_sample.png')
webp_pane = pn.pane.Image('https://assets.holoviz.org/panel/samples/webp_sample.webp')
```

```python
pn.Column(jpg_pane, png_pane, webp_pane)
```

We can scale the size of the image by setting a specific fixed `width` or `height`:

```python
png_pane.clone(width=400)
```

Alternatively we can scale the width and height using the `sizing_mode`:

```python
pn.pane.Image(
    'https://assets.holoviz.org/panel/samples/png_sample2.png', sizing_mode='scale_width'
)
```

You can add a caption to the image by using the caption

```python
pn.pane.Image(
    'https://assets.holoviz.org/panel/samples/png_sample2.png', sizing_mode='scale_width', caption='World Map'
)
```

Note that by default the aspect ratio of the image is fixed, and so there may be a gap beside or below the image even in responsive sizing modes. To override this behavior set `fixed_aspect=False` or provide fixed `width` and `height` values.

## PIL

The Image pane will render any component that defines `_repr_[png | jpeg | svg]_` methods including PIL images:

```python
from PIL import Image, ImageDraw

im = Image.new(mode='RGB', size=(256, 256))

draw = ImageDraw.Draw(im)
draw.line((0, 0) + im.size, fill=128, width=5)
draw.line((0, im.size[1], im.size[0], 0), fill=128, width=5)
draw.rectangle([(96, 96), (160, 160)], fill=(0, 0, 128), width=10)

pn.pane.Image(im)
```

---
