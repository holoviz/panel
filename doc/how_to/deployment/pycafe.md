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

<iframe src="https://py.cafe/app/Panel_Org/pycafe-reference" title="PyCafe Reference Example" frameborder="0" style="width: 100%; height: 500px;"></iframe>

Finally you can click **PUSH** to persist your app and click **SHARE** to share it with the world.

## Example Gallery

Explore the examples below:

- [Basic Github App](https://py.cafe/Panel_Org/pycafe-reference) from the [GitHub repository](https://github.com/holoviz/panel/#interactive-data-apps).
- [Greeting App](https://py.cafe/maartenbreddels/panel-interactive-greeting-app ).
- [XGBoost Training App](https://py.cafe/Panel_Org/xgboost-training) from the [Convert Apps to WASM Guide](https://panel.holoviz.org/how_to/wasm/convert.html).

### Basic Tutorials

- [Animation](https://py.cafe/Panel_Org/basic-animation) from the [Build an Animation Tutorial](../../tutorials/basic/build_report.md).
- [Chatbot](https://py.cafe/Panel_Org/basic-chatbot) from the [Build a Chatbot Tutorial](../../tutorials/basic/build_chatbot.md).
- [Crossfilter Dashboard](https://py.cafe/Panel_Org/basic-crossfilter-dashboard) from the [Build Crossfiltering Dashboard Tutorial](../../tutorials/basic/build_crossfilter_dashboard.md).
- [Dashboard](https://py.cafe/Panel_Org/basic-dashboard) from the [Build a Dashboard Tutorial](../../tutorials/basic/build_dashboard.md).
- [Image Classifier](https://py.cafe/Panel_Org/basic-image-classifier) from the [Build an Image Classifier Tutorial](../../tutorials/basic/build_image_classifier.md).
- [Monitoring Dashboard](https://py.cafe/Panel_Org/basic-monitoring-dashboard) from the [Build an Monitoring Dashboard Tutorial](../../tutorials/basic/build_monitoring_dashboard.md).
- [Report](https://py.cafe/Panel_Org/basic-report) from the [Build a Report Tutorial](../../tutorials/basic/build_report.md).
- [Streaming Dashboard](https://py.cafe/Panel_Org/basic-streaming-dashboard) from the [Build Streaming Dashboard Tutorial](../../tutorials/basic/build_streaming_dashboard.md).
- [Todo app | Widget approach](https://py.cafe/Panel_Org/basic-todo) from the [Build a todo app](../../tutorials/basic/build_todo.md).

### Intermediate Tutorials

- [Todo App | Class approach](https://py.cafe/Panel_Org/intermediate-todo-app) from the [Build a todo app](../../tutorials/intermediate/build_todo.md).

### App Gallery

- [Altair Brushing](https://py.cafe/Panel_Org/altair-brushing) from the [Altair Brushing Tutorial](../../gallery/altair_brushing.ipynb).
- [hvPlot Explorer](https://py.cafe/Panel_Org/hvplot-explorer) from the [hvPlot Explorer Tutorial](../../gallery/hvplot_explorer.ipynb)
- [NYC Deck.GL](https://py.cafe/Panel_Org/nyc-deckgl) from the [NYC Deck.Gl Tutorial](../../gallery/nyc_deckgl.ipynb).
- [Penguin Crossfilter](https://py.cafe/Panel_Org/penguin-crossfilter) from the [Penguin Crossfilter Tutorial](../../gallery/penguin_crossfilter.ipynb)
- [Portfolio Analyzer](https://py.cafe/Panel_Org/portfolio-analyzer) from the [Portfolio Analyzer Tutorial](../../gallery/portfolio_analyzer.ipynb).
- [VideoStream Interface](https://py.cafe/Panel_Org/videostream) from the [VideoStream Interface Tutorial](../../gallery/streaming_videostream.ipynb).
