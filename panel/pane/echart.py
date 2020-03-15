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
        myDiv.after_layout = myChart.resize;
    </script>"""

# @Philippfr. For now I've assumed a convention that if the web component has an after_layout
# function it will be run in the .ts after_layout function. Is that a good convertion?

class EChart(pn.pane.WebComponent):
    """Echarts/ Pyecharts pane

    [ECharts]((https://www.echartsjs.com/en/index.html)) is an open-sourced JavaScript
    visualization tool, which can run fluently on PC and mobile devices.
    It is compatible with most modern Web Browsers

    ECharts depends on ZRender, a graphic rendering engine, to
    create intuitive, interactive, and highly-customizable charts.

    [Pyecharts](https://pyecharts.org/#/en-us/) is a Python api for using ECharts in Python
    including Standalone, Flask, Django and Jupyter Notebooks.
    """



    html = param.String(HTML)
    properties_to_watch = param.Dict({"option": "option"})

    # @Philippfr. Is this a good name? Is it better with object?
    echart = param.Parameter(doc="""
    A echart dictionary or pyechart object.
    """)
    option = param.Dict()

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
        """Run this to pudate the plot"""
        self.option = self._to_echart_dict(self.echart)