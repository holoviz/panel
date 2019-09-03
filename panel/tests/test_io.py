import os
import json
import glob

from io import StringIO

from panel import Row
from panel.config import config
from panel.io.embed import embed_state
from panel.pane import Str
from panel.widgets import Select, FloatSlider, Checkbox


def test_embed_discrete(document, comm):
    select = Select(options=['A', 'B', 'C'])
    string = Str()
    select.link(string, value='object')
    panel = Row(select, string)
    with config.set(embed=True):
        model = panel.get_root(document, comm)
    embed_state(panel, model, document)
    _, state = document.roots
    assert set(state.state) == {'A', 'B', 'C'}
    for k, v in state.state.items():
        content = json.loads(v['content'])
        assert 'events' in content
        events = content['events']
        assert len(events) == 1
        event = events[0]
        assert event['kind'] == 'ModelChanged'
        assert event['attr'] == 'text'
        assert event['model'] == model.children[1].ref
        assert event['new'] == '<pre>%s</pre>' % k


def test_embed_continuous(document, comm):
    select = FloatSlider(start=0, end=10)
    string = Str()
    select.link(string, value='object')
    panel = Row(select, string)
    with config.set(embed=True):
        model = panel.get_root(document, comm)
    embed_state(panel, model, document)
    _, state = document.roots
    assert set(state.state) == {0, 1, 2}
    values = [0, 5, 10]
    for k, v in state.state.items():
        content = json.loads(v['content'])
        assert 'events' in content
        events = content['events']
        assert len(events) == 1
        event = events[0]
        assert event['kind'] == 'ModelChanged'
        assert event['attr'] == 'text'
        assert event['model'] == model.children[1].ref
        assert event['new'] == '<pre>%.1f</pre>' % values[k]


def test_embed_checkbox(document, comm):
    checkbox = Checkbox()
    string = Str()
    checkbox.link(string, value='object')
    panel = Row(checkbox, string)
    with config.set(embed=True):
        model = panel.get_root(document, comm)
    embed_state(panel, model, document)
    _, state = document.roots
    assert set(state.state) == {True, False}
    for k, v in state.state.items():
        content = json.loads(v['content'])
        assert 'events' in content
        events = content['events']
        assert len(events) == 1
        event = events[0]
        assert event['kind'] == 'ModelChanged'
        assert event['attr'] == 'text'
        assert event['model'] == model.children[1].ref
        assert event['new'] == '<pre>%s</pre>' % k


def test_save_embed_bytesio():
    checkbox = Checkbox()
    string = Str()
    checkbox.link(string, value='object')
    panel = Row(checkbox, string)
    stringio = StringIO()
    panel.save(stringio, embed=True)
    stringio.seek(0)
    utf = stringio.read()
    assert "&lt;pre&gt;False&lt;" in utf
    assert "&lt;pre&gt;True&lt;" in utf


def test_save_embed(tmpdir):
    checkbox = Checkbox()
    string = Str()
    checkbox.link(string, value='object')
    panel = Row(checkbox, string)
    filename = os.path.join(str(tmpdir), 'test.html')
    panel.save(filename, embed=True)
    assert os.path.isfile(filename)


def test_save_embed_json(tmpdir):
    checkbox = Checkbox()
    string = Str()
    checkbox.link(string, value='object')
    panel = Row(checkbox, string)
    filename = os.path.join(str(tmpdir), 'test.html')
    panel.save(filename, embed=True, embed_json=True,
               save_path=str(tmpdir))
    assert os.path.isfile(filename)
    paths = glob.glob(os.path.join(str(tmpdir), '*'))
    paths.remove(filename)
    assert len(paths) == 1
    json_files = sorted(glob.glob(os.path.join(paths[0], '*.json')))
    assert len(json_files) == 2

    for jf, v in zip(json_files, ('False', 'True')):
        with open(jf) as f:
            state = json.load(f)
        assert 'content' in state
        assert 'events' in state['content']
        events = json.loads(state['content'])['events']
        assert len(events) == 1
        event = events[0]
        assert event['kind'] == 'ModelChanged'
        assert event['attr'] == 'text'
        assert event['new'] == '<pre>%s</pre>' % v
