import sys

from subprocess import check_output
from textwrap import dedent


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
