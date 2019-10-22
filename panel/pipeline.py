from __future__ import absolute_import, division, unicode_literals

import os
import sys
import traceback as tb

from collections import OrderedDict, defaultdict

import param
import numpy as np

from .layout import Row, Column, HSpacer, VSpacer, Spacer
from .pane import HoloViews, Pane
from .widgets import Button, Select
from .param import Param
from .util import param_reprs


class PipelineError(RuntimeError):
    """
    Custom error type which can be raised to display custom error
    message in a Pipeline.
    """


def traverse(graph, v, visited):
    """
    Traverse the graph from a node and mark visited vertices.
    """
    visited[v] = True
    # Recur for all the vertices adjacent to this vertex
    for i in graph.get(v, []):
        if visited[i] == False:
            traverse(graph, i, visited)


def get_root(graph):
    """
    Search for the root not by finding nodes without inputs.
    """
    # Find root node
    roots = []
    targets = [t for ts in graph.values() for t in ts]
    for src in graph:
        if src not in targets:
            roots.append(src)

    if len(roots) > 1:
        raise ValueError("Graph has more than one node with no "
                         "incoming edges. Ensure that the graph "
                         "only has a single source node.")
    elif len(roots) == 0:
        raise ValueError("Graph has no source node. Ensure that the "
                         "graph is not cyclic and has a single "
                         "starting point.")
    return roots[0]


def is_traversable(root, graph, stages):
    """
    Check if the graph is fully traversable from the root node.
    """
    # Ensure graph is traverable from root
    int_graph = {stages.index(s): tuple(stages.index(t) for t in tgts)
                 for s, tgts in graph.items()}
    visited = [False]*len(stages)
    traverse(int_graph, stages.index(root), visited)
    return all(visited)


def get_depth(node, graph, depth=0):
    depths = []
    for sub in graph.get(node, []):
        depths.append(get_depth(sub, graph, depth+1))
    return max(depths) if depths else depth+1


