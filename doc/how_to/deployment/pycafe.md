# PyCafe Guide

This guide demonstrates how to deploy a Panel app on [py.cafe](https://py.cafe/).

PyCafe is a platform for creating and sharing data apps online, powered by [Pyodide](https://pyodide.org/). It offers a free tier for users. You can find the official PyCafe-Panel guide [here](https://py.cafe/docs/apps/panel).

## 1. Log In

Visit [py.cafe](https://py.cafe/) and either sign in or sign up for an account if you want to save your projects to your personal gallery.

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

<iframe src="https://py.cafe/embed/panel-org/pycafe-reference?theme=light&linkToApp=false" title="PyCafe Reference Example" frameborder="0" style="width: 100%; height: 500px;"></iframe>

Finally you can click **PUSH** to persist your app and click **SHARE** to share it with the world.

## Example Gallery

Explore the [`panel-org`](https://py.cafe/panel-org) gallery examples below:

- [Basic Github App](https://py.cafe/panel-org/pycafe-reference) from the [GitHub repository](https://github.com/holoviz/panel/#interactive-data-apps).
- [Build an App](https://py.cafe/panel-org/build-app) from the [Build an App | Getting Started guide](https://panel.holoviz.org/getting_started/build_app.html).
- [XGBoost Training App](https://py.cafe/panel-org/xgboost-training) from the [Convert Apps to WASM Guide](https://panel.holoviz.org/how_to/wasm/convert.html).

### Basic Tutorials

- [Animation](https://py.cafe/panel-org/basic-animation) from the [Build an Animation Tutorial](../../tutorials/basic/build_report).
- [Chatbot](https://py.cafe/panel-org/basic-chatbot) from the [Build a Chatbot Tutorial](../../tutorials/basic/build_chatbot).
- [Crossfilter Dashboard](https://py.cafe/panel-org/basic-crossfilter-dashboard) from the [Build Crossfiltering Dashboard Tutorial](../../tutorials/basic/build_crossfilter_dashboard).
- [Dashboard](https://py.cafe/panel-org/basic-dashboard) from the [Build a Dashboard Tutorial](../../tutorials/basic/build_dashboard).
- [Image Classifier](https://py.cafe/panel-org/basic-image-classifier) from the [Build an Image Classifier Tutorial](../../tutorials/basic/build_image_classifier).
- [Monitoring Dashboard](https://py.cafe/panel-org/basic-monitoring-dashboard) from the [Build an Monitoring Dashboard Tutorial](../../tutorials/basic/build_monitoring_dashboard).
- [Report](https://py.cafe/panel-org/basic-report) from the [Build a Report Tutorial](../../tutorials/basic/build_report).
- [Streaming Dashboard](https://py.cafe/panel-org/basic-streaming-dashboard) from the [Build Streaming Dashboard Tutorial](../../tutorials/basic/build_streaming_dashboard).
- [Todo app | Widget approach](https://py.cafe/panel-org/basic-todo) from the [Build a todo app](../../tutorials/basic/build_todo).

### Intermediate Tutorials

- [Todo App | Class approach](https://py.cafe/panel-org/intermediate-todo-app) from the [Build a todo app](../../tutorials/intermediate/build_todo).

## Expert Tutorials

- [Mario Chime Button | AnyWidget](https://py.cafe/panel-org/panel-mario-chime-anywidget) from the [Custom AnyWidget Tutorial](../../tutorials/expert/custom_anywidget_components).
- [Mario Chime Button | JSComponent](https://py.cafe/panel-org/panel-mario-chime-jscomponent) from the [Custom JSComponent Tutorial](../../tutorials/expert/custom_js_components).

### App Gallery

- [Altair Brushing](https://py.cafe/panel-org/altair-brushing) from the [Altair Brushing Tutorial](../../gallery/altair_brushing).
- [hvPlot Explorer](https://py.cafe/panel-org/hvplot-explorer) from the [hvPlot Explorer Tutorial](../../gallery/hvplot_explorer)
- [NYC Deck.GL](https://py.cafe/panel-org/nyc-deckgl) from the [NYC Deck.Gl Tutorial](../../gallery/nyc_deckgl).
- [Penguin Crossfilter](https://py.cafe/panel-org/penguin-crossfilter) from the [Penguin Crossfilter Tutorial](../../gallery/penguin_crossfilter)
- [Portfolio Analyzer](https://py.cafe/panel-org/portfolio-analyzer) from the [Portfolio Analyzer Tutorial](../../gallery/portfolio_analyzer).
- [VideoStream Interface](https://py.cafe/panel-org/videostream) from the [VideoStream Interface Tutorial](../../gallery/streaming_videostream).

----

For more examples check out [awesome-panel.org](https://py.cafe/awesome.panel.org).
