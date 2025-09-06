"""
The Debugger Widget is an uneditable Card that gives you feedback on errors
thrown by your Panel callbacks.
"""
from __future__ import annotations

import logging

from collections.abc import Mapping
from typing import ClassVar

import param

from ..io.resources import CDN_DIST
from ..io.state import state
from ..layout import Card, HSpacer, Row
from ..reactive import ReactiveHTML
from .terminal import Terminal


class TermFormatter(logging.Formatter):

    def __init__(self, *args, only_last=True, **kwargs):
        """
        Standard logging.Formatter with the default option of prompting
        only the last stack. Does not cache exc_text.

        Parameters
        ----------
        only_last : BOOLEAN, optional
            Whether the full stack trace or only the last file should be shown.
            The default is True.
        """
        super().__init__(*args, **kwargs)
        self.only_last = only_last

    def format(self, record):
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        exc_text = None
        if record.exc_info:
            exc_text = super().formatException(record.exc_info)
            last = exc_text.rfind('File')
            if last >0 and self.only_last:
                exc_text = exc_text[last:]
        if exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s


class CheckFilter(logging.Filter):

    def add_debugger(self, debugger):
        """
        Add a debugger to this logging filter.

        Parameters
        ----------
        widg : panel.widgets.Debugger
            The widget displaying the logs.

        Returns
        -------
        None.
        """
        self.debugger = debugger

    def _update_debugger(self, record):
        if not hasattr(self, 'debugger'):
            return
        if record.levelno >= 40:
            self.debugger._number_of_errors += 1
        elif 40 > record.levelno >= 30:
            self.debugger._number_of_warnings += 1
        elif record.levelno < 30:
            self.debugger._number_of_infos += 1

    def filter(self,record):
        """
        Will filter out messages coming from a different bokeh document than
        the document where the debugger is embedded in server mode.
        Returns True if no debugger was added.
        """
        if not hasattr(self, 'debugger'):
            return True


        if state.curdoc and state.curdoc.session_context:
            session_id = state.curdoc.session_context.id
            widget_session_ids = {m.document.session_context.id
                                     for m in sum(self.debugger._models.values(),
                                                  tuple()) if m.document.session_context}

            if session_id not in widget_session_ids:
                return False
        self._update_debugger(record)
        return True


class DebuggerButtons(ReactiveHTML):

    terminal_output = param.String(doc="""
        The output of the terminal, which is updated by the debugger widget.""")

    debug_name = param.String(doc="""
        The name of the debugger, used to save the terminal output to a file.""")

    clears = param.Integer(default=0, doc="""
        The number of times the terminal has been cleared.""")

    _template: ClassVar[str] = """
    <div style="display: flex;">
      <button class="special_btn clear_btn" id="clear_btn" onclick="${script('click_clear')}" style="width: ${model.width}px;">
        <span class="shown">☐</span>
        <span class="tooltiptext">Acknowledge logs and clear</span>
      </button>
      <button class="special_btn" id="save_btn" onclick="${script('click')}" style="width: ${model.width}px;">💾
        <span class="tooltiptext">Save logs</span>
      </button>
    </div>
    """

    js_cb: ClassVar[str] = """
        var filename = data.debug_name+'.txt'
        console.log('saving debugger terminal output to '+filename)
        var blob = new Blob([data.terminal_output],
            { type: "text/plain;charset=utf-8" });
        if (navigator.msSaveBlob) {
            navigator.msSaveBlob(blob, filename);
        } else {
            var link = document.createElement('a');
            var url = URL.createObjectURL(blob);
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            setTimeout(function() {
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
            }, 0);
        }
        """

    _scripts: ClassVar[dict[str, str | list[str]]] = {
        'click': js_cb,
        'click_clear': "data.clears += 1"
    }

    _dom_events: ClassVar[dict[str, list[str]]] = {'clear_btn': ['click']}


