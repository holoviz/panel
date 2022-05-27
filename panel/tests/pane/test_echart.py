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
    from pyecharts import options as opts
    from pyecharts.charts import Bar

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

def get_pyechart2():
    from pyecharts.charts import Bar

    import panel as pn

    bar1 = pn.widgets.IntSlider(start=1, end=100, value=50)
    bar2 = pn.widgets.IntSlider(start=1, end=100, value=50)

    @pn.depends(bar1.param.value, bar2.param.value)
    def plot(bar1, bar2):
        my_plot= (Bar()
            .add_xaxis(['Bar1', 'Bar2'])
            .add_yaxis('Values', [bar1, bar2])
        )
        return pn.pane.ECharts(my_plot, width=500, height=250)
    return pn.Row(pn.Column(bar1, bar2), plot)

if __name__.startswith("bokeh"):
    # test_echart().servable()
    get_pyechart2().servable()
if __name__.startswith("__main__"):
    test_echart().show(port=5007)
    get_pyechart().show(port=5007)
