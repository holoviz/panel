Releases
========

Version 0.11.2
--------------

Date: 2021-04-08

The 0.11.2 release is a micro-release fixing a number of smaller
bugs. Many thanks to @Hoxbro, @dhruvbalwada, @rmorshea,
@MarcSkovMadsen, @fleming79, @OBITURASU and @philippjfr for their
contributions to this release.

Enhancements:

- Optimize adding of roots to templates to avoid multiple preprocessing cycles (`#2096 <https://github.com/holoviz/panel/issues/2096>`__)
- Use schema to support date(time) dtypes on ``Perspective`` (`#2130 <https://github.com/holoviz/panel/issues/2130>`__)

Bug fixes:

- Fix regression on ``Video`` pane causing video not to be rendered at all (`#2109 <https://github.com/holoviz/panel/issues/2109>`__)
- Fix missing closing tag in Fast templates (`#2121 <https://github.com/holoviz/panel/issues/2121>`__)
- Remove bootstrap CSS from ``FastGridTemplate`` (`#2123 <https://github.com/holoviz/panel/issues/2123>`__)
- Ensure ``Tabulator`` selection can be set from Python (`#2128 <https://github.com/holoviz/panel/issues/2128>`__)
- Ensure changes on ReactiveData objects are scheduled correctly on server (`#2134 <https://github.com/holoviz/panel/issues/2134>`__)
- Fix for ``Player`` widget when start value is 0 (`#2141 <https://github.com/holoviz/panel/issues/2141>`__)
- Support single quotes on JSON pane (`#2143 <https://github.com/holoviz/panel/issues/2143>`__)
- Fix divide by zero issues when value_change is computed from zero baseline (`#2148 <https://github.com/holoviz/panel/issues/2148>`__)
- Ensure ``GridSpec`` handles overrides across multiple cells (`#2150 <https://github.com/holoviz/panel/issues/2150>`__)

Documentation:

- Fix typo in Binder section of server deployment documentation (`#2118 <https://github.com/holoviz/panel/issues/2118>`__)
- Improve documentation surrounding watch=True in Param user guide (`#2120 <https://github.com/holoviz/panel/issues/2120>`__)

Compatibility:

- Ensure IDOM pane configures paths correctly for latest version (`#2117 <https://github.com/holoviz/panel/issues/2127>`__, `#2132 <https://github.com/holoviz/panel/issues/2132>`__)

Version 0.11.1
--------------

Date: 2021-03-15

The 0.11.1 release is a micro-release addressing a number of smaller
bugs in the last release. Many thanks to the contributors to this
release including @Hoxbro, @xavArtley, @Jacob-Barhak and @philippjfr.

Enhancements:

