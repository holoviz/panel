from __future__ import annotations

import sys
import traceback as tb

from collections import OrderedDict, defaultdict
from typing import ClassVar, Tuple

import param

from .layout import Column, Row
from .pane import HoloViews, Markdown
from .param import Param
from .util import param_reprs
from .viewable import Viewer
from .widgets import Button, Select


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


def find_route(graph, current, target):
    """
    Find a route to the target node from the current node.
    """
    next_nodes = graph.get(current)
    if next_nodes is None:
        return None
    elif target in next_nodes:
        return [target]
    else:
        for n in next_nodes:
            route = find_route(graph, n, target)
            if route is None:
                continue
            return [n]+route
        return None


def get_root(graph):
    """
    Search for the root node by finding nodes without inputs.
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



class Pipeline(Viewer):
    """
    A Pipeline represents a directed graph of stages, which each
    return a panel object to render. A pipeline therefore represents
    a UI workflow of multiple linear or branching stages.

    The Pipeline layout consists of a number of sub-components:

    * header:

      * title: The name of the current stage.
      * error: A field to display the error state.
      * network: A network diagram representing the pipeline.
      * buttons: All navigation buttons and selectors.
      * prev_button: The button to go to the previous stage.
      * prev_selector: The selector widget to select between
        previous branching stages.
      * next_button: The button to go to the previous stage
      * next_selector: The selector widget to select the next
        branching stages.

    * stage: The contents of the current pipeline stage.

    By default any outputs of one stage annotated with the
    param.output decorator are fed into the next stage. Additionally,
    if the inherit_params parameter is set any parameters which are
    declared on both the previous and next stage are also inherited.

    The stages are declared using the add_stage method and must each
    be given a unique name. By default any stages will simply be
    connected linearly, but an explicit graph can be declared using
    the define_graph method.
    """

    auto_advance = param.Boolean(default=False, doc="""
        Whether to automatically advance if the ready parameter is True.""")

    debug = param.Boolean(default=False, doc="""
        Whether to raise errors, useful for debugging while building
        an application.""")

    inherit_params = param.Boolean(default=True, doc="""
        Whether parameters should be inherited between pipeline
        stages.""")

    next_parameter = param.String(default=None, doc="""
        Parameter name to watch to switch between different branching
        stages""")

    ready_parameter = param.String(default=None, doc="""
        Parameter name to watch to check whether a stage is ready.""")

    show_header = param.Boolean(default=True, doc="""
        Whether to show the header with the title, network diagram,
        and buttons.""")

    next = param.Action(default=lambda x: x.param.trigger('next'))

    previous = param.Action(default=lambda x: x.param.trigger('previous'))

    _ignored_refs: ClassVar[Tuple[str]] = ('next_parameter', 'ready_parameter')

    def __init__(self, stages=[], graph={}, **params):
        try:
            import holoviews as hv
        except Exception:
            raise ImportError('Pipeline requires holoviews to be installed')

        super().__init__(**params)

        # Initialize internal state
        self._stage = None
        self._stages = OrderedDict()
        self._states = {}
        self._state = None
        self._linear = True
        self._block = False
        self._error = None
        self._graph = {}
        self._route = []

        # Declare UI components
        self._progress_sel = hv.streams.Selection1D()
        self._progress_sel.add_subscriber(self._set_stage)
        self.prev_button = Param(self.param.previous).layout[0]
        self.prev_button.width = 125
        self.prev_selector = Select(width=125)
        self.next_button = Param(self.param.next).layout[0]
        self.next_button.width = 125
        self.next_selector = Select(width=125)
        self.prev_button.disabled = True
        self.next_selector.param.watch(self._update_progress, 'value')
        self.network = HoloViews(backend='bokeh')
        self.title = Markdown('# Header', margin=(0, 0, 0, 5))
        self.error = Row(width=100)
        self.buttons = Row(self.prev_button, self.next_button)
        self.header = Row(
            Column(self.title, self.error),
            self.network,
            self.buttons,
            sizing_mode='stretch_width'
        )
        self.network.object = self._make_progress()
        self.stage = Row()
        self.layout = Column(self.header, self.stage, sizing_mode='stretch_width')

        # Initialize stages and the graph
        for stage in stages:
            kwargs = {}
            if len(stage) == 2:
                name, stage = stage
            elif len(stage) == 3:
                name, stage, kwargs = stage
            self.add_stage(name, stage, **kwargs)
        self.define_graph(graph)

    def __panel__(self):
        return self.layout

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

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, index):
        return self._stages[index][0]

    def _unblock(self, event):
        if self._state is not event.obj or self._block:
            self._block = False
            return

        button = self.next_button
        if button.disabled and event.new:
            button.disabled = False
        elif not button.disabled and not event.new:
            button.disabled = True

        stage_kwargs = self._stages[self._stage][-1]
        if event.new and stage_kwargs.get('auto_advance', self.auto_advance):
            self._next()

    def _select_next(self, event):
        if self._state is not event.obj:
            return
        self.next_selector.value = event.new
        self._update_progress()

    def _init_stage(self):
        stage, stage_kwargs = self._stages[self._stage]

        previous = []
        for src, tgts in self._graph.items():
            if self._stage in tgts:
                previous.append(src)
        prev_states = [self._states[prev] for prev in previous if prev in self._states]

        outputs = []
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
                outputs.append(name)
            if stage_kwargs.get('inherit_params', self.inherit_params):
                ignored = [stage_kwargs.get(p) or getattr(self, p, None)
                           for p in ('ready_parameter', 'next_parameter')]
                params = [k for k, v in state.param.objects('existing').items()
                          if k not in ignored]
                kwargs.update({k: v for k, v in state.param.values().items()
                               if k in stage.param and k != 'name' and k in params})

        if isinstance(stage, param.Parameterized):
            stage.param.update(**kwargs)
            self._state = stage
        else:
            self._state = stage(**kwargs)

        # Hide widgets for parameters that are supplied by the previous stage
        for output in outputs:
            self._state.param[output].precedence = -1

        ready_param = stage_kwargs.get('ready_parameter', self.ready_parameter)
        if ready_param and ready_param in stage.param:
            self._state.param.watch(self._unblock, ready_param, onlychanged=False)

        next_param = stage_kwargs.get('next_parameter', self.next_parameter)
        if next_param and next_param in stage.param:
            self._state.param.watch(self._select_next, next_param, onlychanged=False)

        self._states[self._stage] = self._state
        return self._state.panel()

    def _set_stage(self, index):
        if not index:
            return
        stage = self._progress_sel.source.iloc[index[0], 2]
        if stage in self.next_selector.options:
            self.next_selector.value = stage
            self.param.trigger('next')
        elif stage in self.prev_selector.options:
            self.prev_selector.value = stage
            self.param.trigger('previous')
        elif stage in self._route:
            while len(self._route) > 1:
                self.param.trigger('previous')
        else:
            # Try currently selected route
            route = find_route(self._graph, self._next_stage, stage)
            if route is None:
                # Try alternate route
                route = find_route(self._graph, self._stage, stage)
                if route is None:
                    raise ValueError('Could not find route to target node.')
            else:
                route = [self._next_stage] + route
            for r in route:
                if r not in self.next_selector.options:
                    break
                self.next_selector.value = r
                self.param.trigger('next')


    @property
    def _next_stage(self):
        return self.next_selector.value

    @property
    def _prev_stage(self):
        return self.prev_selector.value

    def _update_button(self):
        stage, kwargs = self._stages[self._stage]
        options = list(self._graph.get(self._stage, []))
        next_param = kwargs.get('next_parameter', self.next_parameter)
        option = getattr(self._state, next_param) if next_param and next_param in stage.param else None
        if option is None:
            option = options[0] if options else None
        self.next_selector.options = options
        self.next_selector.value = option
        self.next_selector.disabled = not bool(options)
        previous = []
        for src, tgts in self._graph.items():
            if self._stage in tgts:
                previous.append(src)
        self.prev_selector.options = previous
        self.prev_selector.value = self._route[-1] if previous else None
        self.prev_selector.disabled = not bool(previous)

        # Disable previous button
        if self._prev_stage is None:
            self.prev_button.disabled = True
        else:
            self.prev_button.disabled = False

        # Disable next button
        if self._next_stage is None:
            self.next_button.disabled = True
        else:
            ready = kwargs.get('ready_parameter', self.ready_parameter)
            disabled = (not getattr(stage, ready)) if ready in stage.param else False
            self.next_button.disabled = disabled

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
                        align='center', margin=(0, 0, 0, 5))
        button.js_on_click(code="alert(`{tb}`)".format(tb=traceback))
        return button

    @param.depends('next', watch=True)
    def _next(self):
        prev_state, prev_stage = self._state, self._stage
        self._stage = self._next_stage
        self.stage.loading = True
        try:
            self.stage[0] = self._init_stage()
        except Exception as e:
            self._error = self._stage
            self._stage = prev_stage
            self._state = prev_state
            self.stage[0] = prev_state.panel()
            self.error[:] = [self._get_error_button(e)]
            if self.debug:
                raise e
            return e
        else:
            self.error[:] = []
            self._error = None
            self._update_button()
            self._route.append(self._stage)
            stage_kwargs = self._stages[self._stage][-1]
            ready_param = stage_kwargs.get('ready_parameter', self.ready_parameter)
            if (ready_param and getattr(self._state, ready_param, False) and
                stage_kwargs.get('auto_advance', self.auto_advance)):
                self._next()
        finally:
            self._update_progress()
            self.stage.loading = False

    @param.depends('previous', watch=True)
    def _previous(self):
        prev_state, prev_stage = self._state, self._stage
        self._stage = self._prev_stage
        try:
            if self._stage in self._states:
                self._state = self._states[self._stage]
                self.stage[0] = self._state.panel()
            else:
                self.stage[0] = self._init_stage()
            self._block = True
        except Exception as e:
            self.error[:] = [self._get_error_button(e)]
            self._error = self._stage
            self._stage = prev_stage
            self._state = prev_state
            if self.debug:
                raise e
        else:
            self.error[:] = []
            self._error = None
            self._update_button()
            self._route.pop()
        finally:
            self._update_progress()

    def _update_progress(self, *args):
        self.title.object = '## Stage: ' + self._stage
        self.network.object = self._make_progress()

    def _make_progress(self):
        import holoviews as hv
        import holoviews.plotting.bokeh  # noqa

        if self._graph:
            root = get_root(self._graph)
            depth = get_depth(root, self._graph)
            breadths = get_breadths(root, self._graph)
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
            for i, n in enumerate(subnodes[::-1]):
                if n == self._stage:
                    state = 'active'
                elif n == self._error:
                    state = 'error'
                elif n == self._next_stage:
                    state = 'next'
                else:
                    state = 'inactive'
                nodes.append((depth, step/2.+i*step, n, state))

        cmap = {'inactive': 'white', 'active': '#5cb85c', 'error': 'red',
                'next': 'yellow'}

        def tap_renderer(plot, element):
            from bokeh.models import TapTool
            gr = plot.handles['glyph_renderer']
            tap = plot.state.select_one(TapTool)
            tap.renderers = [gr]

        nodes = hv.Nodes(nodes, ['x', 'y', 'Stage'], 'State').opts(
            alpha=0, default_tools=['tap'], hooks=[tap_renderer],
            hover_alpha=0, selection_alpha=0, nonselection_alpha=0,
            axiswise=True, size=10, backend='bokeh'
        )
        self._progress_sel.source = nodes
        graph = hv.Graph((edges, nodes)).opts(
            edge_hover_line_color='black', node_color='State', cmap=cmap,
            tools=[], default_tools=['hover'], selection_policy=None,
            node_hover_fill_color='gray', axiswise=True, backend='bokeh')
        labels = hv.Labels(nodes, ['x', 'y'], 'Stage').opts(
            yoffset=-.30, default_tools=[], axiswise=True, backend='bokeh'
        )
        plot = (graph * labels * nodes) if self._linear else (graph * nodes)
        plot.opts(
            xaxis=None, yaxis=None, min_width=400, responsive=True,
            show_frame=False, height=height, xlim=(-0.25, depth+0.25),
            ylim=(0, 1), default_tools=['hover'], toolbar=None, backend='bokeh'
        )
        return plot

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
        for k in kwargs:
            if k not in self.param:
                raise ValueError("Keyword argument %s is not a valid parameter. " % k)

        if not self._linear and self._graph:
            raise RuntimeError("Cannot add stage after graph has been defined.")

        self._stages[name] = (stage, kwargs)
        if len(self._stages) == 1:
            self._stage = name
            self._route = [name]
            self._graph = {}
            self.stage[:] = [self._init_stage()]
        else:
            previous = [s for s in self._stages if s not in self._graph][0]
            self._graph[previous] = (name,)
        self._update_progress()
        self._update_button()

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

        graph = {k: v if isinstance(v, tuple) else (v,) for k, v in graph.items()}

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
            self._linear = False
        else:
            graph = {s: (t,) for s, t in zip(stages[:-1], stages[1:])}

        root = get_root(graph)
        if not is_traversable(root, graph, stages):
            raise ValueError('Graph is not fully traversable from stage: %s.'
                             % root)

        reinit = root is not self._stage
        self._stage = root
        self._graph = graph
        self._route = [root]
        if not self._linear:
            self.buttons[:] = [
                Column(self.prev_selector, self.prev_button),
                Column(self.next_selector, self.next_button)
            ]
        if reinit:
            self.stage[:] = [self._init_stage()]
        self._update_progress()
        self._update_button()


__all__ = (
    "Pipeline",
)
