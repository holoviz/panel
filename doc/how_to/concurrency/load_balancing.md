# Load balancing

Setting up load balancing is a huge topic, dependent on the precise system you
are using, so the example below will be very generic. In most cases
you set up a reverse proxy (like NGINX) to distribute the load across multiple
application servers. If you are using a system like Kubernetes, it will also
handle spinning up and shutting down the servers for you, and can even do so dynamically, depending
on the amount of concurrent users to ensure that you are not wasting resources
when there are fewer users, and / or when there is less computing demand.

<figure>
<img src="https://assets.holoviz.org/panel/how_to/concurrency/what-is-load-balancing-diagram-NGINX.png" width="768"></img>
<figcaption>Diagram showing concept of load balancing (NGINX)</figcaption>
</figure>

Load balancing is the most complex approach to set up but is guaranteed to
improve concurrent usage of your application since different users are not
contending for access to the same process or even necessarily the same physical
compute and memory resources. At the same time it is more wasteful of resources
since it potentially occupies multiple machines and since each process is
isolated there is no sharing of cached data or global state.

To get started configuring a load balancer take a look at the [Bokeh
documentation](https://docs.bokeh.org/en/latest/docs/user_guide/server/deploy.html#load-balancing).

## Use NGINX and Containers with Panel along with other Bokeh extensions

Panel is built on top of Bokeh and uses the Bokeh server to serve applications. To serve Panel-specific resources, Panel is defined as a Bokeh extension.
Panel's resources are available on a CDN, but if you use other Bokeh Extensions, serving them directly from the Bokeh server can be beneficial.
An example of this is [ipywidget_bokeh](https://github.com/bokeh/ipywidgets_bokeh), which is a Bokeh extension that allows you to embed ipywidgets inside a Bokeh application.

### Files

::::{tab-set}

:::{tab-item} app.py

```python
import ipywidgets
import panel as pn

pn.Row(ipywidgets.HTML("This is an IPywidget served with Panel")).servable()
```

:::

:::{tab-item} Containerfile

```Dockerfile
FROM ubuntu:latest

# Linux Packages
RUN apt-get update && \
    apt-get install -y build-essential wget nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Python Packages
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O ~/conda.sh && \
    /bin/bash ~/conda.sh -b -p $CONDA_DIR && rm ~/conda.sh
ENV PATH=$CONDA_DIR/bin:$PATH
RUN conda install python ipywidgets ipywidgets_bokeh panel -y

# Bokeh
ENV BOKEH_RESOURCES server
ENV BOKEH_ALLOW_WS_ORIGIN localhost

# Nginx
RUN rm /etc/nginx/sites-available/default
COPY nginx.conf /etc/nginx/sites-available/default

# App
COPY app.py .
COPY panel-serve.sh .
RUN chmod +x panel-serve.sh
WORKDIR /
CMD ["/bin/bash", "panel-serve.sh"]
```

:::

:::{tab-item} panel-serve.sh

```bash
#!/bin/bash

nginx

# Serve the panel apps
panel serve app.py --port 5100 &
panel serve app.py --port 5101 &
panel serve app.py --port 5102 &

# Never stop
wait -n
```

:::

:::{tab-item} nginx.conf

```nginx
upstream app {
    # Should match what is defined in panel-serve.sh
    least_conn;
    server 127.0.0.1:5100;
    server 127.0.0.1:5101;
    server 127.0.0.1:5102;
}

server {
    listen 80 default_server;
    server_name _;

    access_log /tmp/bokeh.access.log;
    error_log /tmp/bokeh.error.log debug;

    location = /proxy {
        return 301 http://$http_host/proxy/;
    }

    location /proxy/ {
        rewrite ^/proxy/(.*)$ /$1 break;
        proxy_pass http://app/;

        proxy_set_header Host $host:$server_port;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location ~ ^/proxy/(.*)/ws$ {
        rewrite ^/proxy/(.*)/ws$ /$1/ws break;
        proxy_pass http://app;

        proxy_http_version 1.1;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host:$server_port;
        proxy_set_header Upgrade $http_upgrade;
    }
}
```

:::

::::

### Launching the app

You can use any container framework to run the app. The commands below are for Podman, but you can use Docker as well.
First, build the container with `podman build -t my-container .` and the run it `podman run -dt -p 8000:80 localhost/my-container`
