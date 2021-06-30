"""
Contains Image panes including renderers for PNG, SVG, GIF and JPG
file types.
"""
import base64

from io import BytesIO
from six import string_types

import param

from .markup import escape, DivPaneBase
from ..util import isfile, isurl


class FileBase(DivPaneBase):

    embed = param.Boolean(default=True, doc="""
        Whether to embed the file as base64.""")

    _rerender_params = ['embed', 'object', 'style', 'width', 'height']

    __abstract = True

    def _type_error(self, object):
        if isinstance(object, string_types):
            raise ValueError("%s pane cannot parse string that is not a filename "
                             "or URL." % type(self).__name__)
        super()._type_error(object)

    @classmethod
    def applies(cls, obj):
        filetype = cls.filetype
        if hasattr(obj, '_repr_{}_'.format(filetype)):
            return True
        if isinstance(obj, string_types):
            if isfile(obj) and obj.endswith('.'+filetype):
                return True
            if isurl(obj, [cls.filetype]):
                return True
            elif isurl(obj, None):
                return 0
        if hasattr(obj, 'read'):  # Check for file like object
            return True
        return False

    def _data(self):
        if hasattr(self.object, '_repr_{}_'.format(self.filetype)):
            return getattr(self.object, '_repr_' + self.filetype + '_')()
        if isinstance(self.object, string_types):
            if isfile(self.object):
                with open(self.object, 'rb') as f:
                    return f.read()
        if hasattr(self.object, 'read'):
            if hasattr(self.object, 'seek'):
                self.object.seek(0)
            return self.object.read()
        if isurl(self.object, None):
            import requests
            r = requests.request(url=self.object, method='GET')
            return r.content


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

    link_url = param.String(default=None, doc="""
        A link URL to make the image clickable and link to some other
        website.""")

    filetype = 'None'

    _rerender_params = ['alt_text', 'link_url', 'embed', 'object', 'style', 'width', 'height']

    _target_transforms = {'object': """'<img src="' + value + '"></img>'"""}

    __abstract = True

    def _b64(self):
        data = self._data()
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        b64 = base64.b64encode(data).decode("utf-8")
        return "data:image/"+self.filetype+f";base64,{b64}"

    def _imgshape(self, data):
        """Calculate and return image width,height"""
        raise NotImplementedError

    def _get_properties(self):
        p = super()._get_properties()
        if self.object is None:
            return dict(p, text='<img></img>')
        data = self._data()
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
        if not self.embed:
            src = self.object
        else:
            b64 = base64.b64encode(data).decode("utf-8")
            src = "data:image/"+self.filetype+";base64,{b64}".format(b64=b64)

        smode = self.sizing_mode
        if smode in ['fixed', None]:
            w, h = '%spx' % width, '%spx' % height
        elif smode == 'stretch_both':
            w, h = '100%', '100%'
        elif smode == 'stretch_width':
            w, h = '%spx' % width, '100%'
        elif smode == 'stretch_height':
            w, h = '100%', '%spx' % height
        elif smode == 'scale_height':
            w, h = 'auto', '100%'
        else:
            w, h = '100%', 'auto'

        html = '<img src="{src}" width="{width}" height="{height}" alt="{alt}"></img>'.format(
            src=src, width=w, height=h, alt=self.alt_text or '')

        if self.link_url:
            html = '<a href="{url}" target="_blank">{html}</a>'.format(
                url=self.link_url, html=html)

        return dict(p, width=width, height=height, text=escape(html))


class PNG(ImageBase):

    filetype = 'png'

    @classmethod
    def _imgshape(cls, data):
        import struct
        w, h = struct.unpack('>LL', data[16:24])
        return int(w), int(h)


class GIF(ImageBase):

    filetype = 'gif'

    @classmethod
    def _imgshape(cls, data):
        import struct
        w, h = struct.unpack("<HH", data[6:10])
        return int(w), int(h)


class JPG(ImageBase):

    filetype = 'jpg'

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

    encode = param.Boolean(default=False, doc="""
        Whether to enable base64 encoding of the SVG, base64 encoded
        SVGs do not support links.""")

    filetype = 'svg'

    _rerender_params = ImageBase._rerender_params + ['encode']

    @classmethod
    def applies(cls, obj):
        return (super().applies(obj) or
                (isinstance(obj, string_types) and obj.lstrip().startswith('<svg')))

    def _type_error(self, object):
        if isinstance(object, string_types):
            raise ValueError("%s pane cannot parse string that is not a filename, "
                             "URL or a SVG XML contents." % type(self).__name__)
        super()._type_error(object)

    def _data(self):
        if (isinstance(self.object, string_types) and
            self.object.lstrip().startswith('<svg')):
            return self.object
        return super()._data()

    def _b64(self):
        data = self._data()
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:image/svg+xml;base64,{b64}"

    def _imgshape(self, data):
        return (self.width, self.height)

    def _get_properties(self):
        p = super(ImageBase, self)._get_properties()
        if self.object is None:
            return dict(p, text='<img></img>')
        data = self._data()
        width, height = self._imgshape(data)
        if not isinstance(data, bytes):
            data = data.encode('utf-8')

        if self.encode:
            b64 = base64.b64encode(data).decode("utf-8")
            src = "data:image/svg+xml;base64,{b64}".format(b64=b64)
            html = "<img src='{src}' width={width} height={height}></img>".format(
                src=src, width=width, height=height
            )
        else:
            html = data.decode("utf-8")
        return dict(p, width=width, height=height, text=escape(html))


class PDF(FileBase):

    filetype = 'pdf'

    def _get_properties(self):
        p = super()._get_properties()
        if self.object is None:
            return dict(p, text='<embed></embed>')
        if self.embed:
            data = self._data()
            if not isinstance(data, bytes):
                data = data.encode('utf-8')
            base64_pdf = base64.b64encode(data).decode("utf-8")
            src = f"data:application/pdf;base64,{base64_pdf}"
        else:
            src = self.object
        w, h = self.width or '100%', self.height or '100%'
        html = f'<embed src="{src}" width={w!r} height={h!r} type="application/pdf">'
        return dict(p, text=escape(html))
