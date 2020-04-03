Releases
========

Version 0.9.5
-------------

Date: 2020-04-03

This release primarily focuses on improvements and additions to the documentation. Many thanks to @MarcSkovMadsen, @philippjfr and @michaelaye for contributing to this release.

Enhancements:

- Add `Template.save` with ability to save to HTML and PNG but not embed (`#1224 <https://github.com/holoviz/panel/pull/1224>`_)

Bug fixes:

- Fixed formatting of datetimes in `DataFrame` widget (`#1221 <https://github.com/holoviz/panel/pull/1221>`_)
- Add `panel/models/vtk/` subpackage to MANIFEST to ensure it is shipped with packages 

Documentation:

- Add guidance about developing custom models (`#1220 <https://github.com/holoviz/panel/pull/1220>`_)
- Add Folium example to gallery (`#1189 <https://github.com/holoviz/panel/pull/1189>`_))
- Add `FileDownload` and `FileInput` example to gallery (`#1193 <https://github.com/holoviz/panel/pull/1193>`_))


Version 0.9.4
-------------

Date: 2020-04-01

This is a minor release fixing a number of regressions and compatibility issues which continue to crop up due to the upgrade to Bokeh 2.0 Additionally this release completely overhauls how communication in notebook environments are handled, eliminating the need to register custom callbacks with inlined JS callbacks to sync properties. Many thanks to the contributors to this release including @hyamanieu, @maximlt, @mattpap and the maintainer @philippjfr.

Enhancements:

- Switch to using CommManager in notebook hugely simplifying comms in notebooks and reducing the amount of inlined Javascript (`#1171 <https://github.com/holoviz/panel/pull/1171>`_)
- Add ability to serve Flask apps directly using pn.serve (`#1215 <https://github.com/holoviz/panel/pull/1215>`_) 

Bug fixes:

- Fix bug in Template which caused all roots to instantiate two models for each component (`#1216 <https://github.com/holoviz/panel/pull/1216>`_)
- Fixed bug with Bokeh 2.0 DataPicker datetime format (`#1187 <https://github.com/holoviz/panel/pull/1187>`_)
- Publish Panel.js to CDN to allow static HTML exports with CDN resources to work (`#1190 <https://github.com/holoviz/panel/pull/1190>`_)
- Handle bug in rendering Vega models with singular dataset (`#1201 <https://github.com/holoviz/panel/pull/1201>`_)
- Removed escaping workaround for HTML models resulting in broken static exports (`#1206 <https://github.com/holoviz/panel/pull/1206>`_)
- Fixed bug closing Tabs (`#1208 <https://github.com/holoviz/panel/pull/1208>`_)
- Embed Panel logo in server index.html (`#1209 <https://github.com/holoviz/panel/pull/1209>`_)

Compatibility:

- This release adds compatibility with Bokeh 2.0.1 which caused a regression in loading custom models

Version 0.9.3
-------------

Date: 2020-03-21

This is a minor release fixing an issue with recent versions of Tornado. It also fixes issue with the packages built on the PyViz conda channel.

- Respect write-locks on synchronous Websocket events (`#1170 <https://github.com/holoviz/panel/pull/1170>`_)

Version 0.9.2
-------------

Date: 2020-03-19

This is a minor release with a number of bug fixes. Many thanks to @ceball, @Guillemdb and @philippjfr for contributing these fixes.

Bug fixes:

- Fix regression in DiscreteSlider layout (`#1163 <https://github.com/holoviz/panel/pull/1163>`_)
- Fix for saving as PNG which regressed due to changes in bokeh 2.0 (`#1165 <https://github.com/holoviz/panel/pull/1165>`_)
- Allow pn.serve to resolve Template instances returned by a function (`#1167 <https://github.com/holoviz/panel/pull/1167>`_)
- Ensure Template can render empty HoloViews pane (`#1168 <https://github.com/holoviz/panel/pull/1168>`_)

Version 0.9.1
-------------

Date: 2020-03-13

This is very minor releases fixing small regressions in the 0.9.0 release:

Bug fixes

- Fix issue with Button label not being applied (`#1152 <https://github.com/holoviz/panel/pull/1152>`_)
- Pin pyviz_comms 0.7.4 to avoid issues with undefined vars (`#1153 <https://github.com/holoviz/panel/pull/1153>`_)

Version 0.9.0
-------------

Date: 2020-03-12

This is a major release primarily for compatibility with the recent Bokeh 2.0 release. Additionally this release has a small number of features and bug fixes:

Features:

