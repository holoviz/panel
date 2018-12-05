from distutils.version import LooseVersion

import pytest
import param

from panel.layout import Row, Column
from panel.param import Param, ParamMethod
from panel.pipeline import Pipeline

from .test_holoviews import hv_available

if LooseVersion(param.__version__) < '1.8.2':
    pytest.skip("skipping if param version < 1.8.2", allow_module_level=True)

class Stage1(param.Parameterized):
    
    a = param.Number(default=5, bounds=(0, 10))

    b = param.Number(default=5, bounds=(0, 10))
    
    @param.output(c=param.Number)
    def output(self):
        return self.a * self.b
    
    @param.depends('a', 'b')
    def view(self):
        return '%s * %s = %s' % (self.a, self.b, self.output())

    def panel(self):
        return Row(self.param, self.view)


class Stage2(param.Parameterized):
    
    c = param.Number(default=5, precedence=-1, bounds=(0, None))

    exp = param.Number(default=0.1, bounds=(0, 3))
    
    @param.depends('c', 'exp')
    def view(self):
        return '%s^%s=%.3f' % (self.c, self.exp, self.c**self.exp)

    def panel(self):
        return Row(self.param, self.view)

@hv_available
def test_pipeline_from_classes():
    import holoviews as hv
    
    pipeline = Pipeline([('Stage 1', Stage1), ('Stage 2', Stage2)])

    layout = pipeline.layout

    assert isinstance(layout, Column)
    assert isinstance(layout[0], Row)
    progress, prev_button, next_button = layout[0].objects

    assert isinstance(prev_button, Param)
    assert isinstance(next_button, Param)
    assert isinstance(progress, ParamMethod)

    hv_obj = progress.object().object
    points = hv_obj.get(1)
    assert isinstance(points, hv.Points)
    assert len(points) == 2
    labels = hv_obj.get(2)
    assert isinstance(labels, hv.Labels)
    assert list(labels['text']) == ['Stage 1', 'Stage 2']

    stage = layout[2][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'

    pipeline.param.trigger('next')
    stage = layout[2][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '25^0.1=1.380'

    pipeline.param.trigger('previous')
    stage = layout[2][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'


@hv_available
def test_pipeline_from_instances():
    import holoviews as hv

    pipeline = Pipeline([('Stage 1', Stage1()), ('Stage 2', Stage2())])

    layout = pipeline.layout

    assert isinstance(layout, Column)
    assert isinstance(layout[0], Row)
    progress, prev_button, next_button = layout[0].objects

    assert isinstance(prev_button, Param)
    assert isinstance(next_button, Param)
    assert isinstance(progress, ParamMethod)

    hv_obj = progress.object().object
    points = hv_obj.get(1)
    assert isinstance(points, hv.Points)
    assert len(points) == 2
    labels = hv_obj.get(2)
    assert isinstance(labels, hv.Labels)
    assert list(labels['text']) == ['Stage 1', 'Stage 2']

    stage = layout[2][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'

    pipeline.param.trigger('next')
    stage = layout[2][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '25^0.1=1.380'

    pipeline.param.trigger('previous')
    stage = layout[2][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'


@hv_available
def test_pipeline_from_add_stages():
    import holoviews as hv

    pipeline = Pipeline()
    pipeline.add_stage('Stage 1', Stage1)
    pipeline.add_stage('Stage 2', Stage2)

    layout = pipeline.layout

    assert isinstance(layout, Column)
    assert isinstance(layout[0], Row)
    progress, prev_button, next_button = layout[0].objects

    assert isinstance(prev_button, Param)
    assert isinstance(next_button, Param)
    assert isinstance(progress, ParamMethod)

    hv_obj = progress.object().object
    points = hv_obj.get(1)
    assert isinstance(points, hv.Points)
    assert len(points) == 2
    labels = hv_obj.get(2)
    assert isinstance(labels, hv.Labels)
    assert list(labels['text']) == ['Stage 1', 'Stage 2']

    stage = layout[2][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'

    pipeline.param.trigger('next')
    stage = layout[2][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '25^0.1=1.380'

    pipeline.param.trigger('previous')
    stage = layout[2][0]
    assert isinstance(stage, Row)
    assert isinstance(stage[1], ParamMethod)
    assert stage[1].object() == '5 * 5 = 25'


@hv_available
def test_pipeline_add_stage_validate_wrong_type():
    pipeline = Pipeline()
    with pytest.raises(ValueError):
        pipeline.add_stage('Stage 1', 1)


@hv_available
def test_pipeline_add_stage_validate_add_twice():
    pipeline = Pipeline()
    pipeline.add_stage('Stage 1', Stage1)
    with pytest.raises(ValueError):
        pipeline.add_stage('Stage 1', Stage1)


@hv_available
def test_pipeline_getitem():
    pipeline = Pipeline()
    pipeline.add_stage('Stage 1', Stage1)
    assert pipeline[0] == Stage1


@hv_available
def test_pipeline_repr():
    pipeline = Pipeline()
    pipeline.add_stage('Stage 1', Stage1)
    
    pipeline.add_stage('Stage 2', Stage2)
    assert repr(pipeline) == 'Pipeline:\n    [0] Stage 1: Stage1()\n    [1] Stage 2: Stage2()'
