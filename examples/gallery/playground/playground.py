from pathlib import Path

import param

import panel as pn

from panel.reactive import ReactiveHTML

pn.extension("codeeditor", "terminal", design="bootstrap")

HELLO_WORLD_EXAMPLE = """\
import panel as pn
import transformers_js

pn.extension("terminal")

pn.panel("Hello World").servable()
"""

TRANSFORMERS_EXAMPLE = '''\
import panel as pn

MODEL = "sentiment-analysis"
pn.chat.ChatMessage.default_avatars["hugging face"] = "🤗"

pn.extension(design="material")

@pn.cache
async def _get_pipeline(model):
    from transformers_js import import_transformers_js
    transformers = await import_transformers_js()
    return await transformers.pipeline(model)

async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    pipe = await _get_pipeline(MODEL)
    response = await pipe(contents)
    label, score = response[0]["label"], round(response[0]["score"], 2)
    return f"""I feel a {label} vibe here (score: {score})"""

welcome_message = pn.chat.ChatMessage(
    f"""I'm a Hugging Face Transformers `{MODEL}` model.

Please *send a message*!""",
    user="Hugging Face",
)

pn.chat.ChatInterface(
    welcome_message, placeholder_text="Loading the model ...",
    callback=callback, callback_user="Hugging Face",
).servable()
'''

EXAMPLES = {
    "Hello World": HELLO_WORLD_EXAMPLE,
    "Reactive Expressions": """
import panel as pn
import param

pn.extension()


count = pn.widgets.IntSlider(value=1, start=0, end=10, name="Count")
expr = count.rx() * "⭐"

pn.panel(expr).servable()
""",
    "Matplotlib": """\
import numpy as np

from matplotlib.figure import Figure
from matplotlib import cm
from matplotlib.backends.backend_agg import FigureCanvas  # not needed for mpl >= 3.1

import panel as pn
pn.extension()

Y, X = np.mgrid[-3:3:100j, -3:3:100j]
U = -1 - X**2 + Y
V = 1 + X - Y**2
speed = np.sqrt(U*U + V*V)

fig0 = Figure(figsize=(8, 6))
ax0 = fig0.subplots()
FigureCanvas(fig0)  # not needed for mpl >= 3.1

strm = ax0.streamplot(X, Y, U, V, color=U, linewidth=2, cmap=cm.autumn)
fig0.colorbar(strm.lines)

pn.pane.Matplotlib(fig0, dpi=144).servable()
""",
    "Hugging Face Transformers": TRANSFORMERS_EXAMPLE,
}
EXAMPLES = {key: EXAMPLES[key] for key in sorted(EXAMPLES)}

TEMPLATE = f"""
<div id="pn-container" style="height:100%;width:100%;border: 1px solid black">
<iframe id="pn-iframe"></iframe>
</div>
"""

PANEL_LITE_JS = (Path(__file__).parent/"panel-lite.js").read_text()

class PanelPlayground(ReactiveHTML):
    code = param.String(HELLO_WORLD_EXAMPLE)
    examples = param.Dict(EXAMPLES)

    _template = TEMPLATE

    __javascript__ = [
        "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.js",
        "https://cdn.bokeh.org/bokeh/release/bokeh-3.3.0.min.js",
        "https://cdn.bokeh.org/bokeh/release/bokeh-gl-3.3.0.min.js",
        "https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.3.0.min.js",
        "https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.3.0.min.js",
        "https://cdn.holoviz.org/panel/1.3.0/dist/panel.min.js",
    ]

    _scripts = {
        "render": PANEL_LITE_JS + """
async function main() {
    state.editor = new PanelLiteEditor(el=pn_container, code=data.code);
    await state.editor.panel_lite.load()
}
main().then(()=>{self.code()})
""",
        "code": """
let command = `
from panel.io.convert import script_to_html
from io import StringIO
code = \"\"\"import panel as pn\npn.extension()\npn.panel('hello').servable()\"\"\"
print(code)
file = StringIO(code)
html, web_worker = script_to_html(file)
html
`
pyodide = state.editor.panel_lite.pyodide
this.pyodide.runPythonAsync(command).then((html)=>{pn_iframe.srcdoc=html});
    """,
    }

playground = PanelPlayground(sizing_mode="stretch_both")
examples = pn.widgets.RadioButtonGroup(
    options=EXAMPLES,
    name="Examples",
    orientation="vertical",
    sizing_mode="stretch_width",
    button_style="outline",
)

@pn.depends(examples, watch=True)
def _apply_example(value):
    playground.code = value

pn.Row(
    pn.Column(
        "#### Examples",
        examples,
        width=300,
    ),
    pn.widgets.CodeEditor.from_param(playground.param.code, sizing_mode="stretch_both"),
    playground,
).servable()
