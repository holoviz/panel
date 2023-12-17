# Comparing Panel and Streamlit

![Panel Layout Example](https://user-images.githubusercontent.com/42288570/243362603-45ba78a4-d67b-43bc-b3c2-386105fe6ed8.png)

**Streamlit is an alternative** to Panel, Jupyter, Bokeh, and Dash. Like Jupyter, Streamlit provides an interactive, incremental way to build apps. Streamlit works with Python text files written in a separate editor, while Jupyter uses a web-based notebook cell editor. Although a web-based editor makes it simple to work locally on remote files, using a local Python text file allows users to maximize their productivity by choosing their own favorite editor. Dash, Panel, and Bokeh all also support bare Python files developed in a local editor, and like Streamlit they can all also watch that file and automatically re-run the file when you change it in the editor (e.g. for Panel, launch ``panel serve --show --autoreload file.py`` to watch the Python file and re-launch the served app on any changes).

Streamlit's key difference from those other tools is that **with Streamlit, the entire Python source file is effectively re-run *every time a widget changes value***, which has the advantage of not allowing confusing out-of-order execution of notebook cells, and also can make it simpler to reason about state in general. However, for this approach to be practical, it requires all lengthy computations to be made cacheable, which is not always straightforward and can introduce its own highly complicated reasoning about state. Moreover, the Streamlit approach has similar downsides as for Dash's lack of server-side state, in that it becomes difficult to generate responsive apps for complex situations that need a precise mapping between a widget event and a specific small bit of Python code. Panel thus has better support for fully reactive applications, where each widget or component of a plot is explicitly and specifically tied to a bit of computation, re-running only the tiniest bit of code that is needed for that particular action. In this way Panel can support much larger, more complex applications when needed, allowing specific behaviors to be implemented and delivered independently rather than only as part of a tightly connected, monolithic script.

Another major difference is that **Panel, in contrast to Streamlit, fully supports Jupyter notebooks**, for when you wish to preserve a series of text/code/output steps as an exploratory record, whether to document a workflow for later reproducibility, to tell a story about data, or for any other approach where having individual outputs per cell is useful. Thus Panel does not require you to make a binary switch between "exploring some data" or "telling a story" and "developing an app"; it simply lets you use widgets and layouts whenever they are useful or appropriate, without ever having a cost to switch between such activities. Of course, Panel does not *require* Jupyter, but because it supports Jupyter fully it is usable in a wide range of situations for which Streamlit is not designed.

One more key difference between Streamlit and Panel is the organization of the developer community. Streamlit is run and owned by Snowflake, while Panel was developed at Anaconda and was not developed as a product. This difference means that Panel does not have many of the same commercial incentives. As a consequence you **won't** have to provide your email or opt out of telemetry data collection. We have never collected or had plans to collect telemetry data from our users apps.

Overall, **Panel can be used in a much wider range of applications than Streamlit**, including exploratory data analysis and capturing a reproducible workflow in a Jupyter notebook, developing a simple Streamlit-like app, or developing complex, multi-page responsive apps, all without having to switch frameworks or learn a new set of tools. **Panel supports the entire life cycle of data science, engineering, or scientific artifacts, not just a narrow task of developing a specific type of simple app**.

## Streamlits limitations

[This video](https://youtu.be/QiiwEAz6BVY) from a die hard Streamlit fan takes *an unfiltered deep dive into Streamlit's limitations*. The Streamlit community lives happily with these *dead ends*. They
might not even be aware or limited by them. The Panel contributors on the other hand could not
imagine working with a limiting framework like that. They need other features, more flexibility,
higher performance and a fundamentally different architecture to support their use cases.

<iframe width="560" height="315" src="https://www.youtube.com/embed/QiiwEAz6BVY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

We don't think Streamlit sucks as the ironic title of the video thumbnail suggests. There are many enthusiastic Streamlits users that have been enabled by Streamlit to solve their problems. It's created the *data app* genre, its inspired lots of data app innovation and still stands out as one of the benchmark data app frameworks to measure up against.

## Code Examples

If you want to compare examples with code, check out the [How to Migrate From Streamlit Guide](../../how_to/streamlit_migration/index.md).
