import param

import panel as pn

from panel.custom import Child, ReactComponent


class Example(ReactComponent):

    child = Child()

    child2 = Child()

    color = param.Color()

    text = param.String()

    celebrate = param.Boolean()

    _esm = 'react_demo.js'

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

example = Example(text='Hello World!', child='Wow!')

button = pn.widgets.Button(on_click=lambda e: example.param.update(child='Woo!'), name='Update')

pn.Row(
    pn.Param(example.param, parameters=['color', 'text', 'celebrate']),
    example, button
).servable()
