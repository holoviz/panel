# Comparing Panel and Bokeh

Panel and Bokeh can both be used to create dashboards and applications in Python, but are intended for different uses and different audiences:

- Panel is based on the internal layout and server components of Bokeh, while adding full bidirectional communication support for usage in Jupyter, making the same code fully usable in both notebook and server contexts so that it need not be rewritten for different purposes.

- Panel does not depend on any of Bokeh's plotting, and it can be used equally well with plots from a very wide variety of sources. To use such plots with Bokeh directly would require significant custom coding.

- Bokeh focuses on providing lower-level primitives that can be used to create any dashboard with enough effort, while Panel focuses on making common data-science tasks and making typical types of apps easier, while still allowing users to drop down to Bokeh or JavaScript code when needed for specific purposes.

So while Panel builds on Bokeh and has full support for Bokeh-based plotting, it is also an alternative to using Bokeh directly to build an app. Panel makes it simpler to build ambitious apps by providing a wide array of reusable components that can easily be combined together in Jupyter or in standalone applications.
