import subprocess
import sys

import pytest

pytest.importorskip("ipywidgets_bokeh")


def _run(code):
    return subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, timeout=120
    )


def test_kernel_instance_without_document():
    # Regression test for https://github.com/holoviz/panel/issues/6175
    result = _run(
        "import panel as pn\n"
        "pn.extension('ipywidgets')\n"
        "from ipykernel.kernelbase import Kernel\n"
        "assert Kernel.instance() is not None\n"
        "from bokeh.document import Document\n"
        "from panel.io.ipywidget import PanelKernel\n"
        "from panel.io.state import set_curdoc\n"
        "with set_curdoc(Document()):\n"
        "    assert isinstance(Kernel._instance, PanelKernel)\n"
    )
    assert result.returncode == 0, result.stderr


def test_existing_kernel_singleton_preserved():
    result = _run(
        "from ipykernel.kernelbase import Kernel\n"
        "kernel = Kernel.instance()\n"
        "import panel as pn\n"
        "pn.extension('ipywidgets')\n"
        "assert Kernel.instance() is kernel\n"
    )
    assert result.returncode == 0, result.stderr
