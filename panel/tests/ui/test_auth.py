import os
import pathlib
import shutil
import subprocess
import threading
import time

from contextlib import contextmanager

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect
from tornado.netutil import bind_sockets

from panel.config import config
from panel.io.state import state
from panel.pane import Markdown
from panel.tests.util import (
    linux_only, reverse_proxy, run_panel_serve, serve_component, wait_for_port,
    wait_until, write_file,
)

pytestmark = pytest.mark.ui
auth_check = pytest.mark.skipif('PANEL_TEST_AUTH' not in os.environ, reason='PANEL_TEST_AUTH environment variable is required to run this test')


def _port_is_free(port):
    # Bind like the server does (every IPv4 and IPv6 interface), so a listener on
    # [::]:port is detected as well.
    try:
        sockets = bind_sockets(int(port))
    except OSError:
        return False
    for sock in sockets:
        sock.close()
    return True


def _describe_listeners(port):
    out = []
    for cmd in (['ss', '-ltnp'], ['ss', '-ltn6p'], ['lsof', '-nP', '-i', f':{port}']):
        if shutil.which(cmd[0]) is None:
            out.append(f'$ {" ".join(cmd)}\n{cmd[0]} is not available')
            continue
        res = subprocess.run(cmd, capture_output=True, text=True)
        out.append(f'$ {" ".join(cmd)}\n{res.stdout}{res.stderr}')
    return '\n'.join(out)


def _describe_processes():
    res = subprocess.run(['ps', '-eo', 'pid,ppid,etimes,args'], capture_output=True, text=True)
    lines = res.stdout.splitlines()
    return '\n'.join(
        l[:200] for l in lines[:1] + [l for l in lines[1:] if any(k in l for k in ('caddy', 'pytest', 'xdist', 'panel'))]
    )


def _wait_for_free_port(port, timeout=30):
    # The Auth0 callback URL pins the port, so it cannot be swapped for an ephemeral one
    try:
        wait_until(lambda: _port_is_free(port), timeout=timeout * 1000, interval=500)
    except Exception:
        pytest.fail(f'Port {port} is still in use after {timeout}s, listeners:\n{_describe_listeners(port)}')


def _sample_port_sockets(port, stop, samples):
    # Sockets in any state (including TIME_WAIT and outgoing connections) that
    # use the port as local port; they block a bind without being listeners.
    ss = shutil.which('ss')
    if ss is None:
        return
    last = None
    while not stop.is_set():
        res = subprocess.run(
            [ss, '-tanpH', f'sport = :{port}'], capture_output=True, text=True
        )
        current = res.stdout.strip()
        if current and current != last:
            samples.append(f'{time.strftime("%H:%M:%S")}\n{current}')
        last = current
        stop.wait(0.05)


@contextmanager
def _report_listeners_on_failure(port):
    stop, samples = threading.Event(), []
    sampler = threading.Thread(target=_sample_port_sockets, args=(port, stop, samples), daemon=True)
    sampler.start()
    try:
        yield
    except pytest.fail.Exception as e:
        stop.set()
        sampler.join()
        try:
            port_range = pathlib.Path('/proc/sys/net/ipv4/ip_local_port_range').read_text().strip()
        except OSError:
            port_range = 'unknown'
        observed = '\n'.join(samples) or 'none observed'
        pytest.fail(
            f'{e}\n\nSockets with local port {port} observed during startup:\n{observed}\n\n'
            f'ip_local_port_range: {port_range}\n\n'
            f'This process: pid={os.getpid()} worker={os.environ.get("PYTEST_XDIST_WORKER")}\n'
            f'Processes:\n{_describe_processes()}\n\n'
            f'Listeners on port {port} after the failure:\n{_describe_listeners(port)}',
            pytrace=False
        )
    finally:
        stop.set()


def _auth0_login(page, user, password):
    # Auth0's login page may re-render its inputs while hydrating, wiping values filled too early
    page.wait_for_load_state('networkidle')
    username = page.locator('input[name="username"]')
    password_input = page.locator('input[name="password"]')
    username.fill(user)
    password_input.fill(password)
    expect(username).not_to_have_value('')
    expect(password_input).not_to_have_value('')
    page.get_by_role("button", name="Continue", exact=True).click(force=True)

@pytest.mark.internet
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

@pytest.mark.internet
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
        expect(page.locator('input[type="password"]')).to_be_visible()
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
    _wait_for_free_port(port)
    with run_panel_serve(cmd) as p:
        with _report_listeners_on_failure(port):
            served_port = wait_for_port(p.stdout)
        page.goto(f"http://localhost:{served_port}")

        _auth0_login(page, auth0_user, auth0_password)

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
    _wait_for_free_port(proxy)
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

            _auth0_login(page, auth0_user, auth0_password)

            expect(page.locator('.markdown')).to_have_text(auth0_user, timeout=10000)

@pytest.mark.internet
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


@pytest.mark.internet
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


@pytest.mark.internet
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


@pytest.mark.internet
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
