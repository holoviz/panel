import panel as pn
def test_echart():
    echart = {
        "xAxis": {
            "type": 'category',
            "data": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
        "yAxis": {
            "type": 'value'
        },
        "series": [{
            "data": [820, 932, 901, 934, 1290, 1330, 1320],
            "type": 'line'
        }]
    }
    pane = pn.pane.ECharts(echart, width=500, height=500)
    assert pane.object == echart
    return pane

if __name__.startswith("bokeh"):
    test_echart().servable()
if __name__.startswith("__main__"):
    test_echart().show(port=5007)
