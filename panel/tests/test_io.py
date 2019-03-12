import json

from panel import Row
from panel.io import config, embed_state
from panel.pane import Str
from panel.widgets import Select, FloatSlider


def test_embed_discrete(document, comm):
    select = Select(options=['A', 'B', 'C'])
    string = Str()
    select.link(string, value='text')
    panel = Row(select, string)
    with config.set(embed=True):
        model = panel._get_root(document, comm)
    embed_state(panel, model, document)
    _, state = document.roots
    assert set(state.state) == {'A', 'B', 'C'}
    for k, v in state.state.items():
        events = json.loads(v['content'])['events']
        assert len(events) == 1
        event = events[0]
        assert event['kind'] == 'ModelChanged'
        assert event['attr'] == 'value'
        assert event['model'] == model.children[0].ref
        assert event['new'] == k


def test_embed_continuous(document, comm):
    select = FloatSlider(start=0, end=10)
    string = Str()
    select.link(string, value='text')
    panel = Row(select, string)
    with config.set(embed=True):
        model = panel._get_root(document, comm)
    embed_state(panel, model, document)
    _, state = document.roots
    assert set(state.state) == {0, 1, 2}
    for k, v in state.state.items():
        events = json.loads(v['content'])['events']
        assert len(events) == 1
        event = events[0]
        assert event['kind'] == 'ModelChanged'
        assert event['attr'] == 'value'
        assert event['model'] == model.children[0].children[1].ref
        assert event['new'] == k
