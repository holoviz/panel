# ECharts
---
```python
import panel as pn
pn.extension('echarts')
```

The ``ECharts`` pane renders [Apache ECharts](https://echarts.apache.org/en/index.html) and [pyecharts](https://pyecharts.org/#/) plots inside Panel. Note that to use the ``ECharts`` pane in the notebook the Panel extension has to be loaded with 'echarts' as an argument to ensure that echarts.js is initialized.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``object``** (dict): An ECharts plot specification expressed as a Python dictionary, which is then converted to JSON. Or a pyecharts chart like `pyecharts.charts.Bar`.
* **``options``** (dict): An optional dict of options passed to `Echarts.setOption`. Allows to fine-tune the rendering behavior. For example, you might want to use `options={ "replaceMerge": ['series'] })` when updating the `objects` with a value containing a smaller number of series.
* **``renderer``** (str): Whether to render with HTML 'canvas' (default) or 'svg'
* **``theme``** (str): Theme to apply to plots (one of 'default', 'dark', 'light')
___

Lets try the ``ECharts`` pane support for ECharts specs in its raw form (i.e. a dictionary), e.g. here we declare a bar plot:

```python
echart_bar = {
    'title': {
        'text': 'ECharts entry example'
    },
    'tooltip': {},
    'legend': {
        'data':['Sales']
    },
    'xAxis': {
        'data': ["shirt","cardign","chiffon shirt","pants","heels","socks"]
    },
    'yAxis': {},
    'series': [{
        'name': 'Sales',
        'type': 'bar',
        'data': [5, 20, 36, 10, 10, 20]
    }],
};
echart_pane = pn.pane.ECharts(echart_bar, height=480, width=640)
echart_pane
```

Like all other panes, the ``ECharts`` pane ``object`` can be updated, either in place and triggering an update:

```python
echart_bar['series'] = [dict(echart_bar['series'][0], type='line')]
echart_pane.param.trigger('object')
```

Vega specification can also be responsively sized by declaring the width or height to match the container:

```python
responsive_spec = dict(echart_bar, responsive=True)

pn.pane.ECharts(responsive_spec, height=400)
```

The ECharts pane also has support for pyecharts. For example, we can pass a `pyecharts.charts.Bar` chart directly the `ECharts` pane.

```python
from pyecharts.charts import Bar

bar1 = pn.widgets.IntSlider(start=1, end=100, value=50)
bar2 = pn.widgets.IntSlider(start=1, end=100, value=50)

def plot(bar1, bar2):
    my_plot= (Bar()
        .add_xaxis(['Helicoptors', 'Planes'])
        .add_yaxis('Total In Flight', [bar1, bar2])
    )
    return pn.pane.ECharts(my_plot, width=500, height=250)
pn.Row(
    pn.Column(bar1, bar2),
    pn.bind(plot, bar1, bar2),
).servable()
```

The ECharts library supports a wide range of chart types and since the plots are expressed using JSON datastructures we can easily update the data and then emit change events to update the charts:

```python
gauge = {
    'tooltip': {
        'formatter': '{a} <br/>{b} : {c}%'
    },
    'series': [
        {
            'name': 'Gauge',
            'type': 'gauge',
            'detail': {'formatter': '{value}%'},
            'data': [{'value': 50, 'name': 'Value'}]
        }
    ]
};
gauge_pane = pn.pane.ECharts(gauge, width=400, height=400)

slider = pn.widgets.IntSlider(value=50, start=0, end=100)

slider.jscallback(args={'gauge': gauge_pane}, value="""
gauge.data.series[0].data[0].value = cb_obj.value
gauge.properties.data.change.emit()
""")

pn.Column(slider, gauge_pane)
```

## Events

The `EChart` object allows you to listen to any event defined in the Javascript API, either by listening to the event in Python using the `on_event` method or by triggering a Javascript callback with the `js_on_event` method.

For details on what events you can [ECharts events documentation](https://echarts.apache.org/handbook/en/concepts/event).

### Python

Let us start with a simple click event we want to listen to from Python. To add an event listener we simple call the `on_event` method with the event type (in this case 'click') and our Python handler.

```python
echart_pane = pn.pane.ECharts(echart_bar, height=480, width=640)
json = pn.pane.JSON()

def callback(event):
    json.object = event.data

echart_pane.on_event('click', callback)

pn.Row(echart_pane, json)
```

Try clicking on a point on the line. When inspecting the `json.object` after a click you should see something like this:

```python
{'componentType': 'series',
 'componentSubType': 'line',
 'componentIndex': 0,
 'seriesType': 'line',
 'seriesIndex': 0,
 'seriesId': '\x00Sales\x000',
 'seriesName': 'Sales',
 'name': 'shirt',
 'dataIndex': 0,
 'data': 5,
 'value': 5,
 'color': '#5470c6',
 'dimensionNames': ['x', 'y'],
 'encode': {'x': [0], 'y': [1]},
 '$vars': ['seriesName', 'name', 'value'],
 'event': {'detail': 1,
  'altKey': False,
  'button': 0,
  'buttons': 0,
  'clientX': 507,
  'clientY': 911,
  'ctrlKey': False,
  'metaKey': False,
  'pageX': 507,
  'pageY': 911,
  'screenX': 3739,
  'screenY': 762,
  'shiftKey': False,
  'target': {'boundingClientRect': {}},
  'currentTarget': {'boundingClientRect': {}},
  'relatedTarget': None},
 'type': 'click'}
```

To restrict what types of objects a particular event applies to you can also provide a `query` argument to the `on_event` method. The format of the `query` should be `mainType` or `mainType.subType`, such as:

- `'series'`: Fire event when clicking on data series
- `'series.line'`: Fire event only when clicking on a line data series.
- `'dataZoom'`: Fire event when clicking on zoom.
- `'xAxis.category'`: Fire event when clicking on a category on the xaxis.

### Javascript

The same concepts apply in Javascript, however here we pass in Javascript code a JS snippet. The namespace allows you to access the event data `cb_data` and the ECharts chart itself as `cb_obj`. In this way you have access to the event and can manipulate the plot yourself:

```python
echart_pane = pn.pane.ECharts(echart_bar, height=480, width=640)

echart_pane.js_on_event('click', 'alert(`Clicked on point: ${cb_data.dataIndex}`)')

echart_pane
```

If you want to modify another object in response to an event triggered on the chart you can pass additional objects to the `json_on_event` method. The corresponding Bokeh model will then be made available in the callback. As an example here we make the `JSON` pane available so that we can update it on a click event:

```python
echart_pane = pn.pane.ECharts(echart_bar, height=480, width=640)
json = pn.pane.JSON()

echart_pane.js_on_event('click', """
event = {...cb_data}
delete event.event
json.text = JSON.stringify(event)
""", json=json)

pn.Row(echart_pane, json)
```

### Controls

The `EChart` pane exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(gauge_pane.controls(jslink=True), gauge_pane)
```

---
