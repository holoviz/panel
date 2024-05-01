import param
import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.esm import ReactiveESM
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


def test_esm_html_helper(page):
    class Example(ReactiveESM):

        text = param.String()

        _esm = """
        export function render({ data, html }) {
          return html`<h1 id="header">${data.text}</h1>`
        }
        """

    example = Example(text='Hello World!')

    serve_component(page, example)

    expect(page.locator('#header')).to_have_text('Hello World!')


def test_esm_update(page):
    class Example(ReactiveESM):

        text = param.String()

        _esm = """
        export function render({ data }) {
          const h1 = document.createElement('h1')
          h1.id = 'header'
          h1.textContent = data.text
          data.watch(() => {
            h1.textContent = data.text;
          }, 'text')
          return h1
        }
        """

    example = Example(text='Hello World!')

    serve_component(page, example)

    expect(page.locator('#header')).to_have_text('Hello World!')

    example.text = "Foo!"

    expect(page.locator('#header')).to_have_text('Foo!')


def test_esm_gather_input(page):
    class InputExample(ReactiveESM):

        text = param.String()

        _esm = """
        export function render({ data }) {
          const inp = document.createElement('input')
          inp.id = 'input'
          inp.value = data.text
          inp.addEventListener('change', (event) => {
            data.text = event.target.value;
          })
          return inp
        }
        """

    example = InputExample(text='Hello World!')

    serve_component(page, example)

    inp = page.locator('#input')

    inp.click()

    for _ in example.text:
        inp.press('Backspace')

    inp.press_sequentially('Foo!')
    inp.press('Enter')

    wait_until(lambda: example.text == 'Foo!', page)


def test_esm_button_event(page):
    class ButtonExample(ReactiveESM):

        clicks = param.Integer(default=0)

        _esm = """
        export function render({ data }) {
          const button = document.createElement('button')
          button.id = 'button'
          button.onclick = (event) => data.send_event('click', event)
          return button
        }
        """

        def on_click(self, event):
            self.clicks += 1

    button = ButtonExample()

    serve_component(page, button)

    page.locator('#button').click()

    wait_until(lambda: button.clicks, page)


def test_esm_react_update(page):
    class ReactExample(ReactiveESM):

        text = param.String()

        _esm = """
        function App(props) {
          const [text, setText ] = props.state.text
          return (
            <div>
              <h1 id="header">{text}</h1>
            </div>
          );
        }

        export function render({ state }) {
          return <App state={state}/>;
        }
        """

    example = ReactExample(text='Hello World!')

    serve_component(page, example)

    expect(page.locator('#header')).to_have_text('Hello World!')

    example.text = "Foo!"

    expect(page.locator('#header')).to_have_text('Foo!')


def test_esm_react_gather_input(page):
    class ReactInputExample(ReactiveESM):

        text = param.String()

        _esm = """
        function App(props) {
          const [text, setText ] = props.state.text
          return (
            <div>
              <input
                id="input"
                value={text}
                onChange={e => setText(e.target.value)}
              />
            </div>
          );
        }

        export function render({ state }) {
          return <App state={state}/>;
        }
        """

    example = ReactInputExample(text='Hello World!')

    serve_component(page, example)

    inp = page.locator('#input')

    inp.click()

    for _ in example.text:
        inp.press('Backspace')

    inp.press_sequentially('Foo!')

    wait_until(lambda: example.text == 'Foo!', page)
