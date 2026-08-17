# panel.io.save module

Defines utilities to save panel objects to files as HTML or PNG.

panel.io.save.save(panel: Viewable \| Document \| BaseTemplate, filename: str \| os.PathLike \| t.IO, title: str \| None = None, resources: BkResources \| None = None, template: Template \| str \| None = None, template_variables: dict\[str, t.Any\] \| None = None, embed: bool = False, max_states: int = 1000, max_opts: int = 3, embed_json: bool = False, json_prefix: str = '', save_path: str = './', load_path: str \| None = None, progress: bool = True, embed_states={}, as_png: bool \| None = None, **kwargs) → None
Saves Panel objects to file.

Parameters:
**panel: Viewable \| bokeh.document.Document \| panel.template.base.BaseTemplate**
The Panel Viewable to save to file

**filename: str or file-like object**
Filename to save the plot to

**title: str**
Optional title for the plot

**resources: bokeh.resources.Resources**
One of the valid bokeh.resources (e.g. CDN or INLINE)

**template: jinja2.Template \| str**
template file, as used by bokeh.file_html. If None will use bokeh
defaults

**template_variables: Dict\[str, Any\]**
template_variables file dict, as used by bokeh.file_html

**embed: bool**
Whether the state space should be embedded in the saved file.

**max_states: int**
The maximum number of states to embed

**max_opts: int**
The maximum number of states for a single widget

**embed_json: boolean (default=True)**
Whether to export the data to json files

**json_prefix: str (default=’’)**
Prefix for the randomly json directory

**save_path: str (default=’./’)**
The path to save json files to

**load_path: str (default=None)**
The path or URL the json files will be loaded from.

**progress: boolean (default=True)**
Whether to report progress

**embed_states: dict (default={})**
A dictionary specifying the widget values to embed for each widget

**as_png: boolean (default=None)**
To save as a .png. If None save_png will be true if filename is string
and ends with png.

panel.io.save.save_png(model: UIElement \| Document, filename: str \| os.PathLike \| t.IO, resources: BkResources = Resources(mode='cdn'), template=None, template_variables: dict\[str, t.Any\] \| None = None, timeout: int = 5) → None
Saves a bokeh model to png

Parameters:
**model: bokeh.model.Model**
Model to save to png

**filename: str**
Filename to save to

**resources: str**
Resources

**template:**
template file, as used by bokeh.file_html. If None will use bokeh
defaults

**template_variables:**
template_variables file dict, as used by bokeh.file_html

**timeout: int**
The maximum amount of time (in seconds) to wait for

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
