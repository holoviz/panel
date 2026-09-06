"""Render public/og-image.png from scripts/og-card.html.

Run once and commit the result; nothing in the Vite build calls this. The card borrows the
headline and the hero's two chart paths out of the prerendered dist/index.html, so the social
preview cannot keep advertising a headline the page no longer has:

    pixi run homepage-build
    python doc/homepage/scripts/og-image.py

Set CHROME_PATH if Playwright's bundled headless shell is not installed locally.
"""

from __future__ import annotations

import os
import re
import sys
import tempfile

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
HOMEPAGE = HERE.parent
PRERENDERED = HOMEPAGE / 'dist' / 'index.html'
CARD = HERE / 'og-card.html'
OUT = HOMEPAGE / 'public' / 'og-image.png'


def from_prerender() -> dict[str, str]:
    """Pull the headline, and the hero chart's viewBox and two paths, out of the built page."""
    if not PRERENDERED.exists():
        sys.exit(f'{PRERENDERED} is missing; run the homepage build first.')
    html = PRERENDERED.read_text()
    title = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if not title:
        sys.exit('No h1 in the prerendered output; did the markup change?')
    chart = html.split('data-hero-region="bind"', 1)
    if len(chart) == 1:
        sys.exit('No hero chart in the prerendered output; did the markup change?')
    view_box = re.search(r'viewBox="([^"]+)"', chart[1])
    paths = re.findall(r'\sd="(M[^"]+)"', chart[1])
    if not view_box or len(paths) < 2:
        sys.exit('Found the hero chart but not its viewBox and two paths.')
    return {
        # React splits text around interpolations with comment markers, which have to come out.
        '__TITLE__': re.sub(r'<!--.*?-->', '', title.group(1)).strip(),
        '__VIEWBOX__': view_box.group(1),
        '__RAW__': paths[0],
        '__SMOOTH__': paths[1],
    }


def main() -> None:
    source = CARD.read_text()
    for token, value in from_prerender().items():
        source = source.replace(token, value)

    # The filled card is written beside the template so its relative link to
    # doc/_static/logo_horizontal.svg keeps resolving.
    with tempfile.NamedTemporaryFile('w', dir=HERE, suffix='.html', delete=False) as f:
        f.write(source)
        filled = Path(f.name)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=os.environ.get('CHROME_PATH'))
            page = browser.new_page(
                viewport={'width': 1200, 'height': 630}, device_scale_factor=2
            )
            page.goto(filled.as_uri(), wait_until='networkidle')
            page.wait_for_timeout(400)
            page.screenshot(path=str(OUT))
            browser.close()
    finally:
        filled.unlink()

    print(f'wrote {OUT.relative_to(HOMEPAGE.parent.parent)} ({OUT.stat().st_size // 1024} kB)')


if __name__ == '__main__':
    main()
