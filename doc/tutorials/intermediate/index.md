# Intermediate Tutorials

Welcome to the Intermediate Tutorials!

Ready to take your Panel skills to the next level? Dive into these tutorials to explore advanced features, best practices, and techniques for building robust and scalable apps with Panel. Whether you're aiming for better code organization, improved performance, or exploring additional topics, we've got you covered!

## Prerequisites

Before delving into the intermediate tutorials, ensure you have a solid understanding of Panel basics. If not, refer to our [Basic Tutorial](../basic/index.md) to get started.

Please execute the following command to install the dependencies required by the basic tutorials:

::::{tab-set}

:::{tab-item} pip
:sync: pip

```bash
pip install altair hvplot numpy pandas panel pytest watchfiles
```

:::

:::{tab-item} conda
:sync: conda

```bash
conda install -y -c conda-forge altair hvplot numpy pandas panel pytest watchfiles
```

:::

::::

:::{important}
Is Panel installed together with JupyterLab/Jupyter Notebook in your working environment? If not, you need to make sure that `panel` is also installed in the same environment as JupyterLab/Jupyter Notebook (`pip install panel` or `conda install panel`).
:::

## Mastering Intermediate Panel Techniques

Ready to transition from being a *basic* to an *intermediate* Panel user? Let's uncover techniques for constructing reusable components and structuring your projects with maintainability in mind:

- **[Reactive Parameters](parameters.md):** Discover why Panel is built on top of Reactive Parameters and how to effectively utilize them.
- **[Create Reusable Components](reusable_components.md):** Develop reusable Panel components using the Viewer class.
- **[Advanced Interactivity](interactivity.md):** Harness the power of Parameters and parameter dependencies to infuse interactivity.
- **Introduce Side Effects:** Infuse your apps with additional functionality using `.watch` and `watch=True`.
- **[Structuring with DataStore](structure_data_store.md):** Employ the DataStore pattern to organize larger applications efficiently.
- **Organize your Project:** Maintain orderliness in larger applications by compartmentalizing them into multiple modules and folders.

## Enhancing Performance

Supercharge your app's performance through asynchronous programming, threaded operations, and efficient task scheduling:

- **Schedule Tasks:** Leverage functionalities such as `pn.state.onload`, `pn.state.schedule_task`, `pn.state.add_periodic_callback`, `pn.state.on_session_created`, `pn.state.on_session_destroyed`, `async` generators, and `pn.state.execute`.
- **Concurrent Execution:** Unleash the full potential of Panel by embracing threads and async operations to execute tasks concurrently.

## Exploring Additional Topics

Embark on a deeper exploration of supplementary topics to further hone your Panel development prowess:

- **[Efficient Development in Editors](develop_editor.md):** Streamline the debugging process within your preferred editor environment.
- **[Serving Panel Apps](serve.md):** Serve multi-page apps effortlessly while customizing the Panel server to suit your needs.
- **[Advanced Layouts](advanced_layouts.md):** Attain responsive sizing with ease using FlexBox and media queries.

## Projects

Now that you've mastered the more advanced concepts of Panel, it's time to put your skills to the test:

- **Create an Interactive Report:** Elevate the interactivity of your reports through embedding.
- **[Create a Todo App](build_todo.md):** Create a Todo App using a class based approach.
- **[Test a Todo App](test_todo.md):** Learn how to test a class based Panel app.
- **Serve Apps without a Server:** Explore the realm of WASM to serve your apps without traditional servers.
- **[Build a Server Video Stream](build_server_video_stream.md):** Utilize threading to set up a video stream from a camera connected to a server without blocking the UI.

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

parameters
reusable_components
interactivity
structure_data_store
develop_editor
serve
advanced_layouts
build_todo
test_todo
build_server_video_stream
```
