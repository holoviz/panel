import panel as pn
from panel.pane.echart import EChart, JS_FILES
from pyecharts.charts import Bar
from pyecharts import options as opts

HTML="""\n    <div id="main" style="width:100%;height:100%;"></div>\n    <script type="text/javascript">\n        // based on prepared DOM, initialize echarts instance\n        var myScript = document.currentScript;\n        var myDiv = myScript.parentElement.firstChild\n        var myChart = echarts.init(myDiv);\n\n        // specify chart configuration item and data\n        var option = {\'title\': {\'text\': \'ECharts entry example\'}, \'tooltip\': {}, \'legend\': {\'data\': [\'Sales\']}, \'xAxis\': {\'data\': [\'shirt\', \'cardign\', \'chiffon shirt\', \'pants\', \'heels\', \'socks\']}, \'yAxis\': {}, \'series\': [{\'name\': \'Sales\', \'type\': \'bar\', \'data\': [5, 20, 36, 10, 10, 20]}]}\n\n        // use configuration item and data specified to show chart\n        myChart.setOption(option);\n    </script>\n"""

ECHART_DICT = {
    "title": {"text": "ECharts entry example"},
    "tooltip": {},
    "legend": {"data": ["Sales"]},
    "xAxis": {"data": ["shirt", "cardign", "chiffon shirt", "pants", "heels", "socks"]},
    "yAxis": {},
    "series": [{"name": "Sales", "type": "bar", "data": [5, 20, 36, 10, 10, 20]}],
}

ECHART_DICT_PIE = {
    "backgroundColor": '#2c343c',

    "title": {
        "text": 'Customized Pie',
        "left": 'center',
        "top": 20,
        "textStyle": {
            "color": '#ccc'
        }
    },

    "tooltip": {
        "trigger": 'item',
        "formatter": '{a} <br/>{b} : {c} ({d}%)'
    },

    "visualMap": {
        "show": False,
        "min": 80,
        "max": 600,
        "inRange": {
            "colorLightness": [0, 1]
        }
    },
    "series": [
        {
            "name": 'Distribution',
            "type": 'pie',
            "radius": '55%',
            "center": ['50%', '50%'],
            "data": [
                {"value": 335, "name": 'AAA'},
                {"value": 310, "name": 'BBB'},
                {"value": 274, "name": 'CCC'},
                {"value": 235, "name": 'EEE'},
                {"value": 400, "name": 'DDD'}
            ],
            "roseType": 'radius',
            "label": {
                "color": 'rgba(255, 255, 255, 0.3)'
            },
            "labelLine": {
                "lineStyle": {
                    "color": 'rgba(255, 255, 255, 0.3)'
                },
                "smooth": 0.2,
                "length": 10,
                "length2": 20
            },
            "itemStyle": {
                "color": '#c23531',
                "shadowBlur": 200,
                "shadowColor": 'rgba(0, 0, 0, 0.5)'
            },

            "animationType": 'scale',
            "animationEasing": 'elasticOut',
            "animationDelay": 200
        }
    ]
}


def test_view():
    return EChart(echart=ECHART_DICT, height=300)

def test_view_pie():
    return EChart(echart=ECHART_DICT_PIE, height=300)

def test_view_pyechart_bar():
    bar = (
        Bar()
        .add_xaxis(["Microsoft", "Amazon", "IBM", "Oracl", "Google", "Alibaba"])
        .add_yaxis('2017-2018 Revenue in (billion $)', [21.2, 20.4, 10.3, 6.08, 4, 2.2])
        .set_global_opts(title_opts=opts.TitleOpts(title="Top cloud providers 2018", subtitle="2017-2018 Revenue"))
    )
    return EChart(echart=bar, height=300)

if __name__.startswith("bk"):
    # @ Philipp
    pn.config.sizing_mode = "stretch_width"
    pn.config.js_files["echart"] = JS_FILES["echart"]
    chart = test_view()
    chart_pie = test_view_pie()
    chart_pyechart_bar = test_view_pyechart_bar()
    # @Philippfr: How to I automatically resize? When I increment the resizes parameter it resizes
    # But I cannot find a way to do it automatically?
    app = pn.Column(
        chart, chart.param.option,
        chart_pie, chart_pie.param.option,
        chart_pyechart_bar, chart_pyechart_bar.param.option,
    )
    app.servable()