- Allow setting horizontal and vertical alignment separately (`#2072 <https://github.com/holoviz/panel/issues/2072>`__)
- Expose widgets ``visible`` property (`#2065 <https://github.com/holoviz/panel/issues/2065>`__)
- Allow bind to extract dependencies and evaluate other dynamic functions (`#2056 <https://github.com/holoviz/panel/issues/2056>`__)
- Allow setting ``root_directory`` on ``FileSelector`` widget (`#2086 <https://github.com/holoviz/panel/issues/2086()

Bug fixes:

- Fixed loading of jQuery in ``BootstrapTemplate`` (`#2057 <https://github.com/holoviz/panel/issues/2057>`__)
- Fix VTK imports to ensure ``VTKVolume`` pane renders grids (`#2071 <https://github.com/holoviz/panel/issues/2071>`__)
- Fix loading of template resources from relative paths (`#2067 <https://github.com/holoviz/panel/issues/2067>`__)
- Fix ``Spinner`` component overflow (`#2070 <https://github.com/holoviz/panel/issues/2070>`__)
- Handle integer column names on ``Perspective`` widget (`#2069 <https://github.com/holoviz/panel/issues/2069>`__)
- Fix bundling of template resources (`#2076 <https://github.com/holoviz/panel/issues/2076>`__)
- Fix ``value_throttled`` in ``pn.depends`` decorator (`#2085 <https://github.com/holoviz/panel/issues/2085>`__)

Compatibility:

- Switch GitHub OAuth to use header authorization token (`#2073 <https://github.com/holoviz/panel/issues/2073>`__)


Version 0.11.0
--------------

Date: 2021-03-02

The 0.11.0 release brings a number of exciting new features to Panel as well as some enhancements and bug fixes. This release is also required for Bokeh 2.3 compatibility since a lot of changes to the Bokeh property system required updates. Many thanks to the many contributors to this release including @MarcSkovMadsen, @xavArtley, @hyamanieu, @cloud-rocket, @kcpevey, @kaseyrussell, @miliante, @AjayThorve and @philippjfr.

Major features:

- A ``Perspective`` pane based on the FINOS Perspective library (`#2034 <https://github.com/holoviz/panel/issues/2034>`__)
- Implement ``--autoreload`` functionality for the Panel server (`#1983 <https://github.com/holoviz/panel/issues/1983>`__)
- Add ``--warm`` option to panel serve, useful for pre-loading items into the state cache (`#1971 <https://github.com/holoviz/panel/issues/1971>`__)
- Add ability to define JS modules and Template specific resources (`#1967 <https://github.com/holoviz/panel/issues/1967>`__)
- ``panel.serve`` now supports serving static files and Bokeh apps, not just Panel apps (`#1939 <https://github.com/holoviz/panel/issues/1939>`__) 
- Add a ``TrendIndicator`` for conveniently showing history and value of a numeric quantity (`#1895 <https://github.com/holoviz/panel/issues/1895>`__)
- Add ``TextToSpeech`` widget (`#1878 <https://github.com/holoviz/panel/issues/1878>`__)
- Add ``SpeechToText`` widget (`#1880 <https://github.com/holoviz/panel/issues/1880>`__)
- Add ``loading`` parameter and spinners to all components (`#1730 <https://github.com/holoviz/panel/issues/1730>`__, `#2026 <https://github.com/holoviz/panel/issues/2026>`__)
- Add ``IDOM`` pane to develop interactive HTML components in Python (`#2004 <https://github.com/holoviz/panel/issues/2004>`__)
- Add powerful new ``Tabulator`` widget for flexible and configurable display of tabular data (`#1531 <https://github.com/holoviz/panel/issues/1531>`__, `#1887 <https://github.com/holoviz/panel/issues/1887>`__) 

Enhancements:

- Add watch argument to ``bind`` function so that covers all the features of pn.depends (`#2000 <https://github.com/holoviz/panel/issues/2000>`__)
- Add ``format`` parameter to DatetimeRangeInput widget (`#2043 <https://github.com/holoviz/panel/issues/2043>`__) 
- Allow ``ParamMethod`` and ``ParamFunction`` to evaluate lazily (`#1966 <https://github.com/holoviz/panel/issues/1966>`__)
- Add ``value_input`` parameter to TextInput widgets (`#2007 <https://github.com/holoviz/panel/issues/2007>`__)
- Implement ``Glyph3dMapper`` support for ``VTK`` panes (`#2002 <https://github.com/holoviz/panel/issues/2002>`__, `#2003 <https://github.com/holoviz/panel/issues/2003>`__)
- Add Jupyter server extension to serve resources (`#1982 <https://github.com/holoviz/panel/issues/1982>`__)
- Enhancements for ``DarkTheme`` (`#1964 <https://github.com/holoviz/panel/issues/1964>`__)
- Add ``refresh`` functionality to ``FileSelector`` (`#1962 <https://github.com/holoviz/panel/issues/1962>`__)
- Add support for Auth0 authentication (`#1934 <https://github.com/holoviz/panel/issues/1934>`__)
- Avoid recursive preprocessing slowing down rendering (`#1852 <https://github.com/holoviz/panel/issues/1852>`__)
- Add support for per-layer tooltips on ``DeckGL`` pane (`#1846 <https://github.com/holoviz/panel/issues/1846>`__)
- Add ``Viewer`` baseclass for custom user components (`#2045 <https://github.com/holoviz/panel/issues/2045>`__)

Bug fixes:

- Fixed ``FileSelector`` file icon on selected files (`#2046 <https://github.com/holoviz/panel/issues/2046>`__)
- Drop query args when checking URLs (`#2037 <https://github.com/holoviz/panel/issues/2037>`__)
- Fix ``Card.header_background`` propagation (`#2035 <https://github.com/holoviz/panel/issues/2035>`__)
- Disable ``GoldenTemplate`` sidebar when empty (`#2017 <https://github.com/holoviz/panel/issues/2017>`__)
- Ensure ``Card.collapsed`` and ``Accordion.active`` parameters are synced (`#2009 <https://github.com/holoviz/panel/issues/2009>`__)
- Fix inline resources when saving (`#1956 <https://github.com/holoviz/panel/issues/1956>`__)
- Switch ``Param`` pane widget type when bounds (un)defined (`#1953 <https://github.com/holoviz/panel/issues/1953>`__)

Compatibility:

- Compatibility with Bokeh>=2.3 (`#1948 <https://github.com/holoviz/panel/issues/1948>`__, `#1988 <https://github.com/holoviz/panel/issues/1988>`__, `#1991 <https://github.com/holoviz/panel/issues/1991>`__)
- Updated ``ECharts`` pane to 5.0.2 of JS library (`#2016 <https://github.com/holoviz/panel/issues/2016>`__)

Documentation:

- Document pn.bind in API user guide (`#1973)

Version 0.10.3
--------------

Date: 2021-01-18

Another micro-release in the 0.10.x series focusing primarily on bug and regression fixes. Many thanks to @miliante, @MarcSkovMadsen, @Hoxbro, @jlstevens, @jbednar and @philippjfr.

Bug fixes:

- Fix inverted axes on HoloViews plots (`#1732 <https://github.com/holoviz/panel/issues/1732>`__)
- Fix enabling/disabling of ``FileDownload`` widget (`#1510 <https://github.com/holoviz/panel/issues/1510>`__, `#1820 <https://github.com/holoviz/panel/issues/1820>`__)
- Fix issues serving template resources on server with route prefix (`#1821 <https://github.com/holoviz/panel/issues/1821>`__)
- Fixes for rendering ``ECharts`` from pyecharts (`#1874 <https://github.com/holoviz/panel/issues/1874>`__, `#1876 <https://github.com/holoviz/panel/issues/1876>`__)
- Fix issues with scroll behavior when expanding/collapsing Card/Accordion (`#1833 <https://github.com/holoviz/panel/issues/1833>`__, `#1884 <https://github.com/holoviz/panel/issues/1884>`__)
- Ensure DiscreSlider label is correctly linked to value (`#1906 <https://github.com/holoviz/panel/issues/1906>`__)
- Fix support for setting header_color and header_background on all templates (`#1872 <https://github.com/holoviz/panel/issues/1872>`__)
- Ensure that Template preprocessors are applied during initialization (`#1922 <https://github.com/holoviz/panel/issues/1922>`__)

Enhancements:

- Support throttled in ``Param`` widget (`#1800 <https://github.com/holoviz/panel/pull/1800>`__)
- Support rendering of hvPlot Interactive objects (`#1824 <https://github.com/holoviz/panel/issues/1824>`__)
- Allow recording session launch time in server session_info (`#1909 <https://github.com/holoviz/panel/pull/1909>`__)
- Add Button.value parameter (`#1910 <https://github.com/holoviz/panel/issues/1910>`__)
- Support upload of multiple parameters on FileInput (`#1911 <https://github.com/holoviz/panel/pull/1911>`__)
- Improve support for ``DarkTheme`` in templates (`#1855 <https://github.com/holoviz/panel/pull/1855>`__, `#1856 <https://github.com/holoviz/panel/pull/1856>`__)

Documentation:

- Fixed IntSlider and FloatSlider example (`#1825 <https://github.com/holoviz/panel/pull/1825>`__)
- Updated instructions for using Panel in JupyterLab (`#1908 <https://github.com/holoviz/panel/pull/1908>`__)


Version 0.10.2
--------------

Date: 2020-11-13

This is another micro-release primarily fixing various minor bugs in functionality introduced as part of the 0.10.0 release. Many thanks to @MarcSkovMadsen, @ahuang11, @xavArtley, @Hoxbro, @jbednar and @philippjfr.

Bug fixes:

- Fix various issues with Template CSS (`#1663 <https://github.com/holoviz/panel/pull/1663>`__, `#1742 <https://github.com/holoviz/panel/pull/1742>`__)
- Fix BytesIO/StringIO buffers as input to image xpanes (`#1711 <https://github.com/holoviz/panel/issues/1711>`__)
- Fix out-of-bounds errors when assigning to ``GridSpec`` with fixed ``ncols`` (`#1721 <https://github.com/holoviz/panel/pull/1721>`__)
- Fix deserialization issues for ``Plotly.hover_data`` (`#1722 <https://github.com/holoviz/panel/pull/>`__)
- Fixed updating of ``Alert`` parameters after initialization (`#1725 <https://github.com/holoviz/panel/pull/1725>`__)
- Fix ordering of items added to Template areas (`#1736 <https://github.com/holoviz/panel/pull/1736>`__)
- Fix interactivity for items in Card (`#1750 <https://github.com/holoviz/panel/pull/1750>`__)
- Ensure onload callbacks are only run once (`#1746 <https://github.com/holoviz/panel/pull/1746>`__)
- Allow overriding items in grid based templates (`#1741 <https://github.com/holoviz/panel/pull/1741>`__)
- Ensure ``ECharts`` and ``ipywidget`` rerender when in ``Card`` (`#1765 <https://github.com/holoviz/panel/pull/1765>`__)
- Ensure template dark theme persists on HoloViews plots (`#1764 <https://github.com/holoviz/panel/pull/1764>`__)
- Fix responsive height in ``Plotly`` pane (`#1770 <https://github.com/holoviz/panel/pull/1770>`__)
- Ensure image panes resize in width and height (`#1777 <https://github.com/holoviz/panel/pull/1777>`_))
- Fix issues with ``Location.sync`` serialization (`#1784 <https://github.com/holoviz/panel/pull/1784>`_))
- Add ``throttled`` argument to interact (`#1259 <https://github.com/holoviz/panel/pull/1259>`__)
- ECharts pane now loads echarts-gl for 3D support (`#1785 <https://github.com/holoviz/panel/pull/1785>`__)
- Ensure ``CheckBoxGroup`` and ``CheckButtonGroup`` support arbitrary objects as options (`#1793 <https://github.com/holoviz/panel/pull/1793>`_))

