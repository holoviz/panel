import os
import time

import numpy as np
import pandas as pd

from ..models import terminal # noqa
from ..pane import HTML
from ..layout import Card, Column, Row, Tabs, FlexBox
from ..template import FastListTemplate
from ..util import escape
from ..widgets import Terminal
from ..widgets.indicators import Trend
from .server import set_curdoc
from .state import state

try:
    import psutil
    process = psutil.Process(os.getpid())
except:
    process = None

def launch_profiler():
    from pyinstrument.session import Session
    from pyinstrument.renderers import HTMLRenderer
    r = HTMLRenderer()

    tabs = Tabs(sizing_mode='stretch_width')
    for path, sessions in state._sessions.items():
        if sessions:
            session = sessions[0]
            for s in sessions[1:]:
                session = Session.combine(session, s)
            src = r.render(session)
        else:
            continue
        html = HTML(
            f'<iframe srcdoc="{escape(src)}" width="100%" height="100%" frameBorder="0"></iframe>',
            sizing_mode='stretch_both',
            margin=0
        )
        tabs.append((path, html))
    if not tabs:
        tabs.append(('', 'No active sessions'))
    return tabs


def get_mem():
    return pd.DataFrame([(time.time(), process.memory_info().rss/1024/1024)], columns=['time', 'memory'])

def get_cpu():
    return pd.DataFrame([(time.time(), process.cpu_percent())], columns=['time', 'cpu'])

def overview():
    live = 0
    durations, renders, sessions = [], [], []
    for i, session in enumerate(state.session_info['sessions'].values()):
        is_live = session['ended'] is None
        live += 1 if is_live else 0
        if session['rendered'] is not None:
            renders.append(session['rendered']-session['started'])
        if not is_live:
            durations.append(session['ended']-session['launched'])
        duration = np.mean(durations) if durations else 0
        render = np.mean(renders) if renders else 0
        sessions.append((session['launched'], live, i+1, render, duration))
    df = pd.DataFrame(sessions, columns=['time', 'live', 'total', 'render', 'duration'])
    active = Trend(
        data=df, plot_x='time', plot_y='total', plot_type='step',
        title='Total Sessions', width=300, height=300
    )
    total = Trend(
        data=df, plot_x='time', plot_y='live', plot_type='step',
        title='Active Sessions', width=300, height=300
    )
    render = Trend(
        data=df, plot_x='time', plot_y='render', plot_type='step',
        title='Avg. Time to Render (s)', width=300, height=300
    )
    duration = Trend(
        data=df, plot_x='time', plot_y='duration', plot_type='step',
        title='Avg. Session Duration (s)', width=300, height=300
    )
    layout = FlexBox(
        active,
        total,
        render,
        duration,
        margin=0,
        sizing_mode='stretch_width'
    )
    if process is None:
        return layout

    memory = Trend(
        data=get_mem(), plot_x='time', plot_y='memory', plot_type='step',
        title='Memory Usage (MB)', width=300, height=300
    )
    cpu = Trend(
        data=get_cpu(), plot_x='time', plot_y='cpu', plot_type='step',
        title='CPU Usage (%)', width=300, height=300
    )
    def update_memory(): memory.stream(get_mem())
    def update_cpu(): cpu.stream(get_cpu())
    state.add_periodic_callback(update_memory)
    state.add_periodic_callback(update_cpu)

    layout.extend([memory, cpu])
    return layout


def admin_panel(doc):
    template = FastListTemplate(title='Admin Panel', theme='dark')
    tabs = Tabs(
        ('Overview', overview()),
        ('Launch Profiling', launch_profiler()),
        margin=0,
        sizing_mode='stretch_both'
    )
    template.main.append(tabs)
    with set_curdoc(doc):
        template.server_doc(doc)
    return doc
