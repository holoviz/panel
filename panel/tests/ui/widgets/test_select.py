import time

import pytest

from panel.io.server import serve
from panel.widgets import Select

pytestmark = pytest.mark.ui


def test_select_with_size(page, port):
    select = Select(options=['A', 'B', 'C'], size=4)

    serve(select, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    page.locator('option').nth(1).click()

    time.sleep(0.2)

    assert select.value == 'B'