Enhancements:

- Improved OAuth encryption key validation (`#1762 <https://github.com/holoviz/panel/pull/1762>`__)
- Add ``progress`` option to ``.save`` method (`#1776 <https://github.com/holoviz/panel/pull/1776>`__)

Version 0.10.1
--------------

Date: 2020-10-27

This is a micro release of Panel primarily containing bug fixes
following the 0.10.0 release. Many thanks to @MarcSkovMadsen, @jbednar
and @philippjfr for contributing fixes to this release.

Enhancements:

- Add pn.bind function to bind parameters to a function (`#1629 <https://github.com/holoviz/panel/issues/1629>`__)

Bug fixes:

- Fix ``WidgetBox`` CSS (`#855 <https://github.com/holoviz/panel/pull/855>`__)
- Fix CSS load order in Templates (`#1698 <https://github.com/holoviz/panel/pull/1698>`__)
- Allow setting ``DiscreteSlider`` orientation (`#1683 <https://github.com/holoviz/panel/pull/1683>`__)
- Ensure JS callbacks and links are only set up once on templates (`#1700 <https://github.com/holoviz/panel/pull/1700>`__)
- Initialize pipeline only once (`#1705 <https://github.com/holoviz/panel/pull/1705>``__)
- Allow using ``NumberInput`` as ``Param`` pane widget (`#1708 <https://github.com/holoviz/panel/issues/1708>`__)

Version 0.10.0
--------------

Date: 2020-10-23

This is a minor release of Panel, with a slew of new features and
enhancements, plus a wide array of minor fixes and improvements to the
documentation, and website. Many thanks to the people who contributed
to this release, including @philippjfr, @MarkSkovMadsen (alert pane,
templates, docs), @xavArtley (VTK improvements, templates,
input/spinner widgets), @maximlt (panel serve), @jbednar (docs,
reviewing), @kebowen (templates), @ahuang11 (datepicker), @nghenzi
(react template, bugfixes), @nritsche (panel serve), @ltalirz
(autocomplete input), @BoBednar (docs), @tmikolajczyk, @halilbay,
@Hoxbro, and @ceball (testing and automation).

Features:

-  Add ``Card`` and ``Accordion`` layout
   (`#1262 <https://github.com/holoviz/panel/pull/1262>`__,
   `#1266 <https://github.com/holoviz/panel/pull/1266>`__,
   `#1267 <https://github.com/holoviz/panel/pull/1267>`__,
   `#1616 <https://github.com/holoviz/panel/pull/1616>`__,
   `#1619 <https://github.com/holoviz/panel/pull/1619>`__)
-  Location component
   (`#1150 <https://github.com/holoviz/panel/pull/1150>`__,
   `#1297 <https://github.com/holoviz/panel/pull/1297>`__,
   `#1357 <https://github.com/holoviz/panel/pull/1357>`__,
   `#1407 <https://github.com/holoviz/panel/pull/1407>`__,
   `#1498 <https://github.com/holoviz/panel/pull/1498>`__,
   `#1519 <https://github.com/holoviz/panel/pull/1519>`__,
   `#1532 <https://github.com/holoviz/panel/pull/1532>`__,
   `#1638 <https://github.com/holoviz/panel/pull/1638>`__,
   `#1658 <https://github.com/holoviz/panel/pull/1658>`__)
-  VTK improvements: colorbars
   (`#1270 <https://github.com/holoviz/panel/pull/1270>`__),
   synchronization
   (`#1248 <https://github.com/holoviz/panel/pull/1248>`__,
   `#1637 <https://github.com/holoviz/panel/pull/1637>`__), orientation
   widget (`#1635 <https://github.com/holoviz/panel/pull/1635>`__),
   volume controller
   (`#1631 <https://github.com/holoviz/panel/pull/1631>`__),
   serialization
   (`#1596 <https://github.com/holoviz/panel/pull/1596>`__), follower
   (`#1451 <https://github.com/holoviz/panel/pull/1451>`__)
-  Add default templates
   (`#1277 <https://github.com/holoviz/panel/pull/1277>`__,
   `#1374 <https://github.com/holoviz/panel/pull/1374>`__,
   `#1419 <https://github.com/holoviz/panel/pull/1419>`__,
   `#1421 <https://github.com/holoviz/panel/pull/1421>`__,
   `#1459 <https://github.com/holoviz/panel/pull/1459>`__,
   `#1472 <https://github.com/holoviz/panel/pull/1472>`__,
   `#1473 <https://github.com/holoviz/panel/pull/1473>`__,
   `#1479 <https://github.com/holoviz/panel/pull/1479>`__,
   `#1530 <https://github.com/holoviz/panel/pull/1530>`__,
   `#1535 <https://github.com/holoviz/panel/pull/1535>`__,
   `#1608 <https://github.com/holoviz/panel/pull/1608>`__,
   `#1617 <https://github.com/holoviz/panel/pull/1617>`__,
   `#1645 <https://github.com/holoviz/panel/pull/1645>`__,
   `#1647 <https://github.com/holoviz/panel/pull/1647>`__,
   `#1650 <https://github.com/holoviz/panel/pull/1650>`__,
   `#1660 <https://github.com/holoviz/panel/pull/1660>`__,
   `#1661 <https://github.com/holoviz/panel/pull/1661>`__,
   `#1662 <https://github.com/holoviz/panel/pull/1662>`__,
   `#1677 <https://github.com/holoviz/panel/pull/1677>`__,
   `#1682 <https://github.com/holoviz/panel/pull/1682>`__,
   `#1685 <https://github.com/holoviz/panel/pull/1685>`__,
   `#1687 <https://github.com/holoviz/panel/pull/1687>`__)
-  Improvements for ipywidgets support
   (`#1285 <https://github.com/holoviz/panel/pull/1285>`__,
   `#1389 <https://github.com/holoviz/panel/pull/1389>`__,
   `#1476 <https://github.com/holoviz/panel/pull/1476>`__,
   `#1675 <https://github.com/holoviz/panel/pull/1675>`__)
-  Add ``pn.state.busy`` and ``pn.state.onload`` callback
   (`#1392 <https://github.com/holoviz/panel/pull/1392>`__,
   `#1518 <https://github.com/holoviz/panel/pull/1518>`__)
-  Add support for serving static files
   (`#1319 <https://github.com/holoviz/panel/pull/1319>`__,
   `#1492 <https://github.com/holoviz/panel/pull/1492>`__)
-  Add an ``Alert`` pane
   (`#1181 <https://github.com/holoviz/panel/pull/1181>`__,
   `#1422 <https://github.com/holoviz/panel/pull/1422>`__)
-  Add ability to declare OAuth provider
   (`#820 <https://github.com/holoviz/panel/pull/820>`__,
   `#1468 <https://github.com/holoviz/panel/pull/1468>`__,
   `#1470 <https://github.com/holoviz/panel/pull/1470>`__,
   `#1474 <https://github.com/holoviz/panel/pull/1474>`__,
   `#1475 <https://github.com/holoviz/panel/pull/1475>`__,
   `#1480 <https://github.com/holoviz/panel/pull/1480>`__,
   `#1508 <https://github.com/holoviz/panel/pull/1508>`__,
   `#1594 <https://github.com/holoviz/panel/pull/1594>`__,
   `#1625 <https://github.com/holoviz/panel/pull/1625>`__)
-  Add ``ECharts`` pane
   (`#1484 <https://github.com/holoviz/panel/pull/1484>`__,
   `#1691 <https://github.com/holoviz/panel/pull/1691>`__)
-  Add busy/loading indicators and enable on Template
   (`#1493 <https://github.com/holoviz/panel/pull/1493>`__)
-  Allow serving REST APIs as part of panel serve
   (`#1164 <https://github.com/holoviz/panel/pull/1164>`__)
-  Add ``pn.state.as_cached`` function
   (`#1526 <https://github.com/holoviz/panel/pull/1526>`__)
-  Add MenuButton widget
   (`#1533 <https://github.com/holoviz/panel/pull/1533>`__)
-  Add a number of ``ValueIndicators``
   (`#1528 <https://github.com/holoviz/panel/pull/1528>`__,
   `#1590 <https://github.com/holoviz/panel/pull/1590>`__,
   `#1627 <https://github.com/holoviz/panel/pull/1627>`__,
   `#1628 <https://github.com/holoviz/panel/pull/1628>`__,
   `#1633 <https://github.com/holoviz/panel/pull/1633>`__)
-  Add support for ``param.Event``
   (`#1600 <https://github.com/holoviz/panel/pull/1600>`__)
-  Add ``IntInput`` and ``FloatInput`` widgets
   (`#1513 <https://github.com/holoviz/panel/pull/1513>`__)
-  Record session statistics on ``pn.state.session_info``
   (`#1615 <https://github.com/holoviz/panel/pull/1615>`__,
   `#1620 <https://github.com/holoviz/panel/pull/1620>`__,
   `#1634 <https://github.com/holoviz/panel/pull/1634>`__)
-  Bundle external JS dependencies for custom models and templates
   (`#1651 <https://github.com/holoviz/panel/pull/1651>`__,
   `#1655 <https://github.com/holoviz/panel/pull/1655>`__)
-  Add support for ipympl (interactive mode) on Matplotlib
   (`#1469 <https://github.com/holoviz/panel/pull/1469>`__)

Enhancements:

-  Allow defining explicit embed states
   (`#1274 <https://github.com/holoviz/panel/pull/1274>`__)
-  Implement ``__add__`` and ``__iadd__`` on layouts
   (`#1282 <https://github.com/holoviz/panel/pull/1282>`__)
-  Add support for hierarchical multi-indexed DataFrame
   (`#1383 <https://github.com/holoviz/panel/pull/1383>`__)
-  Add ``show_index`` option to ``DataFrame`` widget
   (`#1488 <https://github.com/holoviz/panel/pull/1488>`__)
-  Link widgets with same name during embed
   (`#1543 <https://github.com/holoviz/panel/pull/1543>`__)
-  Wait until JS dependency is loaded before rendering
   (`#1577 <https://github.com/holoviz/panel/pull/1577>`__)
-  For ``AutocompleteInput``, allow user-defined values
   (`#1588 <https://github.com/holoviz/panel/pull/1588>`__) and
   case-insensitivity
   (`#1548 <https://github.com/holoviz/panel/pull/1548>`__)
-  Allow dates to be disabled in DatePicker
   (`#1524 <https://github.com/holoviz/panel/pull/1524>`__)
-  Enable new features for a Bokeh DataTable
   (`#1512 <https://github.com/holoviz/panel/pull/1512>`__)
-  Panel serve improvements: MethodType parameter
   (`#1450 <https://github.com/holoviz/panel/pull/1450>`__), title per
   app (`#1354 <https://github.com/holoviz/panel/pull/1354>`__)
-  Server deployment guide for Azure
   (`#1350 <https://github.com/holoviz/panel/pull/1350>`__)
-  Add Widget.from\_param classmethod
   (`#1344 <https://github.com/holoviz/panel/pull/1344>`__)
-  More options for ACE widget
   (`#1391 <https://github.com/holoviz/panel/pull/1391>`__)

Bugfixes and minor improvements:

-  VTK model compilation
   (`#1669 <https://github.com/holoviz/panel/pull/1669>`__),
   findPokedRenderer
   (`#1456 <https://github.com/holoviz/panel/pull/1456>`__), misc
   (`#1406 <https://github.com/holoviz/panel/pull/1406>`__,
   `#1409 <https://github.com/holoviz/panel/pull/1409>`__)
-  Fix parameterized parameter handling
   (`#1584 <https://github.com/holoviz/panel/pull/1584>`__)
-  Theming improvements
   (`#1670 <https://github.com/holoviz/panel/pull/1670>`__)
-  JS dependency handling
   (`#1626 <https://github.com/holoviz/panel/pull/1626>`__)
-  Parameterized: explicit triggering
   (`#1623 <https://github.com/holoviz/panel/pull/1623>`__), strings
   with None default
   (`#1622 <https://github.com/holoviz/panel/pull/1622>`__)
-  Docs and examples
   (`#1242 <https://github.com/holoviz/panel/pull/1242>`__,
   `#1435 <https://github.com/holoviz/panel/pull/1435>`__,
   `#1448 <https://github.com/holoviz/panel/pull/1448>`__,
   `#1467 <https://github.com/holoviz/panel/pull/1467>`__,
   `#1540 <https://github.com/holoviz/panel/pull/1540>`__,
   `#1541 <https://github.com/holoviz/panel/pull/1541>`__,
   `#1558 <https://github.com/holoviz/panel/pull/1558>`__,
   `#1570 <https://github.com/holoviz/panel/pull/1570>`__,
   `#1576 <https://github.com/holoviz/panel/pull/1576>`__,
   `#1609 <https://github.com/holoviz/panel/pull/1609>`__)
-  Many other minor fixes and improvements
   (`#1284 <https://github.com/holoviz/panel/pull/1284>`__,
   `#1384 <https://github.com/holoviz/panel/pull/1384>`__,
   `#1423 <https://github.com/holoviz/panel/pull/1423>`__,
   `#1489 <https://github.com/holoviz/panel/pull/1489>`__,
   `#1495 <https://github.com/holoviz/panel/pull/1495>`__,
   `#1502 <https://github.com/holoviz/panel/pull/1502>`__,
   `#1503 <https://github.com/holoviz/panel/pull/1503>`__,
   `#1507 <https://github.com/holoviz/panel/pull/1507>`__,
   `#1520 <https://github.com/holoviz/panel/pull/1520>`__,
   `#1521 <https://github.com/holoviz/panel/pull/1521>`__,
   `#1536 <https://github.com/holoviz/panel/pull/1536>`__,
   `#1539 <https://github.com/holoviz/panel/pull/1539>`__,
   `#1546 <https://github.com/holoviz/panel/pull/1546>`__,
   `#1547 <https://github.com/holoviz/panel/pull/1547>`__,
   `#1553 <https://github.com/holoviz/panel/pull/1553>`__,
   `#1562 <https://github.com/holoviz/panel/pull/1562>`__,
   `#1595 <https://github.com/holoviz/panel/pull/1595>`__,
   `#1621 <https://github.com/holoviz/panel/pull/1621>`__,
   `#1639 <https://github.com/holoviz/panel/pull/1639>`__)

Backwards compatibility:

-  Switch away from inline resources in notebook
   (`#1538 <https://github.com/holoviz/panel/pull/1538>`__,
   `#1678 <https://github.com/holoviz/panel/pull/1678>`__)
-  ``Viewable.add_periodic_callback`` is deprecated; use
   `pn.state.add_periodic_callback`
   (`#1542 <https://github.com/holoviz/panel/pull/1542>`__)
-  Use ``widget_type`` instead of ``type`` to override Param widget type
   in Param pane
   (`#1614 <https://github.com/holoviz/panel/pull/1614>`__)
-  ``Spinner`` widget is now called ``NumberInput``
   (`#1513 <https://github.com/holoviz/panel/pull/1513>`__)

Version 0.9.7
-------------

Date: 2020-06-23

The 0.9.6 release unfortunately caused a major regression in layout performance due to the way optimizations in Bokeh and Panel interacted. This release fixes this regression.

- Fix regression in layout performance (`#1453 <https://github.com/holoviz/panel/pull/1453>`_)

Version 0.9.6
-------------

Date: 2020-06-21

This is a minor bug fix release primarily for compatibility with Bokeh versions >=2.1.0 along with a variety of important bug fixes. Many thanks for the many people who contributed to this release including @mattpap, @kebowen730, @xavArtley, @maximlt, @jbednar, @mycarta, @basnijholt, @jbednar and @philippjfr.

- Compatibility with Bokeh 2.1 (`#1424 <https://github.com/holoviz/panel/pull/1424>`_)
- Fixes for `FileDownload` widget handling of callbacks (`#1246 <https://github.com/holoviz/panel/pull/1246>`_, `#1306 <https://github.com/holoviz/panel/pull/1306>`_)
- Improvements and fixes for Param pane widget mapping (`#1301 <https://github.com/holoviz/panel/pull/1301>`_, `#1342 <https://github.com/holoviz/panel/pull/1342>`_, `#1378 <https://github.com/holoviz/panel/pull/1378>`_)
- Fixed bugs handling of closed Tabs (`#1337 <https://github.com/holoviz/panel/pull/1337>`_)
- Fix bug in layout `clone` method (`#1349 <https://github.com/holoviz/panel/pull/1349>`_)
- Improvements for `Player` widget (`#1353 <https://github.com/holoviz/panel/pull/1353>`_, `#1360 <https://github.com/holoviz/panel/pull/1360>`_)
- Fix for `jslink` on Bokeh models (`#1358 <https://github.com/holoviz/panel/pull/1358>`_)
- Fix for rendering geometries in `Vega` pane (`#1359 <https://github.com/holoviz/panel/pull/1359>`_)
- Fix issue with `HoloViews` pane overriding selected renderer (`#1429 <https://github.com/holoviz/panel/pull/1429>`_)
- Fix issues with `JSON` pane depth parameter and rerendering (`#1431 <https://github.com/holoviz/panel/pull/1431>`_)
- Fixed `param.Date` and `param.CalenderDate` parameter mappings (`#1433 <https://github.com/holoviz/panel/pull/1433>`_, `#1434 <https://github.com/holoviz/panel/pull/1434>`_)
- Fixed issue with enabling `num_procs` on `pn.serve` (`#1436 <https://github.com/holoviz/panel/pull/1436>`_)
- Warn if a particular extension could not be loaded (`#1437 <https://github.com/holoviz/panel/pull/1437>`_)
- Fix issues with garbage collection and potential memory leaks (`#1407 <https://github.com/holoviz/panel/pull/1407>`_)
- Support recent versions of pydeck in `DeckGL` pane (`#1443 <https://github.com/holoviz/panel/pull/1443>`_)
- Ensure JS callbacks on widget created from Parameters are initialized (`#1439 <https://github.com/holoviz/panel/pull/1439>`_)


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
- Add Folium example to gallery (`#1189 <https://github.com/holoviz/panel/pull/1189>`_)
- Add `FileDownload` and `FileInput` example to gallery (`#1193 <https://github.com/holoviz/panel/pull/1193>`_)


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
