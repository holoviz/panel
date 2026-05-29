from bokeh.events import ButtonClick, MenuItemClick

from panel.widgets import Button, MenuButton, Toggle
from panel.widgets.icon import ButtonIcon


def test_button(document, comm):
    button = Button(label='Button')

    widget = button.get_root(document, comm=comm)

    assert isinstance(widget, button._widget_type)
    assert widget.label == 'Button'

    button._process_event(None)
    assert button.clicks == 1


def test_button_event(document, comm):
    button = Button(label='Button')

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


def test_button_on_click_kwarg(document, comm):
    events = []
    button = Button(label='Button', on_click=lambda e: events.append(e))
    button.get_root(document, comm=comm)
    button._process_event(None)
    assert len(events) == 1


def test_menu_button_on_click_kwarg(document, comm):
    events = []
    menu_button = MenuButton(
        items=[('Option A', 'a')],
        on_click=lambda e: events.append(e)
    )
    widget = menu_button.get_root(document, comm=comm)
    menu_button._process_event(MenuItemClick(widget, 'a'))
    assert len(events) == 1


def test_button_icon_on_click_kwarg(document, comm):
    events = []
    button_icon = ButtonIcon(icon='heart', on_click=lambda e: events.append(e))
    button_icon.get_root(document, comm=comm)
    button_icon._process_event(None)
    assert len(events) == 1


def test_button_jscallback_clicks(document, comm):
    button = Button(label='Button')
    code = 'console.log("Clicked!")'
    button.jscallback(clicks=code)

    widget = button.get_root(document, comm=comm)
    assert len(widget.js_event_callbacks) == 1
    callbacks = widget.js_event_callbacks
    assert 'button_click' in callbacks
    assert len(callbacks['button_click']) == 1
    assert code in callbacks['button_click'][0].code


def test_toggle(document, comm):
    toggle = Toggle(label='Toggle', value=True)

    widget = toggle.get_root(document, comm=comm)

    assert isinstance(widget, toggle._widget_type)
    assert widget.active == True
    assert widget.label == 'Toggle'

    widget.active = False
    toggle._process_events({'active': widget.active})
    assert toggle.value == False

    toggle.value = True
    assert widget.active == True


def test_button_color_alias_synced():
    button = Button(label="x", color="primary")
    assert button.button_type == "primary"
    assert button.color == "primary"
    button.button_type = "danger"
    assert button.color == "danger"
    button.color = "success"
    assert button.button_type == "success"


def test_button_variant_alias_synced():
    button = Button(label="x", variant="outline")
    assert button.button_style == "outline"
    assert button.variant == "outline"
    button.button_style = "solid"
    assert button.variant == "solid"
    button.variant = "outline"
    assert button.button_style == "outline"


def test_button_color_renders_to_bokeh_model(document, comm):
    button = Button(label="x", color="primary")
    widget = button.get_root(document, comm=comm)
    assert widget.button_type == "primary"
    button.color = "danger"
    assert widget.button_type == "danger"


def test_button_variant_renders_to_css_class(document, comm):
    button = Button(label="x", variant="outline")
    widget = button.get_root(document, comm=comm)
    assert "outline" in widget.css_classes
    button.variant = "solid"
    assert "solid" in widget.css_classes


def test_toggle_color_renders_to_bokeh_model(document, comm):
    toggle = Toggle(label="x", color="primary")
    widget = toggle.get_root(document, comm=comm)
    assert widget.button_type == "primary"
    toggle.color = "danger"
    assert widget.button_type == "danger"


def test_toggle_variant_renders_to_css_class(document, comm):
    toggle = Toggle(label="x", variant="outline")
    widget = toggle.get_root(document, comm=comm)
    assert "outline" in widget.css_classes
    toggle.variant = "solid"
    assert "solid" in widget.css_classes


def test_menu_button_color_renders_to_bokeh_model(document, comm):
    menu_button = MenuButton(label="x", items=[("A", "a")], color="primary")
    widget = menu_button.get_root(document, comm=comm)
    assert widget.button_type == "primary"
    menu_button.color = "danger"
    assert widget.button_type == "danger"


def test_menu_variant_renders_to_css_class(document, comm):
    menu_button = MenuButton(label="x", items=[("A", "a")], variant="outline")
    widget = menu_button.get_root(document, comm=comm)
    assert "outline" in widget.css_classes
    menu_button.variant = "solid"
    assert "solid" in widget.css_classes
