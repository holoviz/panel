"""
Contains Image panes including renderers for PNG, SVG, GIF and JPG
file types.
"""
from __future__ import annotations

import asyncio
import base64
import struct

from collections.abc import Mapping
from io import BytesIO
from pathlib import PurePath
from typing import TYPE_CHECKING, Any, ClassVar

import param

from ..models import PDF as _BkPDF
from ..util import isfile, isurl
from .markup import HTMLBasePane, escape

if TYPE_CHECKING:
    from bokeh.model import Model

_tasks = set()

class FileBase(HTMLBasePane):

    embed = param.Boolean(default=False, doc="""
        Whether to embed the file as base64.""")

    filetype: ClassVar[str]

    _extensions: ClassVar[None | tuple[str, ...]] = None

    _rename: ClassVar[Mapping[str, str | None]] = {'embed': None}

    _rerender_params: ClassVar[list[str]] = [
        'embed', 'object', 'styles', 'width', 'height'
    ]

    __abstract = True

    def __init__(self, object=None, **params):
        if isinstance(object, PurePath):
            object = str(object)
        super().__init__(object=object, **params)

    def _type_error(self, object):
        if isinstance(object, str):
            raise ValueError(
                f"{type(self).__name__} pane cannot parse string that "
                f"is not a filename or URL ({object!r})."
            )
        super()._type_error(object)

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        filetype = cls.filetype.split('+')[0]
        exts = cls._extensions or (filetype,)
        if hasattr(obj, f'_repr_{filetype}_'):
            return 0.15
        if isinstance(obj, PurePath):
            obj = str(obj.absolute())
        if isinstance(obj, str):
            if isurl(obj, exts):
                return True
            elif any(obj.lower().endswith(f'.{ext}') for ext in exts):
                return True
            elif isurl(obj, None):
                return 0.0
        elif isinstance(obj, bytes):
            try:
                cls._imgshape(obj)
                return True
            except Exception:
                return False
        if hasattr(obj, 'read'):  # Check for file like object
            return True
        return False

    def _b64(self, data: str | bytes) -> str:
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:image/{self.filetype};base64,{b64}"

    def _data(self, obj: Any) -> bytes | None:
        filetype = self.filetype.split('+')[0]
        if hasattr(obj, f'_repr_{filetype}_'):
            return getattr(obj, f'_repr_{filetype}_')()
        elif isinstance(obj, (str, PurePath)):
            if isfile(obj):
                with open(obj, 'rb') as f:
                    return f.read()
        elif isinstance(obj, bytes):
            return obj
        elif hasattr(obj, 'read'):
            if hasattr(obj, 'seek'):
                obj.seek(0)
            return obj.read()
        elif not isurl(obj, None):
            return None

        from ..io.state import state
        if state._is_pyodide:
            from ..io.pyodide import _IN_WORKER, fetch_binary
            if _IN_WORKER:
                return fetch_binary(obj).read()
            else:
                from pyodide.http import pyfetch
                async def replace_content():
                    self.object = await (await pyfetch(obj)).bytes()
                task = asyncio.create_task(replace_content())
                _tasks.add(task)
                task.add_done_callback(_tasks.discard)
        else:
            import requests
            r = requests.request(url=obj, method='GET')
            return r.content
        return None


