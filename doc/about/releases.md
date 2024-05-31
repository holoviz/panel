# Releases

See [the HoloViz blog](https://blog.holoviz.org/#category=panel) for a visual summary of the major features added in each release.

## Version 1.4.4

Date: 2024-05-31

This release primarily addresses a critical regression in notebook comm channel handling introduced in 1.4.3 and includes a few minor fixes for Tabulator and documentation related issues. Many thanks to @justinwiley for his first contribution to Panel, @twobitunicorn as a returning contributor and the core contributors @maximlt and @philippjfr for their continued work.

### Bug fixes

- Fix notebook CommManager extraction of buffers ([#6880](https://github.com/holoviz/panel/pull/6880))
- Fix issue when editing timezone-aware datetime column `Tabulator` ([#6879](https://github.com/holoviz/panel/pull/6879))
- Ensure `Tabulator` does not rebuild children when using `embed_content` with `row_content` ([#6881](https://github.com/holoviz/panel/pull/6881))

### Documentation

- Update OAuth documentation to correctly reference auth_code provider ([#6875](https://github.com/holoviz/panel/pull/6875))
- Fix `CheckBoxGroup` `value` type annotation in reference docs ([#6877](https://github.com/holoviz/panel/pull/6877))

## Version 1.4.3

Date: 2024-05-23

This patch release is likely the last in the 1.4.x series. The most important fixes in this release are fixes to ensure keyboard shortcuts do not get triggered inside Panel components for for recent versions of JupyterLab, fixes for OAuth token refreshes, and various documentation fixes. The release also includes a small number of enhancements, including improved UX for the `FileSelector`. Many thanks to the many contributors to this release including @jrycw, @Coderambling, @cdeil, @twobitunicorn, and the maintainers @Hoxbro, @MarcSkovMadsen, @ahuang11, @maximlt and @philippjfr.

### Enhancements

- Add CSS on mouse interaction with `Card` ([#6636](https://github.com/holoviz/panel/pull/6636))
- Make `ChatMessage.reaction_icons` reactive ([#6807](https://github.com/holoviz/panel/pull/6807))
- Allow external library to define additional socket handler ([#6820](https://github.com/holoviz/panel/pull/6820))
- Allow navigating `FileSelector` with double click ([#6843](https://github.com/holoviz/panel/pull/6843))

### Bug fixes

- Ensure reference is resolved when passing options to `from_param` ([#6762](https://github.com/holoviz/panel/pull/6762))
- Ensure token refresh is always scheduled ([#6802](https://github.com/holoviz/panel/pull/6802))
- Fix small memory leak when caching `Design` modifiers ([#4978](https://github.com/holoviz/panel/pull/4978))
- Ensure refreshed tokens can be accessed across processes ([#6817](https://github.com/holoviz/panel/pull/6817))
- Ensure binary buffers are correctly extracted in notebook `CommManager` ([#6818](https://github.com/holoviz/panel/pull/6818))
- Make `Tabulator` resize handling more robust ([#6821](https://github.com/holoviz/panel/pull/6821))
- Fix links in `panel convert` index ([#6828](https://github.com/holoviz/panel/pull/6828))
- Suppress keyboard shortcuts in notebook output ([#6825](https://github.com/holoviz/panel/pull/6825))
- Ensure we don't error out when `FastDesignProvider` is undefined ([#6832](https://github.com/holoviz/panel/pull/6832))
- Ensure model changes are applied while session is starting ([#6835](https://github.com/holoviz/panel/pull/6835))

### Documentation

- Refactor the `hvplot.interactive` tutorial utilizing `pn.rx` ([#6700](https://github.com/holoviz/panel/pull/6700))
- Update styling after upgrade to latest pydata-sphinx-theme ([#6823](https://github.com/holoviz/panel/pull/6823))
- Fix bug in Reset Jupyterlite script ([#6834](https://github.com/holoviz/panel/pull/6834))
- Fix gallery deployment URL ([#6831](https://github.com/holoviz/panel/pull/6831))
- Add redirects for old documentation pages ([#6833](https://github.com/holoviz/panel/pull/6833))
- Remove Google Analytics ([#6836](https://github.com/holoviz/panel/pull/6836))
- Various documentation fixes ([#6829](https://github.com/holoviz/panel/pull/6829))
- Fix link in gallery index ([#6858](https://github.com/holoviz/panel/pull/6858))

## Version 1.4.2

Date: 2024-04-23

This micro-release fixes a number of smaller regressions and bugs including parsing of notebooks. Many thanks to our new contributor @bkreider, our returning contributors, @jrycw and @ea42gh, and our dedicated team of maintainers including @ahuang11, @MarcSkovMadsen and @philippjfr.

### Enhancements

- Allow toggling CTRL+Enter vs Enter to send `ChatAreaInput` ([#6592](https://github.com/holoviz/panel/pull/6592))
- Allow adding JS callbacks in `ChatInterface.button_properties` ([#6706](https://github.com/holoviz/panel/pull/6706))

### Bug fixes

- Fix regression in parsing notebooks served as apps ([#6736](https://github.com/holoviz/panel/pull/6736))
- Do not include placeholder in `ChatInterface.serialize` and properly replace placeholder for streams ([#6734](https://github.com/holoviz/panel/pull/6734))
- Remove `Perspective.toggle_config` which was erroneously reintroduced in 1.4.1 ([#6721](https://github.com/holoviz/panel/pull/6721))
- Fix dynamically setting `ChatMessage` `footer_objects`/`header_objects` ([#6705](https://github.com/holoviz/panel/pull/6705))
- Allow `Location.sync` of DataFrame parameters ([#6745](https://github.com/holoviz/panel/pull/6745))
- Fix and improve Plotly event handling ([#6753](https://github.com/holoviz/panel/pull/6753))
- Fix issue when converting templated apps to Pyodide/PyScript ([#6756](https://github.com/holoviz/panel/pull/6756))
- Fix styling of loading indicator in Fast design ([#6761](https://github.com/holoviz/panel/pull/6761))
- Ensure `VTK` nan, above and below colors are serialized ([#6763](https://github.com/holoviz/panel/pull/6763))
- Fix issues with `Perspective` theme and persist config when switching plugins ([#6764](https://github.com/holoviz/panel/pull/6764))
- Do not restore unmodified parameters in `config.set` triggering undesirable side-effects ([#6772 ([#6771](https://github.com/holoviz/panel/pull/6772))
- Make autoreload module cleanup more robust ([#6771](https://github.com/holoviz/panel/pull/6771))
- Ensure that cache `.clear()` clears the correct function  ([#6771](https://github.com/holoviz/panel/pull/6781))

### Documentation

- Various fixes and cleanup of documentation ([#6704](https://github.com/holoviz/panel/pull/6704), [#6707](https://github.com/holoviz/panel/pull/6707), [#6710](https://github.com/holoviz/panel/pull/6710), [#6755](https://github.com/holoviz/panel/pull/6755),)
- Document how display full html document in iframe ([#6740](https://github.com/holoviz/panel/pull/6740))
- Improve Plotly reference documentation ([#6751](https://github.com/holoviz/panel/pull/6751), [#6760](https://github.com/holoviz/panel/pull/6760))

## Version 1.4.1

Date: 2024-04-05

This micro-release fixes a number of regressions and other bugs introduced in recent releases and further improves the dashboard builder UI. Additionally it includes some tweaks and polish for the new tutorial material. Many thanks to our new contributor @jrycw, our returning contributors @cdeil and @TheoMathurin and our maintainers @ahuang11, @MarcSkovMadsen, @Hoxbro and @philippjfr for their contributions to this release.

### Enhancements

- Allow rendering raw `IPython.display` output in dashboard builder ([#6657](https://github.com/holoviz/panel/pull/6657))
- Improve snapping behavior and add undo functionality in dashboard builder UI ([#6687](https://github.com/holoviz/panel/pull/6687)))

### Bug Fixes

- Fix layout persistence issues in dashboard builder ([#6602](https://github.com/holoviz/panel/pull/6602))
- Ensure `Perspective` loads in notebooks and docs ([#6626](https://github.com/holoviz/panel/pull/6626))
- Allow full reset of dashboard builder layout ([#6625](https://github.com/holoviz/panel/pull/6625))
- Fix issues with `VTK` colormap serialization ([#6651](https://github.com/holoviz/panel/pull/6651))
- Allow `Tabulator` `HTMLTemplateFormatter` to reference multiple columns ([#6663](https://github.com/holoviz/panel/pull/6663))
- Fix loading spinner in converted app without template ([#6665](https://github.com/holoviz/panel/pull/6665))
- Avoid unnecessary rescroll on Column ([#6666](https://github.com/holoviz/panel/pull/6666))
- Fix dynamically updating description tooltips ([#6676](https://github.com/holoviz/panel/pull/6676))
- Ensure Perspective is fully loaded before attempting render ([#6689](https://github.com/holoviz/panel/pull/6689)))
- Ensure busy indicators are always reset ([#6698](https://github.com/holoviz/panel/pull/6698))

### Styling

- Only apply styling to Bootstrap buttons ([#6610](https://github.com/holoviz/panel/pull/6610))
- Change into a slicker `Card` button icon ([#6638](https://github.com/holoviz/panel/pull/6638))
- Fix card header margins ([#6639](https://github.com/holoviz/panel/pull/6639))
- Ensure `Perspective` renders correctly in all browsers ([#6664](https://github.com/holoviz/panel/pull/6664))

### Documentation

- Improve layout builder docs ([#6601](https://github.com/holoviz/panel/pull/6601))
- Various Tutorial fixes ([#6614](https://github.com/holoviz/panel/pull/6614), [#6669](https://github.com/holoviz/panel/pull/6669), [#6670](https://github.com/holoviz/panel/pull/6670), [#6679](https://github.com/holoviz/panel/pull/6679))
- Ensure all docs pages are indexed ([#6615](https://github.com/holoviz/panel/pull/6615))
- Document `Flexbox.gap` parameter ([#6616](https://github.com/holoviz/panel/pull/6616))
- Improve custom template documentation ([#6618](https://github.com/holoviz/panel/pull/6618))
- Improve Layout Builder Docs ([#6619](https://github.com/holoviz/panel/pull/6619))
- Improve PyCharm and Colab notebook documentation ([#6599](https://github.com/holoviz/panel/pull/6599))
- Update gallery endpoint in docs ([#6645](https://github.com/holoviz/panel/pull/6645))
- Various smaller documentation fixes and improvements ([#6682](https://github.com/holoviz/panel/pull/6682), [#6690](https://github.com/holoviz/panel/pull/6690))

## Version 1.4.0

Date: 2024-03-25

This minor release packs a punch both in terms of features, the number of enhancements and bug fixes and perhaps most importantly the addition of a set of tutorials that aim to get novices up-to-speed. The main new feature is a so called `EditableTemplate` which allows arranging dashboards using a drag-and-drop interface and also has strong integration with JupyterLab previews to go from a notebook to a deployed app without having to worry about writing layout code. Next, this release includes a number of need widgets (`NestedSelect`, `DateRangePicker`, `ButtonIcon`), layouts (`Feed`) and panes (`Textual`, `WebP`), and overhauls the autoreload feature with faster and more robust support for reloading entire modules. Lastly this release, along with Param 2.1.0, continues to build on the new reactive expression API making it easy to write reactive expressions and pipelines including support for streaming data with generators. We really appreciate all the work that went into this release and especially want to call out @MarcSkovMadsen's effort in putting together the new tutorial materials. There's more work to do but it's a huge step forward and we're excited to hear your feedback. We want to extend a special thanks to our amazing new crop of new contributors including @atisor73, @Osuwaidi, @suryako, @Davide-sd, @doraaki, @mayonnaisecolouredbenz7, @CTPassion, @J01024, @l3ender and @Coderambling. Next we want to recognize our returning contributors @vaniisgh, @cdeil, @limx0m, and @TheoMaturin, and the finally the dedicated crew of core contributors which include @maximelt, @Hoxbro, @MarcSkovMadsen, @ahuang11, @mattpap and @philippjfr.

### Features

- Add `EditableTemplate` to support dashboard builder UI in Jupyter ([#5802](https://github.com/holoviz/panel/pull/5802))
- Add `ChatAreaInput` as default text input widget for `ChatInterface` ([#6379](https://github.com/holoviz/panel/pull/6379))
- Add `NestedSelect` widget ([#5791](https://github.com/holoviz/panel/pull/5791), [#6011](https://github.com/holoviz/panel/pull/6011))
- Add Panel tutorials ([#5525](https://github.com/holoviz/panel/pull/5525), [#6208](https://github.com/holoviz/panel/pull/6208), [#6212](https://github.com/holoviz/panel/pull/6212), [#6388](https://github.com/holoviz/panel/pull/6388), [#6425](https://github.com/holoviz/panel/pull/6425), [#6466](https://github.com/holoviz/panel/pull/6466), [#6491](https://github.com/holoviz/panel/pull/6491))
- Add `DateRangePicker` widget ([#6027](https://github.com/holoviz/panel/pull/6027))
- Add `Feed` layout and use it as layout for `ChatFeed` ([#6031](https://github.com/holoviz/panel/pull/6031), [#6296](https://github.com/holoviz/panel/pull/6296))
- Add `WebP` pane ([#6035](https://github.com/holoviz/panel/pull/6035))
- Add `ButtonIcon` ([#6138](https://github.com/holoviz/panel/pull/6138))
- Add `Textual` pane ([#6181](https://github.com/holoviz/panel/pull/6181))

### Enhancements

- Improve `--autoreload` by using watchfiles and selectively reloading packages ([#5894](https://github.com/holoviz/panel/pull/5894), [#6459](https://github.com/holoviz/panel/pull/6459))
 Load loading indicator from file instead of inlining ([#6112](https://github.com/holoviz/panel/pull/6112))
- Allow providing additional stylesheets in `card_params` ([#6242](https://github.com/holoviz/panel/pull/6242))
- Add `scroll` options to permanently toggle on layouts ([#6266](https://github.com/holoviz/panel/pull/6266))
- Allow choosing position of frozen columns on `Tabulator` ([#6309](https://github.com/holoviz/panel/pull/6309))
- Add help message on `ChatFeed` ([#6311](https://github.com/holoviz/panel/pull/6311))
- Ensure CSS can be applied to every aspect of `ChatMessage` ([#6346](https://github.com/holoviz/panel/pull/6346))
- Add HoloViz logos as `ChatMessage` avatars ([#6348](https://github.com/holoviz/panel/pull/6348))
- Add `gap` parameter to `FlexBox` ([#6354](https://github.com/holoviz/panel/pull/6354))
- Set default `step` of `DatetimeRangeSlider` to 1 minute ([#6373](https://github.com/holoviz/panel/pull/6373))
- Add support for passing objects reference to `FlexBox` ([#6387](https://github.com/holoviz/panel/pull/6387))
- Allow editable sliders to be embedded ([#6391](https://github.com/holoviz/panel/pull/6391))
- Add `message` into `css_classes` to `ChatMessage` markup ([#6407](https://github.com/holoviz/panel/pull/6407))
- Allow appending objects to the `ChatMessage` header & footer ([#6410](https://github.com/holoviz/panel/pull/6410))
- Add ability to declare icon label ([#6411](https://github.com/holoviz/panel/pull/6411))
- Add title and settings and fix datetime to `Perspective` ([#6482](https://github.com/holoviz/panel/pull/6482))
- Warn user if loading extension in VSCode or Colab without `jupyter_bokeh` ([#6485](https://github.com/holoviz/panel/pull/6485))
- Throttle updates to Boolean indicators ([#6481](https://github.com/holoviz/panel/pull/6481))
- Add `ParamRef` baseclass for `ParamFunction` and `ParamMethod` ([#6392](https://github.com/holoviz/panel/pull/6392))
- Add ability to Skip `Param<Ref|Function|Method>` updates ([#6396](https://github.com/holoviz/panel/pull/6396))
- Add `Param<Ref|Method|Function>` and `ReactiveExpr` to panes module ([#6432](https://github.com/holoviz/panel/pull/6432))
- Set up `param.rx` display accessor on import ([#6470](https://github.com/holoviz/panel/pull/6470))
- Allow using Carto tiles in `DeckGL` ([#6531](https://github.com/holoviz/panel/pull/6531))
- Improve `VTKJS` binary serialization ([#6559](https://github.com/holoviz/panel/pull/6559))
- Ensure component CSS is pre-loaded if possible, avoiding flicker on load ([#6563](https://github.com/holoviz/panel/pull/6563))

#### Styling

- Ensure navbar toggle icon is correct color in `BootstrapTemplate` ([#6111](https://github.com/holoviz/panel/pull/6111))
- Change `loading` background filters to work better in dark themes ([#6112](https://github.com/holoviz/panel/pull/6112))
- Improve styling of `FileInput` widget ([#6479](https://github.com/holoviz/panel/pull/6479))
- Improve Jupyter Preview error handling and error template ([#6496](https://github.com/holoviz/panel/pull/6496))
- Add scale animation to icons on hover and click ([#6376](https://github.com/holoviz/panel/pull/6376))
- Redesign index pages ([#6497](https://github.com/holoviz/panel/pull/6497))
- Improve `Tabulator` editor text color in `Fast` design ([#6512](https://github.com/holoviz/panel/pull/6512))
- Ensure `BootstrapTemplate` hamburger icon is white ([#6562](https://github.com/holoviz/panel/pull/6562))

### Compatibility & Version Updates

- Bump `Perspective` version to 2.9.0 ([#5722](https://github.com/holoviz/panel/pull/5722))
- Upgrade to Bokeh 3.4.x ([#6072](https://github.com/holoviz/panel/pull/6072))
- Upgrade `Vizzu` to 0.9.3 ([#6476](https://github.com/holoviz/panel/pull/6476))
- Bump `JSONEditor` version to 10.0.1 ([#6477](https://github.com/holoviz/panel/pull/6477))
- Upgrade to PyScript Next and Pyodide 0.25.0 in `panel convert` ([#6490](https://github.com/holoviz/panel/pull/6490))
- Bump vtk.js version to 30.1.0 ([#6559](https://github.com/holoviz/panel/pull/6559))

### Bug fixes

- Add resize handler for `FloatPanel` ([#6201](https://github.com/holoviz/panel/pull/6201))
- Fix serving of global template in notebook ([#6210](https://github.com/holoviz/panel/pull/6210))
- Ensure `Tabulator` renders in collapsed `Card` ([#6223](https://github.com/holoviz/panel/pull/6223))
- Fix issues with `VTK`, `VTKVolume` and `VTKJS` due to webgpu renderer ([#6244](https://github.com/holoviz/panel/issues/6244))
- Ensure `ChatInterface` respect supplied default user ([#6290](https://github.com/holoviz/panel/pull/6290))
- Ensure `HTML` and other markup panes can be emptied ([#6303](https://github.com/holoviz/panel/pull/6303))
- Ensure `ChatMessage` internals correctly respect `Design` ([#6304](https://github.com/holoviz/panel/pull/6304))
- Ensure collapsed `Card` does not cause stretching ([#6305](https://github.com/holoviz/panel/pull/6305))
- Ensure notebook preview always uses server resources ([#6317](https://github.com/holoviz/panel/pull/6317))
- Remove animation from loading spinner without spin ([#6324](https://github.com/holoviz/panel/pull/6324))
- Ensure model is only added/removed from Document once ([#6342](https://github.com/holoviz/panel/pull/6342))
- Ensure `loading_indicator` resets when configured with context manager ([#6343](https://github.com/holoviz/panel/pull/6343))
- Fix modal overflow and resizing issues ([#6355](https://github.com/holoviz/panel/pull/6355))
- Ensure that ripple matches notification size ([#6360](https://github.com/holoviz/panel/pull/6360))
- Fully re-render `CodeEditor` on render calls ensuring it displays correctly ([#6361](https://github.com/holoviz/panel/pull/6361))
- Ensure `FileDownload` button has correct height ([#6362](https://github.com/holoviz/panel/pull/6362))
- Ensure `HTML` model is redrawn if `stylesheets` is emptied ([#6365](https://github.com/holoviz/panel/pull/6365))
- Allow providing custom template ([#6383](https://github.com/holoviz/panel/pull/6383))
- Ensure `Debugger` renders without error ([#6423](https://github.com/holoviz/panel/pull/6423))
- Ensure `ChatMessage` `header` updates dynamically  ([#6441](https://github.com/holoviz/panel/pull/6441))
- Ensure pending writes are dispatched in order and only from correct thread ([#6443](https://github.com/holoviz/panel/pull/6443))
- Ensure layout reuses model if available ([#6446](https://github.com/holoviz/panel/pull/6446))
- Improved exception handler in unlocked message dispatch ([#6447](https://github.com/holoviz/panel/pull/6447))
- Fix display of interactive `Matplotlib` ([#6450](https://github.com/holoviz/panel/pull/6450))
- Ensure streaming `ChatMessage` on `ChatInterface` and mention `serialize` ([#6452](https://github.com/holoviz/panel/pull/6452))
- Ensure `Plotly` pane renders and hides correctly in `Card` ([#6468](https://github.com/holoviz/panel/pull/6468))
- Fix issues rendering widget components with `Fast` design ([#6474](https://github.com/holoviz/panel/pull/6474))
- Fix binary serialization from JS -> Pyodide ([#6490](https://github.com/holoviz/panel/pull/6490))
- Avoid overeager garbage collection ([#6518](https://github.com/holoviz/panel/pull/6518))
- Fix floating point error in `IntRangeSlider` ([#6516](https://github.com/holoviz/panel/pull/6516))
- Load JS modules from relative path ([#6526](https://github.com/holoviz/panel/pull/6526))
- Ensure no events are dispatched before the websocket is open ([#6528](https://github.com/holoviz/panel/pull/6528))
- Ensure `Markdown` parsing does not choke on partial links ([#6535](https://github.com/holoviz/panel/pull/6535))
- Fixes to ensure larger `PDF`s can be rendered ([#6538](https://github.com/holoviz/panel/pull/6538))
- Ensure `IPywidget` comms are only opened once ([#6542](https://github.com/holoviz/panel/pull/6542))
- Fixes for message handling in Jupyter Preview context ([#6547](https://github.com/holoviz/panel/pull/6547))
- Fix unnecessary loading of `ReactiveHTML` resources ([#6552](https://github.com/holoviz/panel/pull/6552))
- Ensure `Template.raw_css` has higher precedence than default template CSS ([#6554](https://github.com/holoviz/panel/pull/6554))
- Avoid asyncio event loop startup issues in some contexts ([#6555](https://github.com/holoviz/panel/pull/6555))
- Ensure column subset is retained on `Tabulator.style` ([#6560](https://github.com/holoviz/panel/pull/6560))
- Ensure bokeh mathjax bundle when mathjax extension is loaded in notebook ([#6564](https://github.com/holoviz/panel/pull/6564))

#### Chat Components

- Fix `ChatInterface` `stop` button for synchronous functions ([#6312](https://github.com/holoviz/panel/pull/6312))
- Include `stylesheets` downstream, including layouts in ChatMessage ([#6405](https://github.com/holoviz/panel/pull/6405))
- Ensure ChatInterface supports chat input without `value_input` parameter  ([#6505](https://github.com/holoviz/panel/pull/6505))
- Ensure word breaks to avoid overflow in `ChatMessage` ([#6187](https://github.com/holoviz/panel/pull/6187), [#6509](https://github.com/holoviz/panel/pull/6509))
- Ensure nested disabled state stays disabled on `ChatFeed` ([#6507](https://github.com/holoviz/panel/pull/6507))
- Allow streaming `None` as the initial `ChatMessage` value ([#6522](https://github.com/holoviz/panel/pull/6522))

### Documentation

- Add Roadmap to documentation ([#5443](https://github.com/holoviz/panel/pull/5443))
- Refactor `ReactiveHTML` docs ([#5448](https://github.com/holoviz/panel/pull/5448), [#6358](https://github.com/holoviz/panel/pull/6358))
- Improve `HoloViews` reference guide ([#6065](https://github.com/holoviz/panel/pull/6065))
- Improve the user experience for resetting Jupyterlite ([#6198](https://github.com/holoviz/panel/pull/6198))
- Add explanation docs about APIs ([#6289](https://github.com/holoviz/panel/pull/6289), [#6469](https://github.com/holoviz/panel/pull/6469))
- Add section headers to Chat reference documentation ([#6370](https://github.com/holoviz/panel/pull/6370))
- Migrate gallery to new Anaconda DSP instance ([#6413](https://github.com/holoviz/panel/pull/6413))
- Improve home page ([#6422](https://github.com/holoviz/panel/pull/6422))
- Adding AWS deployment to documentation ([#6434](https://github.com/holoviz/panel/pull/6434))
- Update Streamlit comparison ([#6467](https://github.com/holoviz/panel/pull/6467))
- Add logging how-to guide ([#6511](https://github.com/holoviz/panel/pull/6511))
- Document pygments dependency for code syntax highlighting ([#6519](https://github.com/holoviz/panel/pull/6519))
- Add how-to guide on configuring PyCharm ([#6525](https://github.com/holoviz/panel/pull/6525))

### Deprecations & Removals

- Remove `Ace` alias for `CodeEditor`
- Remove `ChatBox` which has been replaced by `panel.chat` components
- Remove `HTML.style` which is now replaced with `HTML.styles`
- Remove `Trend.title` which is now replaced by `Trend.name`
- Remove `Viewable.app` which is now replaced with `pn.io.notebook.show_server`
- Remove `Viewable.background` which is now replaced with `Viewable(styles={'background': ...})`
- Remove `Viewable.pprint` which is now replaced with `print(Viewable(...))`

## Version 1.3.8

Date: 2024-01-24

This patch release fixes an important regression in the 1.3.6 release that resulted in global state to be incorrectly resolved in certain cases. Many thanks to our new contributor @fohrloop and our maintainers @ahuang11

### Bug fixes

- Ensure `ReactiveHTML` correctly resets `Event` parameters ([#6247](https://github.com/holoviz/panel/pull/6247))
- Fix `ChatFeed` / `ChatInterface` tests and async generator placeholders ([#6245](https://github.com/holoviz/panel/pull/6245))
- Fix logic when looking up `pn.state.curdoc` ([#6254](https://github.com/holoviz/panel/pull/6254))
- Handle margin=None in layout sizing mode computation ([#6267](https://github.com/holoviz/panel/pull/6267))

### Compatibility

- Updates for compatibility with pandas 2.2 ([#6259](https://github.com/holoviz/panel/pull/6259))

### Documentation

- Fix typos and add a cross-reference in docs (User Profiling) ([#6263](https://github.com/holoviz/panel/pull/6263))
- Improve documentation on `TextAreaInput` ([#6264](https://github.com/holoviz/panel/pull/6264))

## Version 1.3.7

Date: 2024-01-19

This patch release focuses on a number of fixes and minor enhancements for the chat components and various other smaller improvements and fixes including docs improvements. In particular we want to highlight the new Ploomber deployment guide contributed by @neelash23. Next we want to welcome @jz314, @fayssalelmofatiche and @neelasha23 as new contributors and welcome back @SultanOrazbayev as a returning contributor. Lastly we want to thank the core contributor team, including @MarcSkovMadsen, @ahuang11, @maximlt, @Hoxbro and @philippjfr for their continued efforts maintaining Panel.

### Enhancements

- Add `filter_by` to `ChatMessage.serialize` ([#6090](https://github.com/holoviz/panel/pull/6090))
- Support using an SVG for `ToggleIcon` ([#6127](https://github.com/holoviz/panel/pull/6127))
- Add resizable param to `TextAreaInput` ([#6126](https://github.com/holoviz/panel/pull/6126))
- Improve date and datetime picker functionality ([#6152](https://github.com/holoviz/panel/pull/6152))
- Add activity indicator to `ChatMessage` ([#6153](https://github.com/holoviz/panel/pull/6153))
- Lazily import bleach HTML sanitizer ([#6179](https://github.com/holoviz/panel/pull/6179))

### Bug fixes

- Fix alignment issues in chat components ([#6104](https://github.com/holoviz/panel/pull/6104), [#6135](https://github.com/holoviz/panel/pull/6135))
- Fix generator placeholder and optimize updates in Chat components ([#6105](https://github.com/holoviz/panel/pull/6105))
- Fix issue with callback future handling on Chat components ([#6120](https://github.com/holoviz/panel/pull/6120))
- Fix bug in Chat interfaces related to `pn.state.browser_info` ([#6122](https://github.com/holoviz/panel/pull/6122))
- Allow instantiating empty `Matplotlib` pane ([#6128](https://github.com/holoviz/panel/pull/6128))
- Ensure icon displays inline with text on `FileDownload` ([#6133](https://github.com/holoviz/panel/pull/6133))
- Fix styling of links in `Tabulator` fast theme ([#6146](https://github.com/holoviz/panel/pull/6146))
- Fix passing of `card_params` on `ChatFeed` ([#6154](https://github.com/holoviz/panel/pull/6154))
- Handle `Tabulator.title_formatter` if is type `dict` ([#6166](https://github.com/holoviz/panel/pull/6166))
- Fix `per_session` caching ([#6169](https://github.com/holoviz/panel/pull/6169))
- Correctly reshape nd-arrays in `Plotly` pane ([#6174](https://github.com/holoviz/panel/pull/6174))
- Handle NaT values on `Perspective` pane ([#6176](https://github.com/holoviz/panel/pull/6176))
- Do not rerender output if `ReplacementPane` object identity is unchanged ([#6183](https://github.com/holoviz/panel/pull/6183))
- Tabulator: fix valuesLookup set up for older list-like editors ([#6192](https://github.com/holoviz/panel/pull/6192))
- Fix pyodide loading message styling issues ([#6194](https://github.com/holoviz/panel/pull/6194))
- More complete patch for the `TextEditor` to support being rendered in the Shadow DOM ([#6222](https://github.com/holoviz/panel/pull/6222))
- Add guard to `Tabulator` ensuring that it does not error when it is not rendered ([#6223](https://github.com/holoviz/panel/pull/6223))
- Fix race conditions when instantiating Comm in Jupyter causing notifications to break ([#6229](https://github.com/holoviz/panel/pull/6229), [#6234](https://github.com/holoviz/panel/pull/6234))
- Handle duplicate attempts at refreshing auth tokens ([#6233](https://github.com/holoviz/panel/pull/6233))

### Compatibility & Security

- Upgrade Plotly.js to 2.25.3 to address CVE-2023-46308 ([#6230](https://github.com/holoviz/panel/pull/6230))

### Documentation

- Add `Design` and `Theme` explanation documentation ([#4741](https://github.com/holoviz/panel/pull/4741))
- Fix pyodide execution in documentation
- Fix wrong and broken link ([#5988](https://github.com/holoviz/panel/pull/5988), [#6132](https://github.com/holoviz/panel/pull/6132))
- Use GoatCounter for website analytics ([#6117](https://github.com/holoviz/panel/pull/6117))
- Add Dask How to guide ([#4234](https://github.com/holoviz/panel/pull/4234))
- Fix `Material` template notebook .show() call ([#6137](https://github.com/holoviz/panel/pull/6137))
- Add missing item in docstring ([#6167](https://github.com/holoviz/panel/pull/6167))
- Ploomber Cloud deployment documentation ([#6182](https://github.com/holoviz/panel/pull/6182))
- Correct duplicate wording ([#6188](https://github.com/holoviz/panel/pull/6188))
- Update JupyterLite Altair example to latest API ([#6226](https://github.com/holoviz/panel/pull/6226))

## Version 1.3.6

Date: 2023-12-20

This patch release addresses a major regression in server performance introduced in 1.3.5 along with some additional minor fixes. We want to welcome @nenb as a new contributor and want to thank the maintainers @ahuang11, @maximlt and @philippjfr for their contributions to this release.

### Enhancements

- Add explicit size option to ToggleIcon ([#6092](https://github.com/holoviz/panel/pull/6092))

### Bug fixes

- Fix execution of OAuth of callback to refresh `access_token` ([#6084](https://github.com/holoviz/panel/pull/6084))
- Fix `ChatReactionIcons` alignment and trigger reactions correctly ([#6086](https://github.com/holoviz/panel/pull/6086))
- Change `Column` `scroll_position` default value from `None` to `0` ([#6082](https://github.com/holoviz/panel/pull/6082))
- Fix issue with accumulating callbacks on server ([#6091](https://github.com/holoviz/panel/pull/6091))
- Ensure `ReactiveExpr` renders in pyodide ([#6097](https://github.com/holoviz/panel/pull/6097))
- Ensure `TooltipIcon` description can be updated ([#6099](https://github.com/holoviz/panel/pull/6099))
- Fix IPyWidgets rendering in `BootstrapTemplate` ([#6100](https://github.com/holoviz/panel/pull/6100))
- Fix padding and alignment of `FileDownload` ([#6101](https://github.com/holoviz/panel/pull/6101))

## Version 1.3.5

Date: 2023-12-18

This micro-release fixes a large number of issues, applies some performance optimizations and resolves some regressions introduced in previous micro-releases. The main regressions that were addressed include rendering of `ChatMessage` reaction icons, the ability to obtain an OAuth `access_token` if it is not a valid JWT token, and issues with async callbacks. We are very pleased to welcome new contributors @mitulb, @fazledyn-or, @benbarn313 and @vaniisgh and want to thank them for their contributions. We also want to thank @cdeil for continuing to contribute and the maintainer team including @MarcSkovMadsen, @Hoxbro, @maximlt, @ahuang11, @droumis and @philippjfr for their continued efforts.

### Enhancements

- Add support for timestamp timezones for `ChatMessage` ([#5961](https://github.com/holoviz/panel/pull/5961))
- Replace whitelist blacklist with allowlist denylist ([#5975](https://github.com/holoviz/panel/pull/5975))
- Allow stopping respond callbacks midway on `ChatInterface` ([#5962](https://github.com/holoviz/panel/pull/5962))
- Add support for `Image.caption` ([#6003](https://github.com/holoviz/panel/pull/6003))
- Improvements for `Fast` template styling ([#6023](https://github.com/holoviz/panel/pull/6023))
- Replace `Player` widget unicode icons with SVG for more consistency ([#6030](https://github.com/holoviz/panel/pull/6030))
- Elaborate on `ChatInterface` callback exception summary ([#6046](https://github.com/holoviz/panel/pull/6046))
- Add `ToggleIcon` widget ([#6034](https://github.com/holoviz/panel/pull/6034))
- Use minified `Tabulator.js` ([#6060](https://github.com/holoviz/panel/pull/6060))
- Support rendering `GeoDataFrame` and `GeoSeries` in `DataFrame` pane ([#6061](https://github.com/holoviz/panel/pull/6061))
- Optimize rendering of `ChatMessage` ([#6069](https://github.com/holoviz/panel/pull/6069))
- Apply smaller  optimizations for `Viewable` and `ChatMessage` ([#6074](https://github.com/holoviz/panel/pull/6074))
- Add bottom padding to `MaterialTemplate` ([#6075](https://github.com/holoviz/panel/pull/6075))
- Update mapbox-gl version for `DeckGL` pane ([#6077](https://github.com/holoviz/panel/pull/6077))

### Bug fixes

- Remove duplicate property definition of `VizzuChart.config` ([#5947](https://github.com/holoviz/panel/pull/5947))
- Remove stray print in `Tabulator` styler handling ([#5944](https://github.com/holoviz/panel/pull/5944))
- Fix bug when clearing `pn.cache` before anything has been cached ([#5981](https://github.com/holoviz/panel/pull/5981))
- Fix `obj.save()` when threading is enabled ([#5993](https://github.com/holoviz/panel/pull/5993))
- Fix `Matplotlib` responsiveness and improve reference notebook ([#5973](https://github.com/holoviz/panel/pull/5973))
- Gracefully handle non-decodable `access_token` ([#5994](https://github.com/holoviz/panel/pull/5994))
- Ensure `onload` callbacks scheduled during or after load are still executed ([#6005](https://github.com/holoviz/panel/pull/6005))
- Don't attempt to set Tabulator `text_align` on Bokeh formatters that don't support it ([#6010](https://github.com/holoviz/panel/pull/6010))
- Correctly set error page to be rendered on auth failure ([#6014](https://github.com/holoviz/panel/pull/6014))
- Fix `ChatInterface` post callback for default ([#5998](https://github.com/holoviz/panel/pull/5998))
- Ensure matplotlib backend is set correctly in pyodide worker ([#6029](https://github.com/holoviz/panel/pull/6029))
- Synchronously create Document patch message to avoid race conditions ([#6028](https://github.com/holoviz/panel/pull/6028))
- Do not inline CSS if it can be loaded from CDN ([#6039](https://github.com/holoviz/panel/pull/6039))
- Fix `ChatMessage` reactions icon rendering ([#6034](https://github.com/holoviz/panel/pull/6034))
- Fix issues with `ChatInterface` stop ensuring send button is re-enabled and placeholder removed ([#6033](https://github.com/holoviz/panel/pull/6033))
- Ensure that `Design` does not override properties on `HoloViews` pane ([#6051](https://github.com/holoviz/panel/pull/6051))
- Ensure async callbacks correctly dispatch events when Websocket is locked ([#6052](https://github.com/holoviz/panel/pull/6052))
- Fix `state.add_periodic_callback` when callback is async ([#6053](https://github.com/holoviz/panel/pull/6053))
- Do no update objects inplace unless explicitly requested fixing issues with non-updating components ([#6055](https://github.com/holoviz/panel/pull/6055))
- Update sizing of Panel models dynamically ([#6054](https://github.com/holoviz/panel/pull/6054))
- Make `panel.chat.langchain` import lazy improving import time ([#6056](https://github.com/holoviz/panel/pull/6056))
- Change prominence of `TooltipIcon` ([#6057](https://github.com/holoviz/panel/pull/6057))

### Documentation

- Improve reactive expression notebook ([#5960](https://github.com/holoviz/panel/pull/5960))
- Document requirement to install `pyviz_comms` in same env as Jupyter ([#5980](https://github.com/holoviz/panel/pull/5980))
- Update documentation's pyodide version to use version from panel.io.convert ([#5996](https://github.com/holoviz/panel/pull/5996))

## Version 1.3.4

Date: 2023-11-29

This micro-release primarily addresses two important regressions related to the Tabulator `text_align` option and OAuth failing if the `id_token` does not contain the required user information. We are very excited to welcome @TBym to the growing list of contributors and thank the core maintainers @Hoxbro, @ahuang11, @MarcSkovMadsen and @philippjfr for their contributions to this release.

### Enhancements

- Allow passing partial function to tabulator filter ([#5912](https://github.com/holoviz/panel/pull/5912))
- Allow defining custom callbacks for `ChatInterface` buttons ([#5839](https://github.com/holoviz/panel/pull/5839))

### Bug fixes

- Fix regression when setting `text_align` and `HTMLTemplateFormatter` on `Tabulator` ([#5922](https://github.com/holoviz/panel/pull/5922))
- Ensure notifications are correctly destroyed ([#5924](https://github.com/holoviz/panel/pull/5924))
- Fix header overflow issues in `FastGridTemplate` ([#5935](https://github.com/holoviz/panel/pull/5935))
- Ensure `Audio` model respects sizing ([#5936](https://github.com/holoviz/panel/pull/5936))
- Persist Tabulator selection across pages when `pagination='remote'` for all selection modes ([#5929](https://github.com/holoviz/panel/pull/5929))
- Ensure `Tabulator` styler subset logic is not lost ([#5938](https://github.com/holoviz/panel/pull/5938))
- Fix regression in OAuth when `id_token` does not contain user key ([#5939](https://github.com/holoviz/panel/pull/5939))
- Ensure Vega/Altair plot with responsive width/height respects fixed width/height value when set ([#5940](https://github.com/holoviz/panel/pull/5940))
- Ensure `BrowserInfo` is imported by default ([#5942](https://github.com/holoviz/panel/pull/5942))

### Documentation

- Restore plot styling guides in how-to guide ([#5919](https://github.com/holoviz/panel/pull/5919))
- Document support for emojis on Button labels ([#5926](https://github.com/holoviz/panel/pull/5926))
- Update and improve `SVG` pane reference docs ([#5934](https://github.com/holoviz/panel/pull/5934))

## Version 1.3.2

Date: 2023-11-22

This micro-release focuses on a number of performance improvements, speeding up the initial rendering of simple apps by 2x in many cases. In addition it includes a number of smaller enhancements for various widgets, better support for async and threading and a number of bug fixes related to authentication, the `Tabulator` widget and a few other items. We are very pleased to welcome @isumitjha and @fohria as new contributors and want to thank our core team including @maximlt, @Hoxbro, @MarcSkovMadsen, @ahuang11 and @philippjfr for their continuing contributions.

### Performance

- Speed up `Pane.clone` ([#5848](https://github.com/holoviz/panel/pull/5848))
- Speed up `config` attribute access ([#5851](https://github.com/holoviz/panel/pull/5851))
- Cache templates loaded from string ([#5854](https://github.com/holoviz/panel/pull/5854))
- Only load extension entrypoints once ([#5855](https://github.com/holoviz/panel/pull/5855))
- Do not freeze document models unless needed ([#5864](https://github.com/holoviz/panel/pull/5864))

### Enhancements

- Use the compiled version of Pyodide by default ([#5808](https://github.com/holoviz/panel/pull/5808))
- Add support for `AutocompleteInput.search_strategy` parameter ([#5832](https://github.com/holoviz/panel/pull/5832))
- Use `stdlib_module_names` when determining pyodide dependencies  ([#5818](https://github.com/holoviz/panel/pull/5818))
- Add `Tabulator.sortable` parameter ([#5827](https://github.com/holoviz/panel/pull/5827))
- Add delay for tooltip to show up for buttons ([#5860](https://github.com/holoviz/panel/pull/5860))
- Add `serialize` method on `ChatMessage` and `ChatFeed` ([#5764](https://github.com/holoviz/panel/pull/5764))
- Allow running onload and defer_load tasks on threads ([#5865](https://github.com/holoviz/panel/pull/5865))
- Allow Image panes for `ChatMessage.avatar` ([#5870](https://github.com/holoviz/panel/pull/5870))
- Allow async callbacks on `FileDownload` ([#5878](https://github.com/holoviz/panel/pull/5878))
- Allow running scheduled tasks on threads ([#5879](https://github.com/holoviz/panel/pull/5879))

### Bug fixes

- Fix Google OAuth default scopes ([#5823](https://github.com/holoviz/panel/pull/5823))
- Fix logic for cleaning up OAuth user ([#5824](https://github.com/holoviz/panel/pull/5824))
- Set `text_align` correctly if `Tabulator` is given Bokeh `formatter` ([#5866](https://github.com/holoviz/panel/pull/5866))
- Fix `FileDownload` `embed=True` style for `Fast` design ([#5875](https://github.com/holoviz/panel/pull/5875))
- Enable `Tabulator` selection across pages with `pagination="remote"` and `selectable="checkbox"` ([#5889](https://github.com/holoviz/panel/pull/5889))
- Fix rendering of `VTK` colorbar ([#5902](https://github.com/holoviz/panel/pull/5902))
- Ensure HoloViews `DynamicMap` updates when widget dimension has unit ([#5904](https://github.com/holoviz/panel/pull/5904))
- Add space between `MaterialTemplate` app and site title separator ([#5905](https://github.com/holoviz/panel/pull/5905))
- Consistently handle errors during authentication ([#5909](https://github.com/holoviz/panel/pull/5909))

### Compatibility

- Updates for Numpy 2.0 compatibility ([#5817](https://github.com/holoviz/panel/pull/5817))
- Improve notebook handling when loading bokeh dev versions ([#5820](https://github.com/holoviz/panel/pull/5820))
- Support for rendering into DOM from PyScript Next worker ([#5820](https://github.com/holoviz/panel/pull/5911))

### Documentation

- Enhance `extension` and `config` docs ([#5790](https://github.com/holoviz/panel/pull/5790))
- Document setting a *multiselect* header filter on `Tabulator` ([#5825](https://github.com/holoviz/panel/pull/5825))
- Add missing `GridSpec` docs ([#5840](https://github.com/holoviz/panel/pull/5840))
- Fix for getting_started widgets example ([#5859](https://github.com/holoviz/panel/pull/5859))
- Add more references to Panel Chat Examples ([#5881](https://github.com/holoviz/panel/pull/5881))
- Document `Tabulator` fontawesome css ([#5892](https://github.com/holoviz/panel/pull/5892))
- Fix broken link to panel tagged items in holoviz blog ([#5903](https://github.com/holoviz/panel/pull/5903))
- MenuButton docs improvements ([#5907](https://github.com/holoviz/panel/pull/5907))

## Version 1.3.1

Date: 2023-10-31

This micro-release primarily ships a variety of bug and regression fixes focusing on auth, the chat components, and WASM (i.e. PyScript and Pyodide) support. It also adds an enhancement to the auth components that now makes it possible to let users access applications as a guest. Many thanks to
our new contributors @art3xa, @polivbr and @tupui as well as our core development team including @MarcSkovMadsen, @maximlt, @ahuang11 and @philippjfr.

### Enhancements

- Add support for authenticating as guest using OAuth and basic auth components ([#5743](https://github.com/holoviz/panel/pull/5743))

### Bug fixes

- Ensure `ColorMap` widget correctly handles shared layout and display parameters ([#5732](https://github.com/holoviz/panel/pull/5732))
- Fix accessing refreshed `access_token` ([#5734](https://github.com/holoviz/panel/pull/5734))
- Ensure `Markdown` code blocks always wrap ([#5738](https://github.com/holoviz/panel/pull/5738))
- Fix returning `state.user_info` if no `id_token` is present in cookies ([#5747](https://github.com/holoviz/panel/pull/5747))
- Fix `Widget.from_param` type annotation ([#5754](https://github.com/holoviz/panel/pull/5754))
- Fix auto send for `ChatInterface` with `TextAreaInput` ([#5762](https://github.com/holoviz/panel/pull/5762))
- Add support for iframe `srcdoc` on `Location` ([#5774](https://github.com/holoviz/panel/pull/5774))
- Ensure `Tabulator.style` applies correctly with changing data ([#5757](https://github.com/holoviz/panel/pull/5757))
- Ensure `panel convert` can correctly detect `transformers_js` import ([#5772](https://github.com/holoviz/panel/pull/5772))
- Adjust `ReactiveHTML` css resources for relative paths ([#5779](https://github.com/holoviz/panel/pull/5779))
- Ensure invalid query parameters warn instead of erroring ([#5781](https://github.com/holoviz/panel/pull/5781))
- Apply pyscript CSS by default without the splashscreen ([#5784](https://github.com/holoviz/panel/pull/5784))
- Ensure components which require DOM element to be attached can be rendered in `Card` ([#5786](https://github.com/holoviz/panel/pull/5786))

### Documentation

- Fix typo in examples/reference/widgets/StaticText.ipynb ([#5739](https://github.com/holoviz/panel/pull/5739))
- Add `ReactiveExpr` reference docs and change default widget location ([#5755](https://github.com/holoviz/panel/pull/5755), [#5760](https://github.com/holoviz/panel/pull/5760))
- Fix pyscript WASM example ([#5771](https://github.com/holoviz/panel/pull/5771))
- Improve documentation for deep linking docs ([#5752](https://github.com/holoviz/panel/pull/5752))

## Version 1.3.0

Date: 2023-10-23

This minor release packs many exciting new features, specifically a new `panel.chat` subpackage containing components with powerful capabilities for interacting with LLM whether local or remote. Secondly this release adds compatibility with Param 2.0 bringing powerful new features including the ability to leverage reactive expressions using the `rx` wrapper and deeper support for reactively linking parameters, expressions and bound functions on Panel components. Lastly we overhauled the OAuth implementations adding support for code authorization and password based OAuth grant workflows and automatically refreshing the `access_token` when it expires. Beyond that this release includes many enhancements and numerous bug fixes. Special thanks to our first time contributors @aktech and @monodera and returning contributors @cdeil, @pierrotsmnrd and @TheoMartin. We also want to highlight the contribution of our new core contributor @ahuang11 for developing the chat components and recognize @MarcSkovMadsen and @philippjfr for their efforts on testing and improving these new components. Finally we thank the entire core team @Hoxbro, @MarcSkovMadsen, @maximlt, @ahuang11 and @philippjfr for their continued efforts.

### Feature

- Integrate support for param reactive expressions and expose `pn.rx` ([#5138](https://github.com/holoviz/panel/pull/5138), [#5582](https://github.com/holoviz/panel/pull/5582))
- Implement `ChatMessage`, `ChatFeed` and `ChatInterface` components ([#5333](https://github.com/holoviz/panel/pull/5333))
- Unify OAuth implementations and refresh `access_token` ([#5627](https://github.com/holoviz/panel/pull/5627))
- Add `ColorMap` widget ([#5647](https://github.com/holoviz/panel/pull/5647))

### Enhancement

- Add unit to widget in `HoloViews` pane if provided ([#5535](https://github.com/holoviz/panel/pull/5535))
- Allow registering global `on_session_destroyed` callback ([#5585](https://github.com/holoviz/panel/pull/5585))
- Implement `auto_grow` on `TextAreaInput` ([#5592](https://github.com/holoviz/panel/pull/5592))
- Add ability to redirect users from authorization callback ([#5594](https://github.com/holoviz/panel/pull/5594))
- Add support for `Path` object in `FileDownload` ([#5607](https://github.com/holoviz/panel/pull/5607))
- Add authorization_code and password based OAuth login handlers ([#5547](https://github.com/holoviz/panel/pull/5547))
- Add format to `EditableFloatSlider` and `EditableIntSlider` ([#5631](https://github.com/holoviz/panel/pull/5631))
- Add support for decorating async functions with `pn.io.cache` ([#5649](https://github.com/holoviz/panel/pull/5649))
- Map `param.Bytes` to `FileInput` widget ([#5665](https://github.com/holoviz/panel/pull/5665))

### Bug fixes

- Fixes for `Column` invisible `scroll_button` taking space ([#5532](https://github.com/holoviz/panel/pull/5532))
- Guard undefined values from being set on `BrowserInfo` ([#5588](https://github.com/holoviz/panel/pull/5588))
- Fix thumbnails and use Panel design on index page ([#5595](https://github.com/holoviz/panel/pull/5595))
- Fix regressions in `TextEditor` caused by migration to shadow DOM ([#5609](https://github.com/holoviz/panel/pull/5609))
- Sync `location` state from request ([#5581](https://github.com/holoviz/panel/pull/5581))
- Fix `Select` widget label offset in Material Design ([#5639](https://github.com/holoviz/panel/pull/5639))
- Override token contents when reusing sessions ([#5640](https://github.com/holoviz/panel/pull/5640))
- Fix patching a table with a `DataFrame` with a custom index ([#5645](https://github.com/holoviz/panel/pull/5645))
- Set `FloatPanel` status correctly on initialization ([#5651](https://github.com/holoviz/panel/pull/5651))
- Fix patching table with `pd.Timestamp` values ([#5650](https://github.com/holoviz/panel/pull/5650))
- Ensure `notifications` and `browser_info` are loaded when `HoloViews` is loaded ([#5657](https://github.com/holoviz/panel/pull/5657))
- Gracefully handle resolution of invalid paths in `_stylesheets` ([#5666](https://github.com/holoviz/panel/pull/5666))
- Handle patching tables with `NaT` values ([#5675](https://github.com/holoviz/panel/pull/5675))

### Compatibility

- Add support for Python 3.12 and drop Python 3.8 support
- Upgrade to Param 2.0 as minimum required version
- Compatibility with Bokeh 3.3.0

### Documentation

- Improved docs on deploying with GCP ([#5531](https://github.com/holoviz/panel/pull/5531))
- Add Streamlit migration guide for chat components ([#5670](https://github.com/holoviz/panel/pull/5670))

## Version 1.2.3

Date: 2023-09-18

This micro-release primarily fixes some critical regressions that were introduced in the 1.2.2 release, along with some other minor bug fixes. Many thanks for our users for reporting these issues so quickly and @monodera, @ndmlny-qs, @ahuang11, @mattpap, @Hoxbro and @philippjfr for their contributions to the release.

### Enhancements

- Add ability to change admin page endpoint ([#5447](https://github.com/holoviz/panel/pull/5447))
- Authentication `/logout` endpoint now serves configurable template ([#5514](https://github.com/holoviz/panel/pull/5514))
- Add options to sanitize `HTML` panes ([#5516](https://github.com/holoviz/panel/pull/5516))

### Bug fixes

- Fix regression introduced in 1.2.2 causing issues with periodic callbacks and `--autoreload` ([#5490](https://github.com/holoviz/panel/pull/5490))
- Fix regression introduced in 1.2.2 causing issues with authorization callbacks ([#5504](https://github.com/holoviz/panel/pull/5504))
- Fix regression introduced in 1.2.2 related to logout redirects ([#5484](https://github.com/holoviz/panel/pull/5484))
- Fix extracting `panel convert` requirements from requirements.txt ([#5509](https://github.com/holoviz/panel/pull/5509))
- Ensure visibility is applied correctly for all components when initialized as False ([#5508](https://github.com/holoviz/panel/pull/5508))
- Fix rendering of backticks in `ReactiveHTML` ([#5512](https://github.com/holoviz/panel/pull/5512))
- Ensure Quill `TextEditor` correctly detects selections and renders HTML ([#5511](https://github.com/holoviz/panel/pull/5511))
- Fix `Markdown` rendering with the MyST parser ([#5497](https://github.com/holoviz/panel/pull/5497))
- Fix OAuth login endpoint when `--prefix` is set ([#5492](https://github.com/holoviz/panel/issues/5492))

### Documentation

- Update outdated `DateRangeSlider.step` documentation ([#5510](https://github.com/holoviz/panel/pull/5510))

## Version 1.2.2

Date: 2023-08-31

This micro-release is likely the last in the 1.2.x series with a large number of bug fixes and a few enhancements to existing components. The enhancements include the ability to control the scroll position on a `Column`, improvements for authentication and authorization, the ability to add click event handlers to `Perspective` and a few other items. In terms of bug fixes this release also includes fixes for authentication, some improvements when rendering `Tabulator` avoiding various race conditions in its rendering pipeline, and fixes for `Perspective`, `Echarts`, `DeckGL` and a few other components. We are very grateful for a large number of community contributions to this release and welcome and congratulate new contributors @s22chan, @RaulPL, @dogbunny, @thomasjpfan, @SultanOrazbayev and @pierrotsmnrd. Many thanks also to returning contributors @TBym, @Lnk2past, @ndmlny-qs, @owenlamont and our core developer team @MarcSkovMadsen, @ahuang11, @Hoxbro, @maximlt, and @philippjfr.

### Enhancements

- Add scroll button, auto-scroll and scroll position options to `Column` ([#5245](https://github.com/holoviz/panel/pull/5245), [#5365](https://github.com/holoviz/panel/pull/5365), [#5369](https://github.com/holoviz/panel/pull/5369), [#5403](https://github.com/holoviz/panel/pull/5403))
- Add cache busting to server CSS resources ([#5414](https://github.com/holoviz/panel/pull/5414))
- Add `Tabulator.title_formatters` parameter ([#5421](https://github.com/holoviz/panel/pull/5421))
- Provide the the accessed path to authorization checks ([#5386](https://github.com/holoviz/panel/pull/5386))
- Add `Perspective` click events ([#5430](https://github.com/holoviz/panel/pull/5430))
- Add and improve `pn.io.hold` and `pn.io.immediate_dispatch` context managers to control events ([#5444](https://github.com/holoviz/panel/pull/5444))
- Allow to passing `basic_login_template` argument to panel server ([#5454](https://github.com/holoviz/panel/pull/5454))

### Bug fixes

- Ensure `BasicAuth` forwards to original URL after login ([#5357](https://github.com/holoviz/panel/pull/5357))
- Correct return types from `threading.Thread` to `panel.io.server.StoppableThread` ([#5396](https://github.com/holoviz/panel/pull/5396))
- Various guards and fixes ensuring `Tabulator` re-renders correctly ([#5410](https://github.com/holoviz/panel/pull/5410), [#5412](https://github.com/holoviz/panel/pull/5412))
- Avoid extra executions when executing periodic callback with counter ([#5344](https://github.com/holoviz/panel/pull/5344))
- Ensure updates to `DataModel` are correctly scheduled on the event loop ([#5360](https://github.com/holoviz/panel/pull/5360))
- Fixes for displaying single newlines in `Markdown` output and add `renderer_options` ([#5376](https://github.com/holoviz/panel/pull/5376))
- Allow update of `Accordion` title without updating content ([#5413](https://github.com/holoviz/panel/pull/5413))
- Fix authentication handling when prefix is set ([#5422](https://github.com/holoviz/panel/pull/5422))
- Fix serialization issues affecting `TextLayer` objects in `DeckGL` ([#5427](https://github.com/holoviz/panel/pull/5427))
- Fix height responsiveness of `Perspective` pane ([#5429](https://github.com/holoviz/panel/pull/5429))
- Ensure `FileDownload` button can be clicked anywhere ([#5431](https://github.com/holoviz/panel/pull/5431))
- Ensure `ReactiveHTML` children are rendered just like other models ([#5434](https://github.com/holoviz/panel/pull/5434))
- Set `Perspective` properties correctly to avoid causing unfocus on keypresses ([#5432](https://github.com/holoviz/panel/pull/5432))
- Ensure `FloatPanel` correctly exposes its children to allow linking ([#5433](https://github.com/holoviz/panel/pull/5433))
- Do no reset `Tabulator` options if DataFrame indexes are unchanged ([#5436](https://github.com/holoviz/panel/pull/5436))
- Add ability to work around issues when removing series from `ECharts` ([#5435](https://github.com/holoviz/panel/pull/5435))
- Fix race conditions when initializing and rendering IPyWidgets in notebooks ([#5462](https://github.com/holoviz/panel/pull/5462))
- Tweak `Accordion` CSS to remove gaps and avoid border overlap ([#5460](https://github.com/holoviz/panel/pull/5460))
- Ensure columns are deleted when updating traces on `Plotly` pane to avoid corruption ([#5464](https://github.com/holoviz/panel/pull/5464))
- Invalidate layout when `TextEditor` CSS loads ([#5465](https://github.com/holoviz/panel/pull/5465))
- Ensure `FloatPanel` reflects closed status ([#5466](https://github.com/holoviz/panel/pull/5466))
- Fix handling of string dtypes on `Perspective` pane ([#5467](https://github.com/holoviz/panel/pull/5467))

### Documentation

- Fix incorrectly linked images in streamlit migration guide and VSCode guide ([#5327](https://github.com/holoviz/panel/pull/5327), [#5329](https://github.com/holoviz/panel/pull/5329))
- Improve developer instructions ([#5305](https://github.com/holoviz/panel/pull/5305), [#5380](https://github.com/holoviz/panel/pull/5380), [#5426](https://github.com/holoviz/panel/pull/5426))

### Compatibility

- Compatibility with param 2.0 watchers ([#5350](https://github.com/holoviz/panel/pull/5350), [#5455](https://github.com/holoviz/panel/pull/5455))

## Version 1.2.1

Date: 2023-07-25

This micro-release focuses on a small number of enhancements and rendering related bug fixes. Specifically it adds support for notifying users when the page is ready and when the Websocket disconnects using corresponding config options and upgrades the Vizzu version, thereby adding support for tooltips and enabling animations when the data is updated. The bug fixes are primarily focused on ensuring components such as `GridStack` and `Tabulator` render correctly and do not unnecessarily re-render or reload stylesheets. Many thanks and welcome to @owenlamont, @sciemon, @DGLaurits, @Ciemarr and @Kislovskiy for their first contributions to Panel and the maintainers @MarcSkovMadsen, @Hoxbro and @philippjfr for contributing to this release.

### Enhancements

- Add `config.disconnect_notification` and `config.ready_notification` ([#5244](https://github.com/holoviz/panel/pull/5244))
- Add `Vizzu` tooltip support and allow animations when data is updated ([#5258](https://github.com/holoviz/panel/pull/5258))
- Style tweaks for `Card` and `Select` components ([#5280](https://github.com/holoviz/panel/pull/5280))

### Bug fixes

- Ensure `GridStack` children are sized correctly after render ([#5242](https://github.com/holoviz/panel/pull/5242))
- Fix `Tabulator` expanded row rendering ([#5253](https://github.com/holoviz/panel/pull/5253))
- Fix bug where local `PDF` pane is rendered as base64 string ([#5264](https://github.com/holoviz/panel/issues/5264))
- Avoid full re-rendering when updating `HTML` based components ([#5275](https://github.com/holoviz/panel/pull/5275))
- Ensure that `Design` does not trigger unnecessary updates to stylesheets ([#5278](https://github.com/holoviz/panel/pull/5278))
- Treat `Tabulator` `row_contents` as real children ensuring layout behaves correctly ([#5292](https://github.com/holoviz/panel/pull/5292))
- Fix `Video` `min_height` and `max_height` ([#5296](https://github.com/holoviz/panel/pull/5296))
- Make `TextEditor` invisible until CSS is loaded ([#5297](https://github.com/holoviz/panel/pull/5297))
- Fix `disabled` parameter on editable sliders ([#5319]((https://github.com/holoviz/panel/pull/5319))

### Compatibility

- Update pyodide and pyscript versions and switch to compiled build ([#5309](https://github.com/holoviz/panel/pull/5309))

### Documentation

- Add VS Code How To Guide ([#5196](https://github.com/holoviz/panel/pull/5196))
- Fix binder ([#5257](https://github.com/holoviz/panel/pull/5257))
- Various smaller documentation fixes ([#4821], [#5249](https://github.com/holoviz/panel/pull/5249), [#5266](https://github.com/holoviz/panel/pull/5266))
- Tweak example in the Build an App section of Getting Started ([#5302](https://github.com/holoviz/panel/pull/5302))
- Update pyodide documentation with latest versions ([#5234](https://github.com/holoviz/panel/pull/5234), [#5308](https://github.com/holoviz/panel/pull/5308))
- Remove MyST inline directives from JupyterLite notebooks ([#5311](https://github.com/holoviz/panel/pull/5311))

## Version 1.2.0

Date: 2023-07-06

This release primarily aims at providing compatibility with Bokeh 3.2 and the upcoming Param 2.0 release. Additionally it includes a number of improvements including the ability to generate multiple outputs from a generator using the new `'append'` mode and updates and fixes for Tabulator. We are also excited about the new Streamlit migration guide and a number of bug fixes. Many thanks to @sdc50, @xiaoyang-sde and the core team including @ahuang11, @MarcSkovMadsen, @Hoxbro, @maximlt and @philippjfr for contributing to this release.

### Enhancements

- Add `append` mode for reactive generator output ([#5129](https://github.com/holoviz/panel/pull/5129))
- Upgrade to `Tabulator` 5.5 ([#5182](https://github.com/holoviz/panel/pull/5182))
- Add support for `LoadingSpinner` label ([#5194](https://github.com/holoviz/panel/pull/5194))
- Add the `editable` parameter to `Perspective` ([#5211](https://github.com/holoviz/panel/pull/5211))
- Add support for setting `theme_classes` on `Tabulator` ([#5216](https://github.com/holoviz/panel/pull/5216))
- Move resource handling onto `BaseTemplate` ([#5228](https://github.com/holoviz/panel/pull/5228))

### Bug fixes

- Correctly process fields on `Vega` (and altair) selections ([#5164](https://github.com/holoviz/panel/pull/5164))
- Fix for resource handling particularly when working with Django ([#5175](https://github.com/holoviz/panel/pull/5175))
- Fix `ChatBox` bubble width ([#5172](https://github.com/holoviz/panel/pull/5172))
- Fix `Tabulator.visible` handling ([#5182](https://github.com/holoviz/panel/pull/5182))
- Fix programmatic updates to `Tabulator.page` ([#5187](https://github.com/holoviz/panel/pull/5187))
- Ensure bokeh events generated in pyodide convert `None` to `null` ([#5191](https://github.com/holoviz/panel/pull/5191))
- Improve notebook detection ([#5201](https://github.com/holoviz/panel/pull/5201))
- Reduce priority of `_repr_<img>_` to ensure `_repr_html_` takes precedence ([#5217](https://github.com/holoviz/panel/pull/5217))
- Ensure we do not modify `Tabulator.hidden_columns` inplace ([#5218](https://github.com/holoviz/panel/pull/5218))
- Alignment and styling fixes for text input and button widgets ([#5219](https://github.com/holoviz/panel/pull/5219))
- Fix updates to `Plotly` nested properties such as selections ([#5227](https://github.com/holoviz/panel/pull/5227))

### Documentation

- Add Streamlit migration guide ([#5027](https://github.com/holoviz/panel/pull/5027))
- Improve `defer_load` how-to guide ([#5112](https://github.com/holoviz/panel/pull/5112))

### Compatibility

- Remove markdown-it-py pins ([#5159](https://github.com/holoviz/panel/pull/5159))
- Forward compatibility fixes for Param 2.0 ([#5169](https://github.com/holoviz/panel/pull/5169), [#5198](https://github.com/holoviz/panel/pull/5198))
- Compatibility with Bokeh 3.2 ([#5185](https://github.com/holoviz/panel/pull/5185))

## Version 1.1.1

Date: 2023-06-21

The first micro-release in the 1.1.x series brings a large number of bug fixes and some minor enhancements. The most important fixes include compatibility with JupyterLab 4 and improved support for updating ipywidgets. This release saw a lot of contributors and we welcome @TBym, @Glatzli, @theyashi, and @enismaxim1 to the Panel developer community and thank our existing contributors and maintainers @ahuang11, @Hoxbro, @sophiamyang, @maximlt, @MarcSkovMadsen, and @philippjfr for their continued contributions.

### Enhancements

- Implement `per_session` cache ([#5117](https://github.com/holoviz/panel/pull/5117))
- Enhancements for `ChatBox` including methods to update rows and hide names ([#5118](https://github.com/holoviz/panel/pull/5118), [#5118](https://github.com/holoviz/panel/pull/5152))

### Bug fixes

- Fix `Progress` indicator `sizing_mode` ([#5051](https://github.com/holoviz/panel/pull/5051))
- Fix various `ChatBox` issues ([#5065](https://github.com/holoviz/panel/pull/5065), [#5101](https://github.com/holoviz/panel/pull/5101), [#5101](https://github.com/holoviz/panel/pull/5139))
- Ensure kernel shutdown futures are not collected in Jupyter server extension ([#5069](https://github.com/holoviz/panel/pull/5069))
- Add bokeh version check for notebook to better support bokeh dev versions ([#5071](https://github.com/holoviz/panel/pull/5071), [#5093](https://github.com/holoviz/panel/pull/5093))
- Fix false warning emitted when constructing a Param pane with `throttled` or `onkeyup` ([#5078](https://github.com/holoviz/panel/pull/5078))
- Allow to updating/clearing `enabled_dates` on `DatetimePicker` ([#5089](https://github.com/holoviz/panel/pull/5089))
- Ensure session arguments are correctly parsed by Jupyter executor ([#5106](https://github.com/holoviz/panel/pull/5106))
- Fix `defer_load` handling ([#5107](https://github.com/holoviz/panel/pull/5107))
- Fix styling with filters in `Tabulator` ([#5110](https://github.com/holoviz/panel/pull/5110))
- Fix issues when using `in` filter with single value on Tabulator ([#5125](https://github.com/holoviz/panel/pull/5125))
- Add fallback if `ReactiveHTML` shadow DOM lookup fails ([#5126](https://github.com/holoviz/panel/pull/5126))
- Allow automatic loading of extensions during launch and warn about missing extensions ([#5144](https://github.com/holoviz/panel/pull/5144))
- Correctly process fields on `Vega` (and altair) selections ([#5145](https://github.com/holoviz/panel/pull/5145))
- Immediately dispatch `ColumnDataChangedEvent` fixing `Plotly` plots not updating ([#5147](https://github.com/holoviz/panel/pull/5147))

### Documentation

- Overhaul Perspective reference page ([#5087](https://github.com/holoviz/panel/pull/5087))
- Add new HuggingFace deployment documentation ([#5158](https://github.com/holoviz/panel/pull/5150))
- Enable and document mathjax extension in Markdown reference ([#5158](https://github.com/holoviz/panel/pull/5158))

### Compatibility

- Correctly serialize new IPyWidget models on creation ([#5114](https://github.com/holoviz/panel/pull/5114))
- Ensure we handle JupyterLab 4 comm messages correctly ([#5140](https://github.com/holoviz/panel/pull/5140))

### Backward compatibility

- Renamed Trend parameter title to name ([#5092](https://github.com/holoviz/panel/pull/5092))

## Version 1.1.0

Date: 2023-05-31

This is the first minor release in the 1.x series with a number of new features and small bug fixes. The main features we are excited about are the new `ChatBox` widget added by @ahuang11 and support for reactive generators. Many thanks to @ahuang11, @philippjfr and @Hoxbro for contributing to this release and our amazing community for reporting issues.

### Features

- Add the `ChatBox` widget ([#4702](https://github.com/holoviz/panel/issues/4702))
- Add a standalone `TooltipIcon` indicator ([#4909](https://github.com/holoviz/panel/pull/4909))
- Implement support for reactive generator functions ([#5019](https://github.com/holoviz/panel/issues/5019))
- Allow setting `on_*` handlers in constructor ([#5026](https://github.com/holoviz/panel/issues/5026))
- Allow controlling initial `Template` sidebar state ([#5033](https://github.com/holoviz/panel/issues/5033))

### Bug fixes

- Handle height responsiveness of `HoloViews` layout correctly ([#5009](https://github.com/holoviz/panel/issues/5009))
- Apply `Plotly` toolbar colors depending on template ([#5012](https://github.com/holoviz/panel/issues/5012))
- Fix Fast `Design` style variables ([#5015](https://github.com/holoviz/panel/issues/5015))
- Allow reactive updates to override constant parameters ([#5032](https://github.com/holoviz/panel/issues/5032))
- Fix `Tabulator` header filter styling ([#5038](https://github.com/holoviz/panel/issues/5038))
- Ensure Jupyter extensions warns users if app has no contents ([#5041](https://github.com/holoviz/panel/issues/5041))

## Version 1.0.4

Date: 2023-05-31

Another micro-release in the 1.0.x series addressing small issues reported by our engaged community. Many thanks to @ahuang11, @simzer, @alexmilowski and the core contributors @droumis, @Hoxbro and @philippjfr for contributing to this release.

- Fix global loading spinner ([#4936](https://github.com/holoviz/panel/issues/4936))
- Fix issues resolving whether `IPyWidget` model ([#4939](https://github.com/holoviz/panel/issues/4939))
- Fix recursive and inplace updates on reactive panes ([#4946](https://github.com/holoviz/panel/issues/4946), [#4958](https://github.com/holoviz/panel/issues/4958))
- Fix issues with single `Select` widget ([#4947](https://github.com/holoviz/panel/issues/4947))
- Ensure CSS `config` parameters can be passed to `Template` constructor ([#4948](https://github.com/holoviz/panel/issues/4948))
- Fixed vizzu data series type conversion for datetime ([#4955](https://github.com/holoviz/panel/issues/4955))
- Small documentation fixes ([#4943](https://github.com/holoviz/panel/issues/4960), [#4960](https://github.com/holoviz/panel/issues/4943))
- Fix `icon` on `Toggle` and `Button` widget ([#4961](https://github.com/holoviz/panel/issues/4961))
- Fix Volume definition on `Video` pane ([#4970](https://github.com/holoviz/panel/issues/4970))
- Ensure `Card.header_color` is correctly applied ([#4971](https://github.com/holoviz/panel/issues/4971))
- Update `param.List` signatures to suppress warnings ([#4973](https://github.com/holoviz/panel/pull/4973))
- Fix font loading in Vanilla template ([#4975](https://github.com/holoviz/panel/pull/4975))
 ([#4975](https://github.com/holoviz/panel/pull/4975))
- Guard is_file check on Windows ([#4985](https://github.com/holoviz/panel/pull/4985))
- Fix serialization of `Plotly.selection_data` ([#4987](https://github.com/holoviz/panel/pull/4987))
- Speed up dynamic layout updates ([#4989](https://github.com/holoviz/panel/pull/4989))

## Version 1.0.3

Date: 2023-05-25

Another micro-release in the 1.0.x series with a number of smaller bug fixes. Most importantly this resolves issues with loading indicators and with apps converted to the `pyodide-worker` target. Many thanks to @n3011, @Hoxbro and @philippjfr for contributing to this release.

- Resolve `_repr_jpeg_` methods correctly ([#4904](https://github.com/holoviz/panel/pull/4904))
- Fix handling of queued events in pyodide worker ([#4913](https://github.com/holoviz/panel/pull/4913))
- Various fixes for loading indicator ([#4915](https://github.com/holoviz/panel/pull/4915))
- Allow `-1` in `Tabs.active` and allow recovering from closed tabs ([#4920](https://github.com/holoviz/panel/pull/4920))
- Ensure `HoloViews` layout is correctly initialized when `center` is set ([#4921](https://github.com/holoviz/panel/pull/4921))
- Ensure VSCode editor does not apply white background to Panel output ([#4923](https://github.com/holoviz/panel/pull/4923))
- Do not error on deserialization errors in notebooks ([#4927](https://github.com/holoviz/panel/pull/4927))
- Ensure basic auth provider works when dynamically starting server ([#4926](https://github.com/holoviz/panel/pull/4926))
- Ensure `Param` pane `name` is updated when object changes ([#4928](https://github.com/holoviz/panel/pull/4928))
- Align functionality and styling of `FileDownload` with `Button` ([#4929](https://github.com/holoviz/panel/pull/4929))
- Fix equality comparisons of parameter values when updating a `Pane` ([#4934](https://github.com/holoviz/panel/pull/4934))
- Warn about ignored widget parameters on `Param` pane ([#4934](https://github.com/holoviz/panel/pull/4935))

## Version 1.0.2

Date: 2023-05-19

A micro-release in the 1.0.2 series with a number of bug fixes and documentation tweaks. Many thanks to @jbednar and @philippjfr for contributing to this release.

### Bug fixes

- Ensure `Design` stylesheets are not replaced when updating component stylesheets ([#4883](https://github.com/holoviz/panel/pull/4883))
- Ensure tooltips are rendered correctly as HTML ([#4887](https://github.com/holoviz/panel/pull/4887))
- Fix loading of index page resources ([#4891](https://github.com/holoviz/panel/pull/4891))
- Ensure `FloatPanel` can be rendered in classic notebooks ([#4892](https://github.com/holoviz/panel/pull/4892))
- Attempt rendering output in notebooks even if not all resources have been initialized ([#4893](https://github.com/holoviz/panel/pull/4893))
- Do not load large bokeh-mathjax bundle in notebooks by default ([#4895](https://github.com/holoviz/panel/pull/4895))
- Make Fast template sidebar opening transition smoother ([#4898](https://github.com/holoviz/panel/pull/4898))
- Ensure new items added to `Card` layout are rendered ([#4899](https://github.com/holoviz/panel/pull/4899))
- Fix logo rendering in BasicAuth template ([#4900](https://github.com/holoviz/panel/pull/4900))

### Documentation

- Various documentation tweaks ([#4884](https://github.com/holoviz/panel/pull/4884), [#4888](https://github.com/holoviz/panel/pull/4888), [#4889](https://github.com/holoviz/panel/pull/4889))
- Update Vega/Altair reference notebook to use altair 5 APIs ([#4894](https://github.com/holoviz/panel/pull/4894))

## Version 1.0.1

Date: 2023-05-18

A micro-release fixing some small issues discovered in Panel 1.0. Thank you to @droumis, @Hoxbro and @philippjfr for contributing fixes.

### Bug fixes

- Ensure `Reactive` objects wrapped in reactive are re-rendered correctly ([#4868](https://github.com/holoviz/panel/pull/4868))
- Tweaks for Material `Design` component inset label styling ([#4877](https://github.com/holoviz/panel/pull/4877))
- Ensure `SlidesTemplate` slides changes trigger updates in the `pn.state.location.hash` ([#4878](https://github.com/holoviz/panel/pull/4878))

### Documentation

- Fixes for cross-referencing and links in documentation ([#4870](https://github.com/holoviz/panel/pull/4870), [#4872](https://github.com/holoviz/panel/pull/4872), [#4874](https://github.com/holoviz/panel/pull/4874), [#4875](https://github.com/holoviz/panel/pull/4875))

## Version 1.0.0

Date: 2023-05-17

The Panel 1.0 release is finally here and it brings a huge number of improvements. The largest improvements in this release come from an upgrade from Bokeh 2.x to Bokeh 3.x. Bokeh overhauled its internal layout engine and stylesheet handling, making applications significantly more performant and customizable going forward.

This release marks a huge step forward in the usability of Panel but is also just a first step in leveraging many of the new capabilities that the updated layout engine and design system affords. In the coming months we will continue to improve and polish the UI and UX and make it easier for you to extend Panel as needed.

For now we want to thank the many people that contributed to this release either by contributing directly or by testing and providing feedback. Many thanks to the core contributors @MarcSkovMadsen, @Hoxbro, @maximlt, @jbednar, @droumis and @philippjfr and the outside contributors @ahuang11, @cdeil, @MridulS, @AndrewMaged814, @midnighter and @wendrul.

### Major Features

The three main features we want to highlight as part of this release are:

- Add new and highly performant layout engine, addressing many performance and layout issues ([#4326](https://github.com/holoviz/panel/pull/4326), [#4463](https://github.com/holoviz/panel/pull/4463), [#4491](https://github.com/holoviz/panel/pull/4491), [#4503](https://github.com/holoviz/panel/pull/4503), [#4522](https://github.com/holoviz/panel/pull/4522), [#4690](https://github.com/holoviz/panel/pull/4690))
- Add unified Design and Theme system ([#4413](https://github.com/holoviz/panel/pull/4413), [#4475](https://github.com/holoviz/panel/pull/4475), [#4466](https://github.com/holoviz/panel/pull/4466), [#4540](https://github.com/holoviz/panel/pull/4540), [#4548](https://github.com/holoviz/panel/pull/4548), [#4770](https://github.com/holoviz/panel/pull/4770), [#4792](https://github.com/holoviz/panel/pull/4792), [#4793](https://github.com/holoviz/panel/pull/4793), [#4801](https://github.com/holoviz/panel/pull/4801))
- Implement support for passing parameters, widgets and bound functions by reference for simple and powerful reactivity ([#4495](https://github.com/holoviz/panel/pull/4495), [#4505](https://github.com/holoviz/panel/pull/4505), [#4603](https://github.com/holoviz/panel/pull/4603), [#4606](https://github.com/holoviz/panel/pull/4606))

Some of the changes related to the new layout engine and design system will require small updates to your existing applications. To make this transition as smooth as possible we have provided an [upgrade/migration guide](https://panel.holoviz.org/panel/upgrade.html).

### New Components

This release also adds a number of exciting new components you can leverage in your applications:

- Add `Swipe` layout ([#3007](https://github.com/holoviz/panel/pull/3007))
- Add `Switch` widget ([#4130](https://github.com/holoviz/panel/pull/4130))
- Add `Vizzu` pane ([#4226](https://github.com/holoviz/panel/pull/4226), [#4739](https://github.com/holoviz/panel/pull/4739))
- Add `BrowserInfo` model to expose browser window and navigator APIs ([#4533](https://github.com/holoviz/panel/pull/4533))
- Add `BasicAuth` provider for quick password based auth ([#4684](https://github.com/holoviz/panel/pull/4684))
- Add `FloatPanel` layout ([#4707](https://github.com/holoviz/panel/pull/4707), [#4711](https://github.com/holoviz/panel/pull/4711))
- Add a `SlidesTemplate` based on reveal.js to create interactive presentations ([#4798](https://github.com/holoviz/panel/pull/4798))

### Major enhancements

There are also a number of major enghancements in this release that we are very excited about:

- Improved Markdown rendering ([#4688](https://github.com/holoviz/panel/pull/4688))
- Add support for tooltips on widgets ([#4130](https://github.com/holoviz/panel/pull/4130), [#4621](https://github.com/holoviz/panel/pull/4621), [#4643](https://github.com/holoviz/panel/pull/4643))
- Ensure `.ipynb` and `.md` based apps can be used as `--index` ([#4432](https://github.com/holoviz/panel/pull/4432))
- Add support for selecting `format` and `encoding` for Matplotlib image output and implemented  responsive Image sizing ([#4514](https://github.com/holoviz/panel/pull/4514))
- Add support for icons on `Button` ([#4797](https://github.com/holoviz/panel/pull/4797))
- Add generic `Image` pane that auto-detects the image filetype ([#4551](https://github.com/holoviz/panel/pull/4551))
- Add support for writing applications in Markdown ([#4602](https://github.com/holoviz/panel/pull/4602))
- Improve support for inline resources for Jupyter ([#3013](https://github.com/holoviz/panel/pull/3013), [#4787](https://github.com/holoviz/panel/pull/4787))
- Add ability to reuse sessions to speed up rendering ([#3679](https://github.com/holoviz/panel/pull/3679), [#4658](https://github.com/holoviz/panel/pull/4658))
- Improve notebook resource and extension loading ([#4752](https://github.com/holoviz/panel/pull/4752))
- Add ability to add global loading spinner to application(s) ([#4659](https://github.com/holoviz/panel/pull/4659))

### Documentation

The last major change we want to highlight is a complete overhaul of the documentation, moving from long and difficult-to-navigate user guides to distinct easily applied how-to guides along with separate, longer explanation sections. We also put in significant effort to ensure that most of our documentation can be run interactively in Pyodide or JupyterLite.

- Modernize documentation by using latest pydata-sphinx-theme ([#4609](https://github.com/holoviz/panel/pull/4609), [#4701](https://github.com/holoviz/panel/pull/4701))
- Add upgrade/migration guide ([#4693](https://github.com/holoviz/panel/pull/4693))
- Add Explanation section ([#2797](https://github.com/holoviz/panel/pull/2797), [#3168](https://github.com/holoviz/panel/pull/3168), [#4664](https://github.com/holoviz/panel/pull/4664))
- Migrate user guide to how-to guides ([#4244](https://github.com/holoviz/panel/pull/4244), [#4251](https://github.com/holoviz/panel/pull/4251), [#4267](https://github.com/holoviz/panel/pull/4267), [#4290](https://github.com/holoviz/panel/pull/4290), [#4412](https://github.com/holoviz/panel/pull/4412), [#4422](https://github.com/holoviz/panel/pull/4422), [#4759](https://github.com/holoviz/panel/pull/4759), [#4774](https://github.com/holoviz/panel/pull/4774))
- Completely overhaul App Gallery ([#4047](https://github.com/holoviz/panel/pull/4047), [#4565](https://github.com/holoviz/panel/pull/4565), [#4574](https://github.com/holoviz/panel/pull/4574), [#4598](https://github.com/holoviz/panel/pull/4598), [#4683](https://github.com/holoviz/panel/pull/4683))
- Use pyodide rendering throughout documentation and add JupyterLite links ([#4751](https://github.com/holoviz/panel/pull/4751))

### Deprecations & API changes

#### Compatibility

- Bokeh 3 compatibility ([#4098](https://github.com/holoviz/panel/pull/4098), [#4117](https://github.com/holoviz/panel/pull/4117), [#4129](https://github.com/holoviz/panel/pull/4129), [#4140](https://github.com/holoviz/panel/pull/4140), [#4150](https://github.com/holoviz/panel/pull/4150), [#4275](https://github.com/holoviz/panel/pull/4275), [#4467](https://github.com/holoviz/panel/pull/4467), [#4435](https://github.com/holoviz/panel/pull/4435), [#4441](https://github.com/holoviz/panel/pull/4441), [#4449](https://github.com/holoviz/panel/pull/4449), [#4448](https://github.com/holoviz/panel/pull/4448), [#4508](https://github.com/holoviz/panel/pull/4508))
- Upgrade plotly.js to 2.18.0 ([#4320](https://github.com/holoviz/panel/pull/4320))
- Upgrade Tabulator to 5.4 and optimize rendering ([#4482](https://github.com/holoviz/panel/pull/4482))
- Upgrade Echarts to 5.4.1 ([#4538](https://github.com/holoviz/panel/pull/4538))
- Upgrade pyodide (0.23.1) and pyscript versions ([#4344](https://github.com/holoviz/panel/pull/4344))
- Add support for altair and vega-lite v5 ([#4488](https://github.com/holoviz/panel/pull/4488))
- Add support for latest versions of ipywidgets ([#4716](https://github.com/holoviz/panel/pull/4716), [#4766](https://github.com/holoviz/panel/pull/4766), [#4779](https://github.com/holoviz/panel/pull/4779))

#### Deprecations

- Deprecate `IDOM` pane ([#4293](https://github.com/holoviz/panel/pull/4293), [#4323](https://github.com/holoviz/panel/pull/4323))
- Deprecate `Viewable.app` ([#4293](https://github.com/holoviz/panel/pull/4293))
- Deprecate `Viewable.pprint` ([#4347](https://github.com/holoviz/panel/pull/4347))
- Deprecate and remove `RGGPlot`
- Rename `Ace` to `CodeEditor` ([#4627](https://github.com/holoviz/panel/pull/4627))

#### API changes & Backward Compatibility

- Pandas is now only a (lazy) runtime dependency ([#4411](https://github.com/holoviz/panel/pull/4411))
- `Tabulator.frozen_rows` now respects the order of rows in the data instead of the order in which the `frozen_rows` were defined ([#4482](https://github.com/holoviz/panel/pull/4482))
- Make `margin` defaults consistent across widgets and panes ([#4528](https://github.com/holoviz/panel/pull/4528))
- Extension calls must specify all required extensions ([#4562](https://github.com/holoviz/panel/pull/4562))
- The `.embed` method now returns a Mimebundle object for rendering ([#4791](https://github.com/holoviz/panel/pull/4791))
- Remove `panel examples` CLI command and pyct dependency ([#4691](https://github.com/holoviz/panel/pull/4691))
- Expose all layout components in top-level API ([#4696](https://github.com/holoviz/panel/pull/4696))

### Other Enhancements

#### Configuration

- Allow to set the log level of the Admin logger ([#3495](https://github.com/holoviz/panel/pull/3495))
- Add `pn.state.served` to simplify determining whether script is executed as an application or in an interactive session ([#4252](https://github.com/holoviz/panel/pull/4252))
- Add `pn.config.loading_indicator` to determine whether to show loading indicator by default ([#4259](https://github.com/holoviz/panel/pull/4259))

#### Jupyter

- Improve startup, error handling and shutdown of Jupyter kernels ([#4364](https://github.com/holoviz/panel/pull/4364))
- Log errors in JupyterLab preview to server logs ([#4773](https://github.com/holoviz/panel/pull/4773))
- Support binary JS -> Python communication in notebooks ([#4635](https://github.com/holoviz/panel/pull/4635))
- Modify sys.path when running inside Jupyter Kernel ([#4489](https://github.com/holoviz/panel/pull/4489))

#### Pyodide

- IPython `display` compatibility in pyodide builds ([#4270](https://github.com/holoviz/panel/pull/4270))
- Ensure `panel convert` respects `pn.config` ([#4359](https://github.com/holoviz/panel/pull/4359))
- Fix notification support in Pyodide ([#4387](https://github.com/holoviz/panel/pull/4387))

#### Miscelleanous

- Handle cancelling and empty value edit events on `Tabulator` ([#4343](https://github.com/holoviz/panel/pull/4343))
- Add favicon to base template ([#4626](https://github.com/holoviz/panel/pull/4626))
- Ensure `CrossSelector` filters apply on each keystroke ([#4339](https://github.com/holoviz/panel/pull/4339))
- Do not re-create `Vega.selections` object unless selections changed ([#4497](https://github.com/holoviz/panel/pull/4497))
- Standardize parameter mapping APIs ([#4386](https://github.com/holoviz/panel/pull/4386))
- Add `Plotly.link_figure` parameter ([#4333](https://github.com/holoviz/panel/pull/4333))
- Add support for .JPEG file extension in the `JPG` pane ([#4532](https://github.com/holoviz/panel/pull/4532))
- Make periodic callback `counter` a parameter ([#4134](https://github.com/holoviz/panel/pull/4134))
- Add Echarts events ([#2174](https://github.com/holoviz/panel/pull/2174))
- Additional cache support ([#4663](https://github.com/holoviz/panel/pull/4663), [#4667](https://github.com/holoviz/panel/pull/4667))

### Bug fixes

- Fix caching on undecorated Parameterized method ([#4332](https://github.com/holoviz/panel/pull/4332))
- Ensure that global notification object can be used inside notebook callbacks ([#4331](https://github.com/holoviz/panel/pull/4331))
- Ensure `hash_funcs` are applied recursively in cache ([#4334](https://github.com/holoviz/panel/pull/4334))
- Fix cache `FIFO` policy bug ([#4789](https://github.com/holoviz/panel/pull/4789))
- Fix specifying custom index with relative path ([#4288](https://github.com/holoviz/panel/pull/4288))
- Fix issue reusing `FileDownload` model ([#4328](https://github.com/holoviz/panel/pull/4328))
- Fix `DeckGL` tooltip handling ([#4628](https://github.com/holoviz/panel/pull/4628))
- Fix NumPy integer/floating checks on `Perspective` ([#4366](https://github.com/holoviz/panel/pull/4366))
- Ensure `memray` profiler temporary file is flushed ([#4666](https://github.com/holoviz/panel/pull/4666))
- Fix mimetype issue on windows ([#4738](https://github.com/holoviz/panel/pull/4738))
- Fix `Plotly` undefined value errors for eventdata ([#4355](https://github.com/holoviz/panel/pull/4355))

#### Tabulator

- Ensure updates to `Tabulator` formatter or editor updates model ([#4296](https://github.com/holoviz/panel/pull/4296), [#4781](https://github.com/holoviz/panel/pull/4781))
- Ensure `Tabulator` internal `_index_mapping` is updated on stream ([#4292](https://github.com/holoviz/panel/pull/4292))
- Ensure `Tabulator` header filters aren't treated as regex ([#4423](https://github.com/holoviz/panel/pull/4423))
- Ensure `Tabulator` `styles` are re-applied when local pagination changes ([#4795](https://github.com/holoviz/panel/pull/4795))

#### Jupyter

- Ensure JupyterLab preview works on Windows ([#4819](https://github.com/holoviz/panel/pull/4819))
- Ensure notifications are enabled even if hv.extension has been loaded ([#4330](https://github.com/holoviz/panel/pull/4330))

## Version 0.14.4

Date: 2023-03-04

This release is a small bug fix release preceding the upcoming major release of Panel 1.0. Many thanks to the contributors to this release which include @MarcSkovMadsen, @maximlt, @Hoxbro and @philippjfr.

### Bugs

- Fix `Tabulator` client-side string filters by not parsing them as regex ([4423](https://github.com/holoviz/panel/pull/4423))
- Fix the RGGPlot pane ([#4380](https://github.com/holoviz/panel/pull/4380))
- Fix `panel examples` command by ensuring examples are correctly packaged ([#4484](https://github.com/holoviz/panel/pull/4484))
- Fix event generation by considering NaNs as equal when comparing Numpy arrays ([#4481](https://github.com/holoviz/panel/pull/4481))
- Use cache from previous sessions when using `to_disk` ([#4481](https://github.com/holoviz/panel/pull/4481))
- Fix relative imports when running inside Jupyter Kernel ([#4489](https://github.com/holoviz/panel/pull/4489))
- Do not re-create `Vega.selections` object unless selections changed ([#4497](https://github.com/holoviz/panel/pull/4497))

### Enhancements

- Add support for altair and vega-lite v5 ([#4488](https://github.com/holoviz/panel/pull/4488))

### Misc

- Use latest react-grid from CDN ([#4461](https://github.com/holoviz/panel/pull/4461))

## Version 0.14.3

Date: 2023-01-28

This release introduces a large number of bug fixes and minor enhancements. Due to the upcoming release of Panel 1.0 we have also made the unconventional decision to issue new deprecation in a micro release. Specifically the `IDOM` pane and `Viewable.app` and `Viewable.pprint` methods have been scheduled for deprecation. Many thanks to the contributors to this release which include @wendrul, @droumis and the core team @MarcSkovMadsen, @maximlt, @Hoxbro and @philippjfr.

### Bugs

#### Tabulator

- Ensure streamed rows on `Tabulator` can be edited ([#4292](https://github.com/holoviz/panel/pull/4292))
- Ensure changes on `Tabulator` `formatter` and `editor` models are reflected in frontend ([#4296](https://github.com/holoviz/panel/pull/4296))
- Ensure cancelling edit does not clear cell on `Tabulator` ([#4343](https://github.com/holoviz/panel/pull/4343))
- Ensure inserting empty data on numeric column in `Tabulator` does not error ([#4343](https://github.com/holoviz/panel/pull/4343))

#### Notebook

- Fix issues rendering components as ipywidgets for some versions of ipykernel ([#4289](https://github.com/holoviz/panel/pull/4289))
- Add warning if custom resources could not be loaded in notebook ([#4329](https://github.com/holoviz/panel/pull/4329))
- Ensure notifications are enabled even if `hv.extension` has been loaded ([#4330](https://github.com/holoviz/panel/pull/4330))
- Ensure global notification object can be used inside notebook callbacks ([#4331](https://github.com/holoviz/panel/pull/4331))

#### Type definitions

- Fix return type of `Widget.from_param` ([#4335](https://github.com/holoviz/panel/pull/4335))
- Ensure type annotation allows `str` and `PathLike` objects on `panel.serve` ([#4336](https://github.com/holoviz/panel/pull/4336))
- Fix type annotations on `panel.io.convert.convert_app`(s) ([#4342](https://github.com/holoviz/panel/pull/4342))

#### Misc

- Ensure markdown links render correctly in template sidebar ([#4222](https://github.com/holoviz/panel/pull/4222))
- Improve .applies for `ECharts` and `DeckGL` ([#4224](https://github.com/holoviz/panel/pull/4224))
- Fix specifying custom `--index` with relative path ([#4288](https://github.com/holoviz/panel/pull/4288))
- Skip `on_load` callbacks in liveness check ([#4302](https://github.com/holoviz/panel/pull/4302))
- Ensure re-rendered `FileDownload` still fetches live data ([#4328](https://github.com/holoviz/panel/pull/4328))
- Fix handling of `panel.cache` on undecorated `Parameterized` method ([#4332](https://github.com/holoviz/panel/pull/4332))
- Ensure user provided `hash_funcs` are applied in `panel.cache` ([#4334](https://github.com/holoviz/panel/pull/4334))
- Fix plotly eventdata undefined val ([#4355](https://github.com/holoviz/panel/pull/4355))
- Ensure `panel convert` respects `panel.config` options ([#4359](https://github.com/holoviz/panel/pull/4359))
- Propagate options from HoloViews and Bokeh plots to enclosing Pane ([#4360](https://github.com/holoviz/panel/pull/4360))
- Propagate options from dynamic components such as ParamMethod and Interactive to enclosing layout ([#4360](https://github.com/holoviz/panel/pull/4360))

### Minor enhancements

- Allow to set the log level of the Admin logger ([#3495](https://github.com/holoviz/panel/pull/3495))
- Make `refresh_token` available in Auth ([#4227](https://github.com/holoviz/panel/pull/4227))
- Simplify determining whether script is executed as application with `pn.state.served` property ([#4252](https://github.com/holoviz/panel/pull/4252))
- Add `loading_indicator` to global `config` ([#4259](https://github.com/holoviz/panel/pull/4259))
- IPython `display` compatibility in pyodide builds ([#4270](https://github.com/holoviz/panel/pull/4270))
- Split `PanelJupyterExecutor` into separate module ([#4276](https://github.com/holoviz/panel/pull/4276))
- Allow dynamic loading of javascript modules in `ReactiveHTML` ([#4319](https://github.com/holoviz/panel/pull/4319))
- Add `Plotly.link_figure` parameter ([#4333](https://github.com/holoviz/panel/pull/4333))
- Ensure `CrossSelector` filters apply on each keystroke ([#4339](https://github.com/holoviz/panel/pull/4339))
- Improve startup, error handling and shutdown of Jupyter kernels in `jupyter_server_extension` ([#4364](https://github.com/holoviz/panel/pull/4364))

### Compatibility and Version Updates

- Upgrade plotly.js to 2.10.1 ([#4320](https://github.com/holoviz/panel/pull/4320))
- Upgrade to pyodide 0.22.1 in `panel convert` ([#4334](https://github.com/holoviz/panel/pull/4334))
- Upgrade to pyscript 2022.12.01 in `panel convert` ([#4334](https://github.com/holoviz/panel/pull/4334))
- Fix compatibility of Perspective pane with Numpy 1.24 ([#4362](https://github.com/holoviz/panel/issues/4362))

### Deprecations

- Add deprecation warning to `IDOM` pane ([#4293](https://github.com/holoviz/panel/pull/4293))
- Add deprecation warning for `Viewable.app` and `Viewable.pprint` methods ([#4293](https://github.com/holoviz/panel/pull/4293), [#4347](https://github.com/holoviz/panel/pull/4347))

### Documentation

- Add CONTRIBUTING.md ([#4262](https://github.com/holoviz/panel/pull/4262))
- Add Gallery VideoStream example ([#4047](https://github.com/holoviz/panel/pull/4047))
- Add description of literal options to the docs for `ReactiveHTML` ([#3803](https://github.com/holoviz/panel/pull/3803))

## Version 0.14.2

Date: 2022-12-14

This release primarily focuses on bug fixes. In particular it resolves various issues with support for rendering `ipywidgets` (particularly in `ipywidgets>=8.0`) and also fixes a number of issues with the Jupyter Server previews. Many thanks for @govinda18, @joelostblom, @banesullivan, @xeldnahcram, @geronimogoemon, @minasouliman, @peterfpeterson, @jlstevens and the core maintainers @maximlt, @Hoxbro, @MarcSkovMadsen and @philippjfr for their contributions to this release.

### Enhancements

- Add support for `Tqdm.process_map` ([#4093](https://github.com/holoviz/panel/pull/4093))
- Support non-vtkPolyData types in vtk synchronizer ([#4124](https://github.com/holoviz/panel/pull/4124))
- Allow invoking `convert` functions from pyodide ([#4135](https://github.com/holoviz/panel/pull/4135))
- Support `step` format in date sliders ([#4152](https://github.com/holoviz/panel/pull/4152))
- Add a `Reacton` component to simplify rendering ([#4190](https://github.com/holoviz/panel/pull/4190))

### Bugs

- Ensure Jupyter server extension serves resources, extensions and paths correctly ([#4083](https://github.com/holoviz/panel/pull/4083), [#4133](https://github.com/holoviz/panel/pull/4133), [#4202](https://github.com/holoviz/panel/pull/4202))
- Ensure `IPyWidget` comm does not break when new widget is rendered ([#4091](https://github.com/holoviz/panel/pull/4091))
- Improving detection of comms in VSCode and Google Colab ([#4115](https://github.com/holoviz/panel/pull/4115))
- Ensure `.js` mimetype is served correctly on Windows ([#4118](https://github.com/holoviz/panel/pull/4118))
- Ensure unhiding `Tabulator` columns renders cells correctly ([#4119](https://github.com/holoviz/panel/pull/4119))
- Ensure embedded `Slider` widgets initialize with correct default ([#4121](https://github.com/holoviz/panel/pull/4121))
- Handle missing event loop in thread gracefully ([#4123](https://github.com/holoviz/panel/pull/4123))
- Ensure `Matplotlib` pane handles explicit `width`/`height` settings correctly ([#4128](https://github.com/holoviz/panel/pull/4128))
- Allow `Viewer` to render servable but non-viewable objects ([#4131](https://github.com/holoviz/panel/pull/4131))
- Fix regression in tracking sessions in admin interface ([#4132](https://github.com/holoviz/panel/pull/4132))
- Ensure `Tabs` headers do not scroll unnecessarily ([#4146](https://github.com/holoviz/panel/pull/4146))
- Ensure `Location` model reports as idle ([#4159](https://github.com/holoviz/panel/pull/4159))
- Fix auth error template rendering ([#4162](https://github.com/holoviz/panel/pull/4162))
- Fix issues with value on `EditableSlider` when it is outside `fixed_start` / `fixed_end` range ([#4169](https://github.com/holoviz/panel/pull/4169))
- Ensure `ipywidgets` events are handled the same way as regular events ([#4171](https://github.com/holoviz/panel/pull/4171))
- Don't raise `TypeError` for class which contains `__panel__` ([#4174](https://github.com/holoviz/panel/pull/4174))
- Do not dispatch events if bokeh `Document` is set to hold events ([#4178](https://github.com/holoviz/panel/pull/4178))
- Execute `onload` callbacks immediately in pyodide app ([#4191](https://github.com/holoviz/panel/pull/4191))
- Improve `IPyWidget` kernel handling in server contexts ([#4195](https://github.com/holoviz/panel/pull/4195))
- Fix rendering of `IPyWidget` with child views in the notebook ([#4197](https://github.com/holoviz/panel/pull/4197))

### Docs

- Add JupyterLite build and instructions ([#4122](https://github.com/holoviz/panel/pull/4122))
- Document deployment to Hugging Face Spaces ([#4143](https://github.com/holoviz/panel/pull/4143))

## Version 0.14.1

Date: 2022-10-28

This release primarily addresses regressions introduced in 0.14.0 and various long standing bugs. Many thanks to external contributors @liu-kan and @KedoKudo and the maintainers @Hoxbro, @maximlt and @philippjfr for contributing a number of fixes.

### Minor enhancements

- Improve support for `requests` in pyodide ([#3973](https://github.com/holoviz/panel/pull/3973))
- Add option to clear value of DatetimePicker ([#3990](https://github.com/holoviz/panel/pull/3990))
- Add support for hashing dates in pn.cache ([#4004](https://github.com/holoviz/panel/pull/4004))
- Silence `EMPTY_LAYOUT` warnings ([#4056](https://github.com/holoviz/panel/pull/4056))

### Compatibility

- Fix Jupyterlite and latest PyScript compatibility ([#4040](https://github.com/holoviz/panel/pull/4040))

### Bugs

#### Webassembly conversion

- Correctly handle resource mode in when converting to WebAssembly ([#3967](https://github.com/holoviz/panel/pull/3967))

### Jupyter and Server

- Correctly handle future exceptions on threads ([#3977](https://github.com/holoviz/panel/pull/3977))
- Fix `panel serve` index template ([#3980](https://github.com/holoviz/panel/pull/3980))
- Do not error if `curdoc` has been destroyed ([#3994](https://github.com/holoviz/panel/pull/3994))
- Ensure extensions loaded in jupyter kernel are served by StaticHandler ([#4000](https://github.com/holoviz/panel/pull/4000))
- Various fixes for OAuth handling with `pn.serve` ([#4006](https://github.com/holoviz/panel/pull/4006))
- Fix bug in `on_load` callback exception handling ([#4007](https://github.com/holoviz/panel/pull/4007))
- Ensure periodic callbacks are only started on main thread ([#4011](https://github.com/holoviz/panel/pull/4011))
- Ensure jupyter server extension handles explicit `root_dir` ([#4029](https://github.com/holoviz/panel/pull/4029))
- Ensure futures are correctly awaited when executed on thread ([#4031](https://github.com/holoviz/panel/pull/4031))

#### Components

- Ensure `Tabulator` handles filtering on edited values correctly if `show_index=False` ([#3988](https://github.com/holoviz/panel/pull/3988), [#4016](https://github.com/holoviz/panel/pull/4016))
- Ensure `Tabulator` declares numeric sorter for numeric dtypes ([#3999](https://github.com/holoviz/panel/pull/3999))
- Fix regression initializing `DiscreteSlider` with non-integer value ([#4009](https://github.com/holoviz/panel/pull/4009))
- Ensure that template.config.raw_css is correctly applied ([#4018](https://github.com/holoviz/panel/pull/4018))
- Fix handling `MenuButton` clicks when `split=True` ([#4021](https://github.com/holoviz/panel/pull/4021))
- Ensure styling on `Tabulator` with empty DataFrame does not error ([#4028](https://github.com/holoviz/panel/pull/4028))
- Allow changing `level` on `Debugger` widget ([#4057](https://github.com/holoviz/panel/pull/4057))

## Version 0.14.0

Blog post: [https://blog.holoviz.org/panel_0.14.html](https://blog.holoviz.org/panel_0.14.html)

Date: 2022-09-30

This release focuses on three main themes:

- Support for running Panel apps entirely in the browser using WebAssembly (via Pyodide and PyScript)
- Improvements in the app-user experience by making it easier to build responsive and performant applications
- Improvements in the developer experience through static typing and docstrings.

Many, many thanks to everyone who filed issues or contributed to this release. In particular we would like to thank @janimo, @xavArtley, @thuydotm, @jmosbacher, @dmarx, @2WoLpH, @ipopa144, @sdc50 for contributions and @philippjfr, @Hoxbro, @maximlt, and @MarcSkovMadsen for ongoing maintenance and development.

### Features

- Add support for converting Panel apps to pyscript/pyodide ([#3817](https://github.com/holoviz/panel/pull/3817), [#3830](https://github.com/holoviz/panel/pull/3830), [#3851](https://github.com/holoviz/panel/pull/3851), [#3856](https://github.com/holoviz/panel/pull/3856), [#3857](https://github.com/holoviz/panel/pull/3857), [#3858](https://github.com/holoviz/panel/pull/3858), [#3860](https://github.com/holoviz/panel/pull/3860), [#3861](https://github.com/holoviz/panel/pull/3861), [#3863](https://github.com/holoviz/panel/pull/3863), [#3864](https://github.com/holoviz/panel/pull/3864), [#3868](https://github.com/holoviz/panel/pull/3868), [#3878](https://github.com/holoviz/panel/pull/3878))
- Manage our own CDN to improve performance and reliability for delivering JS payloads ([#3867](https://github.com/holoviz/panel/pull/3867), [#3870](https://github.com/holoviz/panel/pull/3870))
- Add ability to `defer_load` of components ([#3882](https://github.com/holoviz/panel/pull/3882))
- Add `pn.widget` helper function ([#1826](https://github.com/holoviz/panel/pull/1826), [#3589](https://github.com/holoviz/panel/pull/3589))
- Add `config.exception_handler` to easily capture, log and notify users about errors ([#3893](https://github.com/holoviz/panel/pull/3893))
- Implement `pn.cache` function for memoization support ([#2411](https://github.com/holoviz/panel/pull/2411))
- Rewrite server extension to run Panel applications in kernels so that previews run in the same environment as the deployed app ([#3763](https://github.com/holoviz/panel/pull/3763))
- Add ability to define authorization callback ([#3777](https://github.com/holoviz/panel/pull/3777))
- Support memray profiler ([#3509](https://github.com/holoviz/panel/pull/3509))
- Add liveness endpoint ([#3832](https://github.com/holoviz/panel/pull/3832))
- Add ability to configure exception handler ([#3896](https://github.com/holoviz/panel/pull/3896))

### Enhancements

- Ensure OAuth redirects to requested app and retains query arguments ([#3555](https://github.com/holoviz/panel/pull/3555))
- Add extension entry point ([#3738](https://github.com/holoviz/panel/pull/3738))
- Update Admin Logs page to use `Tabulator` ([#3694](https://github.com/holoviz/panel/pull/3694))
- Ensure `location.unsync` unsets query params ([#3806](https://github.com/holoviz/panel/pull/3806))
- Allow None value on numeric sliders and `LiteralInput` ([#3174](https://github.com/holoviz/panel/pull/3174))
- Allow serving admin panel with `pn.serve` ([#3798](https://github.com/holoviz/panel/pull/3798))
- Improve `ReactiveHTML` loop support and validation ([#3813](https://github.com/holoviz/panel/pull/3813))
- Support declaring `Perspective.plugin_config` pane ([#3814](https://github.com/holoviz/panel/pull/3814))
- Do not flicker busy indicator during `--autoreload` check ([#3804](https://github.com/holoviz/panel/pull/3804))
- Improve robustness of `state.curdoc` in threaded and async contexts ([#3776](https://github.com/holoviz/panel/pull/3776), [#3810](https://github.com/holoviz/panel/pull/3810), [#3834](https://github.com/holoviz/panel/pull/3834))
- Support datetime bounds for `DatetimePicker` and `DatetimeRangePicker` ([#3788](https://github.com/holoviz/panel/pull/3788))
- Allow setting the Oauth provider using environment variables ([#3698](https://github.com/holoviz/panel/pull/3698))
- Implement `Player.value_throttled` ([#3756](https://github.com/holoviz/panel/pull/3756))
- Ensure that URL query parameters are preserved during OAuth ([#3656](https://github.com/holoviz/panel/pull/3656))
- Improve `Markdown` code syntax highlighting ([#3758](https://github.com/holoviz/panel/pull/3758))
- Ensure components do not re-render if `background` or `loading` parameters change ([#3599](https://github.com/holoviz/panel/pull/3599))
- Add ability to define admin dashboard plugins ([#3668](https://github.com/holoviz/panel/pull/3668))
- Do not calculate embed state for disabled widgets ([#3757](https://github.com/holoviz/panel/pull/3757))
- Add hard bounds to editable sliders ([#3739](https://github.com/holoviz/panel/pull/3739))
- Add bundling of shared resources ([#3894](https://github.com/holoviz/panel/pull/3894))
- Add `Tabulator` as default `param.DataFrame` widget ([#3912](https://github.com/holoviz/panel/pull/3912))


### Documentation

- Overhaul documentation ([#3568](https://github.com/holoviz/panel/pull/3568))
- Improve Fast Template docstrings ([#3570](https://github.com/holoviz/panel/pull/3570))
- Reorganize docs and convert static notebooks to Markdown ([#3875](https://github.com/holoviz/panel/pull/3875), [#3833](https://github.com/holoviz/panel/pull/3833))
- Add DevelopingCustomModels to the webpage ([#3710](https://github.com/holoviz/panel/pull/3710))
- Improve typing ([#3561](https://github.com/holoviz/panel/pull/3561), [#3562](https://github.com/holoviz/panel/pull/3562), [#3592](https://github.com/holoviz/panel/pull/3592), [#3604](https://github.com/holoviz/panel/pull/3604), [#3714](https://github.com/holoviz/panel/pull/3714), [#3729](https://github.com/holoviz/panel/pull/3729))

### Compatibility & Version updates

- Support ipywidgets>=8.0 ([#3782](https://github.com/holoviz/panel/pull/3782))
- Bump jsoneditor package ([#3838](https://github.com/holoviz/panel/pull/3838))
- Upgrade to Tabulator 5.3.2 ([#3784](https://github.com/holoviz/panel/pull/3784))
- Improve Django compatibility ([#3843](https://github.com/holoviz/panel/pull/3843), [#3835](https://github.com/holoviz/panel/pull/3835))
- Remove all usage of deprecated `Pane`

### Bugs

#### Server

- Ensure closed websocket does not cause errors
- Handle session and websocket close cleanly ([#3769](https://github.com/holoviz/panel/pull/3769))
- Fix prefix handling for admin page ([#3809](https://github.com/holoviz/panel/pull/3809))
- Support admin dashboard in multi-process deployments ([#3812](https://github.com/holoviz/panel/pull/3812))
- Improve document cleanup when not invoked using `server_destroy` ([#3842](https://github.com/holoviz/panel/pull/3842))
- Ensure `pn.state.execute` dispatches immediately if possible ([#3859](https://github.com/holoviz/panel/pull/3859))
- Ensure autoload.js resources are appropriately prefixed ([#3873](https://github.com/holoviz/panel/pull/3873))

#### Notebook

- Fix support for copying cells and creating new views in JupyterLab ([#3652](https://github.com/holoviz/panel/pull/3652))
- Ensure output renders in VSCode notebook with latest ipywidgets ([#3765](https://github.com/holoviz/panel/pull/3765))
- Resolve issues with Jupyter slowdown due to event_loop patching on Windows ([#3770](https://github.com/holoviz/panel/pull/3770))
	- Ensure old comm managers do not raise errors in notebook ([#3853](https://github.com/holoviz/panel/pull/3853))
	- Simplify rendering of ipywidget ([#3937](https://github.com/holoviz/panel/pull/3937))

#### Tabulator

- Do not re-render `Tabulator` on `css_classes` or `background` change ([#3598](https://github.com/holoviz/panel/pull/3598))
- Ensure expand icon updates on `Tabulator.expanded` change ([#3703](https://github.com/holoviz/panel/pull/3703))
- Update `page` Parameter when pagination is 'local' ([#3704](https://github.com/holoviz/panel/pull/3704))
- Do not apply `sorters` on `Tabulator` cell edits ([#3744](https://github.com/holoviz/panel/pull/3744))
- Ensure `Tabulator.controls` renders ([#3768](https://github.com/holoviz/panel/pull/3768))
- Ensure correctness of event row and selection indices in `Tabulator` ([#3771](https://github.com/holoviz/panel/pull/3771), [#3841](https://github.com/holoviz/panel/pull/3841))
- Fix issues with frontend and backend sorters being out of sync in Tabulator ([#3825](https://github.com/holoviz/panel/pull/3825), [#3839](https://github.com/holoviz/panel/pull/3839))
- Fix default values of a list header filter in `Tabulator` ([#3826](https://github.com/holoviz/panel/pull/3826))
- Fix the edit event with a python filter in `Tabulator` ([#3829](https://github.com/holoviz/panel/pull/3829))
- Disable client-side date filtering on `Tabulator` ([#3849](https://github.com/holoviz/panel/pull/3849))
- Support editing of pandas masked array dtypes in `Tabulator` ([#3850](https://github.com/holoviz/panel/pull/3850))
- Fix issues editing a cell when client-side filtering applied ([#3852](https://github.com/holoviz/panel/pull/3852))
- Do not recompute data when local pagination is enabled ([#3854](https://github.com/holoviz/panel/pull/3854))
- Don't skip filtering when the column name is undefined ([#3862](https://github.com/holoviz/panel/pull/3862))

#### Misc

- Fix `FileInput.save` ([#3579](https://github.com/holoviz/panel/pull/3579))
- Fix issues with `Matplotlib.high_dpi` option ([#3591](https://github.com/holoviz/panel/pull/3591), [#3594](https://github.com/holoviz/panel/pull/3594))
- Ensure layout recomputes on `HTML`/`Markdown` re-rerender ([#3616](https://github.com/holoviz/panel/pull/3616))
- Allow overriding all widget parameters on `Param` pane ([#3754](https://github.com/holoviz/panel/pull/3754))
- Ensure `DatePicker` start/end are transformed when jslinked ([#3759](https://github.com/holoviz/panel/pull/3759))
- Ensure notifications can be enabled without a template ([#3820](https://github.com/holoviz/panel/pull/3820))
- Ensure `ReactiveHTML` inline callbacks on loop variables return correct node ([#3840](https://github.com/holoviz/panel/pull/3840))
- Ensure that `Perspective` does not take precedence on empty dict ([#3936](https://github.com/holoviz/panel/pull/3936))
- Improve `sizing_mode` behavior when width/height are specified ([#3955](https://github.com/holoviz/panel/pull/3955))
- Do not load notyf resources unless notifications are enabled ([#3958](https://github.com/holoviz/panel/pull/3958))

## Version 0.13.1

Date: 2022-05-20

### Enhancements

- Add repr to cell and edit events ([#3434](https://github.com/holoviz/panel/pull/3534))
- Improvements for pyodide handling ([#3444](https://github.com/holoviz/panel/pull/3444), [#3508](https://github.com/holoviz/panel/pull/3508), [#3511](https://github.com/holoviz/panel/pull/3511))
- Add support for Plotly animation frames ([#3449](https://github.com/holoviz/panel/pull/3499))
- Implement single and multi-selection in Vega pane ([#3470](https://github.com/holoviz/panel/pull/3470), [#3499](https://github.com/holoviz/panel/pull/3499), [#3505](https://github.com/holoviz/panel/pull/3505))
- Add typehints to help developers and users ([#3476](https://github.com/holoviz/panel/pull/3476))
- Add `pn.state.execute` method to run callbacks in the right context ([#3550](https://github.com/holoviz/panel/pull/3550))
- Add support for asynchronous `on_edit`/`on_click` Tabulator callbacks ([#3550](https://github.com/holoviz/panel/pull/3550))
- Add `DatetimeRangeSlider` widget ([#3548](https://github.com/holoviz/panel/pull/3548))


### Bug fixes

- Fix pyodide array buffer conversion ([#3409](https://github.com/holoviz/panel/pull/3409))
- Allow `placeholder` to be updated on `TextEditor` ([#3427](https://github.com/holoviz/panel/pull/3427))
- Ensure bokeh correctly detects whether `HTML`/`Markdown` contains latex ([#3438](https://github.com/holoviz/panel/pull/3438))
- Ensure notifications work on server created with `pn.serve` and `.show` ([#3445](https://github.com/holoviz/panel/pull/3445))
- Replace slickgrid background image in custom `FastTemplate` CSS ([#3461](https://github.com/holoviz/panel/pull/3461))
- Ensure `param.Array` is synced correctly in `ReactiveHTML` ([#3456](https://github.com/holoviz/panel/pull/3456))
- Ensure selection on filtered `Tabulator` does not raise out-of-bounds error ([#3462](https://github.com/holoviz/panel/pull/3462))
- Ensure updating `Tabulator` does not reset scroll position ([#3450](https://github.com/holoviz/panel/issues/3450))
- Various fixes for `FastTemplate` CSS ([#3464](https://github.com/holoviz/panel/pull/3464))
- Ensure `Tabulator` `on_click` and `on_edit` events return correct row when paginated ([#3410](https://github.com/holoviz/panel/pull/3410))
- Fix broken JupyterLab preview ([#3469](https://github.com/holoviz/panel/pull/3469))
- Skip `Tabulator` row selection when clicking on expand button ([#3474](https://github.com/holoviz/panel/pull/3474))
- Ensure overflow in `MaterialTemplate` is not clipped ([#3492](https://github.com/holoviz/panel/pull/3492))
- Allow providing `--index` for directory style apps ([#3493](https://github.com/holoviz/panel/pull/3493))
- Ensure Tabulator expanded rows are sized correctly after re-render ([#3507](https://github.com/holoviz/panel/pull/3507))
- Make CodeHandler robust to document that has been destroyed ([#3510](https://github.com/holoviz/panel/pull/3510))
- Do not sync `DataFrame` widget `sorters` parameter with bokeh model ([#3527](https://github.com/holoviz/panel/pull/3527))
- Ensure that HoloViews callback events are not auto-dispatched ([#3528](https://github.com/holoviz/panel/pull/3528))
- Ensure non-updateable `Pane` can be updated inside `Tabs` ([#3532](https://github.com/holoviz/panel/pull/3532))
- Fix slowdown of JupyterLab on Windows ([#3531](https://github.com/holoviz/panel/pull/3531))
- Fix issue with inverted data when editing a cell in a sorted Tabulator column ([#3531](https://github.com/holoviz/panel/pull/3531))
- Ensure `Tabulator` has correct layout after re-render ([#3536](https://github.com/holoviz/panel/pull/3536))
- Do not log events generated by admin page on the admin page ([#3539](https://github.com/holoviz/panel/pull/3539))
- Fix Tabulator events when the original column is not a string ([#3541](https://github.com/holoviz/panel/pull/3541))

### Documentation

- Adds docstrings to layouts ([#3417](https://github.com/holoviz/panel/pull/3417))
- Show how to filter categorical and temporal data from `Altair`/VegaLite ([#3401](https://github.com/holoviz/panel/pull/3401))
- Document how to make a `Tabulator` column non-editable ([#3489](https://github.com/holoviz/panel/pull/3489))

## Version 0.13.0

Date: 2022-04-15

Blog post: [https://blog.holoviz.org/panel_0.13.0.html](https://blog.holoviz.org/panel_0.13.0.html)

### Features

- Add support for scheduling global callbacks ([#2661](https://github.com/holoviz/panel/pull/2661))
- MathJax now supported in `Markdown` and `HTML` ([#2847](https://github.com/holoviz/panel/pull/2847))
- Improved support for async (e.g. in ParamMethod/ParamFunction, bind, onload etc.) ([#2964](https://github.com/holoviz/panel/pull/2964), [#3264](https://github.com/holoviz/panel/pull/3264), [#2737](https://github.com/holoviz/panel/pull/2737))
- Support rendering Panel objects in Jupyterlite and Pyodide ([#3252](https://github.com/holoviz/panel/pull/3252), [#3361](https://github.com/holoviz/panel/pull/3361), [#3381](https://github.com/holoviz/panel/pull/3381))
- Add `JSONEditor` widget ([#1974](https://github.com/holoviz/panel/pull/1974))
- Add quill.js based `TextEditor` widget ([#2875](https://github.com/holoviz/panel/pull/2875))
- Add `GenericLoginHandler` for custom OAuth ([#2873](https://github.com/holoviz/panel/pull/2873), [#2960](https://github.com/holoviz/panel/pull/2960))
- Implement `Notifications` API for templates ([#3093](https://github.com/holoviz/panel/pull/3093))
- Implement built-in threading ([#2597](https://github.com/holoviz/panel/pull/2597), [#2632](https://github.com/holoviz/panel/pull/2632), [#3081](https://github.com/holoviz/panel/pull/3081))
- Implement profiling page for Panel ([#2645](https://github.com/holoviz/panel/pull/2645), [#2664](https://github.com/holoviz/panel/pull/2664), [#2667](https://github.com/holoviz/panel/pull/2667), [#2707](https://github.com/holoviz/panel/pull/2707), [#2905](https://github.com/holoviz/panel/pull/2905))
- Implement support for `Vega` events ([#2592](https://github.com/holoviz/panel/pull/2592))
- Implement `ArrayInput` widget ([#2047](https://github.com/holoviz/panel/pull/2047))
- Add `Debugger` widget ([#2548](https://github.com/holoviz/panel/pull/2548))
- Add LinearGauge indicator ([#3222](https://github.com/holoviz/panel/pull/3222))
- Add `ComponentResourceHandler` to server ([#3284](https://github.com/holoviz/panel/pull/3284), [#3289](https://github.com/holoviz/panel/pull/3289), [#3303](https://github.com/holoviz/panel/pull/3303))

### Enhancements

#### Components

- Editable sliders `name` can be changed ([#2678](https://github.com/holoviz/panel/pull/2678))
- Make `Plotly` pane resize when window resizes ([#2704](https://github.com/holoviz/panel/pull/2704))
- `Viewer` objects can now be used with `pn.serve` ([#2769](https://github.com/holoviz/panel/pull/2769))
- `VTK` improvement for NaN handling ([#2826](https://github.com/holoviz/panel/pull/2826))
- Add support for configuring `Vega` output ([#2846](https://github.com/holoviz/panel/pull/2846))
- Add a `groups` parameter to `Select` widget ([#2876](https://github.com/holoviz/panel/pull/2876))
- Add `Card.hide_header` option ([#2947](https://github.com/holoviz/panel/pull/2947))
- Support bytes and pathlib.Path objects on Image ([#2963](https://github.com/holoviz/panel/pull/2963), [#3294](https://github.com/holoviz/panel/pull/3294))
- Add programmatic control over Player widget ([#2970](https://github.com/holoviz/panel/pull/2970), [#2994](https://github.com/holoviz/panel/pull/2994))
- Add alphabetical and custom sort to `Param` ([#2986](https://github.com/holoviz/panel/pull/2986))
- Add `autoplay` and `muted` to `Audio` and `Video` ([#3053](https://github.com/holoviz/panel/pull/3053))
- Add a `disabled_options` parameter to a custom Select widget ([#3067](https://github.com/holoviz/panel/pull/3067))
- Expose the `orientation` parameter of the button group widgets ([#3083](https://github.com/holoviz/panel/pull/3083))
- Add support for rendering pandas styler objects ([#3152](https://github.com/holoviz/panel/pull/3152))
- `Viewer` now better at working with `depends` functions ([#3159](https://github.com/holoviz/panel/pull/3159))
- Improve support for jinja2 loops in `ReactiveHTML` ([#3236](https://github.com/holoviz/panel/pull/3236))
- Add ability to require explicit load of ReactiveHTML extension ([#3254](https://github.com/holoviz/panel/pull/3254))
- Improve datetime handling of sliders ([#3276](https://github.com/holoviz/panel/pull/3276))
- Add support for multiple files in `FileInput.save` ([#3300](https://github.com/holoviz/panel/pull/3300))
- Add improved Tabs model that resolves sizing and hover issues ([#3301](https://github.com/holoviz/panel/pull/3301), [#3321](https://github.com/holoviz/panel/pull/3321), [#3329](https://github.com/holoviz/panel/pull/3329))

#### Tabulator

- Add support to expand rows in `Tabulator` ([#2762](https://github.com/holoviz/panel/pull/2762), [#2837](https://github.com/holoviz/panel/pull/2837), [#3010](https://github.com/holoviz/panel/pull/3010), [#3163](https://github.com/holoviz/panel/pull/3163))
- Implement client-side filtering on `Tabulator` ([#2815](https://github.com/holoviz/panel/pull/2815), [#3298](https://github.com/holoviz/panel/pull/3298))
- Add `Tabulator.header_align` parameter ([#2861](https://github.com/holoviz/panel/pull/2861))
- Implement `Tabulator.on_edit` callbacks ([#2887](https://github.com/holoviz/panel/pull/2887), [#3209](https://github.com/holoviz/panel/pull/3209), [#2958](https://github.com/holoviz/panel/pull/2958))
- Implement DateEditor and DatetimeEditor for `Tabulator` ([#2899](https://github.com/holoviz/panel/pull/2899), [#3008](https://github.com/holoviz/panel/pull/3008))
- Implement `Tabulator.buttons` ([#3111](https://github.com/holoviz/panel/pull/3111))
- Redesign `Tabulator.styles` handling ([#3175](https://github.com/holoviz/panel/pull/3175))
- Set default alignment for `Tabulator` ([#3194](https://github.com/holoviz/panel/pull/3194))
- Bidirectionally sync `Tabulator.sorters` ([#3217](https://github.com/holoviz/panel/pull/3217))
- Add support for setting percentage widths on `Tabulator` columns ([#3239](https://github.com/holoviz/panel/pull/3239))
- Add `Tabulator.on_click` callback ([#3245](https://github.com/holoviz/panel/pull/3245))
- Restore `Tabulator` scroll position after patch ([#3273](https://github.com/holoviz/panel/pull/3273))
- Enable max row limits for `Tabulator` ([#3306](https://github.com/holoviz/panel/pull/3306))

#### Notebook

- Add basic JupyterLab theme support ([#2848](https://github.com/holoviz/panel/pull/2848))
- Support jupyter server `root_dir` with lab extension ([#3172](https://github.com/holoviz/panel/pull/3172))
- Avoid multiple extension execution in the notebook ([#3266](https://github.com/holoviz/panel/pull/3266))
- Added fullpath to `jupyter_server_extension` ([#3270](https://github.com/holoviz/panel/pull/3270))

#### General improvements

- Warn users if extension is not loaded before server page is rendered ([#2766](https://github.com/holoviz/panel/pull/2766))
- Sync URL location hash interactively ([#2982](https://github.com/holoviz/panel/pull/2982))
- Change accent and header background color for Fast Templates ([#2984](https://github.com/holoviz/panel/pull/2984))
- Add thread safety and TTL to `pn.state.as_cached` ([#3198](https://github.com/holoviz/panel/pull/3198))
- Add py.typed file to support mypy ([#3055](https://github.com/holoviz/panel/pull/3055))
- Handle authentication errors ([#3096](https://github.com/holoviz/panel/pull/3096))
- Support saving png to file-like objects ([#3155](https://github.com/holoviz/panel/pull/3155))
- Check if there are any query parameters in `baseurl` and adds it to `location.search` if possible ([#3214](https://github.com/holoviz/panel/pull/3214))
- Improve handling of `--index` CLI argument ([#3221](https://github.com/holoviz/panel/pull/3221))
- Fix event dispatch ([#3231](https://github.com/holoviz/panel/pull/3231))
- Add azure oauth v2.0 endpoint support ([#3224](https://github.com/holoviz/panel/pull/3224))
- Ensure `gc.collect` is not excessively called ([#3259](https://github.com/holoviz/panel/pull/3259))
- Added `panel.reactive` and `panel.viewable` to namespace ([#3157](https://github.com/holoviz/panel/pull/3157))
- Consistent handling of page title ([#3290](https://github.com/holoviz/panel/pull/3290))

### Bugs

#### Components

- Fix warnings in `ReactiveHTML` regex ([#2786](https://github.com/holoviz/panel/pull/2786))
- Fixed UTF-8 decoding in Terminal widget ([#2880](https://github.com/holoviz/panel/pull/2880))
- Allow a `param.Selector` with no objects to be casted to `AutocompleteInput` ([#2966](https://github.com/holoviz/panel/pull/2966))
- Update `ButtonGroup` value when changing options ([#2999](https://github.com/holoviz/panel/pull/2999))
- Fix `TQDM` style color reset ([#3040](https://github.com/holoviz/panel/pull/3040))
- Fix align-items on `Flexbox` ([#3122](https://github.com/holoviz/panel/pull/3122))
- Fix issue serializing `Spinner` with negative value ([#3154](https://github.com/holoviz/panel/pull/3154))
- Fixes for jslinking `HoloViews` components ([#3165](https://github.com/holoviz/panel/pull/3165))
- `BooleanStatus` and `LoadingSpinner` now update when changing color ([#3191](https://github.com/holoviz/panel/pull/3191))
- Fix `Widget.from_param` when precedence is negative ([#3199](https://github.com/holoviz/panel/pull/3199))
- Ensure `DiscreteSlider` label is updated ([#3278](https://github.com/holoviz/panel/pull/3278))
- Ensure `ReactiveHTML` template variables only escapes exact matches ([#3279](https://github.com/holoviz/panel/pull/3279))
- Fix handling of single and empty options on `DiscreteSlider` ([#3297](https://github.com/holoviz/panel/pull/3297))
- Ensure `Progress` correctly initializes as indeterminate ([#3307](https://github.com/holoviz/panel/pull/3307))
- Always resolve DOM nodes in ReactiveHTML._scripts ([#3311](https://github.com/holoviz/panel/pull/3311))
- Fixes `CrossSelector.disabled` parameter ([#3326](https://github.com/holoviz/panel/pull/3326))
- Fix `EditableSlider` updates when no `value_throttled` is set ([#3387](https://github.com/holoviz/panel/pull/3387))

#### Tabulator

- Fix HTMLTemplateFormatter on `Tabulator` ([#2781](https://github.com/holoviz/panel/pull/2781))
- Fix layout of `Tabulator` with non-default theme ([#3147](https://github.com/holoviz/panel/pull/3147))
- Ensure `Tabulator` selection is not reset on patch ([#3287](https://github.com/holoviz/panel/pull/3287))
- Fix `Tabulator.download` method ([#3292](https://github.com/holoviz/panel/pull/3292))
- Restore ability to limit number of `selectable` rows on `Tabulato` ([#3295](https://github.com/holoviz/panel/pull/3295))
- Ensure `Tabulator` value update reports correct old value ([#3308](https://github.com/holoviz/panel/pull/3308))

#### Templates

- Fix Fast template vertical slider CSS ([#3045](https://github.com/holoviz/panel/pull/3045))
- Fix template `theme.css` ([#3057](https://github.com/holoviz/panel/pull/3057))
- Ensure roots are rendered into `GoldenTemplate` ([#3313](https://github.com/holoviz/panel/pull/3313))
- Ensure correct theme is applied to `HoloViews` pane in template ([#3386](https://github.com/holoviz/panel/pull/3386))

#### General

- Added check for bool in `Location.parse_query` ([#2759](https://github.com/holoviz/panel/pull/2759))
- Ensure cleanup happens when enabling `--warm` or `--autoreload` with Bokeh 2.4 ([#2760](https://github.com/holoviz/panel/pull/2760))
- Ensure autoload.js correctly determines `state.rel_path` ([#2776](https://github.com/holoviz/panel/pull/2776))
- Fix issue with `.app` method ([#3047](https://github.com/holoviz/panel/pull/3047))
- Add document argument to django.py autoload_js_script call ([#3100](https://github.com/holoviz/panel/pull/3100))
- Avoid sending messages on closed or closing Websocket ([#3115](https://github.com/holoviz/panel/pull/3115))
- Fix Django resource handling ([#3116](https://github.com/holoviz/panel/pull/3116))
- Fix handling of `loading_max_height` ([#3205](https://github.com/holoviz/panel/pull/3205))
- Fix Django `DocConsumer` ([#3281](https://github.com/holoviz/panel/pull/3281))
- Fix `jupyter_server_config` for preview server extension ([#3291](https://github.com/holoviz/panel/pull/3291))
- Fix handling of `oauth_provider` argument to `panel.io.server.serve` ([#3293](https://github.com/holoviz/panel/pull/3293))
- Allow exporting absolute paths when saving ([#3305](https://github.com/holoviz/panel/pull/3305))

### Documentation

- Added `ToggleGroup` docs ([#2679](https://github.com/holoviz/panel/pull/2679))
- Adds a code of conduct ([#2892](https://github.com/holoviz/panel/pull/2892))
- Add docstrings to sliders module ([#3176](https://github.com/holoviz/panel/pull/3176))
- Gallery Examples for Graphviz and NetworkX ([#2732](https://github.com/holoviz/panel/pull/2732))
- Add layouts + throttling sections to Performance docs ([#3171](https://github.com/holoviz/panel/pull/3171))
- Adds `Plotly` styling gallery notebook ([#3038](https://github.com/holoviz/panel/pull/3038))
- Adds a matplotlib style guide notebook to gallery ([#3036](https://github.com/holoviz/panel/pull/3036))
- Adds vega altair style example for the gallery. ([#3032](https://github.com/holoviz/panel/pull/3032))
- Wrap new gallery examples into apps ([#2546](https://github.com/holoviz/panel/pull/2546))
- Add docstring to panel module ([#3177](https://github.com/holoviz/panel/pull/3177))
- added documentation for gcp ([#3119](https://github.com/holoviz/panel/pull/3119))
- Add docs about the file size limits of the `FileInput` widget ([#3044](https://github.com/holoviz/panel/pull/3044))
- Add docstrings for most widgets and panes ([#3352](https://github.com/holoviz/panel/pull/3352), [#3353](https://github.com/holoviz/panel/pull/3353), [#3354](https://github.com/holoviz/panel/pull/3354), [#3359](https://github.com/holoviz/panel/pull/3359), [#3365](https://github.com/holoviz/panel/pull/3365), [#3366](https://github.com/holoviz/panel/pull/3366), [#3367](https://github.com/holoviz/panel/pull/3367), [#3369](https://github.com/holoviz/panel/pull/3369))

### Compatibility

- Update to latest version of `Perspective` ([#3318](https://github.com/holoviz/panel/pull/3318))
- Update `Vega` version ([#3320](https://github.com/holoviz/panel/pull/3320))
- Update `ipywidgets` support for compatibility with latest bokeh ([#3206](https://github.com/holoviz/panel/pull/3206), [#3299](https://github.com/holoviz/panel/pull/3299))
- Bump plotly.js version ([#3227](https://github.com/holoviz/panel/pull/3227))
- Updates to Param 2.0 API ([#2845](https://github.com/holoviz/panel/pull/2845))
- Updates for Python 3.10 deprecations ([#3065](https://github.com/holoviz/panel/pull/3065))
- Update and improve `DeckGL` pane ([#3158](https://github.com/holoviz/panel/pull/3158))

### API Changes

- Make `Param.mapping` public ([#3173](https://github.com/holoviz/panel/pull/3173))
- Switch `DatetimePicker` `start`/`end` to `param.Date` ([#3202](https://github.com/holoviz/panel/pull/3202))
- `Perspective` parameters renamed: `row_pivots` -> `split_by`, `column_pivots` -> `group_by` and `computed_columns` -> `expressions` ([#3318](https://github.com/holoviz/panel/pull/3318))

## Version 0.12.7

Date: 2021-03-27

The 0.12.7 release primarily fixes an incompatibility with the new jinja2 3.1.0 release. Many thanks to @maartenbreddels, @govinda18, @raybellwaves and the maintainers @maximlt and @philippjfr for contributing further fixes to this release.

Bug fixes:

- Wrong offset when memoryview format is non-byte ([#3206](https://github.com/holoviz/panel/pull/3206))
- Support jupyter server root_dir with lab extension ([#3172](https://github.com/holoviz/panel/pull/3172))

Docs:

- add note on enabling panel widget on Jupyter Lab ([#3029](https://github.com/holoviz/panel/pull/3029))
- Remove redundant and confusing JupyterLab install instructions ([#3037](https://github.com/holoviz/panel/pull/3037))

Compatibility:

- Fix jinja2 imports ([#3258](https://github.com/holoviz/panel/pull/3258))

## Version 0.12.6

Date: 2021-12-08

The 0.12.6 release fixes a major regression introduced in the last release along with a small number of pre-existing bugs.

Regressions:

- Always load imported bokeh extensions ([#2957](https://github.com/holoviz/panel/pull/2957))
- Fix regression rendering `HoloViews` plotly backend ([#2961](https://github.com/holoviz/panel/pull/2961))

Bug fixes:

- Do not run `Ace` import on initialization ([#2959](https://github.com/holoviz/panel/pull/2959))
- Improve handling of `ReactiveHTML` cleanup ([#2974](https://github.com/holoviz/panel/pull/2974), [#2993](https://github.com/holoviz/panel/pull/2993))
- Ensure empty `Str` has same height as non-empty ([#2981](https://github.com/holoviz/panel/pull/2981))
- Ensure `Tabulator` supports grouping on numeric columns ([#2987](https://github.com/holoviz/panel/pull/2987))
- Fix `Tabulator` with multi-index and pagination ([#2989](https://github.com/holoviz/panel/pull/2989))
- Allow index as column name in table widgets ([#2990](https://github.com/holoviz/panel/pull/2990))
- Ensure TemplateActions component does not have height ([#2997](https://github.com/holoviz/panel/pull/2997))

## Version 0.12.5

Date: 2021-11-23

The 0.12.5 release contains a larger number of bug fixes and minor enhancements. Many thanks to @pmav99, @samuelyeewl, @xavArtley, @L8Y, @Prashant0kgp, @t-houssian, @kristw, @jlstevens and the maintainers @maximlt, @MarcSkovMadsen and @philippjfr for their contributions to this release.

Compatibility:

- Ensure ipywidget rendering is compatible with ipykernel>6 and bokeh>2.4 ([#2798](https://github.com/holoviz/panel/pull/2798))
- Build panel.js against bokeh.js 2.4.2 ([#2945](https://github.com/holoviz/panel/pull/2945))

Enhancements:

- Add 'light' to list of button types ([#2814](https://github.com/holoviz/panel/pull/2814), [#2816](https://github.com/holoviz/panel/pull/2816))
- Make OAuth cookie expiry configurable ([#2724](https://github.com/holoviz/panel/pull/2724))
- Run `onload` callbacks with `--warm` option ([#2844](https://github.com/holoviz/panel/pull/2844))
- Improve Plotly responsive sizing behavior ([#2838](https://github.com/holoviz/panel/pull/2838))
- Adds escape parameter to `DataFrame` pane to enable using html markup ([#2893](https://github.com/holoviz/panel/pull/2893))
- Allow to update the completions options from a parameter ([#2895](https://github.com/holoviz/panel/pull/2895))
- `Tabs` cache dynamic contents ([#2909](https://github.com/holoviz/panel/pull/2909))
- Allow setting a maximum height for the loading indicator ([#2910](https://github.com/holoviz/panel/pull/2910))
- Ensure loading of MathJax bundle is optional ([#2919](https://github.com/holoviz/panel/pull/2919))

Bug fixes:

- Resolve issues with inline resources on save ([#2794](https://github.com/holoviz/panel/pull/2794))
- Restore ability to set a maximum number of selectable rows on `Tabulator` ([#2791](https://github.com/holoviz/panel/pull/2791))
- Fixed bug where Tabulator with remote pagination would modify the wrong rows ([#2801](https://github.com/holoviz/panel/pull/2801))
- Ensure non-exported requirejs modules do not error ([#2808](https://github.com/holoviz/panel/pull/2808))
- Ensure `Tabulator` checkbox selection only happens in checkbox column ([#2812](https://github.com/holoviz/panel/pull/2812))
- `Vtkvolume` correction of dimensions order ([#2818](https://github.com/holoviz/panel/pull/2818))
- Allow data item to miss optional field in `Vega` pane ([#2853](https://github.com/holoviz/panel/pull/2853))
- Allow to set `AutoCompleteInput` in a Param pane ([#2874](https://github.com/holoviz/panel/pull/2874))
- Fix `Terminal` keystroke and size handling ([#2878](https://github.com/holoviz/panel/pull/2878))
- Fix `Tabulator` styles on scroll ([#2881](https://github.com/holoviz/panel/pull/2881))
- Do not sync `Indicator` properties from frontend to avoid errors ([#2886](https://github.com/holoviz/panel/pull/2886))
- Fix roundtrip of datetimes on `ReactiveData` components ([#2888](https://github.com/holoviz/panel/pull/2888))
- Fix handling of `Plotly` pane in `Tabs` ([#2890](https://github.com/holoviz/panel/pull/2890))
- Fix bokeh colorbar background for dark theme ([#2897](https://github.com/holoviz/panel/pull/2897))
- Fix issues when streaming or patching `ReactiveData` ([#2900](https://github.com/holoviz/panel/pull/2900))
- Ensure stream and patch events do not boomerang ([#2902](https://github.com/holoviz/panel/pull/2902))
- Fixes for `Card` rendering in `MaterialTemplate` ([#2911](https://github.com/holoviz/panel/pull/2911), [#2912](https://github.com/holoviz/panel/pull/2912))
- Ensure `HoloViews` matplotlib output uses tight layout ([#2920](https://github.com/holoviz/panel/pull/2920))
- Fix decoding of single quoted strings in url parameters ([#2925](https://github.com/holoviz/panel/pull/2925))
- Fix Tabulator checkbox selection ([#2931](https://github.com/holoviz/panel/pull/2931))
- Fix Vega pane sizing issues ([#2933](https://github.com/holoviz/panel/pull/2933))
- Ensure toggled Accordion only triggers one event on change of active Card ([#2934](https://github.com/holoviz/panel/pull/2934))
- Ensure LiteralInput JS deserializer does not insert extra spaces ([#2935](https://github.com/holoviz/panel/pull/2935))
- Fix issue in detecting script data assignment in `ReactiveHTML` ([#2939](https://github.com/holoviz/panel/pull/2939))
- Ensure `Card` collapsible icon offset is computed robustly ([#2940](https://github.com/holoviz/panel/pull/2940))
- Ensure `--autoreload` does not reload panel modules ([#2941](https://github.com/holoviz/panel/pull/2941))
- Ensure `pn.state.curdoc` is available to async callbacks ([#2942](https://github.com/holoviz/panel/pull/2942))

Documentation:

- Fix default values of `panels.io.server.serve` ([#2799](https://github.com/holoviz/panel/pull/2799))
- Update docs about pn.serve per user state ([#2849](https://github.com/holoviz/panel/pull/2849))
- Added FastApi in the user guide for embedding apps ([#2870](https://github.com/holoviz/panel/pull/2870))
- Simplify homepage ([#2850](https://github.com/holoviz/panel/pull/2850))

CVEs:

- Update jQuery to remediate CVEs ([#2885](https://github.com/holoviz/panel/pull/2885))

## Version 0.12.4

Date: 2021-09-24

The 0.12.4 release fixes a number of bugs and a regression of the autoreload feature in 0.12.2 and 0.12.3.

Compatibility:

- Fix issues with `--autoreload` caused by changes in Bokeh 2.4 ([#2755](https://github.com/holoviz/panel/pull/2755))

Enhancements:

- Ensure user is warned if an extension was not loaded in time on server ([#2765](https://github.com/holoviz/panel/pull/2765))
- Allow Viewer classes to be served ([#2768](https://github.com/holoviz/panel/pull/2768))
- Add support for rendering `.ico` files and `pathlib` objects ([#2757](https://github.com/holoviz/panel/pull/2757))

Bug fixes:

- Fixed export of vtk.js module ([#2562](https://github.com/holoviz/panel/pull/2562))
- Fix broken `HTMLTemplateFormatter` on `Tabulator` ([#2730](https://github.com/holoviz/panel/pull/2730))
- Fix serialization issues of Panel components on `ReactiveHTML` ([#2743](https://github.com/holoviz/panel/pull/2743))
- Ensure `FlexBox` behaves like a layout and makes its children discoverable ([#2779](https://github.com/holoviz/panel/pull/2779))
- Ensure `Plotly` plots can be updated in tabs ([#2747](https://github.com/holoviz/panel/pull/2747))
- Fix embedding of Panel apps in Flask ([#2727](https://github.com/holoviz/panel/pull/2727))
- Ensure `Spinner` widget honors bounds when created from `Param` object ([#2740](https://github.com/holoviz/panel/pull/2740))
- Ensure `Tabulator` style does not disappear after resize event ([#2770](https://github.com/holoviz/panel/pull/2770))
- Fix `PeriodicCallback` errors ([#2764](https://github.com/holoviz/panel/pull/2764))
- Fix syncing of boolean types with URL parameters ([#2758](https://github.com/holoviz/panel/pull/2758))
- Ensure Tabulator `download_menu` applies kwargs to the filename `TextInput` ([#2763](https://github.com/holoviz/panel/pull/2764))
- Ensure `Tabulator` does not error when no Styler is defined ([#2785](https://github.com/holoviz/panel/pull/2785))

Documentation:

- Fix MaterialUI custom component example ([#2680](https://github.com/holoviz/panel/pull/2680))
- Fix image url in `Markdown` reference gallery example ([#2734](https://github.com/holoviz/panel/pull/2734))
- Add Folium thumbnail in reference gallery ([#2744](https://github.com/holoviz/panel/pull/2744))


## Version 0.12.3

Date: 2021-09-17

The 0.12.2 release unfortunately has a compatibility issue with Bokeh 2.4 which broke the `show()` method. This release fixes this regression.

- Patch Bokeh to fix show() ([#2748](https://github.com/holoviz/panel/pull/2748))


## Version 0.12.2

Date: 2021-09-16

This a patch release with a small number of bug fixes and compatibility for bokeh 2.4. Many thanks to the contributors @Stubatiger, @maximlt, @nghenzi and the maintainers @MarcSkovMadsen and @philippjfr for the fixes in this release.

Enhancements:

- Add option to hide constant parameters on `Param` pane ([#2637](https://github.com/holoviz/panel/issues/2637))
- Added `on_session_destroyed` callback ([#2659](https://github.com/holoviz/panel/issues/2659))
- Stricter validation for linking syntax in `ReactiveHTML._template` ([#2689](https://github.com/holoviz/panel/issues/2689))

Bug fixes:

- Improved thread safety ([#2631](https://github.com/holoviz/panel/issues/2631))
- Ensure sessions get distinct files in `config` ([#2646](https://github.com/holoviz/panel/issues/2646))
- Fix bug when updating `Trend` data ([#2647](https://github.com/holoviz/panel/issues/2647))
- Ensure sorters are applied correctly after updating `Tabulator` value ([#2639](https://github.com/holoviz/panel/issues/2639))
- Correctly reflect filtered data on `Tabulator.selection` ([#2676](https://github.com/holoviz/panel/issues/2676)
- Unescape child literal HTML in ReactiveHTML ([#2690](https://github.com/holoviz/panel/issues/2690))
- Ensure Trend indicator can be rendered in layout ([#2694](https://github.com/holoviz/panel/issues/2694))

Documentation:

- Enhance templates docs ([#2658](https://github.com/holoviz/panel/issues/2658))
- Add Folium reference notebook ([#2672](https://github.com/holoviz/panel/issues/2672))

Compatibility:

- Add support for bokeh 2.4 ([#2644](https://github.com/holoviz/panel/issues/2644), [#2687](https://github.com/holoviz/panel/issues/2687), [#2696](https://github.com/holoviz/panel/issues/2696))


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
- Tabulator no longer loaded by default, must be initialized with `pn.extension('tabulator')` ([#2364](https://github.com/holoviz/panel/issues/2364))

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
- Allow setting `root_directory` on `FileSelector` widget ([#2086](https://github.com/holoviz/panel/issues/2086))

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
   * Misc widget fixes and improvements ([#703](https://github.com/holoviz/panel/issues/703), [#717](https://github.com/holoviz/panel/issues/717), [#724](https://github.com/holoviz/panel/issues/724), [#762](https://github.com/holoviz/panel/issues/762), [#775](https://github.com/holoviz/panel/issues/775))

Bug fixes and minor improvements:
- Removed mutable default args ([#692](https://github.com/holoviz/panel/issues/692), [#694](https://github.com/holoviz/panel/issues/694))
- Improved tests ([#691](https://github.com/holoviz/panel/issues/691), [#699](https://github.com/holoviz/panel/issues/699), [#700](https://github.com/holoviz/panel/issues/700))
- Improved fancy layout for scrubber ([#571](https://github.com/holoviz/panel/issues/571))
- Improved plotly datetime handling ([#688](https://github.com/holoviz/panel/issues/688), [#698](https://github.com/holoviz/panel/issues/698))
- Improved JSON embedding ([#589](https://github.com/holoviz/panel/issues/589))
- Misc fixes and improvements ([#626](https://github.com/holoviz/panel/issues/626), [#631](https://github.com/holoviz/panel/issues/631), [#645](https://github.com/holoviz/panel/issues/645), [#662](https://github.com/holoviz/panel/issues/662), [#681](https://github.com/holoviz/panel/issues/681), [#689](https://github.com/holoviz/panel/issues/689), [#695](https://github.com/holoviz/panel/issues/695), [#723](https://github.com/holoviz/panel/issues/723), [#725](https://github.com/holoviz/panel/issues/725), [#738](https://github.com/holoviz/panel/issues/738), [#743](https://github.com/holoviz/panel/issues/743), [#744](https://github.com/holoviz/panel/issues/744), [#748](https://github.com/holoviz/panel/issues/748), [#749](https://github.com/holoviz/panel/issues/749), [#758](https://github.com/holoviz/panel/issues/758), [#768](https://github.com/holoviz/panel/issues/768), [#772](https://github.com/holoviz/panel/issues/772), [#774](https://github.com/holoviz/panel/issues/774), [#775](https://github.com/holoviz/panel/issues/775), [#779](https://github.com/holoviz/panel/issues/779), [#784](https://github.com/holoviz/panel/issues/784), [#785](https://github.com/holoviz/panel/issues/785), [#787](https://github.com/holoviz/panel/issues/787), [#788](https://github.com/holoviz/panel/issues/788), [#789](https://github.com/holoviz/panel/issues/789))
- Prepare support for python 3.8 ([#702](https://github.com/holoviz/panel/issues/702))

Documentation:
- Expanded and updated FAQ ([#750](https://github.com/holoviz/panel/issues/750), [#765](https://github.com/holoviz/panel/issues/765))
- Add Comparisons section ([#643](https://github.com/holoviz/panel/issues/643))
- Docs fixes and improvements ([#635](https://github.com/holoviz/panel/issues/635), [#670](https://github.com/holoviz/panel/issues/670), [#705](https://github.com/holoviz/panel/issues/705), [#708](https://github.com/holoviz/panel/issues/708), [#709](https://github.com/holoviz/panel/issues/709), [#740](https://github.com/holoviz/panel/issues/740), [#747](https://github.com/holoviz/panel/issues/747), [#752](https://github.com/holoviz/panel/issues/752))


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


## Version 0.6.2

Date: 2019-08-08T15:13:31Z

Minor bugfix release patching issues with 0.6.1, primarily in the CI setup. Also removed the not-yet-supported definition_order parameter of pn.CrossSelector.


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


## Version 0.1.3

Date: 2018-10-23T12:09:07Z