def get_breadths(node, graph, depth=0, breadths=None):
    if breadths is None:
        breadths = defaultdict(list)
        breadths[depth].append(node)
    for sub in graph.get(node, []):
        if sub not in breadths[depth+1]:
            breadths[depth+1].append(sub)
        get_breadths(sub, graph, depth+1, breadths)
    return breadths



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

    def __init__(self, stages=[], graph={}, **params):
        try:
            import holoviews as hv
        except:
            raise ImportError('Pipeline requires holoviews to be installed')

        self._stage = None
        self._stages = OrderedDict()
        super(Pipeline, self).__init__(**params)
        self._states = {}
        self._state = None
        self._linear = True
        self._block = False
        self._graph = {}
        self._progress_sel = hv.streams.Selection1D()
        self._progress_sel.add_subscriber(self._set_stage)
        self._prev_button = Param(self.param.previous).layout[0]
        self._prev_button.width = 125
        self._prev_selector = Select(width=125)
        self._next_button = Param(self.param.next).layout[0]
        self._next_button.width = 125
        self._next_selector = Select(width=125)
        self._prev_button.disabled = True
        self._progress_bar = Row(
            Spacer(width=100),
            self._make_progress(),
            self._prev_button,
            self._next_button,
            sizing_mode='stretch_width'
        )
        spinner = Pane(os.path.join(os.path.dirname(__file__), 'assets', 'spinner.gif'))
        self._spinner_layout = Row(
            HSpacer(),
            Column(VSpacer(), spinner, VSpacer()),
            HSpacer()
        )
        self._layout = Column(self._progress_bar, Row(), sizing_mode='stretch_width')
        for stage in stages:
            kwargs = {}
            if len(stage) == 2:
                name, stage = stage
            elif len(stage) == 3:
                name, stage, kwargs = stage
            self.add_stage(name, stage, **kwargs)
        self.define_graph(graph)

    def _validate(self, stage):
        if any(stage is s for n, (s, kw) in self._stages.items()):
            raise ValueError('Stage %s is already in pipeline' % stage)
        elif not ((isinstance(stage, type) and issubclass(stage, param.Parameterized))
                  or isinstance(stage, param.Parameterized)):
            raise ValueError('Pipeline stages must be Parameterized classes or instances.')

    def __repr__(self):
        repr_str = 'Pipeline:'
        for i, (name, (stage, _)) in enumerate(self._stages.items()):
            if isinstance(stage, param.Parameterized):
                cls_name = type(stage).__name__
            else:
                cls_name = stage.__name__
            params = ', '.join(param_reprs(stage))
            repr_str += '\n    [%d] %s: %s(%s)' % (i, name, cls_name, params)
        return repr_str

    def __getitem__(self, index):
        return self._stages[index][1]

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
        stage, stage_kwargs = self._stages[self._stage]

        previous = []
        for src, tgts in self._graph.items():
            if self._stage in tgts:
                previous.append(src)
        prev_states = [self._states[prev] for prev in previous if prev in self._states]

        kwargs, results = {}, {}
        for state in prev_states:
            for name, (_, method, index) in state.param.outputs().items():
                if name not in stage.param:
                    continue
                if method not in results:
                    results[method] = method()
                result = results[method]
                if index is not None:
                    result = result[index]
                kwargs[name] = result
            if stage_kwargs.get('inherit_params', self.inherit_params):
                params = [k for k, v in state.param.objects('existing').items()
                              if v.precedence is None or v.precedence >= 0]
                kwargs.update({k: v for k, v in state.param.get_param_values()
                               if k in stage.param and k != 'name' and k in params})

        ready_param = stage_kwargs.get('ready_parameter', self.ready_parameter)
        if ready_param and ready_param in stage.param:
            stage.param.watch(self._unblock, ready_param, onlychanged=False)

        if isinstance(stage, param.Parameterized):
            stage.set_param(**kwargs)
            self._state = stage
        else:
            self._state = stage(**kwargs)

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

    @property
    def _next_stage(self):
        return self._next_selector.value

    @property
    def _prev_stage(self):
        return self._prev_selector.value

    def _update_button(self):
        options = list(self._graph.get(self._stage, []))
        self._next_selector.options = options
        self._next_selector.value = options[0] if options else None
        self._next_selector.disabled = not bool(options)
        previous = []
        for src, tgts in self._graph.items():
            if self._stage in tgts:
                previous.append(src)
        self._prev_selector.options = previous
        self._prev_selector.value = previous[0] if previous else None
        self._prev_selector.disabled = not bool(previous)

        # Disable previous button
        if self._prev_stage is None:
            self._prev_button.disabled = True
        else:
            self._prev_button.disabled = False

        # Disable next button
        if self._next_stage is None:
            self._next_button.disabled = True
        else:
            stage, kwargs = self._stages[self._stage]
            ready = kwargs.get('ready_parameter', self.ready_parameter)
            disabled = (not getattr(stage, ready)) if ready in stage.param else False
            self._next_button.disabled = disabled

    def _get_error_button(self, e):
        msg = str(e) if isinstance(e, PipelineError) else ""
        if self.debug:
            type, value, trb = sys.exc_info()
            tb_list = tb.format_tb(trb, None) + tb.format_exception_only(type, value)
            traceback = (("%s\n\nTraceback (innermost last):\n" + "%-20s %s") %
                         (msg, ''.join(tb_list[-5:-1]), tb_list[-1]))
        else:
            traceback = msg or "Undefined error, enable debug mode."
        button = Button(name='Error', button_type='danger', width=100,
                        align='center')
        button.jslink(button, code={'clicks': "alert(`{tb}`)".format(tb=traceback)})
        return button

    @param.depends('next', watch=True)
    def _next(self):
        self._stage = self._next_stage
        prev_state = self._state
        self._layout[1][0] = self._spinner_layout
        try:
            self._layout[1][0] = self._init_stage()
        except Exception as e:
            self._stage = self._prev_stage
            self._state = prev_state
            self._layout[1][0] = prev_state.panel()
            self._progress_bar[0] = self._get_error_button(e)
            if self.debug:
                raise e
            return e
        else:
            self._progress_bar[0] = Spacer(width=100)
            self._update_button()
        finally:
            self._progress_bar[1] = self._make_progress()

    @param.depends('previous', watch=True)
    def _previous(self):
        self._stage = self._prev_stage
        prev_state = self._state
        try:
            if self._stage in self._states:
                self._state = self._states[self._stage]
                self._layout[1][0] = self._state.panel()
            else:
                self._layout[1][0] = self._init_stage()
            self._block = True
        except Exception as e:
            self._stage = self._next_stage
            self._state = prev_state
            self._progress_bar[0] = self._get_error_button(e)
            if self.debug:
                raise e
        else:
            self._progress_bar[0] = Spacer(width=100)
            self._update_button()
        finally:
            self._progress_bar[1] = self._make_progress()

    def _make_progress(self):
        import holoviews as hv
        import holoviews.plotting.bokeh # noqa

        if self._graph:
            root = get_root(self._graph)
            depth = get_depth(root, self._graph)
            breadths = get_breadths('A', self._graph)
            max_breadth = max(len(v) for v in breadths.values())
        else:
            root = None
            max_breadth, depth = 0, 0
            breadths = {}

        height = 80 + (max_breadth-1) * 20

        edges = []
        for src, tgts in self._graph.items():
            for t in tgts:
                edges.append((src, t))

        nodes = []
        for depth, subnodes in breadths.items():
            breadth = len(subnodes)
            step = 1./breadth
            for i, n in enumerate(subnodes):
                nodes.append((depth, step/2.+i*step, n, n==self._stage))

        nodes = hv.Nodes(nodes, ['x', 'y', 'Stage'], 'Active')
        graph = hv.Graph((edges, nodes)).opts(
            node_color='Active', cmap={'False': 'white', 'True': '#5cb85c'},
            tools=[], default_tools=['hover'], selection_policy=None,
            edge_hover_line_color='black', node_hover_fill_color='gray',
            backend='bokeh')
        labels = hv.Labels(nodes, ['x', 'y'], 'Stage').opts(
            yoffset=-.2, backend='bokeh')
        plot = (graph * labels) if self._linear else graph
        plot.opts(
            xaxis=None, yaxis=None, min_width=600, responsive=True,
            show_frame=False, height=height, xlim=(-0.25, depth+0.25), ylim=(0, 1),
            default_tools=['hover'], toolbar=None,
            backend='bokeh'
        )
        return HoloViews(plot, backend='bokeh')

    #----------------------------------------------------------------
    # Public API
    #----------------------------------------------------------------

    def add_stage(self, name, stage, **kwargs):
        """
        Adds a new, named stage to the Pipeline.

        Arguments
        ---------
        name: str
          A string name for the Pipeline stage
        stage: param.Parameterized
          A Parameterized object which represents the Pipeline stage.
        **kwargs: dict
          Additional arguments declaring the behavior of the stage.
        """
        self._validate(stage)
        self._stages[name] = (stage, kwargs)

    def define_graph(self, graph, force=False):
        """
        Declares a custom graph structure for the Pipeline overriding
        the default linear flow. The graph should be defined as an
        adjacency mapping.

        Arguments
        ---------
        graph: dict
          Dictionary declaring the relationship between different
          pipeline stages. Should map from a single stage name to
          one or more stage names.
        """
        stages = list(self._stages)
        if not stages:
            self._graph = {}
            return

        not_found = []
        for source, targets in graph.items():
            if source not in stages:
                not_found.append(source)
            not_found += [t for t in targets if t not in stages]
        if not_found:
            raise ValueError(
                'Pipeline stage(s) %s not found, ensure all stages '
                'referenced in the graph have been added.' %
                (not_found[0] if len(not_found) == 1 else not_found)
            )

        if graph:
            if not (self._linear or force):
                raise ValueError("Graph has already been defined, "
                                 "cannot override existing graph.")
            graph = {k: v if isinstance(v, tuple) else (v,)
                     for k, v in graph.items()}
            self._linear = False
        else:
            graph = {s: (t,) for s, t in zip(stages[:-1], stages[1:])}

        root = get_root(graph)
        if not is_traversable(root, graph, stages):
            raise ValueError('Graph is not fully traversable from stage: %s.'
                             % root)

        self._stage = root
        self._graph = graph
        if not self._linear:
            self._progress_bar[2] = Column(self._prev_selector, self._prev_button)
            self._progress_bar[3] = Column(self._next_selector, self._next_button)

    @property
    def layout(self):
        if self._linear or not self._graph:
            self.define_graph(self._graph)
        self._layout[1][:] = [self._init_stage()]
        self._update_button()
        self._progress_bar[1] = self._make_progress()
        return self._layout
