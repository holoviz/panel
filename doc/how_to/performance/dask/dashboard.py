# utils
import os

import param

import panel as pn

DASK_DASHBOARD_ADDRESS = os.getenv("DASK_DASHBOARD", "http://localhost:8787/status")

VIEWS = {
    "aggregate-time-per-action": "individual-aggregate-time-per-action",
    "bandwidth-types": "individual-bandwidth-types",
    "bandwidth-workers": "individual-bandwidth-workers",
    "cluster-memory": "individual-cluster-memory",
    "compute-time-per-key": "individual-compute-time-per-key",
    "cpu": "individual-cpu",
    "exceptions": "individual-exceptions",
    "gpu-memory": "individual-gpu-memory",
    "gpu-utilization": "individual-gpu-utilization",
    "graph": "individual-graph",
    "groups": "individual-groups",
    "memory-by-key": "individual-memory-by-key",
    "nprocessing": "individual-nprocessing",
    "occupancy": "individual-occupancy",
    "profile-server": "individual-profile-server",
    "profile": "individual-profile",
    "progress": "individual-progress",
    "scheduler-system": "individual-scheduler-system",
    "task-stream": "individual-task-stream",
    "workers-cpu-timeseries": "individual-workers-cpu-timeseries",
    "workers-disk-timeseries": "individual-workers-disk-timeseries",
    "workers-disk": "individual-workers-disk",
    "workers-memory-timeseries": "individual-workers-memory-timeseries",
    "workers-memory": "individual-workers-memory",
    "workers-network-timeseries": "individual-workers-network-timeseries",
    "workers-network": "individual-workers-network",
    "workers": "individual-workers",
}

VIEWER_PARAMETERS = ["url", "path"]

def to_iframe(url):
    return f"""<iframe src="{url}" frameBorder="0" style="height:100%;width:100%"></iframe>"""

class DaskViewer(pn.viewable.Viewer):
    url = param.String(DASK_DASHBOARD_ADDRESS, doc="The url of the Dask status dashboard")
    path = param.Selector(default="individual-cpu", objects=VIEWS, doc="the endpoint", label="View")

    def __init__(self, size=20, **params):
        viewer_params = {k:v for k, v in params.items() if k in VIEWER_PARAMETERS}
        layout_params = {k:v for k, v in params.items() if k not in VIEWER_PARAMETERS}

        self._iframe =  pn.pane.HTML(sizing_mode="stretch_both")
                
        super().__init__(**viewer_params)

        self._select = pn.widgets.Select.from_param(self.param.path, size=size, width=300, sizing_mode="fixed", margin=(20,5,10,5))
        self._link = pn.panel(f"""<a href="{DASK_DASHBOARD_ADDRESS}" target="_blank">Dask Dashboard</a>""", height=50, margin=(0,20))
        self._panel = pn.Column(pn.Row(self._iframe, self._select, sizing_mode="stretch_both"), self._link, **layout_params)


    @pn.depends("url", "path", watch=True, on_init=True)
    def _update_panel(self):
        url = self.url.replace("/status", "/") + self.path
        self._iframe.object = to_iframe(url)

    def __panel__(self):
        return self._panel

if __name__.startswith("bokeh"):
    pn.extension(sizing_mode="stretch_width")

    DaskViewer(height=500, size=25).servable()   
