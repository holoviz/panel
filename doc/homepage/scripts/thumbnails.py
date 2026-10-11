"""Render the homepage's component, pane and gallery pictures into src/assets/.

Run once and commit the result; nothing in the Vite build calls this. It needs a development
environment with Panel and the plotting libraries installed, which the homepage pixi
environment deliberately does not have:

    python doc/homepage/scripts/thumbnails.py components
    python doc/homepage/scripts/thumbnails.py gallery --source examples/gallery
    python doc/homepage/scripts/thumbnails.py copilot --app ../lumen/examples/ai/penguin_copilot.py

Components and panes are rendered through pn.ui at one size, so every tile has the same
framing and the same theme as the snippets on the page. Gallery screenshots are taken from
the served notebooks rather than the square docs thumbnails, so they show the whole app. The
copilot screenshot drives Lumen's demo through one real LLM turn, so it needs OPENAI_API_KEY
and its wording varies between runs; check the widgets actually moved before committing it.
"""

from __future__ import annotations

import argparse
import io
import socket
import subprocess
import sys
import time

from pathlib import Path

import altair as alt
import hvplot.pandas  # noqa: F401
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import linear_cmap
from PIL import Image
from playwright.sync_api import sync_playwright

import panel as pn

# Figures are built on server threads, where the macOS GUI backend cannot run.
matplotlib.use('agg')

ASSETS = Path(__file__).resolve().parent.parent / 'src' / 'assets'

TILE = {'width': 480, 'height': 360}
APP = {'width': 1440, 'height': 900}

GALLERY = [
    'portfolio_analyzer',
    'gaia_million_star_atlas',
    'storm_surge_studio',
    'model_serving_monitor',
    'glaciers',
    'penguin_crossfilter',
]


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        return probe.getsockname()[1]


def wait_for(port: int, timeout: float = 60) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            socket.create_connection(('localhost', port), timeout=1).close()
            return
        except OSError:
            time.sleep(0.25)
    sys.exit(f'Nothing listening on port {port} after {timeout}s')


def save(png: bytes, path: Path, width: int | None = None, quality: int = 82) -> None:
    image = Image.open(io.BytesIO(png)).convert('RGB')
    if width and image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, 'WEBP', quality=quality, method=6)
    print(f'{path.relative_to(ASSETS)}  {path.stat().st_size / 1024:.0f} kB')  # noqa: T201


