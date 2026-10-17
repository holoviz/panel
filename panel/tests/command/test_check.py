import pytest

from panel.command.check import check_app


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


def test_check_missing_file(tmp_path):
    result = check_app(str(tmp_path / 'missing.py'))
    assert result['ok'] is False
    assert result['error']['type'] == 'ValueError'
