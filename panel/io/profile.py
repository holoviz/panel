from __future__ import annotations

import io
import os
import re
import tempfile
import uuid

from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from cProfile import Profile
from functools import wraps
from typing import (
    TYPE_CHECKING, Literal, ParamSpec, TypeVar,
)

from ..config import config
from ..util import escape
from .state import state

if TYPE_CHECKING:
    from pyinstrument.session import Session

    _P = ParamSpec("_P")
    _R = TypeVar("_R")

ProfilingEngine = Literal["pyinstrument", "snakeviz", "memray"]


def render_pyinstrument(sessions, timeline=False, show_all=False):
    from pyinstrument.renderers import HTMLRenderer
    from pyinstrument.session import Session
    r = HTMLRenderer(timeline=timeline, show_all=show_all)
    if timeline:
        session = sessions[-1]
    else:
        session = sessions[0]
        for s in sessions[1:]:
            session = Session.combine(session, s)
    try:
        rendered = r.render(session)
    except Exception:
        rendered = "<h2><b>Rendering pyinstrument session failed</b></h2>"
    return escape(rendered), ""

def render_snakeviz(name, sessions):
    from pstats import Stats

    import snakeviz

    from snakeviz.stats import json_stats, table_rows
    from tornado.template import Template

    SNAKEVIZ_PATH = os.path.join(os.path.dirname(snakeviz.__file__), 'templates', 'viz.html')
    with open(SNAKEVIZ_PATH) as f:
        SNAKEVIZ_TEMPLATE = Template(f.read())
    pstats = Stats(sessions[0])
    for session in sessions[1:]:
        pstats.add(session)
    rendered = SNAKEVIZ_TEMPLATE.generate(
        profile_name=name, table_rows=table_rows(pstats), callees=json_stats(pstats)
    ).decode('utf-8').replace('/static/', '/snakeviz/static/')
    return escape(rendered), "background-color: white;"

def render_memray(name, sessions, show_memory_leaks=True, merge_threads=True, reporter='tree'):
    from memray import FileReader
    from memray.reporters.flamegraph import FlameGraphReporter
    from memray.reporters.stats import StatsReporter
    from memray.reporters.table import TableReporter
    from memray.reporters.tree import TreeReporter

    reporter_cls = {
        'flamegraph': FlameGraphReporter,
        'stats': StatsReporter,
        'table': TableReporter,
        'tree': TreeReporter
    }.get(reporter)

    session = sessions[-1]
    with tempfile.NamedTemporaryFile() as nf:
        nf.write(session)
        nf.flush()
        reader = FileReader(nf.name)
        if show_memory_leaks:
            snapshot = reader.get_leaked_allocation_records(
                merge_threads=merge_threads if merge_threads is not None else True
            )
        else:
            snapshot = reader.get_high_watermark_allocation_records(
                merge_threads=merge_threads if merge_threads is not None else True
            )

        kwargs = {'native_traces': reader.metadata.has_native_traces}
        if reporter in ('flamegraph', 'table'):
            kwargs['memory_records'] = tuple(reader.get_memory_snapshots())
        reporter_inst = reporter_cls.from_snapshot(
            snapshot,
            **kwargs
        )

    out = io.StringIO()
    if reporter == 'flamegraph':
        reporter_inst.render(out, reader.metadata, show_memory_leaks, merge_threads)
    elif reporter == 'table':
        reporter_inst.render(out, reader.metadata, show_memory_leaks)
    else:
        reporter_inst.render(file=out)
    out.seek(0)
    return out.read(), ""

def get_profiles(profilers, **kwargs):
    from ..pane import HTML, Markdown
    profiles = []
    for (path, engine), sessions in profilers.items():
        if not sessions:
            continue
        if engine == 'memray':
            src, style = render_memray(path, sessions, **kwargs)
            if kwargs.get('reporter', 'tree') not in ('flamegraph', 'table'):
                from ..widgets import Terminal
                term = Terminal(sizing_mode='stretch_both', margin=0, min_height=600)
                term.write(src)
                profiles.append((path, term))
                continue
            else:
                src = escape(src)
        if engine == 'pyinstrument':
            src, style = render_pyinstrument(sessions, **kwargs)
        elif engine == 'snakeviz':
            src, style = render_snakeviz(path, sessions)
        html = HTML(
            f'<iframe srcdoc="{src}" width="100%" height="100%" frameBorder="0" style="{style}"></iframe>',
            sizing_mode='stretch_both',
            margin=0,
            min_height=800
        )
        profiles.append((path, html))
    if not profiles:
        profiles.append(('', Markdown('No profiling output available')))
    return profiles


