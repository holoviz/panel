# Django Apps

As the core user guides including the Introduction have demonstrated, it is easy to display Panel apps in the notebook, launch them from an interactive Python prompt, and deploy them as a standalone Bokeh server app from the commandline. However, it is also often useful to embed a Panel app in large web application, such as a Django web server. Using Panel with Django requires a bit more work than for notebooks and Bokeh servers.

To run this example app yourself, you will first need to install django 2 or 3 (e.g. conda install "django=2").

We will show how to build a simple django apps with 3 apps stockscreener, sliders, sliders_cosine. this app shows how to integrate Panel with a Django view, but there's currently no interaction between the Param and Django models.

### Init
In the root directory (alongside settings.py):
- Install channels 

- Create a file ***asgi.py***:

```python
import os

import django
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_Panel_Multi.settings')
django.setup()
application = get_default_application()
```

- Create a file ***routing.py***:
```python
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.apps import apps

bokeh_app_config = apps.get_app_config('bokeh.server.django')

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(bokeh_app_config.routes.get_websocket_urlpatterns())),
    'http': AuthMiddlewareStack(URLRouter(bokeh_app_config.routes.get_http_urlpatterns())),
})
```

- In  ***setting.py***:

```python
from bokeh.settings import bokehjsdir
...

# WSGI_APPLICATION = 'Django_Panel_Multi.wsgi.application'
ASGI_APPLICATION = 'Django_Panel_Multi.routing.application'
...
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # local
    'channels',
    'bokeh.server.django',
]

#  at the bottom 
STATICFILES_DIRS = [bokehjsdir()]
```
## Sliders app
- Create a new app:
```python
python manage.py startapp sliders
```
- Create ***pn_model.py*** for the sliders app
```python
import numpy as np
import param
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

class SineWave(param.Parameterized):
    offset = param.Number(default=0.0, bounds=(-5.0, 5.0))
    amplitude = param.Number(default=1.0, bounds=(-5.0, 5.0))
    phase = param.Number(default=0.0, bounds=(0.0, 2 * np.pi))
    frequency = param.Number(default=1.0, bounds=(0.1, 5.1))
    N = param.Integer(default=200, bounds=(0, None))
    x_range = param.Range(default=(0, 4 * np.pi), bounds=(0, 4 * np.pi))
    y_range = param.Range(default=(-2.5, 2.5), bounds=(-10, 10))

    def __init__(self, **params):
        super(SineWave, self).__init__(**params)
        x, y = self.sine()
        self.cds = ColumnDataSource(data=dict(x=x, y=y))
        self.plot = figure(plot_height=400, plot_width=400,
                           tools="crosshair, pan, reset, save, wheel_zoom",
                           x_range=self.x_range, y_range=self.y_range)
        self.plot.line('x', 'y', source=self.cds, line_width=3, line_alpha=0.6)

    @param.depends('N', 'frequency', 'amplitude', 'offset', 'phase', 'x_range', 'y_range', watch=True)
    def update_plot(self):
        x, y = self.sine()
        self.cds.data = dict(x=x, y=y)
        self.plot.x_range.start, self.plot.x_range.end = self.x_range
        self.plot.y_range.start, self.plot.y_range.end = self.y_range

    def sine(self):
        x = np.linspace(0, 4 * np.pi, self.N)
        y = self.amplitude * np.sin(self.frequency * x + self.phase) + self.offset
        return x, y
```
- Create ***pn_app.py*** for the sliders app
```python
import panel as pn
from .pn_model import SineWave

def app(doc):
    sw = SineWave()
    row = pn.Row(sw.param, sw.plot)
    row.server_doc(doc)
```

- In **views.py** add:
```python
# Create your views here.
from bokeh.embed import server_document

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def sliders(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "sliders/sliders.html", dict(script=script))
```
We assume that the templates folder is in the root directory of the django project and each app has its own folder

- Create ***urls.py***:
```python
from django.urls import path

from . import views

app_name = 'sliders'
urlpatterns = [
    path('', views.sliders, name='sliders'),
]
```
- In the project **urls.py** the urls for the app
```python
from bokeh.server.django import autoload
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

import gbm.pn_app as sliders_cosine_app
import sliders.pn_app as sliders_app

pn_app_config = apps.get_app_config('bokeh.server.django')

urlpatterns = [
    path('/sliders', include('sliders.urls')),
    path('admin/', admin.site.urls),
]

base_path = settings.BASE_PATH
# print(f"base_path: {base_path}")

bokeh_apps = [
    autoload("sliders", sliders_app.app),
]

urlpatterns += staticfiles_urlpatterns()
print(f"urlpatterns: {urlpatterns}")
```


