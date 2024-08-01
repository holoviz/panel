# Comparing Panel and Dash

Panel and Dash can both be used to create dashboards in Python, but take very different approaches:

- Panel provides full, seamless support for usage in Jupyter notebooks, making it simple to add controls and layouts wherever they are needed in a workflow, without necessarily building up to any particular shareable app. Dash is focused almost exclusively on standalone dashboards, though there are some workarounds available for using Dash in notebooks.

- Panel focuses on helping Python users create apps and dashboards using Python, with a concise and expressive Pythonic syntax. Dash reveals more of the underlying HTML and CSS details, which is useful for customization but can be distracting during the data-exploration phase of a project and leads to apps that require extensive knowledge beyond Python to extend and maintain.

- Panel is plotting-library agnostic, fully supporting a wide range of Python libraries out of the box, including Plotly. Dash has full support for Plotly but only limited support for other plotting libraries, using separate extension packages.

- Dash dashboards store all of their per-user session state in the client (i.e., the browser), while Panel allows per-user, per-session state in both the server and the client, synchronizing between the two if needed. This difference has important implications:

  * Dash's approach is more highly scalable in some cases, allowing many simultaneous client sessions without necessarily using up resources on the server for each new client.

  * Panel's approach makes it easy to do server-side caching of intermediate computations for each user, which can make complex processing pipelines much more responsive. For instance, when used with a Datashader pipeline where the server renders an image from data that is never transmitted to the client, only the stages that have actually changed need to be re-run when a user interacts with the plot, making rendering changes like selecting a colormap almost instantaneous because the already aggregated data can be reused. With Dash, the server does not retain a copy of the intermediate data in such a pipeline, so when a new request comes in, it has to recompute each of the stages even when the data involved has not changed.  The [Datashader example dashboard](https://examples.pyviz.org/datashader_dashboard/dashboard.html) shows how to use this intermediate-value caching to provide the fastest possible updates for a given user action, only re-running the computation actually needed to satisfy the request, re-using cached values stored on the server when appropriate.
