import datetime as dt
import logging
import os
import sys
import time

import bokeh
import numpy as np
import pandas as pd
import param

from ..config import config
from ..models import terminal # noqa
from ..pane import HTML
from ..layout import Accordion, Column, Row, Tabs, FlexBox
from ..template import FastListTemplate
from ..widgets import MultiSelect, Terminal, TextInput
from ..widgets.indicators import Trend
from . import panel_logger
from .profile import profiling_tabs
from .server import set_curdoc
from .state import state

try:
    import psutil
    process = psutil.Process(os.getpid())
except Exception:
    process = None

log_sessions = []

class LogFilter(logging.Filter):

    def filter(self, record):
        if 'Session ' not in record.msg:
            return True
        session_id = record.args[0]
        if session_id in log_sessions:
            return False
        elif session_id not in session_filter.options:
            session_filter.options = session_filter.options + [session_id]
        if session_filter.value and session_id not in session_filter.value:
            return False
        if name_filter.value and name_filter.value not in record.name:
            return False
        return True

# Set up logging
log_handler = logging.StreamHandler()
log_handler.setLevel('DEBUG')
panel_logger.addHandler(log_handler)

log_filter = LogFilter()
log_handler.addFilter(log_filter)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(name)s - %(message)s')
log_handler.setFormatter(formatter)
log_terminal = Terminal(sizing_mode='stretch_both', min_height=400)
log_handler.setStream(log_terminal)

session_filter = MultiSelect(name='Filter by session', options=[])
name_filter = TextInput(name='Filter by component')

def get_mem():
    return pd.DataFrame([(time.time(), process.memory_info().rss/1024/1024)], columns=['time', 'memory'])

def get_cpu():
    return pd.DataFrame([(time.time(), process.cpu_percent())], columns=['time', 'cpu'])

def get_session_info():
    durations, renders, sessions = [], [], []
    session_info = state.session_info['sessions']
    for i, session in enumerate(session_info.values()):
        is_live = session['ended'] is None
        live = sum([
            1 for s in session_info.values()
            if s['launched'] < session['launched'] and
            (not s['ended'] or s['ended'] > session['launched'])
        ]) + 1
        if session['rendered'] is not None:
            renders.append(session['rendered']-session['started'])
        if not is_live:
            durations.append(session['ended']-session['launched'])
        duration = np.mean(durations) if durations else 0
        render = np.mean(renders) if renders else 0
        sessions.append((session['launched'], live, i+1, render, duration))
    if not sessions:
        i = -1
        duration = 0
        render = 0
    now = dt.datetime.now().timestamp()
    live = sum([
        1 for s in session_info.values()
        if s['launched'] < now and
        (not s['ended'] or s['ended'] > now)
    ])
    sessions.append((now, live, i+1, render, duration))
    return pd.DataFrame(sessions, columns=['time', 'live', 'total', 'render', 'duration'])


def overview():
    from panel import __version__
    df = get_session_info()
    active = Trend(
        data=df[['time', 'total']], plot_x='time', plot_y='total', plot_type='step',
        title='Total Sessions', width=300, height=300
    )
    total = Trend(
        data=df[['time', 'live']], plot_x='time', plot_y='live', plot_type='step',
        title='Active Sessions', width=300, height=300
    )
    render = Trend(
        data=df[['time', 'render']], plot_x='time', plot_y='render', plot_type='step',
        title='Avg. Time to Render (s)', width=300, height=300
    )
    duration = Trend(
        data=df[['time', 'duration']], plot_x='time', plot_y='duration', plot_type='step',
        title='Avg. Session Duration (s)', width=300, height=300
    )
    def update_session_info(event):
        df = get_session_info()
        for trend in layout.objects[:4]:
            trend.data = df[[trend.plot_x, trend.plot_y]]
    state.param.watch(update_session_info, 'session_info')
    layout = FlexBox(
        active,
        total,
        render,
        duration,
        margin=0,
        sizing_mode='stretch_width'
    )
    info = HTML(f"""
    <h4>
    Panel Server running on following versions:
    </h4>
    <code>
    Python {sys.version.split('|')[0]}</br>
    Panel: {__version__}</br>
    Bokeh: {bokeh.__version__}</br>
    Param: {param.__version__}</br>
    </code>""", width=300, height=300, margin=(0, 5))
    if process is None:
        layout.append(info)
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
    state.add_periodic_callback(update_memory, period=1000)
    state.add_periodic_callback(update_cpu, period=1000)
    
    layout.extend([memory, cpu, info])
    return layout


def log_component():
    return Column(
        Accordion(
            ('Filters', Row(
                session_filter,
                name_filter
            )),
            active=[],
            active_header_background='#444444',
            header_background='#333333',
            sizing_mode='stretch_width'
        ),
        log_terminal,
        sizing_mode='stretch_both'
    )


def admin_panel(doc):
    log_sessions.append(id(doc))
    template = FastListTemplate(title='Admin Panel', theme='dark')
    tabs = Tabs(
        ('Overview', overview()),
        margin=0,
        sizing_mode='stretch_both'
    )
    if config.profiler:
        tabs.append(
            ('Launch Profiling', profiling_tabs(state, r'^\/.*', None))
        )
    tabs.extend([
        ('User Profiling', profiling_tabs(state, None, r'^\/.*')),
        ('Logs', log_component())
    ])
    template.main.append(tabs)
    with set_curdoc(doc):
        template.server_doc(doc)
    return doc
