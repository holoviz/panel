import json
import sys
import time

import nbformat
import pytest

from panel.command import main
from panel.command.check import check_app
from panel.config import config


@pytest.fixture
def app(tmp_path):
    def write(source, name='app.py'):
        path = tmp_path / name
        path.write_text(source)
        return str(path)
    return write


def test_check_good_app(app):
    result = check_app(app("import panel as pn\npn.panel('Hello').servable()\n"))
    assert result['ok'] is True
    assert result['error'] is None


def test_check_crash_reports_script_line(app):
    app("def boom():\n    return 1 / 0\n", name='helper.py')
    result = check_app(app("import panel as pn\nfrom helper import boom\nboom()\n"))
    error = result['error']
    assert result['ok'] is False
    assert error['type'] == 'ZeroDivisionError'
    assert error['message'] == 'division by zero'
    assert error['file'].endswith('app.py')
    assert error['line'] == 3


def test_check_syntax_error(app):
    result = check_app(app("import panel as pn\nx = (\n"))
    assert result['ok'] is False
    assert result['error']['type'] == 'SyntaxError'
    assert result['error']['line'] == 2


def test_check_empty_app(app):
    result = check_app(app("import panel as pn\npn.panel('Hello')\n"))
    assert result['ok'] is False
    assert result['error']['type'] == 'EmptyApp'


def test_check_template_app(app):
    result = check_app(app(
        "import panel as pn\n"
        "pn.template.FastListTemplate(main=[pn.pane.Markdown('x')]).servable()\n"
    ))
    assert result['ok'] is True


def test_check_onload_error(app):
    result = check_app(app(
        "import panel as pn\n"
        "pn.panel('Hello').servable()\n"
        "pn.state.onload(lambda: 1 / 0)\n"
    ))
    assert result['ok'] is False
    assert result['error']['type'] == 'ZeroDivisionError'
    assert result['error']['line'] == 3


def test_check_async_onload_error(app):
    result = check_app(app(
        "import asyncio\n"
        "import panel as pn\n"
        "pn.panel('Hello').servable()\n"
        "async def load():\n"
        "    await asyncio.sleep(0.1)\n"
        "    1 / 0\n"
        "pn.state.onload(load)\n"
    ))
    assert result['error']['type'] == 'ZeroDivisionError'
    assert result['error']['line'] == 6


def test_check_threaded_onload_without_threads(app):
    result = check_app(app(
        "import panel as pn\n"
        "pn.panel('Hello').servable()\n"
        "pn.state.onload(lambda: None, threaded=True)\n"
    ))
    assert result['ok'] is False
    assert result['error']['type'] == 'RuntimeError'


def test_check_exception_group(app):
    result = check_app(app(
        "import panel as pn\n"
        "try:\n"
        "    {}['k']\n"
        "except KeyError as e:\n"
        "    raise ExceptionGroup('many', [e, ValueError('v')])\n"
    ))
    assert result['error']['type'] == 'ExceptionGroup'
    assert result['error']['message'] == 'many (2 sub-exceptions)'
    assert result['error']['line'] == 5


def test_check_http_error(app, monkeypatch):
    monkeypatch.setattr('panel.io.server.DocHandler.get', _respond_500)
    result = check_app(app("import panel as pn\npn.panel('Hello').servable()\n"))
    assert result['error']['type'] == 'HTTPError'
    assert result['error']['message'].startswith('500')


async def _respond_500(self, *args, **kwargs):
    self.send_error(500)


def test_check_markdown_reports_source_line(app):
    path = app("# Title\n\n```python\nimport panel as pn\npn.panel(1 / 0).servable()\n```\n", name='app.md')
    error = check_app(path)['error']
    assert (error['type'], error['line'], error['cell']) == ('ZeroDivisionError', 5, None)


def notebook(app, *sources):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_markdown_cell('Intro')] + [nbformat.v4.new_code_cell(s) for s in sources]
    return app(nbformat.writes(nb), name='app.ipynb')


def test_check_notebook_reports_cell_and_line(app):
    path = notebook(app, "import panel as pn", "x = 1\n{}['k']\npn.panel(x).servable()")
    error = check_app(path)['error']
    assert (error['type'], error['cell'], error['line']) == ('KeyError', 3, 2)


def test_check_notebook_reports_last_expression(app):
    path = notebook(app, "import panel as pn", "x = 0\npn.panel(1 / x)")
    error = check_app(path)['error']
    assert (error['type'], error['cell'], error['line']) == ('ZeroDivisionError', 3, 2)


def test_check_missing_file(tmp_path):
    result = check_app(str(tmp_path / 'missing.py'))
    assert result['ok'] is False
    assert result['error']['type'] == 'ValueError'


def run_cli(monkeypatch, *args):
    monkeypatch.setattr(sys, 'argv', ['panel', 'check', *args])
    try:
        main()
    except SystemExit as e:
        return e.code
    return 0


def test_cli_good_exits_zero(app, monkeypatch, capsys):
    path = app("import panel as pn\npn.panel('Hello').servable()\n")
    assert run_cli(monkeypatch, path) == 0
    assert capsys.readouterr().out == f'{path}: ok\n'


