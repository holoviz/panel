from __future__ import annotations

import json
import os
import sys
import typing as t

from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

BASE_DIR = Path(__file__).parent
GREEN, RED, RESET = "\033[0;32m", "\033[0;31m", "\033[0m"


def reset_stdout():
    if sys.platform == "win32":
        return
    # npm can cause non-blocking stdout; so reset it just in case
    import fcntl

    flags = fcntl.fcntl(sys.stdout, fcntl.F_GETFL)
    fcntl.fcntl(sys.stdout, fcntl.F_SETFL, flags & ~os.O_NONBLOCK)

def build_models():
    from bokeh.ext import build

    print(f"{GREEN}[PANEL]{RESET} Starting building custom models", flush=True)
    panel_dir = BASE_DIR / "panel"
    success = build(panel_dir)
    reset_stdout()

    if success:
        print(f"{GREEN}[PANEL]{RESET} Finished building custom models", flush=True)
    else:
        print(f"{RED}[PANEL]{RESET} Failed building custom models", flush=True)
        sys.exit(1)

def bundle_resources():
    sys.path.insert(0, str(BASE_DIR))
    from panel.compiler import bundle_resources

    print(f"{GREEN}[PANEL]{RESET} Starting bundling custom model resources", flush=True)
    try:
        bundle_resources()
        print(f"{GREEN}[PANEL]{RESET} Finished bundling custom model resources", flush=True)
    except Exception as e:
        print(f"{GREEN}[PANEL]{RESET} Failed bundling custom model resources", flush=True)
        raise e

def build_ui_bundle():
    if not (BASE_DIR / "panel" / "ui").is_dir():
        return

    sys.path.insert(0, str(BASE_DIR))
    from panel.io.compile import compile_components, find_module_bundles

    print(f"{GREEN}[PANEL]{RESET} Starting building panel.ui bundle", flush=True)
    try:
        bundles = find_module_bundles("panel.ui")
    except RuntimeError:
        bundles = {}
    if not bundles:
        # panel.ui declares no ESM components (yet), so there is nothing to bundle
        print(f"{GREEN}[PANEL]{RESET} No panel.ui components to bundle", flush=True)
        return
    errors = 0
    for bundle, components in bundles.items():
        ret = compile_components(
            components,
            outfile=bundle,
            file_loaders=["woff", "woff2"],
        )
        if ret != 0:
            errors += 1
        # compile_components reports some build failures on stdout without
        # signalling them in its return value, so check the artifact itself.
        if not (bundle.is_file() and bundle.stat().st_size):
            print(f"{RED}[PANEL]{RESET} {bundle} was not written", flush=True)
            errors += 1
    reset_stdout()

    if errors:
        print(f"{RED}[PANEL]{RESET} Failed building panel.ui bundle", flush=True)
        sys.exit(1)
    print(f"{GREEN}[PANEL]{RESET} Finished building panel.ui bundle", flush=True)

def clean_js_version(version):
    version = version.replace("-", "")
    for dev in ("a", "b", "rc"):
        version = version.replace(dev + ".", dev)
    return version


def validate_js_version(version):
    # TODO: Double check the logic in this function
    version = version.split(".post")[0]
    with open("./panel/package.json") as f:
        package_json = json.load(f)
    js_version = package_json["version"]
    version = version.split("+")[0]
    if any(dev in version for dev in ("a", "b", "rc")) and "-" not in js_version:
        raise ValueError(f"panel.js dev versions ({js_version}) must separate dev suffix with a dash, e.g. v1.0.0rc1 should be v1.0.0-rc.1.")
    if version != "None" and version != clean_js_version(js_version):
        raise ValueError(f"panel.js version ({js_version}) does not match panel version ({version}). Cannot build release.")


class BuildHook(BuildHookInterface):
    """The hatch build hook."""

    PLUGIN_NAME = "install"

    def initialize(self, version: str, build_data: dict[str, t.Any]) -> None:
        """Initialize the plugin."""
        if self.target_name not in ["wheel", "sdist"]:
            return

        validate_js_version(self.metadata.version)

        if "PANEL_LITE" not in os.environ:
            build_models()
            bundle_resources()
            if "PANEL_SKIP_UI_BUNDLE" not in os.environ:
                build_ui_bundle()
