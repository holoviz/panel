# Heroku

Heroku makes deployment of arbitrary apps including Panel apps and dashboards very easy and provides a free tier to get you started. This makes it a great starting point for users not too familiar with web development and deployment.

To get started working with Heroku [signup](https://signup.heroku.com) for a free account and [download and install the CLI](https://devcenter.heroku.com/articles/getting-started-with-python#set-up). Once you are set up follow the instructions to log into the CLI.

1. Create a new Git repo (or to follow along clone the [minimal-heroku-demo](https://github.com/pyviz-demos/minimal-heroku-demo) GitHub repo)

2. Add a Jupyter notebook or Python script which declares a Panel app or dashboard to the repository.

3. Define a requirements.txt containing all the requirements for your app (including Panel itself). For the sample app the requirements are as minimal as:

```
panel
hvplot
scikit-learn
```

3. Define a `Procfile` which declares the command Heroku should run to serve the app. In the sample app the following command serves the `iris_kmeans.ipynb` example. The websocket origin should match the name of the app on Heroku ``app-name.herokuapp.com`` which you will declare in the next step:

```
web: panel serve --address="0.0.0.0" --port=$PORT iris_kmeans.ipynb --allow-websocket-origin=app-name.herokuapp.com
```

4. Create a Heroku app using the CLI ensuring that the name matches the URL we declared in the previous step:

```
heroku create app-name
```

5. Push the app to heroku and wait until it is deployed.

6. Visit the app at app-name.herokuapp.com

Once you have deployed the app you might find that if your app is visited by more than one user at a time it will become unresponsive. In this case you can use the Heroku CLI [to scale your deployment](https://devcenter.heroku.com/articles/getting-started-with-python#scale-the-app).
