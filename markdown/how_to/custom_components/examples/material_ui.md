# Wrapping Material UI components

```python
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

```python
class MaterialTextField(MaterialBase):

    value = param.String(default='')

    _template = """
    <label id="text-field" class="mdc-text-field mdc-text-field--filled">
      
      Label
      <input id="text-input" type="text" class="mdc-text-field__input" aria-labelledby="my-label" value="${value}"></input>
      
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
    
      <input id="slider-input" class="mdc-slider__input" min="${start}" max="${end}" value="${value}">
      </input>
      
        
        
          
        
      
      
        
      
    
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
