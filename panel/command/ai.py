import re

from bokeh.command.subcommand import Subcommand

from .. import __version__

_DOCS_RE = re.match(r"\d+\.\d+\.\d+", __version__)
_DOCS_VERSION = _DOCS_RE.group(0) if _DOCS_RE else "latest"
_DOCS_BASE = f"https://panel.holoviz.org/en/docs/{_DOCS_VERSION}"
_TXT = f"""\
Panel is a Python library for building interactive dashboards and web apps.
Widgets, plots and layouts are ordinary Python objects that you compose and
bind to your data, then serve with `panel serve app.py`.

Resources for using AI assistants with Panel:

  Panel llms.txt (curated index of the docs for assistants):
    {_DOCS_BASE}/llms.txt

  Markdown versions of the docs, e.g.:
    {_DOCS_BASE}/tutorials/basic/build_dashboard.html
  becomes:
    {_DOCS_BASE}/markdown/tutorials/basic/build_dashboard.md

  HoloViz Agent Skills:
    https://skills.holoviz.org/
      uvx holoviz-skills@latest install
    or
      pip install holoviz-skills
      holoviz-skills install

  Guide: Using Panel with an AI assistant:
    {_DOCS_BASE}/markdown/how_to/use_llms.md"""


class AI(Subcommand):
    ''' Subcommand to display resources for using Panel with AI assistants.

    '''

    name = "ai"

    help = "Show resources for using Panel with AI assistants"

    args = ()

    def invoke(self, args):
        print(_TXT)  # noqa: T201
