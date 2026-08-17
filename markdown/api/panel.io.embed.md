# panel.io.embed module

Various utilities for recording and embedding state in a rendered app.

panel.io.embed.embed_state(panel, model, doc, max_states=1000, max_opts=3, json=False, json_prefix='', save_path='./', load_path=None, progress=True, states={})
Embeds the state of the application on a State model which allows
exporting a static version of an app. This works by finding all widgets
with a predefined set of options and evaluating the cross product of the
widget values and recording the resulting events to be replayed when
exported. The state is recorded on a State model which is attached as an
additional root on the Document.

Parameters:
**panel: panel.reactive.Reactive**
The Reactive component being exported

**model: bokeh.model.Model**
The bokeh model being exported

**doc: bokeh.document.Document**
The bokeh Document being exported

**max_states: int (default=1000)**
The maximum number of states to export

**max_opts: int (default=3)**
The max number of ticks sampled in a continuous widget like a slider

**json: boolean (default=True)**
Whether to export the data to json files

**json_prefix: str (default=’’)**
Prefix for JSON filename

**save_path: str (default=’./’)**
The path to save json files to

**load_path: str (default=None)**
The path or URL the json files will be loaded from.

**progress: boolean (default=True)**
Whether to report progress

**states: dict (default={})**
A dictionary specifying the widget values to embed for each widget

panel.io.embed.link_to_jslink(model, source, src_spec, target, tgt_spec)
Converts links declared in Python into JS Links by using the declared
forward and reverse JS transforms on the source and target.

panel.io.embed.param_to_jslink(model, widget)
Converts Param pane widget links into JS links if possible.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
