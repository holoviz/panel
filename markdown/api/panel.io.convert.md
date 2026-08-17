# panel.io.convert module

class panel.io.convert.DummyRequirement(url: 'str', name: 'str' = 'DUMMY', specifier: 'str' = '')
Bases: `object`

panel.io.convert.collect_python_requirements(code: str \| PathLike \| IO, requirements: list\[str\] \| Literal\['auto'\] \| PathLike = 'auto', panel_version: Literal\['auto', 'local'\] \| str = 'auto', http_patch: bool = True) → list\[str\]
Make sense of python requirements for our Panel script.

panel.io.convert.convert_apps(apps: str \| os.PathLike \| Sequence\[str \| os.PathLike\], dest_path: str \| os.PathLike \| None = None, title: str \| None = None, runtime: Runtimes = 'pyodide-worker', requirements: list\[str\] \| t.Literal\['auto'\] \| os.PathLike = 'auto', resources: list\[str\] \| list\[os.PathLike\] \| None = None, prerender: bool = True, build_index: bool = True, build_pwa: bool = True, pwa_config: dict\[t.Any, t.Any\] = {}, max_workers: int = 4, panel_version: t.Literal\['auto', 'local'\] \| str = 'auto', local_prefix: str = './', http_patch: bool = True, inline: bool = False, compiled: bool = False, verbose: bool = True)
Parameters:
**apps: str \| List\[str\]**
>
>
> The filename(s) of the Panel/Bokeh application(s) to convert.
>
>

dest_path: str \| pathlib.Path
The directory to write the converted application(s) to.

title: str \| None
A title for the application(s). Also used to generate unique name for
the application cache to ensure.

runtime: ‘pyodide’ \| ‘pyscript’ \| ‘pyodide-worker’
The runtime to use for running Python in the browser.

requirements: ‘auto’ \| List\[str\] \| os.PathLike \| Dict\[str, ‘auto’ \| List\[str\] \| os.PathLike\]
The list of requirements to include (in addition to Panel). By default
automatically infers dependencies from imports in the application. May
also provide path to a requirements.txt

prerender: bool
Whether to pre-render the components so the page loads.

build_index: bool
Whether to write an index page (if there are multiple apps).

build_pwa: bool
Whether to write files to define a progressive web app (PWA) including a
manifest and a service worker that caches the application locally

pwa_config: Dict\[Any, Any\]
Configuration for the PWA including (see
[https://developer.mozilla.org/en-US/docs/Web/Manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest))

>
>
> - display: Display options (‘fullscreen’, ‘standalone’, ‘minimal-ui’
>   ‘browser’)
>
> - orientation: Preferred orientation
>
> - background_color: The background color of the splash screen
>
> - theme_color: The theme color of the application
>
>

max_workers: int
The maximum number of parallel workers

panel_version: Literal\[‘auto’ \| ‘local’\] \| str

**‘ The panel version to include.**
local_prefix: str
Prefix for the path to serve local wheel files from.

http_patch: bool
Whether to patch the HTTP request stack with the pyodide-http library to
allow urllib3 and requests to work.

inline: bool
Whether to inline resources.

compiled: bool
Whether to use the compiled and faster version of Pyodide.

panel.io.convert.pack_files(filemap: dict, destination: str \| PathLike \| IO)
Pack files into a zipfile for distribution

panel.io.convert.script_to_html(filename: str \| PathLike \| IO, requirements: list\[str\] = \[\], app_resources: str \| PathLike \| None = None, js_resources: Literal\['auto'\] \| list\[str\] = 'auto', css_resources: Literal\['auto'\] \| list\[str\] \| None = 'auto', runtime: Literal\['pyodide', 'pyscript', 'pyodide-worker', 'pyscript-worker'\] = 'pyodide', prerender: bool = True, panel_version: Literal\['auto', 'local'\] \| str = 'auto', local_prefix: str = './', manifest: str \| None = None, inline: bool = False, compiled: bool = True) → tuple\[str, str \| None\]
Converts a Panel or Bokeh script to a standalone WASM Python
application.

Parameters:
**filename: str \| Path \| IO**
The filename of the Panel/Bokeh application to convert.

**requirements: list\[str\]**
The preprocessed, micropip-compatible list of requirements to include.

**app_resources: os.PathLike**
relative path of zip with data to extract

**js_resources: ‘auto’ \| list\[str\]**
The list of JS resources to include in the exported HTML.

**css_resources: ‘auto’ \| list\[str\] \| None**
The list of CSS resources to include in the exported HTML.

**runtime: ‘pyodide’ \| ‘pyscript’**
The runtime to use for running Python in the browser.

**prerender: bool**
Whether to pre-render the components so the page loads.

**panel_version: Literal\[‘auto’, ‘local’\] \| str**
The panel release version to use in the exported HTML.

**local_prefix: str**
Prefix for the path to serve local wheel files from.

**inline: bool**
Whether to inline resources.

**compiled: bool**
Whether to use pre-compiled pyodide bundles.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
