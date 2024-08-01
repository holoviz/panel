import param

import panel as pn

from panel.custom import ReactComponent

pn.extension()

class JSSlideshow(ReactComponent):

    index = param.Integer(default=0)

    _esm = """
	export function render({ model }) {
      const [index, setIndex] = model.useState("index")
      const img = `https://picsum.photos/800/300?image=${index}`
      return <img id="slideshow" src={img} onClick={ (event) => { setIndex(index+1) } }></img>
    }
	"""


class PySlideshow(ReactComponent):

    index = param.Integer(default=0)

    _esm = """
	export function render({ model }) {
      const [index, setIndex] = model.useState("index")
      const img = `https://picsum.photos/800/300?image=${index}`
      return <img id="slideshow" src={img} onClick={ (event) => model.send_event('click', event) }></img>
    }
	"""

    def _handle_click(self, event):
        self.index += 1


pn.Row(
    JSSlideshow(),
    PySlideshow()
).servable()