- Added a MultiChoice widget (`#1140 <https://github.com/holoviz/panel/pull/1140>`_)
- Add FileDownload widget (`#915 <https://github.com/holoviz/panel/pull/915>`_, `#1146 <https://github.com/holoviz/panel/pull/1146>`_)
- Add ability to define Slider format option (`#1142 <https://github.com/holoviz/panel/pull/1142>`_)
- Expose `pn.state.cookies` and `pn.state.headers` to allow accessing HTTP headers and requests from inside an app (`#1143 <https://github.com/holoviz/panel/pull/1143>`_)

Bug fixes:

- Ensure DiscreteSlider respects layout options (`#1144 <https://github.com/holoviz/panel/pull/1144>`_)

Removals:

- Slider no longer support `callback_policy` and `callback_throttle` as they have been replaced by the `value_throttled` property in bokeh


Version 0.8.1
-------------

Date: 2020-03-10

This release is a minor release with a number of bug fixes and minor enhancements. Many thanks to the community of contributors including @bstadlbauer, @ltalirz @ceball and @gmoutsofor submitting the fixes and the maintainers, including @xavArtley, @jbednar and @philippjfr, for continued development.

Minor enhancements:

- Added verbose option to display server address (`#1098 <https://github.com/holoviz/panel/issues/1098>`_) [@philippjfr]

Bug fixes:

- Fix PNG export due to issue with PhantomJS (`#1081 <https://github.com/holoviz/panel/issues/1081>`_, `#1092 <https://github.com/holoviz/panel/issues/1092>`_) [@bstadlbauer, @philippjfr]
- Fix for threaded server (`#1090 <https://github.com/holoviz/panel/issues/1090>`_) [@xavArtley]
- Ensure Plotly Pane does not perform rerender on each property change (`#1109 <https://github.com/holoviz/panel/issues/1109>`_) [@philippjfr]
- Fix issues with jslink and other callbacks in Template (`#1135 <https://github.com/holoviz/panel/issues/1135>`_) [@philippjfr]
- Various fixes for VTK pane (`#1123 <https://github.com/holoviz/panel/issues/1123>`_) [@xavArtley]
- Fixes for .show keyword arguments (`#1073 <https://github.com/holoviz/panel/issues/1073>`_, `#1106 <https://github.com/holoviz/panel/issues/1107>`_) [@gmoutso]

Version 0.8.0
-------------

Date: 2020-01-30

This release focused primarily on solidifying existing functionality, improving performance and closing fixing a number of important bugs. Additionally this release contains a number of exciting new functionality and components. We want to thank the many contributors to this release (a full list is provided at the bottom), particularly `Marc Skov Madsen <https://github.com/MarcSkovMadsen>`_ (the author of `awesome-panel.org <http://awesome-panel.org/>`_) and `Xavier Artusi <https://github.com/xavArtley>`_, who has been hard at work at improving VTK support. We also want to thank the remaining contributors including @philippjfr, @ceball, @jbednar, @jlstevens, @Italirz, @mattpap, @Jacob-Barhak, @stefjunod and @kgullikson88. This release introduced only minimal changes in existing APIs and added a small number of new ones demonstrating that Panel is relatively stable and is progressing steadily towards a 1.0 release.

Major Enhancements:

- Added new `DeckGL` pane (`#1019 <https://github.com/holoviz/panel/issues/1019>`_, `#1027 <https://github.com/holoviz/panel/issues/1027>`_) [@MarcSkovMadsen & @philippjfr] 
- Major improvements to support for JS linking (`#1007 <https://github.com/holoviz/panel/issues/1007>`_) [@philippjfr]
- Huge performance improvements when nesting a lot of components deeply (`#867 <https://github.com/holoviz/panel/issues/867>`_, `#888 <https://github.com/holoviz/panel/issues/888>`_, `#895 <https://github.com/holoviz/panel/issues/895>`_, `#988 <https://github.com/holoviz/panel/issues/988>`_) [@philippjfr]
- Add support for displaying callback errors and print output in the notebook simplifying debugging (`#977 <https://github.com/holoviz/panel/issues/977>`_) [@philippjfr]
- Add support for dynamically populating `Tabs` (`#995 <https://github.com/holoviz/panel/issues/995>`_) [@philippjfr]
- Added `FileSelector` widget to browse the servers file system and select files (`#909 <https://github.com/holoviz/panel/issues/909>`_) [@philippjfr]
- Add `pn.serve` function to serve multiple apps at once on the same serve (`#963 <https://github.com/holoviz/panel/issues/963>`_) [@philippjfr]
- Add a `JSON` pane to display json data in a tree format (`#953 <https://github.com/holoviz/panel/issues/953>`_) [@philippjfr]

