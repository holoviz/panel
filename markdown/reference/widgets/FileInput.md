# FileInput
---
```python
import io
import panel as pn
pn.extension()
```

The ``FileInput`` widget allows uploading one or more files from the frontend and makes the filename, file data and [MIME type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types) available in Python. To upload large files, use the `FileDropper` widget.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``accept``** (str):  A list of file input filters that restrict what files the user can pick from
* **``directory``** (str): If directories is upload instead of files
* **``filename``** (str/list): The filename(s) of the uploaded file(s)
* **``mime_type``** (str/list): The mime type(s) of the uploaded file(s)
* **``multiple``** (boolean): Whether to allow uploading multiple files
* **``value``** (bytes/list): A bytes object containing the file data or if `multiple` is set a list of bytes objects.

##### Display

* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

```python
file_input = pn.widgets.FileInput()

file_input
```

To read out the content of the file you can access the ``value`` parameter, which holds a [bytestring](https://docs.python.org/3/library/stdtypes.html#bytes-objects) containing the file's contents. Additionally information about the file type is made available on the ``filetype`` parameter expressed as a MIME type, e.g. ``image/png`` or ``text/csv``.

```python
file_input.value
```

The widget also has a ``save`` method that allows saving the uploaded data to a file or [BytesIO](https://docs.python.org/3/library/io.html#binary-i-o) object.

```python
# File
if file_input.value is not None:
    file_input.save('test.png')

# BytesIO object
if file_input.value is not None:
    out = io.BytesIO()
    file_input.save(out)
```

The `accept` parameter restricts what files the user can pick from. This consists of comma-separated list of standard HTML
file input filters. Values can be:

* `<file extension>` - Specific file extension(s) (e.g: .gif, .jpg, .png, .doc) are pickable
* `audio/*` - all sound files are pickable
* `video/*` - all video files are pickable
* `image/*` - all image files are pickable
* `<media type>` - A valid [IANA Media Type](https://www.iana.org/assignments/media-types/media-types.xhtml), with no parameters.

```python
file_input = pn.widgets.FileInput(accept='.csv,.json')

file_input
```

To allow uploading multiple files we can also set `multiple=True` or if you want to upload a whole directory `directory=True`:

```python
file_input = pn.widgets.FileInput(accept='.png', multiple=True)

file_input
```

When uploading one or more files the `filename`, `mime_type` and `value` parameters will now be lists.

You can also clear the file input with the `.clear()` method.

```python
file_input.clear()
```

### Upload size limits

While the `FileInput` widget doesn't set any limit on the size of a file that can be selected by a user, the infrastructure onto which Panel relies (web browsers, Bokeh, Tornado, notebooks, kubernetes etc.) limits significantly what is actually possible. By default the `FileInput` widget allows to upload data that is in the order of 10 MB. To increase these limits see the [Websocket Configuration Guide](../../how_to/server/websockets.md).

### Controls

The `FileInput` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(file_input.controls(jslink=True), file_input)
```

---
