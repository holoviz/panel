from __future__ import absolute_import, division, unicode_literals

import os
import sys
import traceback as tb

import param
import numpy as np

from .layout import Row, Column, HSpacer, VSpacer, Spacer
from .pane import HoloViews, HTML, Pane
from .widgets import Button
from .param import Param
from .util import param_reprs


class PipelineError(RuntimeError):
    """
    Custom error type which can be raised to display custom error
    message in a Pipeline.
    """


class Pipeline(param.Parameterized):
    """
    Allows connecting a linear series of panels to define a workflow.
    Each stage in a pipeline should declare a panel method which
    returns a panel object that can be displayed and annotate its
    outputs using the param.output decorator.
    """

    auto_advance = param.Boolean(default=False, precedence=-1, doc="""
        Whether to automatically advance if the ready parameter is True.""")

    debug = param.Boolean(default=False, precedence=-1, doc="""
        Whether to raise errors, useful for debugging while building an application.""")

    inherit_params = param.Boolean(default=True, precedence=-1, doc="""
        Whether parameters should be inherited between pipeline stages""")

    ready_parameter = param.String(default=None, doc="""
        Parameter name to watch to check whether a stage is ready.""")

    next = param.Action(default=lambda x: x.param.trigger('next'))

    previous = param.Action(default=lambda x: x.param.trigger('previous'))

    def __init__(self, stages=[], **params):
        try:
            import holoviews as hv
        except:
            raise ImportError('Pipeline requires holoviews to be installed')

        self._stages = []
        for stage in stages:
            kwargs = {}
            if len(stage) == 2:
                name, stage = stage
            elif len(stage) == 3:
                name, stage, kwargs = stage
            self.add_stage(name, stage, **kwargs)
        self._stage = 0
        super(Pipeline, self).__init__(**params)
        self._states = []
        self._state = None
        self._block = False
        self._progress_sel = hv.streams.Selection1D()
        self._progress_sel.add_subscriber(self._set_stage)
        prev_button =  Param(self.param.previous, width=100)
        next_button =  Param(self.param.next, width=100)
        prev_button.layout[0].disabled = True
        self._progress_bar = Row(Spacer(width=100), self._make_progress(), prev_button, next_button)
        spinner = Pane(os.path.join(os.path.dirname(__file__), 'assets', 'spinner.gif'))
        self._spinner_layout = Row(HSpacer(), Column(VSpacer(), spinner, VSpacer()), HSpacer())
        stage_layout = Row()
        if len(stages):
            stage = self._init_stage()
            stage_layout.append(stage)
            self._update_button(stage)
        self._layout = Column(self._progress_bar, stage_layout)

    def add_stage(self, name, stage, **kwargs):
        self._validate(stage)
        self._stages.append((name, stage, kwargs))
        if len(self._stages) == 1:
            stage = self._init_stage()
            self._layout[1].append(stage)
            self._update_button(stage)

    def _validate(self, stage):
        if any(stage is s for n, s, kw in self._stages):
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
        self._progress_bar[1] = self._make_progress
        return self._layout

    def _unblock(self, event):
        if self._state is not event.obj or self._block:
            self._block = False
            return

        button = self._progress_bar[-1][0]
        if button.disabled and event.new:
            button.disabled = False
        elif not button.disabled and not event.new:
            button.disabled = True

        stage_kwargs = self._stages[self._stage][-1]
        if event.new and stage_kwargs.get('auto_advance', self.auto_advance):
            self._next()

    def _init_stage(self):
        _, stage, stage_kwargs = self._stages[self._stage]
        kwargs = {}
        if self._state is not None:
            results = {}
            for name, (_, method, index) in self._state.param.outputs().items():
                print(name, method)
                if name not in stage.param:
                    continue
                if method not in results:
                    results[method] = method()
                result = results[method]
                if index is not None:
                    result = result[index]
                kwargs[name] = result
            if stage_kwargs.get('inherit_params', self.inherit_params):
                params = [k for k, v in self._state.param.objects('existing').items()
                          if v.precedence is None or v.precedence >= 0]
                kwargs.update({k: v for k, v in self._state.param.get_param_values()
                               if k in stage.param and k != 'name' and k in params})

        ready_param = stage_kwargs.get('ready_parameter', self.ready_parameter)
        if ready_param and ready_param in stage.param:
            stage.param.watch(self._unblock, ready_param, onlychanged=False)

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
                self.param.trigger('previous')
                if self._error.object:
                    break
        else:
            for i in range(steps):
                self.param.trigger('next')
                if self._error.object:
                    break

    def _update_button(self, stage):
        # Disable previous button
        if self._stage == 0:
            self._progress_bar[2].layout[0].disabled = True
        else:
            self._progress_bar[2].layout[0].disabled = False

        # Disable next button
        if self._stage == len(self._stages)-1:
            self._progress_bar[3].layout[0].disabled = True
        else:
            kwargs = self._stages[self._stage][2]
            ready = kwargs.get('ready_parameter', self.ready_parameter)
            disabled = (not getattr(stage, ready)) if ready in stage.param else False
            self._progress_bar[3].layout[0].disabled = disabled

    def _get_error_button(cls, e):
        msg = str(e) if isinstance(e, PipelineError) else ""
        type, value, trb = sys.exc_info()
        tb_list = tb.format_tb(trb, None) + tb.format_exception_only(type, value)
        traceback = (("%s\n\nTraceback (innermost last):\n" + "%-20s %s") %
                     (msg, ''.join(tb_list[-5:-1]), tb_list[-1]))
        button = Button(name='Error', button_type='danger', width=100,
                        align='center')
        button.jslink(button, code={'clicks': "alert(`{tb}`)".format(tb=traceback)})
        return button

    @param.depends('next', watch=True)
    def _next(self):
        self._stage += 1
        prev_state = self._state
        self._layout[1][0] = self._spinner_layout
        try:
            new_stage = self._init_stage()
            self._state = self._states[self._stage]
            self._layout[1][0] = new_stage
            self._update_button(new_stage)
        except Exception as e:
            self._stage -= 1
            self._state = prev_state
            self._layout[1][0] = prev_state
            self._progress_bar[0] = self._get_error_button(e)
            if self.debug:
                raise e
            return e
        else:
            self._progress_bar[0] = Spacer(width=100)
        finally:
            self._progress_bar[1] = self._make_progress()


    @param.depends('previous', watch=True)
    def _previous(self):
        self._stage -= 1
        prev_state = self._state
        try:
            self._state = self._states[self._stage]
            self._block = True
            self._layout[1][0] = self._state.panel()
            self._update_button(self._state)
        except Exception as e:
            self._stage += 1
            self._state = prev_state
            self._progress_bar[0] = self._get_error_button(e)
            if self.debug:
                raise e
        else:
            self._progress_bar[0] = Spacer(width=100)
        finally:
            self._progress_bar[1] = self._make_progress()

    def _make_progress(self):
        import holoviews as hv
        import holoviews.plotting.bokeh # noqa
        stages = len(self._stages)
        line = hv.Path([[(0, 0), (stages-1, 0)]]).options(
            line_width=6, color='black', backend='bokeh'
        )
        vals = np.arange(stages)
        active = [1 if v == self._stage else 0 for v in vals]
        points = hv.Points((vals, np.zeros(stages), active), vdims=['active']).options(
            color_index='active', line_color='black', cmap={0: 'white', 1: '#5cb85c'},
            show_legend=False, size=20, default_tools=[], tools=['tap'],
            nonselection_alpha=1, backend='bokeh'
        )
        point_labels = points.add_dimension('text', 0, [s[0] for s in self._stages], vdim=True)
        labels = hv.Labels(point_labels).options(yoffset=-2.5, backend='bokeh')
        self._progress_sel.source = points
        hv_plot = (line * points * labels).options(
            xaxis=None, yaxis=None, width=800, show_frame=False, toolbar=None,
            height=80, xlim=(-0.5, stages-0.5), ylim=(-4, 1.5),
            clone=False, backend='bokeh'
        )
        return HoloViews(hv_plot, backend='bokeh')
