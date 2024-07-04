import param

import panel as pn

from panel.custom import JSComponent

pn.extension()

class JSSlideshow(JSComponent):

    index = param.Integer(default=0)

    _esm = """
	export function render({ model }) {
      const img = document.createElement('img')
      img.addEventListener('click', () => { model.index += 1 })
      const update = () => {
        img.src = `https://picsum.photos/800/300?image=${model.index}`
      }
      model.watch(update, 'index')
      update()
      return img
    }
	"""


class PySlideshow(JSComponent):

    index = param.Integer(default=0)

    _esm = """
	export function render({ model }) {
      const img = document.createElement('img')
      img.addEventListener('click', (event) => model.send_event('click', event))
      const update = () => {
        img.src = `https://picsum.photos/800/300?image=${model.index}`
      }
      model.watch(update, 'index')
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
