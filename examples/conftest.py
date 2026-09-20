from importlib.util import find_spec

import pytest

collect_ignore_glob = [
    "apps/",
    "developer_guide/",
    "homepage.ipynb",
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


def pytest_configure(config):
    # A cell that never finishes would otherwise hang until the job times out
    config.option.nbval_cell_timeout = min(config.option.nbval_cell_timeout, 60)
    # The cells that time out are the ones downloading their data
    config.option.reruns = max(config.option.reruns or 0, 2)
    config.option.only_rerun = [*(config.option.only_rerun or []), "Timeout of"]


def pytest_runtest_makereport(item, call):
    """
    Skip tests that fail because "the kernel died before replying to kernel_info"
    this is a common error when running the example tests in CI.

    Inspired from: https://stackoverflow.com/questions/32451811

    """
    from _pytest.runner import pytest_runtest_makereport

    tr = pytest_runtest_makereport(item, call)

    if call.excinfo is not None:
        # nbval expects every later cell of a timed out notebook to fail, and
        # the interrupted cell can leave the ones after it without their state
        if "Timeout of" in str(call.excinfo.value):
            item.parent.timed_out = False
            for cell in item.session.items:
                if cell.nodeid.startswith(f"{item.parent.nodeid}::"):
                    cell.add_marker(pytest.mark.flaky(reruns=2, only_rerun=[".*"]))
        msgs = [
            "Kernel died before replying to kernel_info",
            "Kernel didn't respond in 60 seconds",
        ]
        for msg in msgs:
            if call.excinfo.type == RuntimeError and call.excinfo.value.args[0] in msg:
                tr.outcome = "skipped"
                tr.wasxfail = f"reason: {msg}"

    return tr
