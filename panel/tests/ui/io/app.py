import panel as pn

pn.config.raw_css = ['.bk-Row { background-color: purple; }']

if 'num' in pn.state.cache:
    pn.state.cache['num'] += 1
else:
    pn.state.cache['num'] = 0

md = pn.pane.Markdown(f"{pn.state.cache['num']}", css_classes=['counter'])

button = pn.widgets.Button(name='Click')

string = pn.pane.Str(object=0, css_classes=['string'])

def cb(event):
    string.object += 1

button.on_click(cb)

pn.Row(md, button, string).servable()
