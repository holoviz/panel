def start_perspective_tornado_server():
    import random

    from datetime import datetime, timedelta

    import pandas as pd
    import perspective as psp
    import tornado.ioloop
    import tornado.web

    from perspective.handlers.tornado import PerspectiveTornadoHandler

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

    server = psp.Server()
    client = server.new_local_client()
    client.table(df, name="data_source_one")
    app = tornado.web.Application([
        (r"/websocket", PerspectiveTornadoHandler, {
            "perspective_server": server,
        })
    ])

    app.listen(5005)
    loop = tornado.ioloop.IOLoop.current()
    loop.start()

def start_panel_app():
    import param

    import panel as pn

    class Perspective(pn.custom.AnyWidgetComponent):
        value = param.String()
        websocket = param.String()

        _esm = "perspective_anywidget.js"
        _stylesheets = ["https://cdn.jsdelivr.net/npm/@finos/perspective-viewer/dist/css/themes.css"]

    Perspective(
        value="data_source_one",
        websocket="wss://mnr-jupyterhub.de-prod.dk/mt-ai/user/masma/vscode/proxy/5005/websocket",
        height=500, sizing_mode="stretch_width"
    ).servable()


if __name__=="__main__":
    start_perspective_tornado_server()

elif __name__.startswith("bokeh"):
    start_panel_app()
