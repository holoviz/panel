import time

import pytest

from bokeh.models import Div

from panel import Accordion
from panel.io.server import serve

try:
    from playwright.sync_api import expect
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui


@pytest.fixture
def accordion_components():
    # divs with mock css classes for easy search for elements in the Accordion
    d1 = Div(name='Div 1', text='Text 1', css_classes=['class_div1'])
    d2 = Div(name='Div 2', text='Text 2', css_classes=['class_div2'])
    return d1, d2


def is_collapsed(card_object, card_content):
    expect(card_object).to_contain_text("\u25ba")
    expect(card_object).not_to_contain_text(card_content)
    return True


def is_expanded(card_object, card_content):
    expect(card_object).to_contain_text("\u25bc")
    expect(card_object).to_contain_text(card_content)
    return True


def test_accordion_default(page, port, accordion_components):
    d1, d2 = accordion_components
    accordion = Accordion(d1, d2)
    serve(accordion, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    accordion_elements = page.locator('.bk.accordion')
    # there are 2 card in this accordion
    expect(accordion_elements).to_have_count(len(accordion_components))

    # order of the elements
    d1_object = accordion_elements.nth(0)
    d2_object = accordion_elements.nth(1)
    d1_object.wait_for()
    d2_object.wait_for()

    # cards name
    expect(d1_object).to_contain_text(d1.name)
    expect(d2_object).to_contain_text(d2.name)

    # cards are collapsed and their content is hidden by default
    assert is_collapsed(card_object=d1_object, card_content=d1.text)
    assert is_collapsed(card_object=d2_object, card_content=d2.text)

    # cards can be expanded simultaneously
    d1_object.click()
    d2_object.click()
    assert is_expanded(card_object=d1_object, card_content=d1.text)
    assert is_expanded(card_object=d2_object, card_content=d2.text)


def test_accordion_active(page, port, accordion_components):
    d1, d2 = accordion_components
    accordion = Accordion(d1, d2, active=[0])
    serve(accordion, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    accordion_elements = page.locator('.bk.accordion')
    # there are 2 card in this accordion
    expect(accordion_elements).to_have_count(len(accordion_components))

    # first card is expanded and its content is displayed
    d1_object = accordion_elements.nth(0)
    d1_object.wait_for()
    assert is_expanded(card_object=d1_object, card_content=d1.text)

    # second card is collapsed and its content is hidden
    d2_object = accordion_elements.nth(1)
    d2_object.wait_for()
    assert is_collapsed(card_object=d2_object, card_content=d2.text)


def test_accordion_objects(page, port, accordion_components):
    d1, d2 = accordion_components
    accordion = Accordion(d1, d2)
    serve(accordion, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    # change the entire list of objects in the accordion
    new_objects = [d1]
    accordion.objects = new_objects
    accordion_elements = page.locator('.bk.accordion')
    expect(accordion_elements).to_have_count(len(new_objects))


def test_accordion_toggle(page, port, accordion_components):
    d1, d2 = accordion_components
    accordion = Accordion(d1, d2, toggle=True)
    serve(accordion, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    accordion_elements = page.locator('.bk.accordion')
    # there are 2 card in this accordion
    expect(accordion_elements).to_have_count(len(accordion_components))

    d1_object = accordion_elements.nth(0)
    d2_object = accordion_elements.nth(1)
    d1_object.wait_for()
    d2_object.wait_for()

    # cannot expand all cards simultaneously, only one can be expanded at a time
    # click to expand the first card, 2nd card is collapsed
    d1_object.click()
    assert is_expanded(card_object=d1_object, card_content=d1.text)
    assert is_collapsed(card_object=d2_object, card_content=d2.text)

    # click to expand the 2nd card, 1st card is collapsed
    d2_object.click()
    assert is_collapsed(card_object=d1_object, card_content=d1.text)
    assert is_expanded(card_object=d2_object, card_content=d2.text)


def test_accordion_append(page, port, accordion_components):
    accordion = Accordion()
    serve(accordion, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    accordion_elements = page.locator('.bk.accordion')
    # empty accordion
    expect(accordion_elements).to_have_count(0)

    d1, d2 = accordion_components

    # add new element d1
    accordion.append(d1)
    expect(accordion_elements).to_have_count(1)
    # collapsed by default
    d1_object = accordion_elements.nth(0)
    assert is_collapsed(card_object=d1_object, card_content=d1.text)

    # add new element d2
    accordion.append(d2)
    expect(accordion_elements).to_have_count(2)
    d2_object = accordion_elements.nth(1)
    # both cards are collapsed
    assert is_collapsed(card_object=d1_object, card_content=d1.text)
    assert is_collapsed(card_object=d2_object, card_content=d2.text)


def test_accordion_extend(page, port, accordion_components):
    d1, d2 = accordion_components
    accordion = Accordion(d1, d2)
    serve(accordion, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    accordion_elements = page.locator('.bk.accordion')
    expect(accordion_elements).to_have_count(len(accordion_components))

    d3 = Div(name='Div 3', text='Text 3', css_classes=['class_div3'])
    additional_list = [d3]
    # add new list of elements to the accordion
    accordion.extend(additional_list)
    expect(accordion_elements).to_have_count(len(accordion_components) + len(additional_list))

    # collapsed by default
    d1_object = accordion_elements.nth(0)
    d2_object = accordion_elements.nth(1)
    d3_object = accordion_elements.nth(2)
    assert is_collapsed(card_object=d1_object, card_content=d1.text)
    assert is_collapsed(card_object=d2_object, card_content=d2.text)
    assert is_collapsed(card_object=d3_object, card_content=d3.text)


def test_accordion_clear(page, port, accordion_components):
    d1, d2 = accordion_components
    accordion = Accordion(d1, d2)
    serve(accordion, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}")

    accordion_elements = page.locator('.bk.accordion')
    expect(accordion_elements).to_have_count(len(accordion_components))

    # clear all contents of the accordion
    accordion.clear()
    # empty accordion
    expect(accordion_elements).to_have_count(0)
