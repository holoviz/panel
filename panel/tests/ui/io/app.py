import panel as pn

pn.config.raw_css = ['.bk-Row { background-color: purple; }']

button = pn.widgets.Button(name='Click')

string = pn.pane.Str(object=0, css_classes=['string'])

def cb(event):
    string.object += 1

button.on_click(cb)

pn.Row(button, string).servable()
