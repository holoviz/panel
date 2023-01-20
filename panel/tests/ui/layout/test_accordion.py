import pytest

from bokeh.models import Div

from panel import Accordion
from panel.tests.util import serve_panel_widget

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui


@pytest.fixture
def accordion_components():
    # divs with mock css classes for easy search for elements in the Accordion
    d0 = Div(name='Div 0', text='Text 0')
    d1 = Div(name='Div 1', text='Text 1')
    return d0, d1


def is_collapsed(card_object, card_content):
    expect(card_object).to_contain_text("\u25ba")
    expect(card_object).not_to_contain_text(card_content)
    return True


def is_expanded(card_object, card_content):
    expect(card_object).to_contain_text("\u25bc")
    expect(card_object).to_contain_text(card_content)
    return True


def test_accordion_default(page, port, accordion_components):
    d0, d1 = accordion_components
    accordion = Accordion(d0, d1)
    serve_panel_widget(page, port, accordion)

    accordion_elements = page.locator('.accordion')
    # there are 2 card in this accordion
    expect(accordion_elements).to_have_count(len(accordion_components))

    # order of the elements
    d0_object = accordion_elements.nth(0)
    d1_object = accordion_elements.nth(1)
    d0_object.wait_for()
    d1_object.wait_for()

    # cards name
    expect(d0_object).to_contain_text(d0.name)
    expect(d1_object).to_contain_text(d1.name)

    # cards are collapsed and their content is hidden by default
    assert is_collapsed(card_object=d0_object, card_content=d0.text)
    assert is_collapsed(card_object=d1_object, card_content=d1.text)

    # cards can be expanded simultaneously
    d0_object.click()
    d1_object.click()
    assert is_expanded(card_object=d0_object, card_content=d0.text)
    assert is_expanded(card_object=d1_object, card_content=d1.text)


def test_accordion_card_name(page, port, accordion_components):
    d0, d1 = accordion_components
    accordion = Accordion(
        ('Card 0', d0),
        ('Card 1', d1),
    )
    serve_panel_widget(page, port, accordion)

    accordion_elements = page.locator('.accordion')
    d0_object = accordion_elements.nth(0)
    d1_object = accordion_elements.nth(1)
    # cards name
    expect(d0_object).to_contain_text('Card 0')
    expect(d1_object).to_contain_text('Card 1')


def test_accordion_active(page, port, accordion_components):
    d0, d1 = accordion_components
    accordion = Accordion(d0, d1, active=[0])
    serve_panel_widget(page, port, accordion)

    accordion_elements = page.locator('.accordion')
    # there are 2 card in this accordion
    expect(accordion_elements).to_have_count(len(accordion_components))

    # first card is expanded and its content is displayed
    d0_object = accordion_elements.nth(0)
    d0_object.wait_for()
    assert is_expanded(card_object=d0_object, card_content=d0.text)

    # second card is collapsed and its content is hidden
    d1_object = accordion_elements.nth(1)
    d1_object.wait_for()
    assert is_collapsed(card_object=d1_object, card_content=d1.text)


def test_accordion_objects(page, port, accordion_components):
    d0, d1 = accordion_components
    accordion = Accordion(d0, d1)
    serve_panel_widget(page, port, accordion)

    # change the entire list of objects in the accordion
    new_objects = [d0]
    accordion.objects = new_objects
    accordion_elements = page.locator('.accordion')
    expect(accordion_elements).to_have_count(len(new_objects))


def test_accordion_toggle(page, port, accordion_components):
    d0, d1 = accordion_components
    accordion = Accordion(d0, d1, toggle=True)
    serve_panel_widget(page, port, accordion)

    accordion_elements = page.locator('.accordion')
    # there are 2 card in this accordion
    expect(accordion_elements).to_have_count(len(accordion_components))

    d0_object = accordion_elements.nth(0)
    d1_object = accordion_elements.nth(1)
    d0_object.wait_for()
    d1_object.wait_for()

    # cannot expand all cards simultaneously, only one can be expanded at a time
    # click to expand the first card, 2nd card is collapsed
    d0_object.click()
    assert is_expanded(card_object=d0_object, card_content=d0.text)
    assert is_collapsed(card_object=d1_object, card_content=d1.text)

    # click to expand the 2nd card, 1st card is collapsed
    d1_object.click()
    assert is_collapsed(card_object=d0_object, card_content=d0.text)
    assert is_expanded(card_object=d1_object, card_content=d1.text)


