"""
Script to manually test the panels custom bokeh models.

- Models are those defined in index.ts

- Optional installs:
    - ipywidgets
    - ipywidgets_bokeh
    - plotly
    - altair

"""

from io import StringIO

import numpy as np
import param

from bokeh.sampledata.autompg import autompg

import panel as pn

_before = list(locals())

# Model: ace
ace = pn.widgets.Ace(value="import sys", language="python", height=100)

# Model: audio
audio = pn.pane.Audio("http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3", name="Audio")

# Model: card
_w1 = pn.widgets.TextInput(name="Text:")
_w2 = pn.widgets.FloatSlider(name="Slider")
card = pn.Card(_w1, _w2)

# Model: comm_manager
# Model: customselect

# Model: datetime_picker
datetime_picker = pn.widgets.DatetimePicker()
datetime_range_picker = pn.widgets.DatetimeRangePicker()

# Model: deckgl
_MAPBOX_KEY = "pk.eyJ1IjoicGFuZWxvcmciLCJhIjoiY2s1enA3ejhyMWhmZjNobjM1NXhtbWRrMyJ9.B_frQsAVepGIe-HiOJeqvQ"
_json_spec = {
    "initialViewState": {
        "bearing": -27.36,
        "latitude": 52.2323,
        "longitude": -1.415,
        "maxZoom": 15,
        "minZoom": 5,
        "pitch": 40.5,
        "zoom": 6,
    },
    "layers": [
        {
            "@@type": "HexagonLayer",
            "autoHighlight": True,
            "coverage": 1,
            "data": "https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv",
            "elevationRange": [0, 3000],
            "elevationScale": 50,
            "extruded": True,
            "getPosition": "@@=[lng, lat]",
            "id": "8a553b25-ef3a-489c-bbe2-e102d18a3211",
            "pickable": True,
        }
    ],
    "mapStyle": "mapbox://styles/mapbox/dark-v9",
    "views": [{"@@type": "MapView", "controller": True}],
}

deck_gl = pn.pane.DeckGL(_json_spec, mapbox_api_key=_MAPBOX_KEY)

# Model: echarts
_echart = {
    "title": {"text": "ECharts entry example"},
    "tooltip": {},
    "legend": {"data": ["Sales"]},
    "xAxis": {"data": ["shirt", "cardign", "chiffon shirt", "pants", "heels", "socks"]},
    "yAxis": {},
    "series": [{"name": "Sales", "type": "bar", "data": [5, 20, 36, 10, 10, 20]}],
}
echart_pane = pn.pane.ECharts(_echart, height=480, width=640)

# Model: file_downloadm
_sio = StringIO()
autompg.to_csv(_sio)
_sio.seek(0)
file_download = pn.widgets.FileDownload(_sio, embed=True, filename="autompg.csv")

# Model: html (py: Markup)
html = pn.pane.HTML("<h1>TEST<h1>")

# Model: ipywidget
try:
    import ipywidgets as _ipw
    import ipywidgets_bokeh as _ipwb  # noqa

    ipywidget = pn.pane.IPyWidget(_ipw.FloatSlider(description="Float"))
except ImportError:
    ipywidget = "Need to have ipywidgets and ipywidgets_bokeh installed"

# Model: json (py: Markup)
json = pn.pane.JSON({"test": 1, "B": ["1", None]})

# Model: json_editor
json_editor = pn.widgets.JSONEditor(
    value={
        "dict": {"key": "value"},
        "float": 3.14,
        "int": 1,
        "list": [1, 2, 3],
        "string": "A string",
    },
    width=500,
)

# Model: katex
latex1 = pn.pane.LaTeX(
    r"The LaTeX pane supports two delimiters: $LaTeX$ and \(LaTeX\)",
    styles={"font-size": "18pt"},
    width=800,
)

# Model: location

# Model: mathjax
latex2 = pn.pane.LaTeX(
    r"$\sum_{j}{\sum_{i}{a*w_{j, i}}}$", renderer="mathjax", styles={"font-size": "18pt"}
)

# Model: perspective
_data = {"x": [1, 2, 3], "y": [1, 2, 3]}
perspective = pn.pane.Perspective(_data)

# Model: player
player = pn.widgets.Player(
    name="Player", start=0, end=100, value=32, loop_policy="loop"
)

# Model: plotly
try:
    import plotly.express as _px

    plotly = pn.pane.Plotly(
        _px.line({"Day": range(7), "Orders": range(7)}, x="Day", y="Orders")
    )
except ImportError:
    plotly = "Need to have plotly installed"

# Model: progress
progress = pn.indicators.Progress(name="Progress", value=20, width=200, height=20)

# Model: quill
text_editor = pn.widgets.TextEditor(placeholder="Enter some text", width=500)

# Model: reactive_html
class _Slideshow(pn.reactive.ReactiveHTML):

    index = param.Integer(default=0)

    _template = '<img id="slideshow" src="https://picsum.photos/800/300?image=${index}" onclick="${_img_click}"></img>'

    def _img_click(self, event):
        self.index += 1


_Slideshow.name = "ReactiveHTML <br> (not working in html)"
reactive = _Slideshow(width=800, height=300)

# Model: singleselect
single_select = pn.widgets.Select(value="A", options=list("ABCD"))

# Model: speech_to_text
# speech_to_text_basic = pn.widgets.SpeechToText(button_type="light")

# Model: state
# Model: tabs
_w1 = pn.widgets.TextInput(name="Text:")
_w2 = pn.widgets.FloatSlider(name="Slider")
tabs = pn.Tabs(_w1, _w2)

# Model: tabulator
tabulator = pn.widgets.Tabulator(autompg)


# Model: terminal
terminal = pn.widgets.Terminal(
    "Welcome to the Panel Terminal!\nI'm based on xterm.js\n\n",
    options={"cursorBlink": True},
    height=300,
    sizing_mode="stretch_width",
)

# Model: text_to_speech
# text_to_speech = pn.widgets.TextToSpeech(name="Speech Synthesis")

# Model: trend
_data = {"x": np.arange(50), "y": np.random.randn(50).cumsum()}
trend = pn.indicators.Trend(name="Price", data=_data, width=200, height=200)

# Model: vega
try:
    import altair as _alt

    _chart = (
        _alt.Chart(autompg)
        .mark_circle(size=60)
        .encode(
            x="hp", y="mpg", color="origin", tooltip=["name", "origin", "hp", "mpg"]
        )
        .interactive()
    )

    vega = pn.pane.Vega(_chart)
except ImportError:
    vega = "Need to have altair installed"


# Model: video
video = pn.pane.Video(
    "https://file-examples.com/storage/fe2333f3be630e8e7965da7/2017/04/file_example_MP4_480_1_5MG.mp4",
    width=640,
    height=360,
    loop=True,
)

# Model: videostream
video_stream = pn.widgets.VideoStream(name="Video Stream")

# Model: vtk.vtkjs
# Model: vtk.vtkvolume
# Model: vtk.vtkaxes
# Model: vtk.vtksynchronized


# Combine and save to html
widgets = [v for k, v in locals().items() if k not in _before and not k.startswith("_")]
names = [getattr(w.__class__, "name", w) for w in widgets]
combined = pn.Column(
    *[
        pn.Column(
            pn.Row(pn.Column(n, width=300), w),
            pn.layout.Divider(),
            sizing_mode="stretch_width",
        )
        for w, n, in zip(widgets, names)
    ]
)

if __name__ == "__main__":
    from bokeh.resources import INLINE

    combined.save("models.html", resources=INLINE)
elif __name__.startswith("bokeh"):
    combined.servable()