def test_cli_crash_exits_one(app, monkeypatch, capsys):
    path = app("import panel as pn\n\n1 / 0\n")
    assert run_cli(monkeypatch, path) == 1
    assert capsys.readouterr().out == f'{path}:3: ZeroDivisionError: division by zero\n'


def test_cli_prints_one_line_per_app(app, monkeypatch, capsys):
    path = app("import panel as pn\nraise ValueError('first\\nsecond')\n")
    assert run_cli(monkeypatch, path) == 1
    assert capsys.readouterr().out == f'{path}:2: ValueError: first\n'


def test_cli_json(app, monkeypatch, capsys):
    good = app("import panel as pn\nprint('noise')\npn.panel('Hello').servable()\n")
    bad = app("import panel as pn\n1 / 0\n", name='bad.py')
    assert run_cli(monkeypatch, '--json', '--jobs', '1', good, bad) == 1
    output = json.loads(capsys.readouterr().out)
    assert output['ok'] is False
    assert [r['ok'] for r in output['results']] == [True, False]
    assert output['results'][1]['error']['line'] == 2


def test_cli_num_threads_allows_threaded_onload(app, monkeypatch):
    path = app(
        "import panel as pn\n"
        "pn.panel('Hello').servable()\n"
        "pn.state.onload(lambda: None, threaded=True)\n"
    )
    assert run_cli(monkeypatch, '--num-threads', '2', path) == 0
    assert config.nthreads is None


def test_cli_threaded_onload_error(app, monkeypatch, capsys):
    path = app(
        "import time\n"
        "import panel as pn\n"
        "pn.panel('Hello').servable()\n"
        "def load():\n"
        "    time.sleep(0.2)\n"
        "    1 / 0\n"
        "pn.state.onload(load, threaded=True)\n"
    )
    assert run_cli(monkeypatch, '--num-threads', '2', path) == 1
    assert capsys.readouterr().out == f'{path}:6: ZeroDivisionError: division by zero\n'


def test_cli_timeout_reports_hanging_line(app, monkeypatch, capsys):
    path = app("import time\n\ntime.sleep(60)\n")
    assert run_cli(monkeypatch, '--timeout', '1', path) == 1
    assert capsys.readouterr().out.startswith(f'{path}:3: Timeout: ')


def test_cli_kills_app_past_deadline(app, monkeypatch, capsys):
    path = app("import faulthandler\nimport time\nfaulthandler.cancel_dump_traceback_later()\ntime.sleep(60)\n")
    assert run_cli(monkeypatch, '--timeout', '1', path) == 1
    assert capsys.readouterr().out.startswith(f'{path}: Timeout: ')


def test_cli_does_not_wait_for_leftover_threads(app, monkeypatch):
    path = app(
        "import threading\nimport time\nimport panel as pn\n"
        "threading.Thread(target=time.sleep, args=(60,)).start()\n"
        "pn.panel('Hello').servable()\n"
    )
    start = time.monotonic()
    assert run_cli(monkeypatch, '--timeout', '30', path) == 0
    assert time.monotonic() - start < 20


def test_cli_reports_hard_crash(app, monkeypatch, capsys):
    path = app("import ctypes\n\nctypes.string_at(0)\n")
    assert run_cli(monkeypatch, path) == 1
    assert capsys.readouterr().out.startswith(f'{path}:3: ProcessExited: Fatal Python error')


def test_cli_reports_exit_code(app, monkeypatch, capsys):
    path = app("import os\nos._exit(3)\n")
    assert run_cli(monkeypatch, path) == 1
    assert capsys.readouterr().out == f'{path}: ProcessExited: exit code 3\n'


def test_cli_reports_sys_exit_line(app, monkeypatch, capsys):
    path = app("import sys\n\nsys.exit(2)\n")
    assert run_cli(monkeypatch, path) == 1
    assert capsys.readouterr().out == f'{path}:3: SystemExit: 2\n'


def test_cli_json_ignores_low_level_output(app, monkeypatch, capsys):
    path = app("import os\nimport panel as pn\nos.write(1, b'noise')\npn.panel('Hello').servable()\n")
    assert run_cli(monkeypatch, '--json', path) == 0
    assert json.loads(capsys.readouterr().out)['ok'] is True


def test_cli_reports_child_failure_before_check(app, monkeypatch, capsys):
    path = app("import panel as pn\npn.panel('Hello').servable()\n")
    assert run_cli(monkeypatch, '--num-threads', '-1', path) == 1
    assert capsys.readouterr().out == f'{path}: ProcessExited: exit code 1\n'


def test_cli_runs_apps_in_isolation(app, monkeypatch):
    first = app("import sys\nimport panel as pn\nsys.leaked = 1\npn.panel('a').servable()\n", name='first.py')
    second = app("import sys\nimport panel as pn\nassert 'leaked' not in vars(sys)\npn.panel('b').servable()\n", name='second.py')
    assert run_cli(monkeypatch, first, second) == 0


def test_cli_reports_path_as_given(app, monkeypatch, capsys, tmp_path):
    app("import panel as pn\n1 / 0\n")
    monkeypatch.chdir(tmp_path)
    assert run_cli(monkeypatch, 'app.py') == 1
    assert capsys.readouterr().out == 'app.py:2: ZeroDivisionError: division by zero\n'