def get_sessions(allow=None, deny=None):
    return {(name, e): ps for (name, e), ps in state._profiles.items()
            if (not allow or re.match(allow, name)) and (not deny or not re.match(deny, name))}


def profiling_tabs(state, allow=None, deny=[]):
    from ..layout import (
        Accordion, Column, Row, Tabs,
    )
    from ..widgets import Checkbox, Select
    tabs = Tabs(
        *get_profiles(get_sessions(allow, deny)),
        margin=(0, 5),
        sizing_mode='stretch_width'
    )
    def update_profiles(*args, **kwargs):
        tabs[:] = get_profiles(
            get_sessions(allow, deny), **kwargs

        )
    state.param.watch(update_profiles, '_profiles')

    if config.profiler == 'pyinstrument':
        def update_pyinstrument(*args):
            update_profiles(timeline=timeline.value, show_all=show_all.value)
        timeline = Checkbox(name='Enable timeline', margin=(5, 0))
        timeline.param.watch(update_pyinstrument, 'value')
        show_all = Checkbox(name='Show All', margin=(5, 0))
        show_all.param.watch(update_pyinstrument, 'value')
        config_panel = Row(
            timeline,
            show_all,
            sizing_mode='stretch_width'
        )
    elif config.profiler == 'memray':
        def update_memray(*args):
            update_profiles(reporter=reporter.value)
        reporter = Select(name='Reporter', options=['flamegraph', 'table', 'tree'], value='tree')
        reporter.param.watch(update_memray, 'value')
        config_panel = reporter
    else:
        config_panel = Row(sizing_mode='stretch_width')
    return Column(
        Accordion(
            ('Config', config_panel),
            active=[],
            active_header_background='#444444',
            header_background='#333333',
            sizing_mode='stretch_width',
            margin=0
        ),
        tabs,
        sizing_mode='stretch_width'
    )


@contextmanager
def profile_ctx(engine: ProfilingEngine = 'pyinstrument') -> Iterator[Sequence[Profile | bytes | Session]]:
    """
    A context manager which profiles the body of the with statement
    with the supplied profiling engine and returns the profiling object
    in a list.

    Parameters
    ----------
    engine: str
      The profiling engine, e.g. 'pyinstrument', 'snakeviz' or 'memray'

    Returns
    -------
    sessions: list
      A list containing the profiling session.
    """
    if engine == 'pyinstrument':
        from pyinstrument import Profiler
        try:
            prof = Profiler()
            prof.start()
        except RuntimeError:
            prof = Profiler(async_mode='disabled')
            prof.start()
    elif engine == 'snakeviz':
        profile = Profile()
        profile.enable()
    elif engine == 'memray':
        import memray
        tmp_file = f'{tempfile.gettempdir()}/tmp{uuid.uuid4().hex}'
        tracker = memray.Tracker(tmp_file)
        tracker.__enter__()
    elif engine is None:
        pass
    sessions: Sequence[Profile | bytes | Session] = []
    yield sessions
    if engine == 'pyinstrument':
        sessions.append(prof.stop())
    elif engine == 'snakeviz':
        profile.disable()
        sessions.append(profile)
    elif engine == 'memray':
        tracker.__exit__(None, None, None)
        sessions.append(open(tmp_file, 'rb').read())
        os.remove(tmp_file)


def profile(name: str, engine: ProfilingEngine = 'pyinstrument') -> Callable[[Callable[_P, _R]], Callable[_P, _R]]:
    """
    A decorator which may be added to any function to record profiling
    output.

    Parameters
    ----------
    name: str
      A unique name for the profiling session.
    engine: str
      The profiling engine, e.g. 'pyinstrument', 'snakeviz' or 'memray'
    """
    if not isinstance(name, str):
        raise ValueError("Profiler must be given a name.")
    def wrapper(func: Callable[_P, _R]) -> Callable[_P, _R]:
        @wraps(func)
        def wrapped(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            if state.curdoc and state.curdoc in state._launching:
                return func(*args, **kwargs)
            with profile_ctx(engine) as sessions:
                ret = func(*args, **kwargs)
            state._profiles[(name, engine)] += list(sessions)
            state.param.trigger('_profiles')
            return ret
        return wrapped
    return wrapper
