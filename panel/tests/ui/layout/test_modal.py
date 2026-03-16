import pytest

from panel.layout import Modal, Spacer
from panel.tests.util import serve_component, wait_until

pytest.importorskip("playwright")

from playwright.sync_api import expect

pytestmark = pytest.mark.ui


def test_modal_close_open(page):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        Spacer(styles=dict(background="green"), width=200, height=200),
        Spacer(styles=dict(background="blue"), width=200, height=200),
    )

    serve_component(page, modal)

    modal_locator = page.locator("#pnx_dialog_content")
    expect(modal_locator).to_be_hidden()

    modal.open = True
    expect(modal_locator).to_be_visible()


def test_modal_open_close(page):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        Spacer(styles=dict(background="green"), width=200, height=200),
        Spacer(styles=dict(background="blue"), width=200, height=200),
        open=True,
    )

    serve_component(page, modal)

    modal_locator = page.locator("#pnx_dialog_content")
    expect(modal_locator).to_be_visible()

    page.mouse.click(0, 0)
    expect(modal_locator).to_be_hidden()


@pytest.mark.parametrize("show_close_button", [True, False])
def test_modal_show_close_button(page, show_close_button):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        Spacer(styles=dict(background="green"), width=200, height=200),
        Spacer(styles=dict(background="blue"), width=200, height=200),
        open=True,
        show_close_button=show_close_button,
    )

    serve_component(page, modal)

    modal_locator = page.locator("#pnx_dialog_content")
    expect(modal_locator).to_be_visible()

    modal_locator = page.locator("#pnx_dialog_close")
    if show_close_button:
        expect(modal_locator).to_be_visible()
    else:
        expect(modal_locator).to_be_hidden()


def test_modal_background_close(page):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        Spacer(styles=dict(background="green"), width=200, height=200),
        Spacer(styles=dict(background="blue"), width=200, height=200),
        open=True,
        background_close=False,
    )

    serve_component(page, modal)

    modal_locator = page.locator("#pnx_dialog_content")
    expect(modal_locator).to_be_visible()

    # Should still be visible
    page.mouse.click(0, 0)
    expect(modal_locator).to_be_visible()


def test_modal_update_objects(page):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        open=True,
    )

    serve_component(page, modal)

    content = page.locator("#pnx_dialog_content")
    expect(content).to_be_visible()

    # Verify initial child is inside dialog_content
    initial_child = content.locator(":scope > div").first
    expect(initial_child).to_be_visible()

    # Update objects dynamically
    modal.objects = [
        Spacer(styles=dict(background="blue"), width=300, height=300),
    ]
    page.wait_for_timeout(500)

    # New child must render inside #pnx_dialog_content, not inline (#7669)
    updated_children = content.locator(":scope > div:not(.pnx-dialog-close)")
    expect(updated_children).to_have_count(1)

    # Modal should still be functional: close and reopen
    page.mouse.click(0, 0)
    expect(content).to_be_hidden()

    # Regression #7669: if children leaked outside the dialog into
    # the shadow root, they would remain visible after dialog closes
    dialog = page.locator("#pnx_dialog")
    expect(dialog).to_be_hidden()

    wait_until(lambda: not modal.open, page)
    modal.open = True
    expect(content).to_be_visible()


def test_modal_update_objects_while_closed(page):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
    )

    serve_component(page, modal)

    content = page.locator("#pnx_dialog_content")
    expect(content).to_be_hidden()

    # Update objects while modal is closed
    modal.objects = [
        Spacer(styles=dict(background="green"), width=300, height=300),
    ]
    page.wait_for_timeout(500)

    # Open modal and verify content is inside dialog
    modal.open = True
    expect(content).to_be_visible()
    updated_children = content.locator(":scope > div:not(.pnx-dialog-close)")
    expect(updated_children).to_have_count(1)


def test_modal_append_objects(page):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        open=True,
    )

    serve_component(page, modal)

    content = page.locator("#pnx_dialog_content")
    expect(content).to_be_visible()

    children = content.locator(":scope > div:not(.pnx-dialog-close)")
    expect(children).to_have_count(1)

    # Append a new child
    modal.append(Spacer(styles=dict(background="blue"), width=200, height=200))
    page.wait_for_timeout(500)

    children = content.locator(":scope > div:not(.pnx-dialog-close)")
    expect(children).to_have_count(2)


def test_modal_clear_objects(page):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        open=True,
    )

    serve_component(page, modal)

    content = page.locator("#pnx_dialog_content")
    expect(content).to_be_visible()

    children = content.locator(":scope > div:not(.pnx-dialog-close)")
    expect(children).to_have_count(1)

    # Clear all objects
    modal.objects = []
    page.wait_for_timeout(500)

    children = content.locator(":scope > div:not(.pnx-dialog-close)")
    expect(children).to_have_count(0)

    # Modal should still be functional
    page.mouse.click(0, 0)
    expect(content).to_be_hidden()
    wait_until(lambda: not modal.open, page)
    modal.open = True
    expect(content).to_be_visible()


def test_modal_multiple_updates(page):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        open=True,
    )

    serve_component(page, modal)

    content = page.locator("#pnx_dialog_content")
    expect(content).to_be_visible()

    # Rapid successive updates
    for color in ["blue", "green", "orange"]:
        modal.objects = [
            Spacer(styles=dict(background=color), width=200, height=200),
        ]

    page.wait_for_timeout(500)

    # Only the final update should be visible, inside the dialog
    children = content.locator(":scope > div:not(.pnx-dialog-close)")
    expect(children).to_have_count(1)

    # Modal still functional
    page.mouse.click(0, 0)
    expect(content).to_be_hidden()
    wait_until(lambda: not modal.open, page)
    modal.open = True
    expect(content).to_be_visible()
