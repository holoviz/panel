import asyncio
import base64
import html
import json
import sys

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from panel import config
from panel.pane import (
    HTML, JSON, DataFrame, Markdown, PaneBase, Str,
)
from panel.tests.util import not_windows, streamz_available


def test_get_markdown_pane_type():
    assert PaneBase.get_pane_type("**Markdown**") is Markdown

def test_get_dataframe_pane_type():
    df = pd.DataFrame({"A": [1, 2, 3]})
    assert PaneBase.get_pane_type(df) is DataFrame

def test_get_series_pane_type():
    ser = pd.Series([1, 2, 3])
    assert PaneBase.get_pane_type(ser) is DataFrame

@pytest.fixture
async def streamz_df():
    from streamz.dataframe import Random
    sdf = Random(interval='200ms', freq='50ms', start=False)
    sdf.start()
    yield sdf
    sdf.stop()
    sdf.loop.asyncio_loop.stop()
    while sdf.loop.asyncio_loop.is_running():
        await asyncio.sleep(0.1)
    sdf.loop.asyncio_loop.close()

@not_windows
@streamz_available
def test_get_streamz_dataframe_pane_type(streamz_df):
    assert PaneBase.get_pane_type(streamz_df) is DataFrame

@not_windows
@streamz_available
def test_get_streamz_dataframes_pane_type(streamz_df):
    assert PaneBase.get_pane_type(streamz_df.groupby('y').sum()) is DataFrame

@not_windows
@streamz_available
def test_get_streamz_series_pane_type(streamz_df):
    assert PaneBase.get_pane_type(streamz_df.x) is DataFrame

@not_windows
@streamz_available
def test_get_streamz_seriess_pane_type(streamz_df):
    assert PaneBase.get_pane_type(streamz_df.groupby('y').sum().x) is DataFrame

def test_markdown_pane(document, comm):
    pane = Markdown("**Markdown**")

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.endswith("&lt;p&gt;&lt;strong&gt;Markdown&lt;/strong&gt;&lt;/p&gt;\n")

    # Replace Pane.object
    pane.object = "*Markdown*"
    assert pane._models[model.ref['id']][0] is model
    assert model.text.endswith("&lt;p&gt;&lt;em&gt;Markdown&lt;/em&gt;&lt;/p&gt;\n")

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}

def test_markdown_pane_dedent(document, comm):
    pane = Markdown("    ABC")

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.endswith("&lt;p&gt;ABC&lt;/p&gt;\n")

    pane.dedent = False
    assert model.text.startswith('&lt;pre&gt;&lt;code&gt;ABC')

@pytest.mark.parametrize('renderer', ('markdown-it', 'markdown'))
def test_markdown_pane_hard_line_break_default(document, comm, renderer):
    assert Markdown.hard_line_break is False
    txt = "Hello\nWorld\nI am here"
    pane = Markdown(txt, renderer=renderer)
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    # No <br />, single <p>
    assert html.unescape(model.text).rstrip() == f"<p>{txt}</p>"

@pytest.mark.parametrize('renderer', ('markdown-it', 'markdown'))
def test_markdown_pane_hard_line_break_enabled(document, comm, renderer):
    assert Markdown.hard_line_break is False
    pane = Markdown("Hello\nWorld\nI am here", renderer=renderer, hard_line_break=True)
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    # Two <br />, single <p>
    assert html.unescape(model.text).rstrip() == "<p>Hello<br />\nWorld<br />\nI am here</p>"

@pytest.mark.parametrize('hard_line_break', (False, True))
def test_markdown_pane_hard_line_break_myst(document, comm, hard_line_break):
    pytest.importorskip("myst_parser")
    # hard_line_break not supported
    assert Markdown.hard_line_break is False
    txt = "Hello\nWorld\nI am here"
    pane = Markdown(txt, renderer='myst', hard_line_break=hard_line_break)
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    # No <br />, single <p>
    assert html.unescape(model.text).rstrip() == f"<p>{txt}</p>"

@pytest.mark.parametrize('renderer', ('markdown-it', 'markdown', 'myst'))
@pytest.mark.parametrize('hard_line_break', (False, True))
def test_markdown_pane_hard_line_break_default_two_spaces(document, comm, renderer, hard_line_break):
    if renderer == 'myst':
        pytest.importorskip("myst_parser")
    # Same output, whether hard_line_break is True or False
    assert Markdown.hard_line_break is False
    # Note the two empty spaces at the end of each line.
    pane = Markdown("Hello  \nWorld  \nI am here", renderer=renderer, hard_line_break=hard_line_break)
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    # Two <br />, single <p>
    assert html.unescape(model.text).rstrip() == "<p>Hello<br />\nWorld<br />\nI am here</p>"

