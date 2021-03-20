import panel as pn
import sys
import subprocess
import shlex
import logging
import uuid

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
        term.write(f"Emoji: Python 🐍  Love ❤️  LOL 😊 \n")
        term.write(f"Links: https://awesome-panel.org\n")

def get_app():
    pn.config.sizing_mode="stretch_width"
    terminal = pn.widgets.Terminal(object="Welcome to the Panel Terminal!\nI'm based on xterm.js\n", height=400)

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
            pn.Param(terminal, parameters=["write_to_console", "clear"]),
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


if __name__.startswith("bokeh"):
    get_app().servable()