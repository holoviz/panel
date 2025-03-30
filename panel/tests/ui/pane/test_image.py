import pytest

from numpy.testing import assert_allclose

pytestmark = pytest.mark.ui

from panel.layout import Row
from panel.pane import PDF, PNG, SVG
from panel.tests.util import serve_component, wait_for_server, wait_until

PDF_FILE = 'https://assets.holoviz.org/panel/samples/pdf_sample.pdf'
PNG_FILE = 'https://assets.holoviz.org/panel/samples/png_sample.png'
SVG_FILE = 'https://assets.holoviz.org/panel/samples/svg_sample.svg'

def get_bbox(page, obj):
    _, port = serve_component(page, obj)
    if isinstance(obj, Row):
        obj = obj[0]

    wait_for_server(port)

    if obj.embed:
        page.goto(f"http://localhost:{port}")
    else:
        with page.expect_response(obj.object):
            page.goto(f"http://localhost:{port}")
    wait_until(lambda: page.locator("img") is not None, page)
    for _ in range(5):
        bbox = page.locator("img").bounding_box()
        if bbox["width"] and bbox["height"]:
            return bbox
        page.wait_for_timeout(100)

    raise TimeoutError("Image has not been loaded")

@pytest.mark.parametrize('embed', [False, True])
def test_png_native_size(embed, page):
    png = PNG(PNG_FILE, embed=embed)
    bbox = get_bbox(page, png)
    assert bbox['width'] == 800
    assert bbox['height'] == 600

@pytest.mark.parametrize('embed', [False, True])
def test_png_native_size_with_width(embed, page):
    png = PNG(PNG_FILE, embed=embed, width=200)
    bbox = get_bbox(page, png)
    assert bbox['width'] == 200
    assert bbox['height'] == 150

@pytest.mark.parametrize('embed', [False, True])
def test_png_native_size_with_height(embed, page):
    png = PNG(PNG_FILE, embed=embed, height=200)
    bbox = get_bbox(page, png)
    assert int(bbox['width']) == 266
    assert bbox['height'] == 200

@pytest.mark.parametrize('embed', [False, True])
def test_png_scaled_fixed_size(embed, page):
    png = PNG(PNG_FILE, width=400, embed=embed)
    bbox = get_bbox(page, png)
    assert bbox['width'] == 400
    assert bbox['height'] == 300

@pytest.mark.parametrize('sizing_mode', ['scale_width', 'stretch_width'])
@pytest.mark.parametrize('embed', [False, True])
def test_png_scale_width(sizing_mode, embed, page):
    png = PNG(PNG_FILE, sizing_mode=sizing_mode, fixed_aspect=True, embed=embed)
    row = Row(png, width=800)
    bbox = get_bbox(page, row)
    assert bbox['width'] == 780
    assert bbox['height'] == 585

@pytest.mark.parametrize('sizing_mode', ['scale_height', 'stretch_height'])
@pytest.mark.parametrize('embed', [False, True])
def test_png_scale_height(sizing_mode, embed, page):
    png = PNG(PNG_FILE, sizing_mode=sizing_mode, fixed_aspect=True, embed=embed)
    row = Row(png, height=500)
    bbox = get_bbox(page, row)
    assert int(bbox['width']) == 653
    assert bbox['height'] == 490

@pytest.mark.parametrize('sizing_mode', ['stretch_both', 'scale_both'])
@pytest.mark.parametrize('embed', [False, True])
def test_png_scale_both(sizing_mode, embed, page):
    png = PNG(PNG_FILE, sizing_mode=sizing_mode, fixed_aspect=True, embed=embed)
    row = Row(png, width=800, height=500)
    bbox = get_bbox(page, row)
    assert bbox['width'] == 780
    assert bbox['height'] == 490

@pytest.mark.parametrize('embed', [False, True])
def test_png_stretch_width(embed, page):
    png = PNG(PNG_FILE, sizing_mode='stretch_width', fixed_aspect=False, embed=embed, height=500)
    row = Row(png, width=1000)
    bbox = get_bbox(page, row)
    assert bbox['width'] == 980
    assert bbox['height'] == 500

@pytest.mark.parametrize('embed', [False, True])
def test_png_stretch_height(embed, page):
    png = PNG(PNG_FILE, sizing_mode='stretch_height', fixed_aspect=False, width=500, embed=embed)
    row = Row(png, height=500)
    bbox = get_bbox(page, row)
    assert bbox['width'] == 500
    assert bbox['height'] == 490

