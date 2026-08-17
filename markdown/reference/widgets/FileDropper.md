# FileDropper
---
```python
import io
import panel as pn
pn.extension('filedropper')
```

The `FileDropper` allows the user to upload one or more files to the server. It is built on top of the [FilePond](https://pqina.nl/filepond/) library, if you use this component extensively consider donating to them. The `FileDropper` is similar to the `FileInput` widget but additionally adds support for chunked uploads, making it possible to upload large files. The UI also supports previews for image files. Unlike `FileInput` the uploaded files are stored as dictionary of bytes object indexed by the filename.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **`accepted_filetypes`** (list): List of accepted file types. Can be mimetypes, file extensions or wild cards. For instance `['image/*']` will accept all images while `['.png', 'image/jpeg']` will only accepts PNGs and JPEGs.
* **`chunk_size`** (int): Size in bytes per chunk transferred across the WebSocket (`default=10000000`, i.e. 10MB).
* **`layout`** (Literal["circle", "compact", "integrated"] | None): Compact mode removes padding. Integrated mode renders FilePond as part of a bigger element and should not be used with `multiple=True`. Circle mode keeps FilePond's per-file action buttons and upload progress indicator inside the circular drop area.
* **`max_file_size`** (str): Maximum size of a file as a string with units given in KB or MB, e.g. 5MB or 750KB.
* **`max_files`** (int): Maximum number of files that can be uploaded if `multiple=True`.
* **`max_total_file_size`** (str): Maximum size of all uploaded files, as a string with units given in KB or MB, e.g. 5MB or 750KB.
* **`mime_type`** (dict[str, str]): A dictionary containing the mimetypes for each of the uploaded files indexed by their filename.
* **`previews`** (list[str]): List of previews to enable in the FileDropper. The following previews are available:
    * `image`: Adds support for image previews.
    * `pdf`: Adds support for PDF previews.
* **`multiple`** (bool): Whether to allow uploading multiple files.
* **`value`** (dict[str, str | bytes]): A dictionary containing the uploaded file(s) as bytes or string objects indexed by the filename. Files that have a `text/*` mimetype will automatically be decoded as `utf-8`.

##### Display

* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

```python
file_dropper = pn.widgets.FileDropper()

file_dropper
```

Try uploading an image or PDF file and you will see a preview of the uploaded file.

To read out the content of the file you can access the ``value`` parameter, which holds a dictionary mapping from the filename to a string or [bytestring](https://docs.python.org/3/library/stdtypes.html#bytes-objects) containing the file's contents. Any filetype that declares a `text/*` mimetype will automatically be decoded into a string. The mimetype itself is made available on the `mime_type` parameter expressed as a MIME type, e.g. `image/png` or `text/csv`, again expressed as a dictionary mapping from filename to filetype.

```python
file_dropper.value
```

### Filetypes

The `accepted_filetypes` parameter restricts what files the user can pick from. This consists of a list of mimetypes that also allows wildcards. Values can be:

* `<file extension>` - Specific file extension(s) (e.g: .gif, .jpg, .png, .doc) are pickable
* `audio/*` - all sound files are pickable
* `video/*` - all video files are pickable
* `image/*` - all image files are pickable
* `<media type>` - A valid [IANA Media Type](https://www.iana.org/assignments/media-types/media-types.xhtml), with no parameters.

```python
file_dropper = pn.widgets.FileDropper(accepted_filetypes=['.png', 'image/jpeg'])

file_dropper
```

To allow uploading multiple files we can also set `multiple=True`:

```python
file_dropper = pn.widgets.FileDropper(multiple=True)

file_dropper
```

### Layout

The `FileDropper` allows for a few different layout options:

- `"compact"`: Remove margins.
- `"integrated"`: Removes background and other styling. Useful when the component is embedded inside a larger component.
- `"circle"`: Circular upload area useful for profile picture uploads.

```python
pn.Row(
    pn.widgets.FileDropper(layout="compact"),
    pn.widgets.FileDropper(layout="integrated", styles={'background-color': 'black', 'border-radius': '1em', 'color': 'white'}),
    pn.widgets.FileDropper(layout="circle"),
)
```

### Upload size limits

Unlike the `FileInput` widget the `FileDropper` widget bypasses restrictions to the maximum file size imposed by web browsers, Bokeh, Tornado, notebooks, etc. by chunking large uploads. This makes it feasible to upload much larger files than would otherwise be possible. The default `chunk_size` is 10MB (which is expressed in as 10000000 bytes). You can configure `max_file_size`, `max_total_file_size` (limiting the total upload size if you have set `multiple=True`) and `max_files` to provide an upper bound on the amount of data that can be uploaded.

### Controls

The `FileDropper` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(file_dropper.controls(jslink=True), file_dropper)
```

---