Minor Enhancements:

- Updated Parameter mappings (`#999 <https://github.com/holoviz/panel/issues/999>`_) [@philippjfr]
- Ensure that closed tabs update `Tabs.objects` (`#973 <https://github.com/holoviz/panel/issues/973>`_) [@philippjfr]
- Fixed HoloViews axis linking across `Template` roots (`#980 <https://github.com/holoviz/panel/issues/980>`_) [@philippjfr]
- Merge FactorRange when linking HoloViews axes (`#968 <https://github.com/holoviz/panel/issues/968>`_) [@philippjfr]
- Expose title and other kwargs on `.show()` (`#962 <https://github.com/holoviz/panel/issues/962>`_) [@philippjfr]
- Let `FileInput` widget set filename (`#956 <https://github.com/holoviz/panel/issues/956>`_) [Leopold Talirz]
- Expose further bokeh CLI commands and added help (`#951 <https://github.com/holoviz/panel/issues/951>`_) [@philippjfr]
- Enable responsive sizing for `Vega`/altair pane (`#949 <https://github.com/holoviz/panel/issues/949>`_) [@philippjfr]
- Added encode parameter to `SVG` pane (`#913 <https://github.com/holoviz/panel/issues/913>`_) [@philippjfr]
- Improve `Markdown` handling including syntax highlighting and indentation (`#881 <https://github.com/holoviz/panel/issues/881>`_) [@philippjfr]
- Add ability to define Template variables (`#815 <https://github.com/holoviz/panel/issues/815>`_) [@philippjfr]
- Allow configuring responsive behavior globally (`#851 <https://github.com/holoviz/panel/issues/951>`_) [@xavArtley]
- Ensure that changes applied in callbacks are reflected on the frontend immediately (`#857 <https://github.com/holoviz/panel/issues/857>`_) [@philippjfr]
- Add ability to add axes coordinates to `VTK` view (`#817 <https://github.com/holoviz/panel/issues/817>`_) [@xavArtley]
- Add config option for `safe_embed` which ensures all state is recorded (`#1040  <https://github.com/holoviz/panel/issues/1040>`_) [@philippjfr]
- Implemented `__signature__` for tab completion (`#1029 <https://github.com/holoviz/panel/issues/1029>`_) [@philippjfr]

Bug fixes:

- Fixed `DataFrame` widget selection parameter (`#989 <https://github.com/holoviz/panel/issues/989>`_) [@philippjfr]
- Fixes for rendering long strings on Windows systems (`#986 <https://github.com/holoviz/panel/issues/986>`_)
- Ensure that panel does not modify user objects (`#967 <https://github.com/holoviz/panel/issues/967>`_) [@philippjfr]
- Fix multi-level expand `Param` subobject (`#965 <https://github.com/holoviz/panel/issues/965>`_) [@philippjfr]
- Ensure `load_notebook` is executed only once (`#1000 <https://github.com/holoviz/panel/issues/1000>`_) [@philippjfr]
- Fixed bug updating `StaticText` on server (`#964 <https://github.com/holoviz/panel/issues/964>`_) [@philippjfr]
- Do not link `HoloViews` axes with different types (`#937 <https://github.com/holoviz/panel/issues/937>`_) [@philippjfr]
- Ensure that integer sliders are actually integers (`#876 <https://github.com/holoviz/panel/issues/867>`_) [@philippjfr]
- Ensure that `GridBox` contents maintain size (`#971 <https://github.com/holoviz/panel/issues/971>`_) [@philippjfr]

Compatibility:

- Compatibility for new Param API (`#992 <https://github.com/holoviz/panel/issues/992>`_, `#998 <https://github.com/holoviz/panel/issues/998>`_) [@jlstevens]
- Changes for compatibility with Vega5 and altair 4 (`#873 <https://github.com/holoviz/panel/issues/873>`_, `#889 <https://github.com/holoviz/panel/issues/889>`_, `#892 <https://github.com/holoviz/panel/issues/892>`_, `#927 <https://github.com/holoviz/panel/issues/927>`_, `#933 <https://github.com/holoviz/panel/issues/933>`_) [@philippjfr]

API Changes:

- The Ace pane has been deprecated in favor of the Ace widget (`#908 <https://github.com/holoviz/panel/issues/908>`_) [@kgullikson88]

Docs:

