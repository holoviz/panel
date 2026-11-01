import os

from base64 import b64decode, b64encode
from html import escape
from io import BytesIO, StringIO
from pathlib import Path

import pytest

from panel.pane import (
    AVIF, GIF, ICO, JPG, PDF, PNG, SVG, Image, WebP,
)

AVIF_FILE = 'https://assets.holoviz.org/panel/samples/avif_sample.avif'
JPG_FILE = 'https://assets.holoviz.org/panel/samples/jpg_sample.jpg'
JPEG_FILE = 'https://assets.holoviz.org/panel/samples/jpeg_sample.jpeg'
PNG_FILE = 'https://assets.holoviz.org/panel/samples/png_sample.png'
SVG_FILE = 'https://assets.holoviz.org/panel/samples/svg_sample.svg'
WEBP_FILE = 'https://assets.holoviz.org/panel/samples/webp_sample.webp'

embed_parametrize = pytest.mark.parametrize(
    'embed', [False, pytest.param(True, marks=pytest.mark.internet)]
)

def test_jpeg_applies():
    assert JPG.applies(JPEG_FILE)
    assert JPG.applies(JPG_FILE)

def test_svg_pane(document, comm):
    rect = """
    <svg xmlns="http://www.w3.org/2000/svg">
      <rect x="10" y="10" height="100" width="100"/>
    </svg>
    """
    pane = SVG(rect, encode=True)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('&lt;img src=&quot;data:image/svg+xml;base64')
    assert b64encode(rect.encode('utf-8')).decode('utf-8') in model.text

    # Replace Pane.object
    circle = """
    <svg xmlns="http://www.w3.org/2000/svg" height="100">
      <circle cx="50" cy="50" r="40" />
    </svg>
    """
    pane.object = circle
    assert pane._models[model.ref['id']][0] is model
    assert model.text.startswith('&lt;img src=&quot;data:image/svg+xml;base64')
    assert b64encode(circle.encode('utf-8')).decode('utf-8') in model.text

    pane.encode = False
    assert model.text == escape(circle)

    # Cleanup
    pane._cleanup(model)
    assert pane._models == {}


twopixel = dict(\
    avif= b'AAAAHGZ0eXBhdmlmAAAAAGF2aWZtaWYxbWlhZgAAAOptZXRhAAAAAAAAACFoZGx' + \
          b'yAAAAAAAAAABwaWN0AAAAAAAAAAAAAAAAAAAAAA5waXRtAAAAAAABAAAAImlsb2' + \
          b'MAAAAAREAAAQABAAAAAAEOAAEAAAAAAAAAIgAAACNpaW5mAAAAAAABAAAAFWluZ' + \
          b'mUCAAAAAAEAAGF2MDEAAAAAamlwcnAAAABLaXBjbwAAAAxhdjFDgSACAAAAABNj' + \
          b'b2xybmNseAABAA0AAIAAAAAUaXNwZQAAAAAAAAACAAAAAQAAABBwaXhpAAAAAAM' + \
          b'ICAgAAAAXaXBtYQAAAAAAAAABAAEEgQIDBAAAACptZGF0EgAKBzgAJpAQ0AIyFR' + \
          b'gACiiihQABAABsnSRm9hs9BNOQ9A==',
    gif = b'R0lGODlhAgABAPAAAEQ6Q2NYYCH5BAAAAAAAIf8LSW1hZ2VNYWdpY2sNZ2FtbWE' + \
          b'9MC40NTQ1NQAsAAAAAAIAAQAAAgIMCgA7',
    png = b'iVBORw0KGgoAAAANSUhEUgAAAAIAAAABCAYAAAD0In+KAAAAFElEQVQIHQEJAPb' + \
          b'/AWNYYP/h4uMAFL0EwlEn99gAAAAASUVORK5CYII=',
    jpg = b'/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQE' + \
          b'BAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQ' + \
          b'EBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBA' + \
          b'QEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAIDAREAAhEBAxEB/8QAFAABAAAAAAAA' + \
          b'AAAAAAAAAAAACf/EABoQAAEFAQAAAAAAAAAAAAAAAAYABAU2dbX/xAAVAQEBAAA' + \
          b'AAAAAAAAAAAAAAAAFBv/EABkRAAEFAAAAAAAAAAAAAAAAAAEAAjFxsf/aAAwDAQ' + \
          b'ACEQMRAD8AA0qs5HvTHQcJdsChioXSbOr/2Q==',
    ico = b'AAABAAEAAgEAAAEAIAA0AAAAFgAAACgAAAACAAAAAgAAAAEAIAAAAAAACAAAAHQ' + \
          b'SAAB0EgAAAAAAAAAAAAD//////////wAAAAA=',
    webp= b'UklGRkIAAABXRUJQVlA4WAoAAAAQAAAAAQAAAAAAQUxQSAMAAAAAAAAAVlA4IBg' + \
          b'AAAAwAQCdASoCAAEAAUAmJaQAA3AA/v02aAA=',
    webp_lossy = b'UklGRjoAAABXRUJQVlA4IC4AAACwAQCdASoCAAEAAUAmJaACdLoABDAAAP7x3I/4' + \
                 b'DdfFtMv/vYL/3YL/3YL/WwAA',
    webp_lossless = b'UklGRh4AAABXRUJQVlA4TBEAAAAvAQAAAAdQjyLXo/+BiOh/AAA=',
          )


