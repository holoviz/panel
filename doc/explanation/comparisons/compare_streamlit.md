# Comparing Panel and Streamlit

![Panel Layout Example](https://user-images.githubusercontent.com/42288570/243362603-45ba78a4-d67b-43bc-b3c2-386105fe6ed8.png)

**Streamlit is an alternative** to Panel, Jupyter, Bokeh, and Dash. Like Jupyter, Streamlit provides an interactive, incremental way to build apps. Streamlit works with Python text files written in a separate editor, while Jupyter uses a web-based notebook cell editor. Although a web-based editor simplifies working locally on remote files, using a local Python text file enables users to maximize productivity by choosing their preferred editor. Dash, Panel, and Bokeh also support bare Python files developed in a local editor. Similarly, like Streamlit, they all watch that file and automatically re-run it when changes occur in the editor (e.g., for Panel, launch `panel serve --show --autoreload file.py` to watch the Python file and re-launch the served app on any changes).

A key difference with Streamlit is that **the entire Python source file is effectively re-run *every time a widget changes value***, preventing confusing out-of-order execution of notebook cells and simplifying reasoning about state. However, this approach necessitates making all lengthy computations cacheable, which is not always straightforward and can introduce complexities in state management. Moreover, similar to Dash's lack of server-side state, Streamlit's approach can make it challenging to generate responsive apps for complex situations requiring a precise mapping between a widget event and specific Python code. In contrast, Panel offers better support for fully reactive applications, where each widget or plot component is explicitly tied to computation, re-running only the necessary code for that action. Consequently, Panel can support larger, more complex applications, allowing specific behaviors to be implemented and delivered independently.

Another significant difference is that **Panel fully supports Jupyter notebooks, unlike Streamlit**, enabling users to preserve a series of text/code/output steps as an exploratory record. This capability is valuable for documenting workflows for reproducibility, storytelling with data, or any approach where individual outputs per cell are useful. Panel eliminates the need to switch between "exploring data" or "telling a story" and "developing an app," allowing users to use widgets and layouts whenever they are useful or appropriate without incurring a cost to switch activities. While Panel does not require Jupyter, its full support extends its usability to various situations for which Streamlit is not designed.

Another key distinction between Streamlit and Panel is the organization of the developer community. Streamlit is run and owned by [Snowflake](https://www.snowflake.com), while Panel was developed at [Anaconda](https://www.anaconda.com) without being conceived as a product. This difference means that Panel does not have the same commercial incentives. As a consequence, you **won't** have to [provide your email or opt out of telemetry data collection](https://github.com/streamlit/streamlit/issues/4747). We have never collected or had plans to collect telemetry data from our users' apps. Furthermore, we would not [ask for access to your private GitHub accounts for deployment](https://github.com/streamlit/streamlit/issues/4344) if we offered free deployment, as it contradicts our core values.

Overall, **Panel can be used in a much wider range of applications than Streamlit**, including exploratory data analysis and capturing a reproducible workflow in a Jupyter notebook, developing a simple Streamlit-like app, or creating complex, multi-page responsive apps, all without the need to switch frameworks or learn new tools. **Panel supports the entire life cycle of data science, engineering, or scientific artifacts, rather than merely the task of developing a specific type of simple app**.

## Streamlit's Limitations

These videos from a dedicated Streamlit fan walk you through some of Streamlit's fundamental limitations.

<iframe width="560" height="315" src="https://www.youtube.com/embed/QiiwEAz6BVY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<iframe width="560" height="315" src="https://www.youtube.com/embed/IOYHVPPbZII?si=GwV4muZWYAB94GDo" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## Code Examples

If you want to compare examples with code, check out the [How to Migrate From Streamlit Guide](../../how_to/streamlit_migration/index).
