# Minimal echarts test server, start with:
# panel serve panel/tests/test_echarts.py --allow-websocket-origin=localhost:5005 --port=5005

import time
import pandas as pd
import panel as pn

COLOR = "#E1477E"

data_tree = [{'name':'ROOT', 'children': [{'name': 'Child Non-clickable', 'value': 1}, {'name': 'Child Clickable', 'value': 2, 'id': 'ABC'}]}]

# Spinner styles: 'arc', 'arcs', 'bar', 'dots', 'petal'
pn.extension(loading_spinner='arc', loading_color=COLOR)

btn = pn.widgets.Button(name="Refresh", button_type="primary")

echart_option = {
    "tooltip": {
        "trigger": 'item',
        "triggerOn": 'mousemove'
    },
    "series": [
        {
            "type": 'tree',
            "data": data_tree,
            "top": '18%',
            "bottom": '14%',
            "layout": 'radial',
            "symbol": 'emptyCircle',
            "symbolSize": 10,
            "initialTreeDepth": 2,
            "animationDurationUpdate": 750,
            "emphasis": {
                "focus": 'descendant'
            }
        }
    ],
    "responsive": True
}

event_config = {
    'click': 'series.tree', # Tests for Echarts event names with query
    # 'click': None, # Tests for Echarts event names without query
    # 'click': {'name': 'Child Clickable'}, # Tests for Echarts event names without query
    # 'click': {'query': 'series.tree', 'base_url': 'https://www.TEST.de/AssetDetail.aspx?AssetId=',
    #     'identifier': 'id'}, # Tests for new browser tab Echarts event
    # 'click': {'query': 'series.tree', 'handler': 'e => console.log("I got an event:", e)'}, # Tests for handler Echarts event
    # 'cluck': 'series.tree', # Tests for wrong Echarts event names
}

echart = pn.pane.ECharts(echart_option, event_config=event_config, sizing_mode="stretch_both")

def update(event):
    with pn.param.set_values(echart, loading=True):
        time.sleep(1)
        echart.object = echart_option
    
btn.on_click(update)

react = pn.template.ReactTemplate(
    title="Minimal Echarts Test",
    header_background=COLOR,
    header_color="#ffffff",
)

react.sidebar.append(btn)
react.main[:2, :6] = pn.Card(echart, title='eChart', sizing_mode="stretch_both", collapsible=False)

react.servable()

