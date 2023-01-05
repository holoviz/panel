# Optimize Layouts

Panel is built on the Bokeh library which was originally written as a plotting library but grew into a more general framework for building data apps and dashboards. This history shows up in some architectural decisions and the main one is the way layouts are handled by Bokeh. Instead of relying on CSS to configure and compute the layouts Bokeh (and therefore Panel) rely on a layout engine which computes the sizes of different components to apply fixed positioning on the page. This works well but is an expensive operation and scales imperfectly the more components are added to a layout. In future, i.e. with the upcoming Bokeh 3.0 and Panel 1.0 releases the layout engine will be replaced with a CSS based framework. Until that time there are a few tricks to apply to avoid the layout engine degrading the performance of your application:

The main approach to avoid bogging down the layout engine is to leverage [Templates](./Templates.ipynb) and add components as separate "roots" to the page. This means that instead of adding components to a layout like this:

```python
pn.Column(a, b, c, ...)
```

You add them as separate roots to the template:

```python
template = pn.template.BootstrapTemplate()

template.main.append(a)
template.main.append(b)
template.main.append(c)
```

Doing this will ensure that the Bokeh.js layout engine considers each component separately and will speed up rendering a lot if `a`, `b` and `c` are deeply nested components.
