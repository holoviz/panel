import sys

from importlib import import_module
from subprocess import check_output
from textwrap import dedent

import pytest


def test_no_blocklist_imports():
    check = """\
    import sys
    import panel

    blocklist = {"pandas", "bokeh.plotting"}
    mods = blocklist & set(sys.modules)

    if mods:
        print(", ".join(mods), end="")
    """

    output = check_output([sys.executable, '-c', dedent(check)])

    assert output == b""


def test_limited_panel_imports():
    check = """\
    import sys
    import panel

    found = {k for k in sys.modules if k.startswith("panel")}
    expected = {
        "panel",
        "panel.__version",
        "panel._version",
        "panel.config",
        "panel.depends",
        "panel.util",
        "panel.util.checks",
        "panel.util.parameters",
    }
    mods = found - expected
    if mods:
        print(", ".join(mods), end="")
    """

    output = check_output([sys.executable, '-c', dedent(check)])

    assert output == b""

@pytest.mark.parametrize("mod_name", ["panel", "panel.io", "panel.pane", "panel.widgets"])
def test_lazy_import(mod_name):
    mod = import_module(mod_name)
    assert mod.__dir__() == list(mod.__all__)

    check = f"""\
    import {mod_name} as mod
    a, b, c = set(mod.__all__), set(mod._attrs), set(mod.__dict__)

    # Check no overlap between b and c
    if b & c:
        print("Failed: b and c overlap: ", end="")
        print(", ".join(b & c), end="")
    # Check if all imports are either directly imported or in attrs
    if a - (b | c):
        print("Failed: a - (b | c): ", end="")
        print(", ".join(a - (b | c)), end="")
    """
    output = check_output([sys.executable, '-c', dedent(check)])
    assert output == b""

    for n in mod._attrs:
        assert getattr(mod, n)
