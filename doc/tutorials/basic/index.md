# Basic Tutorials

These tutorials are for those who have decided they would like to start learning Panel systematically. For those that have not decided yet, we recommend doing the less comprehensive [Getting Started Guide](../../getting_started/index.md) instead.

Together, we will explore the world of (wind turbine) data and give you the skills to build a chat bot, a static report, a todo app, an image classifier app, a dashboard, and a streaming application. We will take you *from zero to hero*.

We will assume you have successfully been able to [install Panel](../../getting_started/installation.md) as described in the [Getting Started Guide](../../getting_started/index.md). If not, please reach out for help on [Discord](https://discord.gg/rb6gPXbdAr).

Please put on your safety helmet before entering the world of (wind turbine) data apps.

::::::{tab-set}

:::::{tab-item} Skills
:sync: skills

The sections below will give you the skills to build *basic apps* from *single files* using a *function-based approach*.

Each section builds on the previous section.

## Part 1. Start from Zero

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`browser;2.5em;sd-mr-1` Build Hello World App
:link: serve
:link-type: doc

Kickstart our journey by creating a *Hello World* app from a Python script, Notebook, or Markdown document.
:::

::::

## Part 2. Display Content

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`zap;2.5em;sd-mr-1` Display Content with `pn.panel`
:link: pn_panel
:link-type: doc

Display our beloved wind turbine images, data, and plots easily and dynamically with `pn.panel`.
:::

:::{grid-item-card} {octicon}`device-desktop;2.5em;sd-mr-1` Display Content with Panes
:link: panes
:link-type: doc

Fine-tune how the wind turbine data is displayed with Panes, ensuring our data apps can meet the unique demands of wind turbine data visualization.
:::

:::{grid-item-card} {octicon}`pulse;2.5em;sd-mr-1` Display Performance with Indicators
:link: indicators_performance
:link-type: doc

Show the performance of your wind turbines with Panel's Indicators.
:::

::::

## Part 3. Organize Content

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`table;2.5em;sd-mr-1` Layout Content
:link: layouts
:link-type: doc

Layout Panel apps as beautifully as efficiently as a wind farm is laid out.
:::

:::{grid-item-card} {octicon}`screen-full;2.5em;sd-mr-1` Control the Size
:link: size
:link-type: doc

We will discover how sizing works in Panel, exploring the differences between inherent sizing, fixed sizing and responsive sizing. Finally we will cover responsive layouts.
:::

:::{grid-item-card} {octicon}`arrow-switch;2.5em;sd-mr-1` Align Content
:link: align
:link-type: doc

We will align our wind turbine images perfectly using `align`, `margin` and `Spacer`s.
:::

## Part 4. Handle User Input

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`person;2.5em;sd-mr-1` Accept Inputs with Widgets
:link: widgets
:link-type: doc

Elevate our app's functionality by accepting user input via widgets. Add nice tooltips with explanations to our users or disable widgets for security reasons.
:::

:::{grid-item-card} {octicon}`arrow-switch;2.5em;sd-mr-1` React to User Input
:link: pn_bind
:link-type: doc

React to user input by leveraging `pn.bind`, enabling our users to foster a deeper understanding of wind turbine data through exploration.
:::

:::{grid-item-card} {octicon}`list-ordered;2.5em;sd-mr-1` Handle State
:link: state
:link-type: doc

Be able to build larger and more complex apps by defining and maintaining state via `pn.rx`.
:::

::::

## Part 5. Improve the look

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`zap;2.5em;sd-mr-1` Use Templates
:link: templates
:link-type: doc

Use pre-made templates to easily layout our apps with a header, sidebar, and main area.
:::

:::{grid-item-card} {octicon}`zap;2.5em;sd-mr-1` Apply A Design
:link: design
:link-type: doc

Just as wind turbines come in various designs, this section empowers us to choose a design that best suits our app's style and functionality.
:::

::::

## Part 6. Improve the Feel

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` Display Activity with Indicators
:link: indicators_activity
:link-type: doc

Show activity with indicators just as rotating blades show the activity of wind turbines.
:::

:::{grid-item-card} {octicon}`versions;2.5em;sd-mr-1` Update Progressively
:link: progressive_layouts
:link-type: doc

Unleash the power of generators and reactive expressions in our Wind Turbine Apps!
:::

:::{grid-item-card} {octicon}`archive;2.5em;sd-mr-1` Add Caching
:link: caching
:link-type: doc

Caching allows our apps to store and reuse valuable computations, reducing the energy required for calculations and making our apps run faster and smoother.
:::

::::

## Part 7. Share as a Hero

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`globe;2.5em;sd-mr-1` Build a Dashboard
:link: build_dashboard
:link-type: doc

Lets build that dashboard!
:::

:::{grid-item-card} {octicon}`globe;2.5em;sd-mr-1` Deploy a Dashboard
:link: deploy
:link-type: doc

Get your dashboard in the hands of your users. Let's deploy it to Hugging Face spaces together.
:::

::::

Congrats. You have now acquired the *basic* skills required to build a wide range of Panel apps. You are now a *Panel Hero*.

The recommend next steps are to check out the the *apps* on the *Apps* tab, check out the *topics* on the *Topics* tab and start using Panel for real.

When you are ready to acquire the skills to build larger and more complex apps then check out the [Intermediate Tutorials](../intermediate/index.md).

:::::

:::::{tab-item} Apps
:sync: apps

We should be able to build any of the apps below using the skills acquired on the *Skills* tab.

Pick an app!

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`clock;2.5em;sd-mr-1` Build a Monitoring Dashboard
:link: build_monitoring_dashboard
:link-type: doc

Build a periodically refreshing dashboard to monitor your wind turbines.
:::

:::{grid-item-card} {octicon}`file;2.5em;sd-mr-1` Build a Report
:link: build_report
:link-type: doc

Construct a static Wind Turbine Report, exportable to HTML for efficient distribution to management.
:::

:::{grid-item-card} {octicon}`checklist;2.5em;sd-mr-1` Build a Todo App
:link: build_todo
:link-type: doc

Enable our wind turbine technicians to keep track of their tasks.
:::

:::{grid-item-card} {octicon}`image;2.5em;sd-mr-1` Build an Image Classifier
:link: build_image_classifier
:link-type: doc

We will build an image classifier to identify wind turbine images.
:::

:::{grid-item-card} {octicon}`clock;2.5em;sd-mr-1` Build a Streaming Dashboard
:link: build_streaming_dashboard
:link-type: doc

Build a live, updating dashboard to monitor your wind turbines.
:::

:::{grid-item-card} {octicon}`dependabot;2.5em;sd-mr-1` Build a Chat Bot
:link: build_chatbot
:link-type: doc

Develop a Streaming Wind Turbine Chat Bot that can handle many questions about wind turbines.
:::

::::

:::::

:::::{tab-item} Topics
:sync: topics

Pick any topic below to supplement the *basic skills* you acquired on the *Skills* tab.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`beaker;2.5em;sd-mr-1` Data Exploration
:link: explore_data
:link-type: doc

We will explore the wind turbine dataset and discover how Panel can power up our data exploration workflow.
:::

:::{grid-item-card} {octicon}`note;2.5em;sd-mr-1` Develop in a Notebook
:link: develop_notebook
:link-type: doc

Discover tips and tricks that will make you *swift as the wind* at exploring turbine data and building wind turbine data apps in a notebook.
:::

:::{grid-item-card} {octicon}`code;2.5em;sd-mr-1` Develop in an Editor
:link: develop_editor
:link-type: doc

Discover tips and tricks that will increase your *developer capacity* from kilowatts to megawatts when developing in an editor!
:::

:::{grid-item-card} {octicon}`people;2.5em;sd-mr-1` Join the community
:link: join_community
:link-type: doc

Find inspiration in the community forums, ask for help, help others, share your work, report issues, and add feature requests.
:::

::::

:::::

::::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

serve
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
build_dashboard
deploy
build_chatbot
build_monitoring_dashboard
build_report
build_todo
build_image_classifier
build_streaming_dashboard
explore_data
develop_notebook
develop_editor
join_community
```
