from __future__ import annotations

import pytest

from panel.tests.util import serve_component
from panel.widgets import Debugger

pytest.importorskip("playwright")

pytestmark = pytest.mark.ui


def test_tabulator_no_console_error(page):
    widget = Debugger()

    msgs, _ = serve_component(page, widget)

    page.wait_for_timeout(1000)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []
