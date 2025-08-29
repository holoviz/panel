import os
import pathlib
import time

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.config import config
from panel.io.state import state
from panel.pane import Markdown
from panel.tests.util import (
    linux_only, reverse_proxy, run_panel_serve, serve_component, wait_for_port,
    wait_until, write_file,
)

pytestmark = pytest.mark.ui
auth_check = pytest.mark.skipif('PANEL_TEST_AUTH' not in os.environ, reason='PANEL_TEST_AUTH environment variable is required to run this test')

@linux_only
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

@linux_only
@pytest.mark.parametrize('prefix', ['', 'prefix'])
def test_basic_auth_via_proxy(py_file, page, prefix, reverse_proxy):
    app = "import panel as pn; pn.pane.Markdown(pn.state.user).servable(title='A')"
    write_file(app, py_file.file)

    app_name = os.path.basename(py_file.name)[:-3]

    port, proxy = reverse_proxy
    cmd = [
        "--port", str(port), "--basic-auth", "my_password", "--cookie-secret", "secret", py_file.name,
        "--root-path", "/proxy/", "--allow-websocket-origin", f"localhost:{proxy}"
    ]
    if prefix:
        app_name = f'{prefix}/{app_name}'
        cmd += ['--prefix', prefix]
    with run_panel_serve(cmd) as p:
        wait_for_port(p.stdout)
        page.goto(f"http://localhost:{proxy}/proxy/{app_name}")
        page.locator('input[name="username"]').fill("test_user")
        page.locator('input[name="password"]').fill("my_password")
        page.get_by_role("button").click(force=True)

        expect(page.locator('.markdown')).to_have_text('test_user', timeout=10000)


@linux_only
@auth_check
@pytest.mark.skipif('OKTA_OAUTH_KEY' not in os.environ, reason='OKTA_OAUTH_KEY environment variable is required to run this test')
@pytest.mark.xdist_group("auth")
def test_okta_oauth(py_file, page):
    app = "import panel as pn; pn.pane.Markdown(pn.state.user).servable(title='A')"
    write_file(app, py_file.file)

    port = os.environ.get('OKTA_PORT', '5703')
    cookie_secret = os.environ['OAUTH_COOKIE_SECRET']
    encryption_key = os.environ['OAUTH_ENCRYPTION_KEY']
    oauth_key = os.environ['OKTA_OAUTH_KEY']
    oauth_secret = os.environ['OKTA_OAUTH_SECRET']
    extra_params = os.environ['OKTA_OAUTH_EXTRA_PARAMS']
    okta_user = os.environ['OKTA_OAUTH_USER']
    okta_password = os.environ['OKTA_OAUTH_PASSWORD']
    cmd = [
        "--port", port, "--oauth-provider", "okta", "--oauth-key", oauth_key,
        "--oauth-secret", oauth_secret, "--cookie-secret", cookie_secret,
        "--oauth-encryption-key", encryption_key, "--oauth-extra-params", extra_params,
        py_file.name
    ]
    with run_panel_serve(cmd) as p:
        port = wait_for_port(p.stdout)
        page.goto(f"http://localhost:{port}")

        page.locator('input[name="identifier"]').fill(okta_user)
        page.locator('input[type="submit"]').click(force=True)
        page.locator('input[type="password"]').fill(okta_password)
        page.locator('input[type="submit"]').click(force=True)

        expect(page.locator('.markdown')).to_have_text(okta_user, timeout=10000)


@linux_only
@auth_check
@pytest.mark.skipif('AZURE_OAUTH_KEY' not in os.environ, reason='AZURE_OAUTH_KEY environment variable is required to run this test')
@pytest.mark.xdist_group("auth")
def test_azure_oauth(py_file, page):
    app = "import panel as pn; pn.pane.Markdown(pn.state.user).servable(title='A')"
    write_file(app, py_file.file)

    port = os.environ.get('AZURE_PORT', '5702')
    cookie_secret = os.environ['OAUTH_COOKIE_SECRET']
    encryption_key = os.environ['OAUTH_ENCRYPTION_KEY']
    oauth_key = os.environ['AZURE_OAUTH_KEY']
    oauth_secret = os.environ['AZURE_OAUTH_SECRET']
    azure_user = os.environ['AZURE_OAUTH_USER']
    azure_password = os.environ['AZURE_OAUTH_PASSWORD']
    cmd = [
        "--port", port, "--oauth-provider", "azure", "--oauth-key", oauth_key,
        "--oauth-secret", oauth_secret, "--cookie-secret", cookie_secret,
        "--oauth-encryption-key", encryption_key,
        py_file.name
    ]
    with run_panel_serve(cmd) as p:
        port = wait_for_port(p.stdout)
        page.goto(f"http://localhost:{port}")

        page.locator('input[type="email"]').fill(azure_user)
        page.locator('input[type="submit"]').click(force=True)

        expect(page.locator('input[type="submit"]')).to_have_attribute('value', 'Next')
        time.sleep(1) # Loading password page is slow
        page.locator('input[type="password"]').fill(azure_password)
        page.locator('button[type="submit"]').click(force=True)
        page.locator('button[type="submit"][id="acceptButton"]').click(force=True)  # Stay signed in
        expect(page.locator('.markdown')).to_have_text(f'live.com#{azure_user}', timeout=10000)


