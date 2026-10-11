"""Render the README's pictures from the built homepage into doc/_static/readme/.

Run after a homepage build and commit the result; the README links to these files on main,
because PyPI renders the same README and cannot resolve relative paths:

    pixi run -e homepage homepage-build
    python doc/homepage/scripts/readme_images.py

Each picture is taken in light and dark, so the README can switch with GitHub's theme.
"""

from __future__ import annotations

import functools
import http.server
import io
import socket
import threading

from pathlib import Path

from PIL import Image
from playwright.sync_api import Page, sync_playwright

HOMEPAGE = Path(__file__).resolve().parent.parent
DIST = HOMEPAGE / 'dist'
OUT = HOMEPAGE.parent / '_static' / 'readme'

VIEWPORT = {'width': 1280, 'height': 900}
# GitHub's README column is about 900 px wide, so 1800 px covers a 2x display.
WIDTH = 1800

# Less than the 24 px gap between the hero app and its code, so no border bleeds in.
PAD = 16


def clip(selector: str, end: int) -> str:
    """
    Clip to children 1 to `end` of a section's container. Child 0 is the heading, which the
    README has as text, and what follows `end` is code or links, which a picture cannot copy
    or click.
    """
    return f"""() => {{
        const kids = [...document.querySelector('{selector}').querySelector('.MuiContainer-root').children].slice(1, {end})
        const first = kids[0].getBoundingClientRect(), last = kids[kids.length - 1].getBoundingClientRect()
        const left = Math.min(...kids.map((k) => k.getBoundingClientRect().left))
        const right = Math.max(...kids.map((k) => k.getBoundingClientRect().right))
        return {{x: left - {PAD}, y: first.top + window.scrollY - {PAD},
                width: right - left + 2 * {PAD}, height: last.bottom - first.top + 2 * {PAD}}}
    }}"""


# The hero app and the rerun contrast, the two parts of the page whose argument is visual.
# Everything else the README says in text, or with the homepage's screenshots in src/assets/.
SHOTS = {'hero': clip('main section', 2), 'execution': clip('#execution', -1)}


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        return probe.getsockname()[1]


def settle(page: Page) -> None:
    # The sticky header would otherwise sit on top of whatever is scrolled under it.
    page.add_style_tag(content='header { position: static !important }')
    page.evaluate("""async () => {
        const imgs = [...document.querySelectorAll('img')]
        imgs.forEach((i) => { i.loading = 'eager' })
        await Promise.all(imgs.map((i) => i.decode().catch(() => null)))
    }""")
    page.wait_for_timeout(500)


def save(png: bytes, path: Path) -> None:
    image = Image.open(io.BytesIO(png)).convert('RGB')
    if image.width > WIDTH:
        image = image.resize((WIDTH, round(image.height * WIDTH / image.width)), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, 'WEBP', quality=86, method=6)
    print(f'{path.relative_to(HOMEPAGE.parent.parent)}  {path.stat().st_size / 1024:.0f} kB')  # noqa: T201


def main() -> None:
    if not (DIST / 'index.html').exists():
        raise SystemExit(f'{DIST} has not been built')
    port = free_port()

    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(('127.0.0.1', port), functools.partial(Quiet, directory=str(DIST)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for scheme in ('light', 'dark'):
                page = browser.new_page(viewport=VIEWPORT, device_scale_factor=2, color_scheme=scheme)
                page.goto(f'http://127.0.0.1:{port}/', wait_until='networkidle')
                settle(page)
                for name, clip in SHOTS.items():
                    box = page.evaluate(clip)
                    save(page.screenshot(clip=box, full_page=True), OUT / f'{name}-{scheme}.webp')
                page.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
