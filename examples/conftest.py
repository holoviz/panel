from importlib.util import find_spec

collect_ignore_glob = [
    "apps/",
    "developer_guide/",
    "homepage.ipynb",
    "*VTK*.ipynb",
    "*Vega.ipynb",
    "*DeckGL*.ipynb",
    "*Terminal.ipynb",
]


# TODO: Need to be double checked
requires_pandas = [
    "gallery/altair_brushing.ipynb",
    "gallery/deckgl_game_of_life.ipynb",
    "gallery/gapminders.ipynb",
    "gallery/glaciers.ipynb",
    "gallery/hvplot_explorer.ipynb",
    "gallery/iris_kmeans.ipynb",
    "gallery/nyc_deckgl.ipynb",
    "gallery/penguin_crossfilter.ipynb",
    "gallery/penguin_kmeans.ipynb",
    "gallery/portfolio_analyzer.ipynb",
    "gallery/portfolio_optimizer.ipynb",
    "gallery/vtk_interactive.ipynb",
    "gallery/vtk_slicer.ipynb",
    "gallery/vtk_warp.ipynb",
    "gallery/windturbines.ipynb",
    "gallery/xgboost_classifier.ipynb",
    "reference/chat/ChatMessage.ipynb",
    "reference/indicators/Tqdm.ipynb",
    "reference/indicators/Trend.ipynb",
    "reference/layouts/Swipe.ipynb",
    "reference/panes/Bokeh.ipynb",
    "reference/panes/DataFrame.ipynb",
    "reference/panes/ECharts.ipynb",
    "reference/panes/HTML.ipynb",
    "reference/panes/HoloViews.ipynb",
    "reference/panes/IPyWidget.ipynb",
    "reference/panes/Matplotlib.ipynb",
    "reference/panes/Param.ipynb",
    "reference/panes/Perspective.ipynb",
    "reference/panes/Plotly.ipynb",
    "reference/panes/ReactiveExpr.ipynb",
    "reference/panes/Reacton.ipynb",
    "reference/panes/Streamz.ipynb",
    "reference/panes/Vizzu.ipynb",
    "reference/templates/Bootstrap.ipynb",
    "reference/templates/EditableTemplate.ipynb",
    "reference/templates/FastGridTemplate.ipynb",
    "reference/templates/FastListTemplate.ipynb",
    "reference/templates/GoldenLayout.ipynb",
    "reference/templates/Material.ipynb",
    "reference/templates/React.ipynb",
    "reference/templates/Slides.ipynb",
    "reference/templates/Vanilla.ipynb",
    "reference/widgets/DataFrame.ipynb",
    "reference/widgets/FileDownload.ipynb",
    "reference/widgets/Tabulator.ipynb",
]

if find_spec("pandas") is None:
    collect_ignore_glob += requires_pandas


def pytest_runtest_makereport(item, call):
    """
    Skip tests that fail because "the kernel died before replying to kernel_info"
    this is a common error when running the example tests in CI.

    Inspired from: https://stackoverflow.com/questions/32451811

    """
    from _pytest.runner import pytest_runtest_makereport

    tr = pytest_runtest_makereport(item, call)

    if call.excinfo is not None:
        msgs = [
            "Kernel died before replying to kernel_info",
            "Kernel didn't respond in 60 seconds",
        ]
        for msg in msgs:
            if call.excinfo.type == RuntimeError and call.excinfo.value.args[0] in msg:
                tr.outcome = "skipped"
                tr.wasxfail = f"reason: {msg}"

    return tr
