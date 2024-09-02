import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel import Card, Row
from panel.tests.util import serve_component, wait_until
from panel.widgets import FloatSlider, TextInput

pytestmark = pytest.mark.ui


@pytest.fixture
def card_components():
    # widgets with mock css classes for easy search for elements in the Card
    w1 = FloatSlider(name='Slider', css_classes=['class_w1'])
    w2 = TextInput(name='Text:', css_classes=['class_w2'])
    return w1, w2


def test_card_default(page, card_components):
    w1, w2 = card_components
    card = Card(w1, w2)
    serve_component(page, card)

    card_elements = page.locator('.card > div, .card > button')
    # the card is expanded as default and includes a header and its inner objects
    expect(card_elements).to_have_count(len(card) + 1)

    card_header = card_elements.nth(0)
    w1_object = card_elements.nth(1)
    w2_object = card_elements.nth(2)
    assert 'card-header' in card_header.get_attribute('class')
    assert 'class_w1' in w1_object.get_attribute('class')
    assert 'class_w2' in w2_object.get_attribute('class')

    # icon display in card button in expanded mode
    card_button = page.locator('.card-button')
    expect(card_button.locator('svg')).to_have_class("icon icon-tabler icons-tabler-outline icon-tabler-chevron-down")


def test_card_collapsed(page, card_components):
    w1, w2 = card_components
    card = Card(w1, w2)
    serve_component(page, card)

    card_elements = page.locator('.card > div, .card > button')
    card_button = page.locator('.card-button')

    # collapse the card
    card_button.wait_for()
    card_button.click()
    expect(card_button.locator('svg')).to_have_class("icon icon-tabler icons-tabler-outline icon-tabler-chevron-right")
    # only show the card header, other elements are hidden
    expect(card_elements).to_have_count(1)

    # expand the card again
    card_button.wait_for()
    card_button.click()
    expect(card_elements).to_have_count(len(card) + 1)
    expect(card_button.locator('svg')).to_have_class("icon icon-tabler icons-tabler-outline icon-tabler-chevron-down")


def test_card_not_collapsible(page, card_components):
    w1, w2 = card_components
    card = Card(w1, w2, collapsible=False)
    serve_component(page, card)

    # no card button to disable collapsing the card
    card_button = page.locator('.card-button')
    expect(card_button).to_have_count(0)
    # card header and other inner objects
    card_elements = page.locator('.card > div, .card > button')
    expect(card_elements).to_have_count(len(card) + 1)


def test_card_hide_header(page, card_components):
    w1, w2 = card_components
    card = Card(w1, w2, hide_header=True)
    serve_component(page, card)

    # no card header
    card_header = page.locator('.card-header')
    expect(card_header).to_have_count(0)
    # only inner card objects
    card_elements = page.locator('.card > div, .card > button')
    expect(card_elements).to_have_count(len(card))


def test_card_objects(page, card_components):
    w1, w2 = card_components
    card = Card(w1, w2)
    serve_component(page, card)

    card.objects = [w2]

    card_elements = page.locator('.card > div, .card > button')
    expect(card_elements).to_have_count(2)

    card_header = card_elements.nth(0)
    w2_object = card_elements.nth(1)
    expect(card_header).to_have_class('card-header')
    expect(w2_object).to_have_class('bk-panel-models-widgets-TextInput class_w2')

    w3 = TextInput(name='Text:', css_classes=['class_w3'])
    card.append(w3)

    expect(card_elements).to_have_count(3)
    expect(card_elements.nth(2)).to_have_class('bk-panel-models-widgets-TextInput class_w3')


def test_card_title(page, card_components):
    w1, w2 = card_components
    card_title = 'Card Title'
    card = Card(w1, w2, title=card_title)
    serve_component(page, card)

    expect(page.locator('.card-title').locator("div")).to_have_text(card_title)


def test_card_background(page, card_components):
    w1, w2 = card_components
    background = 'rgb(128, 128, 128)'
    card = Card(w1, w2, styles=dict(background=background))

    serve_component(page, card)

    card_widget = page.locator('.card')
    expect(card_widget).to_have_css('background-color', background)


def test_card_header_color_formatting(page):
    header_color = 'rgb(0, 0, 128)'
    active_header_background = 'rgb(0, 128, 0)'
    header_background = 'rgb(128, 0, 0)'
    card = Card(
        header_color=header_color,
        active_header_background=active_header_background,
        header_background=header_background,
    )
    serve_component(page, card)

    card_header = page.locator('.card-header')
    expect(card_header).to_have_css('color', header_color)

    # card is expanded by default
    expect(card_header).to_have_css('background-color', active_header_background)

    # collapse the card, header background color is set to header_background
    card_header.wait_for()
    card_header.click()
    expect(card_header).to_have_css('background-color', header_background)


def test_card_custom_css(page):
    # mock css classes to test the Card setting
    additional_css_class = 'css_class'
    additional_header_css_class = 'header_css_class'
    additional_button_css_class = 'button_css_class'

    # adding new css formatting classes to the default ones
    card = Card()
    card.css_classes.append(additional_css_class)
    card.header_css_classes.append(additional_header_css_class)
    card.button_css_classes.append(additional_button_css_class)

    serve_component(page, card)

    card_widget = page.locator(f'.card.{additional_css_class}')
    expect(card_widget).to_have_count(1)

    card_header = page.locator(f'.card-header.{additional_header_css_class}')
    expect(card_header).to_have_count(1)

    card_button = page.locator(f'.card-button.{additional_button_css_class}')
    expect(card_button).to_have_count(1)


def test_card_scrollable(page):
    card = Card(scroll=True)
    serve_component(page, card)

    expect(page.locator('.card')).to_have_class('bk-panel-models-layout-Card card scrollable-vertical')


def test_card_widget_not_collapsed(page, card_components):
    # Fixes https://github.com/holoviz/panel/issues/7045
    w1, w2 = card_components
    card = Card(w1, header=Row(w2))

    serve_component(page, card)

    text_input = page.locator('.bk-input[type="text"]')
    expect(text_input).to_have_count(1)

    text_input.click()

    text_input.press("F")
    text_input.press("Enter")

    wait_until(lambda: w2.value == 'F', page)
    assert not card.collapsed
