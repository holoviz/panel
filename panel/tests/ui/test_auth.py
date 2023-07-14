import os

import pytest

try:
    from playwright.sync_api import expect
    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

from panel.tests.util import (
    run_panel_serve, unix_only, wait_for_port, write_file,
)


@unix_only
def test_basic_auth(py_file, page):
    app = "import panel as pn; pn.pane.Markdown(pn.state.user).servable(title='A')"
    write_file(app, py_file.file)

    app_name = os.path.basename(py_file.name)[:-3]

    with run_panel_serve(["--port", "0", "--basic-auth", "my_password", "--cookie-secret", "secret", py_file.name]) as p:
        port = wait_for_port(p.stdout)
        page.goto(f"http://localhost:{port}/{app_name}")

        page.locator('input[name="username"]').fill("test_user")
        page.locator('input[name="password"]').fill("my_password")
        page.get_by_role("button").click(force=True)

        expect(page.locator('.markdown')).to_have_text('test_user', timeout=10000)
