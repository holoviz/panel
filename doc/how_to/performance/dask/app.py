# app.py
from datetime import datetime as dt

import param

from dashboard import DASK_DASHBOARD_ADDRESS, DaskViewer
from dask.distributed import Client

import panel as pn

from cluster import DASK_SCHEDULER_ADDRESS
from tasks import fibonacci

QUEUE = []

pn.extension("terminal", sizing_mode="stretch_width")


async def get_client():
    if not "dask-client" in pn.state.cache:
        pn.state.cache["dask-client"] = await Client(
            DASK_SCHEDULER_ADDRESS, asynchronous=True
        )
    return pn.state.cache["dask-client"]


n_input = pn.widgets.IntInput(value=0, width=100, sizing_mode="fixed", name="n")
submit_button = pn.widgets.Button(name="Submit", button_type="primary", align="end")
queue_widget = pn.widgets.LiteralInput(value=QUEUE, name="In Progress", disabled=True)
terminal_widget = pn.widgets.Terminal(
    height=200,
)
dask_viewer = DaskViewer(height=500)


@pn.depends(submit_button, watch=True)
async def _handle_click(_):
    n = n_input.value
    n_input.value += 1

    start = dt.now()
    QUEUE.append(n)
    queue_widget.value = QUEUE.copy()

    client = await get_client()
    fib_n = await client.submit(fibonacci, n)

    end = dt.now()
    QUEUE.pop(QUEUE.index(n))
    queue_widget.value = QUEUE.copy()
    duration = (end - start).seconds
    terminal_widget.write(f"fibonacci({n})={fib_n} in {duration}sec\n")


component = pn.Column(
    "## Tasks",
    pn.Row(n_input, submit_button),
    queue_widget,
    "## Results",
    terminal_widget,
    "## Dask Dashboard",
    dask_viewer,
)

pn.template.FastListTemplate(
    site="Panel + Dask", title="Async background tasks", main=[component]
).servable()