class ImageBase(FileBase):
    """
    Encodes an image as base64 and wraps it in a Bokeh Div model.
    This is an abstract base class that needs the image type
    to be specified and specific code for determining the image shape.

    The filetype determines the filetype, extension, and MIME type for
    this image. Each image type (png,jpg,gif) has a base class that
    supports anything with a `_repr_X_` method (where X is `png`,
    `gif`, etc.), a local file with the given file extension, or a
    HTTP(S) url with the given extension.  Subclasses of each type can
    provide their own way of obtaining or generating a PNG.
    """

    alt_text = param.String(default=None, doc="""
        alt text to add to the image tag. The alt text is shown when a
        user cannot load or display the image.""")

    caption = param.String(default=None, doc="""
        Optional caption for the image.""")

    fixed_aspect = param.Boolean(default=True, doc="""
        Whether the aspect ratio of the image should be forced to be
        equal.""")

    link_url = param.String(default=None, doc="""
        A link URL to make the image clickable and link to some other
        website.""")

    target = param.String(default="_blank", doc="""
        The target attribute specifies where to open the linked document.
        It can be `_self` (default), `_blank`, etc.""")

    _rerender_params: ClassVar[list[str]] = [
        'alt_text', 'caption', 'link_url', 'embed', 'object', 'styles', 'width', 'height', 'target'
    ]

    _rename: ClassVar[Mapping[str, str | None ]] = {
        'alt_text': None, 'fixed_aspect': None, 'link_url': None, 'caption': None, "target": None
    }

    _target_transforms: ClassVar[Mapping[str, str | None]] = {
        'object': """'<img src="' + value + '"></img>'"""
    }

    __abstract = True

    @classmethod
    def _imgshape(cls, data):
        """Calculate and return image width,height"""
        raise NotImplementedError

    def _format_html(
        self, src: str, width: str | None = None, height: str | None = None
    ):
        alt = f'alt={self.alt_text!r}' if self.alt_text else ''
        width = f' width: {width};' if width else ''
        height = f' height: {height};' if height else ''
        object_fit = "contain" if self.fixed_aspect else "fill"
        html = f'<img src="{src}" {alt} style="max-width: 100%; max-height: 100%; object-fit: {object_fit};{width}{height}"></img>'
        if self.link_url:
            html = f'<a href="{self.link_url}" target="{self.target}">{html}</a>'
        if self.caption:
            html = f'<figure>{html}<figcaption>{self.caption}</figcaption></figure>'
        return escape(html)

    def _img_dims(self, width, height):
        smode = self.sizing_mode
        if smode in ['fixed', None]:
            w, h = (
                (f'{width}px' if width else 'auto'),
                (f'{height}px' if height else 'auto')
            )
        elif smode == 'stretch_both' and not self.fixed_aspect:
            w, h = '100%', '100%'
        elif smode == 'stretch_width' and not self.fixed_aspect:
            w, h = '100%', (f'{height}px' if height else 'auto')
        elif smode == 'stretch_height' and not self.fixed_aspect:
            w, h = (f'{width}px' if width else 'auto'), '100%'
        elif smode in ('scale_height', 'stretch_height'):
            w, h = 'auto', '100%'
        else:
            w, h = '100%', 'auto'
        return w, h

    def _transform_object(self, obj: Any) -> dict[str, Any]:
        if self.embed or (isfile(obj) or not isinstance(obj, (str, PurePath))):
            data = self._data(obj)
        elif isinstance(obj, PurePath):
            raise ValueError(f"Could not find {type(self).__name__}.object {obj}.")
        else:
            w, h = self._img_dims(self.width, self.height)
            return dict(object=self._format_html(obj, w, h))

        if data is None:
            return dict(object='<img></img>')
        if not isinstance(data, bytes):
            data = base64.b64decode(data)
        width, height = self._imgshape(data)
        if self.width is not None:
            if self.height is None:
                height = int((self.width/width)*height)
            else:
                height = self.height
            width = self.width
        elif self.height is not None:
            width = int((self.height/height)*width)
            height = self.height

        src = self._b64(data)

        w, h = self._img_dims(width, height)
        html = self._format_html(src, w, h)
        return dict(width=width, height=height, object=html)


class Image(ImageBase):
    """
    The `Image` pane embeds any known image format in a panel if
    provided a local path, bytes or remote image link.

    :Example:

    >>> Image(
    ...     'https://panel.holoviz.org/_static/logo_horizontal.png',
    ...     alt_text='The Panel Logo',
    ...     link_url='https://panel.holoviz.org/index.html',
    ...     width=500
    ... )
    """

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        precedences = []
        for img_cls in param.concrete_descendents(ImageBase).values():
            if img_cls is Image:
                continue
            applies = img_cls.applies(obj)
            if isinstance(applies, bool) and applies:
                return applies
            elif isinstance(applies, (float, int)):
                precedences.append(applies)
        if precedences:
            return sorted(precedences)[-1]
        return False

    def _transform_object(self, obj: Any) -> dict[str, Any]:
        params = {
            k: v for k, v in self.param.values().items()
            if k not in ('name', 'object')
        }
        for img_cls in param.concrete_descendents(ImageBase).values():
            if img_cls is not Image and img_cls.applies(obj):
                return img_cls(obj, **params)._transform_object(obj)
        return {'object': '<img></img>'}


class PNG(ImageBase):
    """
    The `PNG` pane embeds a .png image file in a panel if provided a local
    path, or will link to a remote image if provided a URL.

    Reference: https://panel.holoviz.org/reference/panes/PNG.html

    :Example:

    >>> PNG(
    ...     'https://panel.holoviz.org/_static/logo_horizontal.png',
    ...     alt_text='The Panel Logo',
    ...     link_url='https://panel.holoviz.org/index.html',
    ...     width=500
    ... )
    """

    filetype: ClassVar[str] = 'png'

    @classmethod
    def _imgshape(cls, data):
        import struct
        w, h = struct.unpack('>LL', data[16:24])
        return int(w), int(h)


