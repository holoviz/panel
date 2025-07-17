import os
import pathlib
import time

import param
import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.config import config
from panel.custom import (
    AnyWidgetComponent, Child, Children, JSComponent, ReactComponent,
)
from panel.io.compile import compile_components
from panel.layout import Row
from panel.layout.base import ListLike
from panel.pane import Markdown
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


@pytest.fixture(scope="module", autouse=True)
def set_expect_timeout():
    timeout = expect._timeout
    expect.set_options(timeout=30_000)
    try:
        yield
    finally:
        expect.set_options(timeout=timeout)


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

class AnyWidgetReactUpdate(AnyWidgetComponent):

    text = param.String()

    _importmap = {
        "imports": {
            "@anywidget/react": "https://esm.sh/@anywidget/react",
            "react": "https://esm.sh/react",
        }
    }

    _esm = """
    import * as React from "react"
    import { createRender, useModelState } from "@anywidget/react"

    function H1() {
      let [text] = useModelState("text")
      return <h1>{text}</h1>
    }

    const render = createRender(H1)

    export default { render }
    """

@pytest.mark.parametrize('component', [JSUpdate, ReactUpdate, AnyWidgetUpdate, AnyWidgetReactUpdate])
def test_update(page, component):
    example = component(text='Hello World!')

    serve_component(page, example)

    expect(page.locator('h1')).to_have_text('Hello World!')

    example.text = "Foo!"

    expect(page.locator('h1')).to_have_text('Foo!')


class JSEventUpdate(JSComponent):

    event = param.Event()

    _esm = """
    export function render({ model }) {
      const h1 = document.createElement('h1')
      h1.textContent = "0"
      model.on('event', () => {
        h1.textContent = (parseInt(h1.textContent) + 1).toString();
      })
      return h1
    }
    """

class ReactEventUpdate(ReactComponent):

    event = param.Event()

    _esm = """
    export function render({ model }) {
      const [event] = model.useState("event")
      const [count, setCount ] = React.useState(-1)
      React.useEffect(() => {
        setCount(count + 1)
      }, [event])
      return <h1>{count}</h1>
    }
    """

class AnyWidgetEventUpdate(AnyWidgetComponent):

    event = param.Event()

    _esm = """
    export function render({ model, el }) {
      const h1 = document.createElement('h1')
      h1.textContent = "0"
      model.on("change:event", () => {
        h1.textContent = (parseInt(h1.textContent) + 1).toString();
      })
      el.append(h1)
    }
    """


@pytest.mark.parametrize('component', [JSEventUpdate, ReactEventUpdate, AnyWidgetEventUpdate])
def test_event_update(page, component):
    example = component()

    serve_component(page, example)

    expect(page.locator('h1')).to_have_text('0')

    example.param.trigger('event')

    expect(page.locator('h1')).to_have_text('1')

    example.param.trigger('event')

    expect(page.locator('h1')).to_have_text('2')


class AnyWidgetInitialize(AnyWidgetComponent):

    count = param.Integer(default=0)

    _esm = """
    export function initialize({ model }) {
      model.set('count', 1)
      model.save_changes()
    }

    export function render({ model, el }) {
      const h1 = document.createElement('h1')
      h1.textContent = `${model.get('count')}`
      el.append(h1)
    }
    """

class JSInitialize(JSComponent):

    count = param.Integer(default=0)

    _esm = """
    export function initialize({ model }) {
      model.count = 1
    }

    export function render({ model }) {
      const h1 = document.createElement('h1')
      h1.textContent = `${model.count}`
      return h1
    }
    """

class ReactInitialize(ReactComponent):

    count = param.Integer(default=0)

    _esm = """
    export function initialize({ model }) {
      model.count = 1
    }

    export function render({ model }) {
      const [count] = model.useState('count')
      return <h1>{count}</h1>
    }
    """

@pytest.mark.parametrize('component', [AnyWidgetInitialize, JSInitialize, ReactInitialize])
def test_initialize(page, component):
    example = Row(component())

    serve_component(page, example)

    expect(page.locator('h1')).to_have_text('1')

    example[0] = component()

    expect(page.locator('h1')).to_have_text('1')


class AnyWidgetModuleCached(AnyWidgetComponent):

    count = param.Integer(default=0)

    _esm = """
    let count = 0

    export function initialize({ model }) {
      count += 1
      model.set('count', count)
      model.save_changes()
    }

    export function render({ model, el }) {
      const h1 = document.createElement('h1')
      h1.textContent = `${model.get('count')}`
      el.append(h1)
    }
    """

