"""The FastGalleryTemplate can be used to show case your applications and other resources in a
nice Gallery"""
import pathlib

import param
from ...base import Template, FAVICON_URL
from ....site import Application


ROOT = pathlib.Path(__file__).parent
CSS = (ROOT / "fast_gallery_template.css").read_text()
JS = (ROOT / "fast_gallery_template.js").read_text()
TEMPLATE = (ROOT / "fast_gallery_template.html").read_text()


class FastGalleryTemplate(Template):
    """The FastGalleryTemplate can be used to show case your applications in a nice way"""

    applications = param.List(class_=Application, doc="""
        The list of applications to show in the Gallery
        """)
    site = param.String(
        default="Panel",
        doc="""
        The name of the site. Will be shown in the header and link to the
        site_url. Default is 'Panel'.""",
    )
    site_url = param.String(
        "/",
        doc="""
        Url of the site and logo. Default is '/'.""",
    )
    title = param.String(
        default="Gallery",
        doc="""
        The name of the gallery. Shown in the header and browser tab. Default is 'Gallery'""",
    )
    description = param.String("Applications running on the server", doc="""
    A description shown in the header. Default is 'Applications running on the server'.
    """)

    background_image = param.String(
        "https://preview.redd.it/9oi428ohy7t21.png?auto=webp&s=5051b77d33e85446b6492a1e02725c6729777d4f",  # pylint: disable=line-too-long
        doc="""
        The url of an image to show in the header"""
    )

    theme = param.ObjectSelector("default", objects=["dark", "default"])
    theme_toggle = param.Boolean(
        default=True,
        doc="""
        Whether or not to enable toggling the theme via a switchbox. Default is True""",
    )
    font_family = param.String("Open Sans", doc="""
    The name of the font family to use. Default is 'Open Sans'.""")
    font_url = param.String("//fonts.googleapis.com/css?family=Open+Sans")
    accent_base_color = param.String("#E1477E", doc="""
    The Accent Color. Default is '#E1477E'.""")
    footer = param.String(doc="""
    Footer text. Default is ''""")

    target = param.ObjectSelector("_self", objects=["_blank", "_parent", "_top", "_self"], doc="""
    How to open the url. One of '_blank', '_parent', '_top' or '_self' (default).""")

    favicon = param.String(
        FAVICON_URL,
        constant=True,
        doc="""
        URI of favicon to add to the document head (if local file, favicon is
        base64 encoded as URI).""",
    )
    meta_name = param.String(
        doc="""
        A meta name to add to the document head for search
        engine optimization. For example 'HoloViz Panel Gallery'. If none is specified the title
        will be used."""
    )
    meta_description = param.String(
        doc="""
        A meta description to add to the document head for search
        engine optimization. For example 'Applications running on the server'. If none is specified
        the description will be used."""
    )
    meta_keywords = param.String(
        doc="""
        Meta keywords to add to the document head for search engine
        optimization. For example 'HoloViz, Panel, Gallery'. Default is ''."""
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

    def __init__(self, **params):  # pylint: disable=too-many-arguments
        """The FastGalleryTemplate can be used to show case your applications in a nice way"""
        super().__init__(template=TEMPLATE, **params)
        self.add_variable("site_name", self.site)
        self.add_variable("site_url", self.site_url)
        self.add_variable("name", self.title)
        self.add_variable("url", "")
        self.add_variable("description", self.description)
        self.add_variable("background_image", self.background_image)
        self.add_variable("applications", list(sorted(self.applications, key=lambda x: x.name)))
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
