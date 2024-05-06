import param
import pytest

hv = pytest.importorskip('holoviews')

from panel.layout import Column, Row
from panel.pane import HoloViews
from panel.param import ParamMethod
from panel.pipeline import Pipeline, find_route
from panel.widgets import Button, Select


class Stage1(param.Parameterized):

    a = param.Number(default=5, bounds=(0, 10))

    b = param.Number(default=5, bounds=(0, 10))

    ready = param.Boolean(default=False)

    next = param.String(default=None)

    @param.output(c=param.Number)
    def output(self):
        return self.a * self.b

    @param.depends('a', 'b')
    def view(self):
        return f'{self.a} * {self.b} = {self.output()}'

    def panel(self):
        return Row(self.param, self.view)


class Stage2(param.Parameterized):

    c = param.Number(default=5, precedence=-1, bounds=(0, None))

    exp = param.Number(default=0.1, bounds=(0, 3))

    @param.depends('c', 'exp')
    def view(self):
        return f'{self.c}^{self.exp}={self.c**self.exp:.3f}'

    def panel(self):
        return Row(self.param, self.view)


class Stage2b(param.Parameterized):

    c = param.Number(default=5, precedence=-1, bounds=(0, None))

    root = param.Parameter(default=0.1)

    @param.depends('c', 'root')
    def view(self):
        return f'{self.c}^-{self.root}={self.c**(-self.root):.3f}'

    def panel(self):
        return Row(self.param, self.view)


class DummyStage(param.Parameterized):

    def panel(self):
        return 'foo'


def test_find_route():
    graph = {'A': ('B', 'C'), 'C': ('D',), 'D': ('E', 'F', 'G'), 'F': ('H',), 'G': ('I',)}

    assert find_route(graph, 'A', 'I') == ['C', 'D', 'G', 'I']
    assert find_route(graph, 'B', 'I') is None
    assert find_route(graph, 'D', 'H') == ['F', 'H']


