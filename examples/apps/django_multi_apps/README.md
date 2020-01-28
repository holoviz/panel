# Multiple Panel Apps in Django

As the core user guides including the Introduction have demonstrated,
it is easy to display Panel apps in the notebook, launch them from an
interactive Python prompt, and deploy them as a standalone Bokeh
server app from the commandline. However, it is also often useful to
embed a Panel app in large web application, such as a Django web
server. Using Panel with Django requires a bit more work than for
notebooks and Bokeh servers.

To run this example app yourself, you will first need to install
django 2 or 3 (e.g. conda install "django=2").

We will show how to build a simple django apps with 3 apps
stockscreener, sliders, gbm.

To simply run the Django server launch it with:

```
python manage.py runserver
```

and then visit http://localhost:8000 in your browser. For detail on
how to configure a bokeh app see the user guide in
/examples/user_guide/Django_Apps.ipynb or visit it [on the website](https://panel.holoviz.org/user_guide/Django_Apps.html).
