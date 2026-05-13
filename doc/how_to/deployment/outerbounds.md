# Outerbounds

This guide will show you how to deploy a Panel app using [Outerbounds](https://outerbounds.com/), a platform for deploying Python applications.
The guide assumes you have a basic understanding of how to create a Panel app and focuses on the deployment process using Outerbounds.

## Setup

To get started working with Outerbounds download and install the [CLI](https://docs.outerbounds.com/outerbounds/inference-cli-reference/).
This can be done with `pipx install outerbounds` or `uvx outerbounds`.

Once you have installed the CLI you need to configure it to be able to deploy your app.
This is done by running `outerbounds configure $TOKEN` where token is found in the Outerbounds dashboard under Setup.
To verify your configuration you can run `outerbounds check`.

## Deploying a Panel App with Outerbounds

Create the following files in a directory and then deploy to `outerbounds app deploy --config-file config.yaml`.

```yaml
# config.yaml
name: panel-app
port: 6000
image: python:3.11-trixie

commands:
  - panel serve app.py --port 6000 --allow-websocket-origin="*.outerbounds.com"

environment:
  BOKEH_RESOURCES: CDN
```

```python
# app.py
import panel_material_ui as pmui

pmui.Page(title="Hello World").servable()
```

```text
# requirements.txt
panel
panel-material-ui
```

:::{note}
The `*.outerbounds.com` wildcard in `--allow-websocket-origin` matches any app
subdomain assigned by Outerbounds, but only one level deep, e.g.,
`myapp.outerbounds.com` and not `myapp.dev.outerbounds.com`.
:::
