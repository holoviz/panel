import base64
import json

import numpy as np

from panel.pane import DataFrame, JSON, HTML, Markdown, PaneBase, Pane, Str
from panel.tests.util import pd_available, streamz_available


def test_get_markdown_pane_type():
    assert PaneBase.get_pane_type("**Markdown**") is Markdown

@pd_available
def test_get_dataframe_pane_type():
    import pandas as pd
    df = pd._testing.makeDataFrame()
    assert PaneBase.get_pane_type(df) is DataFrame

@pd_available
def test_get_series_pane_type():
    import pandas as pd
    df = pd._testing.makeDataFrame()
    assert PaneBase.get_pane_type(df.iloc[:, 0]) is DataFrame

@streamz_available
def test_get_streamz_dataframe_pane_type():
    from streamz.dataframe import Random
    sdf = Random(interval='200ms', freq='50ms')
    assert PaneBase.get_pane_type(sdf) is DataFrame

@streamz_available
def test_get_streamz_dataframes_pane_type():
    from streamz.dataframe import Random
    sdf = Random(interval='200ms', freq='50ms').groupby('y').sum()
    assert PaneBase.get_pane_type(sdf) is DataFrame

@streamz_available
def test_get_streamz_series_pane_type():
    from streamz.dataframe import Random
    sdf = Random(interval='200ms', freq='50ms')
    assert PaneBase.get_pane_type(sdf.x) is DataFrame

@streamz_available
def test_get_streamz_seriess_pane_type():
    from streamz.dataframe import Random
    sdf = Random(interval='200ms', freq='50ms').groupby('y').sum()
    assert PaneBase.get_pane_type(sdf.x) is DataFrame


def test_markdown_pane(document, comm):
    pane = Pane("**Markdown**")

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.endswith("&lt;p&gt;&lt;strong&gt;Markdown&lt;/strong&gt;&lt;/p&gt;")

    # Replace Pane.object
    pane.object = "*Markdown*"
    assert pane._models[model.ref['id']][0] is model
    assert model.text.endswith("&lt;p&gt;&lt;em&gt;Markdown&lt;/em&gt;&lt;/p&gt;")

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}

def test_markdown_pane_dedent(document, comm):
    pane = Pane("    ABC")

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.endswith("&lt;p&gt;ABC&lt;/p&gt;")

    pane.dedent = False
    assert model.text.startswith('&lt;div class=&quot;codehilite')


def test_markdown_pane_extensions(document, comm):
    pane = Pane("""
    ```python
    None
    ```
    """)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('&lt;div class=&quot;codehilite')

    pane.extensions = ["extra", "smarty"]
    assert model.text.startswith('&lt;pre&gt;&lt;code class=&quot;language-python')


def test_html_pane(document, comm):
    pane = HTML("<h1>Test</h1>")

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "&lt;h1&gt;Test&lt;/h1&gt;"

    # Replace Pane.object
    pane.object = "<h2>Test</h2>"
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "&lt;h2&gt;Test&lt;/h2&gt;"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


@pd_available
def test_dataframe_pane_pandas(document, comm):
    import pandas as pd
    pane = DataFrame(pd._testing.makeDataFrame())

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('&lt;table')
    orig_text = model.text

    # Replace Pane.object
    pane.object = pd._testing.makeMixedDataFrame()
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('&lt;table')
    assert model.text != orig_text

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}

@pd_available
def test_dataframe_pane_supports_escape(document, comm):
    import pandas as pd
    url = "<a href='https://panel.holoviz.org/'>Panel</a>"
    df = pd.DataFrame({"url": [url]})
    pane = DataFrame(df)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert pane.escape
    assert "&lt;a href=&#x27;https://panel.holoviz.org/&#x27;&gt;Panel&lt;/a&gt;" not in model.text

    pane.escape = False
    assert "&lt;a href=&#x27;https://panel.holoviz.org/&#x27;&gt;Panel&lt;/a&gt;" in model.text

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


@streamz_available
def test_dataframe_pane_streamz(document, comm):
    from streamz.dataframe import Random
    sdf = Random(interval='200ms', freq='50ms')
    pane = DataFrame(sdf)

    assert pane._stream is None

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._stream is not None
    assert pane._models[model.ref['id']][0] is model
    assert model.text == ''

    # Replace Pane.object
    pane.object = sdf.x
    assert pane._models[model.ref['id']][0] is model
    assert model.text == ''

    # Cleanup
    pane._cleanup(model)
    assert pane._stream is None
    assert pane._models == {}


def test_string_pane(document, comm):
    pane = Str("<h1>Test</h1>")

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "&lt;pre&gt;&lt;h1&gt;Test&lt;/h1&gt;&lt;/pre&gt;"

    # Replace Pane.object
    pane.object = "<h2>Test</h2>"
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "&lt;pre&gt;&lt;h2&gt;Test&lt;/h2&gt;&lt;/pre&gt;"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


class NumpyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            data_b64 = base64.b64encode(obj.data).decode('utf-8')
            return dict(__ndarray__=data_b64,
                        dtype=str(obj.dtype),
                        shape=obj.shape)
        return json.JSONEncoder.default(self, obj)

def test_json_applies():
    assert JSON.applies({1: 2})
    assert JSON.applies([1, 2, 3])
    assert JSON.applies('{"a": 1}') == 0
    assert not JSON.applies({'array': np.array([1, 2, 3])})
    assert JSON.applies({'array': np.array([1, 2, 3])}, encoder=NumpyEncoder)


def test_json_pane(document, comm):
    pane = JSON({'a': 2})

    model = pane.get_root(document, comm=comm)

    assert model.text == '{"a": 2}'
    assert pane._models[model.ref['id']][0] is model

    pane.object = '{"b": 3}'
    assert model.text == '{"b": 3}'
    assert pane._models[model.ref['id']][0] is model

    pane.object = {"test": "can't show this"}
    assert model.text == '{"test": "can\'t show this"}'
    assert pane._models[model.ref['id']][0] is model

    pane.object = ["can't show this"]
    assert model.text == '["can\'t show this"]'
    assert pane._models[model.ref['id']][0] is model

    pane.object = "can't show this"
    assert model.text == '"can\'t show this"'
    assert pane._models[model.ref['id']][0] is model

    pane.object = "can show this"
    assert model.text == '"can show this"'
    assert pane._models[model.ref['id']][0] is model

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


def test_json_pane_rerenders_on_depth_change(document, comm):
    pane = JSON({'a': 2}, depth=2)

    model = pane.get_root(document, comm=comm)

    pane.depth = -1

    assert model.depth is None
