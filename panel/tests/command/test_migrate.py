"""
CLI-level tests for `panel migrate` (plan §10.1).
"""
import argparse
import pathlib
import subprocess
import sys

import pytest

pytest.importorskip("libcst")

from panel.command.migrate import Migrate

CWD = pathlib.Path(__file__).parent


def _invoke(paths, check=False, diff=False):
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    subparser = subs.add_parser(Migrate.name)
    subcommand = Migrate(parser=subparser)
    args = parser.parse_args([Migrate.name, *paths, *(['--check'] if check else []), *(['--diff'] if diff else [])])
    return subcommand.invoke(args)


def test_migrate_rewrites_file_in_place(py_file):
    py_file.write("import panel as pn\npn.widgets.Button(name='Click me')\n")
    py_file.flush()

    ret = _invoke([py_file.name])
    assert ret == 0

    content = pathlib.Path(py_file.name).read_text()
    assert "pnui.Button(label='Click me')" in content
    assert 'import panel.ui as pnui' in content


def test_migrate_check_reports_without_modifying(py_file):
    original = "import panel as pn\npn.widgets.Button(name='Click me')\n"
    py_file.write(original)
    py_file.flush()

    ret = _invoke([py_file.name], check=True)
    assert ret != 0
    assert pathlib.Path(py_file.name).read_text() == original


def test_migrate_check_is_clean_exit_when_nothing_to_change(py_file):
    original = "import panel as pn\nprint('hello')\n"
    py_file.write(original)
    py_file.flush()

    ret = _invoke([py_file.name], check=True)
    assert ret == 0
    assert pathlib.Path(py_file.name).read_text() == original


def test_migrate_diff_prints_unified_diff_and_does_not_modify(py_file, capsys):
    original = "import panel as pn\npn.widgets.Button(name='Click me')\n"
    py_file.write(original)
    py_file.flush()

    ret = _invoke([py_file.name], diff=True)
    assert ret == 0
    out = capsys.readouterr().out
    assert '-pn.widgets.Button' in out
    assert '+pnui.Button' in out
    assert pathlib.Path(py_file.name).read_text() == original


def test_migrate_directory_argument_is_walked_recursively(tmp_path):
    sub = tmp_path / 'sub'
    sub.mkdir()
    (tmp_path / 'top.py').write_text("import panel as pn\npn.widgets.Button(name='Top')\n")
    (sub / 'nested.py').write_text("import panel as pn\npn.widgets.Button(name='Nested')\n")
    (sub / '__pycache__').mkdir()
    (sub / '__pycache__' / 'ignored.py').write_text("this is not valid python (")
    (tmp_path / 'not_python.txt').write_text('ignore me')

    ret = _invoke([str(tmp_path)])
    assert ret == 0

    assert "pnui.Button(label='Top')" in (tmp_path / 'top.py').read_text()
    assert "pnui.Button(label='Nested')" in (sub / 'nested.py').read_text()


def test_migrate_command_subprocess_smoke(py_file):
    py_file.write("import panel as pn\npn.widgets.Button(name='Click me')\n")
    py_file.flush()

    cmd = [sys.executable, "-m", "panel", "migrate", py_file.name]
    p = subprocess.run(cmd, cwd=CWD, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    content = pathlib.Path(py_file.name).read_text()
    assert "pnui.Button(label='Click me')" in content


def test_migrate_file_with_syntax_error_reports_and_exits_non_zero(py_file, capsys):
    original = "def broken(:\n    pass\n"
    py_file.write(original)
    py_file.flush()

    ret = _invoke([py_file.name])
    assert ret != 0

    out = capsys.readouterr().out
    assert 'could not be parsed' in out
    assert py_file.name in out
    # The unparsable file must be left untouched.
    assert pathlib.Path(py_file.name).read_text() == original


def test_migrate_check_mode_exits_non_zero_on_syntax_error(py_file):
    original = "def broken(:\n    pass\n"
    py_file.write(original)
    py_file.flush()

    ret = _invoke([py_file.name], check=True)
    assert ret != 0


def test_migrate_diff_mode_exits_non_zero_on_syntax_error(py_file):
    original = "def broken(:\n    pass\n"
    py_file.write(original)
    py_file.flush()

    ret = _invoke([py_file.name], diff=True)
    assert ret != 0


def test_migrate_directory_with_one_bad_file_still_migrates_the_rest(tmp_path, capsys):
    """
    A file that fails to parse must not abort the whole run: every other
    valid file in the batch is still migrated, and the bad file is reported
    by name rather than silently skipped, with a non-zero overall exit code.
    """
    good = tmp_path / 'good.py'
    bad = tmp_path / 'bad.py'
    good.write_text("import panel as pn\npn.widgets.Button(name='Click me')\n")
    bad.write_text("def broken(:\n    pass\n")

    ret = _invoke([str(tmp_path)])
    assert ret != 0

    assert "pnui.Button(label='Click me')" in good.read_text()
    assert bad.read_text() == "def broken(:\n    pass\n"

    out = capsys.readouterr().out
    assert 'Files that could not be parsed' in out
    assert str(bad) in out
