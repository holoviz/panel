"""Playwright checks for the built homepage.

These run against dist/, not the dev server, because the two things most likely to break are
properties of the production output: the prerendered HTML has to hydrate without React
complaining, and the interactive parts have to keep working after it does.

    pixi run -e homepage homepage-build
    pixi run -e homepage homepage-test
"""

from __future__ import annotations

import http.server
import re
import socket
import threading

from pathlib import Path

import pytest

from playwright.sync_api import ConsoleMessage, Page, expect

DIST = Path(__file__).resolve().parent.parent / 'dist'


@pytest.fixture(scope='session')
def site() -> str:
    if not (DIST / 'index.html').exists():
        pytest.skip(f'{DIST} has not been built')

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(DIST), **kwargs)

        def log_message(self, *args):
            pass

    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]

    server = http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f'http://127.0.0.1:{port}'
    finally:
        server.shutdown()


@pytest.fixture
def home(page: Page, site: str) -> Page:
    page.goto(site, wait_until='networkidle')
    return page


def test_prerendered_without_javascript(page: Page, site: str) -> None:
    """The headline must be in the HTML the server sends, not painted in by the bundle."""
    page.route('**/*.js', lambda route: route.abort())
    page.goto(site, wait_until='domcontentloaded')
    expect(page.get_by_role('heading', level=1)).to_contain_text('keep their shape')


def test_hydrates_without_console_errors(page: Page, site: str) -> None:
    problems: list[str] = []

    def record(msg: ConsoleMessage) -> None:
        if msg.type in ('error', 'warning'):
            problems.append(msg.text)

    page.on('console', record)
    page.on('pageerror', lambda e: problems.append(str(e)))
    page.goto(site, wait_until='networkidle')
    # A hydration mismatch is reported after the first commit, so give React a beat.
    page.wait_for_timeout(600)
    assert not problems, problems


def test_hero_chart_responds_to_the_widgets(home: Page) -> None:
    curve = home.locator('[data-hero-region="bind"] path').last
    before = curve.get_attribute('d')

    home.get_by_label('Smoothing window in days').fill('75')
    home.wait_for_timeout(200)
    windowed = curve.get_attribute('d')
    assert windowed != before
    expect(home.locator('[data-hero-region="widgets"]')).to_contain_text('75 days')

    home.get_by_role('button', name='NVDA').click()
    home.wait_for_timeout(200)
    assert curve.get_attribute('d') != windowed


def test_code_row_hover_recedes_the_other_regions(home: Page) -> None:
    """Hovering a line dims the parts of the app that line did not produce."""
    widgets = home.locator('[data-hero-region="widgets"]')
    chart = home.locator('[data-hero-region="bind"]')

    def opacity(region) -> str:
        return region.evaluate('e => getComputedStyle(e).opacity')

    assert (opacity(widgets), opacity(chart)) == ('1', '1')

    home.locator('[data-hero-row="widgets"]').hover()
    home.wait_for_timeout(300)
    assert opacity(widgets) == '1'
    assert float(opacity(chart)) < 0.5

    home.locator('[data-hero-row="bind"]').hover()
    home.wait_for_timeout(300)
    assert float(opacity(widgets)) < 0.5
    assert opacity(chart) == '1'

    # The layout line produced the whole app, so nothing recedes for it.
    home.locator('[data-hero-row="layout"]').hover()
    home.wait_for_timeout(300)
    assert (opacity(widgets), opacity(chart)) == ('1', '1')


def test_the_rerun_contrast_still_contrasts(home: Page) -> None:
    """The section only makes its point if both traces list the same blocks and fewer re-run.

    A copy edit that dropped a block from one column, or marked them all as running, would
    leave the section looking fine and saying nothing.
    """
    def blocks(trace: str) -> tuple[int, int]:
        scope = home.locator(f'[data-trace="{trace}"]')
        return scope.locator('[data-block]').count(), scope.locator('[data-runs]').count()

    listed, rerun_runs = blocks('rerun')
    also_listed, panel_runs = blocks('panel')

    assert listed == also_listed > 0, 'the two traces have to be the same app'
    assert rerun_runs == listed, 'the top-to-bottom column re-runs everything'
    assert 0 < panel_runs < rerun_runs


def test_selecting_a_plotting_library_changes_the_picture(home: Page) -> None:
    shown = home.locator('#pane-panel img')
    matplotlib = shown.get_attribute('src')
    assert matplotlib and 'Matplotlib' in matplotlib

    home.get_by_role('tab', name='Deck.gl', exact=True).click()
    expect(shown).to_have_attribute('src', re.compile('DeckGL'))
    expect(home.locator('#pane-panel')).to_contain_text('pn.ui.DeckGL')


def test_every_thumbnail_loads(home: Page) -> None:
    """The pictures are remote, and a renamed reference page turns one into a blank tile.

    Needs the network: the reference and gallery thumbnails are served from
    assets.holoviz.org rather than bundled, so this fails offline.
    """
    home.get_by_role('tab', name='ipywidgets', exact=True).click()
    home.wait_for_timeout(200)
    # The component tiles load lazily, so they have to be scrolled past first.
    home.evaluate("""async () => {
        for (let y = 0; y < document.body.scrollHeight; y += 400) {
            window.scrollTo(0, y)
            await new Promise((r) => setTimeout(r, 40))
        }
    }""")
    home.wait_for_load_state('networkidle')
    broken = home.eval_on_selector_all(
        'img', 'els => els.filter(e => !e.naturalWidth).map(e => e.currentSrc || e.src)'
    )
    assert not broken, broken


def test_install_command_copies(home: Page) -> None:
    home.context.grant_permissions(['clipboard-read', 'clipboard-write'])
    copy = home.get_by_role('button', name='Copy')
    copy.click()
    expect(home.get_by_role('button', name='Copied')).to_be_visible()
    assert home.evaluate('navigator.clipboard.readText()') == 'pip install panel'


def test_every_focusable_element_shows_a_ring(home: Page) -> None:
    """MUI's ButtonBase sets `outline: 0`, so this regressed once and would again silently."""
    seen = []
    for _ in range(20):
        home.keyboard.press('Tab')
        seen.append(
            home.evaluate("""() => {
                const e = document.activeElement;
                const s = getComputedStyle(e);
                return [(e.getAttribute('aria-label') || e.textContent || '').slice(0, 30),
                        parseFloat(s.outlineWidth), s.outlineColor];
            }""")
        )
    assert seen, 'nothing took focus'
    ringless = [(label, colour) for label, width, colour in seen if width < 1]
    assert not ringless, ringless

    # Inside the hero the surfaces are saturated blue, so the ring switches to the knockout.
    knockout = 'rgb(238, 238, 238)'
    inverted = [colour for label, _, colour in seen if label in ('Volatility', 'AAPL')]
    assert inverted and all(c == knockout for c in inverted), inverted


def test_no_horizontal_overflow_on_a_phone(page: Page, site: str) -> None:
    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto(site, wait_until='networkidle')
    scroll_width, client_width = page.evaluate(
        '() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]'
    )
    assert scroll_width <= client_width + 1


def test_docs_links_are_absolute_and_versioned(home: Page) -> None:
    """The homepage is unversioned, so every docs link has to name a version explicitly."""
    hrefs = home.eval_on_selector_all(
        'a[href]', 'els => els.map(e => e.getAttribute("href"))'
    )
    internal = [h for h in hrefs if h.startswith('/')]
    assert internal, 'expected some site-internal links'
    assert all(h == '/' or h.startswith('/en/docs/') for h in internal), internal
