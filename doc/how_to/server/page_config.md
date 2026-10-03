# Brand the index, login and error pages

Besides your applications, the Panel server renders a few pages of its own: the index page listing the applications, the login and logout pages of the basic auth provider, and the pages shown when authentication fails or a notebook requests a missing kernel. `panel convert` also generates an index page for the converted applications. These pages follow the Material UI styling of `panel.ui`, and you can give them the same theme, logo and title as your applications.

## Reuse your `panel.ui` branding

If your applications are branded by setting class defaults on `panel.ui.Page`, as described in the [panel-material-ui branding guide](https://panel-material-ui.holoviz.org/how_to/apply_branding.html), the server pages can use that configuration directly. Put it in a module and run it once at server startup with `--setup`:

```python
# brand.py
from panel.ui import Page

Page.param.theme_config.default = {
    'light': {
        'palette': {'primary': {'main': '#00695c'}},
        'typography': {'fontFamily': 'Inter, sans-serif'},
        'shape': {'borderRadius': 12},
    },
    'dark': {
        'palette': {
            'primary': {'main': '#00897b'},
            'background': {'default': '#0c1413', 'paper': '#15201e'},
        },
        'typography': {'fontFamily': 'Inter, sans-serif'},
        'shape': {'borderRadius': 12},
    },
}
Page.param.logo.default = 'assets/logo.svg'
Page.param.title.default = 'Acme Analytics'
Page.config.css_files.append(
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap'
)
```

```bash
panel serve apps/*.py --setup brand.py
```

The server pages read the `theme_config`, `logo`, `favicon`, `title` and `site_url` defaults of `Page`, plus the stylesheets in `Page.config.css_files`, so a font loaded for your applications is available to them too. `Page.config.raw_css` is not applied because it targets the elements of a `Page`. The pages only look at `Page` once `panel.ui` has been imported, so the setup script has to import it before any server page is requested.

## Configure the pages directly

To brand the server pages separately, or when your applications do not use `panel.ui`, set `pn.config.page_config` to a dictionary. Its keys mirror the `Page` parameters and take precedence over the `Page` defaults:

`theme_config`
: A Material UI theme, in the same format as the `theme_config` of `panel.ui` components. Like there, a dictionary with `light` and `dark` keys configures each color scheme separately, otherwise it applies to both.

`dark_theme`
: `True` or `False` to force a color scheme. By default the pages follow the color scheme of the operating system, unless `pn.config.theme` is set to `'dark'`.

`logo`
: The logo shown in the app bar, as a URL or the path to a local image file. A dictionary with `light` and `dark` keys provides one logo per color scheme. Local files are embedded into the page, so they do not have to be served as static files.

`title`
: Replaces "Panel" in the app bar and in the browser title of the login and logout pages, and "Panel Applications" on the index page.

`favicon`
: The favicon, as a URL or a local image file.

`site_url`
: The URL the logo and title link to. Without it, the Panel logo on the index page links to the Panel website and the app bar of the other pages has no link.

`css_files`
: A list of stylesheet URLs to load, e.g. for fonts referenced in `theme_config`.

`raw_css`
: A list of CSS strings appended after the page stylesheet.

On the command line the same configuration can be passed to `panel serve` as a JSON string or as the path to a JSON file with `--page-config`. Relative image paths in a JSON file are resolved relative to the file:

```json
{
  "title": "Acme Analytics",
  "logo": {"light": "assets/logo.svg", "dark": "assets/logo_dark.svg"},
  "favicon": "assets/favicon.ico",
  "site_url": "https://acme.example.com",
  "theme_config": {
    "palette": {"primary": {"main": "#00695c"}},
    "shape": {"borderRadius": 12}
  }
}
```

```bash
panel serve apps/*.py --page-config page.json
```

The `PANEL_PAGE_CONFIG` environment variable accepts the same values and overrides the other options, which is useful for the error pages of the Jupyter server extension. When launching the server with `pn.serve`, assign the dictionary before calling it:

```python
import panel as pn

pn.config.page_config = {
    'title': 'Acme Analytics',
    'theme_config': {'palette': {'primary': {'main': '#00695c'}}},
}

pn.serve({'app': create_app, 'other': create_other})
```

## Supported theme options

The server pages are plain HTML rather than Material UI components, so they translate a subset of the theme into CSS variables:

| Theme option | Applies to |
| --- | --- |
| `palette.primary.main`, `dark`, `light`, `contrastText` | App bar, buttons, links and focused inputs. Hover and focus colors and the text color on the app bar are derived from `main` when not given. |
| `palette.error.main`, `palette.success.main` | The error alert and badges, and the badge on the logout page. |
| `palette.background.default`, `palette.background.paper` | The page background, and the cards and dialogs. |
| `palette.text.primary`, `palette.text.secondary`, `palette.divider` | Text and dividers. |
| `typography.fontFamily` | All text. When it is set for both color schemes, Roboto is no longer loaded, so load the font with `css_files`. |
| `typography.fontSize` | Scales all text, like it does in Material UI. |
| `shape.borderRadius` | Corners of cards, inputs, buttons and alerts. |

Other theme options, such as component overrides, are ignored. For anything the theme cannot express, add CSS with `raw_css`. The page styles are built on `--pn-*` CSS variables, e.g. `--pn-primary` and `--pn-radius`, which can also be overridden there:

```python
pn.config.page_config = {
    'raw_css': ['.pn-card { border: 1px solid var(--pn-divider); box-shadow: none; }'],
}
```

## Custom templates

If you replace one of the pages with your own template, e.g. with `--index`, `--basic-login-template`, `--logout-template` or `--auth-template`, the template can still use the page configuration through the `page` variable:

`page.head`
: The page stylesheet with the theme applied and the configured stylesheet links. Insert it into `<head>` with `{{ page.head }}`, or `{% raw page.head %}` in the Tornado template used by `--index`.

`page.brand(title, tag='span', href=None)`
: Renders the logo and title for an element with the `pn-appbar` class.

`page.title`, `page.logo`, `page.favicon`, `page.site_url`, `page.dark_theme`
: The resolved configuration values, with local images converted to data URIs.

The [authentication templates guide](../authentication/templates) lists the other variables each template receives.
