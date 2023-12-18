import os
import time

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import (
    linux_only, run_panel_serve, wait_for_port, write_file,
)

pytestmark = pytest.mark.ui


@linux_only
def test_autoreload_app(py_file, port, page):
    app = "import panel as pn; pn.Row('Example 1').servable()"
    app2 = "import panel as pn; pn.Row('Example 2').servable()"
    write_file(app, py_file.file)

    app_name = os.path.basename(py_file.name)[:-3]

    with run_panel_serve(["--port", str(port), '--autoreload', py_file.name]) as p:
        port = wait_for_port(p.stdout)
        time.sleep(0.2)

        page.goto(f"http://localhost:{port}/{app_name}")
        expect(page.locator(".markdown")).to_have_text("Example 1")

        # Timeout to ensure websocket is initialized
        time.sleep(1.0)

        write_file(app2, py_file.file)
        expect(page.locator(".markdown")).to_have_text('Example 2')
