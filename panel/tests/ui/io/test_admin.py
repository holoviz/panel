import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.config import config
from panel.io.state import state
from panel.tests.util import serve_and_wait

pytestmark = pytest.mark.ui

PASSWORD = 'admin-secret'


@pytest.fixture(autouse=True)
def admin_config_cleanup():
    values = {name: getattr(config, name) for name in ('_admin', '_admin_password')}
    try:
        yield
    finally:
        config.param.update(**values)
        state.session_info = {'total': 0, 'live': 0, 'sessions': {}}


def _serve_admin(page, prefix=''):
    port = serve_and_wait({'app': '# App'}, admin=True, prefix=prefix)
    base = f'http://127.0.0.1:{port}{prefix.rstrip("/")}'
    page.goto(f'{base}/app')
    expect(page.locator('h1')).to_contain_text('App')
    return base


def test_admin_navigation(page):
    base = _serve_admin(page)
    page.goto(f'{base}/admin')

    expect(page.get_by_role('heading', name='Overview')).to_be_visible()
    expect(page.get_by_text('Total Sessions')).to_be_visible()

    page.get_by_role('button', name='Logs').click()
    expect(page.get_by_role('heading', name='Logs')).to_be_visible()
    expect(page.locator('.tabulator-row').first).to_be_visible()

    page.get_by_role('button', name='Overview').click()
    expect(page.get_by_text('Total Sessions')).to_be_visible()


@pytest.mark.parametrize('prefix', ['', '/prefix'])
def test_admin_password_login_and_logout(page, prefix):
    config.admin_password = PASSWORD
    base = _serve_admin(page, prefix)

    page.goto(f'{base}/admin')
    expect(page).to_have_url(f'{base}/admin/login')

    page.fill('#password', 'wrong')
    page.click('button[type=submit]')
    expect(page.locator('#error-message')).to_have_text('Invalid password!')

    page.fill('#password', PASSWORD)
    page.click('button[type=submit]')
    expect(page).to_have_url(f'{base}/admin')
    expect(page.get_by_role('heading', name='Overview')).to_be_visible()

    page.locator('button:has-text("logout")').click()
    expect(page).to_have_url(f'{base}/admin/login')
    page.goto(f'{base}/admin')
    expect(page).to_have_url(f'{base}/admin/login')
