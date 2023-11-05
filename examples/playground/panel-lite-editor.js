const appContainer = "app-container"
const codeEditor = "code-editor"

const welcomeExample=`\
import panel as pn
pn.extension()

pn.pane.Markdown("Welcome! Try clicking the \`run\` button.").servable()
`

const buttonExample=`\
import panel as pn
pn.extension(design="material")
button = pn.widgets.Button(name="Click Me")
component = pn.Row(button, pn.bind(lambda c: c, button.param.clicks))

component.servable()
`

const matplotlibExample=`
import panel as pn

import numpy as np

from matplotlib.figure import Figure
from matplotlib import cm
from matplotlib.backends.backend_agg import FigureCanvas  # not needed for mpl >= 3.1

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
`

const perspectiveExample=`
import panel as pn
import pandas as pd

import random
from datetime import datetime, timedelta

pn.extension("perspective")

data = {
    "int": [random.randint(-10, 10) for _ in range(9)],
    "float": [random.uniform(-10, 10) for _ in range(9)],
    "date": [(datetime.now() + timedelta(days=i)).date() for i in range(9)],
    "datetime": [(datetime.now() + timedelta(hours=i)) for i in range(9)],
    "category": [
        "Category A",
        "Category B",
        "Category C",
        "Category A",
        "Category B",
        "Category C",
        "Category A",
        "Category B",
        "Category C",
    ],
}
df = pd.DataFrame(data)

pn.pane.Perspective(df, width=1000).servable()
`

const fastTemplateExample=`\
import panel as pn
pn.extension()
button = pn.widgets.Button(name="Click Me")
component = pn.Row(button, pn.bind(lambda c: c, button.param.clicks))

pn.template.FastListTemplate(title="Panel Pyodide", main=[component]).servable()
`

const plotlyExample=`
import panel as pn
import numpy as np
import plotly.graph_objs as go

pn.extension("plotly")

xx = np.linspace(-3.5, 3.5, 100)
yy = np.linspace(-3.5, 3.5, 100)
x, y = np.meshgrid(xx, yy)
z = np.exp(-(x-1)**2-y**2)-(x**3+y**4-x/5)*np.exp(-(x**2+y**2))

surface = go.Surface(z=z)
layout = go.Layout(
    title='Plotly 3D Plot',
    autosize=False,
    width=500,
    height=500,
    margin=dict(t=50, b=50, r=50, l=50)
)

fig = dict(data=[surface], layout=layout)

pn.pane.Plotly(fig).servable()
`

function getCodeFromCodeEditor(){
    return document.getElementById(codeEditor).value
}

async function buildApp(){
    let code = getCodeFromCodeEditor()
    console.log(`sending code to ${appContainer}`)
    iframe = document.getElementById(appContainer)
    iframe.contentWindow.postMessage(code, '*');
}

function reloadIframe(){
    document.getElementById(appContainer).contentWindow.location.reload();
}

function configureCodeEditor(example=welcomeExample){
    document.getElementById("code-editor").value=example
}
async function configureAndBuildApp(example){
    configureCodeEditor(example=example)
    await buildApp()
}
