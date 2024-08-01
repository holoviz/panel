import pathlib

import param
import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.custom import (
    AnyWidgetComponent, Child, Children, JSComponent, ReactComponent,
)
from panel.layout import Row
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


class JSUpdate(JSComponent):

    text = param.String()

    _esm = """
    export function render({ model }) {
      const h1 = document.createElement('h1')
      h1.textContent = model.text
      model.on('text', () => {
        h1.textContent = model.text;
      })
      return h1
    }
    """

class ReactUpdate(ReactComponent):

    text = param.String()

    _esm = """
    export function render({ model }) {
      const [text, setText ] = model.useState("text")
      return <h1>{text}</h1>
    }
    """

class AnyWidgetUpdate(AnyWidgetComponent):

    text = param.String()

    _esm = """
    export function render({ model, el }) {
      const h1 = document.createElement('h1')
      h1.textContent = model.get("text")
      model.on("change:text", () => {
        h1.textContent = model.get("text");
      })
      el.append(h1)
    }
    """


@pytest.mark.parametrize('component', [JSUpdate, ReactUpdate, AnyWidgetUpdate])
def test_update(page, component):
    example = component(text='Hello World!')

    serve_component(page, example)

    expect(page.locator('h1')).to_have_text('Hello World!')

    example.text = "Foo!"

    expect(page.locator('h1')).to_have_text('Foo!')


class JSUnwatch(JSComponent):

    text = param.String()

    _esm = """
    export function render({ model, el }) {
      const h1 = document.createElement('h1')
      const h2 = document.createElement('h2')
      h1.textContent = model.text
      h2.textContent = model.text
      const cb = () => {
        h1.textContent = model.text;
      }
      const cb2 = () => {
        h2.textContent = model.text;
        model.off('text', cb2)
      }
      model.on('text', cb)
      model.on('text', cb2)
      el.append(h1, h2)
    }
    """

class AnyWidgetUnwatch(AnyWidgetComponent):

    text = param.String()

    _esm = """
    export function render({ model, el }) {
      const h1 = document.createElement('h1')
      const h2 = document.createElement('h2')
      h1.textContent = model.get("text")
      h2.textContent = model.get("text")
      const cb = () => {
        h1.textContent = model.get("text");
      }
      const cb2 = () => {
        h2.textContent = model.get("text");
        model.off("change:text", cb2)
      }
      model.on("change:text", cb)
      model.on("change:text", cb2)
      el.append(h1, h2)
    }
    """

@pytest.mark.parametrize('component', [JSUnwatch, AnyWidgetUnwatch])
def test_unwatch(page, component):
    example = component(text='Hello World!')

    serve_component(page, example)

    expect(page.locator('h1')).to_have_text('Hello World!')
    expect(page.locator('h1')).to_have_text('Hello World!')

    example.text = "Foo!"

    expect(page.locator('h1')).to_have_text('Foo!')
    expect(page.locator('h2')).to_have_text('Foo!')

    example.text = "Baz!"

    expect(page.locator('h1')).to_have_text('Baz!')
    expect(page.locator('h2')).to_have_text('Foo!')


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


class ReactInput(ReactComponent):

    text = param.String()

    _esm = """
    export function render({ model }) {
      const [text, setText ] = model.useState("text")
      return (
        <input
          id="input"
          value={text}
          onChange={e => setText(e.target.value)}
        />
      )
    }
    """


@pytest.mark.parametrize('component', [JSInput, ReactInput])
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


class ReactSendEvent(ReactComponent):

    clicks = param.Integer(default=0)

    _esm = """
    export function render({ model }) {
      return <button id="button" onClick={(event) => model.send_event('click', event)}/>
    }
    """

    def _handle_click(self, event):
        self.clicks += 1


@pytest.mark.parametrize('component', [JSSendEvent, ReactSendEvent])
def test_send_event(page, component):
    button = component()

    serve_component(page, button)

    page.locator('#button').click()

    wait_until(lambda: button.clicks, page)


class JSChild(JSComponent):

    child = Child()

    _esm = """
    export function render({ model }) {
      const button = document.createElement('button')
      button.appendChild(model.get_child('child'))
      return button
    }"""


class ReactChild(ReactComponent):

    child = Child()

    _esm = """
    export function render({ model }) {
      return <button>{model.get_child('child')}</button>
    }"""


@pytest.mark.parametrize('component', [JSChild, ReactChild])
def test_child(page, component):
    example = component(child='A Markdown pane!')

    serve_component(page, example)

    expect(page.locator('button')).to_have_text('A Markdown pane!')

    example.child = 'A different Markdown pane!'

    expect(page.locator('button')).to_have_text('A different Markdown pane!')


