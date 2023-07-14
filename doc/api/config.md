# Config

The `pn.config` object allows setting various configuration variables, the config variables can also be set as environment variables or passed through the [`pn.extension`](cheatsheet#pn-extension):

### Python only

`css_files`
: External CSS files to load.

`js_files`
: External JS files to load. Dictionary should map from exported name to the URL of the JS file.

`loading_spinner`
: The style of the global loading indicator, e.g. 'arcs', 'bars', 'dots', 'petals'.

`loading_color`
: The color of the global loading indicator as a hex color, e.g. #6a6a6a

`defer_load`
: Whether reactive function evaluation is deferred until the page is rendered.

`exception_handler`
: A custom exception handler can be defined which should accept any exceptions raised while processing events originating from the frontend and onload callbacks.

`loading_indicator`
: Whether a loading indicator is shown by default when panes are updating.

`nthreads`
: If set will start a `ThreadPoolExecutor` to dispatch events to for concurrent execution on separate cores. By default no thread pool is launched, while setting nthreads=0 launches `min(32, os.cpu_count() + 4)` threads.

`raw_css`
: List of raw CSS strings to add to load.

`reuse_sessions`
: Whether to reuse a session for the initial request to speed up the initial page render. Note that if the initial page differs between sessions, e.g. because it uses query parameters to modify the rendered content, then this option will result in the wrong content being rendered. See the corresponding [how-to guide](../how_to/performance/reuse_sessions.md) for more information.

`safe_embed`
: Whether to record all set events when embedding rather than just those that are changed

`session_history`
: If set to a non-zero value this determines the maximum length of the pn.state.session_info dictionary, which tracks information about user sessions. A value of -1 indicates an unlimited history.
`sizing_mode`
:  Specify the default sizing mode behavior of panels.

`template`
: The template to render the served application into, e.g. `'bootstrap'` or `'material'`.

`theme`
: The theme to apply to the selected template (no effect unless `template` is set)

`throttled`
: Whether sliders and inputs should be throttled until release of mouse.

### Python and Environment variables

`admin_log_level` (`PANEL_ADMIN_LOG_LEVEL`):
Log level of Panel admin's logger (default=DEBUG).

`comms` (`PANEL_COMMS`)
: Whether to render output in Jupyter with the default Jupyter extension or use the `jupyter_bokeh` ipywidget model.

`console_output` (`PANEL_CONSOLE_OUTPUT`): How to log errors and stdout output triggered by callbacks from Javascript in the notebook. Options include `'accumulate'`, `'replace'` and `'disable'`.

`embed` (`PANEL_EMBED`)
: Whether plot data will be [embedded](./Deploy_and_Export.rst#Embedding).

`embed_json` (`PANEL_EMBED_JSON`)
: Whether to save embedded state to json files.

`embed_json_prefix` (`PANEL_EMBED_JSON_PREFIX`)
: Prefix for randomly generated json directories.

`embed_load_path` (`PANEL_EMBED_LOAD_PATH`)
: Where to load json files for embedded state.

`embed_save_path` (`PANEL_EMBED_SAVE_PATH`)
: Where to save json files for embedded state.

`inline` (`PANEL_INLINE`)
: Whether to inline JS and CSS resources. If disabled, resources are loaded from CDN if one is available.

`log_level` (`PANEL_LOG_LEVEL`)
: Log level of Panel's logger (default=WARNING).

`npm_cdn` (`PANEL_NPM_CDN`)
: The CDN to load NPM packages from if resources are served from CDN. Allows switching between 'https://unpkg.com' (default) and 'https://cdn.jsdelivr.net/npm' for most resources.