- Updated Django multiple app example and user guide (`#928 <https://github.com/holoviz/panel/issues/928>`_) [@stefjunod]
- Clarify developer installation instructions, and fix up some metadata. (`#952 <https://github.com/holoviz/panel/issues/952>`_, `#978 <https://github.com/holoviz/panel/issues/978>`_) [@ceball & @philippjfr]
- Added `Param` reference notebook (`#944 <https://github.com/holoviz/panel/issues/994>`_) [@MarcSkovMadsen]
- Added `Divider` reference notebook [@philippjfr]

Version 0.7.0
-------------

Date: 2019-11-18

This major release includes significant new functionality along with important bug and documentation fixes, including contributions from @philippjfr (maintainer and lead developer), @xavArtley (VTK support), @jbednar (docs), @DancingQuanta (FileInput), @a-recknagel (Python 3.8 support, misc), @julwin (TextAreaInput, PasswordInput), @rs2 (example notebooks), @xtaje (default values), @Karamya (Audio widget), @ceball, @ahuang11 , @eddienko, @Jacob-Barhak, @jlstevens, @jsignell, @kleavor, @lsetiawan, @mattpap, @maxibor, and @RedBeardCode.

Major enhancements:

* Added pn.ipywidget() function for using panels and panes as ipwidgets, e.g. in voila (`#745 <https://github.com/holoviz/panel/issues/745>`_, `#755 <https://github.com/holoviz/panel/issues/755>`_, `#771 <https://github.com/holoviz/panel/issues/771>`_)
* Greatly expanded and improved Pipeline, which now allows branching graphs (`#712 <https://github.com/holoviz/panel/issues/712>`_, `#735 <https://github.com/holoviz/panel/issues/735>`_, `#737 <https://github.com/holoviz/panel/issues/737>`_, `#770 <https://github.com/holoviz/panel/issues/770>`_)
* Added streaming helper objects, including for the streamz package (`#767 <https://github.com/holoviz/panel/issues/767>`_, `#769 <https://github.com/holoviz/panel/issues/769>`_)
* Added VTK gallery example and other VTK enhancements (`#605 <https://github.com/holoviz/panel/issues/605>`_, `#606 <https://github.com/holoviz/panel/issues/606>`_, `#715 <https://github.com/holoviz/panel/issues/715>`_, `#729 <https://github.com/holoviz/panel/issues/729>`_)
* Add GridBox layout (`#608 <https://github.com/holoviz/panel/issues/608>`_, `#761 <https://github.com/holoviz/panel/issues/761>`_, `#763 <https://github.com/holoviz/panel/issues/763>`_)
* New widgets and panes:

  * Progress bar (`#726 <https://github.com/holoviz/panel/issues/726>`_)
  * Video (`#696 <https://github.com/holoviz/panel/issues/696>`_)
  * TextAreaInput widget (`#658 <https://github.com/holoviz/panel/issues/658>`_)
  * PasswordInput widget (`#655 <https://github.com/holoviz/panel/issues/655>`_)
  * Divider (`#756 <https://github.com/holoviz/panel/issues/756>`_),
  * bi-directional jslink (`#764 <https://github.com/holoviz/panel/issues/764>`_)
  * interactive DataFrame pane for Pandas, Dask and Streamz dataframes (`#560 <https://github.com/holoviz/panel/issues/560>`_, `#751 <https://github.com/holoviz/panel/issues/751>`_)

Other enhancements:

* Make Row/Column scrollable (`#760 <https://github.com/holoviz/panel/issues/760>`_)
* Support file-like objects (not just paths) for images (`#686 <https://github.com/holoviz/panel/issues/686>`_)
* Added isdatetime utility (`#687 <https://github.com/holoviz/panel/issues/687>`_)
* Added repr, kill_all_servers, and cache to pn.state (`#697 <https://github.com/holoviz/panel/issues/697>`_, `#776 <https://github.com/holoviz/panel/issues/776>`_)
* Added Slider value_throttled parameter (`#777 <https://github.com/holoviz/panel/issues/777>`_)
* Extended existing widgets and panes:

  * WidgetBox can be disabled programmatically (`#532 <https://github.com/holoviz/panel/issues/532>`_)
  * Templates can now render inside a notebook cell (`#666 <https://github.com/holoviz/panel/issues/666>`_)
  * Added jscallback method to Viewable objects (`#665 <https://github.com/holoviz/panel/issues/665>`_)
  * Added min_characters parameter to AutocompleteInput (`#721 <https://github.com/holoviz/panel/issues/721>`_)
  * Added accept parameter to FileInput (`#602 <https://github.com/holoviz/panel/issues/602>`_)
  * Added definition_order parameter to CrossSelector (`#570 <https://github.com/holoviz/panel/issues/570>`_)
  * Misc widget fixes and improvements (`#703 <https://github.com/holoviz/panel/issues/703>`_, `#717 <https://github.com/holoviz/panel/issues/717>`_, `#724 <https://github.com/holoviz/panel/issues/724>`_, `#762 <https://github.com/holoviz/panel/issues/762>`_, `#775 <https://github.com/holoviz/panel/issues/775>`_)

