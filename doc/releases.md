# Releases

## Version 0.12.1

Date: 2021-08-10

This is a patch release with a small number of fixes following the 0.12.0 release. Many thanks to the maintainers @MarcSkovMadsen and @philippjfr for the fixes in this release.

Enhancements:

- Bundle .map files during build to allow source mapping ([#2591](https://github.com/holoviz/panel/issues/2591))
- Various style improvements for Fast templates ([#2604](https://github.com/holoviz/panel/issues/2604), [#2609](https://github.com/holoviz/panel/issues/2609), [#2611](https://github.com/holoviz/panel/issues/2611), [#2615](https://github.com/holoviz/panel/issues/2615))
- Implement hierarchical aggregation for `Tabulator` ([#2624](https://github.com/holoviz/panel/issues/2624))

Bug fixes:

- Fix logo on Fast templates ([#2184](https://github.com/holoviz/panel/issues/2184))
- Fix height responsiveness of Folium pane ([#2231](https://github.com/holoviz/panel/issues/2231))
- Fix bug updating `Tqdm` indicator ([#2554](https://github.com/holoviz/panel/issues/2554))
- Ensure `--autoreload` doesn't error on cleaned up session ([#2570](https://github.com/holoviz/panel/issues/2570))
- Don't use persisted layout if `save_layout=False` ([#2579](https://github.com/holoviz/panel/issues/2579))
- Pin version of tqdm with asyncio support ([#2595](https://github.com/holoviz/panel/issues/2595))
- Reset layout when resetting grid template layout ([#2576](https://github.com/holoviz/panel/issues/2576))
- Fix line-height issues in Fast templates ([#2600](https://github.com/holoviz/panel/issues/2600))
- Clean up sessions after warmup and ensure periodic callbacks are cleaned up ([#2601](https://github.com/holoviz/panel/issues/2601))

Documentation:

- Enable JupyterLab preview button on binder ([#2545](https://github.com/holoviz/panel/issues/2545))
- Update theme toggle documentation for Fast templates ([#2560](https://github.com/holoviz/panel/issues/2560))
- Update Fast template documentation and enable full screen ([#2577](https://github.com/holoviz/panel/issues/2577))
- Fix binder links on website ([#2590](https://github.com/holoviz/panel/issues/2590))
- Add docs about loading the ipywidgets extension ([#2594](https://github.com/holoviz/panel/issues/2594))


## Version 0.12.0

Date: 2021-07-18

Blog post: https://blog.holoviz.org/panel_0.12.0.html

The 0.12.0 release is a minor release with a lot of exciting and a huge amount of bug fixes. We are very excited about the growing community and the many contributions we received. In particular we would like to thank @douglas-raillard-arm, @mathrick, @jlstevens, @hyamanieu, @Liam-Deacon, @Stubatiger, @ablythed, @syamajala, @Hoxbro, @jbednar, @brl0, @OBITORASU, @fleming79, dhruvbalwada and @rmorshea for contributing various fixes and improvements and the core developers @xavArtley, @MarcSkovMadsen and @philippjfr for continuing to push the development of Panel.

Features:

- Add `ReactiveHTML` ([#1894](https://github.com/holoviz/panel/issues/1894), [#2091](https://github.com/holoviz/panel/issues/2091), [#2092](https://github.com/holoviz/panel/issues/2092), [#2098](https://github.com/holoviz/panel/issues/2098), [#2115](https://github.com/holoviz/panel/issues/2115), [#2210](https://github.com/holoviz/panel/issues/2210), [#2287](https://github.com/holoviz/panel/issues/2287), [#2290](https://github.com/holoviz/panel/issues/2290), [#2332](https://github.com/holoviz/panel/issues/2332), [#2345](https://github.com/holoviz/panel/issues/2345), [#2372](https://github.com/holoviz/panel/issues/2372), [#2373](https://github.com/holoviz/panel/issues/2373), [#2374](https://github.com/holoviz/panel/issues/2374), [#2383](https://github.com/holoviz/panel/issues/2383), [#2384](https://github.com/holoviz/panel/issues/2384), [#2393](https://github.com/holoviz/panel/issues/2393), [#2397](https://github.com/holoviz/panel/issues/2397), [#2399](https://github.com/holoviz/panel/issues/2399), [#2400](https://github.com/holoviz/panel/issues/2400), [#2401 [#2402](https://github.com/holoviz/panel/issues/2402), [#2404](https://github.com/holoviz/panel/issues/2404), [#2533](https://github.com/holoviz/panel/issues/2533), [#2535](https://github.com/holoviz/panel/issues/2535))
- Add `Terminal` Widget based on xterm.js ([#2090](https://github.com/holoviz/panel/issues/2090))
- Adding a `DatetimePicker` widget ([#2107](https://github.com/holoviz/panel/issues/2107), [#2135](https://github.com/holoviz/panel/issues/2135))
- Add editable sliders ([#2111](https://github.com/holoviz/panel/issues/2111), [#2133](https://github.com/holoviz/panel/issues/2133), [#2208](https://github.com/holoviz/panel/issues/2208))
- Add `FlexBox` layout ([#2233](https://github.com/holoviz/panel/issues/2233), [#2511](https://github.com/holoviz/panel/issues/2511))
- Add ability to configure global template ([#2271](https://github.com/holoviz/panel/issues/2271))
- Add `GridStack` layout ([#2375](https://github.com/holoviz/panel/issues/2375))
- Add `PDF` pane ([#2444](https://github.com/holoviz/panel/issues/2444))
- Add `/panel-preview` endpoint for Jupyter server extension ([#2341](https://github.com/holoviz/panel/issues/2341), [#2361](https://github.com/holoviz/panel/issues/2361))
- Add `Tqdm` Indicator ([#2079](https://github.com/holoviz/panel/issues/2079))

Enhancements:

- Add empty `Progress` bar ([#2088](https://github.com/holoviz/panel/issues/2088))
- Optimize initialization of templates ([#2096](https://github.com/holoviz/panel/issues/2096))
- Serialize `Perspective` schema ([#2130](https://github.com/holoviz/panel/issues/2130))
- Updated `JSON` pane to accept single quote and wrap properly ([#2143](https://github.com/holoviz/panel/issues/2143), [#2443](https://github.com/holoviz/panel/issues/2443))
- Improvements for `Perspective` ([#2153](https://github.com/holoviz/panel/issues/2153))
- Improve handling of server prefix and proxied deployment scenarios ([#2159](https://github.com/holoviz/panel/issues/2159), [#2162](https://github.com/holoviz/panel/issues/2162))
- Add support for setting bokeh theme ([#2164](https://github.com/holoviz/panel/issues/2164), [#2166](https://github.com/holoviz/panel/issues/2166), [#2170](https://github.com/holoviz/panel/issues/2170))
- Completely overhauled the default index template ([#2198](https://github.com/holoviz/panel/issues/2198), [#2340](https://github.com/holoviz/panel/issues/2340))
- Enhancements for `Template` modals ([#2269](https://github.com/holoviz/panel/issues/2269), [#2523](https://github.com/holoviz/panel/issues/2523))
- Make the Template sidebar width configurable ([#2301](https://github.com/holoviz/panel/issues/2301))
- Improve look and feel and styling of Fast templates ([#2303](https://github.com/holoviz/panel/issues/2303), [#2469](https://github.com/holoviz/panel/issues/2469), [#2484](https://github.com/holoviz/panel/issues/2484), [#2488](https://github.com/holoviz/panel/issues/2488))
- Allow setting kwargs in `Reactive.controls` ([#2304](https://github.com/holoviz/panel/issues/2304))
- Add global configuration variable to always throttle sliders ([#2306](https://github.com/holoviz/panel/issues/2306))
- Add support for controlling text alignment in `DataFrame` and `Tabulator` ([#2331](https://github.com/holoviz/panel/issues/2331))
- Add `Tabulator` theme for Fast Templates ([#2425](https://github.com/holoviz/panel/issues/2425))
- Add ability to make only certain `Tabulator` rows selectable ([#2433](https://github.com/holoviz/panel/issues/2433))
- Add `visible` parameter to all components ([#2440](https://github.com/holoviz/panel/issues/2440))
- Send `Plotly` restyle and relayout events rather than full updates ([#2445](https://github.com/holoviz/panel/issues/2445))
- Add `push_notebook` helper function for syncing bokeh property changes in notebooks ([#2447](https://github.com/holoviz/panel/issues/2447))
- Improve visual styling of `Card` ([#2343](https://github.com/holoviz/panel/issues/2343), [#2348](https://github.com/holoviz/panel/issues/2348), [#2376](https://github.com/holoviz/panel/issues/2376), [#2437](https://github.com/holoviz/panel/issues/2437), [#2527](https://github.com/holoviz/panel/issues/2437))
- Ensure `config` variables are configured per user session ([#2358](https://github.com/holoviz/panel/issues/2358), [#2455](https://github.com/holoviz/panel/issues/2455), [#2481](https://github.com/holoviz/panel/issues/2481))
- Add `save_layout` and `prevent_collision` to `ReactTemplate` and `FastGridTemplate` ([#2296](https://github.com/holoviz/panel/issues/2296), [#2357](https://github.com/holoviz/panel/issues/2357))
- Add ability to declare root application from `panel serve` ([#2392](https://github.com/holoviz/panel/issues/2392))
- Support jslinking Parameterized class ([#2441](https://github.com/holoviz/panel/issues/2441))
- Improve `config.sizing_mode` behavior ([#2442](https://github.com/holoviz/panel/issues/2442))
- Add separate `RangeSlider` `value_start` and `value_end` parameters ([#2457](https://github.com/holoviz/panel/issues/2457), [#2468](https://github.com/holoviz/panel/issues/2468))
- Allow saving Templates ([#2461](https://github.com/holoviz/panel/issues/))
- Bundle `Tabulator` resources to allow usage in airgapped environment ([#2471](https://github.com/holoviz/panel/issues/2471))
- Ensure `Trend` indicator title wraps ([#2483](https://github.com/holoviz/panel/issues/2483))
- Scroll on `Tabulator` selection ([#2503](https://github.com/holoviz/panel/issues/2503))
- Increase notebook resource load timeout ([#2515](https://github.com/holoviz/panel/issues/2515))
- Auto-detect VSCode and Colab comms ([#2536](https://github.com/holoviz/panel/issues/2536))
- Add tooltip to ``Tabulator`` cells to see unformatted value ([#2543](https://github.com/holoviz/panel/issues/2543))

Bug fixes:

- Fix missing video in `Video` ([#2109](https://github.com/holoviz/panel/issues/2109))
- use idom.config to set dist dir ([#2117](https://github.com/holoviz/panel/issues/2117))
- Remove bootstrap CSS from `FastGridTemplate` ([#2123](https://github.com/holoviz/panel/issues/2123))
- Fix issues with `Ace` z-index ([#2126](https://github.com/holoviz/panel/issues/2126))
- Fix updating of `Tabulator` selection property ([#2128](https://github.com/holoviz/panel/issues/2128))
- Ensure changes on ReactiveData source are scheduled correctly ([#2134](https://github.com/holoviz/panel/issues/2134))
- Fixed `Player` looping when start is 0 ([#2141](https://github.com/holoviz/panel/issues/2141))
- Fix divide by zero issues on Trend indicator ([#2148](https://github.com/holoviz/panel/issues/2148))
- Ensure `GridSpec` override handles duplicate matches ([#2150](https://github.com/holoviz/panel/issues/2150))
- Fix for `loading` parameter widget linking ([#2160](https://github.com/holoviz/panel/issues/2160))
- Fix `Tabulator` ajax call on empty data ([#2161](https://github.com/holoviz/panel/issues/2161))
- Fix `Tabulator` sorting and data initialization ([#2163](https://github.com/holoviz/panel/issues/2163))
- Fix editing `Tabulator` with filters applied ([#2165](https://github.com/holoviz/panel/issues/2165))
- Fix theming on `HoloViews` plot updates ([#2209](https://github.com/holoviz/panel/issues/2209))
- Fixed data handling on `Perspective` pane ([#2212](https://github.com/holoviz/panel/issues/2212))
- Improve template and resource management for png export ([#2221](https://github.com/holoviz/panel/issues/2221))
- Improve and standardize selection behavior of `Tabulator` ([#2230](https://github.com/holoviz/panel/issues/2230))
- Ensure JS changes to `Plotly` pane are applied if not explicitly triggered ([#2251](https://github.com/holoviz/panel/issues/2251))
- Fix server-side Tabulator selection changes ([#2252](https://github.com/holoviz/panel/issues/2252))
- Fix update of `Param` subobjects ([#2255](https://github.com/holoviz/panel/issues/2255))
- Add support for `vtkCornerAnnotations` ([#2257](https://github.com/holoviz/panel/issues/2257))
- Improve request handling for remote pagination on `Tabulator` ([#2265](https://github.com/holoviz/panel/issues/2265))
- Allow setting `Param` precedence to None ([#2266](https://github.com/holoviz/panel/issues/2266))
- Disable nested field separators on `Tabulator` ([#2289](https://github.com/holoviz/panel/issues/2289))
- Fix errors when applying `Perspective` filters ([#2300](https://github.com/holoviz/panel/issues/2300), [#2521](https://github.com/holoviz/panel/issues/2521))
- Ensure `Param` pane handles changes to unknown parameter ([#2346](https://github.com/holoviz/panel/issues/2346))
- Fix issues with local `Audio` and `Video` ([#2380](https://github.com/holoviz/panel/issues/2380))
- Ensure `ReactiveData` emits correct old data in event ([#2398](https://github.com/holoviz/panel/issues/2398))
- Ensure `Plotly` interactivity works when `Plotly` panes are displayed in tabs ([#2418](https://github.com/holoviz/panel/issues/2418), [#2463](https://github.com/holoviz/panel/issues/))
- Fix `Ace` widget disabled parameter ([#2449](https://github.com/holoviz/panel/issues/2449))
- Ensure external resources are configured correctly on save ([#2452](https://github.com/holoviz/panel/issues/2452))
- Ensure table formatters and editors are copied on render to avoid bokeh errors ([#2453](https://github.com/holoviz/panel/issues/2453))
- Allow unicode auth response body ([#2462](https://github.com/holoviz/panel/issues/2462))
- Workaround TypeError for non-string json keys on `Plotly` pane ([#2465](https://github.com/holoviz/panel/issues/2465))
- Fix issue with throttled updates on Param ([#2470](https://github.com/holoviz/panel/issues/2470))
- Ensure `Tabulator` style is applied while streaming ([#2478](https://github.com/holoviz/panel/issues/2478))
- Fix issues setting resources on save ([#2492](https://github.com/holoviz/panel/issues/2492))
- Fix `VideoStream` unpause ([#2508](https://github.com/holoviz/panel/issues/2508))
- Ensure `DataFrame` and `Tabulator` widget data can be updated in callback ([#2510](https://github.com/holoviz/panel/issues/2510))
- Fix chaining of `bind` functions ([#2513](https://github.com/holoviz/panel/issues/2513))
- Fix broken serialisation when syncing url parameters ([#2520](https://github.com/holoviz/panel/issues/2520))
- Fix `Perspective` for string types ([#2525](https://github.com/holoviz/panel/issues/2525))
- Fix race condition in `--autoreload` ([#2539](https://github.com/holoviz/panel/issues/2539))

Documentation:

- Update `Server_Deployment.ipynb` ([#2118](https://github.com/holoviz/panel/issues/2118))
- Expand description of `watch=True` in `Param.ipynb` ([#2120](https://github.com/holoviz/panel/issues/2120))
- Switch to PyData Sphinx Theme ([#2139](https://github.com/holoviz/panel/issues/2139))
- Replace altair iris example with penguins ([#2213](https://github.com/holoviz/panel/issues/2213))
- Enable Binder ([#2198](https://github.com/holoviz/panel/issues/2198))
- Updates and fixes for Developer Guide ([#2381](https://github.com/holoviz/panel/issues/2381))
- Fixed `Tabs` documentation ([#2448](https://github.com/holoviz/panel/issues/2448))
- Added basic description and example of the `Tabulator.configuration` parameter ([#2412](https://github.com/holoviz/panel/issues/2412))
- Add parameters to `Plotly` reference guide ([#2385](https://github.com/holoviz/panel/issues/2385))
- Add useful links to developer docs ([#2319](https://github.com/holoviz/panel/issues/2319))
- Add documentation about parameterized components ([#2454](https://github.com/holoviz/panel/issues/2454))
- Demonstrate how to lazily load tabs ([#2479](https://github.com/holoviz/panel/issues/2479))

Compatibility:

- Compatibility with HoloViews 2.0 ([#2344](https://github.com/holoviz/panel/issues/2344))
- Fix Tabulator styling with pandas 1.3 ([#2512](https://github.com/holoviz/panel/issues/2512))

Deprecations:

- Remove add_periodic_callback method ([#2439](https://github.com/holoviz/panel/issues/2439))
- Remove deprecated panel.callbacks modules
- Remove deprecated Ace pane and Audio Widget ([#2427](https://github.com/holoviz/panel/issues/2427))
- Remove Progress widget docs ([#2451](https://github.com/holoviz/panel/issues/2451))
- Tabulator no longer loaded by default, must be initialized with `pn.extension('tabulator'](https://github.com/holoviz/panel/issues/))` ([#2364](https://github.com/holoviz/panel/issues/2364))

## Version 0.11.3

Date: 2021-04-14

The 0.11.3 release is another micro-release in the 0.11 series primarily focused on updating the documentation theme and a regression in loading `Tabulator` data.

Bug fixes:

- Fix `Tabulator` sorting and data initialization ([#2163](https://github.com/holoviz/panel/issues/2163))
- Improved handling of `IDOM` build directory ([#2168](https://github.com/holoviz/panel/issues/2168))

Documentation:

- Switch to PyData Sphinx Theme ([#2139](https://github.com/holoviz/panel/issues/2139))


## Version 0.11.2

Date: 2021-04-08

The 0.11.2 release is a micro-release fixing a number of smaller bugs. Many thanks to @Hoxbro, @dhruvbalwada, @rmorshea, @MarcSkovMadsen, @fleming79, @OBITURASU and @philippjfr for their contributions to this release.

Enhancements:

- Optimize adding of roots to templates to avoid multiple preprocessing cycles ([#2096](https://github.com/holoviz/panel/issues/2096))
- Use schema to support date(time) dtypes on `Perspective` ([#2130](https://github.com/holoviz/panel/issues/2130))

Bug fixes:

- Fix regression on `Video` pane causing video not to be rendered at all ([#2109](https://github.com/holoviz/panel/issues/2109))
- Fix missing closing tag in Fast templates ([#2121](https://github.com/holoviz/panel/issues/2121))
- Remove bootstrap CSS from `FastGridTemplate` ([#2123](https://github.com/holoviz/panel/issues/2123))
- Ensure `Tabulator` selection can be set from Python ([#2128](https://github.com/holoviz/panel/issues/2128))
- Ensure changes on ReactiveData objects are scheduled correctly on server ([#2134](https://github.com/holoviz/panel/issues/2134))
- Fix for `Player` widget when start value is 0 ([#2141](https://github.com/holoviz/panel/issues/2141))
- Support single quotes on JSON pane ([#2143](https://github.com/holoviz/panel/issues/2143))
- Fix divide by zero issues when value_change is computed from zero baseline ([#2148](https://github.com/holoviz/panel/issues/2148))
- Ensure `GridSpec` handles overrides across multiple cells ([#2150](https://github.com/holoviz/panel/issues/2150))
- Fix for `loading` parameter widget linking ([#2160](https://github.com/holoviz/panel/issues/2160))
- Use relative URLs for resource loading to ensure proxied apps work ([#2159](https://github.com/holoviz/panel/issues/2159))
- Fix `Tabulator` ajax call on empty data ([#2161](https://github.com/holoviz/panel/issues/2161))

Documentation:

- Fix typo in Binder section of server deployment documentation ([#2118](https://github.com/holoviz/panel/issues/2118))
- Improve documentation surrounding watch=True in Param user guide ([#2120](https://github.com/holoviz/panel/issues/2120))

Compatibility:

- Ensure IDOM pane configures paths correctly for latest version ([#2117](https://github.com/holoviz/panel/issues/2127), [#2132](https://github.com/holoviz/panel/issues/2132))

## Version 0.11.1

Date: 2021-03-15

The 0.11.1 release is a micro-release addressing a number of smaller
bugs in the last release. Many thanks to the contributors to this
release including @Hoxbro, @xavArtley, @Jacob-Barhak and @philippjfr.

Enhancements:

- Allow setting horizontal and vertical alignment separately ([#2072](https://github.com/holoviz/panel/issues/2072))
- Expose widgets `visible` property ([#2065](https://github.com/holoviz/panel/issues/2065))
- Allow bind to extract dependencies and evaluate other dynamic functions ([#2056](https://github.com/holoviz/panel/issues/2056))
- Allow setting `root_directory` on `FileSelector` widget ([#2086](https://github.com/holoviz/panel/issues/2086()

Bug fixes:

- Fixed loading of jQuery in `BootstrapTemplate` ([#2057](https://github.com/holoviz/panel/issues/2057))
- Fix VTK imports to ensure `VTKVolume` pane renders grids ([#2071](https://github.com/holoviz/panel/issues/2071))
- Fix loading of template resources from relative paths ([#2067](https://github.com/holoviz/panel/issues/2067))
- Fix `Spinner` component overflow ([#2070](https://github.com/holoviz/panel/issues/2070))
- Handle integer column names on `Perspective` widget ([#2069](https://github.com/holoviz/panel/issues/2069))
- Fix bundling of template resources ([#2076](https://github.com/holoviz/panel/issues/2076))
- Fix `value_throttled` in `pn.depends` decorator ([#2085](https://github.com/holoviz/panel/issues/2085))

Compatibility:

- Switch GitHub OAuth to use header authorization token ([#2073](https://github.com/holoviz/panel/issues/2073))

## Version 0.11.0

Date: 2021-03-01

The 0.11.0 release brings a number of exciting new features to Panel
as well as some enhancements and bug fixes. This release is also
required for Bokeh 2.3 compatibility since a lot of changes to the
Bokeh property system required updates. Many thanks to the many
contributors to this release including @MarcSkovMadsen, @xavArtley,
@hyamanieu, @cloud-rocket, @kcpevey, @kaseyrussell, @miliante,
@AjayThorve and @philippjfr.

Major features:

- A `Perspective` pane based on the FINOS Perspective library ([#2034](https://github.com/holoviz/panel/issues/2034))
- Implement `--autoreload` functionality for the Panel server ([#1983](https://github.com/holoviz/panel/issues/1983))
- Add `--warm` option to panel serve, useful for pre-loading items into the state cache ([#1971](https://github.com/holoviz/panel/issues/1971)) 
- Add ability to define JS modules and Template specific resources ([#1967](https://github.com/holoviz/panel/issues/1967))
- `panel.serve` now supports serving static files and Bokeh apps, not just Panel apps ([#1939](https://github.com/holoviz/panel/issues/1939)) 
- Add a `TrendIndicator` for conveniently showing history and value of a numeric quantity ([#1895](https://github.com/holoviz/panel/issues/1895))
- Add `TextToSpeech` widget ([#1878](https://github.com/holoviz/panel/issues/1878))
- Add `SpeechToText` widget ([#1880](https://github.com/holoviz/panel/issues/1880))
- Add `loading` parameter and spinners to all components ([#1730](https://github.com/holoviz/panel/issues/1730), [#2026](https://github.com/holoviz/panel/issues/2026))
- Add `IDOM` pane to develop interactive HTML components in Python ([#2004](https://github.com/holoviz/panel/issues/2004))
- Add powerful new `Tabulator` widget for flexible and configurable display of tabular data ([#1531](https://github.com/holoviz/panel/issues/1531), [#1887](https://github.com/holoviz/panel/issues/1887)) 

Enhancements:

- Add watch argument to `bind` function so that covers all the features of pn.depends ([#2000](https://github.com/holoviz/panel/issues/2000))
- Add `format` parameter to DatetimeRangeInput widget ([#2043](https://github.com/holoviz/panel/issues/2043)) 
- Allow `ParamMethod` and `ParamFunction` to evaluate lazily ([#1966](https://github.com/holoviz/panel/issues/1966))
- Add `value_input` parameter to TextInput widgets ([#2007](https://github.com/holoviz/panel/issues/2007))
- Implement `Glyph3dMapper` support for `VTK` panes ([#2002](https://github.com/holoviz/panel/issues/2002), [#2003](https://github.com/holoviz/panel/issues/2003))
- Add Jupyter server extension to serve resources ([#1982](https://github.com/holoviz/panel/issues/1982))
- Enhancements for `DarkTheme` ([#1964](https://github.com/holoviz/panel/issues/1964))
- Add `refresh` functionality to `FileSelector` ([#1962](https://github.com/holoviz/panel/issues/1962))
- Add support for Auth0 authentication ([#1934](https://github.com/holoviz/panel/issues/1934))
- Avoid recursive preprocessing slowing down rendering ([#1852](https://github.com/holoviz/panel/issues/1852))
- Add support for per-layer tooltips on `DeckGL` pane ([#1846](https://github.com/holoviz/panel/issues/1846))
- Add `Viewer` baseclass for custom user components ([#2045](https://github.com/holoviz/panel/issues/2045))

Bug fixes:

- Fixed `FileSelector` file icon on selected files ([#2046](https://github.com/holoviz/panel/issues/2046))
- Drop query args when checking URLs ([#2037](https://github.com/holoviz/panel/issues/2037))
- Fix `Card.header_background` propagation ([#2035](https://github.com/holoviz/panel/issues/2035))
- Disable `GoldenTemplate` sidebar when empty ([#2017](https://github.com/holoviz/panel/issues/2017))
- Ensure `Card.collapsed` and `Accordion.active` parameters are synced ([#2009](https://github.com/holoviz/panel/issues/2009))
- Fix inline resources when saving ([#1956](https://github.com/holoviz/panel/issues/1956))
- Switch `Param` pane widget type when bounds (un)defined ([#1953](https://github.com/holoviz/panel/issues/1953))

Compatibility:

- Compatibility with Bokeh>=2.3 ([#1948](https://github.com/holoviz/panel/issues/1948), [#1988](https://github.com/holoviz/panel/issues/1988), [#1991](https://github.com/holoviz/panel/issues/1991))
- Updated `ECharts` pane to 5.0.2 of JS library ([#2016](https://github.com/holoviz/panel/issues/2016))

Documentation:

- Document pn.bind in API user guide ([#1973](https://github.com/holoviz/panel/issues/1973))

## Version 0.10.3

Date: 2021-01-18

Another micro-release in the 0.10.x series focusing primarily on bug and regression fixes. Many thanks to @miliante, @MarcSkovMadsen, @Hoxbro, @jlstevens, @jbednar and @philippjfr.

Bug fixes:

- Fix inverted axes on HoloViews plots ([#1732](https://github.com/holoviz/panel/issues/1732))
- Fix enabling/disabling of FileDownload widget ([#1510](https://github.com/holoviz/panel/issues/1510), [#1820](https://github.com/holoviz/panel/issues/1820))
- Fix issues serving template resources on server with route prefix ([#1821](https://github.com/holoviz/panel/issues/1821))
- Fixes for rendering ECharts from pyecharts ([#1874](https://github.com/holoviz/panel/issues/1874), [#1876](https://github.com/holoviz/panel/issues/1876))
- Fix issues with scroll behavior when expanding/collapsing Card/Accordion ([#1833](https://github.com/holoviz/panel/issues/1833), [#1884](https://github.com/holoviz/panel/issues/1884))
- Ensure DiscreSlider label is correctly linked to value ([#1906](https://github.com/holoviz/panel/issues/1906))
- Fix support for setting header_color and header_background on all templates ([#1872](https://github.com/holoviz/panel/issues/1872))
- Ensure that Template preprocessors are applied during initialization ([#1922](https://github.com/holoviz/panel/issues/1922))

Enhancements:

- Support throttled in Param widget ([#1800](https://github.com/holoviz/panel/pull/1800))
- Support rendering of hvPlot Interactive objects ([#1824](https://github.com/holoviz/panel/issues/1824))
- Allow recording session launch time in server session_info ([#1909](https://github.com/holoviz/panel/pull/1909))
- Add Button.value parameter ([#1910](https://github.com/holoviz/panel/issues/1910))
- Support upload of multiple parameters on FileInput ([#1911](https://github.com/holoviz/panel/pull/1911))
- Improve support for DarkTheme in templates ([#1855](https://github.com/holoviz/panel/pull/1855), [#1856](https://github.com/holoviz/panel/pull/1856))

Documentation:

- Fixed IntSlider and FloatSlider example ([#1825](https://github.com/holoviz/panel/pull/1825))
- Updated instructions for using Panel in JupyterLab ([#1908](https://github.com/holoviz/panel/pull/1908))

## Version 0.10.2

Date: 2020-11-13

This is another micro-release primarily fixing various minor bugs in functionality introduced as part of the 0.10.0 release. Many thanks to @MarcSkovMadsen, @ahuang11, @xavArtley, @Hoxbro, @jbednar and @philippjfr.

Bug fixes:

- Fix various issues with Template CSS ([#1663](https://github.com/holoviz/panel/pull/1663), [#1742](https://github.com/holoviz/panel/pull/1742))
- Fix BytesIO/StringIO buffers as input to image panes ([#1711](https://github.com/holoviz/panel/issues/1711))
- Fix out-of-bounds errors when assigning to `GridSpec` with fixed ncols ([#1721](https://github.com/holoviz/panel/pull/1721))
- Fix deserialization issues for `Plotly.hover_data` ([#1722](https://github.com/holoviz/panel/pull/))
- Fixed updating of `Alert` parameters after initialization ([#1725](https://github.com/holoviz/panel/pull/1725))
- Fix ordering of items added to Template areas ([#1736](https://github.com/holoviz/panel/pull/1736))
- Fix interactivity for items in Card ([#1750](https://github.com/holoviz/panel/pull/1750))
- Ensure onload callbacks are only run once ([#1746](https://github.com/holoviz/panel/pull/1746))
- Allow overriding items in grid based templates ([#1741](https://github.com/holoviz/panel/pull/1741))
- Ensure `ECharts` and `ipywidget` rerender when in `Card` ([#1765](https://github.com/holoviz/panel/pull/1765))
- Ensure template dark theme persists on HoloViews plots ([#1764](https://github.com/holoviz/panel/pull/1764))
- Fix responsive height in Plotly pane ([#1770](https://github.com/holoviz/panel/pull/1770))
- Ensure image panes resize in width and height ([#1777](https://github.com/holoviz/panel/pull/1777))
- Fix issues with Location.sync serialization ([#1784](https://github.com/holoviz/panel/pull/1784))
- Add throttled argument to interact ([#1259](https://github.com/holoviz/panel/pull/1259))
- ECharts pane now loads echarts-gl for 3D support ([#1785](https://github.com/holoviz/panel/pull/1785)) 

Enhancements:

- Improved OAuth encryption key validation ([#1762](https://github.com/holoviz/panel/pull/1762))
- Add `progress` option to `.save` method ([#1776](https://github.com/holoviz/panel/pull/1776))

## Version 0.10.1

Date: 2020-10-27

This is a micro release of Paanel primarily containing bug fixes following the 0.10.0 release. Many thanks to @MarcSkovMadsen, @jbednar and @philippjfr for contributing fixes to this release.

Enhancements:

- Add pn.bind function to bind parameters to a function ([#1629](https://github.com/holoviz/panel/issues/1629))

Bug fixes:

- Fix `WidgetBox` CSS ([#855](https://github.com/holoviz/panel/pull/855))
- Fix CSS load order in Templates ([#1698](https://github.com/holoviz/panel/pull/1698))
- Allow setting `DiscreteSlider` orientation ([#1683](https://github.com/holoviz/panel/pull/1683))
- Ensure JS callbacks and links are only set up once on templates ([#1700](https://github.com/holoviz/panel/pull/1700))
- Initialize pipeline only once ([#1705](https://github.com/holoviz/panel/pull/1705))
- Allow using `NumberInput` as `Param` pane widget ([#1708](https://github.com/holoviz/panel/issues/1708))

## Version 0.10.0

Date: 2020-10-23

This is a minor but jam-packed release of Panel, with a slew of new features and enhancements, plus a wide array of minor fixes and improvements to the documentation, and website.
Many thanks to the people who contributed to this release, including @philippjfr, @MarkSkovMadsen (alert pane, templates, docs), @xavArtley (VTK improvements, templates, input/spinner widgets), @maximlt (panel serve), @jbednar (docs, reviewing), @kebowen (templates), @ahuang11 (datepicker), @nghenzi (react template, bugfixes), @nritsche (panel serve), @ltalirz (autocomplete input), @BoBednar (docs), @tmikolajczyk, @halilbay, @Hoxbro, and @ceball (testing and automation).

Features:

- Add `Card` and `Accordion` layout ([#1262](https://github.com/holoviz/panel/pull/1262), [#1266](https://github.com/holoviz/panel/pull/1266), [#1267](https://github.com/holoviz/panel/pull/1267), [#1616](https://github.com/holoviz/panel/pull/1616), [#1619](https://github.com/holoviz/panel/pull/1619))
- Location component ([#1150](https://github.com/holoviz/panel/pull/1150), [#1297](https://github.com/holoviz/panel/pull/1297), [#1357](https://github.com/holoviz/panel/pull/1357), [#1407](https://github.com/holoviz/panel/pull/1407), [#1498](https://github.com/holoviz/panel/pull/1498), [#1519](https://github.com/holoviz/panel/pull/1519), [#1532](https://github.com/holoviz/panel/pull/1532), [#1638](https://github.com/holoviz/panel/pull/1638), [#1658](https://github.com/holoviz/panel/pull/1658))
- VTK improvements: colorbars ([#1270](https://github.com/holoviz/panel/pull/1270)), synchronization ([#1248](https://github.com/holoviz/panel/pull/1248), [#1637](https://github.com/holoviz/panel/pull/1637)), orientation widget ([#1635](https://github.com/holoviz/panel/pull/1635)), volume controller ([#1631](https://github.com/holoviz/panel/pull/1631)), serialization ([#1596](https://github.com/holoviz/panel/pull/1596)), follower ([#1451](https://github.com/holoviz/panel/pull/1451))
- Add default templates ([#1277](https://github.com/holoviz/panel/pull/1277), [#1374](https://github.com/holoviz/panel/pull/1374), [#1419](https://github.com/holoviz/panel/pull/1419), [#1421](https://github.com/holoviz/panel/pull/1421), [#1459](https://github.com/holoviz/panel/pull/1459), [#1472](https://github.com/holoviz/panel/pull/1472), [#1473](https://github.com/holoviz/panel/pull/1473), [#1479](https://github.com/holoviz/panel/pull/1479), [#1530](https://github.com/holoviz/panel/pull/1530), [#1535](https://github.com/holoviz/panel/pull/1535), [#1608](https://github.com/holoviz/panel/pull/1608), [#1617](https://github.com/holoviz/panel/pull/1617), [#1645](https://github.com/holoviz/panel/pull/1645), [#1647](https://github.com/holoviz/panel/pull/1647), [#1650](https://github.com/holoviz/panel/pull/1650), [#1660](https://github.com/holoviz/panel/pull/1660), [#1661](https://github.com/holoviz/panel/pull/1661), [#1662](https://github.com/holoviz/panel/pull/1662), [#1677](https://github.com/holoviz/panel/pull/1677), [#1682](https://github.com/holoviz/panel/pull/1682), [#1685](https://github.com/holoviz/panel/pull/1685), [#1687](https://github.com/holoviz/panel/pull/1687))
- Improvements for ipywidgets support ([#1285](https://github.com/holoviz/panel/pull/1285), [#1389](https://github.com/holoviz/panel/pull/1389), [#1476](https://github.com/holoviz/panel/pull/1476), [#1675](https://github.com/holoviz/panel/pull/1675))
- Add `pn.state.busy` and `pn.state.onload` callback ([#1392](https://github.com/holoviz/panel/pull/1392), [#1518](https://github.com/holoviz/panel/pull/1518))
- Add support for serving static files ([#1319](https://github.com/holoviz/panel/pull/1319), [#1492](https://github.com/holoviz/panel/pull/1492))
- Add an `Alert` pane ([#1181](https://github.com/holoviz/panel/pull/1181), [#1422](https://github.com/holoviz/panel/pull/1422))
- Add ability to declare OAuth provider ([#820](https://github.com/holoviz/panel/pull/820), [#1468](https://github.com/holoviz/panel/pull/1468), [#1470](https://github.com/holoviz/panel/pull/1470), [#1474](https://github.com/holoviz/panel/pull/1474), [#1475](https://github.com/holoviz/panel/pull/1475), [#1480](https://github.com/holoviz/panel/pull/1480), [#1508](https://github.com/holoviz/panel/pull/1508), [#1594](https://github.com/holoviz/panel/pull/1594), [#1625](https://github.com/holoviz/panel/pull/1625))
- Add `ECharts` pane ([#1484](https://github.com/holoviz/panel/pull/1484), [#1691](https://github.com/holoviz/panel/pull/1691))
- Add busy/loading indicators and enable on Template ([#1493](https://github.com/holoviz/panel/pull/1493))
- Allow serving REST APIs as part of panel serve ([#1164](https://github.com/holoviz/panel/pull/1164))
- Add `pn.state.as_cached` function ([#1526](https://github.com/holoviz/panel/pull/1526))
- Add MenuButton widget ([#1533](https://github.com/holoviz/panel/pull/1533))
- Add a number of `ValueIndicators` ([#1528](https://github.com/holoviz/panel/pull/1528), [#1590](https://github.com/holoviz/panel/pull/1590), [#1627](https://github.com/holoviz/panel/pull/1627), [#1628](https://github.com/holoviz/panel/pull/1628), [#1633](https://github.com/holoviz/panel/pull/1633))
- Add support for `param.Event` ([#1600](https://github.com/holoviz/panel/pull/1600))
- Add `IntInput` and `FloatInput` widgets ([#1513](https://github.com/holoviz/panel/pull/1513))
- Record session statistics on `pn.state.session_info` ([#1615](https://github.com/holoviz/panel/pull/1615), [#1620](https://github.com/holoviz/panel/pull/1620), [#1634](https://github.com/holoviz/panel/pull/1634))
- Bundle external JS dependencies for custom models and templates ([#1651](https://github.com/holoviz/panel/pull/1651), [#1655](https://github.com/holoviz/panel/pull/1655))
- Add support for ipympl (interactive mode) on Matplotlib ([#1469](https://github.com/holoviz/panel/pull/1469))

Enhancements:

- Allow defining explicit embed states ([#1274](https://github.com/holoviz/panel/pull/1274))
- Implement `__add__` and `__iadd__` on layouts ([#1282](https://github.com/holoviz/panel/pull/1282))
- Add support for hierarchical multi-indexed DataFrame ([#1383](https://github.com/holoviz/panel/pull/1383))
- Add `show_index` option to `DataFrame` widget ([#1488](https://github.com/holoviz/panel/pull/1488))
- Link widgets with same name during embed ([#1543](https://github.com/holoviz/panel/pull/1543))
- Wait until JS dependency is loaded before rendering ([#1577](https://github.com/holoviz/panel/pull/1577))
- For `AutocompleteInput`, allow user-defined values ([#1588](https://github.com/holoviz/panel/pull/1588)) and case-insensitivity ([#1548](https://github.com/holoviz/panel/pull/1548)) 
- Allow dates to be disabled in DatePicker ([#1524](https://github.com/holoviz/panel/pull/1524))
- Enable new features for a Bokeh DataTable ([#1512](https://github.com/holoviz/panel/pull/1512))
- Panel serve improvements: MethodType parameter ([#1450](https://github.com/holoviz/panel/pull/1450)), title per app ([#1354](https://github.com/holoviz/panel/pull/1354)) 
- Server deployment guide for Azure ([#1350](https://github.com/holoviz/panel/pull/1350))
- Add Widget.from_param classmethod ([#1344](https://github.com/holoviz/panel/pull/1344))
- More options for ACE widget ([#1391](https://github.com/holoviz/panel/pull/1391))

Bugfixes and minor improvements:

- VTK model compilation ([#1669](https://github.com/holoviz/panel/pull/1669)), findPokedRenderer ([#1456](https://github.com/holoviz/panel/pull/1456)), misc ([#1406](https://github.com/holoviz/panel/pull/1406), [#1409](https://github.com/holoviz/panel/pull/1409))
- Fix parameterized parameter handling ([#1584](https://github.com/holoviz/panel/pull/1584))
- Theming improvements ([#1670](https://github.com/holoviz/panel/pull/1670))
- JS dependency handling ([#1626](https://github.com/holoviz/panel/pull/1626))
- Parameterized: explicit triggering ([#1623](https://github.com/holoviz/panel/pull/1623)), strings with None default ([#1622](https://github.com/holoviz/panel/pull/1622))
- Docs and examples ([#1242](https://github.com/holoviz/panel/pull/1242), [#1435](https://github.com/holoviz/panel/pull/1435), [#1448](https://github.com/holoviz/panel/pull/1448), [#1467](https://github.com/holoviz/panel/pull/1467), [#1540](https://github.com/holoviz/panel/pull/1540), [#1541](https://github.com/holoviz/panel/pull/1541), [#1558](https://github.com/holoviz/panel/pull/1558), [#1570](https://github.com/holoviz/panel/pull/1570), [#1576](https://github.com/holoviz/panel/pull/1576), [#1609](https://github.com/holoviz/panel/pull/1609))
- Many other minor fixes and improvements ([#1284](https://github.com/holoviz/panel/pull/1284), [#1384](https://github.com/holoviz/panel/pull/1384), [#1423](https://github.com/holoviz/panel/pull/1423), [#1489](https://github.com/holoviz/panel/pull/1489), [#1495](https://github.com/holoviz/panel/pull/1495), [#1502](https://github.com/holoviz/panel/pull/1502), [#1503](https://github.com/holoviz/panel/pull/1503), [#1507](https://github.com/holoviz/panel/pull/1507), [#1520](https://github.com/holoviz/panel/pull/1520), [#1521](https://github.com/holoviz/panel/pull/1521), [#1536](https://github.com/holoviz/panel/pull/1536), [#1539](https://github.com/holoviz/panel/pull/1539), [#1546](https://github.com/holoviz/panel/pull/1546), [#1547](https://github.com/holoviz/panel/pull/1547), [#1553](https://github.com/holoviz/panel/pull/1553), [#1562](https://github.com/holoviz/panel/pull/1562), [#1595](https://github.com/holoviz/panel/pull/1595), [#1621](https://github.com/holoviz/panel/pull/1621), [#1639](https://github.com/holoviz/panel/pull/1639))

Backwards compatibility:

- Switch away from inline resources in notebook ([#1538](https://github.com/holoviz/panel/pull/1538), [#1678](https://github.com/holoviz/panel/pull/1678))
- `Viewable.add_periodic_callback` is deprecated; use pn.state.add_periodic_callback ([#1542](https://github.com/holoviz/panel/pull/1542))
- Use `widget_type` instead of `type` to override Param widget type in Param pane ([#1614](https://github.com/holoviz/panel/pull/1614)) 
- `Spinner` widget is now called `NumberInput` ([#1513](https://github.com/holoviz/panel/pull/1513))


## Version 0.9.7

The 0.9.6 release unfortunately caused a major regression in layout performance due to the way optimizations in Bokeh and Panel interacted. This release fixes this regression.

- Fix regression in layout performance ([#1453](https://github.com/holoviz/panel/pull/1453))

## Version 0.9.6

This is a minor bug fix release primarily for compatibility with Bokeh versions >=2.1.0 along with a variety of important bug fixes. Many thanks for the many people who contributed to this release including @mattpap, @kebowen730, @xavArtley, @maximlt, @jbednar, @mycarta, @basnijholt, @jbednar and @philippjfr.

- Compatibility with Bokeh 2.1 ([#1424](https://github.com/holoviz/panel/pull/1424), [#1428](https://github.com/holoviz/panel/pull/1428))
- Fixes for `FileDownload` widget handling of callbacks ([#1246](https://github.com/holoviz/panel/pull/1246), [#1306](https://github.com/holoviz/panel/pull/1306))
- Improvements and fixes for Param pane widget mapping ([#1301](https://github.com/holoviz/panel/pull/1301), [#1342](https://github.com/holoviz/panel/pull/1342), [#1378](https://github.com/holoviz/panel/pull/1378)) 
- Fixed bugs handling of closed Tabs ([#1337](https://github.com/holoviz/panel/pull/1337))
- Fix bug in layout `clone` method ([#1349](https://github.com/holoviz/panel/pull/1349))
- Improvements for `Player` widget ([#1353](https://github.com/holoviz/panel/pull/1353), [#1360](https://github.com/holoviz/panel/pull/1360))
- Fix for `jslink` on Bokeh models ([#1358](https://github.com/holoviz/panel/pull/1358))
- Fix for rendering geometries in `Vega` pane ([#1359](https://github.com/holoviz/panel/pull/1359))
- Fix issue with `HoloViews` pane overriding selected renderer ([#1429](https://github.com/holoviz/panel/pull/1429))
- Fix issues with `JSON` pane depth parameter and rerendering ([#1431](https://github.com/holoviz/panel/pull/1431))
- Fixed `param.Date` and `param.CalenderDate` parameter mappings ([#1433](https://github.com/holoviz/panel/pull/1433), [#1434](https://github.com/holoviz/panel/pull/1434))
- Fixed issue with enabling `num_procs` on `pn.serve` ([#1436](https://github.com/holoviz/panel/pull/1436))
- Warn if a particular extension could not be loaded ([#1437](https://github.com/holoviz/panel/pull/1437))
- Fix issues with garbage collection and potential memory leaks ([#1407](https://github.com/holoviz/panel/pull/1407))
- Support recent versions of pydeck in `DeckGL` pane ([#1443](https://github.com/holoviz/panel/pull/1443))
- Ensure JS callbacks on widget created from Parameters are initialized ([#1439](https://github.com/holoviz/panel/pull/1439))

## Version 0.9.5

Date: 2019-04-04

This release primarily focused on improvements and additions to the documentation. Many thanks to @MarcSkovMadsen, @philippjfr and @michaelaye for contributing to this release.

Enhancements:

- Add `Template.save` with ability to save to HTML and PNG but not embed ([#1224](https://github.com/holoviz/panel/pull/1224))

Bug fixes:

- Fixed formatting of datetimes in `DataFrame` widget ([#1221](https://github.com/holoviz/panel/pull/1221))
- Add `panel/models/vtk/` subpackage to MANIFEST to ensure it is shipped with packages

Documentation:

- Add guidance about developing custom models ([#1220](https://github.com/holoviz/panel/pull/1220))
- Add Folium example to gallery ([#1189](https://github.com/holoviz/panel/pull/1189))
- Add `FileDownload` and `FileInput` example to gallery ([#1193](https://github.com/holoviz/panel/pull/1193))

## Version 0.9.4

Date: 2020-04-02

This is a minor release fixing a number of regressions and compatibility issues which continue to crop up due to the upgrade to Bokeh 2.0 Additionally this release completely overhauls how communication in notebook environments are handled, eliminating the need to register custom callbacks with inlined JS callbacks to sync properties. Many thanks to the contributors to this release including @hyamanieu, @maximlt, @mattpap and the maintainer @philippjfr.

Enhancements:

- Switch to using CommManager in notebook hugely simplifying comms in notebooks and reducing the amount of inlined Javascript ([#1171](https://github.com/holoviz/panel/pull/1171))
- Add ability to serve Flask apps directly using pn.serve ([#1215](https://github.com/holoviz/panel/pull/1215)) 

Bug fixes:

- Fix bug in Template which caused all roots to instantiate two models for each component ([#1216](https://github.com/holoviz/panel/pull/1216))
- Fixed bug with Bokeh 2.0 DataPicker datetime format ([#1187](https://github.com/holoviz/panel/pull/1187))
- Publish Panel.js to CDN to allow static HTML exports with CDN resources to work ([#1190](https://github.com/holoviz/panel/pull/1190))
- Handle bug in rendering Vega models with singular dataset ([#1201](https://github.com/holoviz/panel/pull/1201))
- Removed escaping workaround for HTML models resulting in broken static exports ([#1206](https://github.com/holoviz/panel/pull/1206))
- Fixed bug closing Tabs ([#1208](https://github.com/holoviz/panel/pull/1208))
- Embed Panel logo in server index.html ([#1209](https://github.com/holoviz/panel/pull/1209))

Compatibility:

- This release adds compatibility with Bokeh 2.0.1 which caused a regression in loading custom models

## Version 0.9.3

Date: 2019-03-21

This is a minor release fixing an issue with recent versions of Tornado. It also fixes issue with the packages built on the PyViz conda channel.

- Respect write-locks on synchronous Websocket events ([#1170](https://github.com/holoviz/panel/issues/1170))

## Version 0.9.2

Date: 2019-03-21

This is a minor release with a number of bug fixes. Many thanks to @ceball, @Guillemdb and @philippjfr for contributing these fixes.

Bug fixes:

- Fix regression in DiscreteSlider layout ([#1163](https://github.com/holoviz/panel/issues/1164))
- Fix for saving as PNG which regressed due to changes in bokeh 2.0 ([#1165](https://github.com/holoviz/panel/issues/1165))
- Allow pn.serve to resolve Template instances returned by a function ([#1167](https://github.com/holoviz/panel/issues/1167))
- Ensure Template can render empty HoloViews pane ([#1168](https://github.com/holoviz/panel/issues/1168))

## Version 0.9.1

Date: 2019-03-19

This is very minor releases fixing small regressions in the 0.9.0 release:

Bug fixes:

- Fix issue with `Button` label not being applied ([#1152](https://github.com/holoviz/panel/issues/1152))
- Pin pyviz_comms 0.7.4 to avoid issues with undefined vars ([#1153](https://github.com/holoviz/panel/issues/1153))

## Version 0.9.0

Date: 2019-03-13

This is a major release primarily for compatibility with the recent Bokeh 2.0 release. Additionally this release has a small number of features and bug fixes:

Features:

- Added a `MultiChoice` widget ([#1140](https://github.com/holoviz/panel/issues/1140))
- Add `FileDownload` widget ([#915](https://github.com/holoviz/panel/issues/915), [#1146](https://github.com/holoviz/panel/issues/1146))
- Add ability to define `Slider` format option ([#1142](https://github.com/holoviz/panel/issues/1142))
- Expose `pn.state.cookies` and `pn.state.headers` to allow accessing HTTP headers and requests from inside an app ([#1143)

Bug fixes:

- Ensure `DiscreteSlider` respects layout options ([#1144](https://github.com/holoviz/panel/issues/1144))

Removals:

- Slider no longer support `callback_policy` and `callback_throttle` as they have been replaced by the `value_throttled` property in bokeh

## Version 0.8.1

Date: 2019-03-11

This release is a minor release with a number of bug fixes and minor enhancements. Many thanks to the community of contributors including @bstadlbauer, @ltalirz @ceball and @gmoutsofor submitting the fixes and the maintainers, including @xavArtley, @jbednar and @philippjfr, for continued development.

Minor enhancements:

- Added verbose option to display server address ([#1098](https://github.com/holoviz/panel/issues/1098)) [@philippjfr]

Bug fixes:

- Fix PNG export due to issue with PhantomJS ([#1081](https://github.com/holoviz/panel/issues/1081), [#1092](https://github.com/holoviz/panel/issues/1092)) [@bstadlbauer, @philippjfr]
- Fix for threaded server ([#1090](https://github.com/holoviz/panel/issues/1090)) [@xavArtley]
- Ensure Plotly Pane does not perform rerender on each property change ([#1109](https://github.com/holoviz/panel/issues/1109)) [@philippjfr]
- Fix issues with jslink and other callbacks in Template ([#1135](https://github.com/holoviz/panel/issues/1135)) [@philippjfr]
- Various fixes for VTK pane ([#1123](https://github.com/holoviz/panel/issues/1123)) [@xavArtley]
- Fixes for .show keyword arguments ([#1073](https://github.com/holoviz/panel/issues/1073), [#1106](https://github.com/holoviz/panel/issues/1106)) [@gmoutso]

## Version 0.8.0

Date: 2019-01-31

This release focuses primarily on solidifying existing functionality, significantly improving performance and fixing a number of important bugs. Additionally this release contains exciting new functionality, including several new components.  We want to thank the many contributors to this release (a full list is provided at the bottom), particularly @MarcSkovMadsen (the author of [awesome-panel.org](http://awesome-panel.org)) and @xavArtley, who has been hard at work at improving VTK support. We also want to thank the remaining contributors including @philippjfr, @ceball, @jbednar, @jlstevens, @Italirz, @mattpap, @Jacob-Barhak, @stefjunod and @kgullikson88. This release required only minimal changes in existing APIs and added a small number of new ones, reflecting the fact that Panel is now relatively stable and is progressing steadily towards a 1.0 release.

### Major Features & Enhancements

- Added new `DeckGL` pane ([#1019](https://github.com/holoviz/panel/issues/1019), [#1027](https://github.com/holoviz/panel/issues/1027))
- Major improvements to support for JS linking ([#1007](https://github.com/holoviz/panel/issues/1007))
- Huge performance improvements when nesting a lot of components deeply ([#867](https://github.com/holoviz/panel/issues/867), [#888](https://github.com/holoviz/panel/issues/888), [#895](https://github.com/holoviz/panel/issues/895), [#988](https://github.com/holoviz/panel/issues/988))
- Add support for displaying callback errors and print output in the notebook simplifying debugging ([#977](https://github.com/holoviz/panel/issues/977))
- Add support for dynamically populating `Tabs` ([#995](https://github.com/holoviz/panel/issues/995))
- Added `FileSelector` widget to browse the servers file system and select files ([#909](https://github.com/holoviz/panel/issues/909))
- Add `pn.serve` function to serve multiple apps at once on the same serve ([#963](https://github.com/holoviz/panel/issues/963))
- Add a `JSON` pane to display json data in a tree format ([#953](https://github.com/holoviz/panel/issues/953))

### Enhancements

- Updated Parameter mappings ([#999](https://github.com/holoviz/panel/issues/999))
- Ensure that closed tabs update `Tabs.objects` ([#973](https://github.com/holoviz/panel/issues/973))
- Fixed HoloViews axis linking across `Template` roots ([#980](https://github.com/holoviz/panel/issues/980))
- Merge FactorRange when linking HoloViews axes ([#968](https://github.com/holoviz/panel/issues/968))
- Expose title and other kwargs on `.show()` ([#962](https://github.com/holoviz/panel/issues/962))
- Let `FileInput` widget set filename ([#956](https://github.com/holoviz/panel/issues/956)
- Expose further bokeh CLI commands and added help ([#951](https://github.com/holoviz/panel/issues/951))
- Enable responsive sizing for `Vega`/altair pane ([#949](https://github.com/holoviz/panel/issues/949))
- Added encode parameter to `SVG` pane ([#913](https://github.com/holoviz/panel/issues/913))
- Improve `Markdown` handling including syntax highlighting and indentation ([#881](https://github.com/holoviz/panel/issues/881))
- Add ability to define Template variables ([#815](https://github.com/holoviz/panel/issues/815))
- Allow configuring responsive behavior globally ([#851](https://github.com/holoviz/panel/issues/851))
- Ensure that changes applied in callbacks are reflected on the frontend immediately ([#857](https://github.com/holoviz/panel/issues/857))
- Add ability to add axes coordinates to `VTK` view ([#817](https://github.com/holoviz/panel/issues/817))
- Add config option for `safe_embed` which ensures all state is recorded ([#1040](https://github.com/holoviz/panel/issues/1040))
- Implemented `__signature__` for tab completion ([#1029](https://github.com/holoviz/panel/issues/1029))

### Bug fixes

- Fixed `DataFrame` widget selection parameter ([#989](https://github.com/holoviz/panel/issues/989))
- Fixes for rendering long strings on Windows systems ([#986](https://github.com/holoviz/panel/issues/986))
- Ensure that panel does not modify user objects ([#967](https://github.com/holoviz/panel/issues/967))
- Fix multi-level expand `Param` subobject ([#965](https://github.com/holoviz/panel/issues/965))
- Ensure `load_notebook` is executed only once ([#1000](https://github.com/holoviz/panel/issues/1000))
- Fixed bug updating `StaticText` on server ([#964](https://github.com/holoviz/panel/issues/964))
- Do not link `HoloViews` axes with different types ([#937](https://github.com/holoviz/panel/issues/937))
- Ensure that integer sliders are actually integers ([#876](https://github.com/holoviz/panel/issues/876))
- Ensure that `GridBox` contents maintain size ([#971](https://github.com/holoviz/panel/issues/971))

### Compatibility

- Compatibility for new Param API ([#992](https://github.com/holoviz/panel/issues/992), [#998](https://github.com/holoviz/panel/issues/998))
- Changes for compatibility with Vega5 and altair 4 ([#873](https://github.com/holoviz/panel/issues/873), [#889](https://github.com/holoviz/panel/issues/889), [#892](https://github.com/holoviz/panel/issues/892), [#927](https://github.com/holoviz/panel/issues/927), [#933](https://github.com/holoviz/panel/issues/933))

### Backwards compatibility

- The Ace pane has been deprecated in favor of the Ace widget ([#908](https://github.com/holoviz/panel/issues/908))

### Docs

- Updated Django multiple app example and user guide ([#928](https://github.com/holoviz/panel/issues/928)) [@stefjunod]
- Clarify developer installation instructions, and fix up some metadata. ([#952](https://github.com/holoviz/panel/issues/952), [#978](https://github.com/holoviz/panel/issues/978))
- Added `Param` reference notebook ([#944](https://github.com/holoviz/panel/issues/944))
- Added `Divider` reference notebook

## Version 0.7.0

Date: 2019-11-18T21:22:16Z

This major release includes significant new functionality along with important bug and documentation fixes, including contributions from @philippjfr (maintainer and lead developer), @xavArtley (VTK support), @jbednar (docs), @DancingQuanta (FileInput), @a-recknagel (Python 3.8 support, misc), @julwin (TextAreaInput, PasswordInput), @rs2 (example notebooks), @xtaje (default values), @Karamya (Audio widget), @ceball, @ahuang11 , @eddienko, @Jacob-Barhak, @jlstevens, @jsignell, @kleavor, @lsetiawan, @mattpap, @maxibor, and @RedBeardCode.

Major enhancements:
- Added pn.ipywidget() function for using panels and panes as ipwidgets, e.g. in voila ([#745](https://github.com/holoviz/panel/issues/745), [#755](https://github.com/holoviz/panel/issues/755), [#771](https://github.com/holoviz/panel/issues/771))
- Greatly expanded and improved Pipeline, which now allows branching graphs ([#712](https://github.com/holoviz/panel/issues/712), [#735](https://github.com/holoviz/panel/issues/735), [#737](https://github.com/holoviz/panel/issues/737), [#770](https://github.com/holoviz/panel/issues/770))
- Added streaming helper objects, including for the streamz package ([#767](https://github.com/holoviz/panel/issues/767), [#769](https://github.com/holoviz/panel/issues/769))
- Added VTK gallery example and other VTK enhancements ([#605](https://github.com/holoviz/panel/issues/605), [#606](https://github.com/holoviz/panel/issues/606), [#715](https://github.com/holoviz/panel/issues/715), [#729](https://github.com/holoviz/panel/issues/729))
- Add GridBox layout ([#608](https://github.com/holoviz/panel/issues/608), [#761](https://github.com/holoviz/panel/issues/761), [#763](https://github.com/holoviz/panel/issues/763))
- New widgets and panes:
   * Progress bar ([#726](https://github.com/holoviz/panel/issues/726))
   * Video ([#696](https://github.com/holoviz/panel/issues/696))
   * TextAreaInput widget ([#658](https://github.com/holoviz/panel/issues/658))
   * PasswordInput widget ([#655](https://github.com/holoviz/panel/issues/655))
   * Divider ([#756](https://github.com/holoviz/panel/issues/756)),
   * bi-directional jslink ([#764](https://github.com/holoviz/panel/issues/764))
   * interactive DataFrame pane for Pandas, Dask and Streamz dataframes ([#560](https://github.com/holoviz/panel/issues/560), [#751](https://github.com/holoviz/panel/issues/751))

Other enhancements:
- Make Row/Column scrollable ([#760](https://github.com/holoviz/panel/issues/760))
- Support file-like objects (not just paths) for images ([#686](https://github.com/holoviz/panel/issues/686))
- Added isdatetime utility ([#687](https://github.com/holoviz/panel/issues/687))
- Added repr, kill_all_servers, and cache to pn.state ([#697](https://github.com/holoviz/panel/issues/697),[#776](https://github.com/holoviz/panel/issues/776))
- Added Slider value_throttled parameter ([#777](https://github.com/holoviz/panel/issues/777))
- Extended existing widgets and panes:
   * WidgetBox can be disabled programmatically ([#532](https://github.com/holoviz/panel/issues/532))
   * Templates can now render inside a notebook cell ([#666](https://github.com/holoviz/panel/issues/666))
   * Added jscallback method to Viewable objects ([#665](https://github.com/holoviz/panel/issues/665))
   * Added min_characters parameter to AutocompleteInput ([#721](https://github.com/holoviz/panel/issues/721))
   * Added accept parameter to FileInput ([#602](https://github.com/holoviz/panel/issues/602))
   * Added definition_order parameter to CrossSelector ([#570](https://github.com/holoviz/panel/issues/570))
   * Misc widget fixes and improvements ([#703](https://github.com/holoviz/panel/issues/703), [#717](https://github.com/holoviz/panel/issues/717), [#724](https://github.com/holoviz/panel/issues/724), [#762](https://github.com/holoviz/panel/issues/762), [[#775](https://github.com/holoviz/panel/issues/775)](https://github.com/holoviz/panel/issues/775))

Bug fixes and minor improvements:
- Removed mutable default args ([#692](https://github.com/holoviz/panel/issues/692), [#694](https://github.com/holoviz/panel/issues/694))
- Improved tests ([#691](https://github.com/holoviz/panel/issues/691), [#699](https://github.com/holoviz/panel/issues/699), [#700](https://github.com/holoviz/panel/issues/700))
- Improved fancy layout for scrubber ([#571](https://github.com/holoviz/panel/issues/571))
- Improved plotly datetime handling ([#688](https://github.com/holoviz/panel/issues/688), [#698](https://github.com/holoviz/panel/issues/698))
- Improved JSON embedding ([#589](https://github.com/holoviz/panel/issues/589))
- Misc fixes and improvements ([#626](https://github.com/holoviz/panel/issues/626), [#631](https://github.com/holoviz/panel/issues/631), [#645](https://github.com/holoviz/panel/issues/645), [#662](https://github.com/holoviz/panel/issues/662), [#681](https://github.com/holoviz/panel/issues/681), [#689](https://github.com/holoviz/panel/issues/689), [#695](https://github.com/holoviz/panel/issues/695), [#723](https://github.com/holoviz/panel/issues/723), [#725](https://github.com/holoviz/panel/issues/725), [#738](https://github.com/holoviz/panel/issues/738), [#743](https://github.com/holoviz/panel/issues/743), [#744](https://github.com/holoviz/panel/issues/744), [#748](https://github.com/holoviz/panel/issues/748), [#749](https://github.com/holoviz/panel/issues/749), [#758](https://github.com/holoviz/panel/issues/758), [#768](https://github.com/holoviz/panel/issues/768), [#772](https://github.com/holoviz/panel/issues/772), [#774](https://github.com/holoviz/panel/issues/774), [[#775](https://github.com/holoviz/panel/issues/775)](https://github.com/holoviz/panel/issues/775), [#779](https://github.com/holoviz/panel/issues/779), [#784](https://github.com/holoviz/panel/issues/784), [#785](https://github.com/holoviz/panel/issues/785), [#787](https://github.com/holoviz/panel/issues/787), [#788](https://github.com/holoviz/panel/issues/788), [#789](https://github.com/holoviz/panel/issues/789))
- Prepare support for python 3.8 ([#702](https://github.com/holoviz/panel/issues/702))

Documentation:
- Expanded and updated FAQ ([#750](https://github.com/holoviz/panel/issues/750), [#765](https://github.com/holoviz/panel/issues/765))
- Add Comparisons section ([#643](https://github.com/holoviz/panel/issues/643))
- Docs fixes and improvements ([#635](https://github.com/holoviz/panel/issues/635), [#670](https://github.com/holoviz/panel/issues/670), [#705](https://github.com/holoviz/panel/issues/705), [#708](https://github.com/holoviz/panel/issues/708), [#709](https://github.com/holoviz/panel/issues/709), [#740](https://github.com/holoviz/panel/issues/740), [#747](https://github.com/holoviz/panel/issues/747), [#752](https://github.com/holoviz/panel/issues/752))

## Version 0.6.2

Date: 2019-08-08T15:13:31Z

Minor bugfix release patching issues with 0.6.1, primarily in the CI setup. Also removed the not-yet-supported definition_order parameter of pn.CrossSelector.

## Version 0.6.4

Date: 2019-10-08T17:41:51Z

This release includes a number of important bug fixes along with some minor enhancements, including contributions from @philippjfr, @jsignell, @ahuang11, @jonmmease, and @hoseppan.

Enhancements:

- Allow pn.depends and pn.interact to accept widgets and update their output when widget values change ([#639](https://github.com/holoviz/panel/issues/639))
- Add fancy_layout option to HoloViews pane ([#543](https://github.com/holoviz/panel/issues/543))
- Allow not embedding local files (e.g. images) when exporting to HTML ([#625](https://github.com/holoviz/panel/issues/625))

Bug fixes and minor improvements:

- Restore logging messages that were being suppressed by the distributed package ([#682](https://github.com/holoviz/panel/issues/682))
- HoloViews fixes and improvements ([#595](https://github.com/holoviz/panel/issues/595), [#599](https://github.com/holoviz/panel/issues/599), [#601](https://github.com/holoviz/panel/issues/601), [#659](https://github.com/holoviz/panel/issues/659))
- Misc other bug fixes and improvements ([#575](https://github.com/holoviz/panel/issues/575), [#588](https://github.com/holoviz/panel/issues/588), [#649](https://github.com/holoviz/panel/issues/649), [#654](https://github.com/holoviz/panel/issues/654), [#657](https://github.com/holoviz/panel/issues/657), [#660](https://github.com/holoviz/panel/issues/660), [#667](https://github.com/holoviz/panel/issues/667), [#677](https://github.com/holoviz/panel/issues/677))

Documentation:
- Added example of opening a URL from jslink ([#607](https://github.com/holoviz/panel/issues/607))


## Version 0.6.3

Date: 2019-09-19T10:28:36Z

This release saw a number of important bug and documentation fixes along with some minor enhancements.

Enhancements:

- Added support for embedding Player widget ([#584](https://github.com/holoviz/panel/issues/584))
- Add support for linking HoloViews plot axes across panels ([#586](https://github.com/holoviz/panel/issues/586))
- Allow saving to BytesIO buffer ([#596](https://github.com/holoviz/panel/issues/596)) 
- Allow `PeriodicCallback.period` to be updated dynamically ([#609](https://github.com/holoviz/panel/issues/609)) 

Bug fixes:

- While hooks are applied to model no events are sent to frontend ([#585](https://github.com/holoviz/panel/issues/585))
- Various fixes for embedding and rendering ([#594](https://github.com/holoviz/panel/issues/594))

Documentation:

- New example of periodic callbacks ([#573](https://github.com/holoviz/panel/issues/573))
- Improve `panel serve` documentation ([#611](https://github.com/holoviz/panel/issues/611), [#614](https://github.com/holoviz/panel/issues/614))
- Add server deployment guide ([#642](https://github.com/holoviz/panel/issues/642))

## Version 0.6.1

Date: 2019-08-01T14:54:20Z

## Version 0.6.0

Date: 2019-06-02T17:56:26Z

## Version 0.5.1

Date: 2019-04-11T16:52:06Z

Minor release closely following up on 0.5.0 updating version requirements to include the officially released bokeh 1.1.0. This release also includes contributions from @philippjfr (with fixes for pipeline and embed features), @xavArtley (addition of a new widget) and @banesullivan (fixes for VTK support).

Features:

- Addition of ``Spinner`` widget for numeric inputs ([#368](https://github.com/holoviz/panel/issues/368))

Bugfixes:

- Skip jslinked widgets when using embed ([#376](https://github.com/holoviz/panel/issues/376))
- Correctly revert changes to pipelines when stage transitions fail ([#375](https://github.com/holoviz/panel/issues/375))
- Fixed bug handling scalar arrays in VTK pane ([#372](https://github.com/holoviz/panel/issues/372))

## Version 0.5.0

Date: 2019-04-04T00:42:59Z

Major new release, greatly improving usability and capabilities.  Includes contributions from  @philippjfr (docs, better layouts, and many other features),  @xavArtley (VTK support, Ace code editor), @banesullivan (VTK support),  @jbednar and @rtmatx (docs),  @jsignell (docs, infrastructure, interact support), and @jlstevens (labels for parameters).

Major new features:

- Now uses Bokeh 1.1's greatly improved layout system, requiring far fewer manual adjustments to spacing ([#32](https://github.com/holoviz/panel/issues/32))
- Greatly expanded docs, now with galleries ([#241](https://github.com/holoviz/panel/issues/241), [#251](https://github.com/holoviz/panel/issues/251), [#265](https://github.com/holoviz/panel/issues/265), [#281](https://github.com/holoviz/panel/issues/281), [#318](https://github.com/holoviz/panel/issues/318), [#332](https://github.com/holoviz/panel/issues/332), [#347](https://github.com/holoviz/panel/issues/347), [#340](https://github.com/holoviz/panel/issues/340))
- Allow embedding app state, to support static HTML export of panels ([#250](https://github.com/holoviz/panel/issues/250))
- Added new GridSpec layout type, making it simpler to make grid-based dashboards ([#338](https://github.com/holoviz/panel/issues/338))
- Added VTK 3D object pane ([#312](https://github.com/holoviz/panel/issues/312), [#337](https://github.com/holoviz/panel/issues/337), [#349](https://github.com/holoviz/panel/issues/349), [#355](https://github.com/holoviz/panel/issues/355), [#363](https://github.com/holoviz/panel/issues/363))
- Added Ace code editor pane ([#359](https://github.com/holoviz/panel/issues/359))
- Allow defining external JS and CSS resources via config, making it easier to extend Panel ([#330](https://github.com/holoviz/panel/issues/330))
- Add HTML model capable of executing JS code, allowing more complex embedded items ([#32](https://github.com/holoviz/panel/issues/32)6)
- Add a KaTeX and MathJax based LaTeX pane, replacing the previous limited matplotlib/PNG-based support ([#311](https://github.com/holoviz/panel/issues/311))

Other new features:

- Allow passing Parameter instances to Param pane, making it much simpler to work with individual parameters ([#303](https://github.com/holoviz/panel/issues/303))
- Added parameter for widget alignment ([#367](https://github.com/holoviz/panel/issues/367))
- Allow specifying initial value when specifying min/max/step for interact ([#334](https://github.com/holoviz/panel/issues/334))
- Add support for param.Number step ([#365](https://github.com/holoviz/panel/issues/365))
- Add a PeriodicCallback ([#348](https://github.com/holoviz/panel/issues/348))
- Expose curdoc and session_context when using serve ([#336](https://github.com/holoviz/panel/issues/336))
- Add support for saving and loading embedded data from JSON ([#301](https://github.com/holoviz/panel/issues/301))
- Add support for specifying arbitrary `label` for Parameters ([#290](https://github.com/holoviz/panel/issues/290))
- Add ColorPicker widget ([#267](https://github.com/holoviz/panel/issues/267))
- Add support for interact title ([#266](https://github.com/holoviz/panel/issues/266))

Bugfixes and minor improvements:

- Combine HTML and JS in MIME bundle to improve browser compatibility ([#32](https://github.com/holoviz/panel/issues/32)7)
- Inlined subobject expand toggle button ([#32](https://github.com/holoviz/panel/issues/32)9)
- Use Select widget for ObjectSelector consistently to avoid issues with short lists and numeric lists ([#362](https://github.com/holoviz/panel/issues/362))
- Various small improvements ([#238](https://github.com/holoviz/panel/issues/238), [#245](https://github.com/holoviz/panel/issues/245), [#257](https://github.com/holoviz/panel/issues/257), [#258](https://github.com/holoviz/panel/issues/258), [#259](https://github.com/holoviz/panel/issues/259), [#262](https://github.com/holoviz/panel/issues/262), [#264](https://github.com/holoviz/panel/issues/264), [#276](https://github.com/holoviz/panel/issues/276), [#289](https://github.com/holoviz/panel/issues/289), [#293](https://github.com/holoviz/panel/issues/293), [#307](https://github.com/holoviz/panel/issues/307), [#313](https://github.com/holoviz/panel/issues/313), [#343](https://github.com/holoviz/panel/issues/343), [#331](https://github.com/holoviz/panel/issues/331))
- Various bugfixes ([#247](https://github.com/holoviz/panel/issues/247), [#261](https://github.com/holoviz/panel/issues/261), [#263](https://github.com/holoviz/panel/issues/263), [#282](https://github.com/holoviz/panel/issues/282), [#288](https://github.com/holoviz/panel/issues/288), [#291](https://github.com/holoviz/panel/issues/291), [#297](https://github.com/holoviz/panel/issues/297), [#295](https://github.com/holoviz/panel/issues/295), [#305](https://github.com/holoviz/panel/issues/305), [#309](https://github.com/holoviz/panel/issues/309), [#32](https://github.com/holoviz/panel/issues/32)2, [#32](https://github.com/holoviz/panel/issues/32)8, [#341](https://github.com/holoviz/panel/issues/341), [#345](https://github.com/holoviz/panel/issues/345), [#354](https://github.com/holoviz/panel/issues/354), [#364](https://github.com/holoviz/panel/issues/364))

Changes potentially affecting backwards compatibility:

- Refactored io subpackage ([#315](https://github.com/holoviz/panel/issues/315))
- Moved panes and widgets into subpackage ([#283](https://github.com/holoviz/panel/issues/283))
- Cleaned up wdiget, deploy, and export APIs ([#268](https://github.com/holoviz/panel/issues/268), [#269](https://github.com/holoviz/panel/issues/269))
- Renamed pane precedence to priority to avoid confusion with Param precedence ([#235](https://github.com/holoviz/panel/issues/235))


## Version 0.3.1

Date: 2018-12-05T22:49:23Z

Minor release fixing packaging issues.

## Version 0.3.0

Date: 2018-12-05T00:47:25Z

Thanks to @mhc03 for bugfixes.

New features and enhancements
- New app: Euler's Method ([#161](https://github.com/holoviz/panel/issues/161))
- New widgets and panes: Player ([#110](https://github.com/holoviz/panel/issues/110)), DiscretePlayer ([#171](https://github.com/holoviz/panel/issues/171)), CrossSelector ([#153](https://github.com/holoviz/panel/issues/153))
- Spinner (spinner.gif)
- Compositional string reprs ([#129](https://github.com/holoviz/panel/issues/129))
- Add Param.widgets parameter to override default widgets ([#172](https://github.com/holoviz/panel/issues/172))
- Pipeline improvements ([#145](https://github.com/holoviz/panel/issues/145), etc.)
- Additional entry points for user commands ([#176](https://github.com/holoviz/panel/issues/176))
- Support calling from anaconda-project ([#133](https://github.com/holoviz/panel/issues/133))
- Improved docs

Bugfixes:
- Fix example packaging ([#177](https://github.com/holoviz/panel/issues/177))
- Various bugfixes and compatibility improvements ([#126](https://github.com/holoviz/panel/issues/126), [#128](https://github.com/holoviz/panel/issues/128), [#132](https://github.com/holoviz/panel/issues/132), [#136](https://github.com/holoviz/panel/issues/136), [#141](https://github.com/holoviz/panel/issues/141), [#142](https://github.com/holoviz/panel/issues/142), [#150](https://github.com/holoviz/panel/issues/150), [#151](https://github.com/holoviz/panel/issues/151), [#154](https://github.com/holoviz/panel/issues/154), etc.)

Compatibility changes
- Renamed Param expand options ([#127](https://github.com/holoviz/panel/issues/127))


## Version 0.4.0

Date: 2019-01-28T18:02:57Z

Thanks to @xavArtley for several contributions, and to @lebedov for bugfixes.

New features:

- Now Python2 compatible ([#225](https://github.com/holoviz/panel/issues/225))
- Audio player widget ([#215](https://github.com/holoviz/panel/issues/215),[#221](https://github.com/holoviz/panel/issues/221))
- FileInput widget ([#207](https://github.com/holoviz/panel/issues/207))
- General support for linking Panel objects, even in static exports ([#199](https://github.com/holoviz/panel/issues/199))
- New user-guide notebooks: Introduction ([#178](https://github.com/holoviz/panel/issues/178)), Links ([#195](https://github.com/holoviz/panel/issues/195)).

Enhancements:
- Improved Pipeline ([#220](https://github.com/holoviz/panel/issues/220), [#222](https://github.com/holoviz/panel/issues/222))

Bug fixes:
- Windows-specific issues ([#204](https://github.com/holoviz/panel/issues/204), [#209](https://github.com/holoviz/panel/issues/209), etc.)
- Various bugfixes ([#188](https://github.com/holoviz/panel/issues/188), [#189](https://github.com/holoviz/panel/issues/189), [#190](https://github.com/holoviz/panel/issues/190), [#203](https://github.com/holoviz/panel/issues/203))


## Version 0.1.3

Date: 2018-10-23T12:09:07Z
