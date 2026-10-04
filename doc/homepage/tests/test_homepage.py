"""Playwright checks for the built homepage.

These run against dist/, not the dev server, because the two things most likely to break are
properties of the production output: the prerendered HTML has to hydrate without React
complaining, and the interactive parts have to keep working after it does.

    pixi run -e homepage homepage-build
    pixi run -e homepage homepage-test
"""

from __future__ import annotations

import http.server
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


def test_every_pane_and_component_has_a_picture(home: Page) -> None:
    expect(home.locator('#panes [data-tile]')).to_have_count(8)
    expect(home.locator('#components [data-tile]')).to_have_count(12)
    expect(home.locator('#panes')).to_contain_text('pn.ui.DeckGL')


def test_every_picture_loads_from_the_hashed_prefix(home: Page) -> None:
    """The edge redirector only passes /_home/ through, so a picture anywhere else 404s live."""
    # Lazy tiles only fetch near the viewport, so make them all eager and wait for each.
    images = home.evaluate("""async () => {
        const imgs = [...document.querySelectorAll('main img')]
        imgs.forEach((i) => { i.loading = 'eager' })
        await Promise.all(imgs.map((i) => i.decode().catch(() => null)))
        return imgs.map((i) => [i.getAttribute('src'), i.naturalWidth])
    }""")
    assert len(images) == 26
    assert not [src for src, width in images if not width], 'broken pictures'
    # Vite inlines anything under 4 kB as a data: URI, which needs no route at all.
    assert all(src.startswith(('/_home/', 'data:image/')) for src, _ in images), images


def test_featured_app_ends_level_with_its_neighbours(home: Page) -> None:
    """The featured screenshot stretches to the two tiles beside it rather than overhanging."""
    def bottom(name: str) -> float:
        box = home.locator(f'[data-gallery-app="{name}"]').bounding_box()
        return box['y'] + box['height']

    assert abs(bottom('gaia_million_star_atlas') - bottom('portfolio_analyzer')) <= 1


@pytest.mark.parametrize('width', [1440, 390])
def test_no_code_scrolls_sideways(page: Page, site: str, width: int) -> None:
    """Hero and growth snippets wrap rather than hiding the ends of their lines."""
    page.set_viewport_size({'width': width, 'height': 900})
    page.goto(site, wait_until='networkidle')
    clipped = page.eval_on_selector_all(
        '#growth pre, [data-hero-row] pre',
        'els => els.filter(e => e.scrollWidth > e.clientWidth + 1).map(e => e.textContent.slice(0, 40))',
    )
    assert not clipped, clipped


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


# What gh-pages serves at /PyodideServiceWorker.js today, trimmed to the behaviour that
# matters: it claims every page and answers from its cache first.
LEGACY_WORKER = """
self.addEventListener('install', (e) => self.skipWaiting())
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()))
self.addEventListener('fetch', (e) => e.respondWith((async () => {
  const cache = await caches.open('Panel-1.9.4')
  return (await cache.match(e.request)) || fetch(e.request)
})()))
"""


@pytest.mark.parametrize('script', ['/PyodideServiceWorker.js', '/pyodide/serviceWorker.js'])
def test_legacy_service_workers_retire_themselves(page: Page, site: str, script: str) -> None:
    """A worker left behind by the gh-pages site must give way to the retiring one on update."""
    legacy = {'active': True}

    def serve(route):
        if legacy['active']:
            route.fulfill(body=LEGACY_WORKER, content_type='text/javascript')
        else:
            route.continue_()

    page.context.route(f'**{script}', serve)
    page.goto(site, wait_until='networkidle')
    page.evaluate(
        """async (script) => {
            await (await caches.open('Panel-1.9.4')).put('/stale', new Response('old site'))
            const registration = await navigator.serviceWorker.register(script)
            const worker = registration.installing || registration.waiting || registration.active
            if (worker.state !== 'activated') {
                await new Promise((resolve) => worker.addEventListener('statechange', () => {
                    if (worker.state === 'activated') resolve()
                }))
            }
        }""",
        script,
    )

    legacy['active'] = False
    page.evaluate('async () => (await navigator.serviceWorker.getRegistrations())[0].update()')

    # The retiring worker reloads the pages it controlled, so poll in short evaluations.
    def state() -> list:
        try:
            return page.evaluate(
                """async () => [
                    (await navigator.serviceWorker.getRegistrations()).length,
                    (await caches.keys()).filter((name) => name.startsWith('Panel')),
                ]"""
            )
        except Exception:
            return [-1, ['navigating']]

    for _ in range(50):
        if state() == [0, []]:
            break
        page.wait_for_timeout(200)
    assert state() == [0, []]