@pytest.mark.parametrize('t', [AVIF, PNG, JPG, GIF, ICO, WebP], ids=lambda t: t.name.lower())
def test_imgshape(t):
    w, h = t._imgshape(b64decode(twopixel[t.name.lower()]))
    assert w == 2
    assert h == 1

def test_load_from_byteio():
    """Testing a loading a image from a ByteIo"""
    memory = BytesIO()

    path = os.path.dirname(__file__)
    with open(os.path.join(path, '../test_data/logo.png'), 'rb') as image_file:
        memory.write(image_file.read())

    image_pane = PNG(memory)
    image_data = image_pane._data(memory)
    assert b'PNG' in image_data

def test_load_from_stringio():
    """Testing a loading a image from a StringIO"""
    memory = StringIO()

    path = os.path.dirname(__file__)
    with open(os.path.join(path, '../test_data/logo.png'), 'rb') as image_file:
        memory.write(str(image_file.read()))

    image_pane = PNG(memory)
    image_data = image_pane._data(memory)
    assert 'PNG' in image_data

@pytest.mark.internet
def test_loading_a_image_from_url():
    """Tests the loading of a image from a url"""
    url = 'https://raw.githubusercontent.com/holoviz/panel/main/doc/_static/logo.png'

    image_pane = PNG(url)
    image_data = image_pane._data(url)
    assert b'PNG' in image_data

def test_image_from_bytes():
    path = os.path.dirname(__file__)
    with open(os.path.join(path, '../test_data/logo.png'), 'rb') as f:
        img = f.read()

    image_pane = PNG(img)
    image_data = image_pane._data(img)
    assert b'PNG' in image_data

def test_loading_a_image_from_pathlib():
    """Tests the loading of a image from a pathlib"""
    filepath = Path(__file__).parent.parent / "test_data" / "logo.png"

    image_pane = PNG(filepath)
    image_data = image_pane._data(filepath)
    assert b'PNG' in image_data

def test_image_alt_text(document, comm):
    """Tests the loading of a image from a url"""
    url = 'https://raw.githubusercontent.com/holoviz/panel/main/doc/_static/logo.png'

    image_pane = PNG(url, embed=False, alt_text="Some alt text")
    model = image_pane.get_root(document, comm)

    assert 'alt=&#x27;Some alt text&#x27;' in model.text

def test_image_link_url(document, comm):
    """Tests the loading of a image from a url"""
    url = 'https://raw.githubusercontent.com/holoviz/panel/main/doc/_static/logo.png'

    image_pane = PNG(url, embed=False, link_url="http://anaconda.org")
    model = image_pane.get_root(document, comm)

    assert model.text.startswith('&lt;a href=&quot;http://anaconda.org&quot;')

def test_pdf_no_embed(document, comm):
    url = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
    pdf_pane = PDF(url, embed=False)
    model = pdf_pane.get_root(document, comm)

    assert model.text.startswith(f"&lt;embed src=&quot;{url}")

def test_pdf_local_file(document, comm):
    path = Path(__file__).parent.parent / "test_data" / "sample.pdf"
    pdf_pane = PDF(object=path)
    model = pdf_pane.get_root(document, comm)
    assert model.embed
    assert model.text.startswith("JVBER")

def test_pdf_bytes_no_embed(document, comm):
    path = Path(__file__).parent.parent / "test_data" / "sample.pdf"
    pdf_pane = PDF(path.read_bytes(), embed=False)
    model = pdf_pane.get_root(document, comm)
    assert model.embed
    assert model.text.startswith("JVBER")

def test_pdf_url_embed_false_stays_html(document, comm):
    url = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
    model = PDF(url, embed=False).get_root(document, comm)
    assert not model.embed

def test_pdf_switch_between_url_and_local_data(document, comm):
    path = Path(__file__).parent.parent / "test_data" / "sample.pdf"
    url = 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
    pdf_pane = PDF(url, embed=False)
    model = pdf_pane.get_root(document, comm)

    pdf_pane.object = path.read_bytes()
    assert model.embed
    assert not pdf_pane.embed

    pdf_pane.object = url
    assert not model.embed
    assert model.text.startswith("&lt;embed")

