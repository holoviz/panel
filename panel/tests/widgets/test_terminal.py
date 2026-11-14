"""This module contains tests of the Terminal"""
# pylint: disable=missing-function-docstring,protected-access
import logging
import sys
import time
import uuid

import pytest

import panel as pn

from panel.tests.util import not_osx, not_windows


def test_terminal_constructor():
    terminal = pn.widgets.Terminal()
    terminal.write("Hello")

    assert repr(terminal).startswith("Terminal(")

def test_terminal(document, comm):
    terminal = pn.widgets.Terminal("Hello")
    terminal.write(" World!")

    model = terminal.get_root(document, comm)

    assert model.output == "Hello World!"

    terminal.clear()

    assert model._clears == 1
    assert terminal.output == ""

    model2 = terminal.get_root(document, comm)

    assert model2.output == ""

@not_windows
@not_osx
@pytest.mark.subprocess
async def test_subprocess():
    args = "bash"
    terminal = pn.widgets.Terminal()

    subprocess = terminal.subprocess
    subprocess.args = args

    assert subprocess._terminal == terminal
    assert subprocess.args == args
    assert not subprocess.running
    assert repr(subprocess).startswith("TerminalSubprocess(")

    subprocess.run()
    assert subprocess.running
    assert subprocess._child_pid
    assert subprocess._fd  # file descriptor

    subprocess.kill()
    assert not subprocess.running
    assert subprocess._child_pid == 0
    assert subprocess._fd == 0

@not_windows
@not_osx
@pytest.mark.subprocess
async def test_run_list_args():
    terminal = pn.widgets.Terminal()
    subprocess = terminal.subprocess
    subprocess.args = ["ls", "-l"]
    subprocess.run()
    count = 0
    while not subprocess.running and count < 10:
        time.sleep(0.1)
        count += 1
    assert subprocess.running
    subprocess.kill()

_SCRIPT = """
import atexit, os, sys, time, warnings
import panel as pn

marker = sys.argv[1]
atexit.register(lambda: open(marker, 'a').write(f'{os.getpid()}\\n'))

terminal = pn.widgets.Terminal()
sub = terminal.subprocess
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    sub.run(*eval(sys.argv[2]), **eval(sys.argv[3]))
print('WARNINGS', [str(w.message) for w in caught])
for _ in range(100):
    sub._forward_subprocess_output_to_terminal()
    if not sub.running:
        break
    time.sleep(0.05)
print('RUNNING' if sub.running else 'DONE', repr(terminal.output))
"""


def _run_script(tmp_path, args, kwargs=None):
    import os
    import subprocess

    marker = tmp_path / 'marker'
    env = {**os.environ, 'PYTHONPATH': os.pathsep.join(sys.path)}
    proc = subprocess.run(
        [sys.executable, '-c', _SCRIPT, str(marker), repr(args), repr(kwargs or {})],
        capture_output=True, text=True, timeout=60, env=env
    )
    assert proc.returncode == 0, proc.stderr
    pids = marker.read_text().split() if marker.exists() else []
    return proc.stdout.strip(), pids


@not_windows
@pytest.mark.subprocess
def test_subprocess_child_does_not_run_parent_atexit_handlers(tmp_path):
    out, pids = _run_script(tmp_path, [sys.executable, '-c', 'print("hello")'])
    assert "DONE" in out
    assert 'hello' in out
    assert len(pids) == 1


@not_windows
@pytest.mark.subprocess
def test_subprocess_failed_exec_does_not_run_parent_code(tmp_path):
    out, pids = _run_script(tmp_path, ['this-command-does-not-exist'])
    assert "DONE" in out
    assert 'this-command-does-not-exist' in out or 'No such file' in out
    assert len(pids) == 1


@not_windows
@pytest.mark.subprocess
def test_subprocess_cwd_env_and_shell(tmp_path):
    out, pids = _run_script(
        tmp_path, ['echo $PWD-$FOO'],
        {'shell': True, 'cwd': str(tmp_path), 'env': {'FOO': 'bar', 'PATH': '/bin:/usr/bin'}}
    )
    assert "DONE" in out
    assert f'{tmp_path.resolve()}-bar' in out.replace('\\r', '').replace(str(tmp_path), str(tmp_path.resolve()))
    assert len(pids) == 1


@not_windows
@pytest.mark.subprocess
def test_subprocess_unsupported_kwargs_warn(tmp_path):
    out, pids = _run_script(tmp_path, [sys.executable, '-c', 'print("hello")'], {'timeout': 1})
    assert 'timeout' in out.splitlines()[0]
    assert 'DONE' in out
    assert 'hello' in out
    assert len(pids) == 1


