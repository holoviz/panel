# Anaconda Notebooks

[Anaconda](https://www.anaconda.com/) offers an [online Notebooks product](https://www.anaconda.com/products/notebooks) (similar to Google's Colab) that allows you to develop and deploy Panel applications from JupyterLab notebooks.

As of September 2025:

- 1 application can be published with the Free Tier, 4 with the Starter Tier, and 10 with the Business Tier (more information on the [Pricing page](https://www.anaconda.com/pricing)).
- Panel is part of the [Anaconda Distribution](https://www.anaconda.com/docs/getting-started/anaconda/main) and as such is available in the conda environments already made available to you in the platform.
- You cannot choose the deployment name; it will instead be automatically generated from a combination of random words (e.g., `https://spirited-spotted-python.anacondaapps.cloud`).
- All deployed applications are public by default.

Refer to [Anaconda's Notebooks documentation](https://www.anaconda.com/docs/tools/anaconda-notebooks/getting-started) to find out more about this product.

## Create an app

1. Create an account on [anaconda.com](https://www.anaconda.com/) and visit your personal space at https://anaconda.com/app.

2. Open the Notebooks product (quick link: https://nb.anaconda.com) to launch a JupyterLab session.

3. Create a new notebook and start coding your Panel application. If you need to know more about developing Panel applications in JupyterLab, visit the [notebooks how-to guides](../notebook/index.md). In particular, the most practical way to develop an application is to enable the Preview functionality in JupyterLab. See the [corresponding how-to guide](../notebook/jupyterlabpreview.md) for more information.

![anaconda-notebooks-preview](https://assets.holoviz.org/panel/how_to/deployment/anaconda_notebooks/anaconda_notebooks_preview.png)

## Deploy an app

1. Once your application is ready to be deployed, click on the "Save and Publish" icon button located in the toolbar.

![anaconda-notebooks-publish-icon](https://assets.holoviz.org/panel/how_to/deployment/anaconda_notebooks/anaconda_notebooks_publish_icon.png)

2. Click on the "Publish" button of the modal that gets displayed.

![anaconda-notebooks-publish-modal](https://assets.holoviz.org/panel/how_to/deployment/anaconda_notebooks/anaconda_notebooks_publish_modal.png)

3. Your application is deployed!

To update an existing application, simply update your code and repeat the process described in this section. Note the original deployment URL is preserved.

Refer to [Anaconda's documentation on how to publish notebooks](https://www.anaconda.com/docs/tools/anaconda-notebooks/publishing-notebooks) for more information.

## Manage an app

1. Open the Launcher and click on "My Apps" (alternatively, click on the apps count in the header) to open the *App Management* view.

2. Click on the three vertical dots in your app card to access more information about it. For example, click on "Copy app link" to find out at which URL your app has been deployed and share it with your users.

![anaconda-notebooks-app-management](https://assets.holoviz.org/panel/how_to/deployment/anaconda_notebooks/anaconda_notebooks_app_management.png)

## Try it out

The screenshots displayed on this page originate from an app that has been deployed on Anaconda Notebooks:

- You can inspect and open the notebook with this URL: https://anaconda.com/app/share/notebooks/300335e6-88c3-4555-bad3-7c1e66bb4b57/overview
- The app is publicly deployed at this URL: https://bright-calabar-python.anacondaapps.cloud/anaconda_cloud_for_panel_docs
