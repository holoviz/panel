# FileSelector
---
```python
import panel as pn
pn.extension()
```

The `FileSelector` widget allows browsing the filesystem on the server and selecting one or more files in a directory.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **`directory`** (str): The directory to browse (cannot access files above this directory).
* **`file_pattern`** (str, default='*'): A glob-like query expression to limit the displayed files.
* **`only_files`** (bool, default=False): Whether to only allow selecting files.
* **`refresh_period`** (int, default=None): If set to non-None value indicates how frequently to refresh the directory contents in milliseconds.
* **`root_directory`** (str, default=None): If set to non-None value overrides directory parameter as the root directory beyond which users cannot navigate.
* **`show_hidden`** (bool, default=False): Whether to show hidden files and directories (starting with a period).
* **`value`** (list[str]): A list of file names.

##### Display

* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

The `FileSelector` widget allows exploring the specified directory on the server's filesystem and any directories contained within it. The widget consists of the navigation bar with a number of buttons and the address bar:

* Back (`◀`): Goes to the previous directory
* Forward (`▶`): Returns to the last directory after navigating back
* Up (`⬆`): Goes one directory up
* Address bar: Display the directory to navigate to
* Enter (`⬇`): Navigates to the directory in the address bar
* Reload (`↻`): Reloads the contents of the current directory

The actual file selector displays the contents of the current directory, to navigate to a subfolder either double-click on it or click on a directory in the file selector and then hit the down arrow (`⬇`) in the navigation bar. Files and folders may be selected by selecting them in the browser on the left and moving them to the right with the arrow buttons:

```python
files = pn.widgets.FileSelector('~')

files
```

To get the currently selected files simply access the `value` parameter:

```python
files.value
```

## Remote filesystem

By using the power of `fsspec` we can connect to remote filesystems. In the example below we use the `s3fs` package to connect to a remote S3 server

```python
import s3fs

fs = s3fs.S3FileSystem(anon=True)

s3_files = pn.widgets.FileSelector(directory="s3://datasets.holoviz.org", fs=fs)
s3_files
```

```python
s3_files.value
```

---