def component_builders():
    rng = np.random.default_rng(7)

    def tabulator():
        df = pd.DataFrame({
            'ticker': rng.choice(['AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOG'], 30),
            'price': rng.uniform(80, 900, 30).round(2),
            'change': rng.normal(0, 2.5, 30).round(2),
            'volume': rng.integers(1e5, 9e6, 30),
        })
        return pn.ui.Tabulator(
            df, show_index=False, sizing_mode='stretch_both', layout='fit_columns',
            formatters={'change': {'type': 'progress', 'min': -6, 'max': 6, 'color': ['#d32f2f', '#0072b5']}},
        )

    def chat():
        chat = pn.ui.ChatInterface(sizing_mode='stretch_both', show_rerun=False, show_undo=False)
        chat.send('Which region grew fastest?', user='Ana', respond=False)
        chat.send('APAC, up 14% on last quarter.', user='Assistant', respond=False)
        return chat

    def terminal():
        term = pn.ui.Terminal(sizing_mode='stretch_both', options={'fontSize': 13})
        term.write(
            '$ panel serve app.py --dev\r\n'
            'Starting Bokeh server version 3.10.0\r\n'
            'User authentication hooks NOT provided (default user enabled)\r\n'
            'Bokeh app running at: http://localhost:5006/app\r\n'
            'Starting Bokeh server with process id: 48213\r\n'
            '200 GET /app (::1) 41.27ms\r\n'
            '101 GET /app/ws (::1) 0.88ms\r\n'
            'WebSocket connection opened\r\n'
            'ServerConnection created\r\n$ '
        )
        return term

    def json_editor():
        return pn.ui.JSONEditor(
            value={'model': 'gradient-boosting', 'features': ['age', 'tenure', 'plan'],
                   'params': {'depth': 6, 'rate': 0.05, 'early_stop': True}, 'seed': 42},
            mode='tree', sizing_mode='stretch_both',
        )

    def trend():
        y = np.cumsum(rng.normal(0.4, 1, 60)) + 40
        return pn.ui.Trend(
            name='Weekly revenue', data={'x': np.arange(60), 'y': y}, plot_type='area',
            value=round(y[-1], 1), sizing_mode='stretch_both',
        )

    def gauge():
        return pn.ui.Gauge(name='Engine', value=2450, bounds=(0, 3000), format='{value} rpm',
                           sizing_mode='stretch_both')

    def swipe():
        x, y = np.meshgrid(np.linspace(-3, 3, 240), np.linspace(-2, 2, 160))
        field = np.sin(x * 1.4) * np.cos(y * 2) + 0.4 * np.exp(-(x**2 + y**2))

        def figure(cmap):
            fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=200)
            ax.imshow(field, cmap=cmap, aspect='auto')
            ax.set_axis_off()
            fig.subplots_adjust(0, 0, 1, 1)
            plt.close(fig)
            return pn.ui.Matplotlib(fig, sizing_mode='stretch_both', tight=True, format='png')

        return pn.ui.Swipe(figure('viridis'), figure('magma'), value=45, sizing_mode='stretch_both')

    def text_editor():
        return pn.ui.TextEditor(
            value=('<h2>Release notes</h2><p>This release adds <b>streaming</b> to every chat '
                   'component and a <i>new</i> table theme.</p><ul><li>Faster first render</li>'
                   '<li>Keyboard navigation in menus</li><li>Dark mode for every pane</li></ul>'),
            sizing_mode='stretch_both',
        )

    def perspective():
        df = pd.DataFrame({
            'region': rng.choice(['APAC', 'EMEA', 'Americas'], 200),
            'product': rng.choice(['Basic', 'Pro', 'Team'], 200),
            'revenue': rng.gamma(2, 400, 200).round(2),
            'units': rng.integers(1, 40, 200),
        })
        return pn.ui.Perspective(df, group_by=['region'], split_by=['product'], columns=['revenue'],
                                 aggregates={'revenue': 'sum'}, plugin='d3_y_bar', settings=False, theme='pro',
                                 sizing_mode='stretch_both')

    def cross_selector():
        fruits = ['Apple', 'Banana', 'Cherry', 'Grape', 'Mango', 'Pear']
        # List height comes only from `size`, so it has to cover every option or the tile shows a
        # truncated list; four rows is the most that fits the tile.
        return pn.ui.CrossSelector(options=fruits, value=['Banana', 'Mango'], size=4, sizing_mode='stretch_width')

    def code_editor():
        return pn.ui.CodeEditor(
            value=(
                'import pandas as pd\n'
                'import panel as pn\n\n'
                'df = pd.read_parquet("sales.parquet")\n\n'
                'def forecast(df, alpha=0.5):\n'
                '    """Exponentially smoothed revenue."""\n'
                '    trend = df.revenue.ewm(alpha=alpha)\n'
                '    return trend.mean().iloc[-1]\n\n'
                'alpha = pn.ui.FloatSlider(\n'
                '    name="alpha", value=0.5, start=0, end=1\n'
                ')\n'
                'pn.bind(forecast, df, alpha=alpha)\n'
            ),
            language='python', theme='github_light_default', sizing_mode='stretch_both',
            # Ace's 12 px default leaves a tile this size mostly empty.
            stylesheets=['.ace_editor { font-size: 14px !important; }'],
        )

    def player():
        return pn.ui.Player(name='Frame', start=0, end=120, value=48, sizing_mode='stretch_width')

    return {
        'Tabulator': tabulator, 'ChatInterface': chat, 'Terminal': terminal,
        'JSONEditor': json_editor, 'Trend': trend, 'Gauge': gauge, 'Swipe': swipe,
        'TextEditor': text_editor, 'Perspective': perspective, 'CrossSelector': cross_selector,
        'CodeEditor': code_editor, 'Player': player,
    }


