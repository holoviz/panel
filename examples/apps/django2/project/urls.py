"""demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from bokeh.server.django import autoload, static_extensions
from django.apps import apps
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import sliders.pn_app as sliders_app

pn_app_config = apps.get_app_config('bokeh.server.django')

urlpatterns = [
    path('sliders/', include('sliders.urls')),
    path('admin/', admin.site.urls),
]

bokeh_apps = [
    autoload("sliders", sliders_app.app),
]

urlpatterns += static_extensions()
urlpatterns += staticfiles_urlpatterns()