We can add another app
## Geometric Brownian motion ("GBM") app
- Create a new app:
```python
python manage.py startapp gbm
```
- Create ***pn_model.py*** for the gbm app
```python
import numpy as np
import pandas as pd
import param

import hvplot
import hvplot.pandas
import holoviews as hv


class GBM(param.Parameterized):
    # interface
    mean = param.Number(default=5, bounds=(.0, 25.0))
    volatility = param.Number(default=5, bounds=(.0, 50.0))
    maturity = param.Integer(default=1, bounds=(0, 25))
    n_observations = param.Integer(default=10, bounds=(2, 100))
    n_simulations = param.Integer(default=20, bounds=(1, 500))

    def __init__(self, **params):
        super(GBM, self).__init__(**params)

    @param.depends('mean', 'volatility', 'maturity', 'n_observations', 'n_simulations', watch=True)
    def update_plot(self, **kwargs):
        df_s = pd.DataFrame(index=range(0, self.n_observations))

        for s in range(0, self.n_simulations):
            name_s = f"stock_{s}"
            df_s[name_s] = self.gbm(spot=100,
                                    mean=self.mean/100,
                                    vol=self.volatility/100,
                                    dt=self.maturity / self.n_observations,
                                    n_obs=self.n_observations)
        return df_s.hvplot(grid=True, colormap='Paired')

    @staticmethod
    def gbm(spot: float, mean: float, vol: float, dt: float, n_obs: int) -> np.ndarray:
        """ Geometric Brownian Motion

        :param spot: spot value
        :param mean: mean annualised value
        :param vol: volatility annualised value
        :param dt: time steps
        :param n_obs: number of observation to return
        :return: a geometric brownian motion np.array()
        """
        # generate normal random
        rand = np.random.standard_normal(n_obs)
        # initialize the parameters
        S = np.zeros_like(rand)
        S[0] = spot
        # loop to generate the brownian motion
        for t in range(1, n_obs):
            S[t] = S[t - 1] * np.exp((mean - (vol ** 2) / 2) * dt + vol * rand[t] * np.sqrt(dt))
        # return the geometric brownian motion
        return S
```
- Create ***pn_app.py*** for the gbm app
```python
import panel as pn
from .pn_model import GBM


def app(doc):
    gbm = GBM()
    row = pn.Row(gbm.param, gbm.update_plot)
    row.server_doc(doc)
```
 - In **views.py** add:
```python
# Create your views here.
from bokeh.embed import server_document

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def gbm(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "gbm/gbm.html", dict(script=script))
```
We assume that the templates folder is in the root directory of the django project and each app has its own folder

- Create ***urls.py***:
```python
from django.urls import path

from . import views

app_name = 'gbm'
urlpatterns = [
    path('', views.gbm, name='gbm'),
]
```

Do the same as above....and update your project **urls.py**
```python
from bokeh.server.django import autoload
from django.apps import apps
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

import sliders.pn_app as sliders_app
import gbm.pn_app as gbm_app

pn_app_config = apps.get_app_config('bokeh.server.django')

urlpatterns = [
    path('', include('landing.urls')),
    path('sliders/', include('sliders.urls')),
    path('gbm/', include('gbm.urls')),
    path('admin/', admin.site.urls),
]

bokeh_apps = [
    autoload("sliders", sliders_app.app),
    autoload("gbm", gbm_app.app),
]

urlpatterns += staticfiles_urlpatterns()
```

