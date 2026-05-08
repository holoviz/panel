import pytest

pytest.importorskip("playwright")

try:
    import pyecharts as pye
except Exception:
    pye = None # type: ignore

pyecharts_available = pytest.mark.skipif(pye is None, reason='Requires pyecharts')

from playwright.sync_api import expect

from panel.pane import ECharts
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui

data = [
    {"value": 12, "percent": 0.8},
    {"value": 23, "percent": 0.52},
    {"value": 33, "percent": 0.87},
    {"value": 3, "percent": 0.05},
    {"value": 33, "percent": 0.43},
]

@pyecharts_available
def test_pyecharts_with_jscode(page):
    from pyecharts import options as opts
    from pyecharts.charts import Bar
    from pyecharts.commons.utils import JsCode
    from pyecharts.globals import ThemeType


    c = (
        Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
        .add_xaxis([1, 2, 3, 4, 5])
        .add_yaxis("product1", data, stack="stack1", category_gap="50%")
        .set_series_opts(
            label_opts=opts.LabelOpts(
                position="right",
                formatter=JsCode(
                    "function(x){return Number(x.data.percent * 100).toFixed() + '%';}"
                ),
            )
        )
    )

    pane = ECharts(c, renderer='svg')

    serve_component(page, pane)

    for v in data:
        expect(page.locator(f'text:has-text("{int(v["percent"]*100)}%")')).to_have_count(1)
