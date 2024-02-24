# Basic Tutorials

Welcome to the Basic Tutorials!

Are you ready to dive into the exciting world of Panel? Our Basic Tutorials are designed to guide you step by step through building awesome apps with wind turbine data. Whether you're a beginner or an enthusiast, we've got you covered! And don't hesitate to reach out on [Discord](https://discord.gg/rb6gPXbdAr) if you need help along the way.

## Prerequisites

Before we dive in, make sure you've followed along with our [Getting Started Guide](../../getting_started/index.md).

Please execute the following command to install the required dependencies:

::::{tab-set}

:::{tab-item} pip
:sync: pip

```bash
pip install altair hvplot matplotlib numpy pandas panel plotly scipy
```

:::

:::{tab-item} conda
:sync: conda

```bash
conda install -y -c conda-forge altair hvplot matplotlib numpy pandas panel plotly scipy
```

:::

::::

:::{warning}
If you are running your Jupyter Lab or notebook server in a separate Python environment, then please make sure `panel` is installed in that environment too.
:::

## Let's Get Started

Start your journey with these foundational tutorials:

- **[Build Hello World App](serve.md):** Kick things off with a simple app.
- **[Develop in Notebooks](develop_notebook.md):** Learn how to build apps right in your notebooks.
- **[Develop in Editors](develop_editor.md):** Explore tips for developing in your favorite code editor.

## Master Panel Basics

Once you're comfortable, it's time to dive deeper:

- **[Display Content with `pn.panel`](pn_panel.md)**
- **[Display Content with Panes](panes.md)**
- **[Display Performance with Indicators](indicators_performance.md)**
- **[Layout Content](layouts.md)**
- **[Control the Size](size.md)**
- **[Align Content](align.md)**
- **[Accept Inputs with Widgets](widgets.md)**
- **[React to User Input](pn_bind.md)**
- **[Handle State](state.md)**
- **[Utilize Templates](templates.md)**
- **[Apply Design](design.md)**
- **[Enhance Style](style.md)**
- **[Optimize Performance with Caching](caching.md)**
- **[Display Activity with Indicators](indicators_activity.md)**
- **[Update Progressively](progressive_layouts.md)**

## Share Your Creations

Share your awesome apps with the world!

- **[Build a Dashboard](build_dashboard.md)**
- **[Deploy a Dashboard](deploy.md)**

## Ready for Projects?

Now that you've got the basics down, it's time to put your skills to the test:

- **[Build a Report](build_report.md)**
- **[Build a Monitoring Dashboard](build_monitoring_dashboard.md)**
- **[Build an Animation](build_animation.md)**
- **[Build a Todo App](build_todo.md)**
- **[Build an Image Classifier](build_image_classifier.md)**
- **[Build a Streaming Dashboard](build_streaming_dashboard.md)**
- **[Build a Chat Bot](build_chatbot.md)**

Let's start building some amazing wind turbine apps! 🌬️🌀

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

serve
develop_notebook
develop_editor
pn_panel
panes
indicators_performance
layouts
size
align
widgets
pn_bind
state
indicators_activity
progressive_layouts
caching
templates
design
style
build_dashboard
deploy
build_monitoring_dashboard
build_report
build_animation
build_todo
build_image_classifier
build_streaming_dashboard
build_chatbot
```