class GIF(ImageBase):
    """
    The `GIF` pane embeds a .gif image file in a panel if provided a local
    path, or will link to a remote image if provided a URL.

    Reference: https://panel.holoviz.org/reference/panes/GIF.html

    :Example:

    >>> GIF(
    ...     'https://upload.wikimedia.org/wikipedia/commons/b/b1/Loading_icon.gif',
    ...     alt_text='A loading spinner',
    ...     link_url='https://commons.wikimedia.org/wiki/File:Loading_icon.gif',
    ...     width=500
    ... )
    """

    filetype: ClassVar[str] = 'gif'

    @classmethod
    def _imgshape(cls, data):
        import struct
        w, h = struct.unpack("<HH", data[6:10])
        return int(w), int(h)


class ICO(ImageBase):
    """
    The `ICO` pane embeds an .ico image file in a panel if provided a local
    path, or will link to a remote image if provided a URL.

    Reference: https://panel.holoviz.org/reference/panes/ICO.html

    :Example:

    >>> ICO(
    ...     some_url,
    ...     alt_text='An .ico file',
    ...     link_url='https://en.wikipedia.org/wiki/ICO_(file_format)',
    ...     width=50
    ...
    """

    filetype: ClassVar[str] = 'ico'

    def _b64(self, data: str | bytes) -> str:
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:image/x-icon;base64,{b64}"

    @classmethod
    def _imgshape(cls, data):
        import struct
        w, h = struct.unpack("<BB" , data[6:8])
        return int(w or 256), int(h or 256)


class JPG(ImageBase):
    """
    The `JPG` pane embeds a .jpg or .jpeg image file in a panel if
    provided a local path, or will link to a remote image if provided
    a URL.

    Reference: https://panel.holoviz.org/reference/panes/JPG.html

    :Example:

    >>> JPG(
    ...     'https://www.gstatic.com/webp/gallery/4.sm.jpg',
    ...     alt_text='A nice tree',
    ...     link_url='https://en.wikipedia.org/wiki/JPEG',
    ...     width=500
    ... )
    """

    filetype: ClassVar[str] = 'jpeg'

    _extensions: ClassVar[tuple[str, ...]] = ('jpeg', 'jpg')

    @classmethod
    def _imgshape(cls, data):
        import struct
        b = BytesIO(data)
        b.read(2)
        c = b.read(1)
        while (c and ord(c) != 0xDA):
            while (ord(c) != 0xFF): c = b.read(1)
            while (ord(c) == 0xFF): c = b.read(1)
            if (ord(c) >= 0xC0 and ord(c) <= 0xC3):
                b.read(3)
                h, w = struct.unpack(">HH", b.read(4))
                break
            else:
                b.read(int(struct.unpack(">H", b.read(2))[0])-2)
            c = b.read(1)
        return int(w), int(h)


class SVG(ImageBase):
    """
    The `SVG` pane embeds a .svg image file in a panel if provided a
    local path, or will link to a remote image if provided a URL.

    Reference: https://panel.holoviz.org/reference/panes/SVG.html

    :Example:

    >>> SVG(
    ...     'https://upload.wikimedia.org/wikipedia/commons/6/6b/Bitmap_VS_SVG.svg',
    ...     alt_text='A gif vs svg comparison',
    ...     link_url='https://en.wikipedia.org/wiki/SVG',
    ...     width=300, height=400
    ... )
    """

    encode = param.Boolean(default=True, doc="""
        Whether to enable base64 encoding of the SVG, base64 encoded
        SVGs do not support links.""")

    filetype: ClassVar[str] = 'svg+xml'

    _rename: ClassVar[Mapping[str, str | None]] = {'encode': None}

    _rerender_params: ClassVar[list[str]] = ImageBase._rerender_params + ['encode']

    @classmethod
    def applies(cls, obj: Any) -> float | bool | None:
        return (super().applies(obj) or
                (isinstance(obj, str) and obj.lstrip().startswith('<svg')))

    def _type_error(self, object):
        if isinstance(object, str):
            raise ValueError(f"{type(self).__name__} pane cannot parse string that is not a filename, "
                             "URL or a SVG XML contents.")
        super()._type_error(object)

    def _data(self, obj):
        if (isinstance(obj, str) and obj.lstrip().startswith('<svg')):
            return obj
        return super()._data(obj)

    def _imgshape(self, data):
        return (self.width, self.height)

    def _transform_object(self, obj: Any) -> dict[str, Any]:
        width, height = self.width, self.height
        w, h = self._img_dims(width, height)
        if self.embed or (isfile(obj) or (isinstance(obj, str) and obj.lstrip().startswith('<svg'))
                          or not isinstance(obj, (str, PurePath))):
            data = self._data(obj)
        elif isinstance(obj, PurePath):
            raise ValueError(f"Could not find {type(self).__name__}.object {obj}.")
        else:
            return dict(object=self._format_html(obj, w, h))

        if data is None:
            return dict(object='<img></img>')
        if self.encode:
            ws = f' width: {w};' if w else ''
            hs = f' height: {h};' if h else ''
            object_fit = "contain" if self.fixed_aspect else "fill"
            data = f'<img src="{self._b64(data)}" style="max-width: 100%; max-height: 100%; object-fit: {object_fit};{ws}{hs}"></img>'
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return dict(width=width, height=height, text=escape(data))