def test_png_native_size(document, comm):
    png = PNG(PNG_FILE, embed=False)
    model = png.get_root(document, comm)
    assert 'width: auto' in model.text
    assert 'height: auto' in model.text

@pytest.mark.internet
def test_png_native_size_embed(document, comm):
    png = PNG(PNG_FILE, embed=True)
    model = png.get_root(document, comm)
    assert 'width: 800px' in model.text
    assert 'height: 600px' in model.text

@pytest.mark.internet
def test_png_native_size_embed_with_width(document, comm):
    png = PNG(PNG_FILE, embed=True, width=200)
    model = png.get_root(document, comm)
    assert 'width: 200px' in model.text
    assert 'height: 150px' in model.text

def test_png_native_size_with_width(document, comm):
    png = PNG(PNG_FILE, embed=False, width=200)
    model = png.get_root(document, comm)
    assert 'width: 200px' in model.text
    assert 'height: auto' in model.text

@pytest.mark.internet
def test_png_native_size_embed_with_height(document, comm):
    png = PNG(PNG_FILE, embed=True, height=200)
    model = png.get_root(document, comm)
    assert 'width: 266px' in model.text
    assert 'height: 200px' in model.text

def test_png_native_size_with_height(document, comm):
    png = PNG(PNG_FILE, embed=False, height=200)
    model = png.get_root(document, comm)
    assert 'width: auto' in model.text
    assert 'height: 200px' in model.text

@pytest.mark.internet
def test_png_embed_scaled_fixed_size(document, comm):
    png = PNG(PNG_FILE, width=400, embed=True)
    model = png.get_root(document, comm)
    assert 'width: 400px' in model.text
    assert 'height: 300px' in model.text

def test_png_scaled_fixed_size(document, comm):
    png = PNG(PNG_FILE, width=400, embed=False)
    model = png.get_root(document, comm)
    assert 'width: 400px' in model.text
    assert 'height: auto' in model.text

@pytest.mark.parametrize('sizing_mode', ['scale_width', 'stretch_width', 'stretch_both', 'scale_both'])
@embed_parametrize
def test_png_scale_width(sizing_mode, embed, document, comm):
    png = PNG(PNG_FILE, sizing_mode=sizing_mode, fixed_aspect=True, embed=embed)
    model = png.get_root(document, comm)
    assert 'width: 100%' in model.text
    assert 'height: auto' in model.text

@pytest.mark.parametrize('sizing_mode', ['scale_height', 'stretch_height'])
@embed_parametrize
def test_png_scale_height(sizing_mode, embed, document, comm):
    png = PNG(PNG_FILE, sizing_mode=sizing_mode, fixed_aspect=True, embed=embed)
    model = png.get_root(document, comm)
    assert 'width: auto' in model.text
    assert 'height: 100%' in model.text

@embed_parametrize
def test_png_stretch_width(embed, document, comm):
    png = PNG(PNG_FILE, sizing_mode='stretch_width', fixed_aspect=False, embed=embed, height=500)
    model = png.get_root(document, comm)
    assert 'width: 100%' in model.text
    assert 'height: 500px' in model.text

@embed_parametrize
def test_png_stretch_height(embed, document, comm):
    png = PNG(PNG_FILE, sizing_mode='stretch_height', fixed_aspect=False, width=500, embed=embed)
    model = png.get_root(document, comm)
    assert 'width: 500px' in model.text
    assert 'height: 100%' in model.text

@embed_parametrize
def test_png_stretch_both(embed, document, comm):
    png = PNG(PNG_FILE, sizing_mode='stretch_both', fixed_aspect=False, embed=embed)
    model = png.get_root(document, comm)
    assert 'width: 100%' in model.text
    assert 'height: 100%' in model.text

@embed_parametrize
def test_svg_native_size(embed, document, comm):
    svg = SVG(SVG_FILE, embed=embed)
    model = svg.get_root(document, comm)
    assert 'width: auto' in model.text
    assert 'height: auto' in model.text

@embed_parametrize
def test_svg_native_size_with_width(embed, document, comm):
    svg = SVG(SVG_FILE, embed=embed, width=200)
    model = svg.get_root(document, comm)
    assert 'width: 200px' in model.text
    assert 'height: auto' in model.text

@embed_parametrize
def test_svg_native_size_with_height(embed, document, comm):
    svg = SVG(SVG_FILE, embed=embed, height=200)
    model = svg.get_root(document, comm)
    assert 'width: auto' in model.text
    assert 'height: 200px' in model.text