class JSModuleCached(JSComponent):

    count = param.Integer(default=0)

    _esm = """
    let count = 0

    export function initialize({ model }) {
      count += 1
      model.count = count
    }

    export function render({ model }) {
      const h1 = document.createElement('h1')
      h1.textContent = `${model.count}`
      return h1
    }
    """

class ReactModuleCached(ReactComponent):

    count = param.Integer(default=0)

    _esm = """
    let count = 0

    export function initialize({ model }) {
      count += 1
      model.count = count
    }

    export function render({ model }) {
      const [count] = model.useState('count')
      return <h1>{count}</h1>
    }
    """

@pytest.mark.parametrize('component', [AnyWidgetModuleCached, JSModuleCached, ReactModuleCached])
def test_module_cached(page, component):
    example = Row(component())

    serve_component(page, example)

    expect(page.locator('h1')).to_have_text('1')

    example[0] = component()

    expect(page.locator('h1')).to_have_text('2')


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


class Nested(param.Parameterized):

    text = param.String()


class JSParent(JSComponent):

    child = param.ClassSelector(class_=Nested)

    _esm = """
    export function render({ model, el }) {
      const h1 = document.createElement('h1')
      h1.textContent = model.child.text
      const cb = () => {
        h1.textContent = model.child.text
      }
      model.on("change:child.text", cb)
      el.append(h1)
    }
    """


class ReactParent(ReactComponent):

    child = param.ClassSelector(class_=Nested)

    _esm = """
    export function render({ model, el }) {
      const [text] = model.useState("child.text")
      return <h1>{text}</h1>
    }
    """


class AnyWidgetParent(AnyWidgetComponent):

    child = param.ClassSelector(class_=Nested)

    _esm = """
    export function render({ model, el }) {
      const h1 = document.createElement('h1')
      h1.textContent = model.get("child.text")
      const cb = () => {
        h1.textContent = model.get("child.text")
      }
      model.on("change:child.text", cb)
      el.append(h1)
    }
    """


@pytest.mark.parametrize('component', [JSParent, ReactParent, AnyWidgetParent])
def test_nested_update(page, component):
    example = component(child=Nested(text='Hello World!'))

    serve_component(page, example)

    expect(page.locator('h1')).to_have_text('Hello World!')

    example.child.text = "Foo!"

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