Bug fixes and minor improvements:

* Removed mutable default args (`#692 <https://github.com/holoviz/panel/issues/692>`_, `#694 <https://github.com/holoviz/panel/issues/694>`_)
* Improved tests (`#691 <https://github.com/holoviz/panel/issues/691>`_, `#699 <https://github.com/holoviz/panel/issues/699>`_, `#700 <https://github.com/holoviz/panel/issues/700>`_)
* Improved fancy layout for scrubber (`#571 <https://github.com/holoviz/panel/issues/571>`_)
* Improved plotly datetime handling (`#688 <https://github.com/holoviz/panel/issues/688>`_, `#698 <https://github.com/holoviz/panel/issues/698>`_)
* Improved JSON embedding (`#589 <https://github.com/holoviz/panel/issues/589>`_)
* Misc fixes and improvements (`#626 <https://github.com/holoviz/panel/issues/626>`_, `#631 <https://github.com/holoviz/panel/issues/631>`_, `#645 <https://github.com/holoviz/panel/issues/645>`_, `#662 <https://github.com/holoviz/panel/issues/662>`_, `#681 <https://github.com/holoviz/panel/issues/681>`_, `#689 <https://github.com/holoviz/panel/issues/689>`_, `#695 <https://github.com/holoviz/panel/issues/695>`_, `#723 <https://github.com/holoviz/panel/issues/723>`_, `#725 <https://github.com/holoviz/panel/issues/725>`_, `#738 <https://github.com/holoviz/panel/issues/738>`_, `#743 <https://github.com/holoviz/panel/issues/743>`_, `#744 <https://github.com/holoviz/panel/issues/744>`_, `#748 <https://github.com/holoviz/panel/issues/748>`_, `#749 <https://github.com/holoviz/panel/issues/749>`_, `#758 <https://github.com/holoviz/panel/issues/758>`_, `#768 <https://github.com/holoviz/panel/issues/768>`_, `#772 <https://github.com/holoviz/panel/issues/772>`_, `#774 <https://github.com/holoviz/panel/issues/774>`_, `#775 <https://github.com/holoviz/panel/issues/775>`_, `#779 <https://github.com/holoviz/panel/issues/779>`_, `#784 <https://github.com/holoviz/panel/issues/784>`_, `#785 <https://github.com/holoviz/panel/issues/785>`_, `#787 <https://github.com/holoviz/panel/issues/787>`_, `#788 <https://github.com/holoviz/panel/issues/788>`_, `#789 <https://github.com/holoviz/panel/issues/789>`_)
* Prepare support for python 3.8 (`#702 <https://github.com/holoviz/panel/issues/702>`_)

Documentation:

* Expanded and updated FAQ (`#750 <https://github.com/holoviz/panel/issues/750>`_, `#765 <https://github.com/holoviz/panel/issues/765>`_)
* Add Comparisons section (`#643 <https://github.com/holoviz/panel/issues/643>`_)
* Docs fixes and improvements (`#635 <https://github.com/holoviz/panel/issues/635>`_, `#670 <https://github.com/holoviz/panel/issues/670>`_, `#705 <https://github.com/holoviz/panel/issues/705>`_, `#708 <https://github.com/holoviz/panel/issues/708>`_, `#709 <https://github.com/holoviz/panel/issues/709>`_, `#740 <https://github.com/holoviz/panel/issues/740>`_, `#747 <https://github.com/holoviz/panel/issues/747>`_, `#752 <https://github.com/holoviz/panel/issues/752>`_)

Version 0.6.2
-------------

Date: 2019-08-08

Minor bugfix release patching issues with 0.6.1, primarily in the CI setup. Also removed the not-yet-supported definition_order parameter of pn.CrossSelector.

Version 0.6.4
-------------

Date: 2019-10-08

This release includes a number of important bug fixes along with some minor enhancements, including contributions from @philippjfr, @jsignell, @ahuang11, @jonmmease, and @hoseppan.

Enhancements:

* Allow pn.depends and pn.interact to accept widgets and update their output when widget values change (`#639 <https://github.com/holoviz/panel/issues/639>`_)
* Add fancy_layout option to HoloViews pane (`#543 <https://github.com/holoviz/panel/issues/543>`_)
* Allow not embedding local files (e.g. images) when exporting to HTML (`#625 <https://github.com/holoviz/panel/issues/625>`_)

