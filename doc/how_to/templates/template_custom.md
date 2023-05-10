# Build a Custom Template

This guide addresses how to build a custom template.

```{admonition} Prerequisites
1. The [How to > Set a Template](./template_set.md) guide demonstrates how to set a template for a deployable app.
2. The [How to > Customize Template Theme](./template_theme.md) guide addresses how to customize the theme of a template, which may be sufficient in many cases.
```

---

## Build a Template in a Single File

Completely custom templates extend the default [Jinja2](https://palletsprojects.com/p/jinja/) template in various ways. Before we dive into modifying such a template, let us take a look at the default template used by Panel:

```html
{% from macros import embed %}

<!DOCTYPE html>
<html lang="en">
{% block head %}
<head>
    {% block inner_head %}
    <meta charset="utf-8">
    <title>{% block title %}{{ title | e if title else "Panel App" }}{% endblock %}</title>
    {% block preamble %}{% endblock %}
    {% block resources %}
        {% block css_resources %}
        {{ bokeh_css | indent(8) if bokeh_css }}
        {% endblock %}
        {% block js_resources %}
        {{ bokeh_js | indent(8) if bokeh_js }}
        {% endblock %}
    {% endblock %}
    {% block postamble %}{% endblock %}
    {% endblock %}
</head>
{% endblock %}
{% block body %}
<body>
    {% block inner_body %}
    {% block contents %}
        {% for doc in docs %}
        {{ embed(doc) if doc.elementid }}
        {% for root in doc.roots %}
            {{ embed(root) | indent(10) }}
        {% endfor %}
        {% endfor %}
    {% endblock %}
    {{ plot_script | indent(8) }}
    {% endblock %}
</body>
{% endblock %}
</html>
```

As you may be able to note if you are familiar with jinja2 templating or similar languages, this template can easily be extended by overriding the existing `{% block ... %}` definitions. However it is also possible to completely override this default template instead.

That said it is usually easiest to simply extend an existing template by overriding certain blocks. To begin with we start by using `{% extends base %}` to declare that we are merely extending an existing template rather than defining a whole new one; otherwise we would have to repeat the entire header sections of the full template to ensure all the appropriate resources are loaded.

In this case we will extend the postamble block of the header to load some additional resources, and the contents block to redefine how the components will be laid out. Specifically, we will load bootstrap.css in the preamble allowing us to use the bootstrap grid system to lay out the output.

```python
template = """
{% extends base %}

<!-- goes in head -->
{% block postamble %}
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
{% endblock %}

<!-- goes in body -->
{% block contents %}
{{ app_title }}
<p>This is a Panel app with a custom template allowing us to compose multiple Panel objects into a single HTML document.</p>
<br>
<div class="container">
  <div class="row">
    <div class="col-sm">
      {{ embed(roots.A) }}
    </div>
    <div class="col-sm">
      {{ embed(roots.B) }}
    </div>
  </div>
</div>
{% endblock %}
"""
```

If you look closely we defined two different roots in the template using the `embed` macro. In order to be able to render the template we now have to first construct the `pn.Template` object with the template HTML and then populate the template with the two required roots, in this case `'A'` and `'B'` by using the `add_panel` method. If either of the roots is not defined the app is invalid and will fail to launch. The app will also fail to launch if any panels are added that are not referenced in the template.

Additionally we have also declared a new `app_title` variable in the template, which we can populate by using the `add_variable` method:

```python
import panel as pn
import holoviews as hv

tmpl = pn.Template(template)

tmpl.add_variable('app_title', '<h1>Custom Template App</h1>')

tmpl.add_panel('A', hv.Curve([1, 2, 3]))
tmpl.add_panel('B', hv.Curve([1, 2, 3]))

```

Embedding a different CSS framework (like Bootstrap) in the notebook can have undesirable side-effects so a `Template` may also be given a separate `nb_template` that will be used when rendering inside the notebook:

```python
import panel as pn
import holoviews as hv
pn.extension() # for notebook

nb_template = """
{% extends base %}

{% block contents %}
{{ app_title }}
<p>This is a Panel app with a custom template allowing us to compose multiple Panel objects into a single HTML document.</p>
<br>
<div style="display:table; width: 100%">
  <div style="display:table-cell; margin: auto">
    {{ embed(roots.A) }}
  </div>
  <div style="display:table-cell; margin: auto">
    {{ embed(roots.B) }}
  </div>
</div>
{% endblock %}
"""

tmpl = pn.Template(template, nb_template=nb_template)

tmpl.add_variable('app_title', '<h1>Custom Template App</h1>')

tmpl.add_panel('A', hv.Curve([1, 2, 3]))
tmpl.add_panel('B', hv.Curve([1, 2, 3]))

```

## Load Template from a Separate File

If the template is larger it is often cleaner to define it in a separate file. You can either read it in as a string, or use the official loading mechanism available for Jinja2 templates by defining a `Environment` along with a `loader`.

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('.'))
jinja_template = env.get_template('sample_template.html')

tmpl = pn.Template(jinja_template)

tmpl.add_panel('A', hv.Curve([1, 2, 3]))
tmpl.add_panel('B', hv.Curve([1, 2, 3]))
tmpl.servable()
```

## Related Resources

- See [How-to > Apply Templates > Customize Template Theme](./template_theme.md) to just use a custom theme.
- See [How-to > Apply Templates > Set a Template](./template_set.md) for alternate approaches to set a template.
- Read [Explanation > Templates](../../explanation/templates/templates_overview.md) for explanation.
