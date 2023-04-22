# Panel: The powerful data app solution for Python

Trusted by leading organizations worldwide, Panel empowers you to create sophisticated data apps that seamlessly blend your favorite Python tools with modern web technologies. Bring your data to life like never before with Panel's advanced features and intuitive interface.

::::{grid} 1 2 2 4
:gutter: 1 1 1 2

:::{grid-item-card}
:link: ./
:link-type: url

```{image} _static/logo_stacked.png
---
alt: Panel Logo
---
```
:::

:::{grid-item-card}
:link: https://youtu.be/BeBVdjENBZo
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233761035-d74e72d3-b0f6-44bd-beb1-9edd118ac432.png
---
alt: Image asking you to click it to take the tour
---
```
:::

:::{grid-item-card}
:link: https://sharing.awesome-panel.org/MarcSkovMadsen/portfolio-analysis2/app.html
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233766742-8ba1208e-bb16-428c-ad51-6807e793aa3e.png
---
alt: Portfolio Analysis App
---
```
:::

:::{grid-item-card}
:link: https://panel-gallery-dev.pyviz.demo.anaconda.com/penguin_crossfilter
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233767039-86f59454-60d5-46be-ac0f-c96d07b5ec8a.png
---
alt: Palmer Penguins App
---
```
:::

::::

## Description

Panel is a an [open-source](https://github.com/holoviz/panel/blob/main/LICENSE.txt) Python library that **makes it easy to create interactive dashboards and data apps using the tools you already know and love**.

With Panel, you can quickly prototype and iterate on apps and dashboards using your favorite editor or notebook environment. Unlike other tools, Panel supports a wide range of visualization libraries and development environments, which means **you can choose the tools that work best for your workflow**.

One of the most powerful features of Panel is its ability to handle large amounts of data and stream it directly to the frontend of your app. This allows you to build highly interactive and responsive apps that can handle real-time data updates with ease. Panel also provides deep bi-directional interactivity between the frontend and backend, which means **you can build interactive data apps that respond to user input in real-time**.

But what sets Panel apart from its competitors is its ability to build more complex applications. While other tools may have limited capabilities for building complex applications, Panel provides a number of advanced features that make it a unique and powerful tool for building data apps and dashboards. For example, you can develop server-, pyodide-, pyscript- and pure javascript-backed applications, wrap your applications in polished templates for final deployment, and add authentication to your applications using the built-in OAuth providers. This means that with Panel, **you can build applications that are not only interactive and responsive, but also more complex and powerful**.

Whether you're a domain expert, data scientist, software developer, or anyone in between, Panel provides a flexible and powerful platform for building interactive data apps and dashboards. With its broad range of features and support for multiple visualization libraries and development environments, **Panel is a unique and powerful solution that can help you bring your data to life**.

## Demo App

The demo app demonstrates how we can *bind* widgets to plots. Simply **drag the slider** to see how the app responds to user input in real-time. To see how the app was built, **check out the Code tab**. For a description of the app **check out the Description tab**.

<!-- ```{eval-rst}
.. notebook:: panel ../examples/homepage.ipynb
    :disable_interactivity_warning: True
``` -->

The demo app also demonstrates one of Panels novel features: many types of end products. This app is not running on a backend server. Instead we have exported the app to *static html* and *embedded* it in this web page. [Rapids](https://rapids.ai/) uses this technology to power their interactive [Visualization Guide](https://docs.rapids.ai/visualization). In fact Rapids has built their big data, gpu powered visualization framework [cuxfilter](https://github.com/rapidsai/cuxfilter) on top of Panel and the HoloViz ecosystem.

## Learning Resources

The demo app above is just a small example of what you can do with Panel. Whether you're building a simple dashboard or a complex data app, Panel makes it easy to create powerful and interactive user interfaces using the tools you already know and love. So why not give it a try and see what you can build with Panel today?

::::{grid} 1 2 2 4
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`rocket;2.5em;sd-mr-1` Getting Started
:link: getting_started/index
:link-type: doc

The getting started guide will get you set up with Panel and provide a basic overview of the features and strengths of Panel.
:::

:::{grid-item-card} {octicon}`mortar-board;2.5em;sd-mr-1` Explanation
:link: getting_started/core_concept
:link-type: doc

Introduces you to some of the core concepts behind Panel and some of the advanced features that make Panel such a powerful library.
:::

:::{grid-item-card} {octicon}`beaker;2.5em;sd-mr-1` How-to
:link: how_to/index
:link-type: doc

How-to guides provide step by step recipes for solving essential problems and tasks that arise during your work.
:::

:::{grid-item-card} {octicon}`book;2.5em;sd-mr-1` Reference
:link: api/index
:link-type: doc

The Panel API Reference Manual provides a comprehensive reference for all methods and parameters on Panel components.
:::

::::

## HoloViz

Panel is a proud member of the thriving [HoloViz](https://holoviz.org/) data visualization ecosystem, which includes other powerful libraries like [hvPlot](https://hvplot.holoviz.org) (for easy plotting), [HoloViews](https://holoviews.org/) (for advanced plotting), and [Datashader](https://datashader.org/) (for big data visualization).

Built on top of [Param](https://param.holoviz.org), Panel enables you to add parameter ranges, documentation, and dependencies to your code. With this approach, you can develop large, maintainable code bases that can be used in notebooks, data apps, batch processing, or reports, without committing to a specific use case up front.

By leveraging the power of the [HoloViz](https://holoviz.org/) ecosystem, Panel provides a rich and flexible set of tools for building interactive data applications and dashboards, with seamless integration between different libraries and tools.

::::{grid} 1 2 2 4
:gutter: 1 1 1 2

:::{grid-item-card} Easy Plotting
:link: https://hvplot.holoviz.org/
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233769751-40d7fb24-a26e-4f01-8d49-85c4e31c4c1b.png
---
alt: hvPlot Logo
---
```
:::

