# Roadmap

*Last updated: December 2025*

Panel continues to evolve as a flexible, high-level framework for building interactive data applications in Python. As the ecosystem matures, our roadmap reflects a shift toward **clearer boundaries for the core library**, **stronger developer ergonomics**, **modernized UI foundations**, and **better performance and scalability**, while continuing to invest heavily in documentation and learning resources.

## UI and Design Foundations

### Integrate panel-material-ui into Panel core

The `panel-material-ui` extension library was released in early 2025 and has reached a level of maturity and stability that makes us confident in saying it is the future of Panel. To reflect this:

* `panel-material-ui` components will be integrated directly into Panel core
* Existing legacy widget and layout implementations will remain available initially but marked as legacy.
* A gradual deprecation path will be established, targeting full removal of each legacy component in **Panel 3.0** if there is a suitable replacement ready.

This transition will provide a more consistent, modern UI foundation while preserving backward compatibility during the migration period.

### Clear Design and Styling Defaults

Alongside this integration, we will continue refining:

* Theme defaults
* CSS variable usage
* Customization hooks for advanced users

The aim is to make it easy to build applications that look good by default, while remaining fully customizable.

## Core Architecture and Scope

### Reduce Core Scope and Expand the Extension Ecosystem

As Panel has grown, the scope of the core library has expanded to include a wide variety of visualization backends and integrations. While powerful, this breadth increases maintenance burden as well as the JS bundle and Python package size.

Going forward, Panel will focus on a **leaner core** that provides:

* A stable application framework
* Layout, reactivity, and state management
* First-class integration with Bokeh and core rendering infrastructure

More specialized or domain-specific integrations will increasingly live in **separately versioned extension packages**, allowing them to evolve independently and reduce coupling in the core codebase.

This includes factoring out integrations such as:

* Vizzu
* Deck.gl
* Textual
* VTK
* ECharts

These extensions will continue to be supported and documented, but developed and released on their own cadence.

Separating these extensions out not only should make life simpler for the core maintainers, but also helps separate contributors drive these components forward independently of the main Panel release schedule.

## DataFrame Interoperability and Narwhals Integration

Panel has historically focused on first-class support for pandas DataFrames. While pandas remains a core part of the Python data ecosystem, many users are increasingly working with alternative DataFrame libraries that offer improved performance, scalability, or GPU acceleration.

To better support this diversity, Panel will adopt **Narwhals** as its primary DataFrame compatibility layer wherever pandas is currently supported.

### Adopt Narwhals as the DataFrame Compatibility Layer

Across Panel's APIs that accept or operate on tabular data, we will:

* Replace direct pandas-specific handling with Narwhals abstractions where applicable
* Treat pandas as one of several supported backends rather than the only one
* Expand support to additional DataFrame implementations, including:

  * Polars
  * DuckDB
  * cuDF
  * Other Narwhals-compatible libraries

This change allows Panel to interoperate with multiple DataFrame ecosystems while keeping a single, consistent internal API.

### Benefits

* **Broader ecosystem support:** Users can work with their preferred DataFrame library without converting to pandas.
* **Better performance:** Native support for columnar and lazy backends enables more efficient data handling.
* **Improved scalability:** Better alignment with large, out-of-core, and GPU-backed workflows.
* **Cleaner internals:** Reduced pandas-specific branching and special cases in Panel's codebase.

## AnyWidget Integration and External Component Ecosystems

As Panel continues to reduce core scope and lean more heavily on extensions, tighter integration with external component ecosystems becomes increasingly important. One such ecosystem is **AnyWidget**, which has emerged as a lightweight, modern foundation for building reusable frontend components with a growing community of extension authors.

Rather than duplicating this work inside Panel, we aim to **interoperate cleanly and efficiently** with AnyWidget-based components wherever possible.

### Efficient AnyWidget Pane

Panel will introduce a dedicated, optimized **AnyWidget pane** designed to:

* Embed AnyWidget-based components with minimal overhead
* Integrate cleanly with Panel layouts, theming, and reactive updates
* Work consistently across notebook and server-based Panel applications

This ensures AnyWidget components can be treated as first-class building blocks inside Panel apps, not just embedded artifacts.

### Systematic Compatibility and Upstream Collaboration

To make this integration robust and sustainable, Panel will:

* Systematically evaluate popular AnyWidget components in real Panel applications
* Identify performance, lifecycle, and rendering issues when used outside narrow contexts
* Contribute fixes and improvements upstream where possible, reducing long-term maintenance burden

This approach allows both ecosystems to evolve together without Panel-specific forks or fragile adapters.

### Panel + AnyWidget Example Gallery

To make this ecosystem approachable for users, Panel will:

