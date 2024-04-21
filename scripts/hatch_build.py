from __future__ import annotations

import json
import os
import sys
import typing as t

from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

BASE_DIR = Path(__file__).parents[1]


def build_paneljs():
    from bokeh.ext import build

    print("Building custom models:")
    panel_dir = BASE_DIR / "panel"
    build(panel_dir)
    print("Bundling custom model resources:")
    if sys.platform != "win32":
        # npm can cause non-blocking stdout; so reset it just in case
        import fcntl

        flags = fcntl.fcntl(sys.stdout, fcntl.F_GETFL)
        fcntl.fcntl(sys.stdout, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)


def clean_js_version(version):
    version = version.replace("-", "")
    for dev in ("a", "b", "rc"):
        version = version.replace(dev + ".", dev)
    return version


def validate_js_version(version):
    # TODO: Double check the logic in this function
    version = version.split(".dev")[0]
    with open("./panel/package.json") as f:
        package_json = json.load(f)
    js_version = package_json["version"]
    version = version.split("+")[0]
    if any(dev in version for dev in ("a", "b", "rc")) and "-" not in js_version:
        raise ValueError(f"panel.js dev versions ({js_version}) must separate dev suffix with a dash, e.g. v1.0.0rc1 should be v1.0.0-rc.1.")
    if version != "None" and version != clean_js_version(js_version):
        raise ValueError(f"panel.js version ({js_version}) does not match panel version ({version}). Cannot build release.")


class BuildHook(BuildHookInterface):
    """The hatch jupyter builder build hook."""

    PLUGIN_NAME = "install"

    def initialize(self, version: str, build_data: dict[str, t.Any]) -> None:
        """Initialize the plugin."""
        if self.target_name not in ["wheel", "sdist"]:
            return

        validate_js_version(self.metadata.version)
        build_paneljs()

        sys.path.insert(0, str(BASE_DIR))
        from panel.compiler import bundle_resources

        bundle_resources(verbose=True)