def test_pipeline_from_classes():
    pipeline = Pipeline([('Stage 1', Stage1), ('Stage 2', Stage2)])

    layout = pipeline.layout

    assert isinstance(layout, Column)
    assert isinstance(layout[0], Row)
    (title, error), progress, (prev_button, next_button) = layout[0].objects

    assert isinstance(error, Row)
    assert isinstance(prev_button, Button)
    assert isinstance(next_button, Button)
    assert isinstance(progress, HoloViews)

    hv_obj = progress.object
    graph = hv_obj.get(0)
    assert isinstance(graph, hv.Graph)
    assert len(graph) == 1
    labels = hv_obj.get(1)
    assert isinstance(labels, hv.Labels)
    assert list(labels['Stage']) == ['Stage 1', 'Stage 2']

    stage = layout[1][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'

    pipeline.param.trigger('next')
    stage = layout[1][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '25^0.1=1.380'

    pipeline.param.trigger('previous')
    stage = layout[1][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'


def test_pipeline_from_instances():
    pipeline = Pipeline([('Stage 1', Stage1()), ('Stage 2', Stage2())])

    layout = pipeline.layout

    assert isinstance(layout, Column)
    assert isinstance(layout[0], Row)
    (title, error), progress, (prev_button, next_button) = layout[0].objects

    assert isinstance(error, Row)
    assert isinstance(prev_button, Button)
    assert isinstance(next_button, Button)
    assert isinstance(progress, HoloViews)

    hv_obj = progress.object
    graph = hv_obj.get(0)
    assert isinstance(graph, hv.Graph)
    assert len(graph) == 1
    labels = hv_obj.get(1)
    assert isinstance(labels, hv.Labels)
    assert list(labels['Stage']) == ['Stage 1', 'Stage 2']

    stage = layout[1][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'

    pipeline.param.trigger('next')
    stage = layout[1][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '25^0.1=1.380'

    pipeline.param.trigger('previous')
    stage = layout[1][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'


def test_pipeline_from_add_stages():

    pipeline = Pipeline()
    pipeline.add_stage('Stage 1', Stage1)
    pipeline.add_stage('Stage 2', Stage2)

    layout = pipeline.layout

    assert isinstance(layout, Column)
    assert isinstance(layout[0], Row)
    (title, error), progress, (prev_button, next_button) = layout[0].objects

    assert isinstance(error, Row)
    assert isinstance(prev_button, Button)
    assert isinstance(next_button, Button)
    assert isinstance(progress, HoloViews)

    hv_obj = progress.object
    graph = hv_obj.get(0)
    assert isinstance(graph, hv.Graph)
    assert len(graph) == 1
    labels = hv_obj.get(1)
    assert isinstance(labels, hv.Labels)
    assert list(labels['Stage']) == ['Stage 1', 'Stage 2']

    stage = layout[1][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'

    pipeline.param.trigger('next')
    stage = layout[1][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '25^0.1=1.380'

    pipeline.param.trigger('previous')
    stage = layout[1][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'


def test_pipeline_define_graph_missing_node():
    pipeline = Pipeline()
    pipeline.add_stage('Stage 1', Stage1)
    pipeline.add_stage('Stage 2', Stage2)

    with pytest.raises(ValueError):
        pipeline.define_graph({'Stage 1': ('Stage 2', 'Stage 2b')})


def test_pipeline_define_graph():
    pipeline = Pipeline()
    pipeline.add_stage('Stage 2', Stage2)
    pipeline.add_stage('Stage 2b', Stage2b)
    pipeline.add_stage('Stage 1', Stage1)

    pipeline.define_graph({'Stage 1': ('Stage 2', 'Stage 2b')})

    assert pipeline._stage == 'Stage 1'

    assert isinstance(pipeline.buttons, Row)
    (pselect, pbutton), (nselect, nbutton) = pipeline.buttons
    assert isinstance(pselect, Select)
    assert pselect.disabled
    assert isinstance(pbutton, Button)
    assert pbutton.disabled

    assert isinstance(nselect, Select)
    assert not nselect.disabled
    assert nselect.options == ['Stage 2', 'Stage 2b']
    assert nselect.value == 'Stage 2'
    assert isinstance(nbutton, Button)
    assert not nbutton.disabled

    pipeline._next()

    assert isinstance(pipeline._state, Stage2)

    pipeline._previous()

    nselect.value = 'Stage 2b'

    pipeline._next()

    assert isinstance(pipeline._state, Stage2b)


def test_pipeline_set_stage():
    pipeline = Pipeline()
    pipeline.add_stage('Stage 2', Stage2)
    pipeline.add_stage('Stage 2b', Stage2b)
    pipeline.add_stage('Stage 1', Stage1)
    pipeline.add_stage('Final', DummyStage())

    pipeline.define_graph({'Stage 1': ('Stage 2', 'Stage 2b'), 'Stage 2b': 'Final'})

    pipeline._set_stage([2])

    assert pipeline._stage == 'Stage 2'

    pipeline._set_stage([0])

    assert pipeline._stage == 'Stage 1'

    pipeline._set_stage([3])

    assert pipeline._stage == 'Final'


def test_pipeline_define_next_parameter_respected():
    pipeline = Pipeline()
    pipeline.add_stage('Stage 2', Stage2)
    pipeline.add_stage('Stage 2b', Stage2b)
    pipeline.add_stage('Stage 1', Stage1(next='Stage 2b'), next_parameter='next')

    pipeline.define_graph({'Stage 1': ('Stage 2', 'Stage 2b')})

    assert pipeline.next_selector.value == 'Stage 2b'

    pipeline._state.next = 'Stage 2'

    assert pipeline.next_selector.value == 'Stage 2'


def test_pipeline_error_condition():
    pipeline = Pipeline()
    stage2b = Stage2b(root='error')
    pipeline.add_stage('Stage 2', Stage2)
    pipeline.add_stage('Stage 2b', stage2b)
    pipeline.add_stage('Stage 1', Stage1)

    pipeline.define_graph({'Stage 1': ('Stage 2', 'Stage 2b')})

    pipeline.next_selector.value = 'Stage 2b'
    pipeline._next()

    assert isinstance(pipeline.error[0], Button)

    stage2b.root = 2

    pipeline._next()

    assert len(pipeline.error) == 0


def test_pipeline_previous_follows_initial_path():
    pipeline = Pipeline()
    pipeline.add_stage('Stage 1', Stage1)
    pipeline.add_stage('Stage 2', Stage2)
    pipeline.add_stage('Stage 2b', Stage2b)
    pipeline.add_stage('Stage 3', DummyStage)

    pipeline.define_graph({
        'Stage 1': ('Stage 2', 'Stage 2b'),
        'Stage 2': 'Stage 3',
        'Stage 2b': 'Stage 3'
    })

    assert pipeline._route == ['Stage 1']

    pipeline.next_selector.value = 'Stage 2b'
    pipeline._next()

    assert pipeline._route == ['Stage 1', 'Stage 2b']

    pipeline._next()

    assert pipeline._route == ['Stage 1', 'Stage 2b', 'Stage 3']

    pipeline._previous()

    assert pipeline._stage == 'Stage 2b'
    assert pipeline._route == ['Stage 1', 'Stage 2b']


def test_pipeline_ready_respected():
    pipeline = Pipeline(ready_parameter='ready')
    pipeline.add_stage('Stage 1', Stage1)
    pipeline.add_stage('Stage 2', Stage2)

    assert pipeline.next_button.disabled

    pipeline._state.ready = True

    assert not pipeline.next_button.disabled


def test_pipeline_auto_advance_respected():
    pipeline = Pipeline(ready_parameter='ready', auto_advance=True)
    pipeline.add_stage('Stage 1', Stage1)
    pipeline.add_stage('Stage 2', Stage2)

    assert pipeline.next_button.disabled

    pipeline._state.ready = True

    assert isinstance(pipeline._state, Stage2)


def test_pipeline_network_diagram_states():
    pipeline = Pipeline(ready_parameter='ready', auto_advance=True)
    pipeline.add_stage('Stage 1', Stage1)
    pipeline.add_stage('Stage 2', Stage2)
    pipeline.add_stage('Stage 2b', Stage2b)

    pipeline.define_graph({'Stage 1': ('Stage 2', 'Stage 2b')})

    [s1, s2, s2b] = pipeline.network.object.get(0).nodes['State']

    assert s1 == 'active'
    assert s2 == 'inactive'
    assert s2b == 'next'

    pipeline._next()

    [s1, s2, s2b] = pipeline.network.object.get(0).nodes['State']

    assert s1 == 'inactive'
    assert s2 == 'inactive'
    assert s2b == 'active'

    pipeline._previous()

    [s1, s2, s2b] = pipeline.network.object.get(0).nodes['State']

    assert s1 == 'active'
    assert s2 == 'inactive'
    assert s2b == 'next'


def test_pipeline_add_stage_validate_wrong_type():
    pipeline = Pipeline()
    with pytest.raises(ValueError):
        pipeline.add_stage('Stage 1', 1)


def test_pipeline_add_stage_validate_add_twice():
    pipeline = Pipeline()
    pipeline.add_stage('Stage 1', Stage1)
    with pytest.raises(ValueError):
        pipeline.add_stage('Stage 1', Stage1)


def test_pipeline_getitem():
    pipeline = Pipeline()
    pipeline.add_stage('Stage 1', Stage1)
    assert pipeline['Stage 1'] == Stage1


def test_pipeline_repr():
    pipeline = Pipeline()
    pipeline.add_stage('Stage 1', Stage1)

    pipeline.add_stage('Stage 2', Stage2)
    assert repr(pipeline) == 'Pipeline:\n    [0] Stage 1: Stage1()\n    [1] Stage 2: Stage2()'