def test_accordion_append(page, port, accordion_components):
    accordion = Accordion()
    serve_panel_widget(page, port, accordion)

    accordion_elements = page.locator('.accordion')
    # empty accordion
    expect(accordion_elements).to_have_count(0)

    d0, d1 = accordion_components

    # add new element d0
    accordion.append(d0)
    expect(accordion_elements).to_have_count(1)
    # collapsed by default
    d0_object = accordion_elements.nth(0)
    assert is_collapsed(card_object=d0_object, card_content=d0.text)

    # add new element d1
    accordion.append(d1)
    expect(accordion_elements).to_have_count(2)
    d1_object = accordion_elements.nth(1)
    # both cards are collapsed
    assert is_collapsed(card_object=d0_object, card_content=d0.text)
    assert is_collapsed(card_object=d1_object, card_content=d1.text)


def test_accordion_extend(page, port, accordion_components):
    d0, d1 = accordion_components
    accordion = Accordion(d0, d1)
    serve_panel_widget(page, port, accordion)

    accordion_elements = page.locator('.accordion')
    expect(accordion_elements).to_have_count(len(accordion_components))

    d2 = Div(name='Div 2', text='Text 2')
    additional_list = [d2]
    # add new list of elements to the accordion
    accordion.extend(additional_list)
    expect(accordion_elements).to_have_count(len(accordion_components) + len(additional_list))

    # collapsed by default
    d0_object = accordion_elements.nth(0)
    d1_object = accordion_elements.nth(1)
    d2_object = accordion_elements.nth(2)
    assert is_collapsed(card_object=d0_object, card_content=d0.text)
    assert is_collapsed(card_object=d1_object, card_content=d1.text)
    assert is_collapsed(card_object=d2_object, card_content=d2.text)


def test_accordion_clear(page, port, accordion_components):
    d0, d1 = accordion_components
    accordion = Accordion(d0, d1)
    serve_panel_widget(page, port, accordion)

    accordion_elements = page.locator('.accordion')
    expect(accordion_elements).to_have_count(len(accordion_components))

    # clear all contents of the accordion
    accordion.clear()
    # empty accordion
    expect(accordion_elements).to_have_count(0)


def test_accordion_insert(page, port, accordion_components):
    d0, d1 = accordion_components
    accordion = Accordion(d0, d1)
    serve_panel_widget(page, port, accordion)

    accordion_elements = page.locator('.accordion')
    expect(accordion_elements).to_have_count(len(accordion_components))

    # order of the elements
    d0_object = accordion_elements.nth(0)
    d1_object = accordion_elements.nth(1)
    # cards name
    expect(d0_object).to_contain_text(d0.name)
    expect(d1_object).to_contain_text(d1.name)

    inserted_div = Div(name='Inserted Div', text='Inserted text')
    # insert new component
    accordion.insert(index=1, pane=inserted_div)
    expect(accordion_elements).to_have_count(len(accordion_components) + 1)

    # order of the elements after insertion
    d0_object = accordion_elements.nth(0)
    inserted_object = accordion_elements.nth(1)
    d1_object = accordion_elements.nth(2)
    # cards name
    expect(d0_object).to_contain_text(d0.name)
    expect(inserted_object).to_contain_text(inserted_div.name)
    expect(d1_object).to_contain_text(d1.name)


def test_accordion_pop(page, port, accordion_components):
    d0, d1 = accordion_components
    accordion = Accordion(d0, d1)
    serve_panel_widget(page, port, accordion)

    accordion_elements = page.locator('.accordion')
    expect(accordion_elements).to_have_count(len(accordion_components))

    # remove first component
    accordion.pop(index=0)
    expect(accordion_elements).to_have_count(len(accordion_components) - 1)
    # only card d1 in the accordion
    d1_object = accordion_elements.nth(0)
    expect(d1_object).to_contain_text(d1.name)


def test_accordion_remove(page, port, accordion_components):
    d0, d1 = accordion_components
    accordion = Accordion(d0, d1)
    serve_panel_widget(page, port, accordion)

    accordion_elements = page.locator('.accordion')
    expect(accordion_elements).to_have_count(len(accordion_components))

    # remove first component
    accordion.remove(pane=accordion.objects[0])
    expect(accordion_elements).to_have_count(len(accordion_components) - 1)
    # only card d1 in the accordion
    d1_object = accordion_elements.nth(0)
    expect(d1_object).to_contain_text(d1.name)
