# Improve the Performance

There are a number of common bottlenecks and pitfalls that can significantly reduce the performance of your applications and some approaches to improve the performance of your application. This section provides various approaches to try to improve the performance of your applications.

::::{grid} 1 2 2 2
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`versions;2.5em;sd-mr-1 sd-animate-grow50` Reuse sessions
:link: reuse_sessions
:link-type: doc

Discover how to reuse sessions to improve the start render time.
:::

:::{grid-item-card} {octicon}`tab;2.5em;sd-mr-1 sd-animate-grow50` Enable throttling
:link: throttling
:link-type: doc

Discover how to enable throttling to reduce the number of events being processed.
:::

:::{grid-item-card} {octicon}`tab;2.5em;sd-mr-1 sd-animate-grow50` Batching Updates with `hold`
:link: hold
:link-type: doc

Discover how to improve performance by using the `hold` context manager and decorator to batch updates to multiple components.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

reuse_sessions
throttling
hold
```