def test_cannot_assign_string_args_with_spaces():
    terminal = pn.widgets.Terminal()
    subprocess = terminal.subprocess
    with pytest.raises(ValueError):
        subprocess.args = "ls -l"


def write_to_terminal(term):
    term.write("This is written directly to the terminal.\n")


def print_to_terminal(term):
    sys.stdout = term
    print("This print statement is redirected from stdout to the Panel Terminal")  # noqa: T201

    sys.stdout = sys.__stdout__
    print("This print statement is again redirected to the server console")  # noqa: T201


def get_logger(term):
    logger = logging.getLogger("terminal")
    logger.setLevel(logging.DEBUG)

    stream_handler = logging.StreamHandler(term)
    stream_handler.terminator = "  \n"
    formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")

    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    return logger


def _special_characters(term, iterations=1):
    for _ in range(iterations):
        term.write("Danish Characters: æøåÆØÅ\n")
        term.write("Emoji: Python 🐍  Panel ❤️  LOL 😊 \n")
        term.write("Links: https://awesome-panel.org\n")


def get_app():
    pn.config.sizing_mode = "stretch_width"
    terminal = pn.widgets.Terminal(
        object="Welcome to the Panel Terminal!\nI'm based on xterm.js\n\n",
        height=400,
        width=800,
        sizing_mode="stretch_width",
        options={"cursorBlink": True},
    )

    write_to_terminal_button = pn.widgets.Button(
        label="Write to the Terminal", color="primary"
    )
    write_to_terminal_button.on_click(lambda x: write_to_terminal(terminal))

    special_characters_button = pn.widgets.Button(
        label="Write special to the Terminal", color="primary"
    )
    special_characters_button.on_click(lambda x: _special_characters(terminal))

    print_to_terminal_button = pn.widgets.Button(
        label="Print to Terminal", color="primary"
    )
    print_to_terminal_button.on_click(lambda x: print_to_terminal(terminal))

    logger = get_logger(terminal)
    log_button = pn.widgets.Button(label="Log", color="primary")
    log_button.on_click(lambda x: logger.info("Hello Info Logger"))

    stream_button = pn.widgets.Button(label="Stream", color="primary")
    stream_button.on_click(lambda x: [logger.info(uuid.uuid4()) for i in range(300)])

    run_ls_in_subprocess_button = pn.widgets.Button(
        label="Run ls in subprocess", color="primary"
    )
    run_ls_in_subprocess_button.on_click(lambda x: terminal.subprocess.run(args="ls"))

    run_ls_l_in_subprocess_button = pn.widgets.Button(
        label="Run ls -l in subprocess", color="primary"
    )
    run_ls_l_in_subprocess_button.on_click(
        lambda x: terminal.subprocess.run("ls", "-l")
    )

    run_bash_in_subprocess_button = pn.widgets.Button(
        label="Run bash in subprocess", color="primary"
    )
    run_bash_in_subprocess_button.on_click(
        lambda x: terminal.subprocess.run("bash")
    )

    template = pn.template.FastListTemplate(title="Panel - Terminal - PR in Progress!")

    template.main[:] = [
        pn.Column(
            pn.pane.Markdown("#### Terminal"),
            terminal,
            pn.Param(
                terminal,
                parameters=[
                    "value",
                    "object",
                    "write_to_console",
                    "clear",
                    "width",
                    "height",
                    "sizing_mode",
                ],
                widgets={
                    "width": {
                        "widget_type": pn.widgets.IntSlider,
                        "start": 0,
                        "end": 1000,
                    },
                    "height": {
                        "widget_type": pn.widgets.IntSlider,
                        "start": 0,
                        "end": 1000,
                    },
                },
            ),
            pn.Param(
                terminal.subprocess,
                parameters=["kill", "running", "_period"],
                name="Subprocess",
            ),
        )
    ]
    template.sidebar[:] = [
        pn.pane.Markdown("#### Tests"),
        write_to_terminal_button,
        special_characters_button,
        print_to_terminal_button,
        log_button,
        stream_button,
        run_ls_in_subprocess_button,
        run_ls_l_in_subprocess_button,
        run_bash_in_subprocess_button,
    ]
    return template


if pn.state.served:
    get_app().servable()


def test_terminal_writes_are_not_combined_away_by_a_hold(document):
    terminal = pn.widgets.Terminal()
    model = terminal.get_root(document)
    document.add_root(model)

    document.hold('combine')
    terminal.write('first ')
    terminal.write('second')
    assert model.output == 'first second'
    document.unhold()

    terminal.write('third')
    assert model.output == 'third'
    assert terminal.output == 'first secondthird'
