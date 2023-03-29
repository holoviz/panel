# Enable Profiling and Debugging

When trying to understand the performance profiles or track down issues with an application the server logs are rarely sufficient to gain insights. For that reason Panel ships with an admin dashboard that allows tracking resource usage, user behavior, and provides ways of visualizing profiling output to discover bottlenecks in an application.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`meter;2.5em;sd-mr-1 sd-animate-grow50` Enable the admin panel
:link: admin
:link-type: doc

How to enable the admin Panel to begin monitoring resource usage and user behavior.
:::

:::{grid-item-card} {octicon}`codescan;2.5em;sd-mr-1 sd-animate-grow50` Profile your application
:link: profile
:link-type: doc

How to enable profilers like snakeviz or memray to track down bottlenecks in your application.
:::

:::{grid-item-card} {octicon}`note;2.5em;sd-mr-1 sd-animate-grow50` View application logs
:link: logs
:link-type: doc

How to view application logs in the admin dashboard.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

admin
profile
logs
```
