"""In this module we define a Card inspired by the Bootstrap Card

- https://getbootstrap.com/docs/4.3/components/card/ and
- https://disjfa.github.io/bootstrap-tricks/card-collapse-tricks/"""
# @Philippfr. I'm not sure this is the way you would like a new layout/ a card implemented
# Is there some better way to implement this? Custom Bokeh Model?
# Maybe the layout.py file should be refactored into a layout folder and seperate files?
from typing import List

import param

from panel.layout import Column, HSpacer, Row
from panel.pane import Markdown, HTML
from panel.viewable import Viewable
from panel.widgets.button import Button
from panel import panel


class Card(Column):
    """A Card inspired by the Bootstrap Card

    - https://getbootstrap.com/docs/4.3/components/card/ and
    - https://disjfa.github.io/bootstrap-tricks/card-collapse-tricks/
    """
    header = param.String(None)
    body = param.List(default=[], doc="""
        The list of child objects that make up the card.""")
    collapsable = param.Boolean(False)


    _rename = {**Column._rename, "header": None, "body": None, "collapsable": None}

    def __init__(
        self,
        **params,
    ):
        if "css_classes" not in params:
            params["css_classes"] = []
        if "card" not in params["css_classes"]:
            params["css_classes"].append("card")
        if "sizing_mode" not in params and "width" not in params:
            params["sizing_mode"] = "stretch_width"

        if "body" in params:
            panels = params.pop("body")
        else:
            panels = self.param.body.default
        if "collapsable" in params:
            collapsable = params.pop("collapsable")
        else:
            collapsable = self.param.collapsable.default
        if "header" in params:
            header = params.pop("header")
        else:
            header = self.param.header.default

        print(params)
        # Due to https://github.com/holoviz/panel/issues/903 we have to insert the content into a
        # column with relevant margin
        content = self._get_card_content(panels)
        if not collapsable:
            header_pane = self.get_card_header(header)
            super().__init__(
                header_pane, content, **params,
            )
            return

        collapse_button = Button(
            name="-", width=30, sizing_mode="stretch_height", css_classes=["flat"],
        )

        def click_callback(event,):
            if event.new % 2 == 1:
                self.remove(content)
                collapse_button.name = "+"
            elif event.new > 0:
                self.append(content)
                collapse_button.name = "-"

        collapse_button.on_click(click_callback)
        header_row = Row(
            f'<h5 class="card-header"">{header}</h5>',
            HSpacer(),
            collapse_button,
            css_classes=["card-header"],
        )
        super().__init__(
            header_row, content, **params,
        )

    def clone(self, *objects, **params):
        # Hack. See https://github.com/holoviz/panel/issues/1060
        header, body = self.objects
        return super().clone(header.object, body, **params)

    def _get_card_content(self, panels: List[Viewable],) -> Viewable:
        """Combines the list of Viewables into a Viewable with the right css classes

        Args:
            panels (List[Viewable]): A list of Viewables

        Returns:
            Viewable: A Viewable of the input Viewables with the right css classes \
                applied.
        """
        # Due to https://github.com/holoviz/panel/issues/903 we have to insert the content into a
        # column with relevant margin
        content = Column(
            *[self.get_card_panel(panel) for panel in panels],
            css_classes=["card-body"],
            sizing_mode="stretch_width",
            margin=(0, 2, 2, 0,),
        )
        # Due to Bokeh formatting every card-panel is 5px inside the card-body
        # and thus we cannot get borders to overlap.
        # So the first panel should have no border to hide this fact
        if len(content) > 0:
            if content[0].css_classes and "card-panel" in content[0].css_classes:
                content[0].css_classes.remove("card-panel")
                content[0].css_classes.append("card-panel-first")
            else:
                content[0].css_classes = ["card-panel-first"]
        return content

    @staticmethod
    def get_card_header(text: str, **params,) -> HTML:
        """[summary]

        Arguments:
            text {str} -- A header string like 'Card Header'. May also contain HTML tags like <a>
            and <i>

        Returns:
            HTML -- The header text as a HTML Pane
        """
        if "css_classes" not in params:
            params["css_classes"] = []
        if "card-header" not in params["css_classes"]:
            params["css_classes"].append("card-header")
        if "sizing_mode" not in params and "width" not in params:
            params["sizing_mode"] = "stretch_width"
        if "margin" not in params:
            params["margin"] = 0
        object_ = f'<h5 class="card-header"">{text}</h5>'

        return HTML(object_, **params,)

    @staticmethod
    def get_card_panel(obj, **params,) -> Viewable:
        """A Card Panel to be inserted into the body of the Card

        Arguments:
            obj {[type]} -- Any type that can be converted to a panel. An obj of type 'str' will
            always be converted to a Markdown pane

        Returns:
            Viewable -- A Viewable of the obj
        """
        if "css_classes" not in params:
            params["css_classes"] = []
        if "card-panel" not in params["css_classes"]:
            params["css_classes"].append("card-panel")
        if "sizing_mode" not in params and "width" not in params:
            params["sizing_mode"] = "stretch_width"

        if isinstance(obj, str,):
            return Markdown(obj, **params,)

        return panel(obj, **params,)
