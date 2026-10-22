"""
The Django application configuration of the Panel integration.

Adding ``'panel.io.django'`` to the ``INSTALLED_APPS`` is only needed to pick
up the ``runserver`` management command that serves the ASGI application, see
``panel.io.django.management.commands.runserver``.
"""
from django.apps import AppConfig


class PanelConfig(AppConfig):

    name = 'panel.io.django'

    label = 'panel'

    verbose_name = 'Panel'
