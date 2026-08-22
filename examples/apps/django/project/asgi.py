"""
The ASGI application serving both the Django project and the Panel app.

Run it with an ASGI server, e.g.:

    uvicorn project.asgi:application
"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

django.setup()

import sliders.pn_app as sliders_app  # noqa: E402

from panel.io.django import autoload, get_asgi_application  # noqa: E402

application = get_asgi_application([
    autoload('sliders', sliders_app.app),
])
