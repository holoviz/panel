"""The FastGalleryTemplate can be used to show case your applications in a nice way"""
import pathlib

import param

from ...template import Template
from ..models import Resource

ROOT = pathlib.Path(__file__).parent
CSS = (ROOT / "fast_gallery_template.css").read_text()
TEMPLATE = (ROOT / "fast_gallery_template.html").read_text()


class FastGalleryTemplate(Template):
    """The FastGalleryTemplate can be used to show case your applications in a nice way"""

    accent_base_color = param.String("#E1477E")

    background_image_url = param.String(default="")

    description = param.String(default="")

    favicon = param.String(default="")

    font_family = param.String("Open Sans")

    font_url = param.String("//fonts.googleapis.com/css?family=Open+Sans")

    target = param.ObjectSelector("_self", objects=["_blank", "_parent", "_top", "_self"])

    title = param.String(default="Panel Application", doc="""
        A title to show in the header. Also added to the document head
        meta settings and as the browser tab title.""")

    site = param.String(default="", doc="""
        The name of the site. Will be shown in the header and link to the
        root of the site. Default is '', i.e. not shown.""")

    def __init__(self, **params):  # pylint: disable=too-many-arguments
        """The FastGalleryTemplate can be used to show case your applications in a nice way"""
        super().__init__(template=TEMPLATE, **params)
        self.add_variable("title_names", self.site + "|" + self.title)
        self.add_variable("site_name", self.site)
        self.add_variable("site_url", "/")
        self.add_variable("name", self.title)
        self.add_variable("url", "")
        self.add_variable("description", self.description)
        self.add_variable("background_image_url", self.background_image_url)
        self.add_variable("items", list(sorted(self.resources, key=lambda x: x.name)))
        self.add_variable("gallery_css", CSS)
        self.add_variable("favicon", self.favicon)
        self.add_variable("accent_base_color", self.accent_base_color)
        self.add_variable("font_family", self.font_family)
        self.add_variable("font_url", self.font_url)
        self.add_variable("target", self.target)
