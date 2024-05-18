import pathlib

import param

import panel as pn

from panel import ReactComponent


class Example(ReactComponent):

    child = param.ClassSelector(class_=pn.viewable.Viewable)

    child2 = param.ClassSelector(class_=pn.viewable.Viewable)

    color = param.Color()

    text = param.String()

    celebrate = param.Boolean()

    _esm = pathlib.Path(__file__).parent / 'react_demo.js'

    _importmap = {
        "imports": {
            "@emotion/cache": "https://esm.sh/@emotion/cache",
            "@emotion/react": "https://esm.sh/@emotion/react@11.11.4",
            "@mui/material/": "https://esm.sh/@mui/material@5.11.10/",
            "canvas-confetti": "https://esm.sh/canvas-confetti@1.6.0",
        },
        "scopes": {
        }
    }

example = Example(text='Hello World!', child=pn.pane.Markdown('Wow!'))

button = pn.widgets.Button(on_click=lambda e: example.param.update(child=pn.pane.Markdown('Woo!')), name='Update')

pn.Row(
    pn.Param(example.param, parameters=['color', 'text', 'celebrate']),
    example, button
).servable()
