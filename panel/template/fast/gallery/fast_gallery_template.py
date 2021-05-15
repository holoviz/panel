"""The FastGalleryTemplate can be used to show case your applications in a nice way"""
import pathlib

import param
from ...base import Template, FAVICON_URL
from ....application import Application


ROOT = pathlib.Path(__file__).parent
CSS = (ROOT / "fast_gallery_template.css").read_text()
JS = (ROOT / "fast_gallery_template.js").read_text()
TEMPLATE = (ROOT / "fast_gallery_template.html").read_text()


class FastGalleryTemplate(Template):
    """The FastGalleryTemplate can be used to show case your applications in a nice way"""

    resources = param.List(class_=Application)
    title = param.String(
        default="Gallery",
        doc="""
        A title to show in the header. Also added to the document head
        meta settings and as the browser tab title.""",
    )
    description = param.String("Applications running on the server")
    site = param.String(
        default="",
        doc="""
        The name of the site. Will be shown in the header and link to the
        root of the site. Default is '', i.e. not shown.""",
    )
    site_url = param.String(
        "/",
        doc="""
        Url of the site and logo. Default is '/'.""",
    )

    meta_name = param.String(
        doc="""
        A meta name to add to the document head for search
        engine optimization. For example 'HoloViz Panel Gallery'."""
    )
    meta_description = param.String(
        doc="""
        A meta description to add to the document head for search
        engine optimization. For example 'Applications running on the server'."""
    )
    meta_keywords = param.String(
        doc="""
        Meta keywords to add to the document head for search engine
        optimization. For example 'HoloViz, Panel, Gallery'"""
    )
    meta_author = param.String(
        doc="""
        A meta author to add to the the document head for search
        engine optimization. For example 'HoloViz Panel'."""
    )
    meta_viewport = param.String(
        doc="""
        A meta viewport to add to the header."""
    )

    background_image_url = param.String(
        "https://preview.redd.it/9oi428ohy7t21.png?auto=webp&s=5051b77d33e85446b6492a1e02725c6729777d4f"  # pylint: disable=line-too-long
    )
    target = param.ObjectSelector("_self", objects=["_blank", "_parent", "_top", "_self"])
    favicon = param.String(
        FAVICON_URL,
        constant=True,
        doc="""
        URI of favicon to add to the document head (if local file, favicon is
        base64 encoded as URI).""",
    )
    theme = param.ObjectSelector("default", objects=["dark", "default"])
    theme_toggle = param.Boolean(
        default=True,
        doc="""
        If True a switch to toggle the Theme is shown.""",
    )
    font_family = param.String("Open Sans")
    font_url = param.String("//fonts.googleapis.com/css?family=Open+Sans")
    accent_base_color = param.String("#E1477E")
    footer = param.String()

    def __init__(self, **params):  # pylint: disable=too-many-arguments
        """The FastGalleryTemplate can be used to show case your applications in a nice way"""
        super().__init__(template=TEMPLATE, **params)
        self.add_variable("site_name", self.site)
        self.add_variable("site_url", self.site_url)
        self.add_variable("name", self.title)
        self.add_variable("url", "")
        self.add_variable("description", self.description)
        self.add_variable("background_image_url", self.background_image_url)
        self.add_variable("items", list(sorted(self.resources, key=lambda x: x.name)))
        self.add_variable("gallery_js", JS)
        self.add_variable("gallery_css", CSS)
        self.add_variable("app_favicon", self.favicon)
        self.add_variable("target", self.target)
        self.add_variable("theme", self.theme)
        self.add_variable("theme_toggle", self.theme_toggle)
        self.add_variable("font_family", self.font_family)
        self.add_variable("font_url", self.font_url)
        self.add_variable("accent_base_color", self.accent_base_color)

        self.add_variable("head_title", self._head_title)
        self.add_variable("meta_name", self.meta_name or self._head_title)
        self.add_variable("meta_description", self.meta_description or self.description)
        self.add_variable("meta_keywords", self.meta_keywords)
        self.add_variable("meta_author", self.meta_author)
        self.add_variable("meta_viewport", self.meta_viewport)

        self.add_variable("footer", self.footer)

    @property
    def _head_title(self):
        if self.site and self.title:
            return self.site + " | " + self.title
        if self.title:
            return self.title
        if self.site:
            return self.site
        return "Panel Gallery"

    # def create_from_toml(path: Union[str, pathlib.Path]) -> "FastGalleryTemplate":
    #     raise NotImplementedError()