We can add another app
## Stockscreener ("ss") app using pn.widgets !
- Create a new app:
```python
python manage.py startapp stockscreener
```
- Create ***pn_model.py*** for the ss app
```python
import datetime as dt

import panel as pn
import param
import hvplot
import hvplot.pandas
from django.conf import settings


class StockScreener(param.Parameterized):
    # interface
    df = param.DataFrame(precedence=-1)
    Index = pn.widgets.MultiSelect()
    Rebase = pn.widgets.Checkbox(name='Rebase', value=True)
    From = pn.widgets.DateSlider()

    def __init__(self, df, **params):
        super(StockScreener, self).__init__(**params)
        # init df
        self.df = df
        self.start_date = dt.datetime(year=df.index[0].year, month=df.index[0].month, day=df.index[0].day)
        self.end_date = dt.datetime(year=df.index[-1].year, month=df.index[-1].month, day=df.index[-1].day)
        self.col = list(self.df.columns)
        # init interface
        self.Index = pn.widgets.MultiSelect(name='Index', value=self.col[0:5], options=self.col,
                                            size=min(10, len(self.col)))
        self.From = pn.widgets.DateSlider(name='From', start=self.start_date, end=self.end_date, value=self.start_date)

    @param.depends('Index.value', 'Rebase.value', 'From.value', watch=True)
    def update_plot(self, **kwargs):
        unds = list(self.Index.value)
        pos = self.df.index.get_loc(self.From.value, method='bfill')
        dfp = self.df.iloc[pos:][unds]
        if self.Rebase.value:
            dfp = 100 * dfp / dfp.iloc[0]

        return dfp.hvplot(value_label="Level", colormap=settings.COLOR_MAP)
```
- Create ***pn_app.py*** for the ss app
```python
import os

import pandas as pd
import panel as pn

from .pn_model import StockScreener


def app(doc):
    data_path = os.path.join(os.path.dirname(__file__), 'datasets/market_data.csv')
    df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    ss = StockScreener(df=df)
    row = pn.Row(pn.Column(ss.Index, ss.From, ss.Rebase), ss.update_plot)
    row.server_doc(doc)
```
 - In **views.py** add:
```python
# Create your views here.
from bokeh.embed import server_document

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def stockscreener(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "stockscreener/stockscreener.html", dict(script=script))

```
We assume that the templates folder is in the root directory of the django project and each app has its own folder

- Create ***urls.py***:
```python
from django.urls import path

from . import views

app_name = 'stockscreener'
urlpatterns = [
    path('', views.stockscreener, name='stockscreener'),
]
```

Do the same as above....and update your project **urls.py**
```python
from bokeh.server.django import autoload
from django.apps import apps
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

import sliders.pn_app as sliders_app
import gbm.pn_app as gbm_app
import stockscreener.pn_app as stockscreener_app
from .themes import plot_themes

pn_app_config = apps.get_app_config('bokeh.server.django')

urlpatterns = [
    path('', include('landing.urls')),
    path('sliders/', include('sliders.urls')),
    path('gbm/', include('gbm.urls')),
    path('stockscreener/', include('stockscreener.urls')),
    path('admin/', admin.site.urls),
]

bokeh_apps = [
    autoload("sliders", sliders_app.app),
    autoload("gbm", gbm_app.app),
    autoload("stockscreener", stockscreener_app.app),
]

urlpatterns += staticfiles_urlpatterns()

# Set the themes
plot_themes()
```
Above for consistency we have a **themes.py** to format the plot in the django project directory that we run on loading the url (could create a themes for each app and run on AppConfig ready function)
- Create **themes.py**:
```python
import panel as pn
import holoviews as hv
import hvplot
# import hvplot.pandas


def __disable_logo(plot, element):
    plot.state.toolbar.logo = None


def plot_themes():
    # format
    hv.plotting.bokeh.ElementPlot.finalize_hooks.append(__disable_logo)
    pn.widgets.DatetimeInput.format = '%d %B %Y'
    hv.plotting.bokeh.ElementPlot.bgcolor = "#fbfcfc"
    hv.plotting.bokeh.ElementPlot.gridstyle = {"grid_line_alpha": 0.6, "grid_line_dash": 'dashed'}
```



