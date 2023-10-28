import param

import panel as pn

from panel.reactive import ReactiveHTML

pn.extension("codeeditor", "terminal", design="bootstrap")

HELLO_WORLD_EXAMPLE = """\
import panel as pn

pn.extension("terminal")

pn.panel("Hello World").servable()
"""

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
}
EXAMPLES = {key: EXAMPLES[key] for key in sorted(EXAMPLES)}

TEMPLATE = """
<div id="pn-container" style="height:100%;width:100%;border: 1px solid black"></div>
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
state.main = document.createElement('div');
state.code=""
state.ready=false;
data.running=true;

state.log = (message)=>{
    console.log(message);
    data.log_message = "\\n"
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
    await micropip.install(['https://cdn.holoviz.org/panel/wheels/bokeh-3.3.0-py3-none-any.whl', 'https://cdn.holoviz.org/panel/1.3.0/dist/wheels/panel-1.3.0-py3-none-any.whl', 'pyodide-http==0.2.1', 'param', "matplotlib"]);
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
        playground.param.running,
        pn.pane.Str(playground.param.log_message, name="Status"),
        width=300,
    ),
    pn.widgets.CodeEditor.from_param(playground.param.code, sizing_mode="stretch_both"),
    playground,
).servable()
