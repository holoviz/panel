import panel as pn

pn.extension(sizing_mode="stretch_width", template="fast")
pn.state.template.header_background = "red"
# ...

pn.panel("hello").servable()