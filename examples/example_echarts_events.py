# Minimal echarts test server, start with:
# panel serve panel/examples/example_echarts_events.py --allow-websocket-origin=localhost:5005 --port=5005

import time
# import pandas as pd
import panel as pn

COLOR = "#E1477E"

data_tree = [{'name':'ROOT', 'value': 3, 'children': [{'name': 'Child Non-clickable', 'value': 1}, {'name': 'Child Clickable', 'value': 2, 'id': 'ABC'}]}]

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
    # 'click': 'series.tree', # Tests for Echarts event names with query
    # 'click': None, # Tests for Echarts event names without query
    # 'click': {'name': 'Child Clickable'}, # Tests for Echarts event with complex query
    # 'click': {'query': 'series.tree', 'base_url': 'https://www.TEST.de/AssetDetail.aspx?AssetId=',
    #     'identifier': 'id'}, # Tests for new browser tab Echarts event
    # 'click': {'query': 'series.tree', 'handler': 'e => console.log("I got an event:", e)'}, # Tests for handler Echarts event
    # 'cluck': 'series.tree', # Tests for wrong Echarts event names
    # 'click': {'query': 'series.tree', 'select': 'data'}, # Tests for Echarts event with custom select
    # 'click': {'query': 'series.tree', 'filters': ['children']}, # Tests for Echarts event with custom filters
    'click': {'query': 'series.tree', 'select': 'data', 'filters': ['children']}, # Tests for Echarts event with custom select and filters
}

echart = pn.pane.ECharts(echart_option, event_config=event_config, sizing_mode="stretch_both")

def update(event):
    with pn.param.set_values(echart, loading=True):
        time.sleep(1)
        echart.object = echart_option
    
btn.on_click(update)

@pn.depends(event=echart.param.event, watch=True)
def update_info(event):
    print(event)

react = pn.template.ReactTemplate(
    title="Minimal Echarts Test",
    header_background=COLOR,
    header_color="#ffffff",
)

react.sidebar.append(btn)
react.main[:2, :4] = pn.Card(echart, title='ECcarts', sizing_mode="stretch_both", collapsible=False)
react.main[:2, 4:8] = pn.Card(echart.param.event, title='Event', sizing_mode="stretch_both", collapsible=False)

react.servable()

