from importlib.util import find_spec

collect_ignore_glob = [
    "apps/",
    "developer_guide/",
    "*VTK*.ipynb",
    "*Vega.ipynb",
    "*DeckGL*.ipynb",
    "*Terminal.ipynb",
]

if find_spec("altair") is None:
    collect_ignore_glob += [
        "gallery/altair_brushing.ipynb",
        "gallery/gapminders.ipynb",
        "gallery/penguin_kmeans.ipynb",
        "reference/panes/Streamz.ipynb",
    ]

if find_spec("streamz") is None:
    collect_ignore_glob += [
        "reference/panes/DataFrame.ipynb",
        "reference/panes/Streamz.ipynb",
    ]

if find_spec("datashader") is None:
    collect_ignore_glob += [
        "gallery/glaciers.ipynb",
        "gallery/windturbines.ipynb",
        "gallery/vtk_slicer.ipynb",
    ]

if find_spec("pyvista") is None:
    collect_ignore_glob += [
        "gallery/vtk_interactive.ipynb",
        "gallery/vtk_warp.ipynb",
    ]

if find_spec("scikit-learn") is None:
    collect_ignore_glob += [
        "gallery/iris_kmeans.ipynb",
        "gallery/penguin_kmeans.ipynb",
        "gallery/xgboost_classifier.ipynb",
    ]

if find_spec("scikit-image") is None:
    collect_ignore_glob += [
        "gallery/streaming_videostream.ipynb",
    ]

if find_spec("fastparquet") is None and find_spec("pyarrow") is None:
    collect_ignore_glob += [
        "gallery/nyc_deckgl.ipynb",
    ]

if find_spec("scipy") is None:
    collect_ignore_glob += [
        "gallery/penguin_crossfilter.ipynb",
        "gallery/portfolio_optimizer.ipynb",
        "reference/layouts/Swipe.ipynb",
        "reference/panes/Audio.ipynb",
        "reference/panes/HoloViews.ipynb",
    ]
if find_spec("ipyvolume") is None:
    collect_ignore_glob += [
        "reference/panes/IPyWidget.ipynb",
    ]

if find_spec("seaborn") is None:
    collect_ignore_glob += [
        "reference/panes/Matplotlib.ipynb",
    ]


def pytest_configure(config):
    # A cell that never finishes would otherwise hang until the job times out
    config.option.nbval_cell_timeout = min(config.option.nbval_cell_timeout, 60)


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
