"""A Model of an Author"""
from typing import List

import panel as pn
import param

from .base_model import BaseModel

STYLE = "img.pnx-avatar {height:100%;width:100%;border-radius:50%;vertical-align: middle;}"
if STYLE not in pn.config.raw_css:
    pn.config.raw_css.append(STYLE)


class Person(BaseModel):
    """A Model of an Author"""

    name = param.String(doc="The name of the person.")
    url = param.String(doc="A link to a page about the author.")
    avatar_url = param.String(doc="A link to an avatar image of the author.")

    twitter_url = param.String(doc="A link to the Twitter page of the Author")
    linkedin_url = param.String(doc="A link to the Linked In page of the Author")
    github_url = param.String(doc="A link to the Github page of the Author")

    all: List["Person"] = []

    def __init__(self, **params):
        super().__init__(**params)

        self.all.append(self)

    def _repr_html_(self):
        # pylint: disable=line-too-long
        return f"""<a href="{ self.url }" target="_blank"><img src="{ self.avatar_url }" class="pnx-avatar" alt="Avatar" title="{ self.name}"></a>"""