:::{grid-item-card} Advanced Visualization
:link: https://holoviews.org/
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233769974-0c829d68-7367-4f54-a8cf-fd9b439590a7.png
---
alt: HoloViews Logo
---
```
:::

:::{grid-item-card} Big Data Visualization
:link: https://datashader.org/
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233769976-eaf3c709-2bbb-453b-ab2d-754202a69acc.png
---
alt: Datashader Logo
---
```
:::

:::{grid-item-card} Powerful Parameters
:link: https://param.holoviz.org/
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233769761-83629984-392f-461e-89a2-c2b4ec503587.png
---
alt: Param Logo
---
```
:::

::::

## Featured Resources

Below we include a selection of *featured resources*. For more community resources check out
[awesome-panel.org](https://awesome-panel.org).

### Apps

::::{grid} 2 2 4 4
:gutter: 1

:::{grid-item-card} Portfolio Optimizer
:link: https://panel-gallery-dev.pyviz.demo.anaconda.com/portfolio_optimizer
:link-type: url

```{image} https://assets.holoviz.org/panel/gallery/portfolio_optimizer.png
---
alt: Portfolio Optimizer App
---
```
:::

:::{grid-item-card} OGGM Glaciers
:link: https://panel-gallery-dev.pyviz.demo.anaconda.com/glaciers
:link-type: url

```{image} https://assets.holoviz.org/panel/gallery/glaciers.png
---
alt: OGGM Glaciers App
---
```
:::

:::{grid-item-card} Videostream
:link: https://panel-gallery-dev.pyviz.demo.anaconda.com/streaming_videostream
:link-type: url

```{image} https://assets.holoviz.org/panel/gallery/streaming_videostream.png
---
alt: Streaming Video App
---
```
:::

:::{grid-item-card} MRI Cross-sections
:link: https://panel-gallery-dev.pyviz.demo.anaconda.com/vtkslicer
:link-type: url

```{image} https://assets.holoviz.org/panel/gallery/vtkslicer.png
---
alt: VTK 3D Slicer App
---
```
:::

::::

### Videos

::::{grid} 2 2 4 4
:gutter: 1

:::{grid-item-card} Beautiful Dashboards
:link: https://youtu.be/uhxiXOTKzfs
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233267394-8085c328-f5d8-4be7-8c20-f0a8915215a4.jpg
---
alt: Beautiful Dashboards
---
```
:::

:::{grid-item-card} Interactive Dashboards
:link: https://youtu.be/__QUQg96SFs
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233540794-94a38165-5e8b-4b17-a61d-1a02d7487e64.jpg
---
alt: Interactive Dashboards
---
```
:::

:::{grid-item-card} PDF Chatbot
:link: https://youtu.be/IvEh7A308FU
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233267372-e4937904-80c6-4dfa-adfc-2a0c0fd522b5.jpg
---
alt: Question answering PDF Chatbot
---
```
:::

:::{grid-item-card} HoloViz Introduction
:link: https://youtu.be/8du4NNoOtII
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233540795-61aa8ab4-3555-4c4c-8231-88af10cb897c.jpg
---
alt: HoloViz Introduction
---
```
:::

::::

### Blog Posts

::::{grid} 2 2 4 4
:gutter: 1

:::{grid-item-card}
:link: https://towardsdatascience.com/3-ways-to-build-a-panel-visualization-dashboard-6e14148f529d
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233773978-61ebe585-587f-4bf1-9cf8-c2be2e698a75.png
---
alt: 3 Ways to Build a Panel Visualization Dashboard
---
```
:::

