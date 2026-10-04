from __future__ import annotations

import datetime as dt
import functools
import io
import logging
import os
import sys
import time
import typing as t

from functools import partial

import bokeh
import numpy as np
import pandas as pd
import param

from bokeh.models import HoverTool
from bokeh.plotting import ColumnDataSource, figure

from ..config import config, panel_extension as extension
from ..widgets import Tabulator
from .logging import (
    LOG_SESSION_CREATED, LOG_SESSION_DESTROYED, LOG_SESSION_LAUNCHING,
    panel_logger,
)
from .notebook import push_notebook
from .pages import page_theme
from .profile import profiling_tabs
from .server import set_curdoc
from .state import state

if t.TYPE_CHECKING:
    from types import ModuleType

    from bokeh.document import Document
    from psutil import Process

    from ..viewable import Viewable


PROCESSES: dict[int, Process] = {}

LOG_COLUMNS = ["datetime", "level", "app", "session", "message"]

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

log_sessions: list = []


@functools.cache
def _ui() -> ModuleType:
    """
    Imports ``panel.ui`` without the global design switch its import
    performs, which would restyle every application served next to the
    admin panel. The package is dropped from ``sys.modules`` again so that
    an application importing it still gets the switch, its cached
    submodules keep the component classes identical.
    """
    if 'panel.ui' in sys.modules:
        return sys.modules['panel.ui']
    import panel

    design = param.Parameterized.__getattribute__(config, 'design')
    import panel.ui as ui
    param.Parameterized.__setattr__(config, 'design', design)
    del sys.modules['panel.ui']
    del panel.ui
    return ui


def _destroyed(doc: Document | None) -> bool:
    """
    Whether an admin session's document has been destroyed. The watchers on
    shared state are removed in on_session_destroyed callbacks, which run in
    arbitrary order, so they can still fire for a destroyed document.
    """
    return doc is not None and doc.session_context is None


class LogFilter(logging.Filter):

    def filter(self, record):
        if 'Session ' not in record.msg:
            return True
        return record.args[0] not in log_sessions


class Data(param.Parameterized):

    data = param.List(item_type=logging.LogRecord)


class LogDataHandler(logging.StreamHandler):

    def __init__(self, data):
        super().__init__()
        self._data = data

    def emit(self, record: logging.LogRecord):
        if 'Session ' not in record.msg:
            return
        self._data.data.append(record)
        self._data.param.trigger('data')


class _LogTabulator(Tabulator):
    """
    Collects the session log records shared by all admin sessions, each of
    which renders its own filtered view of the records.
    """

    _update_defaults = {
        "layout": "fit_data_stretch",
        "show_index": False,
        "sorters": [{'field': 'datetime', 'dir': 'desc'}],
        "disabled": True,
        "pagination": "local",
        "page_size": 20,
    }

    def __init__(self, **params):
        params["value"] = self._create_frame()
        params = {**self._update_defaults, **params}
        super().__init__(**params)

    @staticmethod
    def _create_frame(data=None):
        if data is None:
            return pd.DataFrame(columns=LOG_COLUMNS)
        return pd.DataFrame([data], columns=LOG_COLUMNS)

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
        except Exception:
            return
        # Streaming a DataFrame rather than a Series triggers the value
        # event the admin sessions watch.
        self.stream(self._create_frame([datetime, level, app, session, message]), follow=False)


# Set up logging
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
log_handler.setStream(t.cast('t.TextIO', log_terminal))


def _filter_logs(
    df: pd.DataFrame, levels: list[str], app: str, sessions: list[int], message: str
) -> pd.DataFrame:
    if df.empty:
        return df
    mask = pd.Series(True, index=df.index)
    if levels:
        mask &= df['level'].isin(levels)
    if sessions:
        mask &= df['session'].isin(sessions)
    # Matched literally, a regex would raise while the pattern is being typed.
    if app:
        mask &= df['app'].str.contains(app, case=False, regex=False)
    if message:
        mask &= df['message'].str.contains(message, case=False, regex=False)
    return df[mask]


