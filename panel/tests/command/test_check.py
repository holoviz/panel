import json
import sys

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


def test_check_threaded_onload_without_threads(app):
    result = check_app(app(
        "import panel as pn\n"
        "pn.panel('Hello').servable()\n"
        "pn.state.onload(lambda: None, threaded=True)\n"
    ))
    assert result['ok'] is False
    assert result['error']['type'] == 'RuntimeError'


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


def test_cli_json(app, monkeypatch, capsys):
    good = app("import panel as pn\nprint('noise')\npn.panel('Hello').servable()\n")
    bad = app("import panel as pn\n1 / 0\n", name='bad.py')
    assert run_cli(monkeypatch, '--json', good, bad) == 1
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
    try:
        assert run_cli(monkeypatch, '--num-threads', '2', path) == 0
    finally:
        config.nthreads = None


def test_cli_reports_path_as_given(app, monkeypatch, capsys, tmp_path):
    app("import panel as pn\n1 / 0\n")
    monkeypatch.chdir(tmp_path)
    assert run_cli(monkeypatch, 'app.py') == 1
    assert capsys.readouterr().out == 'app.py:2: ZeroDivisionError: division by zero\n'
