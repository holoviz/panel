"""
Prepares the Pyodide assets of the documentation build.

On an untagged commit the docs run against a locally built Panel wheel,
because the CDN only hosts wheels for released versions.
"""

import argparse
import glob
import pathlib
import shutil
import subprocess
import sys

PANEL_BASE = pathlib.Path(__file__).parent.parent
WHEELS_DIR = PANEL_BASE / "panel" / "dist" / "wheels"
BUILT_DOCS = PANEL_BASE / "builtdocs"


def is_tagged() -> bool:
    return subprocess.run(
        ["git", "describe", "--exact-match", "--tags", "HEAD"],
        cwd=PANEL_BASE, capture_output=True, check=False,
    ).returncode == 0


def wheels() -> None:
    if not is_tagged():
        subprocess.run(
            [sys.executable, "scripts/build_pyodide_wheels.py", "--panel-only"],
            cwd=PANEL_BASE, check=True,
        )
    if not WHEELS_DIR.is_dir():
        return
    out = BUILT_DOCS / "wheels"
    out.mkdir(parents=True, exist_ok=True)
    for wheel in WHEELS_DIR.glob("*.whl"):
        shutil.copy(wheel, out)


def convert() -> None:
    # VTK does not run in Pyodide.
    files = [
        f for f in sorted(glob.glob("examples/gallery/*.ipynb", root_dir=PANEL_BASE))
        if not pathlib.Path(f).name.startswith("vtk")
    ]
    files += sorted(glob.glob("doc/how_to/*/examples/*.md", root_dir=PANEL_BASE))
    subprocess.run(
        [
            "panel", "convert", *files,
            "--to", "pyodide-worker",
            "--out", "./builtdocs/pyodide/",
            "--pwa", "--index",
            "--requirements", "doc/pyodide_dependencies.json",
            "--panel-version", "auto" if is_tagged() else "local",
        ],
        cwd=PANEL_BASE, check=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["wheels", "convert"])
    args = parser.parse_args()
    {"wheels": wheels, "convert": convert}[args.command]()
