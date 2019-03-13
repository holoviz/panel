import json

from panel import Row
from panel.io import config, embed_state
from panel.pane import Str
from panel.widgets import Select, FloatSlider, Checkbox


def test_embed_discrete(document, comm):
    select = Select(options=['A', 'B', 'C'])
    string = Str()
    select.link(string, value='object')
    panel = Row(select, string)
    with config.set(embed=True):
        model = panel._get_root(document, comm)
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
        model = panel._get_root(document, comm)
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
    checkbox = Checkbox(start=0, end=10)
    string = Str()
    checkbox.link(string, value='object')
    panel = Row(checkbox, string)
    with config.set(embed=True):
        model = panel._get_root(document, comm)
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
