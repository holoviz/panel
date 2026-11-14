"""
A Material Card holding a terminal that prints the logs of Panel callbacks.
"""
from __future__ import annotations

import logging

from io import StringIO

import param

from panel_material_ui.layout import Card, Row
from panel_material_ui.pane import Typography
from panel_material_ui.widgets import Chip, FileDownload, IconButton

from ...layout import HSpacer
from ...widgets.debugger import CheckFilter, TermFormatter
from ...widgets.terminal import Terminal


class _SessionFilter(CheckFilter):

    def filter(self, record):
        # Bokeh destroys a session's models before running its destroy hooks,
        # which log outside any session and so would reach every Debugger.
        models = [model for model, _ in self.debugger._models.values()]
        if models and all(m.document is None for m in models):
            return False
        return super().filter(record)


class Debugger(Card):
    """
    An uneditable Card holding a terminal that prints the logs of your
    callbacks. By default only exceptions are printed; to add your own logs
    use the `panel.callbacks` logger in your callbacks:
    `logger = logging.getLogger('panel.callbacks')`

    :Example:

    >>> Debugger(title='Debugger', level=logging.INFO)
    """

    _number_of_errors = param.Integer(bounds=(0, None), precedence=-1, doc="""
        Number of logged errors since last acknowledged.""")

    _number_of_warnings = param.Integer(bounds=(0, None), precedence=-1, doc="""
        Number of logged warnings since last acknowledged.""")

    _number_of_infos = param.Integer(bounds=(0, None), precedence=-1, doc="""
        Number of logged information since last acknowledged.""")

    collapsed = param.Boolean(default=True, doc="""
        Whether the contents of the Card are collapsed.""")

    formatter_args = param.Dict(
        default={'fmt': "%(asctime)s [%(name)s - %(levelname)s]: %(message)s"},
        precedence=-1, doc="""
        Arguments to pass to the logging formatter. See the standard
        python logging libraries.""")

    level = param.Integer(default=logging.ERROR, doc="""
        Logging level to print in the debugger terminal.""")

    logger_names = param.List(default=['panel'], item_type=str,
        bounds=(1, None), precedence=-1, doc="""
        Loggers which will be prompted in the debugger terminal.""")

    only_last = param.Boolean(default=True, doc="""
        Whether only the last stack is printed or the full.""")

    title = param.String(default='Debugger', doc="""
        The title displayed in the header of the Debugger.""")

    _rename = {
        '_number_of_errors': None, '_number_of_warnings': None,
        '_number_of_infos': None, 'formatter_args': None, 'level': None,
        'logger_names': None, 'only_last': None,
    }

    def __init__(self, **params):
        super().__init__(**params)
        # A stretching terminal would force its sizing onto the Card.
        fill = bool(self.height or 'both' in (self.sizing_mode or '') or 'height' in (self.sizing_mode or ''))
        self.terminal = Terminal(
            min_height=200, height=None if fill else 200, margin=0,
            sizing_mode='stretch_both' if fill else 'stretch_width',
            label=self.title
        )

        self.stream_handler = logging.StreamHandler(self.terminal)
        self.stream_handler.terminator = "  \n"
        self.stream_handler.setFormatter(
            TermFormatter(**self.formatter_args, only_last=self.only_last)
        )
        self.stream_handler.setLevel(self.level)
        log_filter = _SessionFilter()
        log_filter.add_debugger(self)
        self.stream_handler.addFilter(log_filter)
        self._attach_handler()

        self._title = Typography(self.title, variant='subtitle1', margin=(0, 10, 0, 0), align='center')
        self._chips = {
            count: Chip(color=color, size='small', visible=False, margin=(0, 2), align='center')
            for count, color in (
                ('_number_of_errors', 'error'),
                ('_number_of_warnings', 'warning'),
                ('_number_of_infos', 'info'),
            )
        }
        clear = IconButton(
            icon='delete_sweep', description='Acknowledge logs and clear',
            size='small', on_click=lambda _: self.terminal.clear()
        )
        self._save = FileDownload(
            callback=self._log_file, filename=self._filename, icon='download',
            icon_size='20px', label='', description='Save logs', color='default',
            variant='text', size='small', sx={'minWidth': 0}
        )
        self.header = Row(
            self._title, *self._chips.values(), HSpacer(), clear, self._save,
            sizing_mode='stretch_width', margin=0
        )
        self.append(self.terminal)

        # The Debugger owns its contents.
        self.param['objects'].constant = True

        self.param.watch(self.update_log_counts, list(self._chips))
        self.terminal.param.watch(self.acknowledge_errors, '_clears')

    def _attach_handler(self):
        for logger_name in self.logger_names:
            logging.getLogger(logger_name).addHandler(self.stream_handler)

    def _detach_handler(self):
        for logger_name in self.logger_names:
            logging.getLogger(logger_name).removeHandler(self.stream_handler)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        self._attach_handler()
        return super()._get_model(doc, root, parent, comm)

    def _cleanup(self, root=None):
        super()._cleanup(root)
        # Otherwise the loggers keep every discarded session's Debugger alive.
        if not self._models:
            self._detach_handler()

    @property
    def _filename(self) -> str:
        return f'{self.title or "debugger"}.txt'

    def _log_file(self) -> StringIO:
        return StringIO(self.terminal.output)

    def update_log_counts(self, *events):
        for count, chip in self._chips.items():
            n = getattr(self, count)
            label = count.split('_')[-1]
            chip.param.update(label=f'{n} {label[:-1] if n == 1 else label}', visible=bool(n))

    def acknowledge_errors(self, *events):
        self.param.update(_number_of_errors=0, _number_of_warnings=0, _number_of_infos=0)

    @param.depends('level', watch=True)
    def _update_level(self):
        self.stream_handler.setLevel(self.level)

    @param.depends('title', watch=True)
    def _update_title(self):
        self._title.object = self.title
        self._save.filename = self._filename
        self.terminal.label = self.title


__all__ = ("Debugger",)
