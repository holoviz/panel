# Placeholder
---
```python
import panel as pn
import time

pn.extension()
```

The `Placeholder` pane serves as a placeholder for other Panel components. It can be used to display a message while a computation is running, for example.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **`object`** (Any): The Panel object to display, if object is not already a Panel object it will be converted with the `panel(...)` function.

___

The `Placeholder` pane can accept any Panel component as its argument, including other panes.

```python
placeholder = pn.pane.Placeholder("Hello")
placeholder
```

The benefit of using a `Placeholder` is that it allows you to replace the content of the pane without being restricted to a specific type of component. This means you can replace the placeholder with any other pane type, including plots, images, and widgets. You may either use the `update` method:

```python
placeholder.update(pn.widgets.TextInput(value="Hello again!"))
```

or set the `object` directly:

```python
placeholder.object = "Hello once more!"
```

If you'd like to temporarily replace the contents, you can use it as a context manager.

```python
placeholder = pn.pane.Placeholder("⏳ Idle", stylesheets=[":host { font-size: 24pt }"])
placeholder
```

Upon execution of the cell below, the `Placeholder` pane will display `Starting...`, `Running...`, and `Complete!` in sequence, with a 1 second pause between each message, before finally displaying `Idle` again.

```python
with placeholder:
    placeholder.update("🚀 Starting...")
    time.sleep(1)
    placeholder.update("🏃 Running...")
    time.sleep(1)
    placeholder.update("✅ Complete!")
    time.sleep(1)
```

---
