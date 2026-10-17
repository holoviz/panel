"""
Check that a Panel app runs the way it does under ``panel serve``.
"""
import asyncio
import json
import os
import re
import sys
import traceback

from contextlib import redirect_stdout

from bokeh.command.subcommand import Argument, Subcommand
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop

from ..config import config
from ..io.application import build_single_handler_application
from ..io.server import get_server
from ..io.state import state

_FRAME = re.compile(r'^  File "(.+?)", line (\d+)')


def _parse_traceback(text: str, path: str) -> dict:
    """
    Turn a formatted traceback into an error record pointing at the
    deepest frame inside the app file, or the deepest frame overall.
    """
    lines = text.rstrip().splitlines()
    frames = [(i, m) for i, line in enumerate(lines) if (m := _FRAME.match(line))]
    last = frames[-1][0] if frames else -1
    summary = '\n'.join(line for line in lines[last+1:] if line and not line[0].isspace())
    etype, _, message = summary.partition(': ')
    app_path = os.path.realpath(path)
    in_app = [m for _, m in frames if os.path.realpath(m[1]) == app_path]
    frame = (in_app or [m for _, m in frames] or [None])[-1]
    return {
        'type': etype,
        'message': message,
        'file': path if in_app else frame[1] if frame else None,
        'line': int(frame[2]) if frame else None,
        'traceback': text,
    }


def _format(result: dict) -> str:
    if (error := result['error']) is None:
        return f"{result['file']}: ok"
    location = error['file'] or result['file']
    if error['line'] is not None:
        location += f":{error['line']}"
    return f"{location}: {error['type']}: {error['message']}"


def check_app(path: str, argv: list[str] | None = None) -> dict:
    """
    Serve the app at ``path`` on a local port, request it once and
    report whether the session ran and published any content.
    """
    result = {'file': path, 'ok': False, 'error': None}
    try:
        app = build_single_handler_application(path, argv)
    except Exception as e:
        result['error'] = _parse_traceback(''.join(traceback.format_exception_only(e)), path)
        return result

    result['error'] = asyncio.run(_serve_once(app, path))
    result['ok'] = result['error'] is None
    return result


async def _serve_once(app, path: str) -> dict | None:
    server = get_server({'app': app}, port=0, address='127.0.0.1', loop=IOLoop.current(), start=False)
    server.start()
    try:
        response = await AsyncHTTPClient().fetch(
            f'http://127.0.0.1:{server.port}/app', raise_error=False
        )
        handler = app.handlers[0]
        sessions = server.get_sessions('/app')
        if handler.failed:
            return _parse_traceback(handler.error_detail, path)
        elif response.code != 200:
            return _parse_traceback(f'HTTPError: {response.code} {response.reason}', path)
        elif not sessions or not sessions[0].document.roots:
            return _parse_traceback('EmptyApp: the app did not mark anything as servable', path)
        # A browser would now connect and run the pn.state.onload callbacks.
        # Errors in async callbacks only surface once their task is
        # collected, so only sync callbacks and scheduling errors are caught.
        errors = []
        with config.param.update(exception_handler=errors.append):
            try:
                state._on_load(sessions[0].document)
            except Exception as e:
                errors.append(e)
        if errors:
            return _parse_traceback(''.join(traceback.format_exception(errors[0])), path)
        return None
    finally:
        server.stop()
        server.unlisten()


class Check(Subcommand):
    ''' Subcommand to run Panel apps as ``panel serve`` would and report errors.

    '''

    name = "check"

    help = "Run apps as 'panel serve' would and report the file and line of any error."

    args = (
        ('files', Argument(
            metavar = 'DIRECTORY-OR-SCRIPT',
            nargs   = '+',
            help    = "The app directories or scripts to check",
        )),
        ('--json', Argument(
            action  = 'store_true',
            help    = "Print the results as JSON",
        )),
        ('--num-threads', Argument(
            action  = 'store',
            type    = int,
            help    = "Thread pool size, as passed to 'panel serve'",
            default = None
        )),
        ('--args', Argument(
            metavar = 'COMMAND-LINE-ARGS',
            nargs   = "...",
            help    = "Command line arguments passed on to the applications",
        )),
    )

    def invoke(self, args):
        if args.num_threads is not None:
            config.nthreads = args.num_threads
        results = []
        for path in args.files:
            # App output must not end up in the report, e.g. in the JSON
            with redirect_stdout(sys.stderr):
                results.append(check_app(path, args.args))
        ok = all(r['ok'] for r in results)
        if args.json:
            report = json.dumps({'ok': ok, 'results': results}, indent=2)
        else:
            report = '\n'.join(_format(r) for r in results)
        print(report)  # noqa
        return ok