Bug fixes and minor improvements:

* Restore logging messages that were being suppressed by the distributed package (`#682 <https://github.com/holoviz/panel/issues/682>`_)
* HoloViews fixes and improvements (`#595 <https://github.com/holoviz/panel/issues/595>`_, `#599 <https://github.com/holoviz/panel/issues/599>`_, `#601 <https://github.com/holoviz/panel/issues/601>`_, `#659 <https://github.com/holoviz/panel/issues/659>`_)
* Misc other bug fixes and improvements (`#575 <https://github.com/holoviz/panel/issues/575>`_, `#588 <https://github.com/holoviz/panel/issues/588>`_, `#649 <https://github.com/holoviz/panel/issues/649>`_, `#654 <https://github.com/holoviz/panel/issues/654>`_, `#657 <https://github.com/holoviz/panel/issues/657>`_, `#660 <https://github.com/holoviz/panel/issues/660>`_, `#667 <https://github.com/holoviz/panel/issues/667>`_, `#677 <https://github.com/holoviz/panel/issues/677>`_)

Documentation:

* Added example of opening a URL from jslink (`#607 <https://github.com/holoviz/panel/issues/607>`_)

Version 0.6.3
-------------

Date: 2019-09-19

This release saw a number of important bug and documentation fixes along with some minor enhancements.

Enhancements:

* Added support for embedding Player widget (`#584 <https://github.com/holoviz/panel/issues/584>`_)
* Add support for linking HoloViews plot axes across panels (`#586 <https://github.com/holoviz/panel/issues/586>`_)
* Allow saving to BytesIO buffer (`#596 <https://github.com/holoviz/panel/issues/596>`_) 
* Allow ``PeriodicCallback.period`` to be updated dynamically (`#609 <https://github.com/holoviz/panel/issues/609>`_) 

Bug fixes:

* While hooks are applied to model no events are sent to frontend (`#585 <https://github.com/holoviz/panel/issues/585>`_)
* Various fixes for embedding and rendering (`#594 <https://github.com/holoviz/panel/issues/594>`_)

Documentation:

* New example of periodic callbacks (`#573 <https://github.com/holoviz/panel/issues/573>`_)
* Improve ``panel serve`` documentation (`#611 <https://github.com/holoviz/panel/issues/611>`_, `#614 <https://github.com/holoviz/panel/issues/614>`_)
* Add server deployment guide (`#642 <https://github.com/holoviz/panel/issues/642>`_)

Version 0.6.1
-------------

Date: 2019-08-01T14:54:20Z

Version 0.6.0
-------------

Date: 2019-06-02

Version 0.5.1
-------------

Date: 2019-04-11

Minor release closely following up on 0.5.0 updating version requirements to include the officially released bokeh 1.1.0. This release also includes contributions from @philippjfr (with fixes for pipeline and embed features), @xavArtley (addition of a new widget) and @banesullivan (fixes for VTK support).

Features:

* Addition of ``Spinner`` widget for numeric inputs (`#368 <https://github.com/holoviz/panel/issues/368>`_)

Bugfixes:

* Skip jslinked widgets when using embed (`#376 <https://github.com/holoviz/panel/issues/376>`_)
* Correctly revert changes to pipelines when stage transitions fail (`#375 <https://github.com/holoviz/panel/issues/375>`_)
* Fixed bug handling scalar arrays in VTK pane (`#372 <https://github.com/holoviz/panel/issues/372>`_)

Version 0.5.0
-------------

Date: 2019-04-04

Major new release, greatly improving usability and capabilities.  Includes contributions from  @philippjfr (docs, better layouts, and many other features),  @xavArtley (VTK support, Ace code editor), @banesullivan (VTK support),  @jbednar and @rtmatx (docs),  @jsignell (docs, infrastructure, interact support), and @jlstevens (labels for parameters).

Major new features:

