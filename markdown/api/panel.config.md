# panel.config module

The config module supplies the global config object and the extension
which provides convenient support for loading and configuring panel
components.

class panel.config.panel_extension(\*args, **kwargs)
Bases: `extension`

Initializes and configures Panel. You should always run pn.extension as
it declares which components should be loaded in your app or notebook.

- Initialize the notebook extension to enable bi-directional
  communication and loading JS and CSS resources.

- Load .js libraries (positional arguments).

- Update the global configuration pn.config (keyword arguments).

Parameters:
\*args : tuple\[str\]
Positional arguments listing the extension to load. For example
“plotly”, “tabulator”.

**params : dict\[str,Any\]
Keyword arguments to be set on the pn.config element. See
[https://panel.holoviz.org/api/config.html](https://panel.holoviz.org/api/config.html)

**:Example:**

**\>\>\> import panel as pn**

**\>\>\> pn.extension(“plotly”, sizing_mode=”stretch_width”, template=”fast”)**

**This will**

**- Initialize the notebook extension.**

**- Enable you to use the \`Plotly\` pane by loading \`plotly.js\`.**

**- Set the default \`sizing_mode\` to \`stretch_width\` instead of \`fixed\`.**

**- Set the global configuration \`pn.config.template\` to \`fast\`, i.e. you**
will be using the FastListTemplate.

**Parameter Definitions**

------------------------------------------------------------------------

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
