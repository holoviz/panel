from __future__ import absolute_import, division, unicode_literals

from panel.pane import DataFrame, HTML, Markdown, PaneBase, Pane, Str
from panel.tests.util import pd_available, streamz_available


def test_get_markdown_pane_type():
    assert PaneBase.get_pane_type("**Markdown**") is Markdown

@pd_available
def test_get_dataframe_pane_type():
    import pandas as pd
    df = pd.util.testing.makeDataFrame()
    assert PaneBase.get_pane_type(df) is DataFrame

@pd_available
def test_get_series_pane_type():
    import pandas as pd
    df = pd.util.testing.makeDataFrame()
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
    assert model.text.endswith("<p><strong>Markdown</strong></p>")

    # Replace Pane.object
    pane.object = "*Markdown*"
    assert pane._models[model.ref['id']][0] is model
    assert model.text.endswith("<p><em>Markdown</em></p>")

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


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
    pane = DataFrame(pd.util.testing.makeDataFrame())

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('&lt;table')
    orig_text = model.text

    # Replace Pane.object
    pane.object = pd.util.testing.makeMixedDataFrame()
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('&lt;table')
    assert model.text != orig_text

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
    assert model.text == "<pre>&lt;h1&gt;Test&lt;/h1&gt;</pre>"

    # Replace Pane.object
    pane.object = "<h2>Test</h2>"
    assert pane._models[model.ref['id']][0] is model
    assert model.text == "<pre>&lt;h2&gt;Test&lt;/h2&gt;</pre>"

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}
