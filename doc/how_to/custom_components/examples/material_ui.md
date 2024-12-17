# Wrapping Material UI components

:::{note}
The `MaterialBase` component is defined before the call to `pn.extension` to allow us to load the `_extension_name` and thereby initialize the required JS and CSS resources. Ordinarily the component would be defined in an external module.
:::

```{pyodide}
import param
import panel as pn

from panel.reactive import ReactiveHTML

class MaterialBase(ReactiveHTML):

    __javascript__ = ['https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js']

    __css__ = ['https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css']

    _extension_name = 'material_ui'

pn.extension('material_ui', template='material')
```

This example demonstrates how to wrap Material UI components using `ReactiveHTML`.

```{pyodide}
class MaterialTextField(MaterialBase):

    value = param.String(default='')

    _template = """
    <label id="text-field" class="mdc-text-field mdc-text-field--filled">
      <span class="mdc-text-field__ripple"></span>
      <span class="mdc-floating-label">Label</span>
      <input id="text-input" type="text" class="mdc-text-field__input" aria-labelledby="my-label" value="${value}"></input>
      <span class="mdc-line-ripple"></span>
    </label>
    """

    _dom_events = {'text-input': ['change']}

    _scripts = {
        'render': "mdc.textField.MDCTextField.attachTo(text_field);"
    }

class MaterialSlider(MaterialBase):

    end = param.Number(default=100)

    start = param.Number(default=0)

    value = param.Number(default=50)

    _template = """
    <div id="mdc-slider" class="mdc-slider" style="width: ${model.width}px">
      <input id="slider-input" class="mdc-slider__input" min="${start}" max="${end}" value="${value}">
      </input>
      <div class="mdc-slider__track">
        <div class="mdc-slider__track--inactive"></div>
        <div class="mdc-slider__track--active">
          <div class="mdc-slider__track--active_fill"></div>
        </div>
      </div>
      <div class="mdc-slider__thumb">
        <div class="mdc-slider__thumb-knob"></div>
      </div>
    </div>
    """

    _scripts = {
        'render': """
            slider_input.setAttribute('value', data.value)
            state.slider = mdc.slider.MDCSlider.attachTo(mdc_slider)
        """,
        'value': """
            state.slider.setValue(data.value)
        """
    }

slider     = MaterialSlider(value=5, start=0, end=100, width=200)
text_field = MaterialTextField()

pn.Row(
    pn.Column(
        slider.controls(['value']),
        slider
    ),
    pn.Column(
        text_field.controls(['value']),
        text_field
    ),
).servable()
```
