import param

import panel as pn

from panel.esm import JSComponent

pn.extension()

class JSSlideshow(JSComponent):

    index = param.Integer(default=0)

    _esm = """
	export function render({ data, html }) {
      return html`<img id="slideshow" src="https://picsum.photos/800/300?image=${data.index}" onclick=${ (event) => { data += 1} }></img>`
    }
	"""


class PySlideshow(JSComponent):

    index = param.Integer(default=0)

    _esm = """
	export function render({ data, html }) {
      return html`<img id="slideshow" src="https://picsum.photos/800/300?image=${data.index}" onclick=${(event) => data.send_event('click', event)}></img>`
    }
	"""

    def _handle_click(self, event):
        self.index += 1


pn.Row(
    JSSlideshow(),
    PySlideshow()
).servable()
