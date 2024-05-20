import param

import panel as pn

from panel.custom import PreactComponent

pn.extension()

class JSSlideshow(PreactComponent):

    index = param.Integer(default=0)

    _esm = """
    export function render({ data }) {
      return html`<img id="slideshow" src="https://picsum.photos/800/300?image=${data.index}" onclick=${ (event) => { data.index = data.index+1 } }></img>`
    }
	"""


class PySlideshow(PreactComponent):

    index = param.Integer(default=0)

    _esm = """
    export function render({ data }) {
      return html`<img id="slideshow" src="https://picsum.photos/800/300?image=${data.index}" onclick=${(event) => data.send_event('click', event)}></img>`
    }
	"""

    def _handle_click(self, event):
        self.index += 1


pn.Row(
    JSSlideshow(),
    PySlideshow()
).servable()