@pytest.mark.parametrize('renderer', ('markdown-it', 'markdown', 'myst'))
def test_markdown_pane_two_new_lines(document, comm, renderer):
    if renderer == 'myst':
        pytest.importorskip("myst_parser")
    assert Markdown.hard_line_break is False
    pane = Markdown("Hello\n\nWorld", renderer=renderer)
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    # Two <p> elements
    assert html.unescape(model.text).rstrip() == "<p>Hello</p>\n<p>World</p>"

def test_markdown_pane_markdown_it_render_options_breaks(document, comm):
    assert Markdown.hard_line_break is False
    pane = Markdown(
        "Hello\nWorld\nI am here",
        renderer="markdown-it",
        renderer_options={"breaks": True},
    )
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    # Two <br />, single <p>
    assert html.unescape(model.text).rstrip() == "<p>Hello<br />\nWorld<br />\nI am here</p>"

def test_markdown_pane_markdown_it_renderer(document, comm):
    pane = Markdown("""
    - [x] Task1
    - [ ] Task2
    """, renderer='markdown-it')

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text == (
        '&lt;ul class=&quot;contains-task-list&quot;&gt;\n'
        '&lt;li class=&quot;task-list-item&quot;&gt;'
        '&lt;input class=&quot;task-list-item-checkbox&quot; '
        'checked=&quot;checked&quot; disabled=&quot;disabled&quot; '
        'type=&quot;checkbox&quot;&gt; Task1&lt;/li&gt;\n'
        '&lt;li class=&quot;task-list-item&quot;&gt;&lt;input '
        'class=&quot;task-list-item-checkbox&quot; disabled=&quot;disabled&quot; '
        'type=&quot;checkbox&quot;&gt; Task2&lt;/li&gt;\n&lt;/ul&gt;\n'
    )

def test_markdown_pane_markdown_it_renderer_partial_links(document, comm):
    pane = Markdown("[Test](http:/", renderer='markdown-it')

    model = pane.get_root(document, comm=comm)

    assert model.text == '&lt;p&gt;[Test](http:/&lt;/p&gt;\n'

    pane.object = "[Test](http://"

    assert model.text == '&lt;p&gt;[Test](http://&lt;/p&gt;\n'

    pane.object = "[Test](http://google.com)"
    assert model.text == '&lt;p&gt;&lt;a href=&quot;http://google.com&quot;&gt;Test&lt;/a&gt;&lt;/p&gt;\n'

def test_markdown_pane_extensions(document, comm):
    pane = Markdown("""
    ```python
    None
    ```
    """, renderer='markdown')

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert 'codehilite' in model.text

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

def test_html_pane_sanitize_html(document, comm):
    pane = HTML("<h1><strong>HTML</h1></strong>", sanitize_html=True)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.endswith("&lt;strong&gt;HTML&lt;/strong&gt;")

    pane.sanitize_html = False

    assert model.text.endswith('&lt;h1&gt;&lt;strong&gt;HTML&lt;/h1&gt;&lt;/strong&gt;')

def test_dataframe_pane_pandas(document, comm):
    pane = DataFrame(pd.DataFrame({"A": [1, 2, 3]}))

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('&lt;table')
    orig_text = model.text

    # Replace Pane.object
    pane.object = pd.DataFrame({"B": [1, 2, 3]})
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('&lt;table')
    assert model.text != orig_text

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}

def test_dataframe_pane_supports_escape(document, comm):
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

@not_windows
@streamz_available
def test_dataframe_pane_streamz(streamz_df, document, comm):
    pane = DataFrame(streamz_df)

    assert pane._stream is None

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._stream is not None
    assert pane._models[model.ref['id']][0] is model
    assert model.text == ''

    # Replace Pane.object
    pane.object = streamz_df.x
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

@pytest.mark.skipif(sys.version_info < (3, 11), reason="Patch dot import resolution does not work for Python <=3.10")
def test_json_theme():
    assert JSON({"x": 1}).theme == JSON.param.theme.default
    assert JSON({"x": 1}, theme="dark").theme == "dark"

    with patch('panel.config._config.theme', new_callable=lambda: "default"):
        assert JSON({"x": 1}).theme == JSON.param.theme.default

    with patch('panel.config._config.theme', new_callable=lambda: "dark"):
        assert JSON({"x": 1}).theme == JSON.THEME_CONFIGURATION[config.theme]

    with patch('panel.config._config.theme', new_callable=lambda: "dark"):
        assert JSON({"x": 1}, theme="light").theme == "light"
