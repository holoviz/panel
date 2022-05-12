import os
import re

from contextlib import contextmanager
from cProfile import Profile
from functools import wraps

from ..util import escape
from .state import state


def render_pyinstrument(sessions, timeline=False, show_all=False):
    from pyinstrument.session import Session
    from pyinstrument.renderers import HTMLRenderer
    r = HTMLRenderer(timeline=timeline, show_all=show_all)
    session = sessions[0]
    if not timeline:
        for s in sessions[1:]:
            session = Session.combine(session, s)
    return escape(r.render(session)), ""


def render_snakeviz(name, sessions):
    import snakeviz

    from pstats import Stats
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


def get_profiles(profilers, **kwargs):
    from ..pane import HTML, Markdown
    profiles = []
    for (path, engine), sessions in profilers.items():
        if not sessions:
            continue
        if engine == 'pyinstrument':
            src, style = render_pyinstrument(sessions, **kwargs)
        elif engine == 'snakeviz':
            src, style = render_snakeviz(path, sessions)
        html = HTML(
            f'<iframe srcdoc="{src}" width="100%" height="100%" frameBorder="0" style="{style}"></iframe>',
            sizing_mode='stretch_both',
            margin=0,
            min_height=400
        )
        profiles.append((path, html))
    if not profiles:
        profiles.append(('', Markdown('No profiling output available')))
    return profiles


def get_sessions(allow=None, deny=None):
    return {(name, e): ps for (name, e), ps in state._profiles.items()
            if (not allow or re.match(allow, name)) and (not deny or not re.match(deny, name))}


def profiling_tabs(state, allow=None, deny=[]):
    from ..layout import Accordion, Column, Row, Tabs
    from ..widgets import Checkbox
    tabs = Tabs(
        *get_profiles(get_sessions(allow, deny)),
        margin=(0, 5),
        sizing_mode='stretch_width'
    )
    def update_profiles(*args):
        tabs[:] = get_profiles(
            get_sessions(allow, deny),
            timeline=timeline.value,
            show_all=show_all.value
        )
    state.param.watch(update_profiles, '_profiles')
    timeline = Checkbox(name='Enable timeline', margin=(5, 0))
    timeline.param.watch(update_profiles, 'value')
    show_all = Checkbox(name='Show All', margin=(5, 0))
    show_all.param.watch(update_profiles, 'value')
    return Column(
        Accordion(
            ('Config', Row(
                timeline,
                show_all,
                sizing_mode='stretch_width'
            )),
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
def profile_ctx(engine='pyinstrument'):
    """
    A context manager which profiles the body of the with statement
    with the supplied profiling engine and returns the profiling object
    in a list.

    Arguments
    ---------
    engine: str
      The profiling engine, e.g. 'pyinstrument' or 'snakeviz'

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
        prof = Profile()
        prof.enable()
    elif engine is None:
        pass
    sessions = []
    yield sessions
    if engine == 'pyinstrument':
        sessions.append(prof.stop())
    elif engine == 'snakeviz':
        prof.disable()
        sessions.append(prof)


def profile(name, engine='pyinstrument'):
    """
    A decorator which may be added to any function to record profiling
    output.

    Arguments
    ---------
    name: str
      A unique name for the profiling session.
    engine: str
      The profiling engine, e.g. 'pyinstrument' or 'snakeviz'
    """
    if not isinstance(name, str):
        raise ValueError("Profiler must be given a name.")
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if state.curdoc and state.curdoc in state._launching:
                return func(*args, **kwargs)
            with profile_ctx(engine) as sessions:
                ret = func(*args, **kwargs)
            state._profiles[(name, engine)] += sessions
            state.param.trigger('_profiles')
            return ret
        return wrapped
    return wrapper
