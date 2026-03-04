"""React counter button using Preact JSX via import map."""
import param
import panel as pn
from panel.custom import AnyWidgetComponent

class ReactCounterButton(AnyWidgetComponent):
    value = param.Integer()

    _importmap = {
        "imports": {
            "@anywidget/react": "https://esm.sh/@anywidget/react?deps=react@18.2.0,react-dom@18.2.0",
            "react": "https://esm.sh/react@18.2.0",
        }
    }

    _esm = """
    import * as React from "react";
    import { createRender, useModelState } from "@anywidget/react";

    const render = createRender(() => {
      const [value, setValue] = useModelState("value");
      return (
        <button onClick={() => setValue(value + 1)}>
          count is {value}
        </button>
      );
    });
    export default { render }
    """

component = ReactCounterButton()
