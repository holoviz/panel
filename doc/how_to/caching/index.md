# Caching

Caching data and computation is one of the most effective ways to speed up your applications. Some common examples of scenarios that benefit from caching is working with large datasets that you have to load from disk or over a network connection or you have to perform expensive computations that don't depend on any extraneous state. Panel makes it easy for you to add caching to you applications using a few approaches. Panel' architecture is also very well suited towards caching since multiple user sessions can run in the same process and therefore have access to the same global state. This means that we can cache data in Panel's global `state` object, either by directly assigning to the `pn.state.cache` dictionary object, using the `pn.state.as_cached` helper function or the `pn.cache` decorator. Once cached all current and subsequent sessions will be sped up by having access to the cache.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` Manual Caching
:link: manual
:link-type: doc

How to manually cache data and objects on `pn.state.cache`.
:::

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` Memoization
:link: memoization
:link-type: doc

How to use the `panel.cache` decorator to memoize (i.e. cache the output of) functions automatically.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

manual
memoization
```