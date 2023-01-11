# MyBinder

Binder allows you to create custom computing environments that can be shared and used by many remote users. MyBinder is a public, free hosting option, with limited compute and memory resources, which will allow you to deploy your simple app quickly and easily.

Here we will take you through the configuration to quickly set up a GitHub repository with notebooks containing Panel apps for deployment on MyBinder.org. As an example refer to the [Clifford demo repository](https://github.com/pyviz-demos/clifford).

1. Create a GitHub repository and add the notebook or script you want to serve (in the example repository this is the clifford.ipynb file)

2. Add an ``environment.yml`` which declares a conda environment with the dependencies required to run the app (refer to the [conda documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-file-manually) to see how to declare your dependencies). Add `jupyter_panel_proxy` as a dependency by adding either `conda-forge` or `pyviz` to the channel list:

```
channels:
- pyviz

packages:
- jupyter-panel-proxy
```

3. Go to mybinder.org, enter the URL of your GitHub repository and hit ``Launch``

4. mybinder.org will give you a link to the deployment, e.g. for the example app it is https://mybinder.org/v2/gh/panel-demos/clifford-interact/master. To visit the app simply append ``?urlpath=/panel/clifford`` where you should replace clifford with the name of the notebook or script you are serving.
