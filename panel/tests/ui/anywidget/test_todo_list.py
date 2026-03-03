"""
Playwright test for the todo list anywidget example.

Tests:
    1. Widget renders (input, add button, and list appear)
    2. No unexpected console errors
    3. Browser -> Python sync (add item in browser, items list updates in Python)
    4. Python -> Browser sync (add item from Python, list updates in browser)
    5. Delete functionality (delete item in browser, Python state updates)
"""
import anywidget
import pytest
import traitlets

import panel as pn

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until

from .conftest import assert_no_console_errors, wait_for_anywidget

pytestmark = pytest.mark.ui


# --- Widget definition (same as research/anywidget/examples/todo_list.py) ---

class TodoWidget(anywidget.AnyWidget):
    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "todo-container";

        let inputDiv = document.createElement("div");
        inputDiv.className = "todo-input-section";

        let input = document.createElement("input");
        input.type = "text";
        input.placeholder = "Add a new todo item...";
        input.className = "todo-input";

        let addBtn = document.createElement("button");
        addBtn.textContent = "Add";
        addBtn.className = "todo-add-btn";

        addBtn.addEventListener("click", () => {
            let value = input.value.trim();
            if (value) {
                let items = model.get("items") || [];
                let newItems = [...items, value];
                model.set("items", newItems);
                model.save_changes();
                input.value = "";
                renderList();
            }
        });

        input.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                addBtn.click();
            }
        });

        inputDiv.appendChild(input);
        inputDiv.appendChild(addBtn);
        container.appendChild(inputDiv);

        let list = document.createElement("ul");
        list.className = "todo-list";
        container.appendChild(list);

        function renderList() {
            list.innerHTML = "";
            let items = model.get("items") || [];
            items.forEach((item, index) => {
                let li = document.createElement("li");
                li.className = "todo-item";

                let span = document.createElement("span");
                span.textContent = item;
                li.appendChild(span);

                let deleteBtn = document.createElement("button");
                deleteBtn.textContent = "Delete";
                deleteBtn.className = "todo-delete-btn";
                deleteBtn.addEventListener("click", () => {
                    let items = model.get("items") || [];
                    let newItems = [...items];
                    newItems.splice(index, 1);
                    model.set("items", newItems);
                    model.save_changes();
                    renderList();
                });

                li.appendChild(deleteBtn);
                list.appendChild(li);
            });
        }

        renderList();

        model.on("change:items", () => {
            renderList();
        });

        el.appendChild(container);
    }
    export default { render };
    """

    _css = """
    .todo-container { font-family: sans-serif; max-width: 500px; padding: 20px; }
    .todo-input-section { display: flex; gap: 8px; margin-bottom: 20px; }
    .todo-input { flex: 1; padding: 10px 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
    .todo-add-btn { padding: 10px 20px; background-color: #2196F3; color: white; border: none;
                    border-radius: 4px; cursor: pointer; font-weight: 600; }
    .todo-list { list-style: none; padding: 0; margin: 0; }
    .todo-item { display: flex; justify-content: space-between; align-items: center;
                 padding: 12px; background: #f5f5f5; margin-bottom: 8px; border-radius: 4px;
                 border-left: 4px solid #2196F3; }
    .todo-item span { flex: 1; font-size: 15px; }
    .todo-delete-btn { padding: 6px 12px; background-color: #f44336; color: white; border: none;
                       border-radius: 3px; cursor: pointer; font-size: 12px; }
    """

    items = traitlets.List(traitlets.Unicode(), []).tag(sync=True)


def test_todo_renders(page):
    """Widget renders with input, add button, and empty list."""
    widget = TodoWidget(items=[])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    input_el = page.locator("input.todo-input")
    expect(input_el).to_be_visible()

    add_btn = page.locator("button.todo-add-btn")
    expect(add_btn).to_be_visible()
    expect(add_btn).to_contain_text("Add")

    # No items initially
    items = page.locator(".todo-item")
    expect(items).to_have_count(0)

    assert_no_console_errors(msgs)


def test_todo_renders_with_initial_items(page):
    """Widget renders with pre-existing items."""
    widget = TodoWidget(items=["Buy milk", "Walk the dog"])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    items = page.locator(".todo-item")
    expect(items).to_have_count(2)

    expect(items.nth(0)).to_contain_text("Buy milk")
    expect(items.nth(1)).to_contain_text("Walk the dog")

    assert_no_console_errors(msgs)


def test_todo_add_item_browser(page):
    """Adding an item in the browser updates Python state (browser -> Python sync)."""
    widget = TodoWidget(items=[])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    input_el = page.locator("input.todo-input")
    add_btn = page.locator("button.todo-add-btn")

    # Type and add an item
    input_el.fill("Test item 1")
    add_btn.click()

    # Wait for Python-side items to update
    wait_until(lambda: len(widget.items) == 1, page)
    assert widget.items == ["Test item 1"]
    assert pane.component.items == ["Test item 1"]

    # Verify DOM updated
    items = page.locator(".todo-item")
    expect(items).to_have_count(1)
    expect(items.first).to_contain_text("Test item 1")

    # Add another item
    input_el.fill("Test item 2")
    add_btn.click()

    wait_until(lambda: len(widget.items) == 2, page)
    assert widget.items == ["Test item 1", "Test item 2"]

    items = page.locator(".todo-item")
    expect(items).to_have_count(2)

    assert_no_console_errors(msgs)


def test_todo_add_item_python(page):
    """Adding an item from Python updates the browser list (Python -> browser sync)."""
    widget = TodoWidget(items=[])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    items = page.locator(".todo-item")
    expect(items).to_have_count(0)

    # Add item from Python
    pane.component.items = ["Python item"]

    # Wait for DOM to update
    expect(items).to_have_count(1)
    expect(items.first).to_contain_text("Python item")

    # Add more items from Python
    pane.component.items = ["Python item", "Another item"]
    expect(items).to_have_count(2)
    expect(items.nth(1)).to_contain_text("Another item")

    assert widget.items == ["Python item", "Another item"]

    assert_no_console_errors(msgs)


def test_todo_delete_item(page):
    """Deleting an item in the browser updates Python state (browser -> Python sync)."""
    widget = TodoWidget(items=["Item A", "Item B", "Item C"])
    pane = pn.pane.AnyWidget(widget)

    msgs, _ = serve_component(page, pane)
    wait_for_anywidget(page)

    items = page.locator(".todo-item")
    expect(items).to_have_count(3)

    # Delete the middle item ("Item B") by clicking its delete button
    delete_btns = page.locator(".todo-delete-btn")
    delete_btns.nth(1).click()

    # Wait for Python-side items to update
    wait_until(lambda: len(widget.items) == 2, page)
    assert widget.items == ["Item A", "Item C"]

    items = page.locator(".todo-item")
    expect(items).to_have_count(2)

    assert_no_console_errors(msgs)
