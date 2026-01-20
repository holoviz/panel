"""
Script that removes large files from bokeh wheel and repackages it
to be included in the NPM bundle.
"""

import argparse
import os
import pathlib
import shutil
import subprocess
import zipfile

try:
    import tomllib
except ModuleNotFoundError:
    # Can be removed after 3.11 is the minimum version
    import tomli as tomllib

from packaging.requirements import Requirement

PANEL_BASE = pathlib.Path(__file__).parent.parent
PACKAGE_INFO = tomllib.loads((PANEL_BASE / "pyproject.toml").read_text())
bokeh_requirement = next(p for p in PACKAGE_INFO['build-system']['requires'] if "bokeh" in p.lower())
bokeh_dev = Requirement(bokeh_requirement).specifier.prereleases

parser = argparse.ArgumentParser()
parser.add_argument("out", default="panel/dist/wheels", nargs="?", help="Output dir")
parser.add_argument(
    "--no-deps",
    action="store_true",
    default=False,
    help="Don't install package dependencies.",
)
parser.add_argument(
    "--verify-clean",
    action="store_true",
    default=False,
    help="Check if panel folder is clean before running.",
)
args = parser.parse_args()

if args.verify_clean:
    # -n dry run, -d directories, -x remove ignored files
    output = subprocess.check_output(["git", "clean", "-nxd", "panel/"])
    if output:
        print(output.decode("utf-8"))
        msg = "Please clean the panel folder before running this script."
        raise RuntimeError(msg)
    else:
        print("panel folder is clean.")

command = ["pip", "wheel", "."]
if bokeh_dev:
    command.append("--pre")

if args.no_deps:
    command.append("--no-deps")
command.extend(["-w", str(PANEL_BASE / "build")])
print("command: ", " ".join(command))

out = PANEL_BASE / args.out
out.mkdir(exist_ok=True)
print("out dir: ", out)

sp = subprocess.Popen(command, env=dict(os.environ, PANEL_LITE="1"))
sp.wait()


panel_wheels = list(PANEL_BASE.glob("build/panel-*-py3-none-any.whl"))
if not panel_wheels:
    raise RuntimeError("Panel wheel not found.")
panel_wheel = sorted(panel_wheels)[-1]

with (
    zipfile.ZipFile(panel_wheel, "r") as zin,
    zipfile.ZipFile(out / os.path.basename(panel_wheel).replace(".dirty", ""), "w") as zout,
):
    for item in zin.infolist():
        filename = item.filename
        if filename.startswith("panel/tests"):
            continue
        buffer = zin.read(filename)
        if bokeh_dev and filename.startswith("panel-") and filename.endswith("METADATA"):
            lines = buffer.decode("utf-8").split("\n")
            lines = [
                f"Requires-Dist: {bokeh_requirement}"
                if line.startswith("Requires-Dist: bokeh")
                else line for line in lines
            ]
            buffer = "\n".join(lines).encode('utf-8')
        zout.writestr(item, buffer)

bokeh_wheels = PANEL_BASE.glob("build/bokeh-*-py3-none-any.whl")

if not bokeh_wheels:
    raise RuntimeError("Bokeh wheel not found.")
bokeh_wheel = sorted(bokeh_wheels)[-1]

zin = zipfile.ZipFile(bokeh_wheel, "r")

zout = zipfile.ZipFile(out / os.path.basename(bokeh_wheel), "w")
exts = [".js", ".d.ts", ".tsbuildinfo"]
for item in zin.infolist():
    filename = item.filename
    buffer = zin.read(filename)
    if not filename.startswith("bokeh/core/_templates") and (
        filename.endswith("bokeh.json") or any(filename.endswith(ext) for ext in exts)
    ):
        continue
    zout.writestr(item, buffer)

zout.close()
zin.close()

print(f"\nWheels where successfully written to {out}")
