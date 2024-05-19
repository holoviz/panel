import param

import panel as pn

from panel.custom import ReactComponent

pn.extension()

class JSSlideshow(ReactComponent):

    index = param.Integer(default=0)

    _esm = """
    function App(props) {
      const [index, setIndex] = props.state.index
      const img = `https://picsum.photos/800/300?image=${index}`
      return (
        <>
          <img id="slideshow" src={img} onClick={ (event) => { setIndex(1) } }></img>
        </>
      )
    }

	export function render({ state }) {
      return <App state={state}></App>
    }
	"""


class PySlideshow(ReactComponent):

    index = param.Integer(default=0)

    _esm = """
    function App(props) {
      const [index, setIndex] = props.state.index
      const img = `https://picsum.photos/800/300?image=${index}`
      return (
        <>
          <img id="slideshow" src={img} onClick={ (event) => props.data.send_event('click', event) }></img>
        </>
      )
    }

	export function render({ data, state }) {
      return <App data={data} state={state}></App>
    }
	"""

    def _handle_click(self, event):
        self.index += 1


pn.Row(
    JSSlideshow(),
    PySlideshow()
).servable()
