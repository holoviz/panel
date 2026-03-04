"""
Shared fixtures for AnyWidgetComponent example Playwright tests.

Reuses fixtures from the main anywidget conftest.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright")

from panel.tests.ui.anywidget.conftest import (  # noqa: E402, F401
    KNOWN_CONSOLE_MESSAGES,
    assert_no_console_errors,
    console_errors,
    wait_for_anywidget,
)

pytestmark = pytest.mark.ui
