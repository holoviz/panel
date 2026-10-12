"""
A ``runserver`` command which serves the project with an ASGI server.

Django's own development server is WSGI only, so it serves the Django views of
a project but not the Panel applications composed with them in the ASGI
application. This command replaces it with uvicorn running
``settings.ASGI_APPLICATION``, i.e. ``python manage.py runserver`` behaves as
users expect. It is picked up by adding ``'panel.io.django'`` to the
``INSTALLED_APPS``, before ``'django.contrib.staticfiles'``, which ships a
``runserver`` command of its own.
"""
import sys

from datetime import datetime

from django.conf import settings
from django.core.management.base import CommandError
from django.core.management.commands.runserver import (
    Command as RunserverCommand,
)
from django.db import connections


class Command(RunserverCommand):

    help = (
        "Starts a lightweight ASGI web server for development, serving both "
        "the Django project and the Panel applications."
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "--wsgi",
            action="store_true",
            help=(
                "Run Django's WSGI development server instead. The Panel "
                "applications are not served."
            ),
        )

    def run(self, **options):
        if options["wsgi"]:
            super().run(**options)
            return

        try:
            import uvicorn
        except ImportError:
            raise CommandError(
                "uvicorn must be installed to serve the ASGI application. "
                "Install it with 'pip install uvicorn' or run Django's WSGI "
                "development server with 'manage.py runserver --wsgi', which "
                "does not serve the Panel applications."
            ) from None

        asgi_application = getattr(settings, 'ASGI_APPLICATION', None)
        if not asgi_application:
            raise CommandError(
                "ASGI_APPLICATION is not declared in the Django settings, so "
                "there is no ASGI application to serve. Declare the Panel "
                "applications with panel.io.django.get_asgi_application and "
                "point ASGI_APPLICATION at it. See "
                "https://panel.holoviz.org/how_to/integrations/Django.html"
            )
        module, _, attribute = asgi_application.rpartition('.')
        if not module:
            raise CommandError(
                f"ASGI_APPLICATION={asgi_application!r} is not a dotted path "
                "to an ASGI application."
            )

        if not options["skip_checks"]:
            self.stdout.write("Performing system checks...\n\n")
            check_kwargs = self.get_check_kwargs(options)
            check_kwargs["display_num_errors"] = True
            self.check(**check_kwargs)
        self.check_migrations()
        for conn in connections.all(initialized_only=True):
            conn.close()

        self.on_bind(self.port)
        try:
            uvicorn.run(
                f'{module}:{attribute}',
                host=self.addr,
                port=int(self.port),
                reload=options["use_reloader"],
                log_level='info',
            )
        except KeyboardInterrupt:
            pass

    def on_bind(self, server_port):
        if self._raw_ipv6:
            addr = f'[{self.addr}]'
        elif self.addr == '0':
            addr = '0.0.0.0'
        else:
            addr = self.addr
        now = datetime.now().strftime('%B %d, %Y - %X')
        quit_command = 'CTRL-BREAK' if sys.platform == 'win32' else 'CONTROL-C'
        self.stdout.write(
            f"{now}\n"
            f"Django version {self.get_version()}, using settings "
            f"{settings.SETTINGS_MODULE!r}\n"
            f"Starting ASGI development server at {self.protocol}://{addr}:{server_port}/\n"
            f"Quit the server with {quit_command}."
        )
