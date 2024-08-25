# PY.CAFE Guide

This guide demonstrates how to deploy a Panel app on [PY.CAFE](https://py.cafe/).

PY.CAFE is a platform for creating and sharing data apps online, powered by [Pyodide](https://pyodide.org/). It offers a free tier for users.

## 1. Log In

Visit [PY.CAFE](https://py.cafe/) and either sign in or sign up for an account.

## 2. Choose the Panel Framework

Select the Panel framework from the available options.

## 3. Update the `requirements.txt` File

Add `panel` and any other necessary dependencies to your `requirements.txt` file:

```bash
bokeh
panel
```

To minimize load time, we recommend using the minimized `cdn` resources for `panel` and `bokeh` as shown below:

```bash
bokeh @ https://cdn.holoviz.org/panel/wheels/panel-1.4.5-py3-none-any.whl
panel @ https://cdn.holoviz.org/panel/wheels/bokeh-3.4.1-py3-none-any.whl
```

We also recommend pinning the versions of the remaining dependencies to ensure your app continues to function properly despite future updates.

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

After updating the file, click **RESTART** and test the app. It should function like the example app below.

<iframe src="https://py.cafe/app/MarcSkovMadsen/pycafe-reference" title="PyCafe Reference Example" frameborder="0" style="width: 100%; height: 500px;"></iframe>

## Example Gallery

Explore the examples below:

- [Reference Example](https://py.cafe/MarcSkovMadsen/pycafe-reference) from the [GitHub repository](https://github.com/holoviz/panel/#interactive-data-apps).
- [Basic Dashboard](https://py.cafe/MarcSkovMadsen/basic-dashboard) from the [Basic Dashboard Tutorial](../../tutorials/basic/build_dashboard.md).
- [VideoStream Interface](https://py.cafe/MarcSkovMadsen/videostream) from the [VideoStream Interface Tutorial](https://panel.holoviz.org/gallery/streaming_videostream.html).
- [XGBoost Training](https://py.cafe/MarcSkovMadsen/xgboost-training) from the [Converting Panel Applications How-To Guide](https://panel.holoviz.org/how_to/wasm/convert.html).
