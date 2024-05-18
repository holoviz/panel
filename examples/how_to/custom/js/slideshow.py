import param

import panel as pn

from panel.esm import JSComponent

pn.extension()

class JSSlideshow(JSComponent):

    index = param.Integer(default=0)

    _esm = """
	export function render({ data }) {
      const img = document.createElement('img')
      img.addEventListener('click', () => { data.index += 1 })
      const update = () => {
        img.src = `https://picsum.photos/800/300?image=${data.index}`
      }
      data.watch(update, 'index')
      update()
      return img
    }
	"""


class PySlideshow(JSComponent):

    index = param.Integer(default=0)

    _esm = """
	export function render({ data }) {
      const img = document.createElement('img')
      img.addEventListener('click', (event) => data.send_event('click', event))
      const update = () => {
        img.src = `https://picsum.photos/800/300?image=${data.index}`
      }
      data.watch(update, 'index')
      update()
      return img
    }
	"""

    def _handle_click(self, event):
        self.index += 1


pn.Row(
    JSSlideshow(),
    PySlideshow()
).servable()
