"""
Check that a Panel app runs the way it does under ``panel serve``.
"""
import asyncio
import faulthandler
import json
import multiprocessing
import os
import pathlib
import re
import tempfile
import traceback

from bokeh.command.subcommand import Argument, Subcommand
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop

from ..config import config
from ..io.application import build_single_handler_application
from ..io.server import get_server
from ..io.state import state

_FRAME = re.compile(r'^  File "(.+?)", line (\d+)')


def _error(etype: str, message: str, frames: list, path: str, text: str) -> dict:
    """
    Build an error record pointing at the innermost frame inside the
    app file, or the innermost frame overall. Frames run outermost first.
    """
    app_path = os.path.realpath(path)
    in_app = [line for file, line in frames if os.path.realpath(file) == app_path]
    if in_app:
        file, line = path, in_app[-1]
    else:
        file, line = frames[-1] if frames else (None, None)
    return {
        'type': etype,
        'message': message,
        'file': file,
        'line': None if line is None else int(line),
        'traceback': text,
    }


def _parse_traceback(text: str, path: str) -> dict:
    lines = text.rstrip().splitlines()
    frames = [(i, m.groups()) for i, line in enumerate(lines) if (m := _FRAME.match(line))]
    last = frames[-1][0] if frames else -1
    summary = '\n'.join(line for line in lines[last+1:] if line and not line[0].isspace())
    etype, _, message = summary.partition(': ')
    return _error(etype, message, [f for _, f in frames], path, text)


def _parse_dump(text: str, path: str, exitcode: int, timeout: float) -> dict:
    # faulthandler lists the most recent call first
    frames = [m.groups() for line in text.splitlines() if (m := _FRAME.match(line))][::-1]
    if text.startswith('Timeout'):
        return _error('Timeout', f'the app did not finish loading within {timeout}s', frames, path, text)
    message = text.splitlines()[0] if text else f'exit code {exitcode}'
    return _error('ProcessExited', message, frames, path, text)


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


def _check_in_child(conn, path: str, argv: list[str] | None, num_threads: int | None, timeout: float, dump_path: str) -> None:
    # Anything the app writes, even from C code, must stay out of the report
    os.dup2(2, 1)
    if num_threads is not None:
        config.nthreads = num_threads
    with open(dump_path, 'w') as dump:
        faulthandler.enable(dump)
        faulthandler.dump_traceback_later(timeout, exit=True, file=dump)
        try:
            result = check_app(path, argv)
        except BaseException as e:
            # sys.exit() or KeyboardInterrupt in the app escapes the handler
            error = _parse_traceback(''.join(traceback.format_exception(e)), path)
            result = {'file': path, 'ok': False, 'error': error}
        conn.send(result)


def check_app_isolated(
    path: str, argv: list[str] | None = None, timeout: float = 60, num_threads: int | None = None
) -> dict:
    """
    Run ``check_app`` in a fresh process, so apps cannot affect each
    other and a hanging or crashing app is reported with its location.
    """
    ctx = multiprocessing.get_context('spawn')
    receiver, sender = ctx.Pipe(duplex=False)
    with tempfile.TemporaryDirectory() as tmp:
        dump_path = os.path.join(tmp, 'dump')
        proc = ctx.Process(
            target=_check_in_child, args=(sender, path, argv, num_threads, timeout, dump_path)
        )
        proc.start()
        sender.close()
        try:
            result = receiver.recv()
        except EOFError:
            proc.join()
            # The child can die before it opens the dump, e.g. on a bad option
            dump = pathlib.Path(dump_path)
            text = dump.read_text() if dump.exists() else ''
            error = _parse_dump(text, path, proc.exitcode, timeout)
            result = {'file': path, 'ok': False, 'error': error}
        proc.join()
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
        ('--timeout', Argument(
            action  = 'store',
            type    = float,
            help    = "Seconds an app may take to load before it is reported as hanging",
            default = 60
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
        results = [
            check_app_isolated(path, args.args, args.timeout, args.num_threads)
            for path in args.files
        ]
        ok = all(r['ok'] for r in results)
        if args.json:
            report = json.dumps({'ok': ok, 'results': results}, indent=2)
        else:
            report = '\n'.join(_format(r) for r in results)
        print(report)  # noqa
        return ok
