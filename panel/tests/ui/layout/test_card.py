import pytest

from panel import Card
from panel.tests.util import serve_panel_widget
from panel.widgets import FloatSlider, TextInput

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui


@pytest.fixture
def card_components():
    # widgets with mock css classes for easy search for elements in the Card
    w1 = FloatSlider(name='Slider', css_classes=['class_w1'])
    w2 = TextInput(name='Text:', css_classes=['class_w2'])
    return w1, w2


def test_card_default(page, port, card_components):
    w1, w2 = card_components
    card = Card(w1, w2)
    serve_panel_widget(page, port, card)

    card_elements = page.locator('.bk.card > .bk')
    # the card is expanded as default and includes a header and its inner objects
    expect(card_elements).to_have_count(len(card) + 1)
    # order of the elements
    card_header = card_elements.nth(0)
    w1_object = card_elements.nth(1)
    w2_object = card_elements.nth(2)
    assert 'card-header' in card_header.get_attribute('class')
    assert 'class_w1' in w1_object.get_attribute('class')
    assert 'class_w2' in w2_object.get_attribute('class')

    # icon display in card button in expanded mode
    card_button = page.locator('.bk.card-button')
    button_name = card_button.inner_text()
    assert button_name == "\u25bc"


def test_card_collapsed(page, port, card_components):
    w1, w2 = card_components
    card = Card(w1, w2)
    serve_panel_widget(page, port, card)

    card_elements = page.locator('.bk.card > .bk')
    card_button = page.locator('.bk.card-button')

    # collapse the card
    card_button.wait_for()
    card_button.click()
    assert card_button.inner_text() == "\u25ba"
    # only show the card header, other elements are hidden
    expect(card_elements).to_have_count(1)

    # expand the card again
    card_button.wait_for()
    card_button.click()
    expect(card_elements).to_have_count(len(card) + 1)
    assert card_button.inner_text() == "\u25bc"


def test_card_not_collapsible(page, port, card_components):
    w1, w2 = card_components
    card = Card(w1, w2, collapsible=False)
    serve_panel_widget(page, port, card)

    # no card button to disable collapsing the card
    card_button = page.locator('.bk.card-button')
    expect(card_button).to_have_count(0)
    # card header and other inner objects
    card_elements = page.locator('.bk.card > .bk')
    expect(card_elements).to_have_count(len(card) + 1)


def test_card_hide_header(page, port, card_components):
    w1, w2 = card_components
    card = Card(w1, w2, hide_header=True)
    serve_panel_widget(page, port, card)

    # no card header
    card_header = page.locator('.bk.card-header')
    expect(card_header).to_have_count(0)
    # only inner card objects
    card_elements = page.locator('.bk.card > .bk')
    expect(card_elements).to_have_count(len(card))


def test_card_objects(page, port, card_components):
    w1, w2 = card_components
    card = Card(w1, w2)
    serve_panel_widget(page, port, card)

    new_objects = [w2]
    # set new list of objects for the card
    card.objects = new_objects

    card_elements = page.locator('.bk.card > .bk')
    expect(card_elements).to_have_count(len(new_objects) + 1)

    card_header = card_elements.nth(0)
    w2_object = card_elements.nth(1)
    assert 'card-header' in card_header.get_attribute('class')
    assert 'class_w2' in w2_object.get_attribute('class')


def test_card_title(page, port, card_components):
    w1, w2 = card_components
    card_title = 'Card Title'
    card = Card(w1, w2, title=card_title)
    serve_panel_widget(page, port, card)

    assert page.locator('.bk.card-title').inner_text() == card_title


def test_card_background(page, port, card_components):
    w1, w2 = card_components
    background = 'rgb(128, 128, 128)'
    card = Card(w1, w2, background=background)

    serve_panel_widget(page, port, card)

    card_widget = page.locator('.bk.card')
    assert f'background-color: {background};' in card_widget.get_attribute('style')


def test_card_header_color_formatting(page, port):
    header_color = 'rgb(0, 0, 128)'
    active_header_background = 'rgb(0, 128, 0)'
    header_background = 'rgb(128, 0, 0)'
    card = Card(
        header_color=header_color,
        active_header_background=active_header_background,
        header_background=header_background,
    )
    serve_panel_widget(page, port, card)

    card_header = page.locator('.bk.card-header')
    assert f'color: {header_color};' in card_header.get_attribute('style')

    # card is expanded by default
    assert f'background-color: {active_header_background};' in card_header.get_attribute('style')

    # collapse the card, header background color is set to header_background
    card_header.wait_for()
    card_header.click()
    assert f'background-color: {header_background};' in card_header.get_attribute('style')


def test_card_custom_css(page, port):
    # mock css classes to test the Card setting
    additional_css_class = 'css_class'
    additional_header_css_class = 'header_css_class'
    additional_button_css_class = 'button_css_class'

    # adding new css formatting classes to the default ones
    card = Card()
    card.css_classes.append(additional_css_class)
    card.header_css_classes.append(additional_header_css_class)
    card.button_css_classes.append(additional_button_css_class)

    serve_panel_widget(page, port, card)

    card_widget = page.locator(f'.bk.card.{additional_css_class}')
    expect(card_widget).to_have_count(1)

    card_header = page.locator(f'.bk.card-header.{additional_header_css_class}')
    expect(card_header).to_have_count(1)

    card_button = page.locator(f'.bk.card-button.{additional_button_css_class}')
    expect(card_button).to_have_count(1)