@embed_parametrize
def test_svg_scaled_fixed_size(embed, document, comm):
    svg = SVG(SVG_FILE, width=400, embed=embed)
    model = svg.get_root(document, comm)
    assert 'width: 400px' in model.text
    assert 'height: auto' in model.text

@pytest.mark.parametrize('sizing_mode', ['scale_width', 'stretch_width', 'stretch_both', 'scale_both'])
@embed_parametrize
def test_svg_scale_width(sizing_mode, embed, document, comm):
    svg = SVG(SVG_FILE, sizing_mode=sizing_mode, fixed_aspect=True, embed=embed)
    model = svg.get_root(document, comm)
    assert 'width: 100%' in model.text
    assert 'height: auto' in model.text

@pytest.mark.parametrize('sizing_mode', ['scale_height', 'stretch_height'])
@embed_parametrize
def test_svg_scale_height(sizing_mode, embed, document, comm):
    svg = SVG(SVG_FILE, sizing_mode=sizing_mode, fixed_aspect=True, embed=embed)
    model = svg.get_root(document, comm)
    assert 'width: auto' in model.text
    assert 'height: 100%' in model.text

@embed_parametrize
def test_svg_stretch_width(embed, document, comm):
    svg = SVG(SVG_FILE, sizing_mode='stretch_width', fixed_aspect=False, embed=embed, height=500)
    model = svg.get_root(document, comm)
    assert 'width: 100%' in model.text
    assert 'height: 500px' in model.text

@embed_parametrize
def test_svg_stretch_height(embed, document, comm):
    svg = SVG(SVG_FILE, sizing_mode='stretch_height', fixed_aspect=False, width=500, embed=embed)
    model = svg.get_root(document, comm)
    assert 'width: 500px' in model.text
    assert 'height: 100%' in model.text

@embed_parametrize
def test_svg_stretch_both(embed, document, comm):
    svg = SVG(SVG_FILE, sizing_mode='stretch_both', fixed_aspect=False, embed=embed)
    model = svg.get_root(document, comm)
    assert 'width: 100%' in model.text
    assert 'height: 100%' in model.text

def test_image_caption(document, comm):
    png = PNG(PNG_FILE, caption='Some Caption')
    model = png.get_root(document, comm)
    assert 'Some Caption' in model.text
    assert 'figcaption' in model.text


@pytest.mark.parametrize('cls,data', [
    (PNG, b'\x89PNG\r\n\x1a\n'),        # Valid PNG header but truncated before IHDR dimensions
    (GIF, b'GIF89a'),                     # Valid GIF header but truncated before dimensions
    (ICO, b'\x00\x00\x01\x00\x01'),      # Valid ICO header but truncated before entry
], ids=['png', 'gif', 'ico'])
def test_imgshape_truncated_data(cls, data):
    with pytest.raises(ValueError, match="insufficient data"):
        cls._imgshape(data)


def test_imgshape_jpg_no_sof_marker():
    # JPEG with valid SOI marker but no SOF marker (just SOI + SOS)
    data = b'\xff\xd8\xff\xda' + b'\x00' * 10
    with pytest.raises(ValueError, match="no SOF marker found"):
        JPG._imgshape(data)


def test_imgshape_avif_no_ispe_box():
    # AVIF data without an ispe box
    data = b'\x00\x00\x00\x1cftypavifall' + b'\x00' * 50
    with pytest.raises(ValueError, match="no 'ispe' box found"):
        AVIF._imgshape(data)


@pytest.mark.parametrize('variant', ['webp_lossy', 'webp_lossless'])
def test_imgshape_webp_variants(variant):
    w, h = WebP._imgshape(b64decode(twopixel[variant]))
    assert w == 2
    assert h == 1


_bytes_formats = {
    AVIF: 'avif', PNG: 'png', JPG: 'jpg', GIF: 'gif', ICO: 'ico', WebP: 'webp'
}

@pytest.mark.parametrize('cls,fmt', list(_bytes_formats.items()), ids=lambda v: getattr(v, 'name', v))
def test_imgshape_rejects_other_formats(cls, fmt):
    for other in _bytes_formats.values():
        if other == fmt:
            continue
        with pytest.raises(ValueError):
            cls._imgshape(b64decode(twopixel[other]))


@pytest.mark.parametrize('cls,fmt', list(_bytes_formats.items()), ids=lambda v: getattr(v, 'name', v))
def test_image_from_bytes_detects_format(cls, fmt, document, comm):
    data = b64decode(twopixel[fmt])
    for img_cls in _bytes_formats:
        assert bool(img_cls.applies(data)) == (img_cls is cls)

    model = Image(data).get_root(document, comm)
    filetype = 'x-icon' if cls is ICO else cls.filetype
    assert f'data:image/{filetype};base64' in model.text
    assert model.width == 2
    assert model.height == 1