* Publish an example gallery showcasing **Panel applications composed with AnyWidget components**
* Highlight patterns where AnyWidget-based components complement native Panel components
* Provide guidance on composing applications from a mix of Panel, extension, and AnyWidget elements

This reinforces Panel’s role as an **application framework and composition layer**, rather than a monolithic component library.

### What This Means for Users

* Access to a broader ecosystem of UI components without waiting for Panel-native implementations
* Clearer guidance on when to use native Panel components versus external widgets
* Better long-term stability through upstream collaboration rather than custom integrations

This work supports Panel’s broader direction toward a **leaner core**, **stronger extension story**, and **integration-first architecture**.

## Developer Experience

### Typing and IDE Support

Building on recent work in improving `param`'s typing support, Panel will:

* Expand and refine type annotations across the codebase
* Improve IDE auto-completion and static analysis
* Provide clearer type contracts for components, layouts, and reactive APIs

The goal is to make Panel applications easier to reason about, refactor, and maintain, especially in larger codebases.

### Pydantic & Dataclass Support

Panel has long supported building applications around param.Parameterized classes, providing a structured and reactive foundation for stateful applications. Building on recent advances in typing support in Param, Panel will expand this model to better interoperate with Pydantic and other dataclass-like frameworks commonly used to define structured data and application state.

This includes using these models as:

* Application state containers
* Inputs and outputs to UI components
* Configuration and validation layers for Panel applications

The goal is to allow users to define their application’s structure once, using the data-modeling tools they already rely on, and have Panel automatically adapt those models into interactive, reactive interfaces.

### Improved Hot Reload and Development Feedback Loops

We will continue to invest in improving the local development experience, with a particular focus on:

* More reliable and predictable hot reload behavior
* Faster feedback loops when developing apps and extensions
* Clearer separation between server reloads and application state resets

These improvements aim to make iterative development smoother and less error-prone.

### Better Error Messages and Debuggability

We will improve error handling throughout Panel to:

* Surface clearer, more actionable error messages
* Provide better context when errors occur in callbacks, reactive expressions, or layout construction
* Make it easier to trace errors back to user code rather than internal machinery

These improvements are particularly important for users building complex, reactive applications.

## Documentation and Learning Resources

### More Tutorials and Deeper Advanced Documentation

Documentation remains a core priority. Building on the Diátaxis-aligned restructuring, we will expand:

* End-to-end tutorials for common application patterns
* Deeper, opinionated guides for advanced topics such as:

  * Application architecture
  * State management
  * Theming and Styling
  * Performance tuning
  * Extension development

These resources are intended to help experienced users move from “it works” to “it's robust, scalable, and maintainable.”

### Continuous Documentation Maintenance

Documentation will be treated as a first-class part of development:

* Kept in sync with API changes
* Updated alongside deprecations and migrations
* Expanded as new best practices emerge

## Performance and Scalability

### Performance Improvements Across the Stack

We will continue profiling and optimizing performance, with particular attention to:

* Reducing overhead in reactive updates
* Improving rendering efficiency
* Lowering latency in interactive applications

### Free-Threading and Concurrency Support

As Python's free-threading ecosystem matures, Panel will explore:

* Compatibility with free-threaded Python builds
* Safer and more efficient concurrency patterns
* Reduced reliance on single-threaded execution where feasible

### Easier Scaling Out of the Box

To support larger deployments, we aim to make scaling more approachable by:

* Improving documentation and defaults for multi-process and distributed setups
* Making it easier to deploy Panel apps behind common production infrastructures
* Reducing the amount of bespoke configuration required for horizontal scaling

## What This Means for Existing Users

As Panel evolves toward a more streamlined core and modern UI foundation, the following guidance outlines how existing users will experience and navigate the transition, especially around UI components and widget APIs.

### Modern UI with Material Design

Panel is transitioning its widget and UI ecosystem toward a **Material UI–based implementation** (provided by the `panel-material-ui` extension), which offers a modern, consistent, and themeable set of components. ([panel-material-ui.holoviz.org][2])

To support a smooth migration, Panel will introduce a new **opt-in namespace** (e.g., `panel.v2` or `panel.ui`) that exposes next-generation components backed by this modern UI stack. This allows users to adopt the new API incrementally without breaking existing applications. ([GitHub][1])

* **Opt-in modern API:**
  You'll be able to import and use updated widgets via a dedicated namespace (e.g., `panel.ui`) while the legacy API remains unchanged for now. ([GitHub][1])

* **Commercial and community feedback:**
  This approach allows documentation and examples to evolve toward modern widgets while preserving stability for production apps. ([GitHub][1])

### Backwards Compatibility and Migration Path

The existing main widget modules (`panel.widgets`, `panel.pane`, `panel.layout`) will continue to work in the short term, but they are considered **legacy** and the eventual plan is to phase them out around the **Panel 3.0** release.