@pytest.mark.parametrize('embed', [False, True])
def test_png_stretch_both(embed, page):
    png = PNG(PNG_FILE, sizing_mode='stretch_both', fixed_aspect=False, embed=embed)
    row = Row(png, width=800, height=500)
    bbox = get_bbox(page, row)
    assert bbox['width'] == 780
    assert bbox['height'] == 490

@pytest.mark.parametrize('embed', [False, True])
def test_svg_native_size(embed, page):
    svg = SVG(SVG_FILE, embed=embed)
    bbox = get_bbox(page, svg)
    assert_allclose(bbox['width'], 507.21, atol=0.01)
    assert int(bbox['height']) == 427

@pytest.mark.parametrize('embed', [False, True])
def test_svg_scaled_fixed_size(embed, page):
    svg = SVG(SVG_FILE, width=250, embed=embed)
    bbox = get_bbox(page, svg)
    assert bbox['width'] == 250
    assert int(bbox['height']) == 210

@pytest.mark.parametrize('sizing_mode', ['scale_width', 'stretch_width'])
@pytest.mark.parametrize('embed', [False, True])
def test_svg_scale_width(sizing_mode, embed, page):
    svg = SVG(SVG_FILE, sizing_mode=sizing_mode, fixed_aspect=True, embed=embed)
    row = Row(svg, width=800)
    bbox = get_bbox(page, row)
    assert bbox['width'] == 780
    assert bbox['height'] == 657.921875

@pytest.mark.parametrize('sizing_mode', ['scale_height', 'stretch_height'])
@pytest.mark.parametrize('embed', [False, True])
def test_svg_scale_height(sizing_mode, embed, page):
    svg = SVG(SVG_FILE, sizing_mode=sizing_mode, fixed_aspect=True, embed=embed)
    row = Row(svg, height=500)
    bbox = get_bbox(page, row)
    assert int(bbox['width']) == 580
    assert bbox['height'] == 490

@pytest.mark.parametrize('sizing_mode', ['stretch_both', 'scale_both'])
@pytest.mark.parametrize('embed', [False, True])
def test_svg_scale_both(sizing_mode, embed, page):
    svg = SVG(SVG_FILE, sizing_mode=sizing_mode, fixed_aspect=True, embed=embed)
    row = Row(svg, width=800, height=500)
    bbox = get_bbox(page, row)
    assert bbox['width'] == 780
    assert bbox['height'] == 490

@pytest.mark.parametrize('embed', [False, True])
def test_svg_stretch_width(embed, page):
    svg = SVG(SVG_FILE, sizing_mode='stretch_width', fixed_aspect=False, embed=embed, height=500)
    row = Row(svg, width=1000)
    bbox = get_bbox(page, row)
    assert bbox['width'] == 980
    assert bbox['height'] == 500

@pytest.mark.parametrize('embed', [False, True])
def test_svg_stretch_height(embed, page):
    svg = SVG(SVG_FILE, sizing_mode='stretch_height', fixed_aspect=False, width=500, embed=embed)
    row = Row(svg, height=500)
    bbox = get_bbox(page, row)
    assert bbox['width'] == 500
    assert bbox['height'] == 490

@pytest.mark.parametrize('embed', [False, True])
def test_svg_stretch_both(embed, page):
    svg = SVG(SVG_FILE, sizing_mode='stretch_both', fixed_aspect=False, embed=embed)
    row = Row(svg, width=800, height=500)
    bbox = get_bbox(page, row)
    assert bbox['width'] == 780
    assert bbox['height'] == 490

def test_pdf_embed(page):
    pdf_pane = PDF(PDF_FILE, embed=True)

    _, port = serve_component(page, pdf_pane)

    src = page.locator("embed").get_attribute('src')

    assert src.startswith(f"blob:http://localhost:{port}")
    assert src.endswith("#page=1")

def test_pdf_embed_start_page(page):
    # The pdf does not have 2 pages just to verify #page is set
    pdf_pane = PDF(PDF_FILE, start_page=22, embed=True)

    _, port = serve_component(page, pdf_pane)

    src = page.locator("embed").get_attribute('src')

    assert src.startswith(f"blob:http://localhost:{port}")
    assert src.endswith("#page=22")

def test_pdf_no_embed_start_page(page):
    # The pdf does not have 2 pages just to verify #page is set
    pdf_pane = PDF(PDF_FILE, start_page=22, embed=False)

    serve_component(page, pdf_pane)

    src = page.locator("embed").get_attribute('src')
    assert src == PDF_FILE + "#page=22"