:::{grid-item-card}
:link: https://towardsdatascience.com/how-to-deploy-a-panel-app-to-hugging-face-using-docker-6189e3789718
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233773976-c0baa28f-e4ca-4b8a-afae-8ebcf5dc445b.png
---
alt: How to deploy a Panel app to Hugging Face using Docker
---
```
:::

:::{grid-item-card}
:link: https://medium.com/@marcskovmadsen/i-prefer-to-use-panel-for-my-data-apps-here-is-why-1ff5d2b98e8f
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233773979-7a191548-e878-437c-a392-98ed6bc021a7.png
---
alt: I prefer to use Panel for my data apps. Here is why.
---
```
:::

:::{grid-item-card} HoloViz Blog
:link: https://blog.holoviz.org/
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233773975-99d5727e-7428-4f43-a36d-498bd9dc03f9.png
---
alt: HoloViz Blogs
---
```
:::

::::

### Tweets

::::{grid} 2 2 4 4
:gutter: 1

:::{grid-item-card}
:link: https://twitter.com/underdarkGIS/status/1530981610920755201?s=20
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233767803-255d236e-8ea0-40f7-b510-12a616383b1e.png
---
alt: Moving Pandas - Jupyter Panel Preview testimonial
---
```
:::

:::{grid-item-card}
:link: https://twitter.com/ivanziogeo/status/1593956714717380609?s=20
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233767806-10e31dc7-f790-4d6a-ae75-db8caa6d9554.png
---
alt: Impressive App by Ivan D with link to live app and code
---
```
:::

:::{grid-item-card}
:link: https://twitter.com/mgroverwx/status/1575644730750164992?s=20
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233767812-34df20be-6965-4c3c-82cf-d49b518f2b8a.png
---
alt: Testimonial about how powerful and fun XArray + Panel and HoloViz is.
---
```
:::

:::{grid-item-card}
:link: https://twitter.com/DrRParker/status/1573372839708745728?s=20
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233767821-929e8cb4-86fa-4ae3-a60c-35c71c874e80.png
---
alt: Dr Rob Parker tweets about Weather Station data app built by his student Louis.
---
```
:::

::::

## Useful links

If you need help with using Panel or have technical questions, head over to our [Discourse](https://discourse.holoviz.org/) forum. Our friendly community is always happy to help and provide support.

If you run into any [issues](https://github.com/holoviz/panel/issues) or want to [contribute to the development of Panel](https://help.github.com/articles/about-pull-requests), you can [visit our GitHub site](https://github.com/holoviz/panel). Here you can report bugs, suggest new features, or contribute to help improve Panel for everyone.

To connect with other members of the community, you can also [join our Discord chat](https://discord.gg/rb6gPXbdAr). Here you can share ideas, ask for advice, or just chat with other Panel users.

Stay up-to-date on the latest Panel news by following us on [Twitter](https://twitter.com/Panel_org) and [LinkedIn](https://www.linkedin.com/company/panel-org).

If you're looking for a hosted Python environment that works with Panel, we recommend trying out [Panelite](https://panelite.holoviz.org/) or the [Panelite Repl](https://panelite.holoviz.org/repl/). These are pre-configured environments that make it easy to get started with Panel right away. Alternatively, you can use [Binder](https://mybinder.org/v2/gh/holoviz/panel/v0.14.4?urlpath=lab/tree/examples) to launch a Jupyter notebook environment with Panel pre-installed, no setup required.

The Panel community is fantastic. We want it to stay that way. You can find our *Code of Conduct* [here](https://github.com/holoviz/panel/blob/main/CODE_OF_CONDUCT.md).

We hope these links are helpful and that you'll join us in the Panel community soon!

## Contributing

Panel is developed and maintained via community contributions. The easiest way to contribute is to [give a &#11088; on Github](https://github.com/holoviz/panel) or [show some &#10084;&#65039; on social media](https://twitter.com/intent/tweet).

Check out our [Contributing Guide](https://github.com/holoviz/panel/blob/main/CONTRIBUTING.MD) to get started. Thanks.

## Sponsors

The Panel project is grateful for the sponsorship by the organizations and companies below:

::::{grid} 2 2 4 4

:::{grid-item-card}
:link: https://www.anaconda.com/
:link-type: url

```{image} https://static.bokeh.org/sponsor/anaconda.png
---
alt: Anaconda Logo
---
```
:::


:::{grid-item-card}
:link: https://www.blackstone.com/the-firm/
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233770865-721d1074-4471-4b50-9a27-f39841306911.png
---
alt: Blackstone Logo
---
```
:::

:::{grid-item-card}
:link: https://numfocus.org/
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233770863-da493e3b-6368-4b00-818e-cbcbdd44fb72.png
---
alt: NumFOCUS Logo
---
```
:::

:::{grid-item-card}
:link: https://quansight.com/
:link-type: url

```{image} https://assets.holoviz.org/logos/Quansight-logo.svg
---
alt: Quansight Logo
---
```
:::

::::


```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2
:caption: FOR USERS

getting_started/index
how_to/index
gallery/index
background/index
reference/index
api/index
FAQ
about/index
```

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2
:caption: FOR DEVELOPERS

developer_guide/index
```