* Now uses Bokeh 1.1's greatly improved layout system, requiring far fewer manual adjustments to spacing (`#32 <https://github.com/holoviz/panel/issues/32>`_)
* Greatly expanded docs, now with galleries (`#241 <https://github.com/holoviz/panel/issues/241>`_, `#251 <https://github.com/holoviz/panel/issues/251>`_, `#265 <https://github.com/holoviz/panel/issues/265>`_, `#281 <https://github.com/holoviz/panel/issues/281>`_, `#318 <https://github.com/holoviz/panel/issues/318>`_, `#332 <https://github.com/holoviz/panel/issues/332>`_, `#347 <https://github.com/holoviz/panel/issues/347>`_, `#340 <https://github.com/holoviz/panel/issues/340>`_)
* Allow embedding app state, to support static HTML export of panels (`#250 <https://github.com/holoviz/panel/issues/250>`_)
* Added new GridSpec layout type, making it simpler to make grid-based dashboards (`#338 <https://github.com/holoviz/panel/issues/338>`_)
* Added VTK 3D object pane (`#312 <https://github.com/holoviz/panel/issues/312>`_, `#337 <https://github.com/holoviz/panel/issues/337>`_, `#349 <https://github.com/holoviz/panel/issues/349>`_, `#355 <https://github.com/holoviz/panel/issues/355>`_, `#363 <https://github.com/holoviz/panel/issues/363>`_)
* Added Ace code editor pane (`#359 <https://github.com/holoviz/panel/issues/359>`_)
* Allow defining external JS and CSS resources via config, making it easier to extend Panel (`#330 <https://github.com/holoviz/panel/issues/330>`_)
* Add HTML model capable of executing JS code, allowing more complex embedded items (`#32 <https://github.com/holoviz/panel/issues/32>`_)
* Add a KaTeX and MathJax based LaTeX pane, replacing the previous limited matplotlib/PNG-based support (`#311 <https://github.com/holoviz/panel/issues/311>`_)

Other new features:

* Allow passing Parameter instances to Param pane, making it much simpler to work with individual parameters (`#303 <https://github.com/holoviz/panel/issues/303>`_)
* Added parameter for widget alignment (`#367 <https://github.com/holoviz/panel/issues/367>`_)
* Allow specifying initial value when specifying min/max/step for interact (`#334 <https://github.com/holoviz/panel/issues/334>`_)
* Add support for param.Number step (`#365 <https://github.com/holoviz/panel/issues/365>`_)
* Add a PeriodicCallback (`#348 <https://github.com/holoviz/panel/issues/348>`_)
* Expose curdoc and session_context when using serve (`#336 <https://github.com/holoviz/panel/issues/336>`_)
* Add support for saving and loading embedded data from JSON (`#301 <https://github.com/holoviz/panel/issues/301>`_)
* Add support for specifying arbitrary ``label`` for Parameters (`#290 <https://github.com/holoviz/panel/issues/290>`_)
* Add ColorPicker widget (`#267 <https://github.com/holoviz/panel/issues/267>`_)
* Add support for interact title (`#266 <https://github.com/holoviz/panel/issues/266>`_)

Bugfixes and minor improvements:

* Combine HTML and JS in MIME bundle to improve browser compatibility (`#327 <https://github.com/holoviz/panel/issues/327>`_)
* Inlined subobject expand toggle button (`#329 <https://github.com/holoviz/panel/issues/329>`_)
* Use Select widget for ObjectSelector consistently to avoid issues with short lists and numeric lists (`#362 <https://github.com/holoviz/panel/issues/362>`_)
* Various small improvements (`#238 <https://github.com/holoviz/panel/issues/238>`_, `#245 <https://github.com/holoviz/panel/issues/245>`_, `#257 <https://github.com/holoviz/panel/issues/257>`_, `#258 <https://github.com/holoviz/panel/issues/258>`_, `#259 <https://github.com/holoviz/panel/issues/259>`_, `#262 <https://github.com/holoviz/panel/issues/262>`_, `#264 <https://github.com/holoviz/panel/issues/264>`_, `#276 <https://github.com/holoviz/panel/issues/276>`_, `#289 <https://github.com/holoviz/panel/issues/289>`_, `#293 <https://github.com/holoviz/panel/issues/293>`_, `#307 <https://github.com/holoviz/panel/issues/307>`_, `#313 <https://github.com/holoviz/panel/issues/313>`_, `#343 <https://github.com/holoviz/panel/issues/343>`_, `#331 <https://github.com/holoviz/panel/issues/331>`_)
* Various bugfixes (`#247 <https://github.com/holoviz/panel/issues/247>`_, `#261 <https://github.com/holoviz/panel/issues/261>`_, `#263 <https://github.com/holoviz/panel/issues/263>`_, `#282 <https://github.com/holoviz/panel/issues/282>`_, `#288 <https://github.com/holoviz/panel/issues/288>`_, `#291 <https://github.com/holoviz/panel/issues/291>`_, `#297 <https://github.com/holoviz/panel/issues/297>`_, `#295 <https://github.com/holoviz/panel/issues/295>`_, `#305 <https://github.com/holoviz/panel/issues/305>`_, `#309 <https://github.com/holoviz/panel/issues/309>`_, `#322 <https://github.com/holoviz/panel/issues/322>`_, `#328 <https://github.com/holoviz/panel/issues/328>`_, `#341 <https://github.com/holoviz/panel/issues/341>`_, `#345 <https://github.com/holoviz/panel/issues/345>`_, `#354 <https://github.com/holoviz/panel/issues/354>`_, `#364 <https://github.com/holoviz/panel/issues/364>`_)

