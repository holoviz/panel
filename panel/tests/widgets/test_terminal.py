"""This module contains tests of the Terminal"""
# pylint: disable=missing-function-docstring,protected-access
import logging
import sys
import time
import uuid

import pytest

import panel as pn

not_windows = pytest.mark.skipif(sys.platform == 'win32', reason="Does not work on Windows")


def test_terminal_constructor():
    terminal = pn.widgets.Terminal()
    terminal.write("Hello")

    assert repr(terminal).startswith("Terminal(")


def test_terminal():
    terminal = pn.widgets.Terminal("Hello")
    terminal.write(" World!")

    model = terminal.get_root()

    assert model.output == "Hello World!"

    terminal.clear()

    assert model._clears == 1
    assert terminal.output == ""

    model2 = terminal.get_root()

    assert model2.output == ""


@not_windows
def test_subprocess():
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
def test_run_list_args():
    terminal = pn.widgets.Terminal()
    subprocess = terminal.subprocess
    subprocess.args = ["ls", "-l"]
    subprocess.run()
    time.sleep(0.5)
    assert subprocess.running


def test_cannot_assign_string_args_with_spaces():
    terminal = pn.widgets.Terminal()
    subprocess = terminal.subprocess
    with pytest.raises(ValueError):
        subprocess.args = "ls -l"


def write_to_terminal(term):
    term.write("This is written directly to the terminal.\n")


def print_to_terminal(term):
    sys.stdout = term
    print("This print statement is redirected from stdout to the Panel Terminal")

    sys.stdout = sys.__stdout__
    print("This print statement is again redirected to the server console")


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
    for _ in range(0, iterations):
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
        name="Write to the Terminal", button_type="primary"
    )
    write_to_terminal_button.on_click(lambda x: write_to_terminal(terminal))

    special_characters_button = pn.widgets.Button(
        name="Write special to the Terminal", button_type="primary"
    )
    special_characters_button.on_click(lambda x: _special_characters(terminal))

    print_to_terminal_button = pn.widgets.Button(
        name="Print to Terminal", button_type="primary"
    )
    print_to_terminal_button.on_click(lambda x: print_to_terminal(terminal))

    logger = get_logger(terminal)
    log_button = pn.widgets.Button(name="Log", button_type="primary")
    log_button.on_click(lambda x: logger.info("Hello Info Logger"))

    stream_button = pn.widgets.Button(name="Stream", button_type="primary")
    stream_button.on_click(lambda x: [logger.info(uuid.uuid4()) for i in range(0, 300)])

    run_ls_in_subprocess_button = pn.widgets.Button(
        name="Run ls in subprocess", button_type="primary"
    )
    run_ls_in_subprocess_button.on_click(lambda x: terminal.subprocess.run(args="ls"))

    run_ls_l_in_subprocess_button = pn.widgets.Button(
        name="Run ls -l in subprocess", button_type="primary"
    )
    run_ls_l_in_subprocess_button.on_click(
        lambda x: terminal.subprocess.run("ls", "-l")
    )

    run_bash_in_subprocess_button = pn.widgets.Button(
        name="Run bash in subprocess", button_type="primary"
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


if __name__.startswith("bokeh"):
    get_app().servable()
