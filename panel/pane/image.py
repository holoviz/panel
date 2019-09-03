"""
Contains Image panes including renderers for PNG, SVG, GIF and JPG
file types.
"""
from __future__ import absolute_import, division, unicode_literals

import base64
import os

from io import BytesIO
from six import string_types

import param

from .markup import DivPaneBase


class ImageBase(DivPaneBase):
    """
    Encodes an image as base64 and wraps it in a Bokeh Div model.
    This is an abstract base class that needs the image type
    to be specified and specific code for determining the image shape.

    The imgtype determines the filetype, extension, and MIME type for
    this image. Each image type (png,jpg,gif) has a base class that
    supports anything with a `_repr_X_` method (where X is `png`,
    `gif`, etc.), a local file with the given file extension, or a
    HTTP(S) url with the given extension.  Subclasses of each type can
    provide their own way of obtaining or generating a PNG.
    """

    embed = param.Boolean(default=False, doc="""
        Whether to embed the image as base64 if provided a URL.""")

    imgtype = 'None'

    __abstract = True

    @classmethod
    def applies(cls, obj):
        imgtype = cls.imgtype
        return (hasattr(obj, '_repr_'+imgtype+'_') or
                (isinstance(obj, string_types) and
                 ((os.path.isfile(obj) and obj.endswith('.'+imgtype)) or
                  cls._is_url(obj))))

    @classmethod
    def _is_url(cls, obj):
        return (isinstance(obj, string_types) and
                (obj.startswith('http://') or obj.startswith('https://'))
                and obj.endswith('.'+cls.imgtype))

    def _img(self):
        if not isinstance(self.object, string_types):
            return getattr(self.object, '_repr_'+self.imgtype+'_')()
        elif os.path.isfile(self.object):
            with open(self.object, 'rb') as f:
                return f.read()
        else:
            import requests
            r = requests.request(url=self.object, method='GET')
            return r.content

    def _imgshape(self, data):
        """Calculate and return image width,height"""
        raise NotImplementedError

    def _get_properties(self):
        p = super(ImageBase, self)._get_properties()
        if self.object is None:
            return dict(p, text='<img></img>')
        data = self._img()
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
        if self._is_url(self.object) and not self.embed:
            src = self.object
        else:
            b64 = base64.b64encode(data).decode("utf-8")
            src = "data:image/"+self.imgtype+";base64,{b64}".format(b64=b64)

        smode = self.sizing_mode
        if smode in ['fixed', None]:
            w, h = '%spx' % width, '%spx' % height
        elif smode == 'stretch_both':
            w, h = '100%', '100%'
        elif smode == 'stretch_height':
            w, h = '%spx' % width, '100%'
        elif smode == 'stretch_height':
            w, h = '100%', '%spx' % height
        elif smode == 'scale_height':
            w, h = 'auto', '100%'
        else:
            w, h = '100%', 'auto'

        html = "<img src='{src}' width='{width}' height='{height}'></img>".format(
            src=src, width=w, height=h)

        return dict(p, width=width, height=height, text=html)


class PNG(ImageBase):

    imgtype = 'png'

    @classmethod
    def _imgshape(cls, data):
        import struct
        w, h = struct.unpack('>LL', data[16:24])
        return int(w), int(h)


class GIF(ImageBase):

    imgtype = 'gif'

    @classmethod
    def _imgshape(cls, data):
        import struct
        w, h = struct.unpack("<HH", data[6:10])
        return int(w), int(h)


class JPG(ImageBase):

    imgtype = 'jpg'

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

    imgtype = 'svg'

    @classmethod
    def applies(cls, obj):
        return (super(SVG, cls).applies(obj) or
                (isinstance(obj, string_types) and obj.lstrip().startswith('<svg')))

    def _img(self):
        if (isinstance(self.object, string_types) and
            self.object.lstrip().startswith('<svg')):
            return self.object
        return super(SVG, self)._img()

    def _imgshape(self, data):
        return (self.width, self.height)

    def _get_properties(self):
        p = super(ImageBase, self)._get_properties()
        if self.object is None:
            return dict(p, text='<img></img>')
        data = self._img()
        width, height = self._imgshape(data)
        if not isinstance(data, bytes):
            data = data.encode('utf-8')
        b64 = base64.b64encode(data).decode("utf-8")
        src = "data:image/svg+xml;base64,{b64}".format(b64=b64)
        html = "<img src='{src}' width={width} height={height}></img>".format(
            src=src, width=width, height=height
        )
        return dict(p, width=width, height=height, text=html)