def pane_builders():
    rng = np.random.default_rng(11)

    def matplotlib_():
        fig, ax = plt.subplots(figsize=(4.8, 3.6))
        for i, (mu, c) in enumerate([(-1.2, '#0072b5'), (0.3, '#e1812c'), (1.5, '#3a923a')]):
            sample = rng.normal(mu, 0.6 + 0.15 * i, 600)
            ax.hist(sample, bins=40, alpha=0.55, color=c, label=f'group {"abc"[i]}')
        ax.legend(frameon=False)
        ax.spines[['top', 'right']].set_visible(False)
        fig.tight_layout()
        plt.close(fig)
        return pn.ui.Matplotlib(fig, format='svg', sizing_mode='stretch_both', tight=True)

    def plotly_():
        x, y = np.meshgrid(np.linspace(-3, 3, 60), np.linspace(-3, 3, 60))
        z = np.sin(x) * np.cos(y) * np.exp(-0.1 * (x**2 + y**2))
        fig = go.Figure(go.Surface(z=z, x=x, y=y, colorscale='Viridis', showscale=False))
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                          scene_camera=dict(eye=dict(x=1.7, y=1.6, z=1.1)))
        return pn.ui.Plotly(fig, sizing_mode='stretch_both')

    def bokeh_():
        x, y = rng.standard_normal(1500), rng.standard_normal(1500)
        source = ColumnDataSource({'x': x, 'y': y, 'r': np.hypot(x, y)})
        p = figure(sizing_mode='stretch_both', toolbar_location='above', tools='pan,wheel_zoom,box_select,reset')
        p.scatter('x', 'y', source=source, size=6, alpha=0.7, line_color=None,
                  fill_color=linear_cmap('r', 'Viridis256', 0, 3))
        return pn.ui.Bokeh(p, sizing_mode='stretch_both')

    def holoviews_():
        days = pd.date_range('2026-01-01', periods=120)
        df = pd.concat([
            pd.DataFrame({'date': days, 'ticker': t, 'price': 100 + np.cumsum(rng.normal(0.1, 1.5, 120))})
            for t in ['AAPL', 'MSFT', 'NVDA']
        ])
        plot = df.hvplot.line(x='date', y='price', groupby='ticker', responsive=True, height=280,
                              line_width=2, widget_location='top_left')
        return pn.ui.Column(plot, sizing_mode='stretch_both')

    def vega_():
        df = pd.DataFrame({'x': rng.normal(0, 1, 300), 'y': rng.normal(0, 1, 300),
                           'group': rng.choice(['a', 'b', 'c'], 300)})
        brush = alt.selection_interval(name='brush')
        chart = alt.Chart(df).mark_circle(size=45).encode(
            x='x', y='y', color=alt.condition(brush, 'group:N', alt.value('lightgray')),
        ).add_params(brush).properties(width='container', height='container')
        return pn.ui.Vega(chart, sizing_mode='stretch_both')

    def echarts_():
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
        return pn.ui.ECharts({
            'tooltip': {}, 'legend': {'top': 0},
            'grid': {'left': 40, 'right': 16, 'bottom': 28, 'top': 36},
            'xAxis': {'data': months},
            'yAxis': {},
            'series': [
                {'name': 'Orders', 'type': 'bar', 'data': [120, 200, 150, 80, 170, 210, 190, 240],
                 'itemStyle': {'borderRadius': [4, 4, 0, 0]}},
                {'name': 'Returns', 'type': 'line', 'smooth': True, 'data': [20, 32, 28, 18, 30, 26, 35, 31]},
            ],
        }, sizing_mode='stretch_both')

    def deckgl_():
        points = pd.DataFrame({
            'lng': -73.98 + rng.normal(0, 0.03, 4000),
            'lat': 40.75 + rng.normal(0, 0.03, 4000),
        })
        spec = {
            'initialViewState': {'longitude': -73.98, 'latitude': 40.75, 'zoom': 11.2,
                                 'pitch': 50, 'bearing': -20},
            'mapStyle': 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
            'layers': [{
                '@@type': 'HexagonLayer', 'data': points.to_dict('records'),
                'getPosition': '@@=[lng, lat]', 'radius': 220, 'elevationScale': 6,
                'extruded': True, 'coverage': 0.9,
            }],
        }
        return pn.ui.DeckGL(spec, sizing_mode='stretch_both')

    def vizzu_():
        df = pd.DataFrame({
            'quarter': ['Q1', 'Q2', 'Q3', 'Q4'] * 3,
            'region': ['APAC'] * 4 + ['EMEA'] * 4 + ['Americas'] * 4,
            'revenue': rng.integers(20, 60, 12),
        })
        return pn.ui.Vizzu(df, config={'x': 'quarter', 'y': ['revenue', 'region'], 'color': 'region'},
                           sizing_mode='stretch_both')

    return {
        'Matplotlib': matplotlib_, 'Plotly': plotly_, 'Bokeh': bokeh_, 'HoloViews': holoviews_,
        'Vega': vega_, 'ECharts': echarts_, 'DeckGL': deckgl_, 'Vizzu': vizzu_,
    }


