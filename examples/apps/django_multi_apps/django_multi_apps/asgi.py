"""
ASGI config for django_multi_apps project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
https://channels.readthedocs.io/en/latest/deploying.html
"""


import os

import django
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_multi_apps.settings')
django.setup()
application = get_default_application()