* **No immediate breakage:**
  Current applications using `pn.widgets.*`, `pn.pane.*`, and `pn.layout.*` will continue to function as before.

* **Dual support during transition:**
  Both legacy and modern widgets will coexist. You can migrate individual parts of your application progressively to the modern UI namespace without a big rewrite. ([GitHub][1])

* **Namespace choice and evolution:**
  The implementation may use a versioned namespace (`panel.v2`) or a named module (`panel.ui`). The choice will be finalized through community discussion, but either way the goal is to provide a stable **future API surface** that can evolve independently of legacy constraints. ([GitHub][1])

### Documentation and Examples

Documentation will support this transition by:

* Showing modern API usage in new guides and tutorials.
* Clearly labeling legacy APIs as “legacy” in examples and reference documentation.
* Providing migration guides that map legacy widget patterns to their modern counterparts.

This ensures that users learning Panel today will see the modern UI stack as the **recommended default** over time. ([GitHub][1])

### Practical Tips for Users Today

* **Try the modern components early:**
  Install and experiment with `panel-material-ui`. It's compatible with Panel and offers more consistent theming out of the box. ([panel-material-ui.holoviz.org][2])

* **Use the opt-in namespace for new work:**
  When building new dashboards or components, import widgets from the new namespace (`panel.ui` or similar) when available.

* **Prepare for deprecation:**
  Begin auditing usage of legacy modules (`panel.widgets`, `panel.pane`, `panel.layout`) in your codebase so you can plan a gradual migration before Panel 3.0.

## Migration Timeline

To ensure stability for existing applications while allowing Panel to modernize its UI and architecture, changes will be rolled out gradually across major releases.

### Panel 1.x (Current → Early 2026)

**Status:** Stable, fully supported

* Add support for some of the changed APIs for legacy components, e.g. `Widget.name` -> `Widget.label`, `Button.button_type` -> `Button.color` and `Button.button_style` -> `Button.variant`
* `panel.layout`, `panel.pane`, and `panel.widgets` remain the default and fully supported APIs.
* `panel-material-ui` continues to be available as an external package.
* Experimental and early-adopter work continues on:

  * Improved typing and error messages
  * Performance optimizations
  * Extension-first architecture.

**What users should do**

* No action required for existing applications.
* Users are encouraged to experiment with `panel-material-ui` and provide feedback.

### Panel 2.0: *Target: Q2 2026*

**Theme:** Dual APIs, opt-in future

This release introduces the **next-generation UI API** while maintaining full backward compatibility.

* A new, opt-in namespace is introduced (tentatively `panel.ui`) exposing:

  * Material UI–based widgets and components
  * Modern defaults for styling, layout, and interaction
* `panel-material-ui` components are integrated into Panel core and re-exported via the new namespace.
* Existing modules:

  * `panel.widgets`
  * `panel.pane`
  * `panel.layout`
    remain fully functional and supported, but are clearly documented as **legacy APIs**.

**Documentation changes**

* New tutorials and examples default to `panel.ui`.
* Legacy APIs are explicitly labeled as such in reference docs.
* Initial migration guides become available, mapping legacy components to their modern equivalents.

**What users should do**

* New applications are encouraged to use `panel.ui`.
* Existing applications can migrate incrementally, component by component.
* No breaking changes required.

### Panel 2.x (Mid 2026 → 2027)

**Theme:** Migration and consolidation

* Continued refinement of `panel.ui` based on real-world usage.
* Performance improvements and scaling enhancements land primarily in the modern API.
* Legacy APIs remain supported but receive minimal new feature development.
* Deprecation warnings may be introduced for legacy modules, with clear messaging and timelines.

**What users should do**

* Actively plan migration paths for larger or long-lived applications.
* Adopt modern components where possible to benefit from performance and UX improvements.

### Panel 3.0: *Target: 2027*

**Theme:** Modern-by-default

* `panel.ui` becomes the primary and recommended API surface.
* `panel.layout`, `panel.pane`, and `panel.widgets` are formally deprecated and may be removed.
* The core library reflects a slimmer scope, with advanced or specialized functionality living in extensions.
* A consistent, Material UI–based component system is the default experience.

**What users should do**

* Ensure applications have migrated to `panel.ui`.
* Remove dependencies on legacy modules.
* Take advantage of the cleaner API, improved performance, and more scalable defaults.

[1]: https://github.com/holoviz/panel/issues/8326 "Define migration plan for integrating panel-material-ui into core Panel · Issue #8326 · holoviz/panel · GitHub"
[2]: https://panel-material-ui.holoviz.org/?utm_source=chatgpt.com "Panel Material UI - HoloViz"
