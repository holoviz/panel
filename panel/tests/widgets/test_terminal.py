import panel as pn
import sys
import subprocess
import shlex
import logging
import uuid
import time
import select
import pty
import os

def test_constructor():
    terminal = pn.widgets.Terminal()
    terminal.write("Hello")

def run_print(term):
    # Replace default stdout (terminal) with our Panel Terminal
    sys.stdout = term

    print("This print statement is going in to Panel Terminal")
    term.write("Can also be written to like normal.\n")

    # The original `sys.stdout` is kept in a special
    # dunder named `sys.__stdout__`. So you can restore
    # the original output stream to the terminal.
    sys.stdout = sys.__stdout__
    print("Now printing back to console")


def run_process(term):
    # https://stackoverflow.com/questions/21035127/how-to-use-a-custom-file-like-object-as-subprocess-stdout-stderr
    command = "ls -l"

    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)

    term.write(process.stdout.read())

def get_logger(term):
    logger = logging.getLogger('terminal')
    logger.setLevel(logging.DEBUG)

    sh = logging.StreamHandler(term)
    sh.terminator = '  \n'
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')

    sh.setFormatter(formatter)
    sh.setLevel(logging.DEBUG)
    logger.addHandler(sh)
    return logger

def special_characters(term, iterations=1):
    for _ in range(0,iterations):
        term.write(f"Danish Characters: æøåÆØÅ\n")
        term.write(f"Emoji: Python 🐍  Panel ❤️  LOL 😊 \n")
        term.write(f"Links: https://awesome-panel.org\n")

def get_app():
    pn.config.sizing_mode="stretch_width"
    terminal = pn.widgets.Terminal(object="Welcome to the Panel Terminal!\nI'm based on xterm.js\n\n", height=400, width=800, sizing_mode="stretch_width", options={"cursorBlink": True})

    run_print_button = pn.widgets.Button(name="Print", button_type="primary")
    run_print_button.on_click(lambda x: run_print(terminal))

    run_process_button = pn.widgets.Button(name="Run Process", button_type="primary")
    run_process_button.on_click(lambda x: run_process(terminal))

    logger = get_logger(terminal)
    log_button = pn.widgets.Button(name="Log", button_type="primary")
    log_button.on_click(lambda x: logger.info("Hello Info Logger"))

    stream_button = pn.widgets.Button(name="Stream", button_type="primary")
    stream_button.on_click(lambda x: [logger.info(uuid.uuid4()) for i in range(0,300)])

    special_characters_button = pn.widgets.Button(name="Special", button_type="primary")
    special_characters_button.on_click(lambda x: special_characters(terminal))

    template = pn.template.FastListTemplate(title="Panel - Terminal - PR in Progress!")

    template.main[:]=[
        pn.Column(
            pn.pane.Markdown("#### Terminal"),
            terminal,
            pn.Param(
                terminal,
                parameters=["value", "object", "write_to_console", "line_feeds", "clear", "width", "height", "sizing_mode"],
                widgets = {
                    "width": {"widget_type": pn.widgets.IntSlider, "start": 0, "end": 1000},
                    "height": {"widget_type": pn.widgets.IntSlider, "start": 0, "end": 1000}
                }
            ),
        )
    ]
    template.sidebar[:]=[
            pn.pane.Markdown("#### Terminal Use Cases"),
            run_print_button,
            run_process_button,
            log_button,
            stream_button,
            special_characters_button
    ]
    return template

def pid_is_running(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False # It is not running
    else:
        return True # It is running

def test_subprocess():
    command = "bash"
    terminal = pn.widgets.Terminal()

    subprocess = terminal.subprocess
    subprocess.command = command

    assert subprocess.terminal == terminal
    assert subprocess.command == command
    assert isinstance(subprocess.periodic_callback, pn.callbacks.PeriodicCallback)

    subprocess.run()
    assert subprocess._child_pid
    assert subprocess._fd # file descriptor
    assert subprocess.periodic_callback.running
    assert pid_is_running(subprocess._child_pid)

    child_pid = subprocess._child_pid
    subprocess.kill()
    assert subprocess._child_pid==0
    assert subprocess._fd==0
    assert not subprocess.periodic_callback.running
    # assert not pid_is_running(child_pid)

def get_pty_app():
    terminal = pn.widgets.Terminal(object="Welcome to the Panel Terminal!\n\nI'm based on Python 🐍  Panel ❤️  and xterm.js 😊 \n\n", height=500, margin=(10,10,35,10), width=800, sizing_mode="stretch_width", options={"cursorBlink": True}, write_to_console=True)
    config = {"child_pid": None, "fd": None}

    def on_load():
        cmd = 'bash'
        cmd = "".join(shlex.quote(c) for c in cmd) # Clean for security reasons

        # A fork is an operation whereby a process creates a copy of itself
        # The two processes will continue from here as a PARENT and a CHILD process
        (child_pid, fd) = pty.fork()

        if child_pid == 0:
            # this is the CHILD process fork.
            # anything printed here will show up in the pty, including the output
            # of this subprocess
            subprocess.run(cmd)
        else:
            # this is the PARENT process fork.
            # store child fd and pid
            config["child_pid"]=child_pid
            config["fd"]=fd

            def read_and_forward_pty_output():
                max_read_bytes = 1024 * 20
                if fd:
                    timeout_sec = 0
                    (data_ready, _, _) = select.select([fd], [], [], timeout_sec)
                    if data_ready:
                        output = os.read(fd, max_read_bytes).decode()
                        terminal.write(output)
            pn.state.add_periodic_callback(read_and_forward_pty_output, 50)

    @pn.depends(value=terminal.param.value, watch=True)
    def update_pty(value):
        print(value.encode())
        fd = config["fd"]
        if fd:
            os.write(fd, value.encode())

    pn.state.onload(on_load)

    template = pn.template.FastListTemplate(title="Panel - Terminal - PR in Progress!", main=[terminal])

    return template

def get_run_app():
    terminal = pn.widgets.Terminal(object="Welcome to the Panel Terminal!\n\nI'm based on Python 🐍  Panel ❤️  and xterm.js 😊 \n\n", height=500, margin=(10,10,35,10), width=800, sizing_mode="stretch_width", options={"cursorBlink": True}, write_to_console=False)
    terminal.subprocess.command = "python"
    # pn.state.onload(terminal.subprocess.run)
    return pn.Column(terminal, terminal.subprocess.param.run, terminal.subprocess.param.kill, terminal.subprocess.param.running)


if __name__.startswith("bokeh"):
    # get_app().servable()
    # get_pty_app().servable()
    get_run_app().servable()