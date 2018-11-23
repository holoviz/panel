import os

import param
import numpy as np

from .holoviews import HoloViews
from .layout import Row, Column, Spacer
from .pane import Markdown, Pane
from .param import Param
from .util import param_reprs


class Pipeline(param.Parameterized):
    """
    Allows connecting a linear series of panels to define a workflow.
    Each stage in a pipeline should declare a panel method which
    returns a panel object that can be displayed and annotate its
    outputs using the param.output decorator.
    """

    debug = param.Boolean(default=False, precedence=-1, doc="""
        Whether to raise errors, useful for debugging while building an application.""")

    inherit_params = param.Boolean(default=True, precedence=-1, doc="""
        Whether parameters should be inherited between pipeline stages""")

    next = param.Action(default=lambda x: x.param.trigger('next'))

    previous = param.Action(default=lambda x: x.param.trigger('previous'))

    def __init__(self, stages=[], **params):
        try:
            import holoviews as hv
        except:
            raise ImportError('Pipeline requires holoviews to be installed')

        self._stages = list(stages)
        self._stage = 0
        super(Pipeline, self).__init__(**params)
        self._error = Markdown('')
        self._states = []
        self._state = None
        self._progress_sel = hv.streams.Selection1D()
        self._progress_sel.add_subscriber(self._set_stage)
        prev_button =  Param(self.param, parameters=['previous'], show_name=False)
        next_button =  Param(self.param, parameters=['next'], show_name=False)
        self._progress_bar = Row(self._make_progress, prev_button, next_button)
        spinner = Pane(os.path.join(os.path.dirname(__file__), 'assets', 'spinner.gif'))
        self._spinner_layout = Row(Spacer(width=300), Column(Spacer(height=200), spinner))
        stage_layout = Row()
        if len(stages):
            stage_layout.append(self._init_stage())
        self._layout = Column(self._progress_bar, self._error, stage_layout)

    def add_stage(self, name, stage):
        self._validate(stage)
        self._stages.append((name, stage))
        if len(self._stages) == 1:
            self._layout[2].append(self._init_stage())

    def _validate(self, stage):
        if any(stage is s for n, s in self._stages):
            raise ValueError('Stage %s is already in pipeline' % stage)
        elif not ((isinstance(stage, type) and issubclass(stage, param.Parameterized))
                  or isinstance(stage, param.Parameterized)):
            raise ValueError('Pipeline stages must be Parameterized classes or instances.')

    def __repr__(self):
        repr_str = 'Pipeline:'
        for i, (name, stage) in enumerate(self._stages):
            if isinstance(stage, param.Parameterized):
                cls_name = type(stage).__name__
            else:
                cls_name = stage.__name__
            params = ', '.join(param_reprs(stage))
            repr_str += '\n    [%d] %s: %s(%s)' % (i, name, cls_name, params)
        return repr_str

    def __getitem__(self, index):
        return self._stages[index][1]

    @property
    def layout(self):
        self._progress_bar[0] = self._make_progress
        return self._layout


    def _init_stage(self):
        name, stage = self._stages[self._stage]
        kwargs = {}
        if self._state:
            outputs = self._state.param.outputs().items()
            kwargs = {name: method() for name, (_, method) in outputs
                      if name in stage.params()}
            if self.inherit_params:
                params = [k for k, v in self._state.params().items()
                          if v.precedence is None or v.precedence >= 0]
                kwargs.update({k: v for k, v in self._state.param.get_param_values()
                               if k in stage.params() and k != 'name' and k in params})
        if isinstance(stage, param.Parameterized):
            stage.set_param(**kwargs)
            self._state = stage
        else:
            self._state = stage(**kwargs)
        if len(self._states) <= self._stage:
            self._states.append(self._state)
        else:
            self._states[self._stage] = self._state
        return self._state.panel()

    def _set_stage(self, index):
        idx = index[0]
        steps = idx-self._stage
        if steps < 0:
            for i in range(abs(steps)):
                self._previous()
        else:
            for i in range(steps):
                self._next()

    @param.depends('next', watch=True)
    def _next(self):
        self._stage += 1
        prev_state = self._layout[2][0]
        self._layout[2][0] = self._spinner_layout
        try:
            new_stage = self._init_stage()
            print("NEXT", new_stage)
            self._layout[2][0] = new_stage
        except Exception as e:
            print(e)
            self._stage -= 1
            self._error.object = str(e)
            self._layout[2][0] = prev_state
            if self.debug:
                raise e
        else:
            self._error.object = ''

    @param.depends('previous', watch=True)
    def _previous(self):
        self._stage -= 1
        try:
            self._state = self._states[self._stage]
            self._layout[2][0] = self._state.panel()
        except Exception as e:
            self._stage += 1
            self._error.object = str(e)
            if self.debug:
                raise e
        else:
            self._error.object = ''

    @param.depends('previous', 'next')
    def _make_progress(self):
        import holoviews as hv
        import holoviews.plotting.bokeh # noqa
        stages = len(self._stages)
        line = hv.Path([[(0, 0), (stages-1, 0)]]).options(
            line_width=10, color='black', backend='bokeh'
        )
        vals = np.arange(stages)
        active = [1 if v == self._stage else 0 for v in vals]
        points = hv.Points((vals, np.zeros(stages), active), vdims=['active']).options(
            color_index='active', line_color='black', cmap={0: 'white', 1: 'gray'},
            show_legend=False, size=20, default_tools=[], tools=['tap'],
            nonselection_alpha=1, backend='bokeh'
        )
        point_labels = points.add_dimension('text', 0, [n for n, _ in self._stages], vdim=True)
        labels = hv.Labels(point_labels).options(yoffset=-2.5, backend='bokeh')
        self._progress_sel.source = points
        hv_plot = (line * points * labels).options(
            xaxis=None, yaxis=None, width=800, show_frame=False, toolbar=None,
            height=80, xlim=(-0.5, stages-0.5), ylim=(-4, 1.5),
            clone=False, backend='bokeh'
        )
        return HoloViews(hv_plot, backend='bokeh')
