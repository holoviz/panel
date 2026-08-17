# HTML
---
```python
import panel as pn

pn.extension()
```

The `HTML` pane allows rendering arbitrary HTML in a panel. It renders strings containing valid HTML as well as objects with a `_repr_html_` method and may define custom CSS styles.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **`disable_math`** (boolean, `default=True`): Whether to disable MathJax math rendering for strings escaped with `$$` delimiters.
* **`enable_streaming`** (boolean, `default=False`): Whether to enable streaming of text snippets. This will diff the `object` when it is updated and only send the trailing chunk that was added.
* **`object`** (str or object): The string or object with ``_repr_html_`` method to display
* **`sanitize_html`** (boolean, `default=False`): Whether to sanitize HTML sent to the frontend.
* **`sanitize_hook`** (Callable, `default=bleach.clean`): Sanitization callback to apply if `sanitize_html=True`.
* **`styles`** (dict): Dictionary specifying CSS styles

___

The `HTML` pane accepts the entire HTML5 spec including any embedded script tags, which will be executed. It also supports a `styles` dictionary to apply styles to control the style of the `` tag the HTML contents will be rendered in.

```python
styles = {
    'background-color': '#F6F6F6', 'border': '2px solid black',
    'border-radius': '5px', 'padding': '10px'
}

html_pane = pn.pane.HTML("""
<h1>This is an HTML pane</h1>

x = 5;<br>
y = 6;<br>
z = x + y;

<br>
<br>

  
    Firstname
    Lastname 
    Age
  
  
    Jill
    Smith 
    50
  
  
    Eve
    Jackson 
    94
  

""", styles=styles)

html_pane
```

To update the ``object`` or ``styles`` we can simply set it:

```python
html_pane.styles = dict(html_pane.styles, border='2px solid red')
```

## HTML Documents

The `HTML` pane is designed to display *basic* HTML content. It is not suitable for rendering full HTML documents that include JavaScript or other dynamic elements.

To display complete HTML documents, you can escape the HTML content and embed it within an `iframe`. Here's how you can achieve this:

```python
import html
import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn
from io import StringIO

pn.extension()

# Set seed for reproducibility
np.random.seed(1)

# Create a time-series data frame
idx = pd.date_range("1/1/2000", periods=1000)
df = pd.DataFrame(np.random.randn(1000, 4), index=idx, columns=list("ABCD")).cumsum()

# Plot the data using hvplot
plot = df.hvplot()

# Save the plot. We use a StringIO object in the reference guide to avoid saving to disk.
plot_file = StringIO()
hvplot.save(plot, plot_file)
plot_file.seek(0)  # Move to the beginning of the StringIO object

# Read the HTML content and escape it
html_content = plot_file.read()
escaped_html = html.escape(html_content)

# Create iframe embedding the escaped HTML and display it
iframe_html = f'<iframe srcdoc="{escaped_html}" style="height:100%; width:100%" frameborder="0"></iframe>'

# Display iframe in a Panel HTML pane
pn.pane.HTML(iframe_html, height=350, sizing_mode="stretch_width")
```

This method ensures that the embedded HTML is safely isolated within an iframe, preventing any script execution that might otherwise occur directly within the Panel environment. This approach is particularly useful for embedding rich content, such as interactive visualizations, that requires its own separate HTML structure.

---
