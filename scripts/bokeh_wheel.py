"""
Shared helper that strips the bundled JavaScript from a Bokeh wheel so
it can be served to Pyodide, which loads BokehJS from the page instead.
"""

import os
import pathlib
import zipfile

_STRIPPED_EXTENSIONS = (".js", ".d.ts", ".tsbuildinfo")


def strip_bokeh_wheel(wheel: str | os.PathLike, out_dir: str | os.PathLike) -> pathlib.Path:
    """
    Writes a copy of ``wheel`` without the BokehJS bundles to ``out_dir``
    and returns its path. The templates are kept since Bokeh renders them
    in Python.
    """
    wheel = pathlib.Path(wheel)
    out = pathlib.Path(out_dir) / wheel.name
    with zipfile.ZipFile(wheel, "r") as zin, zipfile.ZipFile(out, "w") as zout:
        for item in zin.infolist():
            filename = item.filename
            if not filename.startswith("bokeh/core/_templates") and (
                filename.endswith("bokeh.json") or filename.endswith(_STRIPPED_EXTENSIONS)
            ):
                continue
            zout.writestr(item, zin.read(filename))
    return out
