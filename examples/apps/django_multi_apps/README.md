# Multiple Panel apps in Django

Panel apps can be displayed in a notebook, launched from an interactive Python
prompt and deployed with `panel serve`, but it is also often useful to embed
them in a larger web application such as a Django project. This example shows a
Django project embedding three Panel applications: `sliders`, `gbm` and
`stockscreener`.

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python manage.py runserver
```

Then visit http://localhost:8000 in your browser.

Panel serves its applications on the ASGI application declared in
`django_multi_apps/asgi.py`, so the project has to be run with an ASGI server.
Django's own development server is WSGI only, which is why `panel.io.django` is
listed in the `INSTALLED_APPS`: it replaces `runserver` with a command that
serves the ASGI application with uvicorn. To run it yourself instead, e.g. in
production:

```bash
uvicorn django_multi_apps.asgi:application
```

For details on how to configure the applications see the
[Django how-to guide](https://panel.holoviz.org/how_to/integrations/Django.html).
