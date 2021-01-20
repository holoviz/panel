"""The Resource contains meta data like name, description and url"""
import pathlib
from typing import Dict, List

import markdown
import panel as pn
import param

from panel.template.fast.assets.svg import ICONS

from . import category
from .person import Person
from .base_model import BaseModel

MARKDOWN_EXTENSIONS = ["extra", "smarty", "codehilite"]
STYLE = """
.pnx-resource img.pnx-avatar {
    height: 2em;
    width: 2em;
    margin-left: 0.5em;
}
.pnx-resource svg.pnx-icon {
    height: 1.5em;
    margin-left: 0.5em;
    vertical-align: middle;
    fill: currentColor;
}
.pnx-resource a {
    text-decoration: none;
}
"""
if not STYLE in pn.config.raw_css:
    pn.config.raw_css.append(STYLE)


class Resource(BaseModel):
    """The Resource contains meta data like name, description and url"""

    name = param.String(doc="The name")
    introduction = param.String(doc="A short text description.")
    description = param.String(doc="A longer description. Can contain Markdown and HTML")
    author = param.ClassSelector(class_=Person)
    owner = param.ClassSelector(class_=Person)
    url = param.String(doc="A unique, identifying link.")
    thumbnail_url = param.String(doc="A link to a thumbnail image visualizing the resource.")

    tags = param.List(
        class_=str,
        doc="""A list of tags like 'machine-learning', 'panel', 'holoviews'. Don't use spaces in the
        tag.""",
    )
    category = param.String(default=category.NOT_AVAILABLE)

    documentation_url = param.String(doc="A link to the documentation.")
    code_url = param.String(doc="A link to the source code.")
    mp4_url = param.String(doc="A link to a mp4 video.")
    youtube_url = param.String(doc="A link to a youtube video.")
    gif_url = param.String(doc="A link to a .gif video")
    binder_url = param.String(doc="""A link to a notebook on binder""")

    all: List["Resource"] = []

    def __init__(self, **params):
        super().__init__(**params)

        self.all.append(self)

    @staticmethod
    def _get_url_icon_html(
        title,
        url,
    ):
        return (
            f"""<a title="{ title }" appearance="hypertext" href="{ url }" target="_blank">"""
            f"""{ ICONS[title] }</a>"""
        )

    @staticmethod
    def _markdown_to_html(text: str) -> str:
        return markdown.markdown(text, extensions=MARKDOWN_EXTENSIONS, output_format="html5")

    def intro_section(self) -> pn.pane.HTML:
        """An panel with a text introduction to the Resource

        Returns:
            pn.pane.HTML: The Intro Section panel.
        """
        return pn.pane.HTML(self._repr_html_())

    def _repr_html_(self):
        description = self._markdown_to_html(self.description)
        html = f"""<div class="pnx-resource">
        <h1 class="pnx-header">{ self.name }</h1>
        <p>{ description }</p>
        """
        if self.author:
            # pylint: disable=protected-access
            html += f"""<p><strong>Authors:</strong>{ self.author._repr_html_() }</p>"""

        if self.code_url:
            code = self._get_url_icon_html("code", self.code_url)
            html += "<p><strong>Code:</strong>" + code + "</p>"

        resources = ""
        if self.documentation_url:
            resources += self._get_url_icon_html("doc", self.documentation_url)
        if self.gif_url:
            resources += self._get_url_icon_html("gif", self.gif_url)
        if self.mp4_url:
            resources += self._get_url_icon_html("mp4", self.mp4_url)
        if self.youtube_url:
            resources += self._get_url_icon_html("youtube", self.youtube_url)
        if self.binder_url:
            resources += self._get_url_icon_html("binder", self.binder_url)

        if resources:
            html += "<p><strong>Resources:</strong>" + resources + "</p>"

        tags = ", #".join(self.tags)
        if tags:
            html += "<p><strong>Tags:</strong> #" + tags.lower() + "</p>"

        html += "</div>"
        return html

        # author = _to_avatar_icon(resource.author)

    # pylint: disable=arguments-differ
    @classmethod
    def create_from_toml(cls, path: pathlib.Path, persons: Dict) -> Dict:  # type: ignore
        def clean_func(value):
            value["author"] = persons[value["author"]]
            value["owner"] = persons[value["owner"]]
            return value

        return super().create_from_toml(path=path, clean_func=clean_func)
