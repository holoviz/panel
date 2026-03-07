# Deploy Panel Apps on Replit

This guide shows how to deploy a Panel application using [Replit](https://replit.com/).

Replit allows running Python applications in the browser without requiring local setup, making it easy to share and embed Panel apps.

---

## Create a Replit Project

1. Go to https://replit.com
2. Click **Create Repl**
3. Select **Python** as the language
4. Give the project a name and create the repl

---

## Install Panel

Open the **Shell** tab in your repl and install Panel:

```bash
pip install panel
```

You may also want to install other libraries depending on your application.

---

## Create a Panel App

Create a file called `app.py` with the following example:

```python
import panel as pn

pn.extension()

slider = pn.widgets.IntSlider(name="Value", start=0, end=10)

pn.Column(
    "# Panel on Replit",
    slider,
    pn.bind(lambda v: f"Value: {v}", slider)
).servable()
```

---

## Run the Application

Run the app using:

```bash
panel serve app.py --address 0.0.0.0 --port 8080 --allow-websocket-origin=*
```

This command starts the Panel server inside the Replit environment.

---

## View the App

Click the **Run** button in Replit.

Replit will open a preview window showing the running Panel application.

---

## Share or Embed

Once your app is running, Replit provides a public URL that you can share or embed in blogs or articles.

See the example shared on the HoloViz Discourse forum:

https://discourse.holoviz.org/t/fruityfacts-compare-nutrition-facts-of-fruits-in-replit/5917
