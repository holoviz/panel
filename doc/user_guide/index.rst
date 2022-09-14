User Guide
==========

The Panel user guide introduces the main concepts required for
building interactive apps and dashboards using Panel, and gives
an overview of the functionality available. The guide is split
into core, reference, and supplementary sections.

Core Guide
----------

To get an initial understanding of the core concepts and components of Panel and
how to use it in practice, it is recommended that all users go through each of
the core guide sections.

`Overview <Overview.html>`_
 A high-level overview of the key concepts behind Panel.

`Components <Components.html>`_
 An introduction to the three main component types: Widgets, Panes, and Panels.

`APIs <APIs.html>`_
 An introduction to the different APIs panel provides to build interactive applications and dashboards.

Reference guide
---------------

The reference guides provide a more in-depth treatment of some of the
APIs and components in Panel, with detailed information that you can refer to
when needed.

`Customization <Customization.html>`_
 How to customize the visual appearance, layout, and size of Panel components.

`Interact <Interact.html>`_
 Quickly making a panel using `interact()`.

`Widgets <Widgets.html>`_
 Declaring and working with Panel widgets.

`Parameters <Param.html>`_
 Using Param to express panels in a self-contained class.

`Linking <Links.html>`_
 Defining links between Panel objects in Python and Javascript.

`Templates <Templates.html>`_
 Learn how to compose multiple Panels into a custom HTML document.

`Pipelines <Pipelines.html>`_
 Using Parameterized classes to declare linear workflows containing multiple panels.

`Performance, Profiling and Debugging <Performance_and_Debugging.html>`_
 Learn how to speed up your application and find issues.

State, Caching & Callbacks
^^^^^^^^^^^^^^^^^^^^^^^^^^

`Session State and Callbacks <Session_State_and_Callbacks.html>`_
 Learn how to access session state and schedule callbacks.

`Asynchronous and Concurrent Processing <Async_and_Concurrency.html>`_
 Learn how leverage asynchronous and concurrent processing to make your app more responsive.

Export
^^^^^^

`Display & Export <Display_and_Export.html>`_
 Guide towards configuring and displaying output and exporting Panel apps and components.

`Running Panel in the Browser with WASM <Running_in_Webassembly.html>`_
 Guide to embedding interactive Panel components in a web page or converting entire Panel applications to run entirely in your browser.

Server Usage
^^^^^^^^^^^^

`Server configuration <Server_Configuration.html>`_
 A guide detailing how to launch and configure a server from the commandline or programmatically.

`Server Deployment <Server_Deployment.html>`_
 Step-by-step guides for deploying Panel apps locally, on a web server or on common cloud providers.

`Authentication <Authentication.html>`_
 Learn how to add an authentication component in front of your application.

`Django Integration <Django.html>`_
 How to embed a Panel/Bokeh app inside a Django web-server deployment.

`FastAPI Integration <FastAPI.html>`_
 How to embed a Panel/Bokeh app inside a FastAPI web-server deployment.

Extending Panel
^^^^^^^^^^^^^^^

`Building custom components <Custom_Components.html>`_
 Learn how to extend Panel by building custom components.


.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 2

    Overview <Overview>
    Components <Components>
    APIs <APIs>
    Customization <Customization>
    Interact <Interact>
    Widgets <Widgets>
    Parameters <Param>
    Linking <Links>
    Pipelines <Pipelines>
    Templates <Templates>
    Performance and Debugging <Performance_and_Debugging>
    Session state & Callbacks <Session_State_and_Callbacks>
    Asynchronous and Concurrent Process <Async_and_Concurrency>
    Display & Export <Display_and_Export>
    Running Panel in the Browser with WASM <Running_in_Webassembly>
    Server Configuration <Server_Configuration>
    Server Deployment <Server_Deployment>
    Authentication <Authentication>
    Django Integration <Django>
    FastAPI Integration <FastAPI>
    Building Custom Components <Custom_Components>
