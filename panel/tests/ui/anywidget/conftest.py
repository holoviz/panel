"""
Shared fixtures for AnyWidget pane Playwright tests.

Each test file serves a Panel app (built from a research example or inline)
and uses Playwright to verify rendering, console errors, and bidirectional sync.

Pattern:
    1. Build a Panel app with pn.pane.AnyWidget(some_widget)
    2. serve_component(page, app) — starts in-process server, navigates Playwright
    3. Assert DOM content, check console errors, verify Python-side state
"""
from __future__ import annotations

import pathlib
import re

import pytest

pytest.importorskip("playwright")
pytest.importorskip("anywidget")

from panel.tests.util import serve_component, wait_until  # noqa: E402

pytestmark = pytest.mark.ui

EXAMPLES_DIR = pathlib.Path(__file__).parents[4] / "research" / "anywidget" / "examples"

# Console messages that are expected / benign and should not fail tests.
KNOWN_CONSOLE_MESSAGES = [
    "setting log level to:",
    "Websocket connection 0 is now open",
    "document idle at",
    "items were rendered successfully",
    "Automatic fallback to software WebGL has been deprecated",
    "[bokeh]",
    # SVG attribute warnings from wigglystuff canvas-based components
    "<svg> attribute height: Expected length",
    "<svg> attribute width: Expected length",
    # Split.js CDN library emits this when components are torn down
    "Event of type 'remove' not recognized",
]


def console_errors(msgs, *, ignore_known=True):
    """Filter console messages down to unexpected errors.

    Parameters
    ----------
    msgs : list[ConsoleMessage]
        Raw Playwright ConsoleMessage objects from ``serve_component``.
    ignore_known : bool
        If True (default), filter out messages matching KNOWN_CONSOLE_MESSAGES.

    Returns
    -------
    list[ConsoleMessage]
        Only error-level messages that are not in the known list.
    """
    errors = [m for m in msgs if m.type == "error"]
    if ignore_known:
        errors = [
            m for m in errors
            if not any(known in m.text for known in KNOWN_CONSOLE_MESSAGES)
        ]
    return errors


def assert_no_console_errors(msgs):
    """Assert that there are no unexpected console errors."""
    errors = console_errors(msgs)
    assert errors == [], (
        "Unexpected console errors:\n"
        + "\n".join(f"  [{e.type}] {e.text}" for e in errors)
    )


def wait_for_anywidget(page, timeout=10_000):
    """Wait for the AnyWidget ESM to render (the shadow root or first child appears)."""
    page.locator("[data-root-id]").first.wait_for(state="attached", timeout=timeout)
    page.wait_for_load_state("networkidle")
