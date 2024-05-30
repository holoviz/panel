import pathlib
import tempfile

import param
import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.custom import (
    Child, Children, JSComponent, PreactComponent, ReactComponent,
)
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


class PreactUpdate(PreactComponent):

    text = param.String()

    _esm = """
    export function render({ model }) {
      return html`<h1>${model.text}</h1>`
    }
    """

class JSUpdate(JSComponent):

    text = param.String()

    _esm = """
    export function render({ model }) {
      const h1 = document.createElement('h1')
      h1.textContent = model.text
      model.watch(() => {
        h1.textContent = model.text;
      }, 'text')
      return h1
    }
    """

class ReactUpdate(ReactComponent):

    text = param.String()

    _esm = """
    export function render({ state }) {
      const [text, setText ] = state.text
      return (
        <div>
          <h1>{text}</h1>
        </div>
      );
    }
    """

@pytest.mark.parametrize('component', [JSUpdate, PreactUpdate, ReactUpdate])
def test_update(page, component):
    example = component(text='Hello World!')

    serve_component(page, example)

    expect(page.locator('h1')).to_have_text('Hello World!')

    example.text = "Foo!"

    expect(page.locator('h1')).to_have_text('Foo!')


class JSInput(JSComponent):

    text = param.String()

    _esm = """
    export function render({ model }) {
      const inp = document.createElement('input')
      inp.id = 'input'
      inp.value = model.text
      inp.addEventListener('change', (event) => {
        model.text = event.target.value;
      })
      return inp
    }
    """


class PreactInput(PreactComponent):

    text = param.String()

    _esm = """
    export function render({ model }) {
      return html`
        <input
          id="input"
          value=${model.text}
          onChange=${e => { model.text = e.target.value }}
        />`
    }
    """

class ReactInput(ReactComponent):

    text = param.String()

    _esm = """
    export function render({ state }) {
      const [text, setText ] = state.text
      return (
        <div>
          <input
            id="input"
            value={text}
            onChange={e => setText(e.target.value)}
          />
        </div>
      )
    }
    """


@pytest.mark.parametrize('component', [JSInput, PreactInput, ReactInput])
def test_gather_input(page, component):
    example = component(text='Hello World!')

    serve_component(page, example)

    inp = page.locator('#input')

    inp.click()
    for _ in example.text:
        inp.press('Backspace')
    inp.press_sequentially('Foo!')
    inp.press('Enter')

    wait_until(lambda: example.text == 'Foo!', page)


class JSSendEvent(JSComponent):

    clicks = param.Integer(default=0)

    _esm = """
    export function render({ model }) {
      const button = document.createElement('button')
      button.id = 'button'
      button.onclick = (event) => model.send_event('click', event)
      return button
    }
    """

    def _handle_click(self, event):
        self.clicks += 1


class PreactSendEvent(PreactComponent):

    clicks = param.Integer(default=0)

    _esm = """
    export function render({ model }) {
      return html`<button id="button" onClick=${(event) => model.send_event('click', event)}/>`
    }
    """

    def _handle_click(self, event):
        self.clicks += 1


class ReactSendEvent(ReactComponent):

    clicks = param.Integer(default=0)

    _esm = """
    export function render({ model }) {
      return <button id="button" onClick={(event) => model.send_event('click', event)}/>
    }
    """

    def _handle_click(self, event):
        self.clicks += 1


@pytest.mark.parametrize('component', [JSSendEvent, PreactSendEvent, ReactSendEvent])
def test_send_event(page, component):
    button = component()

    serve_component(page, button)

    page.locator('#button').click()

    wait_until(lambda: button.clicks, page)


class JSChild(JSComponent):

    child = Child()

    _esm = """
    export function render({ children }) {
      const button = document.createElement('button')
      button.appendChild(children.child)
      return button
    }"""


class PreactChild(PreactComponent):

    child = Child()

    _esm = """
    export function render({ children }) {
      return html`<button>${children.child}</button>`
    }"""


class ReactChild(ReactComponent):

    child = Child()

    _esm = """
    export function render({ children }) {
      return <button>{children.child}</button>
    }"""


@pytest.mark.parametrize('component', [JSChild, PreactChild, ReactChild])
def test_child(page, component):
    example = component(child='A Markdown pane!')

    serve_component(page, example)

    expect(page.locator('button')).to_have_text('A Markdown pane!')

    example.child = 'A different Markdown pane!'

    expect(page.locator('button')).to_have_text('A different Markdown pane!')


class JSChildren(JSComponent):

    children = Children()

    _esm = """
    export function render({ children }) {
      const div = document.createElement('div')
      div.id = "container"
      for (const child of children.children) {
        div.appendChild(child)
      }
      return div
    }"""


class PreactChildren(PreactComponent):

    children = Children()

    _esm = """
    export function render({ children }) {
      return html`<div id="container">${children.children}</div>`
    }"""


class ReactChildren(ReactComponent):

    children = Children()

    _esm = """
    export function render({ children }) {
      return <div id="container">{children.children}</div>
    }"""


@pytest.mark.parametrize('component', [JSChildren, PreactChildren, ReactChildren])
def test_children(page, component):
    example = component(children=['A Markdown pane!'])

    serve_component(page, example)

    expect(page.locator('#container')).to_have_text('A Markdown pane!')

    example.children = ['A different Markdown pane!']

    expect(page.locator('#container')).to_have_text('A different Markdown pane!')

    example.children = ['<div class="foo">1</div>', '<div class="foo">2</div>']

    expect(page.locator('.foo').nth(0)).to_have_text('1')
    expect(page.locator('.foo').nth(1)).to_have_text('2')

JS_CODE_BEFORE = """
export function render() {
  const h1 = document.createElement('h1')
  h1.innerText = "foo"
  return h1
}"""

JS_CODE_AFTER = """
export function render() {
  const h1 = document.createElement('h1')
  h1.innerText = "bar"
  return h1
}"""

PREACT_CODE_BEFORE = """
export function render() {
  return html`<h1>foo</h1>`
}"""

PREACT_CODE_AFTER = """
export function render() {
  return html`<h1>bar</h1>`
}"""

REACT_CODE_BEFORE = """
export function render() {
  return <h1>foo</h1>
}"""

REACT_CODE_AFTER = """
export function render() {
  return <h1>bar</h1>
}"""

@pytest.mark.parametrize('component,before,after', [
    (JSComponent, JS_CODE_BEFORE, JS_CODE_AFTER),
    (PreactComponent, PREACT_CODE_BEFORE, PREACT_CODE_AFTER),
    (ReactChildren, REACT_CODE_BEFORE, REACT_CODE_AFTER),
])
def test_reload(page, component, before, after):
    with tempfile.NamedTemporaryFile(suffix='.js', mode='w', encoding='utf-8') as tmp:

        tmp.file.write(before)
        tmp.file.flush()
        tmp.file.seek(0)

        class CustomReload(component):
            _esm = pathlib.Path(tmp.name)

        example = CustomReload()
        serve_component(page, example)

        expect(page.locator('h1')).to_have_text('foo')

        tmp.file.write(after)
        tmp.file.flush()
        tmp.file.seek(0)
        example._update_esm()

        expect(page.locator('h1')).to_have_text('bar')
