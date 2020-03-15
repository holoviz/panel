"""Implementation of echart/ pyecharts pane

See
- [echarts](https://www.echartsjs.com/en/index.html)
- [pyecharts](https://pyecharts.org/#/en-us/)
"""
import panel as pn
import param
import sys
import json

# @Philippfr. What should the user do to automatically include this?
# pn.extension("echarts")
JS_FILES = {"echart": "https://cdn.bootcss.com/echarts/3.7.2/echarts.min.js"}

OBJECT = {
    "title": {"text": "ECharts entry example"},
    "tooltip": {},
    "legend": {"data": ["Sales"]},
    "xAxis": {"data": ["shirt", "cardign", "chiffon shirt", "pants", "heels", "socks"]},
    "yAxis": {},
    "series": [{"name": "Sales", "type": "bar", "data": [5, 20, 36, 10, 10, 20]}],
}

HTML = """
    <div class="echart" style="width:100%;height:100%;"></div>
    <script type="text/javascript">
        var myScript = document.currentScript;
        var myDiv = myScript.parentElement.firstElementChild;
        var myChart = echarts.init(myDiv);
        myDiv.eChart = myChart;
        Object.defineProperty(myDiv, 'option', {
           get: function() { return null; },
           set: function(val) { this.eChart.setOption(val); this.eChart.resize();}
        });
        Object.defineProperty(myDiv, 'resizes', {
           get: function() { return null; },
           set: function(val) { this.eChart.resize();}
        });
    </script>"""

class EChart(pn.pane.WebComponent):
    html = param.String(HTML)
    properties_to_watch = param.Dict({"option": "option", "resizes": "resizes"})

    echart = param.Parameter()
    option = param.Dict()
    resizes = param.Integer()


    def __init__(self, **params):
        if "echart" in params:
            params["option"] = self._to_echart_dict(params["echart"])
        super().__init__(**params)

    @classmethod
    def _to_echart_dict(cls, echart):
        if isinstance(echart, dict):
            return echart
        if 'pyecharts' in sys.modules:
            import pyecharts
            if isinstance(echart, pyecharts.charts.chart.Chart):
                return json.loads(echart.dump_options())

        return {}

    @param.depends("echart", watch=True)
    def update(self):
        self.option = self._to_echart_dict(self.echart)