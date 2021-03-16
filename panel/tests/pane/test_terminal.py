import panel as pn


def test_constructor():
    terminal = pn.pane.Terminal(object="Click Me Now!")

def get_app():
    pn.config.js_files["xtermjs"]="https://unpkg.com/xterm@3.6.0/dist/xterm.js"
    pn.config.js_files["xtermjs-fit"]="https://unpkg.com/xterm@3.6.0/dist/addons/fit/fit.js"
    pn.config.js_files["xtermjs-web-links"]="https://unpkg.com/xterm@3.6.0/dist/addons/webLinks/webLinks.js"
    pn.config.js_files["xtermjs-fullscreen"]="https://unpkg.com/xterm@3.6.0/dist/addons/fullscreen/fullscreen.js"
    pn.config.js_files["xtermjs-search"]="https://unpkg.com/xterm@3.6.0/dist/addons/search/search.js"
    terminal = pn.pane.Terminal(object="Click Me Now!")
    return pn.Column(
        terminal, pn.Param(terminal, parameters=["object", "out"])
    )

if __name__.startswith("bokeh"):
    get_app().servable()