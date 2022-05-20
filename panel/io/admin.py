import datetime as dt
import logging
import os
import sys
import time

from functools import partial

import bokeh
import numpy as np
import pandas as pd
import param

from bokeh.models import HoverTool
from bokeh.plotting import ColumnDataSource, figure

from ..config import config
from ..models import terminal # noqa
from ..pane import Bokeh, HTML
from ..layout import Accordion, Column, Row, Tabs, FlexBox
from ..template import FastListTemplate
from ..widgets import MultiSelect, Terminal, TextInput
from ..widgets.indicators import Trend
from .logging import (
    LOG_SESSION_CREATED, LOG_SESSION_LAUNCHING, LOG_SESSION_DESTROYED,
    panel_logger
)
from .notebook import push_notebook
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


class Data(param.Parameterized):

    data = param.List()


class LogDataHandler(logging.StreamHandler):

    def __init__(self, data):
        super().__init__()
        self._data = data

    def emit(self, record):
        if 'Session ' not in record.msg:
            return
        self._data.data.append(record)
        self._data.param.trigger('data')


# Set up logging
data = Data()
log_data_handler = LogDataHandler(data)
log_handler = logging.StreamHandler()
log_handler.setLevel('DEBUG')
panel_logger.addHandler(log_handler)
panel_logger.addHandler(log_data_handler)

log_filter = LogFilter()
log_handler.addFilter(log_filter)
log_data_handler.addFilter(log_filter)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(name)s - %(message)s')
log_handler.setFormatter(formatter)
log_terminal = Terminal(sizing_mode='stretch_both', min_height=400)
log_handler.setStream(log_terminal)

session_filter = MultiSelect(name='Filter by session', options=[])
name_filter = TextInput(name='Filter by component')

EVENT_TYPES = {
    'initializing': 'MediumSeaGreen',
    'destroyed': 'red',
    'rendering': 'Orange',
    'processing': 'DodgerBlue',
    'periodic': 'Violet',
    'logging': 'white'
}

def get_timeline(doc=None):
    sessions = []

    # Configure plot
    p = figure(
        y_range=list(sessions), x_axis_type='datetime', sizing_mode='stretch_both'
    )
    cds = ColumnDataSource(data={
        'x0': [], 'x1': [], 'y0': [], 'y1': [], 'msg': [],
        'session': [], 'color': [], 'line_color': [], 'type': []
    })
    p.yaxis.axis_label = 'Sessions'
    p.quad(
        left='x0', right='x1', top='y1', bottom='y0', source=cds,
        line_color='line_color', fill_color='color', alpha=0.7,
        legend_field='type'
    )
    p.legend.location = "top_left"
    p.add_tools(HoverTool(
        tooltips=[
            ('Start', '@x0{%F %T}'),
            ('End', '@x1{%F %T}'),
            ('Session', '@session'),
            ('Message', '@msg'),
        ],
        formatters={'@x0': 'datetime', '@x1': 'datetime'}
    ))

    def update_cds(new, nb=False):
        sid = str(new.args[0])
        if sid not in sessions:
            sessions.append(sid)
        if 'finished processing events' in new.msg:
            msg = new.getMessage()
            etype = 'processing'
            try:
                index = cds.data['msg'].index(msg.replace('finished processing', 'received'))
            except Exception:
                return
            patch = {
                'x1': [(index, new.created*1000)],
                'color': [(index, EVENT_TYPES[etype])],
                'type': [(index, etype)],
                'msg': [(index, msg.replace('finished processing', 'processed'))]
            }
            cds.patch(patch)
        elif new.msg == LOG_SESSION_CREATED:
            index = cds.data['msg'].index(LOG_SESSION_LAUNCHING % sid)
            etype = 'initializing'
            patch = {
                'x1': [(index, new.created*1000)],
                'color': [(index, EVENT_TYPES[etype])],
                'type': [(index, etype)],
                'msg': [(index, f'Session {sid} initializing')]
            }
            cds.patch(patch)
        elif 'finished executing periodic callback' in new.msg:
            etype = 'periodic'
            msg = new.getMessage()
            index = cds.data['msg'].index(msg.replace('finished executing', 'executing'))
            patch = {
                'x1': [(index, new.created*1000)],
                'color': [(index, EVENT_TYPES[etype])],
                'type': [(index, etype)]
            }
            cds.patch(patch)
        elif new.msg.endswith('rendered'):
            try:
                index = cds.data['msg'].index(f'Session {sid} initializing')
                x0 = cds.data['x1'][index]
            except ValueError:
                x0 = new.created*1000
            etype = 'rendering'
            event = {
                'x0': [x0],
                'x1': [new.created*1000],
                'y0': [(sid, -.25)],
                'y1': [(sid, .25)],
                'session': [sid],
                'msg': [new.getMessage().replace('rendered', 'rendering')],
                'color': [EVENT_TYPES[etype]],
                'line_color': ['black'],
                'type': [etype]
            }
            cds.stream(event)
        else:
            msg = new.getMessage()
            line_color = 'black'
            if msg.startswith('Session %s logged' % sid):
                etype = 'logging'
                line_color = EVENT_TYPES.get(etype)
            elif msg.startswith(LOG_SESSION_DESTROYED % sid):
                etype = 'destroyed'
                line_color = EVENT_TYPES.get(etype)
            elif 'executing periodic callback' in msg:
                etype = 'periodic'
                line_color = EVENT_TYPES.get(etype)
            else:
                etype = 'processing'
            event = {
                'x0': [new.created*1000],
                'x1': [new.created*1000],
                'y0': [(sid, -.25)],
                'y1': [(sid, .25)],
                'session': [sid],
                'msg': [msg],
                'color': [EVENT_TYPES[etype]],
                'line_color': [line_color],
                'type': [etype]
            }
            if p.y_range.factors != sessions:
                p.y_range.factors = list(sessions)
            cds.stream(event)
        if nb:
            push_notebook(bk_pane)

    for record in log_data_handler._data.data:
        update_cds(record)

    def schedule_cds_update(event):
        new = event.new[-1]
        if doc:
            doc.add_next_tick_callback(partial(update_cds, new))
        else:
            update_cds(new, nb=True)

    watcher = log_data_handler._data.param.watch(schedule_cds_update, 'data')
    if doc:
        def _unwatch_data(session_context):
            log_data_handler._data.param.unwatch(watcher)
        doc.on_session_destroyed(_unwatch_data)

    bk_pane = Bokeh(p)
    return bk_pane

