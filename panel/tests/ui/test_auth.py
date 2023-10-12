import os
import pathlib

import pytest

try:
    from playwright.sync_api import expect
    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

from panel.config import config
from panel.pane import Markdown
from panel.tests.util import (
    run_panel_serve, serve_component, unix_only, wait_for_port, write_file,
)


@unix_only
@pytest.mark.parametrize('prefix', ['', 'prefix'])
def test_basic_auth(py_file, page, prefix):
    app = "import panel as pn; pn.pane.Markdown(pn.state.user).servable(title='A')"
    write_file(app, py_file.file)

    app_name = os.path.basename(py_file.name)[:-3]

    cmd = ["--port", "0", "--basic-auth", "my_password", "--cookie-secret", "secret", py_file.name]
    if prefix:
        app_name = f'{prefix}/{app_name}'
        cmd += ['--prefix', prefix]
    with run_panel_serve(cmd) as p:
        port = wait_for_port(p.stdout)
        page.goto(f"http://localhost:{port}/{app_name}")

        page.locator('input[name="username"]').fill("test_user")
        page.locator('input[name="password"]').fill("my_password")
        page.get_by_role("button").click(force=True)

        expect(page.locator('.markdown')).to_have_text('test_user', timeout=10000)


@unix_only
@pytest.mark.skipif('OKTA_OAUTH_KEY' not in os.environ, reason='Okta credentials not available')
def test_okta_oauth(py_file, page):
    app = "import panel as pn; pn.pane.Markdown(pn.state.user).servable(title='A')"
    write_file(app, py_file.file)

    app_name = os.path.basename(py_file.name)[:-3]

    cookie_secret = os.environ['OAUTH_COOKIE_SECRET']
    encryption_key = os.environ['OAUTH_ENCRYPTION_KEY']
    oauth_key = os.environ['OKTA_OAUTH_KEY']
    oauth_secret = os.environ['OKTA_OAUTH_SECRET']
    extra_params = os.environ['OKTA_OAUTH_EXTRA_PARAMS']
    okta_user = os.environ['OKTA_OAUTH_USER']
    okta_password = os.environ['OKTA_OAUTH_PASSWORD']
    cmd = [
        "--port", "5006", "--oauth-provider", "okta", "--oauth-key", oauth_key,
        "--oauth-secret", oauth_secret, "--cookie-secret", cookie_secret,
        "--oauth-encryption-key", encryption_key, "--oauth-extra-params", extra_params,
        py_file.name
    ]
    with run_panel_serve(cmd) as p:
        port = wait_for_port(p.stdout)
        page.goto(f"http://localhost:{port}/{app_name}")

        page.locator('input[name="username"]').fill(okta_user)
        page.locator('input[name="password"]').fill(okta_password)
        page.locator('input[type="submit"]').click(force=True)

        expect(page.locator('.markdown')).to_have_text(okta_user, timeout=10000)


@unix_only
@pytest.mark.skipif('AZURE_OAUTH_KEY' not in os.environ, reason='Azure credentials not available')
def test_azure_oauth(py_file, page):
    app = "import panel as pn; pn.pane.Markdown(pn.state.user).servable(title='A')"
    write_file(app, py_file.file)

    app_name = os.path.basename(py_file.name)[:-3]

    oauth_key = os.environ['AZURE_OAUTH_KEY']
    oauth_secret = os.environ['AZURE_OAUTH_SECRET']
    cookie_secret = os.environ['OAUTH_COOKIE_SECRET']
    azure_user = os.environ['AZURE_OAUTH_USER']
    azure_password = os.environ['AZURE_OAUTH_PASSWORD']
    encryption_key = os.environ['OAUTH_ENCRYPTION_KEY']
    cmd = [
        "--port", "5006", "--oauth-provider", "azure", "--oauth-key", oauth_key,
        "--oauth-secret", oauth_secret, "--cookie-secret", cookie_secret,
        "--oauth-encryption-key", encryption_key,
        py_file.name
    ]
    with run_panel_serve(cmd) as p:
        port = wait_for_port(p.stdout)
        page.goto(f"http://localhost:{port}/{app_name}")

        page.locator('input[type="email"]').fill(azure_user)
        page.locator('input[type="submit"]').click(force=True)
        page.locator('input[type="password"]').fill(azure_password)
        page.locator('input[type="submit"]').click(force=True)
        page.locator('input[type="submit"]').click(force=True)

        expect(page.locator('.markdown')).to_have_text(f'live.com#{azure_user}', timeout=10000)


@unix_only
@pytest.mark.parametrize('logout_template', [None, (pathlib.Path(__file__).parent / 'logout.html').absolute()])
def test_basic_auth_logout(py_file, page, logout_template):
    app = "import panel as pn; pn.pane.Markdown(pn.state.user).servable(title='A')"
    write_file(app, py_file.file)

    app_name = os.path.basename(py_file.name)[:-3]

    cmd = ["--port", "0", "--basic-auth", "my_password", "--cookie-secret", "secret", py_file.name]
    if logout_template:
        cmd += ['--logout-template', str(logout_template)]
    with run_panel_serve(cmd) as p:
        port = wait_for_port(p.stdout)
        page.goto(f"http://localhost:{port}/{app_name}")

        page.locator('input[name="username"]').fill("test_user")
        page.locator('input[name="password"]').fill("my_password")
        page.get_by_role("button").click(force=True)

        expect(page.locator('.markdown')).to_have_text('test_user', timeout=10000)

        cookies = [cookie['name'] for cookie in page.context.cookies()]
        assert 'user' in cookies
        assert 'id_token' in cookies

        page.goto(f"http://localhost:{port}/logout")

        assert page.title() == ('Test Logout Page' if logout_template else 'Panel App | Logout')

        cookies = [cookie['name'] for cookie in page.context.cookies()]
        assert 'user' not in cookies
        assert 'id_token' not in cookies


def test_authorize_callback_redirect(page):

    def authorize(user_info, uri):
        if uri == '/':
            user = user_info['user']
            if user == 'A':
                return '/a'
            elif user == 'B':
                return '/b'
            else:
                return False
        return True

    app1 = Markdown('Page A')
    app2 = Markdown('Page B')

    with config.set(authorize_callback=authorize):
        _, port = serve_component(page, {'a': app1, 'b': app2, '/': 'Index'}, basic_auth='my_password', cookie_secret='my_secret', wait=False)

        page.locator('input[name="username"]').fill("A")
        page.locator('input[name="password"]').fill("my_password")
        page.get_by_role("button").click(force=True)

        expect(page.locator(".markdown").locator("div")).to_have_text('Page A\n')

        page.goto(f"http://localhost:{port}/logout")

        page.goto(f"http://localhost:{port}/login")

        page.locator('input[name="username"]').fill("B")
        page.locator('input[name="password"]').fill("my_password")
        page.get_by_role("button").click(force=True)

        expect(page.locator(".markdown").locator("div")).to_have_text('Page B\n')
