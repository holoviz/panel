# panel.pipeline module

class panel.pipeline.Pipeline(stages=\[\], graph={}, **params)
Bases: [Viewer](panel.viewable.md#panel.viewable.Viewer)

A Pipeline represents a directed graph of stages, which each return a
panel object to render. A pipeline therefore represents a UI workflow of
multiple linear or branching stages.

The Pipeline layout consists of a number of sub-components:

- header:

  - title: The name of the current stage.

  - error: A field to display the error state.

  - network: A network diagram representing the pipeline.

  - buttons: All navigation buttons and selectors.

  - prev_button: The button to go to the previous stage.

  - prev_selector: The selector widget to select between previous
    branching stages.

  - next_button: The button to go to the previous stage

  - next_selector: The selector widget to select the next branching
    stages.

- stage: The contents of the current pipeline stage.

By default any outputs of one stage annotated with the param.output
decorator are fed into the next stage. Additionally, if the
inherit_params parameter is set any parameters which are declared on
both the previous and next stage are also inherited.

The stages are declared using the add_stage method and must each be
given a unique name. By default any stages will simply be connected
linearly, but an explicit graph can be declared using the define_graph
method.

Methods

|  |  |
|----|----|
| [add_stage](#panel.pipeline.Pipeline.add_stage)(name, stage, **kwargs) | Adds a new, named stage to the Pipeline. |
| [define_graph](#panel.pipeline.Pipeline.define_graph)(graph\[, force\]) | Declares a custom graph structure for the Pipeline overriding the default linear flow. |

**Parameter Definitions**

------------------------------------------------------------------------

`auto_advance`` ``=`` ``Boolean(default=False,`` ``label='Auto`` ``advance')`
Whether to automatically advance if the ready parameter is True.

`debug`` ``=`` ``Boolean(default=False,`` ``label='Debug')`
Whether to raise errors, useful for debugging while building an
application.

`inherit_params`` ``=`` ``Boolean(default=True,`` ``label='Inherit`` ``params')`
Whether parameters should be inherited between pipeline stages.

`next_parameter`` ``=`` ``String(allow_None=True,`` ``label='Next`` ``parameter')`
Parameter name to watch to switch between different branching stages

`ready_parameter`` ``=`` ``String(allow_None=True,`` ``label='Ready`` ``parameter')`
Parameter name to watch to check whether a stage is ready.

`show_header`` ``=`` ``Boolean(default=True,`` ``label='Show`` ``header')`
Whether to show the header with the title, network diagram, and buttons.

`next`` ``=`` ``Event(default=False,`` ``label='Next')`

`previous`` ``=`` ``Event(default=False,`` ``label='Previous')`

add_stage(name, stage, **kwargs)
Adds a new, named stage to the Pipeline.

Parameters:
**name: str**
A string name for the Pipeline stage

**stage: param.Parameterized**
A Parameterized object which represents the Pipeline stage.

****kwargs: dict**
Additional arguments declaring the behavior of the stage.

define_graph(graph, force=False)
Declares a custom graph structure for the Pipeline overriding the
default linear flow. The graph should be defined as an adjacency
mapping.

Parameters:
**graph: dict**
Dictionary declaring the relationship between different pipeline stages.
Should map from a single stage name to one or more stage names.

[![Support us with a star on
GitHub](https://img.shields.io/github/stars/holoviz/panel?style=social&label=Star%20on%20%20GitHub%E2%AD%90)](https://github.com/holoviz/panel)

On this page