class PDF(FileBase):
    """
    The `PDF` pane embeds a .pdf image file in a panel if provided a
    local path, or will link to a remote image if provided a URL.

    Reference: https://panel.holoviz.org/reference/panes/PDF.html

    :Example:

    >>> PDF(
    ...     'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
    ...     width=300, height=410
    ... )
    """

    start_page = param.Integer(default=1, doc="""
        Start page of the pdf, by default the first page.""")

    filetype: ClassVar[str] = 'pdf'

    _bokeh_model: ClassVar[type[Model]] = _BkPDF

    _rename: ClassVar[Mapping[str, str | None]] = {'embed': 'embed'}

    _rerender_params: ClassVar[list[str]] = FileBase._rerender_params + ['start_page']

    @classmethod
    def _imgshape(cls, data):
        assert data.startswith(b'%PDF-')
        return 0, 0

    def _transform_object(self, obj: Any) -> dict[str, Any]:
        if obj is None:
            return dict(object='<embed></embed>')
        elif self.embed or not isurl(obj):
            # This is handled by the Typescript Bokeh model to be able to render large PDF files (>2MB).
            data = self._data(obj)
            if not isinstance(data, bytes):
                data = data.encode('utf-8')
            b64 = base64.b64encode(data).decode("utf-8")
            if self.embed:
                return dict(text=b64)
            obj = f'data:application/pdf;base64,{b64}'

        w, h = self.width or '100%', self.height or '100%'
        page = f'#page={self.start_page}' if getattr(self, 'start_page', None) else ''
        html = f'<embed src="{obj}{page}" width={w!r} height={h!r} type="application/pdf">'
        return dict(text=escape(html))

class WebP(ImageBase):
    """
    The `WebP` pane embeds a .webp image file in a panel if
    provided a local path, or will link to a remote image if provided
    a URL.

    Reference: https://panel.holoviz.org/reference/panes/WebP.html

    :Example:

    >>> WebP(
    ...     'https://assets.holoviz.org/panel/samples/webp_sample.webp',
    ...     alt_text='A nice tree',
    ...     link_url='https://en.wikipedia.org/wiki/WebP',
    ...     width=500,
    ...     caption='A nice tree'
    ... )
    """

    filetype: ClassVar[str] = 'webp'

    _extensions: ClassVar[tuple[str, ...]] = ('webp',)

    @classmethod
    def _imgshape(cls, data):
        with BytesIO(data) as b:
            b.read(12)  # Skip RIFF header
            chunk_header = b.read(4).decode('utf-8')
            if chunk_header[:3] != 'VP8':
                raise ValueError("Invalid WebP file")
            wptype = chunk_header[3]
            b.read(4)
            if wptype == 'X':
                b.read(4)
                w = int.from_bytes(b.read(3), 'little') + 1
                h = int.from_bytes(b.read(3), 'little') + 1
            elif wptype == 'L':
                b.read(1)
                bits = struct.unpack("<I", b.read(4))[0]
                w = (bits & 0x3FFF) + 1
                h = ((bits >> 14) & 0x3FFF) + 1
            elif wptype == ' ':
                b.read(6)
                w = int.from_bytes(b.read(2), 'little') + 1
                h = int.from_bytes(b.read(2), 'little') + 1
        return int(w), int(h)

class AVIF(ImageBase):
    """
    The `AVIF` pane embeds a .avif image file in a panel if
    provided a local path, or will link to a remote image if provided
    a URL.

    Reference: https://panel.holoviz.org/reference/panes/AVIF.html

    :Example:

    >>> AVIF(
    ...     'https://assets.holoviz.org/panel/samples/avif_sample.avif',
    ...     alt_text='A nice tree',
    ...     link_url='https://en.wikipedia.org/wiki/AVIF',
    ...     width=500
    ... )
    """

    filetype: ClassVar[str] = "avif"

    _extensions: ClassVar[tuple[str, ...]] = ("avif",)

    @classmethod
    def _imgshape(cls, data: bytes) -> tuple[int, int]:
        # The width and height position are stored withyin the ispe box, its format is :
        # ispe + 4 bytes + 4 bytes for width + 4 bytes for height

        ispe = data.find(b"ispe")
        w = int.from_bytes(data[ispe + 8 : ispe + 12], byteorder="big", signed=False)
        h = int.from_bytes(data[ispe + 12 : ispe + 16], byteorder="big", signed=False)

        return w, h
