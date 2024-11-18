from __future__ import annotations

import asyncio

from textual._xterm_parser import XTermParser
from textual.app import App
from textual.driver import Driver
from textual.events import Resize
from textual.geometry import Size


class PanelDriver(Driver):

    def __init__(self, app: App, /, **kwargs) -> None:
        super().__init__(app, **kwargs)
        self._terminal = app.__panel__._terminal
        self._input_initialized = False
        self._input_watcher = None
        self._size_watcher = None

    def _resize(self, *events):
        if not self._input_initialized:
            self.write("\x1b[?1049h")  # Alt screen

            self._enable_mouse_support()
            self.write("\x1b[?25l")  # Hide cursor
            self.write("\033[?1003h\n")
            self.flush()
            self._enable_bracketed_paste()
            self._input_initialized = True

        loop = asyncio.get_running_loop()
        textual_size = Size(self._terminal.ncols, self._terminal.nrows)
        event = Resize(textual_size, textual_size)
        asyncio.run_coroutine_threadsafe(
            self._app._post_message(event),
            loop=loop,
        )

    def _enable_bracketed_paste(self) -> None:
        """Enable bracketed paste mode."""
        self.write("\x1b[?2004h")

    def _disable_bracketed_paste(self) -> None:
        """Disable bracketed paste mode."""
        self.write("\x1b[?2004l")

    def _enable_mouse_support(self) -> None:
        """Enable reporting of mouse events."""
        write = self.write
        write("\x1b[?1000h")  # SET_VT200_MOUSE
        write("\x1b[?1003h")  # SET_ANY_EVENT_MOUSE
        write("\x1b[?1015h")  # SET_VT200_HIGHLIGHT_MOUSE
        write("\x1b[?1006h")  # SET_SGR_EXT_MODE_MOUSE

        # write("\x1b[?1007h")
        self.flush()

    def _disable_mouse_support(self) -> None:
        """Disable reporting of mouse events."""
        write = self.write
        write("\x1b[?1000l")  #
        write("\x1b[?1003l")  #
        write("\x1b[?1015l")
        write("\x1b[?1006l")
        self.flush()

    def _process_input(self, event):
        # Textual 0.86 changed from `process_event` to `process_message`
        fn = self.process_event if hasattr(self, 'process_event') else self.process_message
        for parsed_event in self._parser.feed(event.new):
            fn(parsed_event)

    def disable_input(self):
        if self._input_watcher is None:
            return
        self._terminal.param.unwatch(self._input_watcher)
        self._input_watcher = None

    def start_application_mode(self):
        self._size_watcher = self._terminal.param.watch(self._resize, ['nrows', 'ncols'])
        try:
            # Textual < 0.76
            self._parser = XTermParser(lambda: False, debug=self._debug)
        except TypeError:
            # Textual >= 0.76
            self._parser = XTermParser(debug=self._debug)
        self._input_watcher = self._terminal.param.watch(self._process_input, 'value')

    def stop_application_mode(self):
        self._terminal.param.unwatch(self._size_watcher)
        self._disable_bracketed_paste()
        self.disable_input()
        self.write("\x1b[?1049l" + "\x1b[?25h")
        self.flush()

    def write(self, data: str) -> None:
        self._terminal.write(data)

    def flush(self):
        self._terminal.flush()

    def close(self):
        pass
