# Google Cloud Platform (GCP)

First, you need to set up your Google cloud account following the [Cloud Run documentation](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/python) or the [App Engine documentation](https://cloud.google.com/appengine/docs/standard/python3/quickstart) depending on whether you would like to deploy your Panel app to Cloud Run or App Engine.

Next, you will need three files:
1. app.py: This is the Python file that creates the Panel App.

2. requirements.txt: This file lists all the package dependencies of our Panel app. Here is an example for requirements.txt:

```
panel
bokeh
hvplot
```
3. app.yml (for App Engine) or Dockerfile (for Cloud Run)

Here is an example for app.yml (if you would like to deploy to App Engine):
```
runtime: python
env: flex
entrypoint: panel serve app.py --address 0.0.0.0 --port 8080 --allow-websocket-origin="*"

runtime_config:
  python_version: 3
```

Here is an example for Dockerfile (if you would like to deploy to Cloud Run):
```
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup.
CMD panel serve app.py --address 0.0.0.0 --port 8080 --allow-websocket-origin="*"
```

Finally, to deploy a Panel app to App Engine run `gcloud app create` and `gcloud app deploy`.

## Deploying with Cloud Run

To deploy a Panel app to Cloud Run, run `gcloud run deploy`.

Panel apps use a websocket to the running Bokeh server. Websockets are considered by Cloud Run to be long-running HTTP requests.

If you deploy a panel app on GCP with Cloud Run, make sure you set up a long request timeout, with CLI parameter `--timeout=...`

The default timeout is 5 minutes, which makes the panel app lose its websocket connection after this time, leading to unresponsive UI, because Cloud Run considers the websocket as timed-out.

You can extend the timeout up to 60 minutes.

To extend the timeout duration, run `gcloud run deploy --timeout 60min`.

For detailed information and steps, check out this [example](https://towardsdatascience.com/deploy-a-python-visualization-panel-app-to-google-cloud-cafe558fe787?sk=98a75bd79e98cba241cc6711e6fc5be5) on how to deploy a Panel app to App Engine and this [example](https://towardsdatascience.com/deploy-a-python-visualization-panel-app-to-google-cloud-ii-416e487b44eb?sk=aac35055957ba95641a6947bbb436410) on how to deploy a Panel app to Cloud Run.

Regarding Cloud Run, check out the documentation about [Cloud run and WebSockets](https://cloud.google.com/run/docs/triggering/websockets) and about the [`--timeout` option](https://cloud.google.com/run/docs/configuring/request-timeout)
