# Cache Data

Caching data and computation is one of the most effective ways to speed up your applications, especially when working with large datasets or performing expensive computations that don't depend on any extraneous state. Panel's architecture is well suited towards caching since multiple user sessions can run in the same process and therefore have access to Panel's global `state` object. These How-to guides address common tasks related to caching.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`squirrel;2.5em;sd-mr-1 sd-animate-grow50` Manually Cache
:link: manual
:link-type: doc

How to manually cache data and objects on `pn.state.cache`.
:::

:::{grid-item-card} {octicon}`dependabot;2.5em;sd-mr-1 sd-animate-grow50` Automatically Cache
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