def get_version_info():
    from panel import __version__
    return HTML(f"""
    <h4>
    Panel Server running on following versions:
    </h4>
    <code>
    Python {sys.version.split('|')[0]}</br>
    Panel: {__version__}</br>
    Bokeh: {bokeh.__version__}</br>
    Param: {param.__version__}</br>
    </code>""", width=300, height=300, margin=(0, 5))

def get_mem():
    return pd.DataFrame([(time.time(), process.memory_info().rss/1024/1024)], columns=['time', 'memory'])

def get_cpu():
    return pd.DataFrame([(time.time(), process.cpu_percent())], columns=['time', 'cpu'])

def get_process_info():
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
    mem_cb = state.add_periodic_callback(update_memory, period=1000, start=False)
    cpu_cb = state.add_periodic_callback(update_cpu, period=1000, start=False)
    mem_cb.log = False
    cpu_cb.log = False
    mem_cb.start()
    cpu_cb.start()
    return memory, cpu

def get_session_data():
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

def get_session_info(doc=None):
    df = get_session_data()
    total = Trend(
        data=df[['time', 'total']], plot_x='time', plot_y='total', plot_type='step',
        title='Total Sessions', width=300, height=300
    )
    active = Trend(
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
    # Set up callbacks
    def update_session_info(event):
        df = get_session_data()
        for trend in (total, active, render, duration):
            trend.data = df[[trend.plot_x, trend.plot_y]]
    watcher = state.param.watch(update_session_info, 'session_info')
    if doc:
        def _unwatch_session_info(session_context):
            state.param.unwatch(watcher)
        doc.on_session_destroyed(_unwatch_session_info)
    return total, active, render, duration

def get_overview(doc=None):
    layout = FlexBox(*get_session_info(doc), margin=0, sizing_mode='stretch_width')
    info = get_version_info()
    if process is None:
        layout.append(info)
        return layout
    layout.extend([*get_process_info(), info])
    return layout


def log_component():
    return Column(
        Accordion(
            ('Filters', Row(
                session_filter,
                name_filter,
                sizing_mode='stretch_width'
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
    # Add and remove admin panel app from log sessions list
    log_sessions.append(id(doc))
    def _remove_log_session(session_context):
        log_sessions.remove(id(doc))
    doc.on_session_destroyed(_remove_log_session)

    # Set up admin panel
    template = FastListTemplate(title='Admin Panel', theme='dark')
    tabs = Tabs(
        ('Overview', get_overview(doc)),
        ('Timeline', get_timeline(doc)),
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
