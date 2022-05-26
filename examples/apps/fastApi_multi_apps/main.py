from bokeh.embed import server_document
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sliders2.pn_app import createApp2
from sliders.pn_app import createApp

import panel as pn

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def bkapp_page(request: Request):
    script = server_document('http://127.0.0.1:5000/app')
    return templates.TemplateResponse("base.html", {"request": request, "script": script})

@app.get("/app2")
async def bkapp_page2(request: Request):
    script = server_document('http://127.0.0.1:5000/app2')
    return templates.TemplateResponse("app2.html", {"request": request, "script": script})

pn.serve({'/app': createApp, '/app2': createApp2},
        port=5000, allow_websocket_origin=["127.0.0.1:8000"],
         address="127.0.0.1", show=False)