class JSChildren(JSComponent):

    children = Children()

    _esm = """
    export function render({ model }) {
      const div = document.createElement('div')
      div.id = "container"
      div.append(...model.get_child('children'))
      return div
    }"""


class ReactChildren(ReactComponent):

    children = Children()

    _esm = """
    export function render({ model }) {
      return <div id="container">{model.get_child("children")}</div>
    }"""


@pytest.mark.parametrize('component', [JSChildren, ReactChildren])
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
    (ReactChildren, REACT_CODE_BEFORE, REACT_CODE_AFTER),
])
def test_reload(page, js_file, component, before, after):
    js_file.file.write(before)
    js_file.file.flush()
    js_file.file.seek(0)

    class CustomReload(component):
        _esm = pathlib.Path(js_file.name)

    example = CustomReload()
    serve_component(page, example)

    expect(page.locator('h1')).to_have_text('foo')

    js_file.file.write(after)
    js_file.file.flush()
    js_file.file.seek(0)
    example._update_esm()

    expect(page.locator('h1')).to_have_text('bar')


def test_anywidget_custom_event(page):

    class SendEvent(AnyWidgetComponent):

        _esm = """
        export function render({model, el}) {
          const h1 = document.createElement('h1')
          model.on("msg:custom", (msg) => { h1.innerText = msg.text })
          el.append(h1)
        }
        """

    example = SendEvent()
    serve_component(page, example)

    expect(page.locator('h1')).to_have_count(1)

    example.send({"type": "foo", "text": "bar"})

    expect(page.locator('h1')).to_have_text("bar")


class JSLifecycleAfterRender(JSComponent):

    _esm = """
    export function render({ model }) {
      const h1 = document.createElement('h1')
      model.on('after_render', () => { h1.textContent = 'rendered' })
      return h1
    }"""


class ReactLifecycleAfterRender(ReactComponent):

    _esm = """
    import {useState} from "react"

    export function render({ model }) {
      const [text, setText] = useState("")
      model.on('after_render', () => { setText('rendered') })
      return <h1>{text}</h1>
    }"""


@pytest.mark.parametrize('component', [JSLifecycleAfterRender, ReactLifecycleAfterRender])
def test_after_render_lifecycle_hooks(page, component):
    example = component()

    serve_component(page, example)

    expect(page.locator('h1')).to_have_count(1)

    expect(page.locator('h1')).to_have_text("rendered")


class JSLifecycleAfterResize(JSComponent):

    _esm = """
    export function render({ model }) {
      const h1 = document.createElement('h1')
      h1.textContent = "0"
      let count = 0
      model.on('after_resize', () => { count += 1; h1.textContent = `${count}`; })
      return h1
    }"""

class ReactLifecycleAfterResize(ReactComponent):

    _esm = """
    import {useState} from "react"

    export function render({ model }) {
      const [count, setCount] = useState(0)
      model.on('after_resize', () => { setCount(count+1); })
      return <h1>{count}</h1>
    }"""


@pytest.mark.parametrize('component', [JSLifecycleAfterResize, ReactLifecycleAfterResize])
def test_after_resize_lifecycle_hooks(page, component):
    example = component(sizing_mode='stretch_width')

    serve_component(page, example)

    expect(page.locator('h1')).to_have_count(1)

    expect(page.locator('h1')).to_have_text("1")

    page.set_viewport_size({ "width": 50, "height": 300})

    expect(page.locator('h1')).to_have_text("2")


class JSLifecycleRemove(JSComponent):

    _esm = """
    export function render({ model }) {
      const h1 = document.createElement('h1')
      h1.textContent = 'Hello'
      model.on('remove', () => { console.warn('Removed') })
      return h1
    }"""

class ReactLifecycleRemove(ReactComponent):

    _esm = """
    import {useState} from "react"

    export function render({ model }) {
      const [count, setCount] = useState(0)
      model.on('remove', () => { console.warn('Removed') })
      return <h1>Hello</h1>
    }"""


@pytest.mark.parametrize('component', [JSLifecycleRemove, ReactLifecycleRemove])
def test_remove_lifecycle_hooks(page, component):
    example = Row(component(sizing_mode='stretch_width'))

    serve_component(page, example)

    expect(page.locator('h1')).to_have_count(1)

    expect(page.locator('h1')).to_have_text("Hello")

    with page.expect_console_message() as msg_info:
        example.clear()

    wait_until(lambda: msg_info.value.args[0].json_value() == "Removed", page)
