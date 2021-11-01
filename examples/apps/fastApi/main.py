from bokeh.embed import server_document
from panel.io.server import Server
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from threading import Thread
from tornado.ioloop import IOLoop

from sliders.pn_app import createApp

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware( # Middleware to serve panel apps asynchronously via starlette
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def bkapp_page(request: Request):
    script = server_document('http://127.0.0.1:5000/app')
    return templates.TemplateResponse("base.html", {"request": request, "script": script})


def bk_worker():
    server = Server({'/app': createApp},
        port=5000, io_loop=IOLoop(), 
        allow_websocket_origin=["*"])

    server.start()
    server.io_loop.start()

th = Thread(target=bk_worker)
th.daemon = True
th.start()