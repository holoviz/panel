# Serving static files

Whether you're launching your application using `panel serve` from the commandline or using `pn.serve` in a script you can also serve static files. When using `panel serve` you can use the `--static-dirs` argument to specify a list of static directories to serve along with their routes, e.g.:

    panel serve some_script.py --static-dirs assets=./assets

This will serve the `./assets` directory on the servers `/assets` route. Note however that the `/static` route is reserved internally by Panel.

Similarly when using `pn.serve` or `panel_obj.show` the static routes may be defined as a dictionary, e.g. the equivalent to the example would be:

    pn.serve(panel_obj, static_dirs={'assets': './assets'})
