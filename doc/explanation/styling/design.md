# Designs and Theming

:::{versionadded} 1.0.0
Designs and theming allow controlling the look and feel of individual components or your entire application. Before version 1.0 the concept of a design and a template were combined but since it is now possible to apply a `Design` separately from a template.
:::

## `Design` class

The `Design` class has the ability to apply styling and theming to components via three mechanisms:

1. Loading external JS and CSS `resources`.
2. Applying `modifiers` that directly override (or combine with) component parameter settings (including CSS stylesheets).

Additionally a `Design` class always has an associated `Theme` which determines the color palette of the design. This also has the ability to:

1. Apply a `base_css` (usually containing CSS variable definitions and inherited from the base class).
2. Apply a `bokeh_theme` to override Bokeh component styling.
3. Apply a `css` with specific CSS overrides for that theme.
4. Apply its own set of `modifiers`.

### Example: Bootstrap

Let us work through the definition of the `Bootstrap` design step-by-step.

#### Resources

First of all, the `Bootstrap` design defines CSS and JS `resources` which load the bootstrap5 library:

```python
    _resources = {
        'css': {
            'bootstrap': CSS_URLS['bootstrap5']
        },
        'js': {
            'bootstrap': JS_URLS['bootstrap5']
        }
    }
```

#### Modifiers

Next we get to the `modifiers` which is where the meat of the styling definition lives. Modifiers are applied per class and override the default parameter settings of a component. We can apply modifiers to a base class such as `Viewable`, which will affect all components or we can override a specific class, e.g. `Tabulator`:

```python
    modifiers = {
        Accordion: {
            'active_header_background': 'var(--bs-surface-bg)'
        }
		...
        Tabulator: {
            'theme': 'bootstrap4'
        },
        Viewable: {
            'stylesheets': [Inherit, f'{CDN_DIST}bundled/theme/bootstrap.css']
        }
    }
```

Here we define specific parameters to override or combine with, e.g. we set the `active_header_background` of an `Accordion` to inherit from the `--bs-surface-bg` CSS variable. In this way we can control settings that are not controlled by CSS. However, most crucially we also declare that all `Viewable` components should inherit a bundled stylesheet: `bundled/theme/bootstrap.css`.

The `bootstrap.css` file includes styling overrides for many different components and will be loaded by all `Viewable` components.

#### CSS stylesheets

All design stylesheets open with CSS variable definitions which map the global color definitions to specific variables used by a particular design system:

```css
:host, :root {
    --bs-primary-color: var(--jp-ui-font-color0, var(--panel-on-primary-color));
    --bs-primary-bg: var(--jp-brand-color0, var(--panel-primary-color));
}
```

The `:host` and `:root` selectors ensure that these variable definition apply inside the shadow DOM, i.e. that they apply to the shadow `host`, and globally to the document `root` (i.e. usually the `<html>` element).

Note also how we map the `--bs-primary-color` color to two other variables, first the `--jp-ui-font-color0`, which allows us to automatically inherit styles in Jupyter based environments and secondly the `--panel-on-primary-color` which is the primary definition of Panel color themes and also the entrypoint for users to override the color definitions.

Once declared these CSS variables are then used to set the style of specific components:

```css
.bk-menu {
    background-color: var(--bs-form-control-bg);
    color: var(--bs-form-control-color);
}
```

In this way global style definitions and variables can flow down all the way to individual components.

#### Themes

Lastly we get to the themes, each `Design` component declares the set of supported themes by name:

```python
    _themes = {
        'dark': BootstrapDarkTheme,
        'default': BootstrapDefaultTheme,
    }
```

Currently only `default` (light) and `dark` themes are supported. The implementation of these themes subclasses from the `DefaultTheme` and `DarkTheme` base classes and applies specific overrides.

## Developing an internal theme

If you want to help contribute improvements to a `Design` or `Theme` simply edit the CSS definitions in `panel/theme/css` and periodically re-bundle the resources with:

```bash
panel bundle --themes --only-local
```

On UNIX you can simply use `watch -n 5 panel bundle --themes --only-local` to re-bundle these resources every few seconds.