def render_tiles(only: list[str] | None = None) -> None:
    pn.extension('tabulator', 'terminal', 'jsoneditor', 'texteditor', 'codeeditor', 'perspective',
                 'plotly', 'vega', 'echarts', 'deckgl', 'vizzu')

    targets = {f'components/{k}': v for k, v in component_builders().items()}
    targets |= {f'panes/{k}': v for k, v in pane_builders().items()}
    if only:
        targets = {k: v for k, v in targets.items() if k.split('/')[1] in only}

    style = {'padding': '14px', 'box-sizing': 'border-box'}

    def page(build):
        def view():
            obj = build()
            # Spacers centre fixed-height widgets instead of leaving them on top of an empty tile.
            items = [pn.layout.VSpacer(), obj, pn.layout.VSpacer()] if obj.sizing_mode == 'stretch_width' else [obj]
            return pn.ui.Column(*items, sizing_mode='stretch_both', margin=0, styles=style)
        return view

    port = free_port()
    server = pn.serve({k: page(v) for k, v in targets.items()}, port=port, show=False,
                      threaded=True, verbose=False)
    wait_for(port)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for path in targets:
                tab = browser.new_page(viewport=TILE, device_scale_factor=2, color_scheme='light')
                errors: list[str] = []
                tab.on('pageerror', lambda e, errors=errors: errors.append(str(e)))
                tab.goto(f'http://localhost:{port}/{path}', wait_until='networkidle')
                tab.wait_for_timeout(2500)
                if errors:
                    print(f'{path}: {errors}', file=sys.stderr)  # noqa: T201
                save(tab.screenshot(), ASSETS / f'{path}.webp')
                tab.close()
            browser.close()
    finally:
        server.stop()


def render_gallery(source: Path) -> None:
    port = free_port()
    notebooks = [str(source / f'{name}.ipynb') for name in GALLERY]
    server = subprocess.Popen(
        ['panel', 'serve', *notebooks, '--port', str(port), '--allow-websocket-origin', f'localhost:{port}'],
        cwd=source, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )
    try:
        wait_for(port, timeout=120)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for name in GALLERY:
                tab = browser.new_page(viewport=APP, device_scale_factor=1, color_scheme='light')
                tab.goto(f'http://localhost:{port}/{name}', wait_until='networkidle', timeout=180_000)
                # Data loads and the first periodic callbacks land after networkidle.
                tab.wait_for_timeout(6000)
                save(tab.screenshot(), ASSETS / 'gallery' / f'{name}.webp', quality=78)
                tab.close()
            browser.close()
    finally:
        server.terminate()
        server.wait()


COPILOT_PROMPT = 'Only show Gentoo and Chinstrap penguins, colour by sex and plot flipper length against body mass'


def render_copilot(app: Path) -> None:
    """Screenshot Lumen's penguin copilot after a real LLM turn, so the picture shows moved widgets."""
    port = free_port()
    server = subprocess.Popen(
        ['panel', 'serve', str(app), '--port', str(port), '--allow-websocket-origin', f'localhost:{port}'],
        cwd=app.parent, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
    )
    try:
        wait_for(port, timeout=120)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            tab = browser.new_page(viewport=APP, device_scale_factor=1, color_scheme='light')
            tab.goto(f'http://localhost:{port}/{app.stem}', wait_until='networkidle', timeout=180_000)
            tab.wait_for_timeout(3000)
            # The drawer's dock handle, centred on the right edge.
            tab.mouse.click(APP['width'] - 13, APP['height'] // 2)
            prompt = tab.get_by_placeholder('Ask anything...')
            prompt.click()
            prompt.press_sequentially(COPILOT_PROMPT, delay=5)
            prompt.press('Enter')
            # The axis label only reads flipper_length_mm once the agent has written the widget.
            tab.get_by_text('flipper_length_mm', exact=True).first.wait_for(timeout=180_000)
            # Let the closing summary finish streaming.
            tab.wait_for_timeout(15000)
            save(tab.screenshot(), ASSETS / 'ai' / 'penguin_copilot.webp', quality=78)
            browser.close()
    finally:
        server.terminate()
        server.wait()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='what', required=True)
    components = sub.add_parser('components', help='component and pane tiles')
    components.add_argument('--only', nargs='+', metavar='NAME', help='render just these tiles, e.g. Tabulator Plotly')
    gallery = sub.add_parser('gallery', help='gallery app screenshots')
    gallery.add_argument('--source', type=Path, required=True, help='examples/gallery directory to serve')
    copilot = sub.add_parser('copilot', help='Lumen copilot screenshot (needs an OpenAI key)')
    copilot.add_argument('--app', type=Path, required=True, help="lumen's examples/ai/penguin_copilot.py")
    args = parser.parse_args()
    if args.what == 'components':
        render_tiles(args.only)
    elif args.what == 'gallery':
        render_gallery(args.source.resolve())
    else:
        render_copilot(args.app.resolve())


if __name__ == '__main__':
    main()
