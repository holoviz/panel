import param

import panel as pn

from panel.esm import JSComponent

pn.extension()

class JSSlideshow(JSComponent):

    index = param.Integer(default=0)

    _esm = """
	export function render({ data, html }) {
      const img = document.createElement('img')
      img.addEventListener('click', () { data.index += 1 })
      data.watch(() => {
        img.src = `https://picsum.photos/800/300?image=${data.index}`
      }, 'index')
      return img
    }
	"""


class PySlideshow(JSComponent):

    index = param.Integer(default=0)

    _esm = """
	export function render({ data, html }) {
      const img = document.createElement('img')
      img.addEventListener('click', (event) => data.send_event('click', event))
      data.watch(() => {
        img.src = `https://picsum.photos/800/300?image=${data.index}`
      }, 'index')
      return img
    }
	"""

    def _handle_click(self, event):
        self.index += 1


Slideshow(width=500, height=200).servable()
