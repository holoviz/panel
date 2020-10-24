import panel as pn

ECHART = {
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

def test_echart():
    echart = ECHART
    pane = pn.pane.ECharts(echart, width=500, height=500)
    assert pane.object == echart
    return pane

def get_pyechart():
    from pyecharts.charts import Bar
    from pyecharts import options as opts

    bar = (
        Bar()
        .add_xaxis(["A", "B", "C", "D", "E", "F", "G"])
        .add_yaxis("Series1", [114, 55, 27, 101, 125, 27, 105])
        .add_yaxis("Series2", [57, 134, 137, 129, 145, 60, 49])
        .set_global_opts(title_opts=opts.TitleOpts(title="PyeCharts"))
    )
    pane = pn.pane.ECharts(bar, width=500, height=500)
    assert pane.object == bar
    return pane

if __name__.startswith("bokeh"):
    # test_echart().servable()
    get_pyechart().servable()
if __name__.startswith("__main__"):
    test_echart().show(port=5007)
    get_pyechart().show(port=5007)
