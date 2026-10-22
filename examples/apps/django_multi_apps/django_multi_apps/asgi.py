"""
ASGI config for the django_multi_apps project.

It exposes the ASGI callable as a module-level variable named ``application``,
serving both the Django project and the Panel applications.

Run it with 'python manage.py runserver' or with an ASGI server directly:

    uvicorn django_multi_apps.asgi:application
"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_multi_apps.settings')

django.setup()

import gbm.pn_app as gbm_app  # noqa: E402
import sliders.pn_app as sliders_app  # noqa: E402
import stockscreener.pn_app as stockscreener_app  # noqa: E402

from panel.io.django import autoload, get_asgi_application  # noqa: E402

from .themes import plot_themes  # noqa: E402

plot_themes()

application = get_asgi_application([
    autoload('sliders', sliders_app.app),
    autoload('gbm', gbm_app.app),
    autoload('stockscreener', stockscreener_app.app),
])
