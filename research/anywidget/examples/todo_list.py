"""
Todo list anywidget demonstrating List traitlet with complex state.

This example demonstrates:
- Defining a custom anywidget with List traitlet for managing items
- Rendering a dynamic list with add and delete functionality
- Bidirectional synchronization between the anywidget and Panel widgets
- Using param.watch() and pn.bind() on pane.component for Panel-side reactivity

Run with: panel serve research/anywidget/examples/todo_list.py
"""
import anywidget
import traitlets

import panel as pn

pn.extension()


class TodoWidget(anywidget.AnyWidget):
    """A todo list widget with add and delete functionality."""

    _esm = """
    function render({ model, el }) {
        let container = document.createElement("div");
        container.className = "todo-container";

        // Input and Add button
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

        // Todo list
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
    .todo-container {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        max-width: 500px;
        padding: 20px;
    }

    .todo-input-section {
        display: flex;
        gap: 8px;
        margin-bottom: 20px;
    }

    .todo-input {
        flex: 1;
        padding: 10px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 14px;
    }

    .todo-input:focus {
        outline: none;
        border-color: #2196F3;
        box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
    }

    .todo-add-btn {
        padding: 10px 20px;
        background-color: #2196F3;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 600;
    }

    .todo-add-btn:hover {
        background-color: #1976D2;
    }

    .todo-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .todo-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px;
        background: #f5f5f5;
        margin-bottom: 8px;
        border-radius: 4px;
        border-left: 4px solid #2196F3;
    }

    .todo-item span {
        flex: 1;
        font-size: 15px;
    }

    .todo-delete-btn {
        padding: 6px 12px;
        background-color: #f44336;
        color: white;
        border: none;
        border-radius: 3px;
        cursor: pointer;
        font-size: 12px;
    }

    .todo-delete-btn:hover {
        background-color: #d32f2f;
    }
    """

    items = traitlets.List(traitlets.Unicode(), []).tag(sync=True)


# Create the anywidget instance and wrap it with Panel
widget = TodoWidget(items=[])
pane = pn.pane.AnyWidget(widget)

# pane.component is available immediately — use param API
component = pane.component

# Create Panel TextInput + Button to add items from Python
item_input = pn.widgets.TextInput(name="Add item from Python", value="", width=300)
add_button = pn.widgets.Button(name="Add", button_type="primary")

# Reactive counter display using pn.bind on the component param
item_count = pn.pane.Markdown(pn.bind(
    lambda items: f"**Item count:** {len(items)}", component.param.items
))


def add_item_from_python(event):
    if item_input.value.strip():
        component.items = list(component.items) + [item_input.value]
        item_input.value = ""


add_button.on_click(add_item_from_python)

# Layout
header = pn.pane.Markdown("""
# Todo List Example — AnyWidget Pane + List Traitlet

This example demonstrates a **List traitlet** with complex state management.
The todo list is an anywidget rendered via ESM with its own add/delete UI.
You can also add items from **Panel widgets** on the Python side.

**Try it:**
1. Type in the **anywidget input** (top) and click "Add" — item appears in the list.
2. Type in the **Panel TextInput** (bottom) and click "Add" — item also appears.
3. Click "Delete" on any item — the list updates and the Python-side count syncs.

Both directions prove that `List` traitlet sync works for complex state!
""")

pn.Column(
    header,
    pn.pane.Markdown("### Anywidget (browser-side todo list)"),
    pane,
    pn.pane.Markdown("### Panel Widgets (Python-side controls)"),
    pn.Row(item_input, add_button),
    item_count,
).servable()