# HTML Files
We will use the Django Template engine
- Create ***base.html***:
```html
{% load static %}

{% block doc %}
    <!doctype html>
    <html lang="en">
    {% block html %}
        <head>
            {% block head %}
                <title>{% block title %}Django Panel{% endblock title %}</title>
                <!-- Required meta tags -->
                {% block meta %}
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                    <meta name="description" content="Testing Website of the ZGL limited company">
                    <meta name="keywords" content="Prototype Website for Testing of new Technology, Keep out">
                {% endblock meta %}

                {% block styles %}
                    <!-- Bootstrap CSS -->
                    <link rel="stylesheet"
                          href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"
                          integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO"
                          crossorigin="anonymous">
                {% endblock styles %}
                <link rel="shortcut icon" href="{% static 'icons/favicon32x32.png' %}" type="image/x-icon">
                <link rel="icon" href="{% static 'icons/favicon32x32.png' %}" type="image/x-icon">
            {% endblock head %}
        </head>

        <!-- BODY -->
        <body id="home"{% block body_attributs %}{% endblock body_attributs %}>
        {% block body %}
            <!-- NAVBAR -->
            {% block navbar %}
                {% if user.is_authenticated %}
                    <nav id="main-nav" class="navbar navbar-expand-md navbar-dark bg-blue fixed-top
                            {% block navbar_class %}{% endblock navbar_class %}">
                {% else %}
                    <nav id="main-nav" class="navbar navbar-expand-md navbar-dark bg-dark navbar-fixed-top">
                {% endif %}
            <div class="container-fluid">
                <!-- brand -->
                <a class="navbar-brand d-none d-sm-block logo" href="/">
                    [...@djangopanel ~]$<span class="blink_me">_</span></a>
                <a class="navbar-brand d-block d-sm-none logo"
                   href="/">[djangopanel ~]$<span
                        class=" blink_me">_</span></a>
                <!-- navigation button and toggler-icon -->
                <button class="navbar-toggler" type="button" data-toggle="collapse"
                        data-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false"
                        aria-label="Toggle navigation">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <!-- navbar collect element -->
                <div class="collapse navbar-collapse" id="navbarCollapse">
                    <ul class="navbar-nav ml-auto mr-4">
                        {% block navbar_item %}
                            <li class="nav-item">
                                <a href="{% url 'stockscreener:stockscreener' %}" class="nav-link">Stockscreener<span
                                        class="sr-only">(current)</span></a>
                            </li>
                            <li class="nav-item">
                                <a href="{% url 'sliders:sliders' %}" class="nav-link">Sliders<span
                                        class="sr-only">(current)</span></a>
                            </li>
                            <li class="nav-item">
                                <a href="{% url 'gbm:gbm' %}" class="nav-link">GBM<span
                                        class="sr-only">(current)</span></a>
                            </li>
                        {% endblock navbar_item %}
                    </ul>
                </div>
            </div>
            </nav>
            {% endblock navbar %}

            <!-- MAIN-->

            <!-- FLASH MESSAGES -->
            <div class="container">
                {% block messages %}
                    <div class="col-md-8">
                        {% if messages %}
                            {% for message in messages %}
                                <div class="alert alert-{{ message.tags }} alert-dismissible" role="alert">
                                    <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                                        <span aria-hidden="true">&times</span>
                                    </button>
                                    {{ message }}
                                </div>
                            {% endfor %}
                        {% endif %}
                    </div>
                {% endblock messages %}
            </div>
            <!-- CONTENT -->
            {% block content %}
                {{ server_script|safe }}
            {% endblock %}


            <!-- FOOTER -->
            {% if user.is_authenticated %}
                <footer id="footer" class="container-fluid bg-blue text-center p-2 fixed-bottom">
            {% else %}
                <footer id="footer" class="container-fluid bg-dark text-white text-center p-2 fixed-bottom">
            {% endif %}
        {% block footer %}
            Copyright &copy; <span class="year"></span> zgl
        {% endblock footer %}
        </footer>

            {% block scripts %}
                <script src="https://code.jquery.com/jquery-3.3.1.min.js"
                        integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8="
                        crossorigin="anonymous"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js"
                        integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49"
                        crossorigin="anonymous"></script>
                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js"
                        integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy"
                        crossorigin="anonymous"></script>

            {% endblock scripts %}
        {% endblock body %}
        </body>
    {% endblock html %}
    </html>
{% endblock doc %}
```
- Create **sliders/sliders.html**:
```html
{% extends 'base.html' %}
{% load static %}

{% block content %}

    <div class="jumbotron jumbotron-fluid bg-success text-center">
        <h1>Sliders App</h1>
        <p class="lead">Predictive Analytics</p>
    </div>

    <div class="container-fluid text-center">
        <div class="row">
            <div class="col-md-6">
                <h1>This is App1 </h1>
                {{ script |safe }}
            </div>
            <div class="col-md-6">
                <h1>This is App2 </h1>
                {{ script |safe }}
            </div>
        </div>
    </div>

{%  endblock content %}
```