class AnyWidgetInput(AnyWidgetComponent):

    text = param.String()

    _esm = """
    export function render({ model, el }) {
      const inp = document.createElement('input')
      inp.id = 'input'
      inp.value = model.get("text")
      inp.addEventListener('change', (event) => {
        model.set("text", event.target.value)
        model.save_changes()
      })
      el.append(inp)
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

@pytest.mark.parametrize('component', [JSInput, ReactInput, AnyWidgetInput])
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


class JSNestedInput(JSComponent):

    child = param.ClassSelector(class_=Nested)

    _esm = """
    export function render({ model }) {
      const inp = document.createElement('input')
      inp.id = 'input'
      inp.value = model.child.text
      inp.addEventListener('change', (event) => {
        model.child.text = event.target.value;
      })
      return inp
    }
    """

class AnyWidgetNestedInput(AnyWidgetComponent):

    child = param.ClassSelector(class_=Nested)

    _esm = """
    export function render({ model, el }) {
      const inp = document.createElement('input')
      inp.id = 'input'
      inp.value = model.get("child.text")
      inp.addEventListener('change', (event) => {
        model.set("child.text", event.target.value)
        model.save_changes()
      })
      el.append(inp)
    }
    """

class ReactNestedInput(ReactComponent):

    child = param.ClassSelector(class_=Nested)

    _esm = """
    export function render({ model }) {
      const [text, setText ] = model.useState("child.text")
      return (
        <input
          id="input"
          value={text}
          onChange={e => setText(e.target.value)}
        />
      )
    }
    """

@pytest.mark.parametrize('component', [JSNestedInput, ReactNestedInput, AnyWidgetNestedInput])
def test_gather_nested_input(page, component):
    example = component(child=Nested(text='Hello World!'))

    serve_component(page, example)

    inp = page.locator('#input')

    inp.click()
    for _ in example.child.text:
        inp.press('Backspace')
    inp.press_sequentially('Foo!')
    inp.press('Enter')

    wait_until(lambda: example.child.text == 'Foo!', page)


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


class JSSendMsg(JSComponent):

    clicks = param.Integer(default=0)

    msg = param.String()

    _esm = """
    export function render({ model }) {
      const button = document.createElement('button')
      button.id = 'button'
      button.onclick = (event) => model.send_msg('click')
      return button
    }
    """

    def _handle_msg(self, msg):
        self.msg = msg
        self.clicks += 1


class ReactSendMsg(ReactComponent):

    clicks = param.Integer(default=0)

    msg = param.String()

    _esm = """
    export function render({ model }) {
      return <button id="button" onClick={(event) => model.send_msg('click')}/>
    }
    """

    def _handle_msg(self, msg):
        self.msg = msg
        self.clicks += 1


@pytest.mark.parametrize('component', [JSSendMsg, ReactSendMsg])
def test_send_msg(page, component):
    button = component()

    serve_component(page, button)

    page.locator('#button').click()

    wait_until(lambda: button.clicks, page)
    assert button.msg == 'click'


class JSChild(JSComponent):

    child = Child()

    render_count = param.Integer(default=0)

    _esm = """
    export function render({ model }) {
      const button = document.createElement('button')
      button.appendChild(model.get_child('child'))
      model.render_count += 1
      return button
    }"""

class ReactChild(ReactComponent):

    child = Child()

    render_count = param.Integer(default=0)

    _esm = """
    export function render({ model }) {
      model.render_count += 1
      return <button>{model.get_child('child')}</button>
    }"""

@pytest.mark.parametrize('component', [JSChild, ReactChild])
def test_child(page, component):
    example = component(child='A Markdown pane!')

    serve_component(page, example)
    button = page.locator('button')
    expect(button).to_be_attached()

    expect(button).to_have_text('A Markdown pane!')

    example.child = 'A different Markdown pane!'

    expect(button).to_have_text('A different Markdown pane!')

    wait_until(lambda: example.render_count == (2 if component is JSChild else 1), page)

def test_react_child_no_shadow_dom(page):
    example = ReactChild(
        child=ReactChild(
            child='A Markdown pane!', css_classes=['child'], use_shadow_dom=False
        ),
        css_classes=['parent']
    )

    serve_component(page, example)
    parent = page.locator('button').nth(0)
    expect(parent).to_be_attached()
    child = page.locator('.child > button')
    expect(child).to_be_attached()

    expect(child).to_have_text('A Markdown pane!')

    example.child.child = 'A different Markdown pane!'

    expect(child).to_have_text('A different Markdown pane!')

    wait_until(lambda: example.render_count == 1, page)


class JSChildren(ListLike, JSComponent):

    objects = Children()

    render_count = param.Integer(default=0)

    _esm = """
    export function render({ model }) {
      const div = document.createElement('div')
      div.id = "container"
      div.append(...model.get_child('objects'))
      model.render_count += 1
      return div
    }"""

class JSChildrenNoReturn(JSChildren):

    _esm = """
    export function render({ model, view }) {
      const div = document.createElement('div')
      div.id = "container"
      div.append(...model.get_child('objects'))
      view.container.replaceChildren(div)
      model.render_count += 1
    }"""

class ReactChildren(ListLike, ReactComponent):

    objects = Children()

    render_count = param.Integer(default=0)

    _esm = """
    export function render({ model }) {
      model.render_count += 1
      return <div id="container">{model.get_child("objects")}</div>
    }"""

@pytest.mark.parametrize('component', [JSChildren, JSChildrenNoReturn, ReactChildren])
def test_children(page, component):
    example = component(objects=['A Markdown pane!'])

    serve_component(page, example)
    container = page.locator('#container')
    expect(container).to_be_attached()

    expect(container).to_have_text('A Markdown pane!')

    example.objects = ['A different Markdown pane!']

    expect(container).to_have_text('A different Markdown pane!')

    example.objects = ['<div class="foo">1</div>', '<div class="foo">2</div>']

    expect(page.locator('.foo').nth(0)).to_have_text('1')
    expect(page.locator('.foo').nth(1)).to_have_text('2')

    page.wait_for_timeout(400)

    assert example.render_count == (3 if issubclass(component, (JSChildren, ReactChildren)) else 2)

@pytest.mark.parametrize('component', [JSChildren, JSChildrenNoReturn, ReactChildren])
def test_children_add_and_remove_without_error(page, component):
    example = component(objects=['A Markdown pane!'])

    msgs, _ = serve_component(page, example)
    container = page.locator('#container')
    expect(container).to_be_attached()

    expect(container).to_have_text('A Markdown pane!')

    example.append('A different Markdown pane!')
    example.pop(-1)

    expect(container).to_have_text('A Markdown pane!')

    expect(page.locator('.markdown')).to_have_count(1)

    page.wait_for_timeout(500)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []

@pytest.mark.parametrize('component', [JSChildren, JSChildrenNoReturn, ReactChildren])
def test_children_append_without_rerender(page, component):
    child = JSChild(child=Markdown(
        'A Markdown pane!', css_classes=['first']
    ))
    example = component(objects=[child])

    serve_component(page, example)

    expect(page.locator('.first')).to_have_text('A Markdown pane!')

    wait_until(lambda: child.render_count == 1, page)

    example.objects = example.objects+[Markdown(
        'A different Markdown pane!', css_classes=['second']
    )]

    expect(page.locator('.second')).to_have_text('A different Markdown pane!')

    page.wait_for_timeout(400)

    assert child.render_count == 1
    assert example.render_count == 2


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

@pytest.mark.parametrize(['component', 'before', 'after'], [
    (JSComponent, JS_CODE_BEFORE, JS_CODE_AFTER),
    (ReactChildren, REACT_CODE_BEFORE, REACT_CODE_AFTER),
], ids=["JSComponent", "ReactChildren"])
def test_reload(page, js_file, component, before, after):
    js_file.file.write(before)
    js_file.file.flush()
    os.fsync(js_file.file.fileno())
    js_file.file.seek(0)

    class CustomReload(component):
        _esm = pathlib.Path(js_file.name)

    example = CustomReload()

    with config.set(autoreload=True):
        serve_component(page, example)
        h1 = page.locator("h1")
        expect(h1).to_be_attached()

        expect(h1).to_have_text('foo')

        js_file.file.write(after)
        js_file.file.flush()
        os.fsync(js_file.file.fileno())
        js_file.file.seek(0)
        while not pathlib.Path(js_file.name).exists():
            time.sleep(0.1)
        example._update_esm()

        expect(h1).to_have_text('bar')


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

def test_react_child_no_shadow_dom_after_render_lifecycle_hook(page):
    example = ReactChild(
        child=ReactLifecycleAfterRender(use_shadow_dom=False),
    )

    serve_component(page, example)

    expect(page.locator('h1')).to_have_count(1)

    expect(page.locator('h1')).to_have_text("rendered")


class JSLifecycleAfterLayout(JSComponent):

    _esm = """
    export function render({ model }) {
      const h1 = document.createElement('h1')
      model.on('after_layout', () => { h1.textContent = 'layouted' })
      return h1
    }"""

class ReactLifecycleAfterLayout(ReactComponent):

    _esm = """
    import {useState} from "react"

    export function render({ model }) {
      const [text, setText] = useState("")
      model.on('after_layout', () => { setText('layouted') })
      return <h1>{text}</h1>
    }"""

@pytest.mark.parametrize('component', [JSLifecycleAfterLayout, ReactLifecycleAfterLayout])
def test_after_layout_lifecycle_hooks(page, component):
    example = component()

    serve_component(page, example)

    expect(page.locator('h1')).to_have_count(1)

    expect(page.locator('h1')).to_have_text("layouted")

def test_react_child_no_shadow_dom_after_layout_lifecycle_hook(page):
    example = ReactChild(
        child=ReactLifecycleAfterLayout(use_shadow_dom=False),
    )

    serve_component(page, example)

    expect(page.locator('h1')).to_have_count(1)

    expect(page.locator('h1')).to_have_text("layouted")


class JSLifecycleAfterResize(JSComponent):

    _esm = """
    export function render({ model }) {
      const h1 = document.createElement('h1')
      h1.textContent = "0"
      let count = 0
      model.on('resize', () => { count += 1; h1.textContent = `${count}`; })
      return h1
    }"""

class ReactLifecycleAfterResize(ReactComponent):

    _esm = """
    import {useState} from "react"

    export function render({ model }) {
      const [count, setCount] = useState(0)
      model.on('resize', () => { setCount(count+1); })
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

def test_react_child_no_shadow_dom_remove_lifecycle_hook(page):
    example = ReactChild(
        child=ReactLifecycleRemove(use_shadow_dom=False),
    )

    serve_component(page, example)

    expect(page.locator('h1')).to_have_count(1)

    expect(page.locator('h1')).to_have_text("Hello")

    with page.expect_console_message() as msg_info:
        example.child = "New"

    wait_until(lambda: msg_info.value.args[0].json_value() == "Removed", page)


class JSDefaultExport(JSComponent):

    _esm = """
    function render({ model }) {
      const h1 = document.createElement('h1')
      h1.textContent = 'Hello'
      return h1
    }

    export default {render}
    """

class AnyWidgetDefaultExport(AnyWidgetComponent):

    _esm = """
    function render({ model, el }) {
      const h1 = document.createElement('h1')
      h1.textContent = 'Hello'
      el.append(h1)
    }

    export default {render}
    """

class ReactDefaultExport(ReactComponent):

    _esm = """
    function render({ model }) {
      return <h1>Hello</h1>
    }

    export default { render }
    """

@pytest.mark.parametrize('component', [AnyWidgetDefaultExport, JSDefaultExport, ReactDefaultExport])
def test_esm_component_default_export(page, component):
    example = Row(component(sizing_mode='stretch_width'))

    serve_component(page, example)

    expect(page.locator('h1')).to_have_count(1)

    expect(page.locator('h1')).to_have_text("Hello")


class JSDefaultFunctionExport(JSComponent):

    _esm = """
    export default () => {
      function render({ model }) {
        const h1 = document.createElement('h1')
        h1.textContent = 'Hello'
        return h1
      }

      return {render}
    }
    """

class AnyWidgetDefaultFunctionExport(AnyWidgetComponent):

    _esm = """
    export default () => {
      function render({ model, el }) {
        const h1 = document.createElement('h1')
        h1.textContent = 'Hello'
        el.append(h1)
      }

      return {render}
    }
    """

class ReactDefaultFunctionExport(ReactComponent):

    _esm = """
    export default () => {
      function render({ model }) {
        return <h1>Hello</h1>
      }
      return {render}
    }
    """

@pytest.mark.parametrize('component', [AnyWidgetDefaultFunctionExport, JSDefaultExport, ReactDefaultExport])
def test_esm_component_default_function_export(page, component):
    example = Row(component(sizing_mode='stretch_width'))

    serve_component(page, example)

    expect(page.locator('h1')).to_have_count(1)

    expect(page.locator('h1')).to_have_text("Hello")


@pytest.mark.parametrize('component', [AnyWidgetInitialize, JSInitialize, ReactInitialize])
def test_esm_compile_simple(page, component):
    outfile = pathlib.Path(__file__).parent / f'{component.__name__}.bundle.js'
    ret = compile_components([component], outfile=outfile)
    if ret or not outfile.is_file():
        raise RuntimeError('Could not compile ESM component')

    assert component._bundle_path == outfile

    example = Row(component())

    serve_component(page, example)

    expect(page.locator('h1')).to_have_text('1')

    example[0] = component()

    expect(page.locator('h1')).to_have_text('1')


class JSBase(JSComponent):

    _bundle = 'js.bundle.js'

    _esm = """
    export function render({model}) {
      const h1 = document.createElement('h1')
      h1.id = model.name
      h1.textContent = "Rendered"
      return h1
    }
    """

class JS1(JSBase):
    pass

class JS2(JSBase):
    pass


class AnyWidgetBase(AnyWidgetComponent):

    _bundle = 'anywidget.bundle.js'

    _esm = """
    export function render({model, el}) {
      const h1 = document.createElement('h1')
      h1.id = model.get("name")
      h1.textContent = "Rendered"
      el.append(h1)
    }
    """

class AnyWidget1(AnyWidgetBase):
    pass

class AnyWidget2(AnyWidgetBase):
    pass


class ReactBase(ReactComponent):

    _bundle = 'react.bundle.js'

    _esm = """
    export function render({model, el}) {
      return <h1 id={model.name}>Rendered</h1>
    }
    """

class React1(ReactBase):
    pass

class React2(ReactBase):
    pass

@pytest.mark.parametrize('components', [[JS1, JS2], [AnyWidget1, AnyWidget2], [React1, React2]])
def test_esm_compile_shared(page, components):
    component1, component2 = components
    outfile = pathlib.Path(__file__).parent / component1._bundle
    ret = compile_components([component1, component2], outfile=outfile)
    if ret or not outfile.is_file():
        raise RuntimeError('Could not compile ESM component')

    assert component1._bundle_path == outfile
    assert component2._bundle_path == outfile

    example = Row(component1(), component2())

    serve_component(page, example)

    expect(page.locator(f'#{example[0].name}')).to_have_text('Rendered')
    expect(page.locator(f'#{example[1].name}')).to_have_text('Rendered')
