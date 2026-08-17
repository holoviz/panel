# Serving static files

Whether you're launching your application using `panel serve` from the commandline or using `pn.serve` in a script you can also serve static files. When using `panel serve` you can use the `--static-dirs` argument to specify a list of static directories to serve along with their routes, e.g.:

    panel serve some_script.py --static-dirs assets=./assets

This will serve the `./assets` directory on the servers `/assets` route. Note however that the `/static` route is reserved internally by Panel.

Similarly when using `pn.serve` or `panel_obj.show` the static routes may be defined as a dictionary, e.g. the equivalent to the example would be:

    pn.serve(panel_obj, static_dirs={'assets': './assets'})

The same applies to the ASGI implementations, i.e. `panel serve --server fastapi` accepts `--static-dirs` and both `panel.io.fastapi.add_applications` and `panel.io.django.get_asgi_application` accept a `static_dirs` dictionary:

    from panel.io.fastapi import add_applications

    add_applications(panel_obj, app=app, static_dirs={'assets': './assets'})

When embedding Panel in an existing FastAPI or Django project you may of course also serve the files with the framework's own static file handling, e.g. Starlette's `StaticFiles` or Django's `staticfiles`, as long as the route does not collide with one of the Panel routes.