Changes potentially affecting backwards compatibility:

* Refactored io subpackage (`#315 <https://github.com/holoviz/panel/issues/315>`_)
* Moved panes and widgets into subpackage (`#283 <https://github.com/holoviz/panel/issues/283>`_)
* Cleaned up wdiget, deploy, and export APIs (`#268 <https://github.com/holoviz/panel/issues/268>`_, `#269 <https://github.com/holoviz/panel/issues/269>`_)
* Renamed pane precedence to priority to avoid confusion with Param precedence (`#235 <https://github.com/holoviz/panel/issues/235>`_)

Version 0.3.1
-------------

Date: 2018-12-05

Minor release fixing packaging issues.

Version 0.3.0
-------------

Date: 2018-12-05

Thanks to @mhc03 for bugfixes.

New features and enhancements

* New app: Euler's Method (`#161 <https://github.com/holoviz/panel/issues/161>`_)
* New widgets and panes: Player (`#110 <https://github.com/holoviz/panel/issues/110>`_), DiscretePlayer (`#171 <https://github.com/holoviz/panel/issues/171>`_), CrossSelector (`#153 <https://github.com/holoviz/panel/issues/153>`_)
* Spinner (spinner.gif)
* Compositional string reprs (`#129 <https://github.com/holoviz/panel/issues/129>`_)
* Add Param.widgets parameter to override default widgets (`#172 <https://github.com/holoviz/panel/issues/172>`_)
* Pipeline improvements (`#145 <https://github.com/holoviz/panel/issues/145>`_, etc.)
* Additional entry points for user commands (`#176 <https://github.com/holoviz/panel/issues/176>`_)
* Support calling from anaconda-project (`#133 <https://github.com/holoviz/panel/issues/133>`_)
* Improved docs

Bugfixes:

* Fix example packaging (`#177 <https://github.com/holoviz/panel/issues/177>`_)
* Various bugfixes and compatibility improvements (`#126 <https://github.com/holoviz/panel/issues/126>`_, `#128 <https://github.com/holoviz/panel/issues/128>`_, `#132 <https://github.com/holoviz/panel/issues/132>`_, `#136 <https://github.com/holoviz/panel/issues/136>`_, `#141 <https://github.com/holoviz/panel/issues/141>`_, `#142 <https://github.com/holoviz/panel/issues/142>`_, `#150 <https://github.com/holoviz/panel/issues/150>`_, `#151 <https://github.com/holoviz/panel/issues/151>`_, `#154 <https://github.com/holoviz/panel/issues/154>`_, etc.)

Compatibility changes

* Renamed Param expand options (`#127 <https://github.com/holoviz/panel/issues/127>`_)

Version 0.4.0
-------------

Date: 2019-01-28

Thanks to @xavArtley for several contributions, and to @lebedov for bugfixes.

New features:

* Now Python2 compatible (`#225 <https://github.com/holoviz/panel/issues/225>`_)
* Audio player widget (`#215 <https://github.com/holoviz/panel/issues/215>`_, `#221 <https://github.com/holoviz/panel/issues/221>`_)
* FileInput widget (`#207 <https://github.com/holoviz/panel/issues/207>`_)
* General support for linking Panel objects, even in static exports (`#199 <https://github.com/holoviz/panel/issues/199>`_)
* New user-guide notebooks: Introduction (`#178 <https://github.com/holoviz/panel/issues/178>`_), Links (`#195 <https://github.com/holoviz/panel/issues/195>`_).

Enhancements:

* Improved Pipeline (`#220 <https://github.com/holoviz/panel/issues/220>`_, `#222 <https://github.com/holoviz/panel/issues/222>`_)

Bug fixes:

* Windows-specific issues (`#204 <https://github.com/holoviz/panel/issues/204>`_, `#209 <https://github.com/holoviz/panel/issues/209>`_, etc.)
* Various bugfixes (`#188 <https://github.com/holoviz/panel/issues/188>`_, `#189 <https://github.com/holoviz/panel/issues/189>`_, `#190 <https://github.com/holoviz/panel/issues/190>`_, `#203 <https://github.com/holoviz/panel/issues/203>`_)

Version 0.1.3
-------------

Date: 2018-10-23
