import pathlib

import param

import panel as pn

from panel.custom import ReactComponent


class MuiComponent(ReactComponent):

    _importmap = {
        "imports": {
            "@mui/material/": "https://esm.sh/@mui/material@5.15.16/",
        }
    }

class Button(MuiComponent):

    label = param.String()

    variant = param.Selector(default='contained', objects=['text', 'contained', 'outlined'])

    _esm = 'mui_button.js'


class DiscreteSlider(MuiComponent):

    marks = param.List(default=[
        {
            'value': 0,
            'label': '0°C',
        },
        {
            'value': 20,
            'label': '20°C',
        },
        {
            'value': 37,
            'label': '37°C',
        },
        {
            'value': 100,
            'label': '100°C',
        },
    ])

    value = param.Number(default=20)

    _esm = 'mui_slider.js'


b = Button()
s = DiscreteSlider()

pn.Row(
    pn.Param(b.param, parameters=['label', 'variant']),
    pn.Column(b, s)
).servable()