class Debugger(Card):
    """
    A uneditable Card layout holding a terminal printing out logs from your
    callbacks. By default, it will only print exceptions. If you want to add
    your own log, use the `panel.callbacks` logger within your callbacks:
    `logger = logging.getLogger('panel.callbacks')`
    """

    _number_of_errors = param.Integer(bounds=(0, None), precedence=-1, doc="""
        Number of logged errors since last acknowledged.""")

    _number_of_warnings = param.Integer(bounds=(0, None), precedence=-1, doc="""
        Number of logged warnings since last acknowledged.""")

    _number_of_infos = param.Integer(bounds=(0, None), precedence=-1, doc="""
        Number of logged information since last acknowledged.""")

    only_last = param.Boolean(default=True, doc="""
        Whether only the last stack is printed or the full.""")

    level = param.Integer(default=logging.ERROR, doc="""
        Logging level to print in the debugger terminal.""")

    formatter_args = param.Dict(
        default={'fmt': "%(asctime)s [%(name)s - %(levelname)s]: %(message)s"},
        precedence=-1, doc="""
        Arguments to pass to the logging formatter. See the standard
        python logging libraries.""")

    logger_names = param.List(default=['panel'], item_type=str,
        bounds=(1, None), precedence=-1, doc="""
        Loggers which will be prompted in the debugger terminal.""")

    _rename: ClassVar[Mapping[str, str | None]] = dict(
        Card._rename,
        _number_of_errors=None,
        _number_of_warnings=None,
        _number_of_infos=None,
        only_last=None,
        level=None,
        formatter_args=None,
        logger_names=None
    )

    _stylesheets: ClassVar[list[str]] = [f'{CDN_DIST}css/debugger.css']

    def __init__(self, **params):
        super().__init__(**params)
        #change default css
        self.button_css_classes = ['debugger-card-button']
        self.css_classes = ['debugger-card']
        self.header_css_classes = ['debugger-card-header']
        self.title_css_classes = ['debugger-card-title']

        smode = 'stretch_width' if self.height else 'stretch_both'
        height = self.height or self.min_height
        terminal = Terminal(
            min_height=200, sizing_mode=smode, name=self.name,
            margin=0, height=(height-70) if height else None
        )

        stream_handler = logging.StreamHandler(terminal)
        stream_handler.terminator = "  \n"

        formatter = TermFormatter(
            **self.formatter_args,
            only_last=self.only_last
        )

        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(self.level)
        curr_filter = CheckFilter()

        curr_filter.add_debugger(self)

        stream_handler.addFilter(curr_filter)

        for logger_name in self.logger_names:
            logger = logging.getLogger(logger_name)
            logger.addHandler(stream_handler)

        self.terminal = terminal
        self.stream_handler = stream_handler

        #callbacks for header
        self.param.watch(self.update_log_counts,'_number_of_errors')
        self.param.watch(self.update_log_counts,'_number_of_warnings')
        self.param.watch(self.update_log_counts,'_number_of_infos')

        # Buttons
        self.btns = DebuggerButtons(stylesheets=self._stylesheets)
        inc = """
        target.data.terminal_output += source.output
        """
        clr = """
        target.data.terminal_output = ''
        """
        self.terminal.jslink(self.btns, code={'_output': inc})
        self.terminal.jslink(self.btns, code={'_clears': clr})
        self.btns.jslink(self.terminal, clears='_clears')
        self.terminal.param.watch(self.acknowledge_errors, ['_clears'])

        self.jslink(self.btns, name='debug_name')

        #set header
        self.title = ''

        #body
        self.append(
            Row(
                f'### {self.name}', HSpacer(), self.btns,
                sizing_mode='stretch_width', align=('end','start')
            )
        )
        self.append(terminal)

        #make it an uneditable card
        self.param['objects'].constant = True

        #by default it should be collapsed and small.
        self.collapsed = True

    def update_log_counts(self, event):
        title = []
        if self._number_of_errors:
            title.append(f'<span style="color:rgb(190,0,0);">errors: </span>{self._number_of_errors}')
        if self._number_of_warnings:
            title.append(f'<span style="color:rgb(190,160,20);">w: </span>{self._number_of_warnings}')
        if self._number_of_infos:
            title.append(f'i: {self._number_of_infos}')

        self.title = ', '.join(title)

    def acknowledge_errors(self, event):
        self._number_of_errors = 0
        self._number_of_warnings = 0
        self._number_of_infos = 0

    @param.depends("level", watch=True)
    def _update_level(self):
        self.stream_handler.setLevel(self.level)
