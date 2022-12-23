# dask_example.py
from datetime import datetime as dt

import param

from dask.distributed import Client
from tasks import blocking_computation

import panel as pn

pn.extension()

@pn.cache
def get_client():
    return Client()

get_client() # For some unknown reason this is needed. Otherwise we get ModuleNotFoundError: No module named 'panel_dask_cluster'

async def submit(func, *args, **kwargs):
    client = get_client()
    future = client.submit(func, *args, **kwargs)
    return await client.gather(future, asynchronous=True)

float_input = pn.widgets.FloatInput(value=0, name="Input")
submit_button = pn.widgets.Button(name="Run in background", button_type="primary")
other_widget = pn.widgets.IntSlider(value=0, start=0, end=10, name="Non blocked slider")
pn.Column(float_input, submit_button, other_widget, other_widget.param.value).servable()

def start():
    submit_button.disabled=True
    float_input.disabled=True
    float_input.loading=True
    

def stop():
    float_input.disabled=False
    float_input.loading=False
    submit_button.disabled=False

@pn.depends(submit_button, watch=True)
async def run(_):
    start()
    s1 = dt.now()
    print("stop", s1)
    float_input.value = await submit(blocking_computation, float_input.value)
    s2 = dt.now()
    print("stop", s2)
    print("total duration", (s2-s1))
    stop()
    
    