EVENT_TYPES = {
    'initializing': 'MediumSeaGreen',
    'destroyed': 'red',
    'rendering': 'Orange',
    'processing': 'DodgerBlue',
    'periodic': 'Violet',
    'logging': 'SlateGray'
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
        if _destroyed(doc):
            log_data_handler._data.param.unwatch(watcher)
            return
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

    bk_pane = _ui().Bokeh(p, sizing_mode='stretch_both', min_height=500, margin=0)
    return bk_pane

def get_version_info():
    import panel_material_ui

    from panel import __version__

    ui = _ui()
    versions = {
        'Python': sys.version.split()[0],
        'Panel': __version__,
        'Bokeh': bokeh.__version__,
        'Param': param.__version__,
        'panel-material-ui': panel_material_ui.__version__,
    }
    chips = [
        ui.Chip(label=f'{name} {version}', variant='outlined')
        for name, version in versions.items()
    ]
    return ui.Card(
        ui.FlexBox(*chips, gap='8px', margin=0, sizing_mode='stretch_width'),
        title='Server versions', collapsible=False, sizing_mode='stretch_width',
        margin=(0, 0, 0, 0)
    )

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

def _trend(data, plot_y, label):
    ui = _ui()
    return ui.Trend(
        data=data, plot_x='time', plot_y=plot_y, plot_type='step', label=label,
        height=180, sizing_mode='stretch_width', margin=(10, 15)
    )

def get_process_info():
    memory = _trend(get_mem(), 'memory', 'Memory Usage (MB)')
    cpu = _trend(get_cpu(), 'cpu', 'CPU Usage (%)')
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
    total = _trend(df[['time', 'total']], 'total', 'Total Sessions')
    active = _trend(df[['time', 'live']], 'live', 'Active Sessions')
    render = _trend(df[['time', 'render']], 'render', 'Avg. Time to Render (s)')
    duration = _trend(df[['time', 'duration']], 'duration', 'Avg. Session Duration (s)')
    # Set up callbacks
    def update_session_info(event):
        if _destroyed(doc):
            state.param.unwatch(watcher)
            return
        # Destroying this session updates the session info after its models
        # have been cleaned up.
        session = event.new['sessions'].get(doc.session_context.id) if doc else None
        if session and session['ended']:
            return
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
    ui = _ui()
    trends = list(get_session_info(doc))
    try:
        import psutil  # noqa
    except Exception:
        process_info = [ui.Alert(
            'Install psutil to monitor the memory and CPU usage of the server.',
            severity='info', sizing_mode='stretch_width', margin=(0, 0, 0, 0)
        )]
    else:
        trends.extend(get_process_info())
        process_info = []
    cards = [
        ui.Paper(trend, variant='outlined', margin=(0, 0, 0, 0), sizing_mode='stretch_width')
        for trend in trends
    ]
    # Full width items share the grid spacing, keeping all gaps equal.
    return ui.Grid(
        *(ui.Grid(card, size={'xs': 12, 'sm': 6, 'xl': 4}) for card in cards),
        *(ui.Grid(item, size=12) for item in [*process_info, get_version_info()]),
        container=True, spacing=2, margin=(0, 0, 0, 0), sizing_mode='stretch_width'
    )


def log_component(doc: Document | None = None) -> Viewable:
    """
    A filterable view of the session logs with its own filter widgets, so
    that admin sessions do not share filter state.
    """
    ui = _ui()
    level_filter = ui.MultiChoice(
        label='Level', options=LOG_LEVELS, sizing_mode='stretch_width'
    )
    app_filter = ui.TextInput(label='App', sizing_mode='stretch_width')
    session_filter = ui.MultiChoice(
        label='Session', options=sorted(log_terminal.value['session'].unique().tolist()),
        sizing_mode='stretch_width'
    )
    message_filter = ui.TextInput(label='Message', sizing_mode='stretch_width')

    def filtered(df):
        return _filter_logs(
            df, level_filter.value, app_filter.value_input,
            session_filter.value, message_filter.value_input
        )

    table = ui.Tabulator(
        value=filtered(log_terminal.value), sizing_mode='stretch_both',
        min_height=400, margin=0, **_LogTabulator._update_defaults
    )

    def refilter(*events):
        table.value = filtered(log_terminal.value)

    level_filter.param.watch(refilter, 'value')
    session_filter.param.watch(refilter, 'value')
    app_filter.param.watch(refilter, 'value_input')
    message_filter.param.watch(refilter, 'value_input')

    def clear_filters(event):
        level_filter.value = []
        session_filter.value = []
        app_filter.value = app_filter.value_input = ''
        message_filter.value = message_filter.value_input = ''

    clear = ui.Button(
        label='Clear filters', icon='filter_alt_off', variant='outlined',
        on_click=clear_filters, margin=(5, 10)
    )
    download = ui.FileDownload(
        callback=lambda: io.StringIO(table.value.to_csv(index=False)),
        filename='panel_log.csv', label='Download log', icon='download',
        variant='outlined', margin=(5, 10)
    )

    def add_record(record):
        session = record['session'].iloc[0]
        if session not in session_filter.options:
            session_filter.options = sorted([*session_filter.options, session])
        rows = filtered(record)
        if rows.empty:
            return
        elif table.value.empty:
            table.value = rows
        else:
            table.stream(rows, follow=False)

    def schedule_record(event):
        if _destroyed(doc):
            log_terminal.param.unwatch(watcher)
            return
        # Capture the new row now, by the next tick more may have been logged.
        record = event.new.iloc[-1:]
        if doc:
            doc.add_next_tick_callback(partial(add_record, record))
        else:
            add_record(record)

    watcher = log_terminal.param.watch(schedule_record, 'value')
    if doc:
        doc.on_session_destroyed(lambda session_context: log_terminal.param.unwatch(watcher))

    filters = ui.Paper(
        ui.Grid(
            *(
                ui.Grid(widget, size={'xs': 12, 'sm': 6, 'lg': 3})
                for widget in (level_filter, app_filter, session_filter, message_filter)
            ),
            container=True, spacing=1, sizing_mode='stretch_width'
        ),
        ui.Row(clear, download, margin=0),
        variant='outlined', margin=(0, 0, 15, 0), sizing_mode='stretch_width'
    )
    return ui.Column(filters, table, sizing_mode='stretch_both', margin=0)


def _page_branding() -> dict[str, t.Any]:
    """
    Applies ``config.page_config`` so the admin panel shares the branding of
    the server pages. ``Page`` class defaults already apply on their own.
    """
    branding: dict[str, t.Any] = {}
    page_config = config.page_config
    if page_config.get('theme_config'):
        branding['theme_config'] = page_config['theme_config']
    if page_config.get('logo'):
        branding['logo'] = page_theme.logo
    if page_config.get('favicon'):
        branding['favicon'] = page_theme.favicon
    if page_config.get('site_url'):
        branding['site_url'] = page_config['site_url']
    if (dark_theme := page_theme.dark_theme) is not None:
        branding['dark_theme'] = dark_theme
    return branding


def admin_template(doc):
    ui = _ui()
    extension('tabulator', 'terminal')
    # Classic components (Tabulator, Bokeh, Trend) follow the Material design
    # in this session only, see _ui.
    config.design = ui.MaterialUIDesign
    log_sessions.append(id(doc))
    def _remove_log_session(session_context):
        log_sessions.remove(id(doc))
    doc.on_session_destroyed(_remove_log_session)

    sections: list[tuple[str, str, t.Callable[[], Viewable]]] = [
        ('Overview', 'dashboard', partial(get_overview, doc)),
        ('Timeline', 'timeline', partial(get_timeline, doc)),
    ]
    if config.profiler:
        sections.append(
            ('Launch Profiling', 'rocket_launch', partial(profiling_tabs, state, r'^\/.*', None))
        )
    sections.extend([
        ('User Profiling', 'speed', partial(profiling_tabs, state, None, r'^\/.*')),
        ('Logs', 'article', partial(log_component, doc)),
    ])
    sections.extend(
        (name, 'extension', plugin) for name, plugin in config.admin_plugins
    )

    # Sections are built on first visit, so watchers and periodic callbacks
    # only run for the sections an admin actually opens.
    rendered: dict[int, Viewable] = {}
    def section(index: int) -> Viewable:
        if index not in rendered:
            label, _, build = sections[index]
            rendered[index] = ui.Column(
                ui.Typography(label, variant='h5', margin=(0, 0, 10, 0)),
                build(),
                sizing_mode='stretch_both',
                margin=0
            )
        return rendered[index]

    menu = ui.MenuList(
        items=[{'label': label, 'icon': icon} for label, icon, _ in sections],
        active=0, dense=False, sizing_mode='stretch_width'
    )
    main = ui.Column(section(0), sizing_mode='stretch_both', margin=(10, 15))

    def navigate(event):
        # MenuList reports the index path of the item, the menu is flat.
        index = event.new[0] if isinstance(event.new, tuple) and event.new else event.new
        if isinstance(index, int):
            main[:] = [section(index)]
    menu.param.watch(navigate, 'active')

    header = []
    if config.admin_password:
        logout = ui.IconButton(
            icon='logout', description='Log out of the admin panel', color='light'
        )
        # Resolved in the browser so the link survives proxies rewriting the path.
        logout.js_on_click(code=(
            "window.location.assign(window.location.pathname.replace(/\\/?$/, '/logout'))"
        ))
        header.extend([ui.HSpacer(), logout])

    return ui.Page(
        title=f"{page_theme.title or 'Panel'} Admin",
        header=header,
        sidebar=[menu],
        sidebar_width=240,
        main=[main],
        **_page_branding()
    )

def admin_panel(doc):
    with set_curdoc(doc):
        template = admin_template(doc)
        template.server_doc(doc)
    return doc
