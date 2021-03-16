import panel as pn


def test_constructor():
    terminal = pn.pane.Terminal(object="Click Me Now!")

def get_app():
    pn.config.js_files["xtermjs"]="https://unpkg.com/xterm@4.11.0/lib/xterm.js"
    pn.config.css_files.append("https://unpkg.com/xterm@4.11.0/css/xterm.css")
    # pn.config.js_files["xtermjs-fit"]="https://unpkg.com/xterm@4.11.0/lib/addons/fit/fit.js"
    # pn.config.js_files["xtermjs-web-links"]="https://unpkg.com/xterm@4.11.0/lib/addons/webLinks/webLinks.js"
    # pn.config.js_files["xtermjs-fullscreen"]="https://unpkg.com/xterm@4.11.0/lib/addons/fullscreen/fullscreen.js"
    # pn.config.js_files["xtermjs-search"]="https://unpkg.com/xterm@4.11.0/lib/addons/search/search.js"
    terminal = pn.pane.Terminal(object="Welcome to the Panel Terminal!", height=400)
    return pn.Column(
        terminal, pn.Param(terminal, parameters=["object", "out"])
    )

if __name__.startswith("bokeh"):
    get_app().servable()