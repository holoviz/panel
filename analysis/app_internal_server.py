def add_perspective_to_panel_server(panel_server):
    from perspective import GLOBAL_SERVER
    from perspective.handlers.tornado import PerspectiveTornadoHandler

    panel_server._tornado.add_handlers(
        ".*",
        [
        (r"/websocket", PerspectiveTornadoHandler, {
            "perspective_server": GLOBAL_SERVER,
        })
    ])


def app():
    import random

    from datetime import datetime, timedelta

    import pandas as pd
    import param

    from perspective import GLOBAL_CLIENT

    import panel as pn

    @pn.cache
    def add_table():
        data = {
            'int': [random.randint(-10, 10) for _ in range(9)],
            'float': [random.uniform(-10, 10) for _ in range(9)],
            'date': [(datetime.now() + timedelta(days=i)).date() for i in range(9)],
            'datetime': [(datetime.now() + timedelta(hours=i)) for i in range(9)],
            'category': ['Category A', 'Category B', 'Category C', 'Category A', 'Category B',
                    'Category C', 'Category A', 'Category B', 'Category C',],
            'link': ['https://panel.holoviz.org/', 'https://discourse.holoviz.org/', 'https://github.com/holoviz/panel']*3,
        }
        df = pd.DataFrame(data)

        GLOBAL_CLIENT.table(df, name="data_source_one")

    add_table()

    class Perspective(pn.custom.AnyWidgetComponent):
        value = param.String()
        websocket = param.String()

        _esm = "perspective_anywidget.js"
        _stylesheets = ["https://cdn.jsdelivr.net/npm/@finos/perspective-viewer/dist/css/themes.css"]

    return Perspective(
        value="data_source_one",
        # The websocket argument could be removed or hidden from the user
        websocket="wss://mnr-jupyterhub.de-prod.dk/mt-ai/user/masma/vscode/proxy/5006/websocket",
        height=500, sizing_mode="stretch_width"
    ).servable()


if __name__ == '__main__':
    import panel as pn
    pn.extension()

    server = pn.serve(app, start=False, port=5006)

    add_perspective_to_panel_server(panel_server=server)

    server.start()
    server.io_loop.start()
