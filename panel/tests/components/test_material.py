"""Showcase of the **Material Components**

Using the upcoming [WebComponent](https://github.com/holoviz/panel/pull/1252) it is relatively
straightforward to implement the \
[Material Web Components]\
(https://github.com/material-components/material-components-web-components#readme) and use them
in your Panel Application.

This can give you a **more modern look and feel** of your Panel application than using the default
Panel components.

You can find the implementation [here](https://github.com/MarcSkovMadsen/awesome-panel/blob/\
master/package/awesome_panel/express/components/material/__init__.py),
"""
import panel as pn

import material
from panel.widgets import WebComponent


def section(component, message=None, show_html=False):
    """Helper function. Turns the component into a tuple of components containing

    - Title
    - Description
    - The Component
    - A Param of the Component parameters
    - A Divider
    """
    title = "## " + str(type(component)).split(".")[1][:-2]

    parameterset = set(component.param.objects()) - set(WebComponent.param.objects())
    if show_html:
        parameterset.add("html")
    for parameter in component.parameters_to_watch:
        parameterset.add(parameter)

    parameters = list(parameterset)
    if message:
        return (
            pn.pane.Markdown(title),
            component,
            pn.Param(component, parameters=parameters),
            pn.pane.Markdown(message),
            pn.layout.Divider(),
        )
    return (
        pn.pane.Markdown(title),
        component,
        pn.Param(component, parameters=parameters),
        pn.layout.Divider(),
    )


def view(configure=False) -> pn.Column:
    """Returns a view of the Material Components

    Args:
        configure (bool, optional): Set this to True to include Material JS and CSS.
        Defaults to False.

    Returns:
        pn.Column: A Column view of the Material Components
    """
    button = material.MWCButton(name="Click Me", icon="favorite")
    select = material.MWCSelect(name="Framework", options={"p": "Panel", "v": "Voila"}, value="p")
    slider = material.MWCSlider(name="Slide Me")

    objects = [
        pn.pane.Markdown(__doc__),
        pn.layout.Divider(),
        *section(button),
        *section(select),
        *section(slider),
    ]

    if configure:
        pn.config.js_files["mwc"] = material.MWC_JS
        objects.append(material.fonts_pane)

    return pn.Column(*objects, name="Material Components", sizing_mode="fixed", width=500)


if __name__.startswith("bokeh"):
    view(configure=True).servable()
