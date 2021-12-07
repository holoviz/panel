from bokeh.events import ButtonClick, MenuItemClick

from panel.widgets import Button, MenuButton, Toggle


def test_button(document, comm):
    button = Button(name='Button')

    widget = button.get_root(document, comm=comm)

    assert isinstance(widget, button._widget_type)
    assert widget.label == 'Button'

    button._process_event(None)
    assert button.clicks == 1


def test_button_event(document, comm):
    button = Button(name='Button')

    widget = button.get_root(document, comm=comm)

    events = []
    def callback(event):
        events.append(event.new)

    button.param.watch(callback, 'value')

    assert button.value == False
    button._process_event(ButtonClick(widget))
    assert events == [True]
    assert button.value == False


def test_menu_button(document, comm):
    menu_items = [('Option A', 'a'), ('Option B', 'b'), ('Option C', 'c'), None, ('Help', 'help')]
    menu_button = MenuButton(items=menu_items)

    widget = menu_button.get_root(document, comm=comm)

    events = []
    def callback(event):
        events.append(event.new)

    menu_button.param.watch(callback, 'clicked')

    menu_button._process_event(MenuItemClick(widget, 'b'))

    assert events == ['b']


def test_button_jscallback_clicks(document, comm):
    button = Button(name='Button')
    code = 'console.log("Clicked!")'
    button.jscallback(clicks=code)

    widget = button.get_root(document, comm=comm)
    assert len(widget.js_event_callbacks) == 1
    callbacks = widget.js_event_callbacks
    assert 'button_click' in callbacks
    assert len(callbacks['button_click']) == 1
    assert code in callbacks['button_click'][0].code


def test_toggle(document, comm):
    toggle = Toggle(name='Toggle', value=True)

    widget = toggle.get_root(document, comm=comm)

    assert isinstance(widget, toggle._widget_type)
    assert widget.active == True
    assert widget.label == 'Toggle'

    widget.active = False
    toggle._process_events({'active': widget.active})
    assert toggle.value == False

    toggle.value = True
    assert widget.active == True
