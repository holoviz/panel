from __future__ import annotations

import datetime as dt
import logging
import os
import sys
import time

from functools import partial
from typing import TYPE_CHECKING

import bokeh
import numpy as np
import pandas as pd
import param

from bokeh.models import HoverTool
from bokeh.plotting import ColumnDataSource, figure

from ..config import config, panel_extension as extension
from ..depends import bind
from ..layout import (
    Accordion, Column, FlexBox, Row, Tabs,
)
from ..pane import HTML, Bokeh
from ..template import FastListTemplate
from ..widgets import (
    Button, MultiSelect, Tabulator, TextInput,
)
from ..widgets.indicators import Trend
from .logging import (
    LOG_SESSION_CREATED, LOG_SESSION_DESTROYED, LOG_SESSION_LAUNCHING,
    panel_logger,
)
from .notebook import push_notebook
from .profile import profiling_tabs
from .server import set_curdoc
from .state import state

if TYPE_CHECKING:
    from psutil import Process


PROCESSES: dict[int, Process] = {}

log_sessions = []

class LogFilter(logging.Filter):

    def filter(self, record):
        if 'Session ' not in record.msg:
            return True
        session_id = record.args[0]
        if session_id in log_sessions:
            return False
        elif session_id not in session_filter.options:
            session_filter.options = [session_id] + session_filter.options
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


class _LogTabulator(Tabulator):

    _update_defaults = {
        "theme": "midnight",
        "layout": "fit_data_stretch",
        "show_index": False,
        "sorters": [{'field': 'datetime', 'dir': 'dsc'}],
        "disabled": True,
        "pagination": "local",
        "page_size": 18,
    }

    def __init__(self, **params):
        params["value"] = self._create_frame()
        params = {**self._update_defaults, **params}
        super().__init__(**params)

    @staticmethod
    def _create_frame(data=None):
        columns=["datetime", "level", "app", "session", "message"]
        if data is None:
            return pd.DataFrame(columns=columns)
        else:
            return pd.Series(data, index=columns)

    def write(self, log):
        # Example of a log message:
        # '2022-07-13 14:38:04,803 INFO: panel.io.server - Session 140255299576448 launching\n'
        try:
            s = log.strip().split(" ")
            datetime = f"{s[0]} {s[1]}"
            level = s[2][:-1]
            app = s[3]
            session = int(s[6])
            message = " ".join(s[7:])
            df = self._create_frame([datetime, level, app, session, message])

            self.stream(df, follow=False)
        except Exception:
            pass


# Set up logging
session_filter = MultiSelect(name='Filter by session', options=[])
message_filter = TextInput(name='Filter by message')
level_filter = MultiSelect(name="Filter by level", options=["DEBUG", "INFO", "WARNING", "ERROR"])
app_filter = TextInput(name='Filter by app')

data = Data()
log_data_handler = LogDataHandler(data)
log_handler = logging.StreamHandler()
log_handler.setLevel(config.admin_log_level)
panel_logger.addHandler(log_handler)
panel_logger.addHandler(log_data_handler)

log_filter = LogFilter()
log_handler.addFilter(log_filter)
log_data_handler.addFilter(log_filter)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(name)s - %(message)s')
log_handler.setFormatter(formatter)
log_terminal = _LogTabulator(sizing_mode='stretch_both', min_height=400)
log_handler.setStream(log_terminal)

def _textinput_filter(df, pattern, column):
    if not pattern or df.empty:
        return df
    return df[df[column].str.contains(pattern)].copy()

log_terminal.add_filter(level_filter, 'level')
log_terminal.add_filter(bind(_textinput_filter, pattern=app_filter, column='app'))
log_terminal.add_filter(session_filter, 'session')
log_terminal.add_filter(bind(_textinput_filter, pattern=message_filter, column='message'))


def _clear_log_filters(*events):
    level_filter.value = []
    app_filter.value = ""
    session_filter.value = []
    message_filter.value = ""


reset_filter = Button(name="Clear filters")
reset_filter.on_click(_clear_log_filters)


download_filename, download_button = log_terminal.download_menu(
    text_kwargs={'name': 'Enter filename for logfile', 'value': 'log.csv'},
    button_kwargs={'name': 'Download logfile'}
)


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
            if msg.startswith(f'Session {sid} logged'):
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
        try:
            update_cds(record)
        except Exception:
            pass

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

def get_process():
    import psutil
    if os.getpid() in PROCESSES:
        process = PROCESSES[os.getpid()]
    else:
        PROCESSES[os.getpid()] = process = psutil.Process(os.getpid())
    return process

def get_mem():
    return pd.DataFrame([(time.time(), get_process().memory_info().rss/1024/1024)], columns=['time', 'memory'])

def get_cpu():
    return pd.DataFrame([(time.time(), get_process().cpu_percent())], columns=['time', 'cpu'])

def get_process_info():
    memory = Trend(
        data=get_mem(), plot_x='time', plot_y='memory', plot_type='step',
        name='Memory Usage (MB)', width=300, height=300
    )
    cpu = Trend(
        data=get_cpu(), plot_x='time', plot_y='cpu', plot_type='step',
        name='CPU Usage (%)', width=300, height=300
    )
    def update_stats():
        memory.stream(get_mem())
        cpu.stream(get_cpu())
    stats_cb = state.add_periodic_callback(update_stats, period=1000, start=False)
    stats_cb.log = False
    stats_cb.start()
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
        name='Total Sessions', width=300, height=300
    )
    active = Trend(
        data=df[['time', 'live']], plot_x='time', plot_y='live', plot_type='step',
        name='Active Sessions', width=300, height=300
    )
    render = Trend(
        data=df[['time', 'render']], plot_x='time', plot_y='render', plot_type='step',
        name='Avg. Time to Render (s)', width=300, height=300
    )
    duration = Trend(
        data=df[['time', 'duration']], plot_x='time', plot_y='duration', plot_type='step',
        name='Avg. Session Duration (s)', width=300, height=300
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
    try:
        import psutil  # noqa
    except Exception:
        layout.append(info)
        return layout
    else:
        layout.extend([*get_process_info(), info])
        return layout


def log_component():
    # Without this tabulator is empty after reload of website
    log_terminal.param.trigger("value")

    return Column(
        Accordion(
            ('Filters & Download', Row(
                level_filter,
                app_filter,
                session_filter,
                message_filter,
                Column(
                    download_filename,
                    download_button,
                    reset_filter,
                ),
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

def admin_template(doc):
    extension('tabulator', 'terminal')
    log_sessions.append(id(doc))
    def _remove_log_session(session_context):
        log_sessions.remove(id(doc))
    doc.on_session_destroyed(_remove_log_session)

    # Add and remove admin panel app from log sessions list
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
    tabs.extend([
        (name, plugin()) for name, plugin in config.admin_plugins
    ])
    template.main.append(tabs)
    return template

def admin_panel(doc):
    with set_curdoc(doc):
        template = admin_template(doc)
        template.server_doc(doc)
    return doc
