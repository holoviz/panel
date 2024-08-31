# PY.CAFE Guide

This guide demonstrates how to deploy a Panel app on [PY.CAFE](https://py.cafe/).

PY.CAFE is a platform for creating and sharing data apps online, powered by [Pyodide](https://pyodide.org/). It offers a free tier for users.

## 1. Log In

Visit [PY.CAFE](https://py.cafe/) and either sign in or sign up for an account if you want to save your projects to your personal gallery.

## 2. Choose the Panel Framework

Select the Panel framework from the available options or use the direct link [PY.CAFE/snippet/panel](https://py.cafe/snippet/panel/v1).

## 3. Update the `requirements.txt` File

Add `panel` and any other necessary dependencies to your `requirements.txt` file:

```bash
panel
```

You don't have to pin version of panel or other dependencies as PY.CAFE will create a lock file with pinned versions automatically.

## 4. Update the `app.py` File

Update your `app.py` file with the following code:

```python
import panel as pn

pn.extension()


def model(n=5):
    return "⭐" * n

slider = pn.widgets.IntSlider(value=5, start=1, end=5)

interactive_model = pn.bind(model, n=slider)

layout = pn.Column(slider, interactive_model)

pn.template.FastListTemplate(
    site="Panel", title="Example", main=[layout],
).servable()
```

After updating the file, save it, and the app will reload instantly.

<iframe src="https://py.cafe/app/MarcSkovMadsen/pycafe-reference" title="PyCafe Reference Example" frameborder="0" style="width: 100%; height: 500px;"></iframe>

Finally you can click **PUSH** to persist your app and click **SHARE** to share it with the world.

## Example Gallery

Explore the examples below:

- [Greeting App](https://py.cafe/maartenbreddels/panel-interactive-greeting-app ).
- [Basic Github App](https://py.cafe/MarcSkovMadsen/pycafe-reference) from the [GitHub repository](https://github.com/holoviz/panel/#interactive-data-apps).
- [XGBoost Training App](https://py.cafe/MarcSkovMadsen/xgboost-training) from the [Convert Apps to WASM Guide](https://panel.holoviz.org/how_to/wasm/convert.html).

### Basic Tutorials

- [Basic Dashboard](https://py.cafe/MarcSkovMadsen/basic-dashboard) from the [Build a Dashboard Tutorial](../../tutorials/basic/build_dashboard.md).
- [Basic Report](https://py.cafe/MarcSkovMadsen/basic-report) from the [Build a Report Tutorial](../../tutorials/basic/build_report.md).
- [Basic Animation](https://py.cafe/MarcSkovMadsen/basic-animation) from the [Build an Animation Tutorial](../../tutorials/basic/build_report.md).
- [Basic Image Classifier](https://py.cafe/MarcSkovMadsen/basic-image-classifier) from the [Build an Image Classifier Tutorial](../../tutorials/basic/build_image_classifier.md).

### App Gallery

- [VideoStream Interface](https://py.cafe/MarcSkovMadsen/videostream) from the [VideoStream Interface Tutorial](https://panel.holoviz.org/gallery/streaming_videostream.html).

### Other

- [Drawdata](https://py.cafe/MarcSkovMadsen/basic-drawdata) demonstrating that an ipywidget/ AnyWidget can be used with Panel in PY.CAFE.
