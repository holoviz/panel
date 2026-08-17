# FileDownload
---
```python
import panel as pn
pn.extension()
```

The `FileDownload` widget allows downloading a file on the frontend by sending the file data to the browser either on initialization (if `embed=True`) or when the button is clicked.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **`auto`** (boolean):  Whether to download the file with the first click (if `True`) or only after clicking a second time (if `False`, enables right-click -> Save as).
* **`callback`** (callable): A callable that returns a file or file-like object (takes precedence over `file` if set).
* **`embed`** (boolean):  Whether to embed the data on initialization.
* **`file`** (str, Path or file-like object):  A path to a file or a file-like object.
* **`filename`** (str): The filename to save the file as.

##### Display

* **`variant`** (str): The button style, either 'solid' or 'outline'.
* **`color`** (str): A button theme; should be one of `'default'` (white), `'primary'` (blue), `'success'` (green), `'info'` (yellow), `'light'` (light), or `'danger'` (red)
* **`icon`** (str): An icon to render to the left of the button label. Either an SVG or an icon name which is loaded from [tabler-icons.io](https://tabler-icons.io)/.
* **`icon_size`** (str): Size of the icon as a string, e.g. 12px or 1em.
* **`label`** (str): A custom label for the download button (by default uses the filename)
* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

The `FileDownload` widget accepts a path to a file or a file-like object (with a `.read` method) if the latter is provided a `filename` must also be set. By default (`auto=True` and `embed=False`) the file is only transferred to the browser after the button is clicked (this requires a live-server or notebook kernel):

```python
file_download = pn.widgets.FileDownload(file='FileDownload.ipynb', filename='custom_filename.ipynb')

file_download
```

The file data may also be embedded immediately using `embed` parameter, this allows using the widget even in a static export:

```python
pn.widgets.FileDownload(file='FileDownload.ipynb', embed=True)
```

If `auto=False` is set the file will not be downloaded on the initial click but will change the label from "Transfer <file>" to "Download <file>" once the data has been synced. This offers an opportunity to download using the `Save as` dialog once the data has been transferred.

```python
pn.widgets.FileDownload(
    file='FileDownload.ipynb', color='success', auto=False,
    embed=False, label="Right-click to download using 'Save as' dialog"
)
```

The `FileDownload` widget may also be given a file-like object, e.g. here we save a pandas DataFrame as a CSV to a StringIO object and pass that to the widget:

```python
from bokeh.sampledata.autompg import autompg

from io import StringIO
sio = StringIO()
autompg.to_csv(sio)
sio.seek(0)

pn.widgets.FileDownload(sio, embed=True, filename='autompg.csv')
```

If you want to generate the file dynamically, e.g. because it depends on the parameters of some widget you can also supply a callback (which may be decorated with the widgets and/or parameters it depends on):

```python
years_options = list(autompg.yr.unique())
years = pn.widgets.MultiChoice(
    label='Years', options=years_options, value=[years_options[0]], margin=(0, 20, 0, 0)
)
mpg = pn.widgets.RangeSlider(
    label='Mile per Gallon', start=autompg.mpg.min(), end=autompg.mpg.max()
)

def filtered_mpg(yrs, mpg):
    df = autompg
    if years.value:
        df = autompg[autompg.yr.isin(yrs)]
    return df[(df.mpg >= mpg[0]) & (df.mpg <= mpg[1])]

def filtered_file(yr, mpg):
    df = filtered_mpg(yr, mpg)
    sio = StringIO()
    df.to_csv(sio)
    sio.seek(0)
    return sio

fd = pn.widgets.FileDownload(
    callback=pn.bind(filtered_file, years, mpg), filename='filtered_autompg.csv'
)

pn.Column(
    pn.Row(years, mpg),
    fd,
    pn.panel(pn.bind(filtered_mpg, years, mpg), width=600),
    width=600
)
```

### Styles

The color of the `FileDownload` button can be set by selecting one of the available `color` values and the `variant` can be `'solid'` or `'outline'`:

```python
pn.Row(
    *(pn.Column(*(pn.widgets.FileDownload(color=p, variant=bs) for p in pn.widgets.FileDownload.param.color.objects))
    for bs in pn.widgets.FileDownload.param.variant.objects)
)
```

## Icons

Like other buttons you can provide an explicit `icon`, either as a named icon loaded from [tabler-icons.io](https://tabler-icons.io)/:

```python
pn.Row(
    pn.widgets.FileDownload(icon='alert-triangle-filled', color='warning', file='FileDownload.ipynb'),
    pn.widgets.FileDownload(icon='bug', color='danger', file='FileDownload.ipynb')
)
```

or as an explicit SVG:

```python
cash_icon = """
<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-cash" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path stroke="none" d="M0 0h24v24H0z" fill="none"/>
  <path d="M7 9m0 2a2 2 0 0 1 2 -2h10a2 2 0 0 1 2 2v6a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2z" />
  <path d="M14 14m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0" />
  <path d="M17 9v-2a2 2 0 0 0 -2 -2h-10a2 2 0 0 0 -2 2v6a2 2 0 0 0 2 2h2" />
</svg>
"""

pn.widgets.FileDownload(icon=cash_icon, color='success', icon_size='2em', file='FileDownload.ipynb')
```

---
