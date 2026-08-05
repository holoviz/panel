#!/usr/bin/env python3
"""
Fail fast if the JupyterLab / pyviz_comms / Panel server-extension stack
does not match the versions expected for JupyterLab 4.4–4.6 support.

Usage:
  python scripts/check_jupyterlab_stack.py
  python scripts/check_jupyterlab_stack.py --expect-jl 4.5
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

from packaging.version import Version


MIN_PYVIZ_COMMS = Version("3.0.2")
SUPPORTED_JL_MAJOR_MINOR = {(4, 4), (4, 5), (4, 6)}


def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    # jupyter CLI often prints extension tables to stderr
    combined = "\n".join(part for part in (result.stdout, result.stderr) if part)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\n"
            f"output:\n{combined}"
        )
    return combined


def check_pyviz_comms() -> Version:
    import pyviz_comms

    version = Version(pyviz_comms.__version__)
    if version < MIN_PYVIZ_COMMS:
        raise SystemExit(
            f"pyviz_comms {version} is too old; need >={MIN_PYVIZ_COMMS} for JupyterLab 4.4–4.6"
        )
    print(f"OK pyviz_comms {version}")
    return version


def check_jupyterlab(expect_jl: str | None) -> Version:
    import jupyterlab

    version = Version(jupyterlab.__version__)
    major_minor = (version.major, version.minor)
    if major_minor not in SUPPORTED_JL_MAJOR_MINOR:
        raise SystemExit(
            f"jupyterlab {version} is outside supported minors "
            f"{sorted(SUPPORTED_JL_MAJOR_MINOR)} (4.4–4.6)"
        )
    if expect_jl is not None:
        expected = tuple(int(part) for part in expect_jl.split(".")[:2])
        if major_minor != expected:
            raise SystemExit(
                f"jupyterlab {version} does not match expected {expect_jl}.*"
            )
    print(f"OK jupyterlab {version}")
    return version


def check_panel_extension_points() -> None:
    from panel import _jupyter_server_extension_points

    points = _jupyter_server_extension_points()
    if points != [{"module": "panel.io.jupyter_server_extension"}]:
        raise SystemExit(f"Unexpected extension points: {points!r}")
    print("OK panel._jupyter_server_extension_points")


def check_server_extension_enabled() -> None:
    try:
        out = _run([sys.executable, "-m", "jupyter", "server", "extension", "list"])
    except RuntimeError as exc:
        print(f"WARN could not list server extensions: {exc}")
        return
    if "panel.io.jupyter_server_extension" not in out:
        # Not fatal before enable step; warn so CI can enable then re-check.
        print(
            "WARN panel.io.jupyter_server_extension not listed yet "
            "(enable with: jupyter server extension enable "
            "panel.io.jupyter_server_extension --sys-prefix)"
        )
        return
    print("OK panel.io.jupyter_server_extension listed")


def check_labextension() -> None:
    try:
        out = _run([sys.executable, "-m", "jupyter", "labextension", "list"])
    except RuntimeError as exc:
        print(f"WARN could not list labextensions: {exc}")
        return
    if re.search(r"@pyviz/jupyterlab_pyviz", out) is None:
        print(
            "WARN @pyviz/jupyterlab_pyviz not found in labextension list "
            "(install pyviz_comms >= 3.0.2 in the JupyterLab environment)"
        )
        return
    print("OK @pyviz/jupyterlab_pyviz present")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expect-jl",
        default=None,
        help="Expected JupyterLab major.minor (e.g. 4.5)",
    )
    parser.add_argument(
        "--require-enabled",
        action="store_true",
        help="Fail if the Panel server extension is not enabled",
    )
    args = parser.parse_args(argv)

    check_pyviz_comms()
    check_jupyterlab(args.expect_jl)
    check_panel_extension_points()
    if args.require_enabled:
        out = _run([sys.executable, "-m", "jupyter", "server", "extension", "list"])
        if "panel.io.jupyter_server_extension" not in out:
            raise SystemExit("panel.io.jupyter_server_extension is not enabled")
        print("OK panel.io.jupyter_server_extension enabled")
    else:
        check_server_extension_enabled()
    check_labextension()
    print("JupyterLab stack check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
