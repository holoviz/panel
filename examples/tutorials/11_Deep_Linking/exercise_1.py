import panel as pn

slider = pn.widgets.FloatSlider(name='Slider', start=0, end=10)

if pn.state.location:
    pn.state.location.sync(slider, {'value': 'slider_value'})

pn.state.location.reload = False

slider.servable()
