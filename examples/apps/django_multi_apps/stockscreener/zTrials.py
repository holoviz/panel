import param

import panel as pn


class CustomExample(param.Parameterized):
    """An example Parameterized class"""

    select_string = param.Selector(objects=["red", "yellow", "green"])
    select_number = param.Selector(objects=[0, 1, 10, 100])


pn.Param(CustomExample.param, widgets={
    'select_string': pn.widgets.RadioButtonGroup,
    'select_number': pn.widgets.DiscretePlayer}
)
print(pn.Param)