@linux_only
@auth_check
@pytest.mark.skipif('AUTH0_OAUTH_KEY' not in os.environ, reason='AUTH0_OAUTH_KEY environment variable is required to run this test')
@pytest.mark.xdist_group("auth")
def test_auth0_oauth(py_file, page):
    app = "import panel as pn; pn.pane.Markdown(pn.state.user).servable(title='A')"
    write_file(app, py_file.file)

    port = os.environ.get('AUTH0_PORT', '5701')
    cookie_secret = os.environ['OAUTH_COOKIE_SECRET']
    encryption_key = os.environ['OAUTH_ENCRYPTION_KEY']
    oauth_key = os.environ['AUTH0_OAUTH_KEY']
    oauth_secret = os.environ['AUTH0_OAUTH_SECRET']
    extra_params = os.environ['AUTH0_OAUTH_EXTRA_PARAMS']
    auth0_user = os.environ['AUTH0_OAUTH_USER']
    auth0_password = os.environ['AUTH0_OAUTH_PASSWORD']
    cmd = [
        "--port", port, "--oauth-provider", "auth0", "--oauth-key", oauth_key,
        "--oauth-secret", oauth_secret, "--cookie-secret", cookie_secret,
        "--oauth-encryption-key", encryption_key, "--oauth-extra-params", extra_params,
        py_file.name
    ]
    with run_panel_serve(cmd) as p:
        port = wait_for_port(p.stdout)
        page.goto(f"http://localhost:{port}")

        page.locator('input[name="username"]').fill(auth0_user)
        page.locator('input[name="password"]').fill(auth0_password)
        page.get_by_role("button", name="Continue", exact=True).click(force=True)

        expect(page.locator('.markdown')).to_have_text(auth0_user, timeout=10000)


@linux_only
@auth_check
@pytest.mark.skipif('AUTH0_OAUTH_KEY' not in os.environ, reason='AUTH0_OAUTH_KEY environment variable is required to run this test')
@pytest.mark.xdist_group("auth")
def test_auth0_oauth_via_proxy(py_file, page):
    app = "import panel as pn; pn.pane.Markdown(pn.state.user).servable(title='A')"
    write_file(app, py_file.file)

    proxy = os.environ.get('AUTH0_PORT', '5701')
    cookie_secret = os.environ['OAUTH_COOKIE_SECRET']
    encryption_key = os.environ['OAUTH_ENCRYPTION_KEY']
    oauth_key = os.environ['AUTH0_OAUTH_KEY']
    oauth_secret = os.environ['AUTH0_OAUTH_SECRET']
    extra_params = os.environ['AUTH0_OAUTH_EXTRA_PARAMS']
    auth0_user = os.environ['AUTH0_OAUTH_USER']
    auth0_password = os.environ['AUTH0_OAUTH_PASSWORD']
    with reverse_proxy(proxy_port=proxy) as (port, _):
        cmd = [
            "--port", port, "--oauth-provider", "auth0", "--oauth-key", oauth_key,
            "--oauth-secret", oauth_secret, "--cookie-secret", cookie_secret,
            "--oauth-encryption-key", encryption_key, "--oauth-extra-params", extra_params,
            "--allow-websocket-origin", f"localhost:{proxy}", "--root-path", "/proxy/",
            "--oauth-redirect-uri", f"http://localhost:{proxy}/proxy/login",
            py_file.name
        ]
        with run_panel_serve(cmd) as p:
            port = wait_for_port(p.stdout)
            page.goto(f"http://localhost:{port}")

            page.locator('input[name="username"]').fill(auth0_user)
            page.locator('input[name="password"]').fill(auth0_password)
            page.get_by_role("button", name="Continue", exact=True).click(force=True)

            expect(page.locator('.markdown')).to_have_text(auth0_user, timeout=10000)

@linux_only
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


@linux_only
@pytest.mark.parametrize('logout_template', [None, (pathlib.Path(__file__).parent / 'logout.html').absolute()])
def test_basic_auth_logout_via_proxy(py_file, page, logout_template, reverse_proxy):
    app = "import panel as pn; pn.pane.Markdown(pn.state.user).servable(title='A')"
    write_file(app, py_file.file)

    app_name = os.path.basename(py_file.name)[:-3]

    port, proxy = reverse_proxy
    cmd = [
        "--port", str(port), "--basic-auth", "my_password", "--cookie-secret",
        "secret", py_file.name, "--root-path", "/proxy/", "--allow-websocket-origin",
        f"localhost:{proxy}"
    ]
    if logout_template:
        cmd += ['--logout-template', str(logout_template)]
    with run_panel_serve(cmd) as p:
        wait_for_port(p.stdout)
        page.goto(f"http://localhost:{proxy}/proxy/{app_name}")

        page.locator('input[name="username"]').fill("test_user")
        page.locator('input[name="password"]').fill("my_password")
        page.get_by_role("button").click(force=True)

        expect(page.locator('.markdown')).to_have_text('test_user', timeout=10000)

        cookies = [cookie['name'] for cookie in page.context.cookies()]
        assert 'user' in cookies
        assert 'id_token' in cookies

        page.goto(f"http://localhost:{proxy}/proxy/logout")

        assert page.title() == ('Test Logout Page' if logout_template else 'Panel App | Logout')

        cookies = [cookie['name'] for cookie in page.context.cookies()]
        assert 'user' not in cookies
        assert 'id_token' not in cookies


@linux_only
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


@linux_only
def test_global_authorize_callback(page):
    users, sessions = [], []
    def authorize(user_info, uri):
        users.append(user_info['user'])
        return False

    def app():
        sessions.append(state.user)
        return Markdown('Page A')

    with config.set(authorize_callback=authorize):
        _, port = serve_component(page, app, basic_auth='my_password', cookie_secret='my_secret', wait=False)

        page.locator('input[name="username"]').fill("A")
        page.locator('input[name="password"]').fill("my_password")
        page.get_by_role("button").click(force=True)

        wait_until(lambda: len(users) == 1, page)
        assert users[0] == 'A'
        assert len(sessions) == 0
