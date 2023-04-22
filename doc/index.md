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
:link: https://panel-gallery-dev.pyviz.demo.anaconda.com/portfolio_analysis
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233706888-85211d1b-c157-47ed-981b-e5e8816d2a46.png
---
alt: Portfolio Analysis App
---
```
:::

:::{grid-item-card}
:link: https://panel-gallery-dev.pyviz.demo.anaconda.com/penguin_crossfilter
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233760082-c08771cb-b6bc-48de-93cb-b348fc8b2861.png
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

But what sets Panel apart from its competitors is its ability to build more complex applications. While other tools may have limited capabilities for building complex applications, Panel provides a number of advanced features that make it a unique and powerful tool for building data apps and dashboards. For example, you can develop server-, pyodide-, and pyscript-backed applications, wrap your applications in polished templates for final deployment, and add authentication to your applications using the built-in OAuth providers. This means that with Panel, **you can build applications that are not only interactive and responsive, but also more complex and powerful**.

Whether you're a domain expert, data scientist, software developer, or anyone in between, Panel provides a flexible and powerful platform for building interactive data apps and dashboards. With its broad range of features and support for multiple visualization libraries and development environments, **Panel is a unique and powerful solution that can help you bring your data to life**.

## Demo App

The demo app below applies **[k-means clustering](https://en.wikipedia.org/wiki/K-means_clustering) on the [Palmer Penguins dataset](https://github.com/mcnakhaee/palmerpenguins)** using [scikit-learn](https://scikit-learn.org), parameterizing the number of clusters and the variables to plot. Each cluster is denoted by one color while the penguin species is indicated using markers. By comparing the two we can assess the performance of the clustering algorithm.

<!-- ```{eval-rst}
.. notebook:: panel ../examples/homepage.ipynb
    :disable_interactivity_warning: True
``` -->

Simply **drag the slider** to see how the app responds to user input in real-time. To see how the app was built, check out the *Code tab*.

## Usage

The demo app above is just a small example of what you can do with Panel. Whether you're building a simple dashboard or a complex data app, Panel makes it easy to create powerful and interactive user interfaces using the tools you already know and love. So why not give it a try and see what you can build with Panel today?

::::{grid} 1 2 2 4
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`rocket;2.5em;sd-mr-1` Core Concepts
:link: getting_started/core_concepts
:link-type: doc

Introduces you to some of the core concepts behind Panel, how to develop Panel applications effectively both in your IDE and in the notebook and some of the core features that make Panel such a powerful library.
:::

:::{grid-item-card} {octicon}`plug;2.5em;sd-mr-1` Installation
:link: getting_started/installation
:link-type: doc

Walks you through setting up your Python environment, installing Panel into it and how to configure your editor, IDE or notebook environment appropriately.
:::

:::{grid-item-card} {octicon}`tools;2.5em;sd-mr-1` Build an app
:link: getting_started/build_app
:link-type: doc

A more hands on tour taking you through the process of loading some data, displaying it and then building an application around it with some of the rich features that Panel supports.
:::

:::{grid-item-card} {octicon}`book;2.5em;sd-mr-1` How-to
:link: how_to/index
:link-type: doc

How-to guides provide step by step recipes for solving essential problems and tasks that arise during your work.
:::

::::

## HoloViz

Panel is a proud member of the thriving [HoloViz](https://holoviz.org/) data visualization ecosystem, which includes other powerful libraries like [hvPlot](https://hvplot.holoviz.org) (for easy plotting), [HoloViews](https://holoviews.org/) (for advanced plotting), and [Datashader](https://datashader.org/) (for big data visualization).

Built on top of [Param](https://param.holoviz.org), Panel enables you to add parameter ranges, documentation, and dependencies to your code. With this approach, you can develop large, maintainable code bases that can be used in notebooks, data apps, batch processing, or reports, without committing to a specific use case up front.

By leveraging the power of the [HoloViz](https://holoviz.org/) ecosystem, Panel provides a rich and flexible set of tools for building interactive data applications and dashboards, with seamless integration between different libraries and tools.

## Featured Resources

### Apps

::::{grid} 2 2 4 4
:gutter: 1

:::{grid-item-card} Videostream
:link: https://panel-gallery-dev.pyviz.demo.anaconda.com/streaming_videostream
:link-type: url

```{image} https://assets.holoviz.org/panel/gallery/streaming_videostream.png
```
:::

:::{grid-item-card} MRI Cross-sections
:link: https://panel-gallery-dev.pyviz.demo.anaconda.com/vtkslicer
:link-type: url

```{image} https://assets.holoviz.org/panel/gallery/vtkslicer.png
```
:::

:::{grid-item-card} OGGM Glaciers
:link: https://panel-gallery-dev.pyviz.demo.anaconda.com/glaciers
:link-type: url

```{image} https://assets.holoviz.org/panel/gallery/glaciers.png
```
:::

:::{grid-item-card} Portfolio Optimizer
:link: https://panel-gallery-dev.pyviz.demo.anaconda.com/portfolio_optimizer
:link-type: url

```{image} https://assets.holoviz.org/panel/gallery/portfolio_optimizer.png
```
:::

::::

### Videos

::::{grid} 2 2 4 4
:gutter: 1

:::{grid-item-card} Beautiful Dashboard
:link: https://youtu.be/uhxiXOTKzfs
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233267394-8085c328-f5d8-4be7-8c20-f0a8915215a4.jpg
```
:::

