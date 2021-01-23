"""The FastGalleryTemplate can be used to show case your applications in a nice way"""
import pathlib

import param
from ....template import Template
from ..models import Resource

ROOT = pathlib.Path(__file__).parent
CSS = (ROOT / "fast_gallery_template.css").read_text()
JS = (ROOT / "fast_gallery_template.js").read_text()
TEMPLATE = (ROOT / "fast_gallery_template.html").read_text()
FAVICON = (
    "https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel/"
    "2781d86d4ed141889d633748879a120d7d8e777a/assets/images/favicon.ico"
)


class FastGalleryTemplate(Template):
    """The FastGalleryTemplate can be used to show case your applications in a nice way"""

    resources = param.List(class_=Resource)
    title = param.String(
        default="Panel Application",
        doc="""
        A title to show in the header. Also added to the document head
        meta settings and as the browser tab title.""",
    )

    site = param.String(
        default="",
        doc="""
        The name of the site. Will be shown in the header and link to the
        root of the site. Default is '', i.e. not shown.""",
    )

    description = param.String("")
    background_image_url = param.String(
        "https://preview.redd.it/9oi428ohy7t21.png?auto=webp&s=5051b77d33e85446b6492a1e02725c6729777d4f"  # pylint: disable=line-too-long
    )
    target = param.ObjectSelector("_self", objects=["_blank", "_parent", "_top", "_self"])
    favicon = param.String(FAVICON)
    accent_base_color = param.String("#E1477E")
    font_family = param.String("Open Sans")
    font_url = param.String("//fonts.googleapis.com/css?family=Open+Sans")

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
        self.add_variable("gallery_js", JS)
        self.add_variable("gallery_css", CSS)
        self.add_variable("favicon", self.favicon)
        self.add_variable("accent_base_color", self.accent_base_color)
        self.add_variable("font_family", self.font_family)
        self.add_variable("font_url", self.font_url)
        self.add_variable("target", self.target)
