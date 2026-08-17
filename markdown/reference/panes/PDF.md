# PDF
---
```python
import panel as pn

pn.extension()
```

The ``PDF`` pane embeds an ``.pdf`` document in a panel if provided a local path, or will link to a remote file if provided a URL.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``embed``** (boolean, default=False): If given a URL to a file this determines whether the image will be embedded as base64 or merely linked to.
* **``object``** (str or object): The PDF file to display. Can be a string pointing to a local or remote file, or an object with a ``_repr_pdf_`` method.
* **``start_page``** (int): Start page of the `.pdf` file when loading the page.
* **``styles``** (dict): Dictionary specifying CSS styles.

___

The ``PDF`` pane can be pointed at any local or remote ``.pdf`` file. If given a URL starting with ``http`` or ``https``, the ``embed`` parameter determines whether the image will be embedded or linked to:

```python
pdf_pane = pn.pane.PDF('https://assets.holoviz.org/panel/samples/pdf_sample.pdf', width=700, height=1000)

pdf_pane
```

Like any other pane, the ``PDF`` pane can be updated by setting the ``object`` parameter:

```python
pdf_pane.object = 'https://assets.holoviz.org/panel/samples/pdf_sample2.pdf'
```

---
