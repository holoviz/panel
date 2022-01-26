import panel as pn

pn.extension(sizing_mode="stretch_width", template="fast")

import param

class Hello(param.Parameterized):
    value = param.Parameter("test", readonly=True)

Hello(value="this")

pn.widgets.EditableRangeSlider

