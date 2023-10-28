import param

import panel as pn

from panel.reactive import ReactiveHTML

pn.extension("codeeditor", "terminal", design="bootstrap")

HELLO_WORLD_EXAMPLE = """\
import panel as pn

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
    f"I'm a Hugging Face Transformers `{MODEL}` model.\\n\\nPlease *send a message*!",
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

LOADING_SPINNER = """
<svg id="loading" xmlns="http://www.w3.org/2000/svg" style="margin: auto; background: none; display: block; shape-rendering: auto;" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid">
<rect x="15" y="30" width="10" height="40" fill="#424242">
  <animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.5 0 0.5 1;0.5 0 0.5 1" values="1;0.2;1" begin="-0.6"/>
</rect><rect x="35" y="30" width="10" height="40" fill="#424242">
  <animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.5 0 0.5 1;0.5 0 0.5 1" values="1;0.2;1" begin="-0.4"/>
</rect><rect x="55" y="30" width="10" height="40" fill="#424242">
  <animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.5 0 0.5 1;0.5 0 0.5 1" values="1;0.2;1" begin="-0.2"/>
</rect><rect x="75" y="30" width="10" height="40" fill="#424242">
  <animate attributeName="opacity" dur="1s" repeatCount="indefinite" calcMode="spline" keyTimes="0;0.5;1" keySplines="0.5 0 0.5 1;0.5 0 0.5 1" values="1;0.2;1" begin="-1"/>
</rect></svg>
"""

TEMPLATE = f"""
<div id="pn-container" style="height:100%;width:100%;border: 1px solid black">
    {LOADING_SPINNER}
</div>
"""


class PanelPlayground(ReactiveHTML):
    code = param.String(HELLO_WORLD_EXAMPLE)
    timeout = param.Integer(25, bounds=(1, 1000))
    examples = param.Dict(EXAMPLES)

    log_message = param.String(label="Status")
    running = param.Boolean()

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
        "render": """
data.running=true;
state.main = document.createElement('div');
state.code=""
state.ready=false;

state.log = (message)=>{
    data.log_message = message
}

async function main() {
    state.log("Loading pyodide")
    let pyodide = await loadPyodide();
    state.pyodide = pyodide
    state.log("Loading micropip")
    await pyodide.loadPackage("micropip");
    state.log("Loading packages")
    await pyodide.runPythonAsync(`
    import micropip
    await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.3.0-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.3.0/dist/wheels/panel-1.3.0-py3-none-any.whl', 'pyodide-http==0.2.1', 'param', "matplotlib", "transformers_js_py"]);
    `);
}
main().then(()=>{self.runCode()})
""",
        "preCode": """
    data.running=true;
    state.log("Started running the code")
    state.code=data.code;
    const body = document.querySelector('body');
    state.main.innerHTML=""
    state.main.id = 'main';
    body.appendChild(state.main);
    """,
        "postCode": """
    const checkDiv = setInterval(() => {
    if (state.main.hasChildNodes()) {
        clearInterval(checkDiv);
        pn_container.appendChild(state.main);
        data.running=false;
        if (state.code!=data.code){
            state.log("Code changed. I will run the code again")
            self.runCode()
        } else {
            state.log("Finished Running Code")
        }
    } else {
        state.log('Waiting. The code has not been executed yet');
    }
    }, data.timeout);
    """,
        "runCode": """
    self.preCode()
    const cleanCode=data.code.replace(".servable()", '.servable(target="main")')
    state.pyodide.runPythonAsync(cleanCode).then(()=>{
        self.postCode()
    })
    .catch((error) => {
        state.log('An error occurred:' + error.toString());
        pn_container.appendChild(state.main);
        data.running=false;
        state.main.innerText=error.toString();
        if (state.code!=data.code){
            state.log("Code changed. I will run the code again")
            self.runCode()
        }
    });

    """,
        "code": """
    if (!data.running){self.runCode()}else{state.log("The code is already running.")}
    """,
        "running": """
    if (data.running==true){
        setTimeout(() => {
            if (data.running){loading.style.display="block";}
        }, "200");
    } else {loading.style.display="none"}
    """
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
        "#### Status",
        pn.widgets.Checkbox.from_param(playground.param.running, disabled=True),
        pn.pane.Str(playground.param.log_message, name="Status"),
        width=300,
    ),
    pn.widgets.CodeEditor.from_param(playground.param.code, sizing_mode="stretch_both"),
    playground,
).servable()