:::{grid-item-card} Interactive Dashboard
:link: https://youtu.be/__QUQg96SFs
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233540794-94a38165-5e8b-4b17-a61d-1a02d7487e64.jpg
```
:::

:::{grid-item-card} PDF Chatbot
:link: https://youtu.be/IvEh7A308FU
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233267372-e4937904-80c6-4dfa-adfc-2a0c0fd522b5.jpg
```
:::

:::{grid-item-card} HoloViz Introduction
:link: https://youtu.be/8du4NNoOtII
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233540795-61aa8ab4-3555-4c4c-8231-88af10cb897c.jpg
```
:::

::::

## Tweets

::::{grid} 2 2 4 4
:gutter: 1

:::{grid-item-card}
:link: https://twitter.com/underdarkGIS/status/1530981610920755201?s=20
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233758610-14f6d096-3e66-4a1d-973b-fed02e95b9bb.png
```
:::

:::{grid-item-card}
:link: https://twitter.com/ivanziogeo/status/1593956714717380609?s=20
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233758478-bc95b0ed-768a-4efc-9c77-49b01eecfe5c.png
```
:::

:::{grid-item-card}
:link: https://twitter.com/mgroverwx/status/1575644730750164992?s=20
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233758817-640ca94b-9838-4721-bd0f-47ff43c75813.png
```
:::

:::{grid-item-card}
:link: https://twitter.com/DrRParker/status/1573372839708745728?s=20
:link-type: url

```{image} https://user-images.githubusercontent.com/42288570/233758821-b3570fe7-9d4a-481c-8786-64e0862e4bab.png
```
:::

::::

## Useful links

If you need help with using Panel or have technical questions, head over to our [Discourse](https://discourse.holoviz.org/) forum. Our friendly community is always happy to help and provide support.

If you run into any [issues](https://github.com/holoviz/panel/issues) or want to [contribute to the development of Panel](https://help.github.com/articles/about-pull-requests), you can [visit our GitHub site](https://github.com/holoviz/panel). Here you can report bugs, suggest new features, or contribute to help improve Panel for everyone.

To connect with other members of the community, you can also [join our Discord chat](https://discord.gg/rb6gPXbdAr). Here you can share ideas, ask for advice, or just chat with other Panel users.

Stay up-to-date on the latest Panel news by following us on [Twitter](https://twitter.com/Panel_org) and [LinkedIn](https://www.linkedin.com/company/panel-org).

If you're looking for a hosted Python environment that works with Panel, we recommend trying out [Panelite](https://panelite.holoviz.org/) or the [Panelite Repl](https://panelite.holoviz.org/repl/). These are pre-configured environments that make it easy to get started with Panel right away. Alternatively, you can use [Binder](https://mybinder.org/v2/gh/holoviz/panel/v0.14.4?urlpath=lab/tree/examples) to launch a Jupyter notebook environment with Panel pre-installed, no setup required.

We hope these links are helpful and that you'll join us in the Panel community soon!

## Sponsors

The Panel project is grateful for the sponsorship by the organizations and companies below:

::::{grid} 2

:::{grid-item-card}
:class-body: sponsor-logo
:link: https://www.anaconda.com/
:link-type: url
:text-align: center
:columns: 3

```{image} https://static.bokeh.org/sponsor/anaconda.png
---
alt: Anaconda Logo
---
```
:::


:::{grid-item-card}
:class-body: sponsor-logo
:link: https://www.blackstone.com/the-firm/
:link-type: url
:text-align: center
:columns: 3

```{image} https://static.bokeh.org/sponsor/blackstone.png
---
alt: Blackstone Logo
---
```
:::

:::{grid-item-card}
:class-body: sponsor-logo
:link: https://numfocus.org/
:link-type: url
:text-align: center
:columns: 3

```{image} https://numfocus.org/wp-content/uploads/2017/03/numfocusweblogo_orig-1.png
---
alt: NumFOCUS Logo
---
```
:::

:::{grid-item-card}
:class-body: sponsor-logo
:link: https://quansight.com/
:link-type: url
:text-align: center
:columns: 3

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
