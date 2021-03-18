import panel as pn
import sys
import subprocess
import shlex

pn.config.js_files["xtermjs"]="https://unpkg.com/xterm@4.11.0/lib/xterm.js"
pn.config.css_files.append("https://unpkg.com/xterm@4.11.0/css/xterm.css")
# pn.config.js_files["xtermjs-fit"]="https://unpkg.com/xterm@4.11.0/lib/addons/fit/fit.js"
# pn.config.js_files["xtermjs-web-links"]="https://unpkg.com/xterm@4.11.0/lib/addons/webLinks/webLinks.js"
# pn.config.js_files["xtermjs-fullscreen"]="https://unpkg.com/xterm@4.11.0/lib/addons/fullscreen/fullscreen.js"
# pn.config.js_files["xtermjs-search"]="https://unpkg.com/xterm@4.11.0/lib/addons/search/search.js"

def test_constructor():
    terminal = pn.pane.Terminal(object="Click Me Now!")

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

    term.object = process.stdout.read().decode("utf8")


def get_app():
    terminal = pn.pane.Terminal(object="Welcome to the Panel Terminal!\n", height=400)

    run_print_button = pn.widgets.Button(name="Print", button_type="success")
    run_print_button.on_click(lambda x: run_print(terminal))

    run_process_button = pn.widgets.Button(name="Run Process", button_type="success")
    run_process_button.on_click(lambda x: run_process(terminal))

    return pn.Column(
        terminal, run_print_button, run_process_button, pn.Param(terminal, parameters=["object", "out", "write_to_console"])
    )

if __name__.startswith("bokeh"):
    get_app().servable()