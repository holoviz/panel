'use strict';
/*!
 * Copyright (c) Anaconda, Inc., and Bokeh Contributors
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 * 
 * Redistributions of source code must retain the above copyright notice,
 * this list of conditions and the following disclaimer.
 * 
 * Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 * 
 * Neither the name of Anaconda nor the names of any contributors
 * may be used to endorse or promote products derived from this software
 * without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
 * THE POSSIBILITY OF SUCH DAMAGE.
 */
(function(root, factory) {
  factory(root["Bokeh"], undefined);
})(this, function(Bokeh, version) {
  let define;
  return (function(modules, entry, aliases, externals) {
    const bokeh = typeof Bokeh !== "undefined" ? (version != null ? Bokeh[version] : Bokeh) : null;
    if (bokeh != null) {
      return bokeh.register_plugin(modules, entry, aliases);
    } else {
      throw new Error("Cannot find Bokeh" + (version != null ? " " + version : "") + ". You have to load it prior to loading plugins.");
    }
  })
({
"4e90918c0a": /* index.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const Panel = tslib_1.__importStar(require("38670592ce") /* ./models */);
    exports.Panel = Panel;
    const base_1 = require("@bokehjs/base");
    (0, base_1.register_models)(Panel);
},
"38670592ce": /* models/index.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    var ace_1 = require("c780fc99fd") /* ./ace */;
    __esExport("AcePlot", ace_1.AcePlot);
    var audio_1 = require("fd59c985b3") /* ./audio */;
    __esExport("Audio", audio_1.Audio);
    var browser_1 = require("85211a0a5b") /* ./browser */;
    __esExport("BrowserInfo", browser_1.BrowserInfo);
    var button_1 = require("bda381b012") /* ./button */;
    __esExport("Button", button_1.Button);
    var button_icon_1 = require("1738ddeb3a") /* ./button_icon */;
    __esExport("ButtonIcon", button_icon_1.ButtonIcon);
    var icon_1 = require("a97a38b997") /* ./icon */;
    __esExport("ClickableIcon", icon_1.ClickableIcon);
    var card_1 = require("4bed810d7e") /* ./card */;
    __esExport("Card", card_1.Card);
    var checkbox_button_group_1 = require("363b62b1db") /* ./checkbox_button_group */;
    __esExport("CheckboxButtonGroup", checkbox_button_group_1.CheckboxButtonGroup);
    var chatarea_input_1 = require("30fb939eca") /* ./chatarea_input */;
    __esExport("ChatAreaInput", chatarea_input_1.ChatAreaInput);
    var column_1 = require("879751b529") /* ./column */;
    __esExport("Column", column_1.Column);
    var comm_manager_1 = require("352943c042") /* ./comm_manager */;
    __esExport("CommManager", comm_manager_1.CommManager);
    var customselect_1 = require("92bbd30bd1") /* ./customselect */;
    __esExport("CustomSelect", customselect_1.CustomSelect);
    var tabulator_1 = require("f89f0e6802") /* ./tabulator */;
    __esExport("DataTabulator", tabulator_1.DataTabulator);
    var datetime_picker_1 = require("ddf98634bb") /* ./datetime_picker */;
    __esExport("DatetimePicker", datetime_picker_1.DatetimePicker);
    var deckgl_1 = require("dc03aab885") /* ./deckgl */;
    __esExport("DeckGLPlot", deckgl_1.DeckGLPlot);
    var echarts_1 = require("04cbffdfe0") /* ./echarts */;
    __esExport("ECharts", echarts_1.ECharts);
    var feed_1 = require("976c02c0a8") /* ./feed */;
    __esExport("Feed", feed_1.Feed);
    var file_download_1 = require("3ead851ca6") /* ./file_download */;
    __esExport("FileDownload", file_download_1.FileDownload);
    var html_1 = require("89d2d3667a") /* ./html */;
    __esExport("HTML", html_1.HTML);
    var ipywidget_1 = require("8a8089cbf3") /* ./ipywidget */;
    __esExport("IPyWidget", ipywidget_1.IPyWidget);
    var json_1 = require("7eff964d3e") /* ./json */;
    __esExport("JSON", json_1.JSON);
    var jsoneditor_1 = require("d57683bd1f") /* ./jsoneditor */;
    __esExport("JSONEditor", jsoneditor_1.JSONEditor);
    var katex_1 = require("f672d71a9f") /* ./katex */;
    __esExport("KaTeX", katex_1.KaTeX);
    var location_1 = require("bd8e0fe48b") /* ./location */;
    __esExport("Location", location_1.Location);
    var mathjax_1 = require("ec353a3d9a") /* ./mathjax */;
    __esExport("MathJax", mathjax_1.MathJax);
    var pdf_1 = require("cf33f23f5c") /* ./pdf */;
    __esExport("PDF", pdf_1.PDF);
    var perspective_1 = require("54dac9b7a1") /* ./perspective */;
    __esExport("Perspective", perspective_1.Perspective);
    var player_1 = require("f06104d237") /* ./player */;
    __esExport("Player", player_1.Player);
    var plotly_1 = require("c08950da15") /* ./plotly */;
    __esExport("PlotlyPlot", plotly_1.PlotlyPlot);
    var progress_1 = require("aded75e266") /* ./progress */;
    __esExport("Progress", progress_1.Progress);
    var quill_1 = require("c72e00086f") /* ./quill */;
    __esExport("QuillInput", quill_1.QuillInput);
    var radio_button_group_1 = require("361b5f089c") /* ./radio_button_group */;
    __esExport("RadioButtonGroup", radio_button_group_1.RadioButtonGroup);
    var reactive_html_1 = require("6cfc3f348e") /* ./reactive_html */;
    __esExport("ReactiveHTML", reactive_html_1.ReactiveHTML);
    var singleselect_1 = require("168c4d0ebd") /* ./singleselect */;
    __esExport("SingleSelect", singleselect_1.SingleSelect);
    var speech_to_text_1 = require("739cca6576") /* ./speech_to_text */;
    __esExport("SpeechToText", speech_to_text_1.SpeechToText);
    var state_1 = require("92822cb73a") /* ./state */;
    __esExport("State", state_1.State);
    var tabs_1 = require("2231cdc549") /* ./tabs */;
    __esExport("Tabs", tabs_1.Tabs);
    var terminal_1 = require("121f00bd6f") /* ./terminal */;
    __esExport("Terminal", terminal_1.Terminal);
    var textarea_input_1 = require("b7d595d74a") /* ./textarea_input */;
    __esExport("TextAreaInput", textarea_input_1.TextAreaInput);
    var text_to_speech_1 = require("a04eb51988") /* ./text_to_speech */;
    __esExport("TextToSpeech", text_to_speech_1.TextToSpeech);
    var toggle_icon_1 = require("ad985f285e") /* ./toggle_icon */;
    __esExport("ToggleIcon", toggle_icon_1.ToggleIcon);
    var tooltip_icon_1 = require("ae3a172647") /* ./tooltip_icon */;
    __esExport("TooltipIcon", tooltip_icon_1.TooltipIcon);
    var trend_1 = require("3584638c04") /* ./trend */;
    __esExport("TrendIndicator", trend_1.TrendIndicator);
    var vega_1 = require("119dc23765") /* ./vega */;
    __esExport("VegaPlot", vega_1.VegaPlot);
    var video_1 = require("79dc37b888") /* ./video */;
    __esExport("Video", video_1.Video);
    var videostream_1 = require("f8afc4e661") /* ./videostream */;
    __esExport("VideoStream", videostream_1.VideoStream);
    var vizzu_1 = require("470ce1dcbc") /* ./vizzu */;
    __esExport("VizzuChart", vizzu_1.VizzuChart);
    tslib_1.__exportStar(require("c51f25e2a7") /* ./vtk */, exports);
},
"c780fc99fd": /* models/ace.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const dom_1 = require("@bokehjs/core/dom");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    function ID() {
        // Math.random should be unique because of its seeding algorithm.
        // Convert it to base 36 (numbers + letters), and grab the first 9 characters
        // after the decimal.
        const id = Math.random().toString(36).substr(2, 9);
        return `_${id}`;
    }
    class AcePlotView extends layout_1.HTMLBoxView {
        connect_signals() {
            super.connect_signals();
            const { code, theme, language, filename, print_margin, annotations, readonly } = this.model.properties;
            this.on_change(code, () => this._update_code_from_model());
            this.on_change(theme, () => this._update_theme());
            this.on_change(language, () => this._update_language());
            this.on_change(filename, () => this._update_filename());
            this.on_change(print_margin, () => this._update_print_margin());
            this.on_change(annotations, () => this._add_annotations());
            this.on_change(readonly, () => {
                this._editor.setReadOnly(this.model.readonly);
            });
        }
        render() {
            super.render();
            this._container = (0, dom_1.div)({
                id: ID(),
                style: {
                    width: "100%",
                    height: "100%",
                    zIndex: 0,
                },
            });
            this.shadow_el.append(this._container);
            this._container.textContent = this.model.code;
            this._editor = ace.edit(this._container);
            this._editor.renderer.attachToShadowRoot();
            this._langTools = ace.require("ace/ext/language_tools");
            this._modelist = ace.require("ace/ext/modelist");
            this._editor.setOptions({
                enableBasicAutocompletion: true,
                enableSnippets: true,
                fontFamily: "monospace", //hack for cursor position
            });
            this._update_theme();
            this._update_filename();
            this._update_language();
            this._editor.setReadOnly(this.model.readonly);
            this._editor.setShowPrintMargin(this.model.print_margin);
            this._editor.on("change", () => this._update_code_from_editor());
        }
        _update_code_from_model() {
            if (this._editor && this._editor.getValue() != this.model.code) {
                this._editor.setValue(this.model.code);
            }
        }
        _update_print_margin() {
            this._editor.setShowPrintMargin(this.model.print_margin);
        }
        _update_code_from_editor() {
            if (this._editor.getValue() != this.model.code) {
                this.model.code = this._editor.getValue();
            }
        }
        _update_theme() {
            this._editor.setTheme(`ace/theme/${this.model.theme}`);
        }
        _update_filename() {
            if (this.model.filename) {
                const mode = this._modelist.getModeForPath(this.model.filename).mode;
                this.model.language = mode.slice(9);
            }
        }
        _update_language() {
            if (this.model.language != null) {
                this._editor.session.setMode(`ace/mode/${this.model.language}`);
            }
        }
        _add_annotations() {
            this._editor.session.setAnnotations(this.model.annotations);
        }
        after_layout() {
            super.after_layout();
            if (this._editor !== undefined) {
                this._editor.resize();
            }
        }
    }
    exports.AcePlotView = AcePlotView;
    AcePlotView.__name__ = "AcePlotView";
    class AcePlot extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.AcePlot = AcePlot;
    _a = AcePlot;
    AcePlot.__name__ = "AcePlot";
    AcePlot.__module__ = "panel.models.ace";
    (() => {
        _a.prototype.default_view = AcePlotView;
        _a.define(({ Any, List, Bool, Str, Nullable }) => ({
            code: [Str, ""],
            filename: [Nullable(Str), null],
            language: [Str, ""],
            theme: [Str, "chrome"],
            annotations: [List(Any), []],
            readonly: [Bool, false],
            print_margin: [Bool, false],
        }));
        _a.override({
            height: 300,
            width: 300,
        });
    })();
},
"73d6aee8f5": /* models/layout.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const dom_1 = require("@bokehjs/core/dom");
    const types_1 = require("@bokehjs/core/util/types");
    const widget_1 = require("@bokehjs/models/widgets/widget");
    const layout_dom_1 = require("@bokehjs/models/layouts/layout_dom");
    class PanelMarkupView extends widget_1.WidgetView {
        connect_signals() {
            super.connect_signals();
            const { width, height, min_height, max_height, margin, sizing_mode } = this.model.properties;
            this.on_change([width, height, min_height, max_height, margin, sizing_mode], () => {
                set_size(this.el, this.model);
                set_size(this.container, this.model, false);
            });
        }
        async lazy_initialize() {
            await super.lazy_initialize();
            if (this.provider.status == "not_started" || this.provider.status == "loading") {
                this.provider.ready.connect(() => {
                    if (this.contains_tex_string(this.model.text)) {
                        this.render();
                    }
                });
            }
        }
        watch_stylesheets() {
            this._initialized_stylesheets = {};
            for (const sts of this._applied_stylesheets) {
                const style_el = sts.el;
                if (style_el instanceof HTMLLinkElement) {
                    this._initialized_stylesheets[style_el.href] = false;
                    style_el.addEventListener("load", () => {
                        this._initialized_stylesheets[style_el.href] = true;
                        if (Object.values(this._initialized_stylesheets).every(Boolean)) {
                            this.style_redraw();
                        }
                    });
                }
            }
            if (Object.keys(this._initialized_stylesheets).length === 0) {
                this.style_redraw();
            }
        }
        style_redraw() {
        }
        has_math_disabled() {
            return this.model.disable_math || !this.contains_tex_string(this.model.text);
        }
        render() {
            super.render();
            set_size(this.el, this.model);
            this.container = (0, dom_1.div)();
            set_size(this.container, this.model, false);
            this.shadow_el.appendChild(this.container);
            if (this.provider.status == "failed" || this.provider.status == "loaded") {
                this._has_finished = true;
            }
        }
    }
    exports.PanelMarkupView = PanelMarkupView;
    PanelMarkupView.__name__ = "PanelMarkupView";
    function set_size(el, model, adjustMargin = true) {
        let width_policy = model.width != null ? "fixed" : "fit";
        let height_policy = model.height != null ? "fixed" : "fit";
        const { sizing_mode, margin } = model;
        if (sizing_mode != null) {
            if (sizing_mode == "fixed") {
                width_policy = height_policy = "fixed";
            }
            else if (sizing_mode == "stretch_both") {
                width_policy = height_policy = "max";
            }
            else if (sizing_mode == "stretch_width") {
                width_policy = "max";
            }
            else if (sizing_mode == "stretch_height") {
                height_policy = "max";
            }
            else {
                switch (sizing_mode) {
                    case "scale_width":
                        width_policy = "max";
                        height_policy = "min";
                        break;
                    case "scale_height":
                        width_policy = "min";
                        height_policy = "max";
                        break;
                    case "scale_both":
                        width_policy = "max";
                        height_policy = "max";
                        break;
                    default:
                        throw new Error("unreachable");
                }
            }
        }
        let wm, hm;
        if (!adjustMargin) {
            hm = wm = 0;
        }
        else if ((0, types_1.isArray)(margin)) {
            if (margin.length === 4) {
                hm = margin[0] + margin[2];
                wm = margin[1] + margin[3];
            }
            else {
                hm = margin[0] * 2;
                wm = margin[1] * 2;
            }
        }
        else if (margin == null) {
            hm = wm = 0;
        }
        else {
            wm = hm = margin * 2;
        }
        if (width_policy == "fixed" && model.width) {
            el.style.width = `${model.width}px`;
        }
        else if (width_policy == "max") {
            el.style.width = wm ? `calc(100% - ${wm}px)` : "100%";
        }
        if (model.min_width != null) {
            el.style.minWidth = `${model.min_width}px`;
        }
        if (model.max_width != null) {
            el.style.maxWidth = `${model.max_width}px`;
        }
        if (height_policy == "fixed" && model.height) {
            el.style.height = `${model.height}px`;
        }
        else if (height_policy == "max") {
            el.style.height = hm ? `calc(100% - ${hm}px)` : "100%";
        }
        if (model.min_height != null) {
            el.style.minHeight = `${model.min_height}px`;
        }
        if (model.max_width != null) {
            el.style.maxHeight = `${model.max_height}px`;
        }
    }
    exports.set_size = set_size;
    class HTMLBoxView extends layout_dom_1.LayoutDOMView {
        connect_signals() {
            super.connect_signals();
            const { width, height, min_height, max_height, margin, sizing_mode } = this.model.properties;
            this.on_change([width, height, min_height, max_height, margin, sizing_mode], () => {
                set_size(this.el, this.model);
            });
        }
        render() {
            super.render();
            set_size(this.el, this.model);
        }
        watch_stylesheets() {
            this._initialized_stylesheets = {};
            for (const sts of this._applied_stylesheets) {
                const style_el = sts.el;
                if (style_el instanceof HTMLLinkElement) {
                    this._initialized_stylesheets[style_el.href] = false;
                    style_el.addEventListener("load", () => {
                        this._initialized_stylesheets[style_el.href] = true;
                        if (Object.values(this._initialized_stylesheets).every(Boolean)) {
                            this.style_redraw();
                        }
                    });
                }
            }
        }
        style_redraw() {
        }
        get child_models() {
            return [];
        }
    }
    exports.HTMLBoxView = HTMLBoxView;
    HTMLBoxView.__name__ = "HTMLBoxView";
    class HTMLBox extends layout_dom_1.LayoutDOM {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.HTMLBox = HTMLBox;
    HTMLBox.__name__ = "HTMLBox";
},
"fd59c985b3": /* models/audio.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    class AudioView extends layout_1.HTMLBoxView {
        initialize() {
            super.initialize();
            this._blocked = false;
            this._setting = false;
            this._time = Date.now();
        }
        connect_signals() {
            super.connect_signals();
            const { loop, paused, time, value, volume, muted, autoplay } = this.model.properties;
            this.on_change(loop, () => this.set_loop());
            this.on_change(paused, () => this.set_paused());
            this.on_change(time, () => this.set_time());
            this.on_change(value, () => this.set_value());
            this.on_change(volume, () => this.set_volume());
            this.on_change(muted, () => this.set_muted());
            this.on_change(autoplay, () => this.set_autoplay());
        }
        render() {
            super.render();
            this.audioEl = document.createElement("audio");
            this.audioEl.controls = true;
            this.audioEl.src = this.model.value;
            this.audioEl.currentTime = this.model.time;
            this.audioEl.loop = this.model.loop;
            this.audioEl.muted = this.model.muted;
            this.audioEl.autoplay = this.model.autoplay;
            if (this.model.volume != null) {
                this.audioEl.volume = this.model.volume / 100;
            }
            else {
                this.model.volume = this.audioEl.volume * 100;
            }
            this.audioEl.onpause = () => this.model.paused = true;
            this.audioEl.onplay = () => this.model.paused = false;
            this.audioEl.ontimeupdate = () => this.update_time(this);
            this.audioEl.onvolumechange = () => this.update_volume(this);
            (0, layout_1.set_size)(this.audioEl, this.model, false);
            this.shadow_el.appendChild(this.audioEl);
            if (!this.model.paused) {
                this.audioEl.play();
            }
        }
        update_time(view) {
            if (view._setting) {
                view._setting = false;
                return;
            }
            if ((Date.now() - view._time) < view.model.throttle) {
                return;
            }
            view._blocked = true;
            view.model.time = view.audioEl.currentTime;
            view._time = Date.now();
        }
        update_volume(view) {
            if (view._setting) {
                view._setting = false;
                return;
            }
            view._blocked = true;
            view.model.volume = view.audioEl.volume * 100;
        }
        set_loop() {
            this.audioEl.loop = this.model.loop;
        }
        set_muted() {
            this.audioEl.muted = this.model.muted;
        }
        set_autoplay() {
            this.audioEl.autoplay = this.model.autoplay;
        }
        set_paused() {
            if (!this.audioEl.paused && this.model.paused) {
                this.audioEl.pause();
            }
            if (this.audioEl.paused && !this.model.paused) {
                this.audioEl.play();
            }
        }
        set_volume() {
            if (this._blocked) {
                this._blocked = false;
                return;
            }
            this._setting = true;
            if (this.model.volume != null) {
                this.audioEl.volume = this.model.volume / 100;
            }
        }
        set_time() {
            if (this._blocked) {
                this._blocked = false;
                return;
            }
            this._setting = true;
            this.audioEl.currentTime = this.model.time;
        }
        set_value() {
            this.audioEl.src = this.model.value;
        }
    }
    exports.AudioView = AudioView;
    AudioView.__name__ = "AudioView";
    class Audio extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.Audio = Audio;
    _a = Audio;
    Audio.__name__ = "Audio";
    Audio.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = AudioView;
        _a.define(({ Any, Bool, Float, Nullable }) => ({
            loop: [Bool, false],
            paused: [Bool, true],
            muted: [Bool, false],
            autoplay: [Bool, false],
            time: [Float, 0],
            throttle: [Float, 250],
            value: [Any, ""],
            volume: [Nullable(Float), null],
        }));
    })();
},
"85211a0a5b": /* models/browser.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const view_1 = require("@bokehjs/core/view");
    const model_1 = require("@bokehjs/model");
    class BrowserInfoView extends view_1.View {
        initialize() {
            super.initialize();
            if (window.matchMedia != null) {
                this.model.dark_mode = window.matchMedia("(prefers-color-scheme: dark)").matches;
            }
            this.model.device_pixel_ratio = window.devicePixelRatio;
            if (navigator != null) {
                this.model.language = navigator.language;
                this.model.webdriver = navigator.webdriver;
            }
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            if (timezone != null) {
                this.model.timezone = timezone;
            }
            const timezone_offset = new Date().getTimezoneOffset();
            if (timezone_offset != null) {
                this.model.timezone_offset = timezone_offset;
            }
            this._has_finished = true;
            this.notify_finished();
        }
    }
    exports.BrowserInfoView = BrowserInfoView;
    BrowserInfoView.__name__ = "BrowserInfoView";
    class BrowserInfo extends model_1.Model {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.BrowserInfo = BrowserInfo;
    _a = BrowserInfo;
    BrowserInfo.__name__ = "BrowserInfo";
    BrowserInfo.__module__ = "panel.models.browser";
    (() => {
        _a.prototype.default_view = BrowserInfoView;
        _a.define(({ Bool, Nullable, Float, Str }) => ({
            dark_mode: [Nullable(Bool), null],
            device_pixel_ratio: [Nullable(Float), null],
            language: [Nullable(Str), null],
            timezone: [Nullable(Str), null],
            timezone_offset: [Nullable(Float), null],
            webdriver: [Nullable(Bool), null],
        }));
    })();
},
"bda381b012": /* models/button.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tooltip_1 = require("@bokehjs/models/ui/tooltip");
    const build_views_1 = require("@bokehjs/core/build_views");
    const button_1 = require("@bokehjs/models/widgets/button");
    class ButtonView extends button_1.ButtonView {
        *children() {
            yield* super.children();
            if (this.tooltip != null) {
                yield this.tooltip;
            }
        }
        async lazy_initialize() {
            await super.lazy_initialize();
            const { tooltip } = this.model;
            if (tooltip != null) {
                this.tooltip = await (0, build_views_1.build_view)(tooltip, { parent: this });
            }
        }
        remove() {
            this.tooltip?.remove();
            super.remove();
        }
        render() {
            super.render();
            const toggle = (visible) => {
                this.tooltip?.model.setv({
                    visible,
                });
            };
            let timer;
            this.el.addEventListener("mouseenter", () => {
                timer = setTimeout(() => toggle(true), this.model.tooltip_delay);
            });
            this.el.addEventListener("mouseleave", () => {
                clearTimeout(timer);
                toggle(false);
            });
        }
    }
    exports.ButtonView = ButtonView;
    ButtonView.__name__ = "ButtonView";
    class Button extends button_1.Button {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.Button = Button;
    _a = Button;
    Button.__name__ = "Button";
    Button.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = ButtonView;
        _a.define(({ Nullable, Ref, Float }) => ({
            tooltip: [Nullable(Ref(tooltip_1.Tooltip)), null],
            tooltip_delay: [Float, 500],
        }));
    })();
},
"1738ddeb3a": /* models/button_icon.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const icon_1 = require("a97a38b997") /* ./icon */;
    class ButtonIconView extends icon_1.ClickableIconView {
        *controls() { }
        update_cursor() {
            this.icon_view.el.style.cursor = this.model.disabled ? "default" : "pointer";
        }
        click() {
            if (this.model.disabled) {
                return;
            }
            super.click();
            const updateState = (value, disabled) => {
                this.model.value = value;
                this.model.disabled = disabled;
            };
            updateState(true, true);
            new Promise(resolve => setTimeout(resolve, this.model.toggle_duration))
                .then(() => {
                updateState(false, false);
            });
        }
    }
    exports.ButtonIconView = ButtonIconView;
    ButtonIconView.__name__ = "ButtonIconView";
    class ButtonIcon extends icon_1.ClickableIcon {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.ButtonIcon = ButtonIcon;
    _a = ButtonIcon;
    ButtonIcon.__name__ = "ButtonIcon";
    ButtonIcon.__module__ = "panel.models.icon";
    (() => {
        _a.prototype.default_view = ButtonIconView;
        _a.define(({ Int }) => ({
            toggle_duration: [Int, 75],
        }));
    })();
},
"a97a38b997": /* models/icon.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tooltip_1 = require("@bokehjs/models/ui/tooltip");
    const tabler_icon_1 = require("@bokehjs/models/ui/icons/tabler_icon");
    const svg_icon_1 = require("@bokehjs/models/ui/icons/svg_icon");
    const control_1 = require("@bokehjs/models/widgets/control");
    const dom_1 = require("@bokehjs/core/dom");
    const build_views_1 = require("@bokehjs/core/build_views");
    const bokeh_events_1 = require("@bokehjs/core/bokeh_events");
    class ClickableIconView extends control_1.ControlView {
        *controls() { }
        remove() {
            this.tooltip?.remove();
            this.icon_view.remove();
            super.remove();
        }
        async lazy_initialize() {
            await super.lazy_initialize();
            this.was_svg_icon = this.is_svg_icon(this.model.icon);
            this.label_el = (0, dom_1.div)({ class: "bk-IconLabel" }, this.model.title);
            this.label_el.style.fontSize = this.calculate_size(0.6);
            this.icon_view = await this.build_icon_model(this.model.icon, this.was_svg_icon);
            const { tooltip } = this.model;
            if (tooltip != null) {
                this.tooltip = await (0, build_views_1.build_view)(tooltip, { parent: this });
            }
        }
        *children() {
            yield* super.children();
            yield this.icon_view;
            if (this.tooltip != null) {
                yield this.tooltip;
            }
        }
        is_svg_icon(icon) {
            return icon.trim().startsWith("<svg");
        }
        connect_signals() {
            super.connect_signals();
            const { icon, active_icon, disabled, value, size } = this.model.properties;
            this.on_change([active_icon, icon, value], () => this.update_icon());
            this.on_change(this.model.properties.title, () => this.update_label());
            this.on_change(disabled, () => this.update_cursor());
            this.on_change(size, () => this.update_size());
        }
        render() {
            super.render();
            this.icon_view.render();
            this.update_icon();
            this.update_label();
            this.update_cursor();
            this.row_div = (0, dom_1.div)({
                class: "bk-IconRow",
            }, this.icon_view.el, this.label_el);
            this.shadow_el.appendChild(this.row_div);
            const toggle_tooltip = (visible) => {
                this.tooltip?.model.setv({
                    visible,
                });
            };
            let timer;
            this.el.addEventListener("mouseenter", () => {
                timer = setTimeout(() => toggle_tooltip(true), this.model.tooltip_delay);
            });
            this.el.addEventListener("mouseleave", () => {
                clearTimeout(timer);
                toggle_tooltip(false);
            });
        }
        update_label() {
            this.label_el.innerText = this.model.title;
        }
        update_cursor() {
            this.icon_view.el.style.cursor = this.model.disabled ? "not-allowed" : "pointer";
        }
        update_size() {
            this.icon_view.model.size = this.calculate_size();
            this.label_el.style.fontSize = this.calculate_size(0.6);
        }
        async build_icon_model(icon, is_svg_icon) {
            const size = this.calculate_size();
            const icon_model = (() => {
                if (is_svg_icon) {
                    return new svg_icon_1.SVGIcon({ svg: icon, size });
                }
                else {
                    return new tabler_icon_1.TablerIcon({ icon_name: icon, size });
                }
            })();
            const icon_view = await (0, build_views_1.build_view)(icon_model, { parent: this });
            icon_view.el.addEventListener("click", () => this.click());
            return icon_view;
        }
        async update_icon() {
            const icon = this.model.value ? this.get_active_icon() : this.model.icon;
            this.class_list.toggle("active", this.model.value);
            const is_svg_icon = this.is_svg_icon(icon);
            if (this.was_svg_icon !== is_svg_icon) {
                // If the icon type has changed, we need to rebuild the icon view
                // and invalidate the old one.
                const icon_view = await this.build_icon_model(icon, is_svg_icon);
                icon_view.render();
                this.icon_view.remove();
                this.icon_view = icon_view;
                this.was_svg_icon = is_svg_icon;
                this.update_cursor();
                // We need to re-append the new icon view to the DOM
                this.row_div.insertBefore(this.icon_view.el, this.label_el);
            }
            else if (is_svg_icon) {
                this.icon_view.model.svg = icon;
            }
            else {
                this.icon_view.model.icon_name = icon;
            }
            this.icon_view.el.style.lineHeight = "0";
        }
        get_active_icon() {
            return this.model.active_icon !== "" ? this.model.active_icon : `${this.model.icon}-filled`;
        }
        calculate_size(factor = 1) {
            if (this.model.size !== null) {
                return `calc(${this.model.size} * ${factor})`;
            }
            const maxWidth = this.model.width ?? 15;
            const maxHeight = this.model.height ?? 15;
            const size = Math.max(maxWidth, maxHeight) * factor;
            return `${size}px`;
        }
        click() {
            this.model.trigger_event(new bokeh_events_1.ButtonClick());
        }
    }
    exports.ClickableIconView = ClickableIconView;
    ClickableIconView.__name__ = "ClickableIconView";
    class ClickableIcon extends control_1.Control {
        constructor(attrs) {
            super(attrs);
        }
        on_click(callback) {
            this.on_event(bokeh_events_1.ButtonClick, callback);
        }
    }
    exports.ClickableIcon = ClickableIcon;
    _a = ClickableIcon;
    ClickableIcon.__name__ = "ClickableIcon";
    ClickableIcon.__module__ = "panel.models.icon";
    (() => {
        _a.prototype.default_view = ClickableIconView;
        _a.define(({ Nullable, Ref, Float, Str, Bool }) => ({
            active_icon: [Str, ""],
            icon: [Str, "heart"],
            size: [Nullable(Str), null],
            value: [Bool, false],
            title: [Str, ""],
            tooltip: [Nullable(Ref(tooltip_1.Tooltip)), null],
            tooltip_delay: [Float, 500],
        }));
    })();
},
"4bed810d7e": /* models/card.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tslib_1 = require("tslib");
    const column_1 = require("879751b529") /* ./column */;
    const DOM = tslib_1.__importStar(require("@bokehjs/core/dom"));
    const card_css_1 = tslib_1.__importDefault(require("2d2b7d250a") /* ../styles/models/card.css */);
    class CardView extends column_1.ColumnView {
        constructor() {
            super(...arguments);
            this.collapsed_style = new DOM.InlineStyleSheet();
        }
        connect_signals() {
            super.connect_signals();
            const { active_header_background, collapsed, header_background, header_color, hide_header } = this.model.properties;
            this.on_change(collapsed, () => this._collapse());
            this.on_change([header_color, hide_header], () => this.render());
            this.on_change([active_header_background, collapsed, header_background], () => {
                const header_background = this.header_background;
                if (header_background == null) {
                    return;
                }
                this.child_views[0].el.style.backgroundColor = header_background;
                this.header_el.style.backgroundColor = header_background;
            });
        }
        stylesheets() {
            return [...super.stylesheets(), card_css_1.default];
        }
        *_stylesheets() {
            yield* super._stylesheets();
            yield this.collapsed_style;
        }
        get header_background() {
            let header_background = this.model.header_background;
            if (!this.model.collapsed && this.model.active_header_background) {
                header_background = this.model.active_header_background;
            }
            return header_background;
        }
        render() {
            this.empty();
            if (this.model.collapsed) {
                this.collapsed_style.replace(":host", {
                    height: "fit-content",
                    flex: "none",
                });
            }
            this._update_stylesheets();
            this._update_css_classes();
            this._apply_styles();
            this._apply_visible();
            this.class_list.add(...this.css_classes());
            const { button_css_classes, header_color, header_tag, header_css_classes } = this.model;
            const header_background = this.header_background;
            const header = this.child_views[0];
            let header_el;
            if (this.model.collapsible) {
                this.button_el = DOM.createElement("button", { type: "button", class: header_css_classes });
                const icon = DOM.createElement("div", { class: button_css_classes });
                icon.innerHTML = this.model.collapsed ? "\u25ba" : "\u25bc";
                this.button_el.appendChild(icon);
                this.button_el.style.backgroundColor = header_background != null ? header_background : "";
                header.el.style.backgroundColor = header_background != null ? header_background : "";
                this.button_el.appendChild(header.el);
                this.button_el.onclick = () => this._toggle_button();
                header_el = this.button_el;
            }
            else {
                header_el = DOM.createElement(header_tag, { class: header_css_classes });
                header_el.style.backgroundColor = header_background != null ? header_background : "";
                header_el.appendChild(header.el);
            }
            this.header_el = header_el;
            if (!this.model.hide_header) {
                header_el.style.color = header_color != null ? header_color : "";
                this.shadow_el.appendChild(header_el);
                header.render();
                header.after_render();
            }
            if (this.model.collapsed) {
                return;
            }
            for (const child_view of this.child_views.slice(1)) {
                this.shadow_el.appendChild(child_view.el);
                child_view.render();
                child_view.after_render();
            }
        }
        async update_children() {
            await this.build_child_views();
            this.render();
            this.invalidate_layout();
        }
        _toggle_button() {
            this.model.collapsed = !this.model.collapsed;
        }
        _collapse() {
            for (const child_view of this.child_views.slice(1)) {
                if (this.model.collapsed) {
                    this.shadow_el.removeChild(child_view.el);
                    child_view.model.visible = false;
                }
                else {
                    child_view.render();
                    child_view.after_render();
                    this.shadow_el.appendChild(child_view.el);
                    child_view.model.visible = true;
                }
            }
            if (this.model.collapsed) {
                this.collapsed_style.replace(":host", {
                    height: "fit-content",
                    flex: "none",
                });
            }
            else {
                this.collapsed_style.clear();
            }
            this.button_el.children[0].innerHTML = this.model.collapsed ? "\u25ba" : "\u25bc";
            this.invalidate_layout();
        }
        _createElement() {
            return DOM.createElement(this.model.tag, { class: this.css_classes() });
        }
    }
    exports.CardView = CardView;
    CardView.__name__ = "CardView";
    class Card extends column_1.Column {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.Card = Card;
    _a = Card;
    Card.__name__ = "Card";
    Card.__module__ = "panel.models.layout";
    (() => {
        _a.prototype.default_view = CardView;
        _a.define(({ List, Bool, Nullable, Str }) => ({
            active_header_background: [Nullable(Str), null],
            button_css_classes: [List(Str), []],
            collapsed: [Bool, true],
            collapsible: [Bool, true],
            header_background: [Nullable(Str), null],
            header_color: [Nullable(Str), null],
            header_css_classes: [List(Str), []],
            header_tag: [Str, "div"],
            hide_header: [Bool, false],
            tag: [Str, "div"],
        }));
    })();
},
"879751b529": /* models/column.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tslib_1 = require("tslib");
    const column_1 = require("@bokehjs/models/layouts/column");
    const DOM = tslib_1.__importStar(require("@bokehjs/core/dom"));
    class ColumnView extends column_1.ColumnView {
        connect_signals() {
            super.connect_signals();
            const { children, scroll_position, scroll_button_threshold } = this.model.properties;
            this.on_change(children, () => this.trigger_auto_scroll());
            this.on_change(scroll_position, () => this.scroll_to_position());
            this.on_change(scroll_button_threshold, () => this.toggle_scroll_button());
        }
        get distance_from_latest() {
            return this.el.scrollHeight - this.el.scrollTop - this.el.clientHeight;
        }
        scroll_to_position() {
            requestAnimationFrame(() => {
                this.el.scrollTo({ top: this.model.scroll_position, behavior: "instant" });
            });
        }
        scroll_to_latest() {
            // Waits for the child to be rendered before scrolling
            requestAnimationFrame(() => {
                this.model.scroll_position = Math.round(this.el.scrollHeight);
            });
        }
        trigger_auto_scroll() {
            const limit = this.model.auto_scroll_limit;
            const within_limit = this.distance_from_latest <= limit;
            if (limit == 0 || !within_limit) {
                return;
            }
            this.scroll_to_latest();
        }
        record_scroll_position() {
            this.model.scroll_position = Math.round(this.el.scrollTop);
        }
        toggle_scroll_button() {
            const threshold = this.model.scroll_button_threshold;
            const exceeds_threshold = this.distance_from_latest >= threshold;
            if (this.scroll_down_button_el) {
                this.scroll_down_button_el.classList.toggle("visible", threshold !== 0 && exceeds_threshold);
            }
        }
        render() {
            super.render();
            this.scroll_down_button_el = DOM.createElement("div", { class: "scroll-button" });
            this.shadow_el.appendChild(this.scroll_down_button_el);
            this.el.addEventListener("scroll", () => {
                this.record_scroll_position();
                this.toggle_scroll_button();
            });
            this.scroll_down_button_el.addEventListener("click", () => {
                this.scroll_to_latest();
            });
        }
        after_render() {
            super.after_render();
            requestAnimationFrame(() => {
                if (this.model.scroll_position) {
                    this.scroll_to_position();
                }
                if (this.model.view_latest) {
                    this.scroll_to_latest();
                }
                this.toggle_scroll_button();
            });
        }
    }
    exports.ColumnView = ColumnView;
    ColumnView.__name__ = "ColumnView";
    class Column extends column_1.Column {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.Column = Column;
    _a = Column;
    Column.__name__ = "Column";
    Column.__module__ = "panel.models.layout";
    (() => {
        _a.prototype.default_view = ColumnView;
        _a.define(({ Int, Bool }) => ({
            scroll_position: [Int, 0],
            auto_scroll_limit: [Int, 0],
            scroll_button_threshold: [Int, 0],
            view_latest: [Bool, false],
        }));
    })();
},
"2d2b7d250a": /* styles/models/card.css.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    exports.default = `:host(.card){border-radius:0.25rem;box-shadow:rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px;flex:auto;outline:1px solid rgba(0, 0, 0, 0.125);}:host(.accordion){box-shadow:rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px;outline:1px solid rgba(0, 0, 0, 0.125);width:100%;}.card-header{align-items:center;background-color:rgba(0, 0, 0, 0.03);border:unset;border-radius:0.25rem;display:inline-flex;justify-content:start;left:0;outline:unset;position:sticky;width:100%;}.accordion-header{align-items:center;background-color:rgba(0, 0, 0, 0.03);border:unset;outline:1px solid;border-radius:0;display:flex;justify-content:start;position:sticky;left:0;width:100%;}.card-button{background-color:transparent;margin-left:0.5em;margin-right:0.5em;}.card-header-row{margin-left:auto 1em;position:relative !important;max-width:calc(100% - 2em);}.card-title{align-items:center;font-size:1.4em;font-weight:bold;overflow-wrap:break-word;}.card-header-row > .bk{overflow-wrap:break-word;text-align:center;}`;
},
"363b62b1db": /* models/checkbox_button_group.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tooltip_1 = require("@bokehjs/models/ui/tooltip");
    const build_views_1 = require("@bokehjs/core/build_views");
    const checkbox_button_group_1 = require("@bokehjs/models/widgets/checkbox_button_group");
    class CheckboxButtonGroupView extends checkbox_button_group_1.CheckboxButtonGroupView {
        *children() {
            yield* super.children();
            if (this.tooltip != null) {
                yield this.tooltip;
            }
        }
        async lazy_initialize() {
            await super.lazy_initialize();
            const { tooltip } = this.model;
            if (tooltip != null) {
                this.tooltip = await (0, build_views_1.build_view)(tooltip, { parent: this });
            }
        }
        remove() {
            this.tooltip?.remove();
            super.remove();
        }
        render() {
            super.render();
            const toggle = (visible) => {
                this.tooltip?.model.setv({
                    visible,
                });
            };
            let timer;
            this.el.addEventListener("mouseenter", () => {
                timer = setTimeout(() => toggle(true), this.model.tooltip_delay);
            });
            this.el.addEventListener("mouseleave", () => {
                clearTimeout(timer);
                toggle(false);
            });
        }
    }
    exports.CheckboxButtonGroupView = CheckboxButtonGroupView;
    CheckboxButtonGroupView.__name__ = "CheckboxButtonGroupView";
    class CheckboxButtonGroup extends checkbox_button_group_1.CheckboxButtonGroup {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.CheckboxButtonGroup = CheckboxButtonGroup;
    _a = CheckboxButtonGroup;
    CheckboxButtonGroup.__name__ = "CheckboxButtonGroup";
    CheckboxButtonGroup.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = CheckboxButtonGroupView;
        _a.define(({ Nullable, Ref, Float }) => ({
            tooltip: [Nullable(Ref(tooltip_1.Tooltip)), null],
            tooltip_delay: [Float, 500],
        }));
    })();
},
"30fb939eca": /* models/chatarea_input.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a, _b;
    __esModule();
    const textarea_input_1 = require("b7d595d74a") /* ./textarea_input */;
    const bokeh_events_1 = require("@bokehjs/core/bokeh_events");
    class ChatMessageEvent extends bokeh_events_1.ModelEvent {
        constructor(value) {
            super();
            this.value = value;
        }
        get event_values() {
            return { model: this.origin, value: this.value };
        }
    }
    exports.ChatMessageEvent = ChatMessageEvent;
    _a = ChatMessageEvent;
    ChatMessageEvent.__name__ = "ChatMessageEvent";
    (() => {
        _a.prototype.event_name = "chat_message_event";
    })();
    class ChatAreaInputView extends textarea_input_1.TextAreaInputView {
        connect_signals() {
            super.connect_signals();
            const { value_input } = this.model.properties;
            this.on_change(value_input, () => this.update_rows());
        }
        render() {
            super.render();
            this.el.addEventListener("keydown", (event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                    if (!this.model.disabled_enter) {
                        this.model.trigger_event(new ChatMessageEvent(this.model.value_input));
                        this.model.value_input = "";
                    }
                    event.preventDefault();
                }
            });
        }
    }
    exports.ChatAreaInputView = ChatAreaInputView;
    ChatAreaInputView.__name__ = "ChatAreaInputView";
    class ChatAreaInput extends textarea_input_1.TextAreaInput {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.ChatAreaInput = ChatAreaInput;
    _b = ChatAreaInput;
    ChatAreaInput.__name__ = "ChatAreaInput";
    ChatAreaInput.__module__ = "panel.models.chatarea_input";
    (() => {
        _b.prototype.default_view = ChatAreaInputView;
        _b.define(({ Bool }) => {
            return {
                disabled_enter: [Bool, false],
            };
        });
    })();
},
"b7d595d74a": /* models/textarea_input.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const textarea_input_1 = require("@bokehjs/models/widgets/textarea_input");
    class TextAreaInputView extends textarea_input_1.TextAreaInputView {
        connect_signals() {
            super.connect_signals();
            const { value, max_rows } = this.model.properties;
            this.on_change([max_rows, value], () => this.update_rows());
        }
        update_rows() {
            if (!this.model.auto_grow) {
                return;
            }
            // Use this.el directly to access the textarea element
            const textarea = this.input_el;
            const textLines = textarea.value.split("\n");
            const numRows = Math.max(textLines.length, this.model.rows, 1);
            textarea.rows = Math.min(numRows, this.model.max_rows || Infinity);
        }
        render() {
            super.render();
            this.update_rows();
            this.el.addEventListener("input", () => {
                this.update_rows();
            });
        }
    }
    exports.TextAreaInputView = TextAreaInputView;
    TextAreaInputView.__name__ = "TextAreaInputView";
    class TextAreaInput extends textarea_input_1.TextAreaInput {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.TextAreaInput = TextAreaInput;
    _a = TextAreaInput;
    TextAreaInput.__name__ = "TextAreaInput";
    TextAreaInput.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = TextAreaInputView;
        _a.define(({ Bool, Int, Nullable }) => ({
            auto_grow: [Bool, false],
            max_rows: [Nullable(Int), null],
        }));
    })();
},
"352943c042": /* models/comm_manager.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const document_1 = require("@bokehjs/document");
    const view_1 = require("@bokehjs/core/view");
    const model_1 = require("@bokehjs/model");
    const message_1 = require("@bokehjs/protocol/message");
    const receiver_1 = require("@bokehjs/protocol/receiver");
    exports.comm_settings = {
        debounce: true,
    };
    class CommManagerView extends view_1.View {
    }
    exports.CommManagerView = CommManagerView;
    CommManagerView.__name__ = "CommManagerView";
    class CommManager extends model_1.Model {
        constructor(attrs) {
            super(attrs);
            this._document_listener = (event) => this._document_changed(event);
        }
        initialize() {
            super.initialize();
            this._receiver = new receiver_1.Receiver();
            this._event_buffer = [];
            this._blocked = false;
            this._timeout = Date.now();
            if ((window.PyViz == undefined) || (!window.PyViz.comm_manager)) {
                console.log("Could not find comm manager on window.PyViz, ensure the extension is loaded.");
            }
            else {
                this.ns = window.PyViz;
                this.ns.comm_manager.register_target(this.plot_id, this.comm_id, (msg) => {
                    for (const view of this.ns.shared_views.get(this.plot_id)) {
                        if (view !== this) {
                            view.msg_handler(msg);
                        }
                    }
                    try {
                        this.msg_handler(msg);
                    }
                    catch (e) {
                        console.error(e);
                    }
                });
                this._client_comm = this.ns.comm_manager.get_client_comm(this.plot_id, this.client_comm_id, (msg) => this.on_ack(msg));
                if (this.ns.shared_views == null) {
                    this.ns.shared_views = new Map();
                }
                if (this.ns.shared_views.has(this.plot_id)) {
                    this.ns.shared_views.get(this.plot_id).push(this);
                }
                else {
                    this.ns.shared_views.set(this.plot_id, [this]);
                }
            }
        }
        _doc_attached() {
            super._doc_attached();
            if (this.document != null) {
                this.document.on_change(this._document_listener);
            }
        }
        _document_changed(event) {
            // Filter out changes to attributes that aren't server-visible
            if (event instanceof document_1.ModelChangedEvent && !event.model.properties[event.attr].syncable) {
                return;
            }
            this._event_buffer.push(event);
            if (!exports.comm_settings.debounce) {
                this.process_events();
            }
            else if ((!this._blocked || (Date.now() > this._timeout))) {
                setTimeout(() => this.process_events(), this.debounce);
                this._blocked = true;
                this._timeout = Date.now() + this.timeout;
            }
        }
        _extract_buffers(value, buffers) {
            let extracted;
            if (value instanceof Array) {
                extracted = [];
                for (const val of value) {
                    extracted.push(this._extract_buffers(val, buffers));
                }
            }
            else if (value instanceof Object) {
                extracted = {};
                for (const key in value) {
                    if (key === "buffer" && value[key] instanceof ArrayBuffer) {
                        const id = Object.keys(buffers).length;
                        extracted = { id };
                        buffers.push(value[key]);
                        break;
                    }
                    extracted[key] = this._extract_buffers(value[key], buffers);
                }
            }
            else {
                extracted = value;
            }
            return extracted;
        }
        process_events() {
            if ((this.document == null) || (this._client_comm == null)) {
                return;
            }
            const patch = this.document.create_json_patch(this._event_buffer);
            this._event_buffer = [];
            const message = { ...message_1.Message.create("PATCH-DOC", {}, patch) };
            const buffers = [];
            message.content = this._extract_buffers(message.content, buffers);
            this._client_comm.send(message, {}, buffers);
            for (const view of this.ns.shared_views.get(this.plot_id)) {
                if (view !== this && view.document != null) {
                    view.document.apply_json_patch(patch, [], this.id);
                }
            }
        }
        disconnect_signals() {
            super.disconnect_signals();
            this.ns.shared_views.shared_views.delete(this.plot_id);
        }
        on_ack(msg) {
            // Receives acknowledgement from Python, processing event
            // and unblocking Comm if event queue empty
            const metadata = msg.metadata;
            if (this._event_buffer.length > 0) {
                this._blocked = true;
                this._timeout = Date.now() + this.timeout;
                this.process_events();
            }
            else {
                this._blocked = false;
            }
            if ((metadata.msg_type == "Ready") && metadata.content) {
                console.log("Python callback returned following output:", metadata.content);
            }
            else if (metadata.msg_type == "Error") {
                console.log("Python failed with the following traceback:", metadata.traceback);
            }
        }
        msg_handler(msg) {
            const metadata = msg.metadata;
            const buffers = msg.buffers;
            const content = msg.content.data;
            const plot_id = this.plot_id;
            if ((metadata.msg_type == "Ready")) {
                if (metadata.content) {
                    console.log("Python callback returned following output:", metadata.content);
                }
                else if (metadata.msg_type == "Error") {
                    console.log("Python failed with the following traceback:", metadata.traceback);
                }
            }
            else if (plot_id != null) {
                let plot = null;
                if ((plot_id in this.ns.plot_index) && (this.ns.plot_index[plot_id] != null)) {
                    plot = this.ns.plot_index[plot_id];
                }
                else if ((window.Bokeh !== undefined) && (plot_id in window.Bokeh.index)) {
                    plot = window.Bokeh.index[plot_id];
                }
                if (plot == null) {
                    return;
                }
                if (content.length) {
                    this._receiver.consume(content);
                }
                else if ((buffers != undefined) && (buffers.length > 0)) {
                    this._receiver.consume(buffers[0].buffer);
                }
                else {
                    return;
                }
                const comm_msg = this._receiver.message;
                if ((comm_msg != null) && (Object.keys(comm_msg.content).length > 0) && this.document != null) {
                    const patch = comm_msg.content;
                    this.document.apply_json_patch(patch, comm_msg.buffers);
                }
            }
        }
    }
    exports.CommManager = CommManager;
    _a = CommManager;
    CommManager.__name__ = "CommManager";
    CommManager.__module__ = "panel.models.comm_manager";
    (() => {
        _a.prototype.default_view = CommManagerView;
        _a.define(({ Int, Str, Nullable }) => ({
            plot_id: [Nullable(Str), null],
            comm_id: [Nullable(Str), null],
            client_comm_id: [Nullable(Str), null],
            timeout: [Int, 5000],
            debounce: [Int, 50],
        }));
    })();
},
"92bbd30bd1": /* models/customselect.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const select_1 = require("@bokehjs/models/widgets/select");
    class CustomSelectView extends select_1.SelectView {
        connect_signals() {
            super.connect_signals();
            const { disabled_options } = this.model.properties;
            this.on_change(disabled_options, () => this._update_disabled_options());
        }
        options_el() {
            const opts = super.options_el();
            const { disabled_options } = this.model;
            opts.forEach((element) => {
                // XXX: what about HTMLOptGroupElement?
                if (element instanceof HTMLOptionElement && disabled_options.includes(element.value)) {
                    element.setAttribute("disabled", "true");
                }
            });
            return opts;
        }
        _update_disabled_options() {
            for (const element of this.input_el.options) {
                if (this.model.disabled_options.includes(element.value)) {
                    element.setAttribute("disabled", "true");
                }
                else {
                    element.removeAttribute("disabled");
                }
            }
        }
    }
    exports.CustomSelectView = CustomSelectView;
    CustomSelectView.__name__ = "CustomSelectView";
    class CustomSelect extends select_1.Select {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.CustomSelect = CustomSelect;
    _a = CustomSelect;
    CustomSelect.__name__ = "CustomSelect";
    CustomSelect.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = CustomSelectView;
        _a.define(({ List, Str }) => {
            return {
                disabled_options: [List(Str), []],
            };
        });
    })();
},
"f89f0e6802": /* models/tabulator.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a, _b, _c, _d;
    __esModule();
    const dom_1 = require("@bokehjs/core/dom");
    const types_1 = require("@bokehjs/core/util/types");
    const bokeh_events_1 = require("@bokehjs/core/bokeh_events");
    const dom_2 = require("@bokehjs/core/dom");
    const kinds_1 = require("@bokehjs/core/kinds");
    const column_data_source_1 = require("@bokehjs/models/sources/column_data_source");
    const tables_1 = require("@bokehjs/models/widgets/tables");
    const debounce_1 = require("99a25e6992") /* debounce */;
    const comm_manager_1 = require("352943c042") /* ./comm_manager */;
    const data_1 = require("be689f0377") /* ./data */;
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    class TableEditEvent extends bokeh_events_1.ModelEvent {
        constructor(column, row, pre) {
            super();
            this.column = column;
            this.row = row;
            this.pre = pre;
        }
        get event_values() {
            return { model: this.origin, column: this.column, row: this.row, pre: this.pre };
        }
    }
    exports.TableEditEvent = TableEditEvent;
    _a = TableEditEvent;
    TableEditEvent.__name__ = "TableEditEvent";
    (() => {
        _a.prototype.event_name = "table-edit";
    })();
    class CellClickEvent extends bokeh_events_1.ModelEvent {
        constructor(column, row) {
            super();
            this.column = column;
            this.row = row;
        }
        get event_values() {
            return { model: this.origin, column: this.column, row: this.row };
        }
    }
    exports.CellClickEvent = CellClickEvent;
    _b = CellClickEvent;
    CellClickEvent.__name__ = "CellClickEvent";
    (() => {
        _b.prototype.event_name = "cell-click";
    })();
    class SelectionEvent extends bokeh_events_1.ModelEvent {
        constructor(indices, selected, flush = false) {
            super();
            this.indices = indices;
            this.selected = selected;
            this.flush = flush;
        }
        get event_values() {
            return { model: this.origin, indices: this.indices, selected: this.selected, flush: this.flush };
        }
    }
    exports.SelectionEvent = SelectionEvent;
    _c = SelectionEvent;
    SelectionEvent.__name__ = "SelectionEvent";
    (() => {
        _c.prototype.event_name = "selection-change";
    })();
    function find_group(key, value, records) {
        for (const record of records) {
            if (record[key] == value) {
                return record;
            }
        }
        return null;
    }
    function summarize(grouped, columns, aggregators, depth = 0) {
        const summary = {};
        if (grouped.length == 0) {
            return summary;
        }
        const agg = aggregators[depth];
        for (const group of grouped) {
            const subsummary = summarize(group._children, columns, aggregators, depth + 1);
            for (const col in subsummary) {
                if ((0, types_1.isArray)(subsummary[col])) {
                    group[col] = subsummary[col].reduce((a, b) => a + b, 0) / subsummary[col].length;
                }
                else {
                    group[col] = subsummary[col];
                }
            }
            for (const column of columns.slice(1)) {
                const val = group[column.field];
                if (column.field in summary) {
                    const old_val = summary[column.field];
                    if (agg === "min") {
                        summary[column.field] = Math.min(val, old_val);
                    }
                    else if (agg === "max") {
                        summary[column.field] = Math.max(val, old_val);
                    }
                    else if (agg === "sum") {
                        summary[column.field] = val + old_val;
                    }
                    else if (agg === "mean") {
                        if ((0, types_1.isArray)(summary[column.field])) {
                            summary[column.field].push(val);
                        }
                        else {
                            summary[column.field] = [old_val, val];
                        }
                    }
                }
                else {
                    summary[column.field] = val;
                }
            }
        }
        return summary;
    }
    function group_data(records, columns, indexes, aggregators) {
        const grouped = [];
        const index_field = columns[0].field;
        for (const record of records) {
            const value = record[indexes[0]];
            let group = find_group(index_field, value, grouped);
            if (group == null) {
                group = { _children: [] };
                group[index_field] = value;
                grouped.push(group);
            }
            let subgroup = group;
            const groups = {};
            for (const index of indexes.slice(1)) {
                subgroup = find_group(index_field, record[index], subgroup._children);
                if (subgroup == null) {
                    subgroup = { _children: [] };
                    subgroup[index_field] = record[index];
                    group._children.push(subgroup);
                }
                groups[index] = group;
                for (const column of columns.slice(1)) {
                    subgroup[column.field] = record[column];
                }
                group = subgroup;
            }
            for (const column of columns.slice(1)) {
                subgroup[column.field] = record[column.field];
            }
        }
        const aggs = [];
        for (const index of indexes) {
            aggs.push((index in aggregators) ? aggregators[index] : "sum");
        }
        summarize(grouped, columns, aggs);
        return grouped;
    }
    const timestampSorter = function (a, b, _aRow, _bRow, _column, _dir, _params) {
        // Bokeh serializes datetime objects as UNIX timestamps.
        //a, b - the two values being compared
        //aRow, bRow - the row components for the values being compared (useful if you need to access additional fields in the row data for the sort)
        //column - the column component for the column being sorted
        //dir - the direction of the sort ("asc" or "desc")
        //sorterParams - sorterParams object from column definition array
        // Added an _ in front of some parameters as they're unused and the Typescript compiler was complaining about it.
        // const alignEmptyValues = params.alignEmptyValues
        let emptyAlign;
        emptyAlign = 0;
        const opts = { zone: new window.luxon.IANAZone("UTC") };
        // NaN values are serialized to -9223372036854776 by Bokeh
        if (String(a) == "-9223372036854776") {
            a = window.luxon.DateTime.fromISO("invalid");
        }
        else {
            a = window.luxon.DateTime.fromMillis(a, opts);
        }
        if (String(b) == "-9223372036854776") {
            b = window.luxon.DateTime.fromISO("invalid");
        }
        else {
            b = window.luxon.DateTime.fromMillis(b, opts);
        }
        if (!a.isValid) {
            emptyAlign = !b.isValid ? 0 : -1;
        }
        else if (!b.isValid) {
            emptyAlign = 1;
        }
        else {
            //compare valid values
            return a - b;
        }
        // Invalid (e.g. NaN) always at the bottom
        emptyAlign *= -1;
        return emptyAlign;
    };
    const dateEditor = function (cell, onRendered, success, cancel) {
        //cell - the cell component for the editable cell
        //onRendered - function to call when the editor has been rendered
        //success - function to call to pass the successfully updated value to Tabulator
        //cancel - function to call to abort the edit and return to a normal cell
        //create and style input
        const rawValue = cell.getValue();
        const opts = { zone: new window.luxon.IANAZone("UTC") };
        let cellValue;
        if (rawValue === "NaN" || rawValue === null) {
            cellValue = null;
        }
        else {
            cellValue = window.luxon.DateTime.fromMillis(rawValue, opts).toFormat("yyyy-MM-dd");
        }
        const input = document.createElement("input");
        input.setAttribute("type", "date");
        input.style.padding = "4px";
        input.style.width = "100%";
        input.style.boxSizing = "border-box";
        input.value = cellValue;
        onRendered(() => {
            input.focus();
            input.style.height = "100%";
        });
        function onChange() {
            const new_val = window.luxon.DateTime.fromFormat(input.value, "yyyy-MM-dd", opts).toMillis();
            if (new_val != cellValue) {
                success(new_val);
            }
            else {
                cancel();
            }
        }
        //submit new value on blur or change
        input.addEventListener("blur", onChange);
        //submit new value on enter
        input.addEventListener("keydown", (e) => {
            if (e.key == "Enter") {
                setTimeout(onChange, 100);
            }
            if (e.key == "Escape") {
                setTimeout(cancel, 100);
            }
        });
        return input;
    };
    const datetimeEditor = function (cell, onRendered, success, cancel) {
        //cell - the cell component for the editable cell
        //onRendered - function to call when the editor has been rendered
        //success - function to call to pass the successfully updated value to Tabulator
        //cancel - function to call to abort the edit and return to a normal cell
        //create and style input
        const rawValue = cell.getValue();
        const opts = { zone: new window.luxon.IANAZone("UTC") };
        let cellValue;
        if (rawValue === "NaN" || rawValue === null) {
            cellValue = null;
        }
        else {
            cellValue = window.luxon.DateTime.fromMillis(rawValue, opts).toFormat("yyyy-MM-dd'T'T");
        }
        const input = document.createElement("input");
        input.setAttribute("type", "datetime-local");
        input.style.padding = "4px";
        input.style.width = "100%";
        input.style.boxSizing = "border-box";
        input.value = cellValue;
        onRendered(() => {
            input.focus();
            input.style.height = "100%";
        });
        function onChange() {
            const new_val = window.luxon.DateTime.fromFormat(input.value, "yyyy-MM-dd'T'T", opts).toMillis();
            if (new_val != cellValue) {
                success(new_val);
            }
            else {
                cancel();
            }
        }
        //submit new value on blur or change
        input.addEventListener("blur", onChange);
        //submit new value on enter
        input.addEventListener("keydown", (e) => {
            if (e.key == "Enter") {
                setTimeout(onChange, 100);
            }
            if (e.key == "Escape") {
                setTimeout(cancel, 100);
            }
        });
        return input;
    };
    class DataTabulatorView extends layout_1.HTMLBoxView {
        constructor() {
            super(...arguments);
            this.columns = new Map();
            this._tabulator_cell_updating = false;
            this._updating_page = false;
            this._updating_sort = false;
            this._selection_updating = false;
            this._lastVerticalScrollbarTopPosition = 0;
            this._lastHorizontalScrollbarLeftPosition = 0;
            this._applied_styles = false;
            this._building = false;
            this._restore_scroll = false;
        }
        connect_signals() {
            super.connect_signals();
            const { configuration, layout, columns, groupby, visible, download, children, expanded, cell_styles, hidden_columns, page_size, page, max_page, frozen_rows, sorters, theme_classes, } = this.model.properties;
            this.on_change([configuration, layout, groupby], (0, debounce_1.debounce)(() => {
                this.invalidate_render();
            }, 20, false));
            this.on_change(visible, () => {
                if (this.model.visible) {
                    this.tabulator.element.style.visibility = "visible";
                }
            });
            this.on_change(columns, () => {
                this.tabulator.setColumns(this.getColumns());
                this.setHidden();
            });
            this.on_change(download, () => {
                const ftype = this.model.filename.endsWith(".json") ? "json" : "csv";
                this.tabulator.download(ftype, this.model.filename);
            });
            this.on_change(children, () => this.renderChildren());
            this.on_change(expanded, () => {
                // The first cell is the cell of the frozen _index column.
                for (const row of this.tabulator.rowManager.getRows()) {
                    if (row.cells.length > 0) {
                        row.cells[0].layoutElement();
                    }
                }
                // Make sure the expand icon is changed when expanded is
                // changed from Python.
                for (const row of this.tabulator.rowManager.getRows()) {
                    if (row.cells.length > 0) {
                        const index = row.data._index;
                        const icon = this.model.expanded.indexOf(index) < 0 ? "►" : "▼";
                        row.cells[1].element.innerText = icon;
                    }
                }
            });
            this.on_change(cell_styles, () => {
                if (this._applied_styles) {
                    this.tabulator.redraw(true);
                }
                this.setStyles();
            });
            this.on_change(hidden_columns, () => {
                this.setHidden();
                this.tabulator.redraw(true);
            });
            this.on_change(page_size, () => this.setPageSize());
            this.on_change(page, () => {
                if (!this._updating_page) {
                    this.setPage();
                }
            });
            this.on_change(visible, () => this.setVisibility());
            this.on_change(max_page, () => this.setMaxPage());
            this.on_change(frozen_rows, () => this.setFrozen());
            this.on_change(sorters, () => this.setSorters());
            this.on_change(theme_classes, () => this.setCSSClasses(this.tabulator.element));
            this.on_change(this.model.source.properties.data, () => {
                if (this.tabulator === undefined) {
                    return;
                }
                this._selection_updating = true;
                this.setData();
                this._selection_updating = false;
                this.postUpdate();
            });
            this.connect(this.model.source.streaming, () => this.addData());
            this.connect(this.model.source.patching, () => {
                const inds = this.model.source.selected.indices;
                this.updateOrAddData();
                this.record_scroll();
                // Restore indices since updating data may have reset checkbox column
                this.model.source.selected.indices = inds;
            });
            this.connect(this.model.source.selected.change, () => this.setSelection());
            this.connect(this.model.source.selected.properties.indices.change, () => this.setSelection());
        }
        get groupBy() {
            const groupby = (data) => {
                const groups = [];
                for (const g of this.model.groupby) {
                    const group = `${g}: ${data[g]}`;
                    groups.push(group);
                }
                return groups.join(", ");
            };
            return (this.model.groupby.length > 0) ? groupby : false;
        }
        get sorters() {
            const sorters = [];
            if (this.model.sorters.length > 0) {
                sorters.push({ column: "_index", dir: "asc" });
            }
            for (const sort of this.model.sorters.reverse()) {
                if (sort.column === undefined) {
                    sort.column = sort.field;
                }
                sorters.push(sort);
            }
            return sorters;
        }
        invalidate_render() {
            this.tabulator.destroy();
            this.tabulator = null;
            this.render();
        }
        redraw(columns = true, rows = true) {
            if (this._building) {
                return;
            }
            if (columns && (this.tabulator.columnManager.element != null)) {
                this.tabulator.columnManager.redraw(true);
            }
            if (rows && (this.tabulator.rowManager.renderer != null)) {
                this.tabulator.rowManager.redraw(true);
                this.renderChildren();
                this.setStyles();
            }
            this._restore_scroll = true;
        }
        after_layout() {
            super.after_layout();
            if (this.tabulator != null && this._initializing) {
                this.redraw();
            }
            this._initializing = false;
        }
        after_resize() {
            super.after_resize();
            this.redraw(false, true);
        }
        setCSSClasses(el) {
            el.className = "pnx-tabulator tabulator";
            for (const cls of this.model.theme_classes) {
                el.classList.add(cls);
            }
        }
        render() {
            if (this.tabulator != null) {
                this.tabulator.destroy();
            }
            super.render();
            this._initializing = true;
            const container = (0, dom_2.div)({ style: "display: contents;" });
            const el = (0, dom_2.div)({ style: "width: 100%; height: 100%; visibility: hidden;" });
            this.setCSSClasses(el);
            container.appendChild(el);
            this.shadow_el.appendChild(container);
            const configuration = this.getConfiguration();
            this.tabulator = new Tabulator(el, configuration);
            this.watch_stylesheets();
            this.init_callbacks();
        }
        style_redraw() {
            if (this.model.visible) {
                this.tabulator.element.style.visibility = "visible";
            }
            if (!this._initializing && !this._building) {
                this.redraw();
            }
        }
        tableInit() {
            this._building = true;
            // Patch the ajax request and page data parsing methods
            const ajax = this.tabulator.modules.ajax;
            ajax.sendRequest = (_url, params, _config) => {
                return this.requestPage(params.page, params.sort);
            };
            this.tabulator.modules.page._parseRemoteData = () => {
                return false;
            };
        }
        init_callbacks() {
            // Initialization
            this.tabulator.on("tableBuilding", () => this.tableInit());
            this.tabulator.on("tableBuilt", () => this.tableBuilt());
            // Rendering callbacks
            this.tabulator.on("selectableCheck", (row) => {
                const selectable = this.model.selectable_rows;
                return (selectable == null) || selectable.includes(row._row.data._index);
            });
            this.tabulator.on("tooltips", (cell) => {
                return `${cell.getColumn().getField()}: ${cell.getValue()}`;
            });
            this.tabulator.on("scrollVertical", (0, debounce_1.debounce)(() => {
                this.record_scroll();
                this.setStyles();
            }, 50, false));
            this.tabulator.on("scrollHorizontal", (0, debounce_1.debounce)(() => {
                this.record_scroll();
            }, 50, false));
            // Sync state with model
            this.tabulator.on("rowSelectionChanged", (data, rows, selected, deselected) => this.rowSelectionChanged(data, rows, selected, deselected));
            this.tabulator.on("rowClick", (e, row) => this.rowClicked(e, row));
            this.tabulator.on("cellEdited", (cell) => this.cellEdited(cell));
            this.tabulator.on("dataFiltering", (filters) => {
                this.record_scroll();
                this.model.filters = filters;
            });
            this.tabulator.on("dataFiltered", (_, rows) => {
                if (this._building) {
                    return;
                }
                // Ensure that after filtering empty scroll renders
                if (rows.length === 0) {
                    this.tabulator.rowManager.renderEmptyScroll();
                }
                // Ensure that after filtering the page is updated
                this.updatePage(this.tabulator.getPage());
            });
            this.tabulator.on("pageLoaded", (pageno) => {
                this.updatePage(pageno);
            });
            this.tabulator.on("renderComplete", () => {
                if (this._building) {
                    return;
                }
                this.postUpdate();
            });
            this.tabulator.on("dataSorting", (sorters) => {
                const sorts = [];
                for (const s of sorters) {
                    if (s.field !== "_index") {
                        sorts.push({ field: s.field, dir: s.dir });
                    }
                }
                if (this.model.pagination !== "remote") {
                    this._updating_sort = true;
                    this.model.sorters = sorts;
                    this._updating_sort = false;
                }
            });
        }
        tableBuilt() {
            this._building = false;
            this.setSelection();
            this.renderChildren();
            this.setStyles();
            if (this.model.pagination) {
                this.setMaxPage();
                this.tabulator.setPage(this.model.page);
            }
        }
        requestPage(page, sorters) {
            return new Promise((resolve, reject) => {
                try {
                    if (page != null && sorters != null) {
                        this._updating_sort = true;
                        const sorts = [];
                        for (const s of sorters) {
                            if (s.field !== "_index") {
                                sorts.push({ field: s.field, dir: s.dir });
                            }
                        }
                        this.model.sorters = sorts;
                        this._updating_sort = false;
                        this._updating_page = true;
                        try {
                            this.model.page = page || 1;
                        }
                        finally {
                            this._updating_page = false;
                        }
                    }
                    resolve([]);
                }
                catch (err) {
                    reject(err);
                }
            });
        }
        getLayout() {
            const layout = this.model.layout;
            switch (layout) {
                case "fit_data":
                    return "fitData";
                case "fit_data_fill":
                    return "fitDataFill";
                case "fit_data_stretch":
                    return "fitDataStretch";
                case "fit_data_table":
                    return "fitDataTable";
                case "fit_columns":
                    return "fitColumns";
            }
        }
        getConfiguration() {
            // Only use selectable mode if explicitly requested otherwise manually handle selections
            const selectable = this.model.select_mode === "toggle" ? true : NaN;
            const configuration = {
                ...this.model.configuration,
                index: "_index",
                nestedFieldSeparator: false,
                movableColumns: false,
                selectable,
                columns: this.getColumns(),
                initialSort: this.sorters,
                layout: this.getLayout(),
                pagination: this.model.pagination != null,
                paginationMode: this.model.pagination,
                paginationSize: this.model.page_size,
                paginationInitialPage: 1,
                groupBy: this.groupBy,
                rowFormatter: (row) => this._render_row(row),
                frozenRows: (row) => {
                    return (this.model.frozen_rows.length > 0) ? this.model.frozen_rows.includes(row._row.data._index) : false;
                },
            };
            if (this.model.pagination === "remote") {
                configuration.ajaxURL = "http://panel.pyviz.org";
                configuration.sortMode = "remote";
            }
            const cds = this.model.source;
            let data;
            if (cds === null || (cds.columns().length === 0)) {
                data = [];
            }
            else {
                data = (0, data_1.transform_cds_to_records)(cds, true);
            }
            if (configuration.dataTree) {
                data = group_data(data, this.model.columns, this.model.indexes, this.model.aggregators);
            }
            return {
                ...configuration,
                data,
            };
        }
        get child_models() {
            const children = [];
            for (const idx of this.model.expanded) {
                const child = this.model.children.get(idx);
                if (child != null) {
                    children.push(child);
                }
            }
            return children;
        }
        renderChildren() {
            new Promise(async (resolve) => {
                await this.build_child_views();
                resolve(null);
            }).then(() => {
                for (const r of this.model.expanded) {
                    const row = this.tabulator.getRow(r);
                    this._render_row(row, false);
                }
                this._update_children();
                if (this.tabulator.rowManager.renderer != null) {
                    this.tabulator.rowManager.adjustTableSize();
                }
                this.invalidate_layout();
            });
        }
        _render_row(row, resize = true) {
            const index = row._row?.data._index;
            if (!this.model.expanded.includes(index) || this.model.children.get(index) == null) {
                return;
            }
            const model = this.model.children.get(index);
            const view = model == null ? null : this._child_views.get(model);
            if (view == null) {
                return;
            }
            const rowEl = row.getElement();
            const style = getComputedStyle(this.tabulator.element.children[1].children[0]);
            const bg = style.backgroundColor;
            const neg_margin = rowEl.style.paddingLeft ? `-${rowEl.style.paddingLeft}` : "0";
            const viewEl = (0, dom_2.div)({ style: `background-color: ${bg}; margin-left:${neg_margin}; max-width: 100%; overflow-x: hidden;` });
            viewEl.appendChild(view.el);
            rowEl.appendChild(viewEl);
            if (!view.has_finished()) {
                view.render();
                view.after_render();
            }
            if (resize) {
                this._update_children();
                this.tabulator.rowManager.adjustTableSize();
                this.invalidate_layout();
            }
        }
        _expand_render(cell) {
            const index = cell._cell.row.data._index;
            const icon = this.model.expanded.indexOf(index) < 0 ? "►" : "▼";
            return `<i>${icon}</i>`;
        }
        _update_expand(cell) {
            const index = cell._cell.row.data._index;
            const expanded = [...this.model.expanded];
            const exp_index = expanded.indexOf(index);
            if (exp_index < 0) {
                expanded.push(index);
            }
            else {
                const removed = expanded.splice(exp_index, 1)[0];
                const model = this.model.children.get(removed);
                if (model != null) {
                    const view = this._child_views.get(model);
                    if (view !== undefined && view.el != null) {
                        (0, dom_1.undisplay)(view.el);
                    }
                }
            }
            this.model.expanded = expanded;
            if (expanded.indexOf(index) < 0) {
                return;
            }
            let ready = true;
            for (const idx of this.model.expanded) {
                if (this.model.children.get(idx) == null) {
                    ready = false;
                    break;
                }
            }
            if (ready) {
                this.renderChildren();
            }
        }
        getData() {
            let data = (0, data_1.transform_cds_to_records)(this.model.source, true);
            if (this.model.configuration.dataTree) {
                data = group_data(data, this.model.columns, this.model.indexes, this.model.aggregators);
            }
            return data;
        }
        getColumns() {
            this.columns = new Map();
            const config_columns = this.model.configuration?.columns;
            const columns = [];
            columns.push({ field: "_index", frozen: true, visible: false });
            if (config_columns != null) {
                for (const column of config_columns) {
                    if (column.columns != null) {
                        const group_columns = [];
                        for (const col of column.columns) {
                            group_columns.push({ ...col });
                        }
                        columns.push({ ...column, columns: group_columns });
                    }
                    else if (column.formatter === "expand") {
                        const expand = {
                            hozAlign: "center",
                            cellClick: (_, cell) => {
                                this._update_expand(cell);
                            },
                            formatter: (cell) => {
                                return this._expand_render(cell);
                            },
                            width: 40,
                            frozen: true,
                        };
                        columns.push(expand);
                    }
                    else {
                        const new_column = { ...column };
                        if (new_column.formatter === "rowSelection") {
                            new_column.cellClick = (_, cell) => {
                                cell.getRow().toggleSelect();
                            };
                        }
                        columns.push(new_column);
                    }
                }
            }
            for (const column of this.model.columns) {
                let tab_column = null;
                if (config_columns != null) {
                    for (const col of columns) {
                        if (col.columns != null) {
                            for (const c of col.columns) {
                                if (column.field === c.field) {
                                    tab_column = c;
                                    break;
                                }
                            }
                            if (tab_column != null) {
                                break;
                            }
                        }
                        else if (column.field === col.field) {
                            tab_column = col;
                            break;
                        }
                    }
                }
                if (tab_column == null) {
                    tab_column = { field: column.field };
                }
                this.columns.set(column.field, tab_column);
                if (tab_column.title == null) {
                    tab_column.title = column.title;
                }
                if (tab_column.width == null && column.width != null && column.width != 0) {
                    tab_column.width = column.width;
                }
                if (tab_column.formatter == null && column.formatter != null) {
                    const formatter = column.formatter;
                    const ftype = formatter.type;
                    if (ftype === "BooleanFormatter") {
                        tab_column.formatter = "tickCross";
                    }
                    else {
                        tab_column.formatter = (cell) => {
                            const formatted = column.formatter.doFormat(cell.getRow(), cell, cell.getValue(), null, null);
                            if (column.formatter.type === "HTMLTemplateFormatter") {
                                return formatted;
                            }
                            const node = (0, dom_2.div)();
                            node.innerHTML = formatted;
                            const child = node.children[0];
                            if (child.innerHTML === "function(){return c.convert(arguments)}") { // If the formatter fails
                                return "";
                            }
                            return child;
                        };
                    }
                }
                if (tab_column.sorter == "timestamp") {
                    tab_column.sorter = timestampSorter;
                }
                if (tab_column.sorter === undefined) {
                    tab_column.sorter = "string";
                }
                const editor = column.editor;
                const ctype = editor.type;
                if (tab_column.editor != null) {
                    if (tab_column.editor === "date") {
                        tab_column.editor = dateEditor;
                    }
                    else if (tab_column.editor === "datetime") {
                        tab_column.editor = datetimeEditor;
                    }
                }
                else if (ctype === "StringEditor") {
                    if (editor.completions.length > 0) {
                        tab_column.editor = "list";
                        tab_column.editorParams = { values: editor.completions, autocomplete: true, listOnEmpty: true };
                    }
                    else {
                        tab_column.editor = "input";
                    }
                }
                else if (ctype === "TextEditor") {
                    tab_column.editor = "textarea";
                }
                else if (ctype === "IntEditor" || ctype === "NumberEditor") {
                    tab_column.editor = "number";
                    tab_column.editorParams = { step: editor.step };
                    if (ctype === "IntEditor") {
                        tab_column.validator = "integer";
                    }
                    else {
                        tab_column.validator = "numeric";
                    }
                }
                else if (ctype === "CheckboxEditor") {
                    tab_column.editor = "tickCross";
                }
                else if (ctype === "DateEditor") {
                    tab_column.editor = dateEditor;
                }
                else if (ctype === "SelectEditor") {
                    tab_column.editor = "list";
                    tab_column.editorParams = { values: editor.options };
                }
                else if (editor != null && editor.default_view != null) {
                    tab_column.editor = (cell, onRendered, success, cancel) => {
                        this.renderEditor(column, cell, onRendered, success, cancel);
                    };
                }
                tab_column.visible = (tab_column.visible != false && !this.model.hidden_columns.includes(column.field));
                tab_column.editable = () => (this.model.editable && (editor.default_view != null));
                if (tab_column.headerFilter) {
                    if ((0, types_1.isBoolean)(tab_column.headerFilter) && (0, types_1.isString)(tab_column.editor)) {
                        tab_column.headerFilter = tab_column.editor;
                        tab_column.headerFilterParams = tab_column.editorParams;
                    }
                }
                for (const sort of this.model.sorters) {
                    if (tab_column.field === sort.field) {
                        tab_column.headerSortStartingDir = sort.dir;
                    }
                }
                tab_column.cellClick = (_, cell) => {
                    const index = cell.getData()._index;
                    const event = new CellClickEvent(column.field, index);
                    this.model.trigger_event(event);
                };
                if (config_columns == null) {
                    columns.push(tab_column);
                }
            }
            for (const col in this.model.buttons) {
                const button_formatter = () => {
                    return this.model.buttons[col];
                };
                const button_column = {
                    formatter: button_formatter,
                    hozAlign: "center",
                    cellClick: (_, cell) => {
                        const index = cell.getData()._index;
                        const event = new CellClickEvent(col, index);
                        this.model.trigger_event(event);
                    },
                };
                columns.push(button_column);
            }
            return columns;
        }
        renderEditor(column, cell, onRendered, success, cancel) {
            const editor = column.editor;
            const view = new editor.default_view({ column, model: editor, parent: this, container: cell._cell.element });
            view.initialize();
            view.connect_signals();
            onRendered(() => {
                view.setValue(cell.getValue());
            });
            view.inputEl.addEventListener("input", () => {
                const value = view.serializeValue();
                const old_value = cell.getValue();
                const validation = view.validate();
                if (!validation.valid) {
                    cancel(validation.msg);
                }
                if (old_value != null && typeof value != typeof old_value) {
                    cancel("Mismatching type");
                }
                else {
                    success(view.serializeValue());
                }
            });
            return view.inputEl;
        }
        // Update table
        setData() {
            if (this._initializing || this._building || !this.tabulator.initialized) {
                return;
            }
            const data = this.getData();
            if (this.model.pagination != null) {
                this.tabulator.rowManager.setData(data, true, false);
            }
            else {
                this.tabulator.setData(data);
            }
        }
        addData() {
            const rows = this.tabulator.rowManager.getRows();
            const last_row = rows[rows.length - 1];
            const start = ((last_row?.data._index) || 0);
            this.setData();
            if (this.model.follow && last_row) {
                this.tabulator.scrollToRow(start, "top", false);
            }
        }
        postUpdate() {
            this.setSelection();
            this.setStyles();
            if (this._restore_scroll) {
                this.restore_scroll();
                this._restore_scroll = false;
            }
        }
        updateOrAddData() {
            // To avoid double updating the tabulator data
            if (this._tabulator_cell_updating) {
                return;
            }
            // Temporarily set minHeight to avoid "scroll-to-top" issues caused
            // by Tabulator JS entirely destroying the table when .setData is called.
            // Inspired by https://github.com/olifolkerd/tabulator/issues/4155
            const prev_minheight = this.tabulator.element.style.minHeight;
            this.tabulator.element.style.minHeight = `${this.tabulator.element.offsetHeight}px`;
            const data = (0, data_1.transform_cds_to_records)(this.model.source, true);
            this.tabulator.setData(data).then(() => {
                this.tabulator.element.style.minHeight = prev_minheight;
            });
        }
        setFrozen() {
            for (const row of this.model.frozen_rows) {
                this.tabulator.getRow(row).freeze();
            }
        }
        setVisibility() {
            if (this.tabulator == null) {
                return;
            }
            this.tabulator.element.style.visibility = this.model.visible ? "visible" : "hidden";
        }
        updatePage(pageno) {
            if (this.model.pagination === "local" && this.model.page !== pageno) {
                this._updating_page = true;
                this.model.page = pageno;
                this._updating_page = false;
                this.setStyles();
            }
        }
        setGroupBy() {
            this.tabulator.setGroupBy(this.groupBy);
        }
        setSorters() {
            if (this._updating_sort) {
                return;
            }
            this.tabulator.setSort(this.sorters);
        }
        setStyles() {
            const style_data = this.model.cell_styles.data;
            if (this.tabulator == null || this.tabulator.getDataCount() == 0 || style_data == null || !style_data.size) {
                return;
            }
            this._applied_styles = false;
            for (const r of style_data.keys()) {
                const row_style = style_data.get(r);
                const row = this.tabulator.getRow(r);
                if (!row) {
                    continue;
                }
                const cells = row._row.cells;
                for (const c of row_style.keys()) {
                    const style = row_style.get(c);
                    const cell = cells[c];
                    if (cell == null || !style.length) {
                        continue;
                    }
                    const element = cell.element;
                    for (const s of style) {
                        let prop, value;
                        if ((0, types_1.isArray)(s)) {
                            [prop, value] = s;
                        }
                        else if (!s.includes(":")) {
                            continue;
                        }
                        else {
                            [prop, value] = s.split(":");
                        }
                        element.style.setProperty(prop, value.trimLeft());
                        this._applied_styles = true;
                    }
                }
            }
        }
        setHidden() {
            for (const column of this.tabulator.getColumns()) {
                const col = column._column;
                if ((col.field == "_index") || this.model.hidden_columns.includes(col.field)) {
                    column.hide();
                }
                else {
                    column.show();
                }
            }
        }
        setMaxPage() {
            this.tabulator.setMaxPage(this.model.max_page);
            if (this.tabulator.modules.page.pagesElement) {
                this.tabulator.modules.page._setPageButtons();
            }
        }
        setPage() {
            this.tabulator.setPage(Math.min(this.model.max_page, this.model.page));
            if (this.model.pagination === "local") {
                this.renderChildren();
                this.setStyles();
            }
        }
        setPageSize() {
            this.tabulator.setPageSize(this.model.page_size);
            if (this.model.pagination === "local") {
                this.renderChildren();
                this.setStyles();
            }
        }
        setSelection() {
            if (this.tabulator == null || this._initializing || this._selection_updating || !this.tabulator.initialized) {
                return;
            }
            const indices = this.model.source.selected.indices;
            const current_indices = this.tabulator.getSelectedData().map((row) => row._index);
            if (JSON.stringify(indices) == JSON.stringify(current_indices)) {
                return;
            }
            this._selection_updating = true;
            this.tabulator.deselectRow();
            this.tabulator.selectRow(indices);
            for (const index of indices) {
                const row = this.tabulator.rowManager.findRow(index);
                if (row) {
                    this.tabulator.scrollToRow(index, "center", false).catch(() => { });
                }
            }
            this._selection_updating = false;
        }
        restore_scroll() {
            const opts = {
                top: this._lastVerticalScrollbarTopPosition,
                left: this._lastHorizontalScrollbarLeftPosition,
                behavior: "instant",
            };
            setTimeout(() => this.tabulator.rowManager.element.scrollTo(opts), 0);
        }
        // Update model
        record_scroll() {
            this._lastVerticalScrollbarTopPosition = this.tabulator.rowManager.element.scrollTop;
            this._lastHorizontalScrollbarLeftPosition = this.tabulator.rowManager.element.scrollLeft;
        }
        rowClicked(e, row) {
            if (this._selection_updating ||
                this._initializing ||
                (0, types_1.isString)(this.model.select_mode) ||
                this.model.select_mode === false || // selection disabled
                this.model.configuration.dataTree || // dataTree does not support selection
                e.srcElement?.innerText === "►" // expand button
            ) {
                return;
            }
            let indices = [];
            const selected = this.model.source.selected;
            const index = row._row.data._index;
            if (this.model.pagination === "remote") {
                const includes = this.model.source.selected.indices.indexOf(index) == -1;
                const flush = !(e.ctrlKey || e.metaKey || e.shiftKey);
                if (e.shiftKey && selected.indices.length) {
                    const start = selected.indices[selected.indices.length - 1];
                    if (index > start) {
                        for (let i = start; i <= index; i++) {
                            indices.push(i);
                        }
                    }
                    else {
                        for (let i = start; i >= index; i--) {
                            indices.push(i);
                        }
                    }
                }
                else {
                    indices.push(index);
                }
                this._selection_updating = true;
                this.model.trigger_event(new SelectionEvent(indices, includes, flush));
                this._selection_updating = false;
                return;
            }
            if (e.ctrlKey || e.metaKey) {
                indices = [...this.model.source.selected.indices];
            }
            else if (e.shiftKey && selected.indices.length) {
                const start = selected.indices[selected.indices.length - 1];
                if (index > start) {
                    for (let i = start; i < index; i++) {
                        indices.push(i);
                    }
                }
                else {
                    for (let i = start; i > index; i--) {
                        indices.push(i);
                    }
                }
            }
            if (indices.indexOf(index) < 0) {
                indices.push(index);
            }
            else {
                indices.splice(indices.indexOf(index), 1);
            }
            // Remove the first selected indices when selectable is an int.
            if ((0, types_1.isNumber)(this.model.select_mode)) {
                while (indices.length > this.model.select_mode) {
                    indices.shift();
                }
            }
            const filtered = this._filter_selected(indices);
            this.tabulator.deselectRow();
            this.tabulator.selectRow(filtered);
            this._selection_updating = true;
            selected.indices = filtered;
            this._selection_updating = false;
        }
        _filter_selected(indices) {
            const filtered = [];
            for (const ind of indices) {
                if (this.model.selectable_rows == null ||
                    this.model.selectable_rows.indexOf(ind) >= 0) {
                    filtered.push(ind);
                }
            }
            return filtered;
        }
        rowSelectionChanged(data, _row, selected, deselected) {
            if (this._selection_updating ||
                this._initializing ||
                (0, types_1.isBoolean)(this.model.select_mode) ||
                (0, types_1.isNumber)(this.model.select_mode) ||
                this.model.configuration.dataTree) {
                return;
            }
            if (this.model.pagination === "remote") {
                const selected_indices = selected.map((x) => x._row.data._index);
                const deselected_indices = deselected.map((x) => x._row.data._index);
                if (selected_indices.length > 0) {
                    this._selection_updating = true;
                    this.model.trigger_event(new SelectionEvent(selected_indices, true, false));
                }
                if (deselected_indices.length > 0) {
                    this._selection_updating = true;
                    this.model.trigger_event(new SelectionEvent(deselected_indices, false, false));
                }
            }
            else {
                const indices = data.map((row) => row._index);
                const filtered = this._filter_selected(indices);
                this._selection_updating = indices.length === filtered.length;
                this.model.source.selected.indices = filtered;
            }
            this._selection_updating = false;
        }
        cellEdited(cell) {
            const field = cell._cell.column.field;
            const column_def = this.columns.get(field);
            const index = cell.getData()._index;
            const value = cell._cell.value;
            if (column_def.validator === "numeric" && value === "") {
                cell.setValue(NaN, true);
                return;
            }
            this._tabulator_cell_updating = true;
            comm_manager_1.comm_settings.debounce = false;
            this.model.trigger_event(new TableEditEvent(field, index, true));
            try {
                this.model.source.patch({ [field]: [[index, value]] });
            }
            finally {
                comm_manager_1.comm_settings.debounce = true;
                this._tabulator_cell_updating = false;
            }
            this.model.trigger_event(new TableEditEvent(field, index, false));
            this.tabulator.scrollToRow(index, "top", false);
        }
    }
    exports.DataTabulatorView = DataTabulatorView;
    DataTabulatorView.__name__ = "DataTabulatorView";
    exports.TableLayout = (0, kinds_1.Enum)("fit_data", "fit_data_fill", "fit_data_stretch", "fit_data_table", "fit_columns");
    // The Bokeh .ts model corresponding to the Bokeh .py model
    class DataTabulator extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.DataTabulator = DataTabulator;
    _d = DataTabulator;
    DataTabulator.__name__ = "DataTabulator";
    DataTabulator.__module__ = "panel.models.tabulator";
    (() => {
        _d.prototype.default_view = DataTabulatorView;
        _d.define(({ Any, List, Bool, Nullable, Float, Ref, Str }) => ({
            aggregators: [Any, {}],
            buttons: [Any, {}],
            children: [Any, new Map()],
            configuration: [Any, {}],
            columns: [List(Ref(tables_1.TableColumn)), []],
            download: [Bool, false],
            editable: [Bool, true],
            expanded: [List(Float), []],
            filename: [Str, "table.csv"],
            filters: [List(Any), []],
            follow: [Bool, true],
            frozen_rows: [List(Float), []],
            groupby: [List(Str), []],
            hidden_columns: [List(Str), []],
            indexes: [List(Str), []],
            layout: [exports.TableLayout, "fit_data"],
            max_page: [Float, 0],
            pagination: [Nullable(Str), null],
            page: [Float, 0],
            page_size: [Float, 0],
            select_mode: [Any, true],
            selectable_rows: [Nullable(List(Float)), null],
            source: [Ref(column_data_source_1.ColumnDataSource)],
            sorters: [List(Any), []],
            cell_styles: [Any, {}],
            theme_classes: [List(Str), []],
        }));
    })();
},
"99a25e6992": /* debounce/index.js */ function _(require, module, exports, __esModule, __esExport) {
    /**
     * Returns a function, that, as long as it continues to be invoked, will not
     * be triggered. The function will be called after it stops being called for
     * N milliseconds. If `immediate` is passed, trigger the function on the
     * leading edge, instead of the trailing. The function also has a property 'clear'
     * that is a function which will clear the timer to prevent previously scheduled executions.
     *
     * @source underscore.js
     * @see http://unscriptable.com/2009/03/20/debouncing-javascript-methods/
     * @param {Function} function to wrap
     * @param {Number} timeout in ms (`100`)
     * @param {Boolean} whether to execute at the beginning (`false`)
     * @api public
     */
    function debounce(func, wait, immediate) {
        var timeout, args, context, timestamp, result;
        if (null == wait)
            wait = 100;
        function later() {
            var last = Date.now() - timestamp;
            if (last < wait && last >= 0) {
                timeout = setTimeout(later, wait - last);
            }
            else {
                timeout = null;
                if (!immediate) {
                    result = func.apply(context, args);
                    context = args = null;
                }
            }
        }
        ;
        var debounced = function () {
            context = this;
            args = arguments;
            timestamp = Date.now();
            var callNow = immediate && !timeout;
            if (!timeout)
                timeout = setTimeout(later, wait);
            if (callNow) {
                result = func.apply(context, args);
                context = args = null;
            }
            return result;
        };
        debounced.clear = function () {
            if (timeout) {
                clearTimeout(timeout);
                timeout = null;
            }
        };
        debounced.flush = function () {
            if (timeout) {
                result = func.apply(context, args);
                context = args = null;
                clearTimeout(timeout);
                timeout = null;
            }
        };
        return debounced;
    }
    ;
    // Adds compatibility for ES modules
    debounce.debounce = debounce;
    module.exports = debounce;
},
"be689f0377": /* models/data.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const types_1 = require("@bokehjs/core/util/types");
    function transform_cds_to_records(cds, addId = false, start = 0) {
        const data = [];
        const columns = cds.columns();
        const cdsLength = cds.get_length();
        if (columns.length === 0 || cdsLength === null) {
            return [];
        }
        for (let i = start; i < cdsLength; i++) {
            const item = {};
            for (const column of columns) {
                const array = cds.get_array(column);
                const shape = (array[0] == null || array[0].shape == null) ? null : array[0].shape;
                if (shape != null && shape.length > 1 && (0, types_1.isNumber)(shape[0])) {
                    item[column] = array.slice(i * shape[1], i * shape[1] + shape[1]);
                }
                else if (array.length != cdsLength && (array.length % cdsLength === 0)) {
                    const offset = array.length / cdsLength;
                    item[column] = array.slice(i * offset, i * offset + offset);
                }
                else {
                    item[column] = array[i];
                }
            }
            if (addId) {
                item._index = i;
            }
            data.push(item);
        }
        return data;
    }
    exports.transform_cds_to_records = transform_cds_to_records;
    function dict_to_records(data, index = true) {
        const records = [];
        for (let i = 0; i < data.index.length; i++) {
            const record = {};
            for (const col of data) {
                if (index || col !== "index") {
                    record[col] = data[col][i];
                }
            }
        }
        return records;
    }
    exports.dict_to_records = dict_to_records;
},
"ddf98634bb": /* models/datetime_picker.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tslib_1 = require("tslib");
    const flatpickr_1 = tslib_1.__importDefault(require("1156ddcec2") /* flatpickr */);
    const input_widget_1 = require("@bokehjs/models/widgets/input_widget");
    const dom_1 = require("@bokehjs/core/dom");
    const enums_1 = require("@bokehjs/core/enums");
    const types_1 = require("@bokehjs/core/util/types");
    const inputs = tslib_1.__importStar(require("@bokehjs/styles/widgets/inputs.css"));
    const flatpickr_css_1 = tslib_1.__importDefault(require("@bokehjs/styles/widgets/flatpickr.css"));
    function _convert_date_list(value) {
        const result = [];
        for (const item of value) {
            if ((0, types_1.isString)(item)) {
                result.push(item);
            }
            else {
                const [from, to] = item;
                result.push({ from, to });
            }
        }
        return result;
    }
    class DatetimePickerView extends input_widget_1.InputWidgetView {
        connect_signals() {
            super.connect_signals();
            const { value, min_date, max_date, disabled_dates, enabled_dates, inline, enable_time, enable_seconds, military_time, date_format, mode, } = this.model.properties;
            this.on_change(value, () => this.model.value ? this._picker?.setDate(this.model.value) : this._clear());
            this.on_change(min_date, () => this._picker?.set("minDate", this.model.min_date));
            this.on_change(max_date, () => this._picker?.set("maxDate", this.model.max_date));
            this.on_change(disabled_dates, () => {
                const { disabled_dates } = this.model;
                this._picker?.set("disable", disabled_dates != null ? _convert_date_list(disabled_dates) : []);
            });
            this.on_change(enabled_dates, () => {
                const { enabled_dates } = this.model;
                if (enabled_dates != null) {
                    this._picker?.set("enable", _convert_date_list(enabled_dates));
                }
                else {
                    // this reimplements `set()` for the `undefined` case
                    if (this._picker) {
                        this._picker.config._enable = undefined;
                        this._picker.redraw();
                        this._picker.updateValue(true);
                    }
                }
            });
            this.on_change(inline, () => this._picker?.set("inline", this.model.inline));
            this.on_change(enable_time, () => this._picker?.set("enableTime", this.model.enable_time));
            this.on_change(enable_seconds, () => this._picker?.set("enableSeconds", this.model.enable_seconds));
            this.on_change(military_time, () => this._picker?.set("time_24hr", this.model.military_time));
            this.on_change(mode, () => this._picker?.set("mode", this.model.mode));
            this.on_change(date_format, () => this._picker?.set("dateFormat", this.model.date_format));
        }
        remove() {
            this._picker?.destroy();
            super.remove();
        }
        stylesheets() {
            return [...super.stylesheets(), flatpickr_css_1.default];
        }
        _render_input() {
            return this.input_el = (0, dom_1.input)({ type: "text", class: inputs.input, disabled: this.model.disabled });
        }
        render() {
            if (this._picker != null) {
                return;
            }
            super.render();
            const options = {
                appendTo: this.group_el,
                positionElement: this.input_el,
                defaultDate: this.model.value,
                inline: this.model.inline,
                position: this._position.bind(this),
                enableTime: this.model.enable_time,
                enableSeconds: this.model.enable_seconds,
                time_24hr: this.model.military_time,
                dateFormat: this.model.date_format,
                mode: this.model.mode,
                onClose: (selected_dates, date_string, instance) => this._on_close(selected_dates, date_string, instance),
            };
            const { min_date, max_date, disabled_dates, enabled_dates } = this.model;
            if (min_date != null) {
                options.minDate = min_date;
            }
            if (max_date != null) {
                options.maxDate = max_date;
            }
            if (disabled_dates != null) {
                options.disable = _convert_date_list(disabled_dates);
            }
            if (enabled_dates != null) {
                options.enable = _convert_date_list(enabled_dates);
            }
            this._picker = (0, flatpickr_1.default)(this.input_el, options);
            this._picker.maxDateHasTime = true;
            this._picker.minDateHasTime = true;
        }
        _clear() {
            this._picker?.clear();
            this.model.value = null;
        }
        _on_close(_selected_dates, date_string, _instance) {
            if (this.model.mode == "range" && !date_string.includes("to")) {
                return;
            }
            this.model.value = date_string;
            this.change_input();
        }
        _position(self, custom_el) {
            // This function is copied directly from bokehs date_picker
            const positionElement = custom_el ?? self._positionElement;
            const calendarHeight = [...self.calendarContainer.children].reduce((acc, child) => acc + (0, dom_1.bounding_box)(child).height, 0);
            const calendarWidth = self.calendarContainer.offsetWidth;
            const configPos = this.model.position.split(" ");
            const configPosVertical = configPos[0];
            const configPosHorizontal = configPos.length > 1 ? configPos[1] : null;
            // const inputBounds = positionElement.getBoundingClientRect()
            const inputBounds = {
                top: positionElement.offsetTop,
                bottom: positionElement.offsetTop + positionElement.offsetHeight,
                left: positionElement.offsetLeft,
                right: positionElement.offsetLeft + positionElement.offsetWidth,
                width: positionElement.offsetWidth,
            };
            const distanceFromBottom = window.innerHeight - inputBounds.bottom;
            const showOnTop = configPosVertical === "above" ||
                (configPosVertical !== "below" &&
                    distanceFromBottom < calendarHeight &&
                    inputBounds.top > calendarHeight);
            // const top =
            //   window.scrollY +
            //   inputBounds.top +
            //   (!showOnTop ? positionElement.offsetHeight + 2 : -calendarHeight - 2)
            const top = self.config.appendTo
                ? inputBounds.top +
                    (!showOnTop ? positionElement.offsetHeight + 2 : -calendarHeight - 2)
                : window.scrollY +
                    inputBounds.top +
                    (!showOnTop ? positionElement.offsetHeight + 2 : -calendarHeight - 2);
            self.calendarContainer.classList.toggle("arrowTop", !showOnTop);
            self.calendarContainer.classList.toggle("arrowBottom", showOnTop);
            if (self.config.inline) {
                return;
            }
            let left = window.scrollX + inputBounds.left;
            let isCenter = false;
            let isRight = false;
            if (configPosHorizontal === "center") {
                left -= (calendarWidth - inputBounds.width) / 2;
                isCenter = true;
            }
            else if (configPosHorizontal === "right") {
                left -= calendarWidth - inputBounds.width;
                isRight = true;
            }
            self.calendarContainer.classList.toggle("arrowLeft", !isCenter && !isRight);
            self.calendarContainer.classList.toggle("arrowCenter", isCenter);
            self.calendarContainer.classList.toggle("arrowRight", isRight);
            const right = window.document.body.offsetWidth -
                (window.scrollX + inputBounds.right);
            const rightMost = left + calendarWidth > window.document.body.offsetWidth;
            const centerMost = right + calendarWidth > window.document.body.offsetWidth;
            self.calendarContainer.classList.toggle("rightMost", rightMost);
            if (self.config.static) {
                return;
            }
            self.calendarContainer.style.top = `${top}px`;
            if (!rightMost) {
                self.calendarContainer.style.left = `${left}px`;
                self.calendarContainer.style.right = "auto";
            }
            else if (!centerMost) {
                self.calendarContainer.style.left = "auto";
                self.calendarContainer.style.right = `${right}px`;
            }
            else {
                const css = this.shadow_el.styleSheets[0];
                const bodyWidth = window.document.body.offsetWidth;
                const centerLeft = Math.max(0, bodyWidth / 2 - calendarWidth / 2);
                const centerBefore = ".flatpickr-calendar.centerMost:before";
                const centerAfter = ".flatpickr-calendar.centerMost:after";
                const centerIndex = css.cssRules.length;
                const centerStyle = `{left:${inputBounds.left}px;right:auto;}`;
                self.calendarContainer.classList.toggle("rightMost", false);
                self.calendarContainer.classList.toggle("centerMost", true);
                css.insertRule(`${centerBefore},${centerAfter}${centerStyle}`, centerIndex);
                self.calendarContainer.style.left = `${centerLeft}px`;
                self.calendarContainer.style.right = "auto";
            }
        }
    }
    exports.DatetimePickerView = DatetimePickerView;
    DatetimePickerView.__name__ = "DatetimePickerView";
    class DatetimePicker extends input_widget_1.InputWidget {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.DatetimePicker = DatetimePicker;
    _a = DatetimePicker;
    DatetimePicker.__name__ = "DatetimePicker";
    DatetimePicker.__module__ = "panel.models.datetime_picker";
    (() => {
        _a.prototype.default_view = DatetimePickerView;
        _a.define(({ Bool, Str, List, Tuple, Or, Nullable }) => {
            const DateStr = Str;
            const DatesList = List(Or(DateStr, Tuple(DateStr, DateStr)));
            return {
                value: [Nullable(Str), null],
                min_date: [Nullable(Str), null],
                max_date: [Nullable(Str), null],
                disabled_dates: [Nullable(DatesList), null],
                enabled_dates: [Nullable(DatesList), null],
                position: [enums_1.CalendarPosition, "auto"],
                inline: [Bool, false],
                enable_time: [Bool, true],
                enable_seconds: [Bool, true],
                military_time: [Bool, true],
                date_format: [Str, "Y-m-d H:i:S"],
                mode: [Str, "single"],
            };
        });
    })();
},
"1156ddcec2": /* flatpickr/dist/esm/index.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    var __assign = (this && this.__assign) || function () {
        __assign = Object.assign || function (t) {
            for (var s, i = 1, n = arguments.length; i < n; i++) {
                s = arguments[i];
                for (var p in s)
                    if (Object.prototype.hasOwnProperty.call(s, p))
                        t[p] = s[p];
            }
            return t;
        };
        return __assign.apply(this, arguments);
    };
    var __spreadArrays = (this && this.__spreadArrays) || function () {
        for (var s = 0, i = 0, il = arguments.length; i < il; i++)
            s += arguments[i].length;
        for (var r = Array(s), k = 0, i = 0; i < il; i++)
            for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
                r[k] = a[j];
        return r;
    };
    const options_1 = require("651d495396") /* ./types/options */;
    const default_1 = tslib_1.__importDefault(require("3bfa124fda") /* ./l10n/default */);
    const utils_1 = require("15458073ce") /* ./utils */;
    const dom_1 = require("6b6749c6cf") /* ./utils/dom */;
    const dates_1 = require("1bb8c967d1") /* ./utils/dates */;
    const formatting_1 = require("3d14787c35") /* ./utils/formatting */;
    require("6f45019dc1") /* ./utils/polyfills */;
    var DEBOUNCED_CHANGE_MS = 300;
    function FlatpickrInstance(element, instanceConfig) {
        var self = {
            config: __assign(__assign({}, options_1.defaults), flatpickr.defaultConfig),
            l10n: default_1.default,
        };
        self.parseDate = (0, dates_1.createDateParser)({ config: self.config, l10n: self.l10n });
        self._handlers = [];
        self.pluginElements = [];
        self.loadedPlugins = [];
        self._bind = bind;
        self._setHoursFromDate = setHoursFromDate;
        self._positionCalendar = positionCalendar;
        self.changeMonth = changeMonth;
        self.changeYear = changeYear;
        self.clear = clear;
        self.close = close;
        self.onMouseOver = onMouseOver;
        self._createElement = dom_1.createElement;
        self.createDay = createDay;
        self.destroy = destroy;
        self.isEnabled = isEnabled;
        self.jumpToDate = jumpToDate;
        self.updateValue = updateValue;
        self.open = open;
        self.redraw = redraw;
        self.set = set;
        self.setDate = setDate;
        self.toggle = toggle;
        function setupHelperFunctions() {
            self.utils = {
                getDaysInMonth: function (month, yr) {
                    if (month === void 0) {
                        month = self.currentMonth;
                    }
                    if (yr === void 0) {
                        yr = self.currentYear;
                    }
                    if (month === 1 && ((yr % 4 === 0 && yr % 100 !== 0) || yr % 400 === 0))
                        return 29;
                    return self.l10n.daysInMonth[month];
                },
            };
        }
        function init() {
            self.element = self.input = element;
            self.isOpen = false;
            parseConfig();
            setupLocale();
            setupInputs();
            setupDates();
            setupHelperFunctions();
            if (!self.isMobile)
                build();
            bindEvents();
            if (self.selectedDates.length || self.config.noCalendar) {
                if (self.config.enableTime) {
                    setHoursFromDate(self.config.noCalendar ? self.latestSelectedDateObj : undefined);
                }
                updateValue(false);
            }
            setCalendarWidth();
            var isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
            if (!self.isMobile && isSafari) {
                positionCalendar();
            }
            triggerEvent("onReady");
        }
        function getClosestActiveElement() {
            var _a;
            return (((_a = self.calendarContainer) === null || _a === void 0 ? void 0 : _a.getRootNode())
                .activeElement || document.activeElement);
        }
        function bindToInstance(fn) {
            return fn.bind(self);
        }
        function setCalendarWidth() {
            var config = self.config;
            if (config.weekNumbers === false && config.showMonths === 1) {
                return;
            }
            else if (config.noCalendar !== true) {
                window.requestAnimationFrame(function () {
                    if (self.calendarContainer !== undefined) {
                        self.calendarContainer.style.visibility = "hidden";
                        self.calendarContainer.style.display = "block";
                    }
                    if (self.daysContainer !== undefined) {
                        var daysWidth = (self.days.offsetWidth + 1) * config.showMonths;
                        self.daysContainer.style.width = daysWidth + "px";
                        self.calendarContainer.style.width =
                            daysWidth +
                                (self.weekWrapper !== undefined
                                    ? self.weekWrapper.offsetWidth
                                    : 0) +
                                "px";
                        self.calendarContainer.style.removeProperty("visibility");
                        self.calendarContainer.style.removeProperty("display");
                    }
                });
            }
        }
        function updateTime(e) {
            if (self.selectedDates.length === 0) {
                var defaultDate = self.config.minDate === undefined ||
                    (0, dates_1.compareDates)(new Date(), self.config.minDate) >= 0
                    ? new Date()
                    : new Date(self.config.minDate.getTime());
                var defaults = (0, dates_1.getDefaultHours)(self.config);
                defaultDate.setHours(defaults.hours, defaults.minutes, defaults.seconds, defaultDate.getMilliseconds());
                self.selectedDates = [defaultDate];
                self.latestSelectedDateObj = defaultDate;
            }
            if (e !== undefined && e.type !== "blur") {
                timeWrapper(e);
            }
            var prevValue = self._input.value;
            setHoursFromInputs();
            updateValue();
            if (self._input.value !== prevValue) {
                self._debouncedChange();
            }
        }
        function ampm2military(hour, amPM) {
            return (hour % 12) + 12 * (0, utils_1.int)(amPM === self.l10n.amPM[1]);
        }
        function military2ampm(hour) {
            switch (hour % 24) {
                case 0:
                case 12:
                    return 12;
                default:
                    return hour % 12;
            }
        }
        function setHoursFromInputs() {
            if (self.hourElement === undefined || self.minuteElement === undefined)
                return;
            var hours = (parseInt(self.hourElement.value.slice(-2), 10) || 0) % 24, minutes = (parseInt(self.minuteElement.value, 10) || 0) % 60, seconds = self.secondElement !== undefined
                ? (parseInt(self.secondElement.value, 10) || 0) % 60
                : 0;
            if (self.amPM !== undefined) {
                hours = ampm2military(hours, self.amPM.textContent);
            }
            var limitMinHours = self.config.minTime !== undefined ||
                (self.config.minDate &&
                    self.minDateHasTime &&
                    self.latestSelectedDateObj &&
                    (0, dates_1.compareDates)(self.latestSelectedDateObj, self.config.minDate, true) ===
                        0);
            var limitMaxHours = self.config.maxTime !== undefined ||
                (self.config.maxDate &&
                    self.maxDateHasTime &&
                    self.latestSelectedDateObj &&
                    (0, dates_1.compareDates)(self.latestSelectedDateObj, self.config.maxDate, true) ===
                        0);
            if (self.config.maxTime !== undefined &&
                self.config.minTime !== undefined &&
                self.config.minTime > self.config.maxTime) {
                var minBound = (0, dates_1.calculateSecondsSinceMidnight)(self.config.minTime.getHours(), self.config.minTime.getMinutes(), self.config.minTime.getSeconds());
                var maxBound = (0, dates_1.calculateSecondsSinceMidnight)(self.config.maxTime.getHours(), self.config.maxTime.getMinutes(), self.config.maxTime.getSeconds());
                var currentTime = (0, dates_1.calculateSecondsSinceMidnight)(hours, minutes, seconds);
                if (currentTime > maxBound && currentTime < minBound) {
                    var result = (0, dates_1.parseSeconds)(minBound);
                    hours = result[0];
                    minutes = result[1];
                    seconds = result[2];
                }
            }
            else {
                if (limitMaxHours) {
                    var maxTime = self.config.maxTime !== undefined
                        ? self.config.maxTime
                        : self.config.maxDate;
                    hours = Math.min(hours, maxTime.getHours());
                    if (hours === maxTime.getHours())
                        minutes = Math.min(minutes, maxTime.getMinutes());
                    if (minutes === maxTime.getMinutes())
                        seconds = Math.min(seconds, maxTime.getSeconds());
                }
                if (limitMinHours) {
                    var minTime = self.config.minTime !== undefined
                        ? self.config.minTime
                        : self.config.minDate;
                    hours = Math.max(hours, minTime.getHours());
                    if (hours === minTime.getHours() && minutes < minTime.getMinutes())
                        minutes = minTime.getMinutes();
                    if (minutes === minTime.getMinutes())
                        seconds = Math.max(seconds, minTime.getSeconds());
                }
            }
            setHours(hours, minutes, seconds);
        }
        function setHoursFromDate(dateObj) {
            var date = dateObj || self.latestSelectedDateObj;
            if (date && date instanceof Date) {
                setHours(date.getHours(), date.getMinutes(), date.getSeconds());
            }
        }
        function setHours(hours, minutes, seconds) {
            if (self.latestSelectedDateObj !== undefined) {
                self.latestSelectedDateObj.setHours(hours % 24, minutes, seconds || 0, 0);
            }
            if (!self.hourElement || !self.minuteElement || self.isMobile)
                return;
            self.hourElement.value = (0, utils_1.pad)(!self.config.time_24hr
                ? ((12 + hours) % 12) + 12 * (0, utils_1.int)(hours % 12 === 0)
                : hours);
            self.minuteElement.value = (0, utils_1.pad)(minutes);
            if (self.amPM !== undefined)
                self.amPM.textContent = self.l10n.amPM[(0, utils_1.int)(hours >= 12)];
            if (self.secondElement !== undefined)
                self.secondElement.value = (0, utils_1.pad)(seconds);
        }
        function onYearInput(event) {
            var eventTarget = (0, dom_1.getEventTarget)(event);
            var year = parseInt(eventTarget.value) + (event.delta || 0);
            if (year / 1000 > 1 ||
                (event.key === "Enter" && !/[^\d]/.test(year.toString()))) {
                changeYear(year);
            }
        }
        function bind(element, event, handler, options) {
            if (event instanceof Array)
                return event.forEach(function (ev) { return bind(element, ev, handler, options); });
            if (element instanceof Array)
                return element.forEach(function (el) { return bind(el, event, handler, options); });
            element.addEventListener(event, handler, options);
            self._handlers.push({
                remove: function () { return element.removeEventListener(event, handler, options); },
            });
        }
        function triggerChange() {
            triggerEvent("onChange");
        }
        function bindEvents() {
            if (self.config.wrap) {
                ["open", "close", "toggle", "clear"].forEach(function (evt) {
                    Array.prototype.forEach.call(self.element.querySelectorAll("[data-" + evt + "]"), function (el) {
                        return bind(el, "click", self[evt]);
                    });
                });
            }
            if (self.isMobile) {
                setupMobile();
                return;
            }
            var debouncedResize = (0, utils_1.debounce)(onResize, 50);
            self._debouncedChange = (0, utils_1.debounce)(triggerChange, DEBOUNCED_CHANGE_MS);
            if (self.daysContainer && !/iPhone|iPad|iPod/i.test(navigator.userAgent))
                bind(self.daysContainer, "mouseover", function (e) {
                    if (self.config.mode === "range")
                        onMouseOver((0, dom_1.getEventTarget)(e));
                });
            bind(self._input, "keydown", onKeyDown);
            if (self.calendarContainer !== undefined) {
                bind(self.calendarContainer, "keydown", onKeyDown);
            }
            if (!self.config.inline && !self.config.static)
                bind(window, "resize", debouncedResize);
            if (window.ontouchstart !== undefined)
                bind(window.document, "touchstart", documentClick);
            else
                bind(window.document, "mousedown", documentClick);
            bind(window.document, "focus", documentClick, { capture: true });
            if (self.config.clickOpens === true) {
                bind(self._input, "focus", self.open);
                bind(self._input, "click", self.open);
            }
            if (self.daysContainer !== undefined) {
                bind(self.monthNav, "click", onMonthNavClick);
                bind(self.monthNav, ["keyup", "increment"], onYearInput);
                bind(self.daysContainer, "click", selectDate);
            }
            if (self.timeContainer !== undefined &&
                self.minuteElement !== undefined &&
                self.hourElement !== undefined) {
                var selText = function (e) {
                    return (0, dom_1.getEventTarget)(e).select();
                };
                bind(self.timeContainer, ["increment"], updateTime);
                bind(self.timeContainer, "blur", updateTime, { capture: true });
                bind(self.timeContainer, "click", timeIncrement);
                bind([self.hourElement, self.minuteElement], ["focus", "click"], selText);
                if (self.secondElement !== undefined)
                    bind(self.secondElement, "focus", function () { return self.secondElement && self.secondElement.select(); });
                if (self.amPM !== undefined) {
                    bind(self.amPM, "click", function (e) {
                        updateTime(e);
                    });
                }
            }
            if (self.config.allowInput) {
                bind(self._input, "blur", onBlur);
            }
        }
        function jumpToDate(jumpDate, triggerChange) {
            var jumpTo = jumpDate !== undefined
                ? self.parseDate(jumpDate)
                : self.latestSelectedDateObj ||
                    (self.config.minDate && self.config.minDate > self.now
                        ? self.config.minDate
                        : self.config.maxDate && self.config.maxDate < self.now
                            ? self.config.maxDate
                            : self.now);
            var oldYear = self.currentYear;
            var oldMonth = self.currentMonth;
            try {
                if (jumpTo !== undefined) {
                    self.currentYear = jumpTo.getFullYear();
                    self.currentMonth = jumpTo.getMonth();
                }
            }
            catch (e) {
                e.message = "Invalid date supplied: " + jumpTo;
                self.config.errorHandler(e);
            }
            if (triggerChange && self.currentYear !== oldYear) {
                triggerEvent("onYearChange");
                buildMonthSwitch();
            }
            if (triggerChange &&
                (self.currentYear !== oldYear || self.currentMonth !== oldMonth)) {
                triggerEvent("onMonthChange");
            }
            self.redraw();
        }
        function timeIncrement(e) {
            var eventTarget = (0, dom_1.getEventTarget)(e);
            if (~eventTarget.className.indexOf("arrow"))
                incrementNumInput(e, eventTarget.classList.contains("arrowUp") ? 1 : -1);
        }
        function incrementNumInput(e, delta, inputElem) {
            var target = e && (0, dom_1.getEventTarget)(e);
            var input = inputElem ||
                (target && target.parentNode && target.parentNode.firstChild);
            var event = createEvent("increment");
            event.delta = delta;
            input && input.dispatchEvent(event);
        }
        function build() {
            var fragment = window.document.createDocumentFragment();
            self.calendarContainer = (0, dom_1.createElement)("div", "flatpickr-calendar");
            self.calendarContainer.tabIndex = -1;
            if (!self.config.noCalendar) {
                fragment.appendChild(buildMonthNav());
                self.innerContainer = (0, dom_1.createElement)("div", "flatpickr-innerContainer");
                if (self.config.weekNumbers) {
                    var _a = buildWeeks(), weekWrapper = _a.weekWrapper, weekNumbers = _a.weekNumbers;
                    self.innerContainer.appendChild(weekWrapper);
                    self.weekNumbers = weekNumbers;
                    self.weekWrapper = weekWrapper;
                }
                self.rContainer = (0, dom_1.createElement)("div", "flatpickr-rContainer");
                self.rContainer.appendChild(buildWeekdays());
                if (!self.daysContainer) {
                    self.daysContainer = (0, dom_1.createElement)("div", "flatpickr-days");
                    self.daysContainer.tabIndex = -1;
                }
                buildDays();
                self.rContainer.appendChild(self.daysContainer);
                self.innerContainer.appendChild(self.rContainer);
                fragment.appendChild(self.innerContainer);
            }
            if (self.config.enableTime) {
                fragment.appendChild(buildTime());
            }
            (0, dom_1.toggleClass)(self.calendarContainer, "rangeMode", self.config.mode === "range");
            (0, dom_1.toggleClass)(self.calendarContainer, "animate", self.config.animate === true);
            (0, dom_1.toggleClass)(self.calendarContainer, "multiMonth", self.config.showMonths > 1);
            self.calendarContainer.appendChild(fragment);
            var customAppend = self.config.appendTo !== undefined &&
                self.config.appendTo.nodeType !== undefined;
            if (self.config.inline || self.config.static) {
                self.calendarContainer.classList.add(self.config.inline ? "inline" : "static");
                if (self.config.inline) {
                    if (!customAppend && self.element.parentNode)
                        self.element.parentNode.insertBefore(self.calendarContainer, self._input.nextSibling);
                    else if (self.config.appendTo !== undefined)
                        self.config.appendTo.appendChild(self.calendarContainer);
                }
                if (self.config.static) {
                    var wrapper = (0, dom_1.createElement)("div", "flatpickr-wrapper");
                    if (self.element.parentNode)
                        self.element.parentNode.insertBefore(wrapper, self.element);
                    wrapper.appendChild(self.element);
                    if (self.altInput)
                        wrapper.appendChild(self.altInput);
                    wrapper.appendChild(self.calendarContainer);
                }
            }
            if (!self.config.static && !self.config.inline)
                (self.config.appendTo !== undefined
                    ? self.config.appendTo
                    : window.document.body).appendChild(self.calendarContainer);
        }
        function createDay(className, date, _dayNumber, i) {
            var dateIsEnabled = isEnabled(date, true), dayElement = (0, dom_1.createElement)("span", className, date.getDate().toString());
            dayElement.dateObj = date;
            dayElement.$i = i;
            dayElement.setAttribute("aria-label", self.formatDate(date, self.config.ariaDateFormat));
            if (className.indexOf("hidden") === -1 &&
                (0, dates_1.compareDates)(date, self.now) === 0) {
                self.todayDateElem = dayElement;
                dayElement.classList.add("today");
                dayElement.setAttribute("aria-current", "date");
            }
            if (dateIsEnabled) {
                dayElement.tabIndex = -1;
                if (isDateSelected(date)) {
                    dayElement.classList.add("selected");
                    self.selectedDateElem = dayElement;
                    if (self.config.mode === "range") {
                        (0, dom_1.toggleClass)(dayElement, "startRange", self.selectedDates[0] &&
                            (0, dates_1.compareDates)(date, self.selectedDates[0], true) === 0);
                        (0, dom_1.toggleClass)(dayElement, "endRange", self.selectedDates[1] &&
                            (0, dates_1.compareDates)(date, self.selectedDates[1], true) === 0);
                        if (className === "nextMonthDay")
                            dayElement.classList.add("inRange");
                    }
                }
            }
            else {
                dayElement.classList.add("flatpickr-disabled");
            }
            if (self.config.mode === "range") {
                if (isDateInRange(date) && !isDateSelected(date))
                    dayElement.classList.add("inRange");
            }
            if (self.weekNumbers &&
                self.config.showMonths === 1 &&
                className !== "prevMonthDay" &&
                i % 7 === 6) {
                self.weekNumbers.insertAdjacentHTML("beforeend", "<span class='flatpickr-day'>" + self.config.getWeek(date) + "</span>");
            }
            triggerEvent("onDayCreate", dayElement);
            return dayElement;
        }
        function focusOnDayElem(targetNode) {
            targetNode.focus();
            if (self.config.mode === "range")
                onMouseOver(targetNode);
        }
        function getFirstAvailableDay(delta) {
            var startMonth = delta > 0 ? 0 : self.config.showMonths - 1;
            var endMonth = delta > 0 ? self.config.showMonths : -1;
            for (var m = startMonth; m != endMonth; m += delta) {
                var month = self.daysContainer.children[m];
                var startIndex = delta > 0 ? 0 : month.children.length - 1;
                var endIndex = delta > 0 ? month.children.length : -1;
                for (var i = startIndex; i != endIndex; i += delta) {
                    var c = month.children[i];
                    if (c.className.indexOf("hidden") === -1 && isEnabled(c.dateObj))
                        return c;
                }
            }
            return undefined;
        }
        function getNextAvailableDay(current, delta) {
            var givenMonth = current.className.indexOf("Month") === -1
                ? current.dateObj.getMonth()
                : self.currentMonth;
            var endMonth = delta > 0 ? self.config.showMonths : -1;
            var loopDelta = delta > 0 ? 1 : -1;
            for (var m = givenMonth - self.currentMonth; m != endMonth; m += loopDelta) {
                var month = self.daysContainer.children[m];
                var startIndex = givenMonth - self.currentMonth === m
                    ? current.$i + delta
                    : delta < 0
                        ? month.children.length - 1
                        : 0;
                var numMonthDays = month.children.length;
                for (var i = startIndex; i >= 0 && i < numMonthDays && i != (delta > 0 ? numMonthDays : -1); i += loopDelta) {
                    var c = month.children[i];
                    if (c.className.indexOf("hidden") === -1 &&
                        isEnabled(c.dateObj) &&
                        Math.abs(current.$i - i) >= Math.abs(delta))
                        return focusOnDayElem(c);
                }
            }
            self.changeMonth(loopDelta);
            focusOnDay(getFirstAvailableDay(loopDelta), 0);
            return undefined;
        }
        function focusOnDay(current, offset) {
            var activeElement = getClosestActiveElement();
            var dayFocused = isInView(activeElement || document.body);
            var startElem = current !== undefined
                ? current
                : dayFocused
                    ? activeElement
                    : self.selectedDateElem !== undefined && isInView(self.selectedDateElem)
                        ? self.selectedDateElem
                        : self.todayDateElem !== undefined && isInView(self.todayDateElem)
                            ? self.todayDateElem
                            : getFirstAvailableDay(offset > 0 ? 1 : -1);
            if (startElem === undefined) {
                self._input.focus();
            }
            else if (!dayFocused) {
                focusOnDayElem(startElem);
            }
            else {
                getNextAvailableDay(startElem, offset);
            }
        }
        function buildMonthDays(year, month) {
            var firstOfMonth = (new Date(year, month, 1).getDay() - self.l10n.firstDayOfWeek + 7) % 7;
            var prevMonthDays = self.utils.getDaysInMonth((month - 1 + 12) % 12, year);
            var daysInMonth = self.utils.getDaysInMonth(month, year), days = window.document.createDocumentFragment(), isMultiMonth = self.config.showMonths > 1, prevMonthDayClass = isMultiMonth ? "prevMonthDay hidden" : "prevMonthDay", nextMonthDayClass = isMultiMonth ? "nextMonthDay hidden" : "nextMonthDay";
            var dayNumber = prevMonthDays + 1 - firstOfMonth, dayIndex = 0;
            for (; dayNumber <= prevMonthDays; dayNumber++, dayIndex++) {
                days.appendChild(createDay("flatpickr-day " + prevMonthDayClass, new Date(year, month - 1, dayNumber), dayNumber, dayIndex));
            }
            for (dayNumber = 1; dayNumber <= daysInMonth; dayNumber++, dayIndex++) {
                days.appendChild(createDay("flatpickr-day", new Date(year, month, dayNumber), dayNumber, dayIndex));
            }
            for (var dayNum = daysInMonth + 1; dayNum <= 42 - firstOfMonth &&
                (self.config.showMonths === 1 || dayIndex % 7 !== 0); dayNum++, dayIndex++) {
                days.appendChild(createDay("flatpickr-day " + nextMonthDayClass, new Date(year, month + 1, dayNum % daysInMonth), dayNum, dayIndex));
            }
            var dayContainer = (0, dom_1.createElement)("div", "dayContainer");
            dayContainer.appendChild(days);
            return dayContainer;
        }
        function buildDays() {
            if (self.daysContainer === undefined) {
                return;
            }
            (0, dom_1.clearNode)(self.daysContainer);
            if (self.weekNumbers)
                (0, dom_1.clearNode)(self.weekNumbers);
            var frag = document.createDocumentFragment();
            for (var i = 0; i < self.config.showMonths; i++) {
                var d = new Date(self.currentYear, self.currentMonth, 1);
                d.setMonth(self.currentMonth + i);
                frag.appendChild(buildMonthDays(d.getFullYear(), d.getMonth()));
            }
            self.daysContainer.appendChild(frag);
            self.days = self.daysContainer.firstChild;
            if (self.config.mode === "range" && self.selectedDates.length === 1) {
                onMouseOver();
            }
        }
        function buildMonthSwitch() {
            if (self.config.showMonths > 1 ||
                self.config.monthSelectorType !== "dropdown")
                return;
            var shouldBuildMonth = function (month) {
                if (self.config.minDate !== undefined &&
                    self.currentYear === self.config.minDate.getFullYear() &&
                    month < self.config.minDate.getMonth()) {
                    return false;
                }
                return !(self.config.maxDate !== undefined &&
                    self.currentYear === self.config.maxDate.getFullYear() &&
                    month > self.config.maxDate.getMonth());
            };
            self.monthsDropdownContainer.tabIndex = -1;
            self.monthsDropdownContainer.innerHTML = "";
            for (var i = 0; i < 12; i++) {
                if (!shouldBuildMonth(i))
                    continue;
                var month = (0, dom_1.createElement)("option", "flatpickr-monthDropdown-month");
                month.value = new Date(self.currentYear, i).getMonth().toString();
                month.textContent = (0, formatting_1.monthToStr)(i, self.config.shorthandCurrentMonth, self.l10n);
                month.tabIndex = -1;
                if (self.currentMonth === i) {
                    month.selected = true;
                }
                self.monthsDropdownContainer.appendChild(month);
            }
        }
        function buildMonth() {
            var container = (0, dom_1.createElement)("div", "flatpickr-month");
            var monthNavFragment = window.document.createDocumentFragment();
            var monthElement;
            if (self.config.showMonths > 1 ||
                self.config.monthSelectorType === "static") {
                monthElement = (0, dom_1.createElement)("span", "cur-month");
            }
            else {
                self.monthsDropdownContainer = (0, dom_1.createElement)("select", "flatpickr-monthDropdown-months");
                self.monthsDropdownContainer.setAttribute("aria-label", self.l10n.monthAriaLabel);
                bind(self.monthsDropdownContainer, "change", function (e) {
                    var target = (0, dom_1.getEventTarget)(e);
                    var selectedMonth = parseInt(target.value, 10);
                    self.changeMonth(selectedMonth - self.currentMonth);
                    triggerEvent("onMonthChange");
                });
                buildMonthSwitch();
                monthElement = self.monthsDropdownContainer;
            }
            var yearInput = (0, dom_1.createNumberInput)("cur-year", { tabindex: "-1" });
            var yearElement = yearInput.getElementsByTagName("input")[0];
            yearElement.setAttribute("aria-label", self.l10n.yearAriaLabel);
            if (self.config.minDate) {
                yearElement.setAttribute("min", self.config.minDate.getFullYear().toString());
            }
            if (self.config.maxDate) {
                yearElement.setAttribute("max", self.config.maxDate.getFullYear().toString());
                yearElement.disabled =
                    !!self.config.minDate &&
                        self.config.minDate.getFullYear() === self.config.maxDate.getFullYear();
            }
            var currentMonth = (0, dom_1.createElement)("div", "flatpickr-current-month");
            currentMonth.appendChild(monthElement);
            currentMonth.appendChild(yearInput);
            monthNavFragment.appendChild(currentMonth);
            container.appendChild(monthNavFragment);
            return {
                container: container,
                yearElement: yearElement,
                monthElement: monthElement,
            };
        }
        function buildMonths() {
            (0, dom_1.clearNode)(self.monthNav);
            self.monthNav.appendChild(self.prevMonthNav);
            if (self.config.showMonths) {
                self.yearElements = [];
                self.monthElements = [];
            }
            for (var m = self.config.showMonths; m--;) {
                var month = buildMonth();
                self.yearElements.push(month.yearElement);
                self.monthElements.push(month.monthElement);
                self.monthNav.appendChild(month.container);
            }
            self.monthNav.appendChild(self.nextMonthNav);
        }
        function buildMonthNav() {
            self.monthNav = (0, dom_1.createElement)("div", "flatpickr-months");
            self.yearElements = [];
            self.monthElements = [];
            self.prevMonthNav = (0, dom_1.createElement)("span", "flatpickr-prev-month");
            self.prevMonthNav.innerHTML = self.config.prevArrow;
            self.nextMonthNav = (0, dom_1.createElement)("span", "flatpickr-next-month");
            self.nextMonthNav.innerHTML = self.config.nextArrow;
            buildMonths();
            Object.defineProperty(self, "_hidePrevMonthArrow", {
                get: function () { return self.__hidePrevMonthArrow; },
                set: function (bool) {
                    if (self.__hidePrevMonthArrow !== bool) {
                        (0, dom_1.toggleClass)(self.prevMonthNav, "flatpickr-disabled", bool);
                        self.__hidePrevMonthArrow = bool;
                    }
                },
            });
            Object.defineProperty(self, "_hideNextMonthArrow", {
                get: function () { return self.__hideNextMonthArrow; },
                set: function (bool) {
                    if (self.__hideNextMonthArrow !== bool) {
                        (0, dom_1.toggleClass)(self.nextMonthNav, "flatpickr-disabled", bool);
                        self.__hideNextMonthArrow = bool;
                    }
                },
            });
            self.currentYearElement = self.yearElements[0];
            updateNavigationCurrentMonth();
            return self.monthNav;
        }
        function buildTime() {
            self.calendarContainer.classList.add("hasTime");
            if (self.config.noCalendar)
                self.calendarContainer.classList.add("noCalendar");
            var defaults = (0, dates_1.getDefaultHours)(self.config);
            self.timeContainer = (0, dom_1.createElement)("div", "flatpickr-time");
            self.timeContainer.tabIndex = -1;
            var separator = (0, dom_1.createElement)("span", "flatpickr-time-separator", ":");
            var hourInput = (0, dom_1.createNumberInput)("flatpickr-hour", {
                "aria-label": self.l10n.hourAriaLabel,
            });
            self.hourElement = hourInput.getElementsByTagName("input")[0];
            var minuteInput = (0, dom_1.createNumberInput)("flatpickr-minute", {
                "aria-label": self.l10n.minuteAriaLabel,
            });
            self.minuteElement = minuteInput.getElementsByTagName("input")[0];
            self.hourElement.tabIndex = self.minuteElement.tabIndex = -1;
            self.hourElement.value = (0, utils_1.pad)(self.latestSelectedDateObj
                ? self.latestSelectedDateObj.getHours()
                : self.config.time_24hr
                    ? defaults.hours
                    : military2ampm(defaults.hours));
            self.minuteElement.value = (0, utils_1.pad)(self.latestSelectedDateObj
                ? self.latestSelectedDateObj.getMinutes()
                : defaults.minutes);
            self.hourElement.setAttribute("step", self.config.hourIncrement.toString());
            self.minuteElement.setAttribute("step", self.config.minuteIncrement.toString());
            self.hourElement.setAttribute("min", self.config.time_24hr ? "0" : "1");
            self.hourElement.setAttribute("max", self.config.time_24hr ? "23" : "12");
            self.hourElement.setAttribute("maxlength", "2");
            self.minuteElement.setAttribute("min", "0");
            self.minuteElement.setAttribute("max", "59");
            self.minuteElement.setAttribute("maxlength", "2");
            self.timeContainer.appendChild(hourInput);
            self.timeContainer.appendChild(separator);
            self.timeContainer.appendChild(minuteInput);
            if (self.config.time_24hr)
                self.timeContainer.classList.add("time24hr");
            if (self.config.enableSeconds) {
                self.timeContainer.classList.add("hasSeconds");
                var secondInput = (0, dom_1.createNumberInput)("flatpickr-second");
                self.secondElement = secondInput.getElementsByTagName("input")[0];
                self.secondElement.value = (0, utils_1.pad)(self.latestSelectedDateObj
                    ? self.latestSelectedDateObj.getSeconds()
                    : defaults.seconds);
                self.secondElement.setAttribute("step", self.minuteElement.getAttribute("step"));
                self.secondElement.setAttribute("min", "0");
                self.secondElement.setAttribute("max", "59");
                self.secondElement.setAttribute("maxlength", "2");
                self.timeContainer.appendChild((0, dom_1.createElement)("span", "flatpickr-time-separator", ":"));
                self.timeContainer.appendChild(secondInput);
            }
            if (!self.config.time_24hr) {
                self.amPM = (0, dom_1.createElement)("span", "flatpickr-am-pm", self.l10n.amPM[(0, utils_1.int)((self.latestSelectedDateObj
                    ? self.hourElement.value
                    : self.config.defaultHour) > 11)]);
                self.amPM.title = self.l10n.toggleTitle;
                self.amPM.tabIndex = -1;
                self.timeContainer.appendChild(self.amPM);
            }
            return self.timeContainer;
        }
        function buildWeekdays() {
            if (!self.weekdayContainer)
                self.weekdayContainer = (0, dom_1.createElement)("div", "flatpickr-weekdays");
            else
                (0, dom_1.clearNode)(self.weekdayContainer);
            for (var i = self.config.showMonths; i--;) {
                var container = (0, dom_1.createElement)("div", "flatpickr-weekdaycontainer");
                self.weekdayContainer.appendChild(container);
            }
            updateWeekdays();
            return self.weekdayContainer;
        }
        function updateWeekdays() {
            if (!self.weekdayContainer) {
                return;
            }
            var firstDayOfWeek = self.l10n.firstDayOfWeek;
            var weekdays = __spreadArrays(self.l10n.weekdays.shorthand);
            if (firstDayOfWeek > 0 && firstDayOfWeek < weekdays.length) {
                weekdays = __spreadArrays(weekdays.splice(firstDayOfWeek, weekdays.length), weekdays.splice(0, firstDayOfWeek));
            }
            for (var i = self.config.showMonths; i--;) {
                self.weekdayContainer.children[i].innerHTML = "\n      <span class='flatpickr-weekday'>\n        " + weekdays.join("</span><span class='flatpickr-weekday'>") + "\n      </span>\n      ";
            }
        }
        function buildWeeks() {
            self.calendarContainer.classList.add("hasWeeks");
            var weekWrapper = (0, dom_1.createElement)("div", "flatpickr-weekwrapper");
            weekWrapper.appendChild((0, dom_1.createElement)("span", "flatpickr-weekday", self.l10n.weekAbbreviation));
            var weekNumbers = (0, dom_1.createElement)("div", "flatpickr-weeks");
            weekWrapper.appendChild(weekNumbers);
            return {
                weekWrapper: weekWrapper,
                weekNumbers: weekNumbers,
            };
        }
        function changeMonth(value, isOffset) {
            if (isOffset === void 0) {
                isOffset = true;
            }
            var delta = isOffset ? value : value - self.currentMonth;
            if ((delta < 0 && self._hidePrevMonthArrow === true) ||
                (delta > 0 && self._hideNextMonthArrow === true))
                return;
            self.currentMonth += delta;
            if (self.currentMonth < 0 || self.currentMonth > 11) {
                self.currentYear += self.currentMonth > 11 ? 1 : -1;
                self.currentMonth = (self.currentMonth + 12) % 12;
                triggerEvent("onYearChange");
                buildMonthSwitch();
            }
            buildDays();
            triggerEvent("onMonthChange");
            updateNavigationCurrentMonth();
        }
        function clear(triggerChangeEvent, toInitial) {
            if (triggerChangeEvent === void 0) {
                triggerChangeEvent = true;
            }
            if (toInitial === void 0) {
                toInitial = true;
            }
            self.input.value = "";
            if (self.altInput !== undefined)
                self.altInput.value = "";
            if (self.mobileInput !== undefined)
                self.mobileInput.value = "";
            self.selectedDates = [];
            self.latestSelectedDateObj = undefined;
            if (toInitial === true) {
                self.currentYear = self._initialDate.getFullYear();
                self.currentMonth = self._initialDate.getMonth();
            }
            if (self.config.enableTime === true) {
                var _a = (0, dates_1.getDefaultHours)(self.config), hours = _a.hours, minutes = _a.minutes, seconds = _a.seconds;
                setHours(hours, minutes, seconds);
            }
            self.redraw();
            if (triggerChangeEvent)
                triggerEvent("onChange");
        }
        function close() {
            self.isOpen = false;
            if (!self.isMobile) {
                if (self.calendarContainer !== undefined) {
                    self.calendarContainer.classList.remove("open");
                }
                if (self._input !== undefined) {
                    self._input.classList.remove("active");
                }
            }
            triggerEvent("onClose");
        }
        function destroy() {
            if (self.config !== undefined)
                triggerEvent("onDestroy");
            for (var i = self._handlers.length; i--;) {
                self._handlers[i].remove();
            }
            self._handlers = [];
            if (self.mobileInput) {
                if (self.mobileInput.parentNode)
                    self.mobileInput.parentNode.removeChild(self.mobileInput);
                self.mobileInput = undefined;
            }
            else if (self.calendarContainer && self.calendarContainer.parentNode) {
                if (self.config.static && self.calendarContainer.parentNode) {
                    var wrapper = self.calendarContainer.parentNode;
                    wrapper.lastChild && wrapper.removeChild(wrapper.lastChild);
                    if (wrapper.parentNode) {
                        while (wrapper.firstChild)
                            wrapper.parentNode.insertBefore(wrapper.firstChild, wrapper);
                        wrapper.parentNode.removeChild(wrapper);
                    }
                }
                else
                    self.calendarContainer.parentNode.removeChild(self.calendarContainer);
            }
            if (self.altInput) {
                self.input.type = "text";
                if (self.altInput.parentNode)
                    self.altInput.parentNode.removeChild(self.altInput);
                delete self.altInput;
            }
            if (self.input) {
                self.input.type = self.input._type;
                self.input.classList.remove("flatpickr-input");
                self.input.removeAttribute("readonly");
            }
            [
                "_showTimeInput",
                "latestSelectedDateObj",
                "_hideNextMonthArrow",
                "_hidePrevMonthArrow",
                "__hideNextMonthArrow",
                "__hidePrevMonthArrow",
                "isMobile",
                "isOpen",
                "selectedDateElem",
                "minDateHasTime",
                "maxDateHasTime",
                "days",
                "daysContainer",
                "_input",
                "_positionElement",
                "innerContainer",
                "rContainer",
                "monthNav",
                "todayDateElem",
                "calendarContainer",
                "weekdayContainer",
                "prevMonthNav",
                "nextMonthNav",
                "monthsDropdownContainer",
                "currentMonthElement",
                "currentYearElement",
                "navigationCurrentMonth",
                "selectedDateElem",
                "config",
            ].forEach(function (k) {
                try {
                    delete self[k];
                }
                catch (_) { }
            });
        }
        function isCalendarElem(elem) {
            return self.calendarContainer.contains(elem);
        }
        function documentClick(e) {
            if (self.isOpen && !self.config.inline) {
                var eventTarget_1 = (0, dom_1.getEventTarget)(e);
                var isCalendarElement = isCalendarElem(eventTarget_1);
                var isInput = eventTarget_1 === self.input ||
                    eventTarget_1 === self.altInput ||
                    self.element.contains(eventTarget_1) ||
                    (e.path &&
                        e.path.indexOf &&
                        (~e.path.indexOf(self.input) ||
                            ~e.path.indexOf(self.altInput)));
                var lostFocus = !isInput &&
                    !isCalendarElement &&
                    !isCalendarElem(e.relatedTarget);
                var isIgnored = !self.config.ignoredFocusElements.some(function (elem) {
                    return elem.contains(eventTarget_1);
                });
                if (lostFocus && isIgnored) {
                    if (self.config.allowInput) {
                        self.setDate(self._input.value, false, self.config.altInput
                            ? self.config.altFormat
                            : self.config.dateFormat);
                    }
                    if (self.timeContainer !== undefined &&
                        self.minuteElement !== undefined &&
                        self.hourElement !== undefined &&
                        self.input.value !== "" &&
                        self.input.value !== undefined) {
                        updateTime();
                    }
                    self.close();
                    if (self.config &&
                        self.config.mode === "range" &&
                        self.selectedDates.length === 1)
                        self.clear(false);
                }
            }
        }
        function changeYear(newYear) {
            if (!newYear ||
                (self.config.minDate && newYear < self.config.minDate.getFullYear()) ||
                (self.config.maxDate && newYear > self.config.maxDate.getFullYear()))
                return;
            var newYearNum = newYear, isNewYear = self.currentYear !== newYearNum;
            self.currentYear = newYearNum || self.currentYear;
            if (self.config.maxDate &&
                self.currentYear === self.config.maxDate.getFullYear()) {
                self.currentMonth = Math.min(self.config.maxDate.getMonth(), self.currentMonth);
            }
            else if (self.config.minDate &&
                self.currentYear === self.config.minDate.getFullYear()) {
                self.currentMonth = Math.max(self.config.minDate.getMonth(), self.currentMonth);
            }
            if (isNewYear) {
                self.redraw();
                triggerEvent("onYearChange");
                buildMonthSwitch();
            }
        }
        function isEnabled(date, timeless) {
            var _a;
            if (timeless === void 0) {
                timeless = true;
            }
            var dateToCheck = self.parseDate(date, undefined, timeless);
            if ((self.config.minDate &&
                dateToCheck &&
                (0, dates_1.compareDates)(dateToCheck, self.config.minDate, timeless !== undefined ? timeless : !self.minDateHasTime) < 0) ||
                (self.config.maxDate &&
                    dateToCheck &&
                    (0, dates_1.compareDates)(dateToCheck, self.config.maxDate, timeless !== undefined ? timeless : !self.maxDateHasTime) > 0))
                return false;
            if (!self.config.enable && self.config.disable.length === 0)
                return true;
            if (dateToCheck === undefined)
                return false;
            var bool = !!self.config.enable, array = (_a = self.config.enable) !== null && _a !== void 0 ? _a : self.config.disable;
            for (var i = 0, d = void 0; i < array.length; i++) {
                d = array[i];
                if (typeof d === "function" &&
                    d(dateToCheck))
                    return bool;
                else if (d instanceof Date &&
                    dateToCheck !== undefined &&
                    d.getTime() === dateToCheck.getTime())
                    return bool;
                else if (typeof d === "string") {
                    var parsed = self.parseDate(d, undefined, true);
                    return parsed && parsed.getTime() === dateToCheck.getTime()
                        ? bool
                        : !bool;
                }
                else if (typeof d === "object" &&
                    dateToCheck !== undefined &&
                    d.from &&
                    d.to &&
                    dateToCheck.getTime() >= d.from.getTime() &&
                    dateToCheck.getTime() <= d.to.getTime())
                    return bool;
            }
            return !bool;
        }
        function isInView(elem) {
            if (self.daysContainer !== undefined)
                return (elem.className.indexOf("hidden") === -1 &&
                    elem.className.indexOf("flatpickr-disabled") === -1 &&
                    self.daysContainer.contains(elem));
            return false;
        }
        function onBlur(e) {
            var isInput = e.target === self._input;
            var valueChanged = self._input.value.trimEnd() !== getDateStr();
            if (isInput &&
                valueChanged &&
                !(e.relatedTarget && isCalendarElem(e.relatedTarget))) {
                self.setDate(self._input.value, true, e.target === self.altInput
                    ? self.config.altFormat
                    : self.config.dateFormat);
            }
        }
        function onKeyDown(e) {
            var eventTarget = (0, dom_1.getEventTarget)(e);
            var isInput = self.config.wrap
                ? element.contains(eventTarget)
                : eventTarget === self._input;
            var allowInput = self.config.allowInput;
            var allowKeydown = self.isOpen && (!allowInput || !isInput);
            var allowInlineKeydown = self.config.inline && isInput && !allowInput;
            if (e.keyCode === 13 && isInput) {
                if (allowInput) {
                    self.setDate(self._input.value, true, eventTarget === self.altInput
                        ? self.config.altFormat
                        : self.config.dateFormat);
                    self.close();
                    return eventTarget.blur();
                }
                else {
                    self.open();
                }
            }
            else if (isCalendarElem(eventTarget) ||
                allowKeydown ||
                allowInlineKeydown) {
                var isTimeObj = !!self.timeContainer &&
                    self.timeContainer.contains(eventTarget);
                switch (e.keyCode) {
                    case 13:
                        if (isTimeObj) {
                            e.preventDefault();
                            updateTime();
                            focusAndClose();
                        }
                        else
                            selectDate(e);
                        break;
                    case 27:
                        e.preventDefault();
                        focusAndClose();
                        break;
                    case 8:
                    case 46:
                        if (isInput && !self.config.allowInput) {
                            e.preventDefault();
                            self.clear();
                        }
                        break;
                    case 37:
                    case 39:
                        if (!isTimeObj && !isInput) {
                            e.preventDefault();
                            var activeElement = getClosestActiveElement();
                            if (self.daysContainer !== undefined &&
                                (allowInput === false ||
                                    (activeElement && isInView(activeElement)))) {
                                var delta_1 = e.keyCode === 39 ? 1 : -1;
                                if (!e.ctrlKey)
                                    focusOnDay(undefined, delta_1);
                                else {
                                    e.stopPropagation();
                                    changeMonth(delta_1);
                                    focusOnDay(getFirstAvailableDay(1), 0);
                                }
                            }
                        }
                        else if (self.hourElement)
                            self.hourElement.focus();
                        break;
                    case 38:
                    case 40:
                        e.preventDefault();
                        var delta = e.keyCode === 40 ? 1 : -1;
                        if ((self.daysContainer &&
                            eventTarget.$i !== undefined) ||
                            eventTarget === self.input ||
                            eventTarget === self.altInput) {
                            if (e.ctrlKey) {
                                e.stopPropagation();
                                changeYear(self.currentYear - delta);
                                focusOnDay(getFirstAvailableDay(1), 0);
                            }
                            else if (!isTimeObj)
                                focusOnDay(undefined, delta * 7);
                        }
                        else if (eventTarget === self.currentYearElement) {
                            changeYear(self.currentYear - delta);
                        }
                        else if (self.config.enableTime) {
                            if (!isTimeObj && self.hourElement)
                                self.hourElement.focus();
                            updateTime(e);
                            self._debouncedChange();
                        }
                        break;
                    case 9:
                        if (isTimeObj) {
                            var elems = [
                                self.hourElement,
                                self.minuteElement,
                                self.secondElement,
                                self.amPM,
                            ]
                                .concat(self.pluginElements)
                                .filter(function (x) { return x; });
                            var i = elems.indexOf(eventTarget);
                            if (i !== -1) {
                                var target = elems[i + (e.shiftKey ? -1 : 1)];
                                e.preventDefault();
                                (target || self._input).focus();
                            }
                        }
                        else if (!self.config.noCalendar &&
                            self.daysContainer &&
                            self.daysContainer.contains(eventTarget) &&
                            e.shiftKey) {
                            e.preventDefault();
                            self._input.focus();
                        }
                        break;
                    default:
                        break;
                }
            }
            if (self.amPM !== undefined && eventTarget === self.amPM) {
                switch (e.key) {
                    case self.l10n.amPM[0].charAt(0):
                    case self.l10n.amPM[0].charAt(0).toLowerCase():
                        self.amPM.textContent = self.l10n.amPM[0];
                        setHoursFromInputs();
                        updateValue();
                        break;
                    case self.l10n.amPM[1].charAt(0):
                    case self.l10n.amPM[1].charAt(0).toLowerCase():
                        self.amPM.textContent = self.l10n.amPM[1];
                        setHoursFromInputs();
                        updateValue();
                        break;
                }
            }
            if (isInput || isCalendarElem(eventTarget)) {
                triggerEvent("onKeyDown", e);
            }
        }
        function onMouseOver(elem, cellClass) {
            if (cellClass === void 0) {
                cellClass = "flatpickr-day";
            }
            if (self.selectedDates.length !== 1 ||
                (elem &&
                    (!elem.classList.contains(cellClass) ||
                        elem.classList.contains("flatpickr-disabled"))))
                return;
            var hoverDate = elem
                ? elem.dateObj.getTime()
                : self.days.firstElementChild.dateObj.getTime(), initialDate = self.parseDate(self.selectedDates[0], undefined, true).getTime(), rangeStartDate = Math.min(hoverDate, self.selectedDates[0].getTime()), rangeEndDate = Math.max(hoverDate, self.selectedDates[0].getTime());
            var containsDisabled = false;
            var minRange = 0, maxRange = 0;
            for (var t = rangeStartDate; t < rangeEndDate; t += dates_1.duration.DAY) {
                if (!isEnabled(new Date(t), true)) {
                    containsDisabled =
                        containsDisabled || (t > rangeStartDate && t < rangeEndDate);
                    if (t < initialDate && (!minRange || t > minRange))
                        minRange = t;
                    else if (t > initialDate && (!maxRange || t < maxRange))
                        maxRange = t;
                }
            }
            var hoverableCells = Array.from(self.rContainer.querySelectorAll("*:nth-child(-n+" + self.config.showMonths + ") > ." + cellClass));
            hoverableCells.forEach(function (dayElem) {
                var date = dayElem.dateObj;
                var timestamp = date.getTime();
                var outOfRange = (minRange > 0 && timestamp < minRange) ||
                    (maxRange > 0 && timestamp > maxRange);
                if (outOfRange) {
                    dayElem.classList.add("notAllowed");
                    ["inRange", "startRange", "endRange"].forEach(function (c) {
                        dayElem.classList.remove(c);
                    });
                    return;
                }
                else if (containsDisabled && !outOfRange)
                    return;
                ["startRange", "inRange", "endRange", "notAllowed"].forEach(function (c) {
                    dayElem.classList.remove(c);
                });
                if (elem !== undefined) {
                    elem.classList.add(hoverDate <= self.selectedDates[0].getTime()
                        ? "startRange"
                        : "endRange");
                    if (initialDate < hoverDate && timestamp === initialDate)
                        dayElem.classList.add("startRange");
                    else if (initialDate > hoverDate && timestamp === initialDate)
                        dayElem.classList.add("endRange");
                    if (timestamp >= minRange &&
                        (maxRange === 0 || timestamp <= maxRange) &&
                        (0, dates_1.isBetween)(timestamp, initialDate, hoverDate))
                        dayElem.classList.add("inRange");
                }
            });
        }
        function onResize() {
            if (self.isOpen && !self.config.static && !self.config.inline)
                positionCalendar();
        }
        function open(e, positionElement) {
            if (positionElement === void 0) {
                positionElement = self._positionElement;
            }
            if (self.isMobile === true) {
                if (e) {
                    e.preventDefault();
                    var eventTarget = (0, dom_1.getEventTarget)(e);
                    if (eventTarget) {
                        eventTarget.blur();
                    }
                }
                if (self.mobileInput !== undefined) {
                    self.mobileInput.focus();
                    self.mobileInput.click();
                }
                triggerEvent("onOpen");
                return;
            }
            else if (self._input.disabled || self.config.inline) {
                return;
            }
            var wasOpen = self.isOpen;
            self.isOpen = true;
            if (!wasOpen) {
                self.calendarContainer.classList.add("open");
                self._input.classList.add("active");
                triggerEvent("onOpen");
                positionCalendar(positionElement);
            }
            if (self.config.enableTime === true && self.config.noCalendar === true) {
                if (self.config.allowInput === false &&
                    (e === undefined ||
                        !self.timeContainer.contains(e.relatedTarget))) {
                    setTimeout(function () { return self.hourElement.select(); }, 50);
                }
            }
        }
        function minMaxDateSetter(type) {
            return function (date) {
                var dateObj = (self.config["_" + type + "Date"] = self.parseDate(date, self.config.dateFormat));
                var inverseDateObj = self.config["_" + (type === "min" ? "max" : "min") + "Date"];
                if (dateObj !== undefined) {
                    self[type === "min" ? "minDateHasTime" : "maxDateHasTime"] =
                        dateObj.getHours() > 0 ||
                            dateObj.getMinutes() > 0 ||
                            dateObj.getSeconds() > 0;
                }
                if (self.selectedDates) {
                    self.selectedDates = self.selectedDates.filter(function (d) { return isEnabled(d); });
                    if (!self.selectedDates.length && type === "min")
                        setHoursFromDate(dateObj);
                    updateValue();
                }
                if (self.daysContainer) {
                    redraw();
                    if (dateObj !== undefined)
                        self.currentYearElement[type] = dateObj.getFullYear().toString();
                    else
                        self.currentYearElement.removeAttribute(type);
                    self.currentYearElement.disabled =
                        !!inverseDateObj &&
                            dateObj !== undefined &&
                            inverseDateObj.getFullYear() === dateObj.getFullYear();
                }
            };
        }
        function parseConfig() {
            var boolOpts = [
                "wrap",
                "weekNumbers",
                "allowInput",
                "allowInvalidPreload",
                "clickOpens",
                "time_24hr",
                "enableTime",
                "noCalendar",
                "altInput",
                "shorthandCurrentMonth",
                "inline",
                "static",
                "enableSeconds",
                "disableMobile",
            ];
            var userConfig = __assign(__assign({}, JSON.parse(JSON.stringify(element.dataset || {}))), instanceConfig);
            var formats = {};
            self.config.parseDate = userConfig.parseDate;
            self.config.formatDate = userConfig.formatDate;
            Object.defineProperty(self.config, "enable", {
                get: function () { return self.config._enable; },
                set: function (dates) {
                    self.config._enable = parseDateRules(dates);
                },
            });
            Object.defineProperty(self.config, "disable", {
                get: function () { return self.config._disable; },
                set: function (dates) {
                    self.config._disable = parseDateRules(dates);
                },
            });
            var timeMode = userConfig.mode === "time";
            if (!userConfig.dateFormat && (userConfig.enableTime || timeMode)) {
                var defaultDateFormat = flatpickr.defaultConfig.dateFormat || options_1.defaults.dateFormat;
                formats.dateFormat =
                    userConfig.noCalendar || timeMode
                        ? "H:i" + (userConfig.enableSeconds ? ":S" : "")
                        : defaultDateFormat + " H:i" + (userConfig.enableSeconds ? ":S" : "");
            }
            if (userConfig.altInput &&
                (userConfig.enableTime || timeMode) &&
                !userConfig.altFormat) {
                var defaultAltFormat = flatpickr.defaultConfig.altFormat || options_1.defaults.altFormat;
                formats.altFormat =
                    userConfig.noCalendar || timeMode
                        ? "h:i" + (userConfig.enableSeconds ? ":S K" : " K")
                        : defaultAltFormat + (" h:i" + (userConfig.enableSeconds ? ":S" : "") + " K");
            }
            Object.defineProperty(self.config, "minDate", {
                get: function () { return self.config._minDate; },
                set: minMaxDateSetter("min"),
            });
            Object.defineProperty(self.config, "maxDate", {
                get: function () { return self.config._maxDate; },
                set: minMaxDateSetter("max"),
            });
            var minMaxTimeSetter = function (type) {
                return function (val) {
                    self.config[type === "min" ? "_minTime" : "_maxTime"] = self.parseDate(val, "H:i:S");
                };
            };
            Object.defineProperty(self.config, "minTime", {
                get: function () { return self.config._minTime; },
                set: minMaxTimeSetter("min"),
            });
            Object.defineProperty(self.config, "maxTime", {
                get: function () { return self.config._maxTime; },
                set: minMaxTimeSetter("max"),
            });
            if (userConfig.mode === "time") {
                self.config.noCalendar = true;
                self.config.enableTime = true;
            }
            Object.assign(self.config, formats, userConfig);
            for (var i = 0; i < boolOpts.length; i++)
                self.config[boolOpts[i]] =
                    self.config[boolOpts[i]] === true ||
                        self.config[boolOpts[i]] === "true";
            options_1.HOOKS.filter(function (hook) { return self.config[hook] !== undefined; }).forEach(function (hook) {
                self.config[hook] = (0, utils_1.arrayify)(self.config[hook] || []).map(bindToInstance);
            });
            self.isMobile =
                !self.config.disableMobile &&
                    !self.config.inline &&
                    self.config.mode === "single" &&
                    !self.config.disable.length &&
                    !self.config.enable &&
                    !self.config.weekNumbers &&
                    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            for (var i = 0; i < self.config.plugins.length; i++) {
                var pluginConf = self.config.plugins[i](self) || {};
                for (var key in pluginConf) {
                    if (options_1.HOOKS.indexOf(key) > -1) {
                        self.config[key] = (0, utils_1.arrayify)(pluginConf[key])
                            .map(bindToInstance)
                            .concat(self.config[key]);
                    }
                    else if (typeof userConfig[key] === "undefined")
                        self.config[key] = pluginConf[key];
                }
            }
            if (!userConfig.altInputClass) {
                self.config.altInputClass =
                    getInputElem().className + " " + self.config.altInputClass;
            }
            triggerEvent("onParseConfig");
        }
        function getInputElem() {
            return self.config.wrap
                ? element.querySelector("[data-input]")
                : element;
        }
        function setupLocale() {
            if (typeof self.config.locale !== "object" &&
                typeof flatpickr.l10ns[self.config.locale] === "undefined")
                self.config.errorHandler(new Error("flatpickr: invalid locale " + self.config.locale));
            self.l10n = __assign(__assign({}, flatpickr.l10ns.default), (typeof self.config.locale === "object"
                ? self.config.locale
                : self.config.locale !== "default"
                    ? flatpickr.l10ns[self.config.locale]
                    : undefined));
            formatting_1.tokenRegex.D = "(" + self.l10n.weekdays.shorthand.join("|") + ")";
            formatting_1.tokenRegex.l = "(" + self.l10n.weekdays.longhand.join("|") + ")";
            formatting_1.tokenRegex.M = "(" + self.l10n.months.shorthand.join("|") + ")";
            formatting_1.tokenRegex.F = "(" + self.l10n.months.longhand.join("|") + ")";
            formatting_1.tokenRegex.K = "(" + self.l10n.amPM[0] + "|" + self.l10n.amPM[1] + "|" + self.l10n.amPM[0].toLowerCase() + "|" + self.l10n.amPM[1].toLowerCase() + ")";
            var userConfig = __assign(__assign({}, instanceConfig), JSON.parse(JSON.stringify(element.dataset || {})));
            if (userConfig.time_24hr === undefined &&
                flatpickr.defaultConfig.time_24hr === undefined) {
                self.config.time_24hr = self.l10n.time_24hr;
            }
            self.formatDate = (0, dates_1.createDateFormatter)(self);
            self.parseDate = (0, dates_1.createDateParser)({ config: self.config, l10n: self.l10n });
        }
        function positionCalendar(customPositionElement) {
            if (typeof self.config.position === "function") {
                return void self.config.position(self, customPositionElement);
            }
            if (self.calendarContainer === undefined)
                return;
            triggerEvent("onPreCalendarPosition");
            var positionElement = customPositionElement || self._positionElement;
            var calendarHeight = Array.prototype.reduce.call(self.calendarContainer.children, (function (acc, child) { return acc + child.offsetHeight; }), 0), calendarWidth = self.calendarContainer.offsetWidth, configPos = self.config.position.split(" "), configPosVertical = configPos[0], configPosHorizontal = configPos.length > 1 ? configPos[1] : null, inputBounds = positionElement.getBoundingClientRect(), distanceFromBottom = window.innerHeight - inputBounds.bottom, showOnTop = configPosVertical === "above" ||
                (configPosVertical !== "below" &&
                    distanceFromBottom < calendarHeight &&
                    inputBounds.top > calendarHeight);
            var top = window.pageYOffset +
                inputBounds.top +
                (!showOnTop ? positionElement.offsetHeight + 2 : -calendarHeight - 2);
            (0, dom_1.toggleClass)(self.calendarContainer, "arrowTop", !showOnTop);
            (0, dom_1.toggleClass)(self.calendarContainer, "arrowBottom", showOnTop);
            if (self.config.inline)
                return;
            var left = window.pageXOffset + inputBounds.left;
            var isCenter = false;
            var isRight = false;
            if (configPosHorizontal === "center") {
                left -= (calendarWidth - inputBounds.width) / 2;
                isCenter = true;
            }
            else if (configPosHorizontal === "right") {
                left -= calendarWidth - inputBounds.width;
                isRight = true;
            }
            (0, dom_1.toggleClass)(self.calendarContainer, "arrowLeft", !isCenter && !isRight);
            (0, dom_1.toggleClass)(self.calendarContainer, "arrowCenter", isCenter);
            (0, dom_1.toggleClass)(self.calendarContainer, "arrowRight", isRight);
            var right = window.document.body.offsetWidth -
                (window.pageXOffset + inputBounds.right);
            var rightMost = left + calendarWidth > window.document.body.offsetWidth;
            var centerMost = right + calendarWidth > window.document.body.offsetWidth;
            (0, dom_1.toggleClass)(self.calendarContainer, "rightMost", rightMost);
            if (self.config.static)
                return;
            self.calendarContainer.style.top = top + "px";
            if (!rightMost) {
                self.calendarContainer.style.left = left + "px";
                self.calendarContainer.style.right = "auto";
            }
            else if (!centerMost) {
                self.calendarContainer.style.left = "auto";
                self.calendarContainer.style.right = right + "px";
            }
            else {
                var doc = getDocumentStyleSheet();
                if (doc === undefined)
                    return;
                var bodyWidth = window.document.body.offsetWidth;
                var centerLeft = Math.max(0, bodyWidth / 2 - calendarWidth / 2);
                var centerBefore = ".flatpickr-calendar.centerMost:before";
                var centerAfter = ".flatpickr-calendar.centerMost:after";
                var centerIndex = doc.cssRules.length;
                var centerStyle = "{left:" + inputBounds.left + "px;right:auto;}";
                (0, dom_1.toggleClass)(self.calendarContainer, "rightMost", false);
                (0, dom_1.toggleClass)(self.calendarContainer, "centerMost", true);
                doc.insertRule(centerBefore + "," + centerAfter + centerStyle, centerIndex);
                self.calendarContainer.style.left = centerLeft + "px";
                self.calendarContainer.style.right = "auto";
            }
        }
        function getDocumentStyleSheet() {
            var editableSheet = null;
            for (var i = 0; i < document.styleSheets.length; i++) {
                var sheet = document.styleSheets[i];
                if (!sheet.cssRules)
                    continue;
                try {
                    sheet.cssRules;
                }
                catch (err) {
                    continue;
                }
                editableSheet = sheet;
                break;
            }
            return editableSheet != null ? editableSheet : createStyleSheet();
        }
        function createStyleSheet() {
            var style = document.createElement("style");
            document.head.appendChild(style);
            return style.sheet;
        }
        function redraw() {
            if (self.config.noCalendar || self.isMobile)
                return;
            buildMonthSwitch();
            updateNavigationCurrentMonth();
            buildDays();
        }
        function focusAndClose() {
            self._input.focus();
            if (window.navigator.userAgent.indexOf("MSIE") !== -1 ||
                navigator.msMaxTouchPoints !== undefined) {
                setTimeout(self.close, 0);
            }
            else {
                self.close();
            }
        }
        function selectDate(e) {
            e.preventDefault();
            e.stopPropagation();
            var isSelectable = function (day) {
                return day.classList &&
                    day.classList.contains("flatpickr-day") &&
                    !day.classList.contains("flatpickr-disabled") &&
                    !day.classList.contains("notAllowed");
            };
            var t = (0, dom_1.findParent)((0, dom_1.getEventTarget)(e), isSelectable);
            if (t === undefined)
                return;
            var target = t;
            var selectedDate = (self.latestSelectedDateObj = new Date(target.dateObj.getTime()));
            var shouldChangeMonth = (selectedDate.getMonth() < self.currentMonth ||
                selectedDate.getMonth() >
                    self.currentMonth + self.config.showMonths - 1) &&
                self.config.mode !== "range";
            self.selectedDateElem = target;
            if (self.config.mode === "single")
                self.selectedDates = [selectedDate];
            else if (self.config.mode === "multiple") {
                var selectedIndex = isDateSelected(selectedDate);
                if (selectedIndex)
                    self.selectedDates.splice(parseInt(selectedIndex), 1);
                else
                    self.selectedDates.push(selectedDate);
            }
            else if (self.config.mode === "range") {
                if (self.selectedDates.length === 2) {
                    self.clear(false, false);
                }
                self.latestSelectedDateObj = selectedDate;
                self.selectedDates.push(selectedDate);
                if ((0, dates_1.compareDates)(selectedDate, self.selectedDates[0], true) !== 0)
                    self.selectedDates.sort(function (a, b) { return a.getTime() - b.getTime(); });
            }
            setHoursFromInputs();
            if (shouldChangeMonth) {
                var isNewYear = self.currentYear !== selectedDate.getFullYear();
                self.currentYear = selectedDate.getFullYear();
                self.currentMonth = selectedDate.getMonth();
                if (isNewYear) {
                    triggerEvent("onYearChange");
                    buildMonthSwitch();
                }
                triggerEvent("onMonthChange");
            }
            updateNavigationCurrentMonth();
            buildDays();
            updateValue();
            if (!shouldChangeMonth &&
                self.config.mode !== "range" &&
                self.config.showMonths === 1)
                focusOnDayElem(target);
            else if (self.selectedDateElem !== undefined &&
                self.hourElement === undefined) {
                self.selectedDateElem && self.selectedDateElem.focus();
            }
            if (self.hourElement !== undefined)
                self.hourElement !== undefined && self.hourElement.focus();
            if (self.config.closeOnSelect) {
                var single = self.config.mode === "single" && !self.config.enableTime;
                var range = self.config.mode === "range" &&
                    self.selectedDates.length === 2 &&
                    !self.config.enableTime;
                if (single || range) {
                    focusAndClose();
                }
            }
            triggerChange();
        }
        var CALLBACKS = {
            locale: [setupLocale, updateWeekdays],
            showMonths: [buildMonths, setCalendarWidth, buildWeekdays],
            minDate: [jumpToDate],
            maxDate: [jumpToDate],
            positionElement: [updatePositionElement],
            clickOpens: [
                function () {
                    if (self.config.clickOpens === true) {
                        bind(self._input, "focus", self.open);
                        bind(self._input, "click", self.open);
                    }
                    else {
                        self._input.removeEventListener("focus", self.open);
                        self._input.removeEventListener("click", self.open);
                    }
                },
            ],
        };
        function set(option, value) {
            if (option !== null && typeof option === "object") {
                Object.assign(self.config, option);
                for (var key in option) {
                    if (CALLBACKS[key] !== undefined)
                        CALLBACKS[key].forEach(function (x) { return x(); });
                }
            }
            else {
                self.config[option] = value;
                if (CALLBACKS[option] !== undefined)
                    CALLBACKS[option].forEach(function (x) { return x(); });
                else if (options_1.HOOKS.indexOf(option) > -1)
                    self.config[option] = (0, utils_1.arrayify)(value);
            }
            self.redraw();
            updateValue(true);
        }
        function setSelectedDate(inputDate, format) {
            var dates = [];
            if (inputDate instanceof Array)
                dates = inputDate.map(function (d) { return self.parseDate(d, format); });
            else if (inputDate instanceof Date || typeof inputDate === "number")
                dates = [self.parseDate(inputDate, format)];
            else if (typeof inputDate === "string") {
                switch (self.config.mode) {
                    case "single":
                    case "time":
                        dates = [self.parseDate(inputDate, format)];
                        break;
                    case "multiple":
                        dates = inputDate
                            .split(self.config.conjunction)
                            .map(function (date) { return self.parseDate(date, format); });
                        break;
                    case "range":
                        dates = inputDate
                            .split(self.l10n.rangeSeparator)
                            .map(function (date) { return self.parseDate(date, format); });
                        break;
                    default:
                        break;
                }
            }
            else
                self.config.errorHandler(new Error("Invalid date supplied: " + JSON.stringify(inputDate)));
            self.selectedDates = (self.config.allowInvalidPreload
                ? dates
                : dates.filter(function (d) { return d instanceof Date && isEnabled(d, false); }));
            if (self.config.mode === "range")
                self.selectedDates.sort(function (a, b) { return a.getTime() - b.getTime(); });
        }
        function setDate(date, triggerChange, format) {
            if (triggerChange === void 0) {
                triggerChange = false;
            }
            if (format === void 0) {
                format = self.config.dateFormat;
            }
            if ((date !== 0 && !date) || (date instanceof Array && date.length === 0))
                return self.clear(triggerChange);
            setSelectedDate(date, format);
            self.latestSelectedDateObj =
                self.selectedDates[self.selectedDates.length - 1];
            self.redraw();
            jumpToDate(undefined, triggerChange);
            setHoursFromDate();
            if (self.selectedDates.length === 0) {
                self.clear(false);
            }
            updateValue(triggerChange);
            if (triggerChange)
                triggerEvent("onChange");
        }
        function parseDateRules(arr) {
            return arr
                .slice()
                .map(function (rule) {
                if (typeof rule === "string" ||
                    typeof rule === "number" ||
                    rule instanceof Date) {
                    return self.parseDate(rule, undefined, true);
                }
                else if (rule &&
                    typeof rule === "object" &&
                    rule.from &&
                    rule.to)
                    return {
                        from: self.parseDate(rule.from, undefined),
                        to: self.parseDate(rule.to, undefined),
                    };
                return rule;
            })
                .filter(function (x) { return x; });
        }
        function setupDates() {
            self.selectedDates = [];
            self.now = self.parseDate(self.config.now) || new Date();
            var preloadedDate = self.config.defaultDate ||
                ((self.input.nodeName === "INPUT" ||
                    self.input.nodeName === "TEXTAREA") &&
                    self.input.placeholder &&
                    self.input.value === self.input.placeholder
                    ? null
                    : self.input.value);
            if (preloadedDate)
                setSelectedDate(preloadedDate, self.config.dateFormat);
            self._initialDate =
                self.selectedDates.length > 0
                    ? self.selectedDates[0]
                    : self.config.minDate &&
                        self.config.minDate.getTime() > self.now.getTime()
                        ? self.config.minDate
                        : self.config.maxDate &&
                            self.config.maxDate.getTime() < self.now.getTime()
                            ? self.config.maxDate
                            : self.now;
            self.currentYear = self._initialDate.getFullYear();
            self.currentMonth = self._initialDate.getMonth();
            if (self.selectedDates.length > 0)
                self.latestSelectedDateObj = self.selectedDates[0];
            if (self.config.minTime !== undefined)
                self.config.minTime = self.parseDate(self.config.minTime, "H:i");
            if (self.config.maxTime !== undefined)
                self.config.maxTime = self.parseDate(self.config.maxTime, "H:i");
            self.minDateHasTime =
                !!self.config.minDate &&
                    (self.config.minDate.getHours() > 0 ||
                        self.config.minDate.getMinutes() > 0 ||
                        self.config.minDate.getSeconds() > 0);
            self.maxDateHasTime =
                !!self.config.maxDate &&
                    (self.config.maxDate.getHours() > 0 ||
                        self.config.maxDate.getMinutes() > 0 ||
                        self.config.maxDate.getSeconds() > 0);
        }
        function setupInputs() {
            self.input = getInputElem();
            if (!self.input) {
                self.config.errorHandler(new Error("Invalid input element specified"));
                return;
            }
            self.input._type = self.input.type;
            self.input.type = "text";
            self.input.classList.add("flatpickr-input");
            self._input = self.input;
            if (self.config.altInput) {
                self.altInput = (0, dom_1.createElement)(self.input.nodeName, self.config.altInputClass);
                self._input = self.altInput;
                self.altInput.placeholder = self.input.placeholder;
                self.altInput.disabled = self.input.disabled;
                self.altInput.required = self.input.required;
                self.altInput.tabIndex = self.input.tabIndex;
                self.altInput.type = "text";
                self.input.setAttribute("type", "hidden");
                if (!self.config.static && self.input.parentNode)
                    self.input.parentNode.insertBefore(self.altInput, self.input.nextSibling);
            }
            if (!self.config.allowInput)
                self._input.setAttribute("readonly", "readonly");
            updatePositionElement();
        }
        function updatePositionElement() {
            self._positionElement = self.config.positionElement || self._input;
        }
        function setupMobile() {
            var inputType = self.config.enableTime
                ? self.config.noCalendar
                    ? "time"
                    : "datetime-local"
                : "date";
            self.mobileInput = (0, dom_1.createElement)("input", self.input.className + " flatpickr-mobile");
            self.mobileInput.tabIndex = 1;
            self.mobileInput.type = inputType;
            self.mobileInput.disabled = self.input.disabled;
            self.mobileInput.required = self.input.required;
            self.mobileInput.placeholder = self.input.placeholder;
            self.mobileFormatStr =
                inputType === "datetime-local"
                    ? "Y-m-d\\TH:i:S"
                    : inputType === "date"
                        ? "Y-m-d"
                        : "H:i:S";
            if (self.selectedDates.length > 0) {
                self.mobileInput.defaultValue = self.mobileInput.value = self.formatDate(self.selectedDates[0], self.mobileFormatStr);
            }
            if (self.config.minDate)
                self.mobileInput.min = self.formatDate(self.config.minDate, "Y-m-d");
            if (self.config.maxDate)
                self.mobileInput.max = self.formatDate(self.config.maxDate, "Y-m-d");
            if (self.input.getAttribute("step"))
                self.mobileInput.step = String(self.input.getAttribute("step"));
            self.input.type = "hidden";
            if (self.altInput !== undefined)
                self.altInput.type = "hidden";
            try {
                if (self.input.parentNode)
                    self.input.parentNode.insertBefore(self.mobileInput, self.input.nextSibling);
            }
            catch (_a) { }
            bind(self.mobileInput, "change", function (e) {
                self.setDate((0, dom_1.getEventTarget)(e).value, false, self.mobileFormatStr);
                triggerEvent("onChange");
                triggerEvent("onClose");
            });
        }
        function toggle(e) {
            if (self.isOpen === true)
                return self.close();
            self.open(e);
        }
        function triggerEvent(event, data) {
            if (self.config === undefined)
                return;
            var hooks = self.config[event];
            if (hooks !== undefined && hooks.length > 0) {
                for (var i = 0; hooks[i] && i < hooks.length; i++)
                    hooks[i](self.selectedDates, self.input.value, self, data);
            }
            if (event === "onChange") {
                self.input.dispatchEvent(createEvent("change"));
                self.input.dispatchEvent(createEvent("input"));
            }
        }
        function createEvent(name) {
            var e = document.createEvent("Event");
            e.initEvent(name, true, true);
            return e;
        }
        function isDateSelected(date) {
            for (var i = 0; i < self.selectedDates.length; i++) {
                var selectedDate = self.selectedDates[i];
                if (selectedDate instanceof Date &&
                    (0, dates_1.compareDates)(selectedDate, date) === 0)
                    return "" + i;
            }
            return false;
        }
        function isDateInRange(date) {
            if (self.config.mode !== "range" || self.selectedDates.length < 2)
                return false;
            return ((0, dates_1.compareDates)(date, self.selectedDates[0]) >= 0 &&
                (0, dates_1.compareDates)(date, self.selectedDates[1]) <= 0);
        }
        function updateNavigationCurrentMonth() {
            if (self.config.noCalendar || self.isMobile || !self.monthNav)
                return;
            self.yearElements.forEach(function (yearElement, i) {
                var d = new Date(self.currentYear, self.currentMonth, 1);
                d.setMonth(self.currentMonth + i);
                if (self.config.showMonths > 1 ||
                    self.config.monthSelectorType === "static") {
                    self.monthElements[i].textContent =
                        (0, formatting_1.monthToStr)(d.getMonth(), self.config.shorthandCurrentMonth, self.l10n) + " ";
                }
                else {
                    self.monthsDropdownContainer.value = d.getMonth().toString();
                }
                yearElement.value = d.getFullYear().toString();
            });
            self._hidePrevMonthArrow =
                self.config.minDate !== undefined &&
                    (self.currentYear === self.config.minDate.getFullYear()
                        ? self.currentMonth <= self.config.minDate.getMonth()
                        : self.currentYear < self.config.minDate.getFullYear());
            self._hideNextMonthArrow =
                self.config.maxDate !== undefined &&
                    (self.currentYear === self.config.maxDate.getFullYear()
                        ? self.currentMonth + 1 > self.config.maxDate.getMonth()
                        : self.currentYear > self.config.maxDate.getFullYear());
        }
        function getDateStr(specificFormat) {
            var format = specificFormat ||
                (self.config.altInput ? self.config.altFormat : self.config.dateFormat);
            return self.selectedDates
                .map(function (dObj) { return self.formatDate(dObj, format); })
                .filter(function (d, i, arr) {
                return self.config.mode !== "range" ||
                    self.config.enableTime ||
                    arr.indexOf(d) === i;
            })
                .join(self.config.mode !== "range"
                ? self.config.conjunction
                : self.l10n.rangeSeparator);
        }
        function updateValue(triggerChange) {
            if (triggerChange === void 0) {
                triggerChange = true;
            }
            if (self.mobileInput !== undefined && self.mobileFormatStr) {
                self.mobileInput.value =
                    self.latestSelectedDateObj !== undefined
                        ? self.formatDate(self.latestSelectedDateObj, self.mobileFormatStr)
                        : "";
            }
            self.input.value = getDateStr(self.config.dateFormat);
            if (self.altInput !== undefined) {
                self.altInput.value = getDateStr(self.config.altFormat);
            }
            if (triggerChange !== false)
                triggerEvent("onValueUpdate");
        }
        function onMonthNavClick(e) {
            var eventTarget = (0, dom_1.getEventTarget)(e);
            var isPrevMonth = self.prevMonthNav.contains(eventTarget);
            var isNextMonth = self.nextMonthNav.contains(eventTarget);
            if (isPrevMonth || isNextMonth) {
                changeMonth(isPrevMonth ? -1 : 1);
            }
            else if (self.yearElements.indexOf(eventTarget) >= 0) {
                eventTarget.select();
            }
            else if (eventTarget.classList.contains("arrowUp")) {
                self.changeYear(self.currentYear + 1);
            }
            else if (eventTarget.classList.contains("arrowDown")) {
                self.changeYear(self.currentYear - 1);
            }
        }
        function timeWrapper(e) {
            e.preventDefault();
            var isKeyDown = e.type === "keydown", eventTarget = (0, dom_1.getEventTarget)(e), input = eventTarget;
            if (self.amPM !== undefined && eventTarget === self.amPM) {
                self.amPM.textContent =
                    self.l10n.amPM[(0, utils_1.int)(self.amPM.textContent === self.l10n.amPM[0])];
            }
            var min = parseFloat(input.getAttribute("min")), max = parseFloat(input.getAttribute("max")), step = parseFloat(input.getAttribute("step")), curValue = parseInt(input.value, 10), delta = e.delta ||
                (isKeyDown ? (e.which === 38 ? 1 : -1) : 0);
            var newValue = curValue + step * delta;
            if (typeof input.value !== "undefined" && input.value.length === 2) {
                var isHourElem = input === self.hourElement, isMinuteElem = input === self.minuteElement;
                if (newValue < min) {
                    newValue =
                        max +
                            newValue +
                            (0, utils_1.int)(!isHourElem) +
                            ((0, utils_1.int)(isHourElem) && (0, utils_1.int)(!self.amPM));
                    if (isMinuteElem)
                        incrementNumInput(undefined, -1, self.hourElement);
                }
                else if (newValue > max) {
                    newValue =
                        input === self.hourElement ? newValue - max - (0, utils_1.int)(!self.amPM) : min;
                    if (isMinuteElem)
                        incrementNumInput(undefined, 1, self.hourElement);
                }
                if (self.amPM &&
                    isHourElem &&
                    (step === 1
                        ? newValue + curValue === 23
                        : Math.abs(newValue - curValue) > step)) {
                    self.amPM.textContent =
                        self.l10n.amPM[(0, utils_1.int)(self.amPM.textContent === self.l10n.amPM[0])];
                }
                input.value = (0, utils_1.pad)(newValue);
            }
        }
        init();
        return self;
    }
    function _flatpickr(nodeList, config) {
        var nodes = Array.prototype.slice
            .call(nodeList)
            .filter(function (x) { return x instanceof HTMLElement; });
        var instances = [];
        for (var i = 0; i < nodes.length; i++) {
            var node = nodes[i];
            try {
                if (node.getAttribute("data-fp-omit") !== null)
                    continue;
                if (node._flatpickr !== undefined) {
                    node._flatpickr.destroy();
                    node._flatpickr = undefined;
                }
                node._flatpickr = FlatpickrInstance(node, config || {});
                instances.push(node._flatpickr);
            }
            catch (e) {
                console.error(e);
            }
        }
        return instances.length === 1 ? instances[0] : instances;
    }
    if (typeof HTMLElement !== "undefined" &&
        typeof HTMLCollection !== "undefined" &&
        typeof NodeList !== "undefined") {
        HTMLCollection.prototype.flatpickr = NodeList.prototype.flatpickr = function (config) {
            return _flatpickr(this, config);
        };
        HTMLElement.prototype.flatpickr = function (config) {
            return _flatpickr([this], config);
        };
    }
    var flatpickr = function (selector, config) {
        if (typeof selector === "string") {
            return _flatpickr(window.document.querySelectorAll(selector), config);
        }
        else if (selector instanceof Node) {
            return _flatpickr([selector], config);
        }
        else {
            return _flatpickr(selector, config);
        }
    };
    flatpickr.defaultConfig = {};
    flatpickr.l10ns = {
        en: __assign({}, default_1.default),
        default: __assign({}, default_1.default),
    };
    flatpickr.localize = function (l10n) {
        flatpickr.l10ns.default = __assign(__assign({}, flatpickr.l10ns.default), l10n);
    };
    flatpickr.setDefaults = function (config) {
        flatpickr.defaultConfig = __assign(__assign({}, flatpickr.defaultConfig), config);
    };
    flatpickr.parseDate = (0, dates_1.createDateParser)({});
    flatpickr.formatDate = (0, dates_1.createDateFormatter)({});
    flatpickr.compareDates = dates_1.compareDates;
    if (typeof jQuery !== "undefined" && typeof jQuery.fn !== "undefined") {
        jQuery.fn.flatpickr = function (config) {
            return _flatpickr(this, config);
        };
    }
    Date.prototype.fp_incr = function (days) {
        return new Date(this.getFullYear(), this.getMonth(), this.getDate() + (typeof days === "string" ? parseInt(days, 10) : days));
    };
    if (typeof window !== "undefined") {
        window.flatpickr = flatpickr;
    }
    exports.default = flatpickr;
},
"651d495396": /* flatpickr/dist/esm/types/options.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    exports.HOOKS = [
        "onChange",
        "onClose",
        "onDayCreate",
        "onDestroy",
        "onKeyDown",
        "onMonthChange",
        "onOpen",
        "onParseConfig",
        "onReady",
        "onValueUpdate",
        "onYearChange",
        "onPreCalendarPosition",
    ];
    exports.defaults = {
        _disable: [],
        allowInput: false,
        allowInvalidPreload: false,
        altFormat: "F j, Y",
        altInput: false,
        altInputClass: "form-control input",
        animate: typeof window === "object" &&
            window.navigator.userAgent.indexOf("MSIE") === -1,
        ariaDateFormat: "F j, Y",
        autoFillDefaultTime: true,
        clickOpens: true,
        closeOnSelect: true,
        conjunction: ", ",
        dateFormat: "Y-m-d",
        defaultHour: 12,
        defaultMinute: 0,
        defaultSeconds: 0,
        disable: [],
        disableMobile: false,
        enableSeconds: false,
        enableTime: false,
        errorHandler: function (err) {
            return typeof console !== "undefined" && console.warn(err);
        },
        getWeek: function (givenDate) {
            var date = new Date(givenDate.getTime());
            date.setHours(0, 0, 0, 0);
            date.setDate(date.getDate() + 3 - ((date.getDay() + 6) % 7));
            var week1 = new Date(date.getFullYear(), 0, 4);
            return (1 +
                Math.round(((date.getTime() - week1.getTime()) / 86400000 -
                    3 +
                    ((week1.getDay() + 6) % 7)) /
                    7));
        },
        hourIncrement: 1,
        ignoredFocusElements: [],
        inline: false,
        locale: "default",
        minuteIncrement: 5,
        mode: "single",
        monthSelectorType: "dropdown",
        nextArrow: "<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 17 17'><g></g><path d='M13.207 8.472l-7.854 7.854-0.707-0.707 7.146-7.146-7.146-7.148 0.707-0.707 7.854 7.854z' /></svg>",
        noCalendar: false,
        now: new Date(),
        onChange: [],
        onClose: [],
        onDayCreate: [],
        onDestroy: [],
        onKeyDown: [],
        onMonthChange: [],
        onOpen: [],
        onParseConfig: [],
        onReady: [],
        onValueUpdate: [],
        onYearChange: [],
        onPreCalendarPosition: [],
        plugins: [],
        position: "auto",
        positionElement: undefined,
        prevArrow: "<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 17 17'><g></g><path d='M5.207 8.471l7.146 7.147-0.707 0.707-7.853-7.854 7.854-7.853 0.707 0.707-7.147 7.146z' /></svg>",
        shorthandCurrentMonth: false,
        showMonths: 1,
        static: false,
        time_24hr: false,
        weekNumbers: false,
        wrap: false,
    };
},
"3bfa124fda": /* flatpickr/dist/esm/l10n/default.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    exports.english = {
        weekdays: {
            shorthand: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            longhand: [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ],
        },
        months: {
            shorthand: [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ],
            longhand: [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
        },
        daysInMonth: [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31],
        firstDayOfWeek: 0,
        ordinal: function (nth) {
            var s = nth % 100;
            if (s > 3 && s < 21)
                return "th";
            switch (s % 10) {
                case 1:
                    return "st";
                case 2:
                    return "nd";
                case 3:
                    return "rd";
                default:
                    return "th";
            }
        },
        rangeSeparator: " to ",
        weekAbbreviation: "Wk",
        scrollTitle: "Scroll to increment",
        toggleTitle: "Click to toggle",
        amPM: ["AM", "PM"],
        yearAriaLabel: "Year",
        monthAriaLabel: "Month",
        hourAriaLabel: "Hour",
        minuteAriaLabel: "Minute",
        time_24hr: false,
    };
    exports.default = exports.english;
},
"15458073ce": /* flatpickr/dist/esm/utils/index.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    var pad = function (number, length) {
        if (length === void 0) {
            length = 2;
        }
        return ("000" + number).slice(length * -1);
    };
    exports.pad = pad;
    var int = function (bool) { return (bool === true ? 1 : 0); };
    exports.int = int;
    function debounce(fn, wait) {
        var t;
        return function () {
            var _this = this;
            var args = arguments;
            clearTimeout(t);
            t = setTimeout(function () { return fn.apply(_this, args); }, wait);
        };
    }
    exports.debounce = debounce;
    var arrayify = function (obj) {
        return obj instanceof Array ? obj : [obj];
    };
    exports.arrayify = arrayify;
},
"6b6749c6cf": /* flatpickr/dist/esm/utils/dom.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    function toggleClass(elem, className, bool) {
        if (bool === true)
            return elem.classList.add(className);
        elem.classList.remove(className);
    }
    exports.toggleClass = toggleClass;
    function createElement(tag, className, content) {
        var e = window.document.createElement(tag);
        className = className || "";
        content = content || "";
        e.className = className;
        if (content !== undefined)
            e.textContent = content;
        return e;
    }
    exports.createElement = createElement;
    function clearNode(node) {
        while (node.firstChild)
            node.removeChild(node.firstChild);
    }
    exports.clearNode = clearNode;
    function findParent(node, condition) {
        if (condition(node))
            return node;
        else if (node.parentNode)
            return findParent(node.parentNode, condition);
        return undefined;
    }
    exports.findParent = findParent;
    function createNumberInput(inputClassName, opts) {
        var wrapper = createElement("div", "numInputWrapper"), numInput = createElement("input", "numInput " + inputClassName), arrowUp = createElement("span", "arrowUp"), arrowDown = createElement("span", "arrowDown");
        if (navigator.userAgent.indexOf("MSIE 9.0") === -1) {
            numInput.type = "number";
        }
        else {
            numInput.type = "text";
            numInput.pattern = "\\d*";
        }
        if (opts !== undefined)
            for (var key in opts)
                numInput.setAttribute(key, opts[key]);
        wrapper.appendChild(numInput);
        wrapper.appendChild(arrowUp);
        wrapper.appendChild(arrowDown);
        return wrapper;
    }
    exports.createNumberInput = createNumberInput;
    function getEventTarget(event) {
        try {
            if (typeof event.composedPath === "function") {
                var path = event.composedPath();
                return path[0];
            }
            return event.target;
        }
        catch (error) {
            return event.target;
        }
    }
    exports.getEventTarget = getEventTarget;
},
"1bb8c967d1": /* flatpickr/dist/esm/utils/dates.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const formatting_1 = require("3d14787c35") /* ./formatting */;
    const options_1 = require("651d495396") /* ../types/options */;
    const default_1 = require("3bfa124fda") /* ../l10n/default */;
    var createDateFormatter = function (_a) {
        var _b = _a.config, config = _b === void 0 ? options_1.defaults : _b, _c = _a.l10n, l10n = _c === void 0 ? default_1.english : _c, _d = _a.isMobile, isMobile = _d === void 0 ? false : _d;
        return function (dateObj, frmt, overrideLocale) {
            var locale = overrideLocale || l10n;
            if (config.formatDate !== undefined && !isMobile) {
                return config.formatDate(dateObj, frmt, locale);
            }
            return frmt
                .split("")
                .map(function (c, i, arr) {
                return formatting_1.formats[c] && arr[i - 1] !== "\\"
                    ? formatting_1.formats[c](dateObj, locale, config)
                    : c !== "\\"
                        ? c
                        : "";
            })
                .join("");
        };
    };
    exports.createDateFormatter = createDateFormatter;
    var createDateParser = function (_a) {
        var _b = _a.config, config = _b === void 0 ? options_1.defaults : _b, _c = _a.l10n, l10n = _c === void 0 ? default_1.english : _c;
        return function (date, givenFormat, timeless, customLocale) {
            if (date !== 0 && !date)
                return undefined;
            var locale = customLocale || l10n;
            var parsedDate;
            var dateOrig = date;
            if (date instanceof Date)
                parsedDate = new Date(date.getTime());
            else if (typeof date !== "string" &&
                date.toFixed !== undefined)
                parsedDate = new Date(date);
            else if (typeof date === "string") {
                var format = givenFormat || (config || options_1.defaults).dateFormat;
                var datestr = String(date).trim();
                if (datestr === "today") {
                    parsedDate = new Date();
                    timeless = true;
                }
                else if (config && config.parseDate) {
                    parsedDate = config.parseDate(date, format);
                }
                else if (/Z$/.test(datestr) ||
                    /GMT$/.test(datestr)) {
                    parsedDate = new Date(date);
                }
                else {
                    var matched = void 0, ops = [];
                    for (var i = 0, matchIndex = 0, regexStr = ""; i < format.length; i++) {
                        var token = format[i];
                        var isBackSlash = token === "\\";
                        var escaped = format[i - 1] === "\\" || isBackSlash;
                        if (formatting_1.tokenRegex[token] && !escaped) {
                            regexStr += formatting_1.tokenRegex[token];
                            var match = new RegExp(regexStr).exec(date);
                            if (match && (matched = true)) {
                                ops[token !== "Y" ? "push" : "unshift"]({
                                    fn: formatting_1.revFormat[token],
                                    val: match[++matchIndex],
                                });
                            }
                        }
                        else if (!isBackSlash)
                            regexStr += ".";
                    }
                    parsedDate =
                        !config || !config.noCalendar
                            ? new Date(new Date().getFullYear(), 0, 1, 0, 0, 0, 0)
                            : new Date(new Date().setHours(0, 0, 0, 0));
                    ops.forEach(function (_a) {
                        var fn = _a.fn, val = _a.val;
                        return (parsedDate = fn(parsedDate, val, locale) || parsedDate);
                    });
                    parsedDate = matched ? parsedDate : undefined;
                }
            }
            if (!(parsedDate instanceof Date && !isNaN(parsedDate.getTime()))) {
                config.errorHandler(new Error("Invalid date provided: " + dateOrig));
                return undefined;
            }
            if (timeless === true)
                parsedDate.setHours(0, 0, 0, 0);
            return parsedDate;
        };
    };
    exports.createDateParser = createDateParser;
    function compareDates(date1, date2, timeless) {
        if (timeless === void 0) {
            timeless = true;
        }
        if (timeless !== false) {
            return (new Date(date1.getTime()).setHours(0, 0, 0, 0) -
                new Date(date2.getTime()).setHours(0, 0, 0, 0));
        }
        return date1.getTime() - date2.getTime();
    }
    exports.compareDates = compareDates;
    function compareTimes(date1, date2) {
        return (3600 * (date1.getHours() - date2.getHours()) +
            60 * (date1.getMinutes() - date2.getMinutes()) +
            date1.getSeconds() -
            date2.getSeconds());
    }
    exports.compareTimes = compareTimes;
    var isBetween = function (ts, ts1, ts2) {
        return ts > Math.min(ts1, ts2) && ts < Math.max(ts1, ts2);
    };
    exports.isBetween = isBetween;
    var calculateSecondsSinceMidnight = function (hours, minutes, seconds) {
        return hours * 3600 + minutes * 60 + seconds;
    };
    exports.calculateSecondsSinceMidnight = calculateSecondsSinceMidnight;
    var parseSeconds = function (secondsSinceMidnight) {
        var hours = Math.floor(secondsSinceMidnight / 3600), minutes = (secondsSinceMidnight - hours * 3600) / 60;
        return [hours, minutes, secondsSinceMidnight - hours * 3600 - minutes * 60];
    };
    exports.parseSeconds = parseSeconds;
    exports.duration = {
        DAY: 86400000,
    };
    function getDefaultHours(config) {
        var hours = config.defaultHour;
        var minutes = config.defaultMinute;
        var seconds = config.defaultSeconds;
        if (config.minDate !== undefined) {
            var minHour = config.minDate.getHours();
            var minMinutes = config.minDate.getMinutes();
            var minSeconds = config.minDate.getSeconds();
            if (hours < minHour) {
                hours = minHour;
            }
            if (hours === minHour && minutes < minMinutes) {
                minutes = minMinutes;
            }
            if (hours === minHour && minutes === minMinutes && seconds < minSeconds)
                seconds = config.minDate.getSeconds();
        }
        if (config.maxDate !== undefined) {
            var maxHr = config.maxDate.getHours();
            var maxMinutes = config.maxDate.getMinutes();
            hours = Math.min(hours, maxHr);
            if (hours === maxHr)
                minutes = Math.min(maxMinutes, minutes);
            if (hours === maxHr && minutes === maxMinutes)
                seconds = config.maxDate.getSeconds();
        }
        return { hours: hours, minutes: minutes, seconds: seconds };
    }
    exports.getDefaultHours = getDefaultHours;
},
"3d14787c35": /* flatpickr/dist/esm/utils/formatting.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const utils_1 = require("15458073ce") /* ../utils */;
    var doNothing = function () { return undefined; };
    var monthToStr = function (monthNumber, shorthand, locale) { return locale.months[shorthand ? "shorthand" : "longhand"][monthNumber]; };
    exports.monthToStr = monthToStr;
    exports.revFormat = {
        D: doNothing,
        F: function (dateObj, monthName, locale) {
            dateObj.setMonth(locale.months.longhand.indexOf(monthName));
        },
        G: function (dateObj, hour) {
            dateObj.setHours((dateObj.getHours() >= 12 ? 12 : 0) + parseFloat(hour));
        },
        H: function (dateObj, hour) {
            dateObj.setHours(parseFloat(hour));
        },
        J: function (dateObj, day) {
            dateObj.setDate(parseFloat(day));
        },
        K: function (dateObj, amPM, locale) {
            dateObj.setHours((dateObj.getHours() % 12) +
                12 * (0, utils_1.int)(new RegExp(locale.amPM[1], "i").test(amPM)));
        },
        M: function (dateObj, shortMonth, locale) {
            dateObj.setMonth(locale.months.shorthand.indexOf(shortMonth));
        },
        S: function (dateObj, seconds) {
            dateObj.setSeconds(parseFloat(seconds));
        },
        U: function (_, unixSeconds) { return new Date(parseFloat(unixSeconds) * 1000); },
        W: function (dateObj, weekNum, locale) {
            var weekNumber = parseInt(weekNum);
            var date = new Date(dateObj.getFullYear(), 0, 2 + (weekNumber - 1) * 7, 0, 0, 0, 0);
            date.setDate(date.getDate() - date.getDay() + locale.firstDayOfWeek);
            return date;
        },
        Y: function (dateObj, year) {
            dateObj.setFullYear(parseFloat(year));
        },
        Z: function (_, ISODate) { return new Date(ISODate); },
        d: function (dateObj, day) {
            dateObj.setDate(parseFloat(day));
        },
        h: function (dateObj, hour) {
            dateObj.setHours((dateObj.getHours() >= 12 ? 12 : 0) + parseFloat(hour));
        },
        i: function (dateObj, minutes) {
            dateObj.setMinutes(parseFloat(minutes));
        },
        j: function (dateObj, day) {
            dateObj.setDate(parseFloat(day));
        },
        l: doNothing,
        m: function (dateObj, month) {
            dateObj.setMonth(parseFloat(month) - 1);
        },
        n: function (dateObj, month) {
            dateObj.setMonth(parseFloat(month) - 1);
        },
        s: function (dateObj, seconds) {
            dateObj.setSeconds(parseFloat(seconds));
        },
        u: function (_, unixMillSeconds) {
            return new Date(parseFloat(unixMillSeconds));
        },
        w: doNothing,
        y: function (dateObj, year) {
            dateObj.setFullYear(2000 + parseFloat(year));
        },
    };
    exports.tokenRegex = {
        D: "",
        F: "",
        G: "(\\d\\d|\\d)",
        H: "(\\d\\d|\\d)",
        J: "(\\d\\d|\\d)\\w+",
        K: "",
        M: "",
        S: "(\\d\\d|\\d)",
        U: "(.+)",
        W: "(\\d\\d|\\d)",
        Y: "(\\d{4})",
        Z: "(.+)",
        d: "(\\d\\d|\\d)",
        h: "(\\d\\d|\\d)",
        i: "(\\d\\d|\\d)",
        j: "(\\d\\d|\\d)",
        l: "",
        m: "(\\d\\d|\\d)",
        n: "(\\d\\d|\\d)",
        s: "(\\d\\d|\\d)",
        u: "(.+)",
        w: "(\\d\\d|\\d)",
        y: "(\\d{2})",
    };
    exports.formats = {
        Z: function (date) { return date.toISOString(); },
        D: function (date, locale, options) {
            return locale.weekdays.shorthand[exports.formats.w(date, locale, options)];
        },
        F: function (date, locale, options) {
            return (0, exports.monthToStr)(exports.formats.n(date, locale, options) - 1, false, locale);
        },
        G: function (date, locale, options) {
            return (0, utils_1.pad)(exports.formats.h(date, locale, options));
        },
        H: function (date) { return (0, utils_1.pad)(date.getHours()); },
        J: function (date, locale) {
            return locale.ordinal !== undefined
                ? date.getDate() + locale.ordinal(date.getDate())
                : date.getDate();
        },
        K: function (date, locale) { return locale.amPM[(0, utils_1.int)(date.getHours() > 11)]; },
        M: function (date, locale) {
            return (0, exports.monthToStr)(date.getMonth(), true, locale);
        },
        S: function (date) { return (0, utils_1.pad)(date.getSeconds()); },
        U: function (date) { return date.getTime() / 1000; },
        W: function (date, _, options) {
            return options.getWeek(date);
        },
        Y: function (date) { return (0, utils_1.pad)(date.getFullYear(), 4); },
        d: function (date) { return (0, utils_1.pad)(date.getDate()); },
        h: function (date) { return (date.getHours() % 12 ? date.getHours() % 12 : 12); },
        i: function (date) { return (0, utils_1.pad)(date.getMinutes()); },
        j: function (date) { return date.getDate(); },
        l: function (date, locale) {
            return locale.weekdays.longhand[date.getDay()];
        },
        m: function (date) { return (0, utils_1.pad)(date.getMonth() + 1); },
        n: function (date) { return date.getMonth() + 1; },
        s: function (date) { return date.getSeconds(); },
        u: function (date) { return date.getTime(); },
        w: function (date) { return date.getDay(); },
        y: function (date) { return String(date.getFullYear()).substring(2); },
    };
},
"6f45019dc1": /* flatpickr/dist/esm/utils/polyfills.js */ function _(require, module, exports, __esModule, __esExport) {
    if (typeof Object.assign !== "function") {
        Object.assign = function (target) {
            var args = [];
            for (var _i = 1; _i < arguments.length; _i++) {
                args[_i - 1] = arguments[_i];
            }
            if (!target) {
                throw TypeError("Cannot convert undefined or null to object");
            }
            var _loop_1 = function (source) {
                if (source) {
                    Object.keys(source).forEach(function (key) { return (target[key] = source[key]); });
                }
            };
            for (var _a = 0, args_1 = args; _a < args_1.length; _a++) {
                var source = args_1[_a];
                _loop_1(source);
            }
            return target;
        };
    }
},
"dc03aab885": /* models/deckgl.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tslib_1 = require("tslib");
    const dom_1 = require("@bokehjs/core/dom");
    const types_1 = require("@bokehjs/core/util/types");
    const column_data_source_1 = require("@bokehjs/models/sources/column_data_source");
    const debounce_1 = require("99a25e6992") /* debounce */;
    const data_1 = require("be689f0377") /* ./data */;
    const layout_dom_1 = require("@bokehjs/models/layouts/layout_dom");
    const tooltips_1 = require("f8f8ea4284") /* ./tooltips */;
    const constants_1 = tslib_1.__importDefault(require("d970fa7374") /* @luma.gl/constants */);
    function extractClasses() {
        // Get classes for registration from standalone deck.gl
        const classesDict = {};
        const deck = window.deck;
        const classes = Object.keys(deck).filter(x => x.charAt(0) === x.charAt(0).toUpperCase());
        for (const cls of classes) {
            classesDict[cls] = deck[cls];
        }
        return classesDict;
    }
    class DeckGLPlotView extends layout_dom_1.LayoutDOMView {
        connect_signals() {
            super.connect_signals();
            const { data, mapbox_api_key, tooltip, layers, initialViewState, data_sources } = this.model.properties;
            this.on_change([mapbox_api_key, tooltip], () => this.render());
            this.on_change([data, initialViewState], () => this.updateDeck());
            this.on_change([layers], () => this._update_layers());
            this.on_change([data_sources], () => this._connect_sources(true));
            this._layer_map = {};
            this._connected = [];
            this._connect_sources();
        }
        remove() {
            this.deckGL.finalize();
            super.remove();
        }
        _update_layers() {
            this._layer_map = {};
            this._update_data(true);
        }
        _connect_sources(render = false) {
            for (const cds of this.model.data_sources) {
                if (this._connected.indexOf(cds) < 0) {
                    this.on_change(cds.properties.data, () => this._update_data(true));
                    this._connected.push(cds);
                }
            }
            this._update_data(render);
        }
        initialize() {
            super.initialize();
            if (window.deck.JSONConverter) {
                const { CSVLoader, Tiles3DLoader } = window.loaders;
                window.loaders.registerLoaders([Tiles3DLoader, CSVLoader]);
                const jsonConverterConfiguration = {
                    classes: extractClasses(),
                    // Will be resolved as `<enum-name>.<enum-value>`
                    enumerations: {
                        COORDINATE_SYSTEM: window.deck.COORDINATE_SYSTEM,
                        GL: constants_1.default,
                    },
                    // Constants that should be resolved with the provided values by JSON converter
                    constants: {
                        Tiles3DLoader,
                    },
                };
                this.jsonConverter = new window.deck.JSONConverter({
                    configuration: jsonConverterConfiguration,
                });
            }
        }
        _update_data(render = true) {
            let n = 0;
            for (const layer of this.model.layers) {
                let cds;
                n += 1;
                if ((n - 1) in this._layer_map) {
                    cds = this.model.data_sources[this._layer_map[n - 1]];
                }
                else if (!(0, types_1.isNumber)(layer.data)) {
                    continue;
                }
                else {
                    this._layer_map[n - 1] = layer.data;
                    cds = this.model.data_sources[layer.data];
                }
                layer.data = (0, data_1.transform_cds_to_records)(cds);
            }
            if (render) {
                this.updateDeck();
            }
        }
        _on_click_event(event) {
            const click_state = {
                coordinate: event.coordinate,
                lngLat: event.coordinate,
                index: event.index,
            };
            if (event.layer) {
                click_state.layer = event.layer.id;
            }
            this.model.clickState = click_state;
        }
        _on_hover_event(event) {
            if (event.coordinate == null) {
                return;
            }
            const hover_state = {
                coordinate: event.coordinate,
                lngLat: event.coordinate,
                index: event.index,
            };
            if (event.layer) {
                hover_state.layer = event.layer.id;
            }
            this.model.hoverState = hover_state;
        }
        _on_viewState_event(event) {
            const view_state = { ...event.viewState };
            delete view_state.normalize;
            for (const p in view_state) {
                if (p.startsWith("transition")) {
                    delete view_state[p];
                }
            }
            const viewport = new window.deck.WebMercatorViewport(view_state);
            view_state.nw = viewport.unproject([0, 0]);
            view_state.se = viewport.unproject([viewport.width, viewport.height]);
            this.model.viewState = view_state;
        }
        get child_models() {
            return [];
        }
        getData() {
            const view_timeout = this.model.throttle.view || 200;
            const hover_timeout = this.model.throttle.hover || 100;
            const view_cb = (0, debounce_1.debounce)((event) => this._on_viewState_event(event), view_timeout, false);
            const hover_cb = (0, debounce_1.debounce)((event) => this._on_hover_event(event), hover_timeout, false);
            const data = {
                ...this.model.data,
                layers: this.model.layers,
                initialViewState: this.model.initialViewState,
                onViewStateChange: view_cb,
                onClick: (event) => this._on_click_event(event),
                onHover: hover_cb,
            };
            return data;
        }
        updateDeck() {
            if (!this.deckGL) {
                this.render();
                return;
            }
            const data = this.getData();
            if (window.deck.updateDeck) {
                window.deck.updateDeck(data, this.deckGL);
            }
            else {
                const results = this.jsonConverter.convert(data);
                this.deckGL.setProps(results);
            }
        }
        createDeck({ mapboxApiKey, container, jsonInput, tooltip }) {
            let deckgl;
            try {
                const props = this.jsonConverter.convert(jsonInput);
                const getTooltip = (0, tooltips_1.makeTooltip)(tooltip, props.layers);
                deckgl = new window.deck.DeckGL({
                    ...props,
                    map: window.mapboxgl,
                    mapboxApiAccessToken: mapboxApiKey,
                    container,
                    getTooltip,
                    width: "100%",
                    height: "100%",
                });
            }
            catch (err) {
                console.error(err);
            }
            return deckgl;
        }
        render() {
            super.render();
            const container = (0, dom_1.div)({ class: "deckgl" });
            const MAPBOX_API_KEY = this.model.mapbox_api_key;
            const tooltip = this.model.tooltip;
            const data = this.getData();
            if (window.deck.createDeck) {
                this.deckGL = window.deck.createDeck({
                    mapboxApiKey: MAPBOX_API_KEY,
                    container,
                    jsonInput: data,
                    tooltip,
                });
            }
            else {
                this.deckGL = this.createDeck({
                    mapboxApiKey: MAPBOX_API_KEY,
                    container,
                    jsonInput: data,
                    tooltip,
                });
            }
            this.shadow_el.appendChild(container);
        }
        after_layout() {
            super.after_layout();
            this.deckGL.redraw(true);
        }
    }
    exports.DeckGLPlotView = DeckGLPlotView;
    DeckGLPlotView.__name__ = "DeckGLPlotView";
    class DeckGLPlot extends layout_dom_1.LayoutDOM {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.DeckGLPlot = DeckGLPlot;
    _a = DeckGLPlot;
    DeckGLPlot.__name__ = "DeckGLPlot";
    DeckGLPlot.__module__ = "panel.models.deckgl";
    (() => {
        _a.prototype.default_view = DeckGLPlotView;
        _a.define(({ Any, List, Str, Ref }) => ({
            data: [Any],
            data_sources: [List(Ref(column_data_source_1.ColumnDataSource)), []],
            clickState: [Any, {}],
            hoverState: [Any, {}],
            initialViewState: [Any, {}],
            layers: [List(Any), []],
            mapbox_api_key: [Str, ""],
            throttle: [Any, {}],
            tooltip: [Any, true],
            viewState: [Any, {}],
        }));
        _a.override({
            height: 400,
            width: 600,
        });
    })();
},
"f8f8ea4284": /* models/tooltips.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    /*
    This file was adapted from https://github.com/uber/deck.gl/ the LICENSE
    below is preserved to comply with the original license.
    
    Copyright (c) 2015 - 2017 Uber Technologies, Inc.
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
    */
    const types_1 = require("@bokehjs/core/util/types");
    /* global document */
    let lastPickedObject;
    let lastTooltip;
    const DEFAULT_STYLE = {
        fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
        display: "flex",
        flex: "wrap",
        maxWidth: "500px",
        flexDirection: "column",
        zIndex: 2,
    };
    function getDiv() {
        return document.createElement("div");
    }
    function getTooltipDefault(pickedInfo) {
        if (!pickedInfo.picked) {
            return null;
        }
        if (pickedInfo.object === lastPickedObject) {
            return lastTooltip;
        }
        const tooltip = {
            html: tabularize(pickedInfo.object),
            style: DEFAULT_STYLE,
        };
        lastTooltip = tooltip;
        lastPickedObject = pickedInfo.object;
        return tooltip;
    }
    exports.getTooltipDefault = getTooltipDefault;
    const EXCLUDES = new Set(["position", "index"]);
    function tabularize(json) {
        // Turns a JSON object of picked info into HTML for a tooltip
        const dataTable = getDiv();
        // Creates rows of two columns for the tooltip
        for (const key in json) {
            if (EXCLUDES.has(key)) {
                continue; // eslint-disable-line
            }
            const header = getDiv();
            header.className = "header";
            header.textContent = key;
            const valueElement = getDiv();
            valueElement.className = "value";
            valueElement.textContent = toText(json[key]);
            const row = getDiv();
            setStyles(row, header, valueElement);
            row.appendChild(header);
            row.appendChild(valueElement);
            dataTable.appendChild(row);
        }
        return dataTable.innerHTML;
    }
    exports.tabularize = tabularize;
    function setStyles(row, header, value) {
        // Set default tooltip style
        Object.assign(header.style, {
            fontWeight: 700,
            marginRight: "10px",
            flex: "1 1 0%",
        });
        Object.assign(value.style, {
            flex: "none",
            maxWidth: "250px",
            overflow: "hidden",
            whiteSpace: "nowrap",
            textOverflow: "ellipsis",
        });
        Object.assign(row.style, {
            display: "flex",
            flexDirection: "row",
            justifyContent: "space-between",
            alignItems: "stretch",
        });
    }
    function toText(jsonValue) {
        // Set contents of table value, trimming for certain types of data
        let text;
        if (Array.isArray(jsonValue) && jsonValue.length > 4) {
            text = `Array<${jsonValue.length}>`;
        }
        else if ((0, types_1.isString)(jsonValue)) {
            text = jsonValue;
        }
        else if ((0, types_1.isNumber)(jsonValue)) {
            text = String(jsonValue);
        }
        else {
            try {
                text = JSON.stringify(jsonValue);
            }
            catch (err) {
                text = "<Non-Serializable Object>";
            }
        }
        const MAX_LENGTH = 50;
        if (text.length > MAX_LENGTH) {
            text = text.slice(0, MAX_LENGTH);
        }
        return text;
    }
    exports.toText = toText;
    function substituteIn(template, json) {
        let output = template;
        for (const key in json) {
            if ((0, types_1.isPlainObject)(json[key])) {
                for (const subkey in json[key]) {
                    output = output.replace(`{${key}.${subkey}}`, json[key][subkey]);
                }
            }
            output = output.replace(`{${key}}`, json[key]);
        }
        return output;
    }
    exports.substituteIn = substituteIn;
    function makeTooltip(tooltips, layers) {
        /*
         * If explicitly no tooltip passed by user, return null
         * If a JSON object passed, return a tooltip based on that object
         *   We expect the user has passed a string template that will take pickedInfo keywords
         * If a boolean passed, return the default tooltip
         */
        if (!tooltips) {
            return null;
        }
        let per_layer = false;
        const layer_tooltips = {};
        for (let i = 0; i < layers.length; i++) {
            const layer = layers[i];
            const layer_id = layer.id;
            if (!(0, types_1.isBoolean)(tooltips) && (i.toString() in tooltips || layer_id in tooltips)) {
                layer_tooltips[layer_id] = layer_id in tooltips ? tooltips[layer_id] : tooltips[i.toString()];
                per_layer = true;
            }
        }
        if (tooltips.html || tooltips.text || per_layer) {
            return (pickedInfo) => {
                if (!pickedInfo.picked) {
                    return null;
                }
                const tooltip = (per_layer) ? layer_tooltips[pickedInfo.layer.id] : tooltips;
                if (tooltip == null) {
                    return;
                }
                else if ((0, types_1.isBoolean)(tooltip)) {
                    return tooltip ? getTooltipDefault(pickedInfo) : null;
                }
                const formattedTooltip = {
                    style: tooltip.style || DEFAULT_STYLE,
                };
                if (tooltip.html) {
                    formattedTooltip.html = substituteIn(tooltip.html, pickedInfo.object);
                }
                else {
                    formattedTooltip.text = substituteIn(tooltip.text, pickedInfo.object);
                }
                return formattedTooltip;
            };
        }
        return getTooltipDefault;
    }
    exports.makeTooltip = makeTooltip;
},
"d970fa7374": /* @luma.gl/constants/dist/esm/index.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    exports.default = {
        DEPTH_BUFFER_BIT: 0x00000100,
        STENCIL_BUFFER_BIT: 0x00000400,
        COLOR_BUFFER_BIT: 0x00004000,
        POINTS: 0x0000,
        LINES: 0x0001,
        LINE_LOOP: 0x0002,
        LINE_STRIP: 0x0003,
        TRIANGLES: 0x0004,
        TRIANGLE_STRIP: 0x0005,
        TRIANGLE_FAN: 0x0006,
        ZERO: 0,
        ONE: 1,
        SRC_COLOR: 0x0300,
        ONE_MINUS_SRC_COLOR: 0x0301,
        SRC_ALPHA: 0x0302,
        ONE_MINUS_SRC_ALPHA: 0x0303,
        DST_ALPHA: 0x0304,
        ONE_MINUS_DST_ALPHA: 0x0305,
        DST_COLOR: 0x0306,
        ONE_MINUS_DST_COLOR: 0x0307,
        SRC_ALPHA_SATURATE: 0x0308,
        CONSTANT_COLOR: 0x8001,
        ONE_MINUS_CONSTANT_COLOR: 0x8002,
        CONSTANT_ALPHA: 0x8003,
        ONE_MINUS_CONSTANT_ALPHA: 0x8004,
        FUNC_ADD: 0x8006,
        FUNC_SUBTRACT: 0x800a,
        FUNC_REVERSE_SUBTRACT: 0x800b,
        BLEND_EQUATION: 0x8009,
        BLEND_EQUATION_RGB: 0x8009,
        BLEND_EQUATION_ALPHA: 0x883d,
        BLEND_DST_RGB: 0x80c8,
        BLEND_SRC_RGB: 0x80c9,
        BLEND_DST_ALPHA: 0x80ca,
        BLEND_SRC_ALPHA: 0x80cb,
        BLEND_COLOR: 0x8005,
        ARRAY_BUFFER_BINDING: 0x8894,
        ELEMENT_ARRAY_BUFFER_BINDING: 0x8895,
        LINE_WIDTH: 0x0b21,
        ALIASED_POINT_SIZE_RANGE: 0x846d,
        ALIASED_LINE_WIDTH_RANGE: 0x846e,
        CULL_FACE_MODE: 0x0b45,
        FRONT_FACE: 0x0b46,
        DEPTH_RANGE: 0x0b70,
        DEPTH_WRITEMASK: 0x0b72,
        DEPTH_CLEAR_VALUE: 0x0b73,
        DEPTH_FUNC: 0x0b74,
        STENCIL_CLEAR_VALUE: 0x0b91,
        STENCIL_FUNC: 0x0b92,
        STENCIL_FAIL: 0x0b94,
        STENCIL_PASS_DEPTH_FAIL: 0x0b95,
        STENCIL_PASS_DEPTH_PASS: 0x0b96,
        STENCIL_REF: 0x0b97,
        STENCIL_VALUE_MASK: 0x0b93,
        STENCIL_WRITEMASK: 0x0b98,
        STENCIL_BACK_FUNC: 0x8800,
        STENCIL_BACK_FAIL: 0x8801,
        STENCIL_BACK_PASS_DEPTH_FAIL: 0x8802,
        STENCIL_BACK_PASS_DEPTH_PASS: 0x8803,
        STENCIL_BACK_REF: 0x8ca3,
        STENCIL_BACK_VALUE_MASK: 0x8ca4,
        STENCIL_BACK_WRITEMASK: 0x8ca5,
        VIEWPORT: 0x0ba2,
        SCISSOR_BOX: 0x0c10,
        COLOR_CLEAR_VALUE: 0x0c22,
        COLOR_WRITEMASK: 0x0c23,
        UNPACK_ALIGNMENT: 0x0cf5,
        PACK_ALIGNMENT: 0x0d05,
        MAX_TEXTURE_SIZE: 0x0d33,
        MAX_VIEWPORT_DIMS: 0x0d3a,
        SUBPIXEL_BITS: 0x0d50,
        RED_BITS: 0x0d52,
        GREEN_BITS: 0x0d53,
        BLUE_BITS: 0x0d54,
        ALPHA_BITS: 0x0d55,
        DEPTH_BITS: 0x0d56,
        STENCIL_BITS: 0x0d57,
        POLYGON_OFFSET_UNITS: 0x2a00,
        POLYGON_OFFSET_FACTOR: 0x8038,
        TEXTURE_BINDING_2D: 0x8069,
        SAMPLE_BUFFERS: 0x80a8,
        SAMPLES: 0x80a9,
        SAMPLE_COVERAGE_VALUE: 0x80aa,
        SAMPLE_COVERAGE_INVERT: 0x80ab,
        COMPRESSED_TEXTURE_FORMATS: 0x86a3,
        VENDOR: 0x1f00,
        RENDERER: 0x1f01,
        VERSION: 0x1f02,
        IMPLEMENTATION_COLOR_READ_TYPE: 0x8b9a,
        IMPLEMENTATION_COLOR_READ_FORMAT: 0x8b9b,
        BROWSER_DEFAULT_WEBGL: 0x9244,
        STATIC_DRAW: 0x88e4,
        STREAM_DRAW: 0x88e0,
        DYNAMIC_DRAW: 0x88e8,
        ARRAY_BUFFER: 0x8892,
        ELEMENT_ARRAY_BUFFER: 0x8893,
        BUFFER_SIZE: 0x8764,
        BUFFER_USAGE: 0x8765,
        CURRENT_VERTEX_ATTRIB: 0x8626,
        VERTEX_ATTRIB_ARRAY_ENABLED: 0x8622,
        VERTEX_ATTRIB_ARRAY_SIZE: 0x8623,
        VERTEX_ATTRIB_ARRAY_STRIDE: 0x8624,
        VERTEX_ATTRIB_ARRAY_TYPE: 0x8625,
        VERTEX_ATTRIB_ARRAY_NORMALIZED: 0x886a,
        VERTEX_ATTRIB_ARRAY_POINTER: 0x8645,
        VERTEX_ATTRIB_ARRAY_BUFFER_BINDING: 0x889f,
        CULL_FACE: 0x0b44,
        FRONT: 0x0404,
        BACK: 0x0405,
        FRONT_AND_BACK: 0x0408,
        BLEND: 0x0be2,
        DEPTH_TEST: 0x0b71,
        DITHER: 0x0bd0,
        POLYGON_OFFSET_FILL: 0x8037,
        SAMPLE_ALPHA_TO_COVERAGE: 0x809e,
        SAMPLE_COVERAGE: 0x80a0,
        SCISSOR_TEST: 0x0c11,
        STENCIL_TEST: 0x0b90,
        NO_ERROR: 0,
        INVALID_ENUM: 0x0500,
        INVALID_VALUE: 0x0501,
        INVALID_OPERATION: 0x0502,
        OUT_OF_MEMORY: 0x0505,
        CONTEXT_LOST_WEBGL: 0x9242,
        CW: 0x0900,
        CCW: 0x0901,
        DONT_CARE: 0x1100,
        FASTEST: 0x1101,
        NICEST: 0x1102,
        GENERATE_MIPMAP_HINT: 0x8192,
        BYTE: 0x1400,
        UNSIGNED_BYTE: 0x1401,
        SHORT: 0x1402,
        UNSIGNED_SHORT: 0x1403,
        INT: 0x1404,
        UNSIGNED_INT: 0x1405,
        FLOAT: 0x1406,
        DOUBLE: 0x140a,
        DEPTH_COMPONENT: 0x1902,
        ALPHA: 0x1906,
        RGB: 0x1907,
        RGBA: 0x1908,
        LUMINANCE: 0x1909,
        LUMINANCE_ALPHA: 0x190a,
        UNSIGNED_SHORT_4_4_4_4: 0x8033,
        UNSIGNED_SHORT_5_5_5_1: 0x8034,
        UNSIGNED_SHORT_5_6_5: 0x8363,
        FRAGMENT_SHADER: 0x8b30,
        VERTEX_SHADER: 0x8b31,
        COMPILE_STATUS: 0x8b81,
        DELETE_STATUS: 0x8b80,
        LINK_STATUS: 0x8b82,
        VALIDATE_STATUS: 0x8b83,
        ATTACHED_SHADERS: 0x8b85,
        ACTIVE_ATTRIBUTES: 0x8b89,
        ACTIVE_UNIFORMS: 0x8b86,
        MAX_VERTEX_ATTRIBS: 0x8869,
        MAX_VERTEX_UNIFORM_VECTORS: 0x8dfb,
        MAX_VARYING_VECTORS: 0x8dfc,
        MAX_COMBINED_TEXTURE_IMAGE_UNITS: 0x8b4d,
        MAX_VERTEX_TEXTURE_IMAGE_UNITS: 0x8b4c,
        MAX_TEXTURE_IMAGE_UNITS: 0x8872,
        MAX_FRAGMENT_UNIFORM_VECTORS: 0x8dfd,
        SHADER_TYPE: 0x8b4f,
        SHADING_LANGUAGE_VERSION: 0x8b8c,
        CURRENT_PROGRAM: 0x8b8d,
        NEVER: 0x0200,
        ALWAYS: 0x0207,
        LESS: 0x0201,
        EQUAL: 0x0202,
        LEQUAL: 0x0203,
        GREATER: 0x0204,
        GEQUAL: 0x0206,
        NOTEQUAL: 0x0205,
        KEEP: 0x1e00,
        REPLACE: 0x1e01,
        INCR: 0x1e02,
        DECR: 0x1e03,
        INVERT: 0x150a,
        INCR_WRAP: 0x8507,
        DECR_WRAP: 0x8508,
        NEAREST: 0x2600,
        LINEAR: 0x2601,
        NEAREST_MIPMAP_NEAREST: 0x2700,
        LINEAR_MIPMAP_NEAREST: 0x2701,
        NEAREST_MIPMAP_LINEAR: 0x2702,
        LINEAR_MIPMAP_LINEAR: 0x2703,
        TEXTURE_MAG_FILTER: 0x2800,
        TEXTURE_MIN_FILTER: 0x2801,
        TEXTURE_WRAP_S: 0x2802,
        TEXTURE_WRAP_T: 0x2803,
        TEXTURE_2D: 0x0de1,
        TEXTURE: 0x1702,
        TEXTURE_CUBE_MAP: 0x8513,
        TEXTURE_BINDING_CUBE_MAP: 0x8514,
        TEXTURE_CUBE_MAP_POSITIVE_X: 0x8515,
        TEXTURE_CUBE_MAP_NEGATIVE_X: 0x8516,
        TEXTURE_CUBE_MAP_POSITIVE_Y: 0x8517,
        TEXTURE_CUBE_MAP_NEGATIVE_Y: 0x8518,
        TEXTURE_CUBE_MAP_POSITIVE_Z: 0x8519,
        TEXTURE_CUBE_MAP_NEGATIVE_Z: 0x851a,
        MAX_CUBE_MAP_TEXTURE_SIZE: 0x851c,
        TEXTURE0: 0x84c0,
        ACTIVE_TEXTURE: 0x84e0,
        REPEAT: 0x2901,
        CLAMP_TO_EDGE: 0x812f,
        MIRRORED_REPEAT: 0x8370,
        TEXTURE_WIDTH: 0x1000,
        TEXTURE_HEIGHT: 0x1001,
        FLOAT_VEC2: 0x8b50,
        FLOAT_VEC3: 0x8b51,
        FLOAT_VEC4: 0x8b52,
        INT_VEC2: 0x8b53,
        INT_VEC3: 0x8b54,
        INT_VEC4: 0x8b55,
        BOOL: 0x8b56,
        BOOL_VEC2: 0x8b57,
        BOOL_VEC3: 0x8b58,
        BOOL_VEC4: 0x8b59,
        FLOAT_MAT2: 0x8b5a,
        FLOAT_MAT3: 0x8b5b,
        FLOAT_MAT4: 0x8b5c,
        SAMPLER_2D: 0x8b5e,
        SAMPLER_CUBE: 0x8b60,
        LOW_FLOAT: 0x8df0,
        MEDIUM_FLOAT: 0x8df1,
        HIGH_FLOAT: 0x8df2,
        LOW_INT: 0x8df3,
        MEDIUM_INT: 0x8df4,
        HIGH_INT: 0x8df5,
        FRAMEBUFFER: 0x8d40,
        RENDERBUFFER: 0x8d41,
        RGBA4: 0x8056,
        RGB5_A1: 0x8057,
        RGB565: 0x8d62,
        DEPTH_COMPONENT16: 0x81a5,
        STENCIL_INDEX: 0x1901,
        STENCIL_INDEX8: 0x8d48,
        DEPTH_STENCIL: 0x84f9,
        RENDERBUFFER_WIDTH: 0x8d42,
        RENDERBUFFER_HEIGHT: 0x8d43,
        RENDERBUFFER_INTERNAL_FORMAT: 0x8d44,
        RENDERBUFFER_RED_SIZE: 0x8d50,
        RENDERBUFFER_GREEN_SIZE: 0x8d51,
        RENDERBUFFER_BLUE_SIZE: 0x8d52,
        RENDERBUFFER_ALPHA_SIZE: 0x8d53,
        RENDERBUFFER_DEPTH_SIZE: 0x8d54,
        RENDERBUFFER_STENCIL_SIZE: 0x8d55,
        FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE: 0x8cd0,
        FRAMEBUFFER_ATTACHMENT_OBJECT_NAME: 0x8cd1,
        FRAMEBUFFER_ATTACHMENT_TEXTURE_LEVEL: 0x8cd2,
        FRAMEBUFFER_ATTACHMENT_TEXTURE_CUBE_MAP_FACE: 0x8cd3,
        COLOR_ATTACHMENT0: 0x8ce0,
        DEPTH_ATTACHMENT: 0x8d00,
        STENCIL_ATTACHMENT: 0x8d20,
        DEPTH_STENCIL_ATTACHMENT: 0x821a,
        NONE: 0,
        FRAMEBUFFER_COMPLETE: 0x8cd5,
        FRAMEBUFFER_INCOMPLETE_ATTACHMENT: 0x8cd6,
        FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT: 0x8cd7,
        FRAMEBUFFER_INCOMPLETE_DIMENSIONS: 0x8cd9,
        FRAMEBUFFER_UNSUPPORTED: 0x8cdd,
        FRAMEBUFFER_BINDING: 0x8ca6,
        RENDERBUFFER_BINDING: 0x8ca7,
        READ_FRAMEBUFFER: 0x8ca8,
        DRAW_FRAMEBUFFER: 0x8ca9,
        MAX_RENDERBUFFER_SIZE: 0x84e8,
        INVALID_FRAMEBUFFER_OPERATION: 0x0506,
        UNPACK_FLIP_Y_WEBGL: 0x9240,
        UNPACK_PREMULTIPLY_ALPHA_WEBGL: 0x9241,
        UNPACK_COLORSPACE_CONVERSION_WEBGL: 0x9243,
        READ_BUFFER: 0x0c02,
        UNPACK_ROW_LENGTH: 0x0cf2,
        UNPACK_SKIP_ROWS: 0x0cf3,
        UNPACK_SKIP_PIXELS: 0x0cf4,
        PACK_ROW_LENGTH: 0x0d02,
        PACK_SKIP_ROWS: 0x0d03,
        PACK_SKIP_PIXELS: 0x0d04,
        TEXTURE_BINDING_3D: 0x806a,
        UNPACK_SKIP_IMAGES: 0x806d,
        UNPACK_IMAGE_HEIGHT: 0x806e,
        MAX_3D_TEXTURE_SIZE: 0x8073,
        MAX_ELEMENTS_VERTICES: 0x80e8,
        MAX_ELEMENTS_INDICES: 0x80e9,
        MAX_TEXTURE_LOD_BIAS: 0x84fd,
        MAX_FRAGMENT_UNIFORM_COMPONENTS: 0x8b49,
        MAX_VERTEX_UNIFORM_COMPONENTS: 0x8b4a,
        MAX_ARRAY_TEXTURE_LAYERS: 0x88ff,
        MIN_PROGRAM_TEXEL_OFFSET: 0x8904,
        MAX_PROGRAM_TEXEL_OFFSET: 0x8905,
        MAX_VARYING_COMPONENTS: 0x8b4b,
        FRAGMENT_SHADER_DERIVATIVE_HINT: 0x8b8b,
        RASTERIZER_DISCARD: 0x8c89,
        VERTEX_ARRAY_BINDING: 0x85b5,
        MAX_VERTEX_OUTPUT_COMPONENTS: 0x9122,
        MAX_FRAGMENT_INPUT_COMPONENTS: 0x9125,
        MAX_SERVER_WAIT_TIMEOUT: 0x9111,
        MAX_ELEMENT_INDEX: 0x8d6b,
        RED: 0x1903,
        RGB8: 0x8051,
        RGBA8: 0x8058,
        RGB10_A2: 0x8059,
        TEXTURE_3D: 0x806f,
        TEXTURE_WRAP_R: 0x8072,
        TEXTURE_MIN_LOD: 0x813a,
        TEXTURE_MAX_LOD: 0x813b,
        TEXTURE_BASE_LEVEL: 0x813c,
        TEXTURE_MAX_LEVEL: 0x813d,
        TEXTURE_COMPARE_MODE: 0x884c,
        TEXTURE_COMPARE_FUNC: 0x884d,
        SRGB: 0x8c40,
        SRGB8: 0x8c41,
        SRGB8_ALPHA8: 0x8c43,
        COMPARE_REF_TO_TEXTURE: 0x884e,
        RGBA32F: 0x8814,
        RGB32F: 0x8815,
        RGBA16F: 0x881a,
        RGB16F: 0x881b,
        TEXTURE_2D_ARRAY: 0x8c1a,
        TEXTURE_BINDING_2D_ARRAY: 0x8c1d,
        R11F_G11F_B10F: 0x8c3a,
        RGB9_E5: 0x8c3d,
        RGBA32UI: 0x8d70,
        RGB32UI: 0x8d71,
        RGBA16UI: 0x8d76,
        RGB16UI: 0x8d77,
        RGBA8UI: 0x8d7c,
        RGB8UI: 0x8d7d,
        RGBA32I: 0x8d82,
        RGB32I: 0x8d83,
        RGBA16I: 0x8d88,
        RGB16I: 0x8d89,
        RGBA8I: 0x8d8e,
        RGB8I: 0x8d8f,
        RED_INTEGER: 0x8d94,
        RGB_INTEGER: 0x8d98,
        RGBA_INTEGER: 0x8d99,
        R8: 0x8229,
        RG8: 0x822b,
        R16F: 0x822d,
        R32F: 0x822e,
        RG16F: 0x822f,
        RG32F: 0x8230,
        R8I: 0x8231,
        R8UI: 0x8232,
        R16I: 0x8233,
        R16UI: 0x8234,
        R32I: 0x8235,
        R32UI: 0x8236,
        RG8I: 0x8237,
        RG8UI: 0x8238,
        RG16I: 0x8239,
        RG16UI: 0x823a,
        RG32I: 0x823b,
        RG32UI: 0x823c,
        R8_SNORM: 0x8f94,
        RG8_SNORM: 0x8f95,
        RGB8_SNORM: 0x8f96,
        RGBA8_SNORM: 0x8f97,
        RGB10_A2UI: 0x906f,
        TEXTURE_IMMUTABLE_FORMAT: 0x912f,
        TEXTURE_IMMUTABLE_LEVELS: 0x82df,
        UNSIGNED_INT_2_10_10_10_REV: 0x8368,
        UNSIGNED_INT_10F_11F_11F_REV: 0x8c3b,
        UNSIGNED_INT_5_9_9_9_REV: 0x8c3e,
        FLOAT_32_UNSIGNED_INT_24_8_REV: 0x8dad,
        UNSIGNED_INT_24_8: 0x84fa,
        HALF_FLOAT: 0x140b,
        RG: 0x8227,
        RG_INTEGER: 0x8228,
        INT_2_10_10_10_REV: 0x8d9f,
        CURRENT_QUERY: 0x8865,
        QUERY_RESULT: 0x8866,
        QUERY_RESULT_AVAILABLE: 0x8867,
        ANY_SAMPLES_PASSED: 0x8c2f,
        ANY_SAMPLES_PASSED_CONSERVATIVE: 0x8d6a,
        MAX_DRAW_BUFFERS: 0x8824,
        DRAW_BUFFER0: 0x8825,
        DRAW_BUFFER1: 0x8826,
        DRAW_BUFFER2: 0x8827,
        DRAW_BUFFER3: 0x8828,
        DRAW_BUFFER4: 0x8829,
        DRAW_BUFFER5: 0x882a,
        DRAW_BUFFER6: 0x882b,
        DRAW_BUFFER7: 0x882c,
        DRAW_BUFFER8: 0x882d,
        DRAW_BUFFER9: 0x882e,
        DRAW_BUFFER10: 0x882f,
        DRAW_BUFFER11: 0x8830,
        DRAW_BUFFER12: 0x8831,
        DRAW_BUFFER13: 0x8832,
        DRAW_BUFFER14: 0x8833,
        DRAW_BUFFER15: 0x8834,
        MAX_COLOR_ATTACHMENTS: 0x8cdf,
        COLOR_ATTACHMENT1: 0x8ce1,
        COLOR_ATTACHMENT2: 0x8ce2,
        COLOR_ATTACHMENT3: 0x8ce3,
        COLOR_ATTACHMENT4: 0x8ce4,
        COLOR_ATTACHMENT5: 0x8ce5,
        COLOR_ATTACHMENT6: 0x8ce6,
        COLOR_ATTACHMENT7: 0x8ce7,
        COLOR_ATTACHMENT8: 0x8ce8,
        COLOR_ATTACHMENT9: 0x8ce9,
        COLOR_ATTACHMENT10: 0x8cea,
        COLOR_ATTACHMENT11: 0x8ceb,
        COLOR_ATTACHMENT12: 0x8cec,
        COLOR_ATTACHMENT13: 0x8ced,
        COLOR_ATTACHMENT14: 0x8cee,
        COLOR_ATTACHMENT15: 0x8cef,
        SAMPLER_3D: 0x8b5f,
        SAMPLER_2D_SHADOW: 0x8b62,
        SAMPLER_2D_ARRAY: 0x8dc1,
        SAMPLER_2D_ARRAY_SHADOW: 0x8dc4,
        SAMPLER_CUBE_SHADOW: 0x8dc5,
        INT_SAMPLER_2D: 0x8dca,
        INT_SAMPLER_3D: 0x8dcb,
        INT_SAMPLER_CUBE: 0x8dcc,
        INT_SAMPLER_2D_ARRAY: 0x8dcf,
        UNSIGNED_INT_SAMPLER_2D: 0x8dd2,
        UNSIGNED_INT_SAMPLER_3D: 0x8dd3,
        UNSIGNED_INT_SAMPLER_CUBE: 0x8dd4,
        UNSIGNED_INT_SAMPLER_2D_ARRAY: 0x8dd7,
        MAX_SAMPLES: 0x8d57,
        SAMPLER_BINDING: 0x8919,
        PIXEL_PACK_BUFFER: 0x88eb,
        PIXEL_UNPACK_BUFFER: 0x88ec,
        PIXEL_PACK_BUFFER_BINDING: 0x88ed,
        PIXEL_UNPACK_BUFFER_BINDING: 0x88ef,
        COPY_READ_BUFFER: 0x8f36,
        COPY_WRITE_BUFFER: 0x8f37,
        COPY_READ_BUFFER_BINDING: 0x8f36,
        COPY_WRITE_BUFFER_BINDING: 0x8f37,
        FLOAT_MAT2x3: 0x8b65,
        FLOAT_MAT2x4: 0x8b66,
        FLOAT_MAT3x2: 0x8b67,
        FLOAT_MAT3x4: 0x8b68,
        FLOAT_MAT4x2: 0x8b69,
        FLOAT_MAT4x3: 0x8b6a,
        UNSIGNED_INT_VEC2: 0x8dc6,
        UNSIGNED_INT_VEC3: 0x8dc7,
        UNSIGNED_INT_VEC4: 0x8dc8,
        UNSIGNED_NORMALIZED: 0x8c17,
        SIGNED_NORMALIZED: 0x8f9c,
        VERTEX_ATTRIB_ARRAY_INTEGER: 0x88fd,
        VERTEX_ATTRIB_ARRAY_DIVISOR: 0x88fe,
        TRANSFORM_FEEDBACK_BUFFER_MODE: 0x8c7f,
        MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS: 0x8c80,
        TRANSFORM_FEEDBACK_VARYINGS: 0x8c83,
        TRANSFORM_FEEDBACK_BUFFER_START: 0x8c84,
        TRANSFORM_FEEDBACK_BUFFER_SIZE: 0x8c85,
        TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN: 0x8c88,
        MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS: 0x8c8a,
        MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS: 0x8c8b,
        INTERLEAVED_ATTRIBS: 0x8c8c,
        SEPARATE_ATTRIBS: 0x8c8d,
        TRANSFORM_FEEDBACK_BUFFER: 0x8c8e,
        TRANSFORM_FEEDBACK_BUFFER_BINDING: 0x8c8f,
        TRANSFORM_FEEDBACK: 0x8e22,
        TRANSFORM_FEEDBACK_PAUSED: 0x8e23,
        TRANSFORM_FEEDBACK_ACTIVE: 0x8e24,
        TRANSFORM_FEEDBACK_BINDING: 0x8e25,
        FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING: 0x8210,
        FRAMEBUFFER_ATTACHMENT_COMPONENT_TYPE: 0x8211,
        FRAMEBUFFER_ATTACHMENT_RED_SIZE: 0x8212,
        FRAMEBUFFER_ATTACHMENT_GREEN_SIZE: 0x8213,
        FRAMEBUFFER_ATTACHMENT_BLUE_SIZE: 0x8214,
        FRAMEBUFFER_ATTACHMENT_ALPHA_SIZE: 0x8215,
        FRAMEBUFFER_ATTACHMENT_DEPTH_SIZE: 0x8216,
        FRAMEBUFFER_ATTACHMENT_STENCIL_SIZE: 0x8217,
        FRAMEBUFFER_DEFAULT: 0x8218,
        DEPTH24_STENCIL8: 0x88f0,
        DRAW_FRAMEBUFFER_BINDING: 0x8ca6,
        READ_FRAMEBUFFER_BINDING: 0x8caa,
        RENDERBUFFER_SAMPLES: 0x8cab,
        FRAMEBUFFER_ATTACHMENT_TEXTURE_LAYER: 0x8cd4,
        FRAMEBUFFER_INCOMPLETE_MULTISAMPLE: 0x8d56,
        UNIFORM_BUFFER: 0x8a11,
        UNIFORM_BUFFER_BINDING: 0x8a28,
        UNIFORM_BUFFER_START: 0x8a29,
        UNIFORM_BUFFER_SIZE: 0x8a2a,
        MAX_VERTEX_UNIFORM_BLOCKS: 0x8a2b,
        MAX_FRAGMENT_UNIFORM_BLOCKS: 0x8a2d,
        MAX_COMBINED_UNIFORM_BLOCKS: 0x8a2e,
        MAX_UNIFORM_BUFFER_BINDINGS: 0x8a2f,
        MAX_UNIFORM_BLOCK_SIZE: 0x8a30,
        MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS: 0x8a31,
        MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS: 0x8a33,
        UNIFORM_BUFFER_OFFSET_ALIGNMENT: 0x8a34,
        ACTIVE_UNIFORM_BLOCKS: 0x8a36,
        UNIFORM_TYPE: 0x8a37,
        UNIFORM_SIZE: 0x8a38,
        UNIFORM_BLOCK_INDEX: 0x8a3a,
        UNIFORM_OFFSET: 0x8a3b,
        UNIFORM_ARRAY_STRIDE: 0x8a3c,
        UNIFORM_MATRIX_STRIDE: 0x8a3d,
        UNIFORM_IS_ROW_MAJOR: 0x8a3e,
        UNIFORM_BLOCK_BINDING: 0x8a3f,
        UNIFORM_BLOCK_DATA_SIZE: 0x8a40,
        UNIFORM_BLOCK_ACTIVE_UNIFORMS: 0x8a42,
        UNIFORM_BLOCK_ACTIVE_UNIFORM_INDICES: 0x8a43,
        UNIFORM_BLOCK_REFERENCED_BY_VERTEX_SHADER: 0x8a44,
        UNIFORM_BLOCK_REFERENCED_BY_FRAGMENT_SHADER: 0x8a46,
        OBJECT_TYPE: 0x9112,
        SYNC_CONDITION: 0x9113,
        SYNC_STATUS: 0x9114,
        SYNC_FLAGS: 0x9115,
        SYNC_FENCE: 0x9116,
        SYNC_GPU_COMMANDS_COMPLETE: 0x9117,
        UNSIGNALED: 0x9118,
        SIGNALED: 0x9119,
        ALREADY_SIGNALED: 0x911a,
        TIMEOUT_EXPIRED: 0x911b,
        CONDITION_SATISFIED: 0x911c,
        WAIT_FAILED: 0x911d,
        SYNC_FLUSH_COMMANDS_BIT: 0x00000001,
        COLOR: 0x1800,
        DEPTH: 0x1801,
        STENCIL: 0x1802,
        MIN: 0x8007,
        MAX: 0x8008,
        DEPTH_COMPONENT24: 0x81a6,
        STREAM_READ: 0x88e1,
        STREAM_COPY: 0x88e2,
        STATIC_READ: 0x88e5,
        STATIC_COPY: 0x88e6,
        DYNAMIC_READ: 0x88e9,
        DYNAMIC_COPY: 0x88ea,
        DEPTH_COMPONENT32F: 0x8cac,
        DEPTH32F_STENCIL8: 0x8cad,
        INVALID_INDEX: 0xffffffff,
        TIMEOUT_IGNORED: -1,
        MAX_CLIENT_WAIT_TIMEOUT_WEBGL: 0x9247,
        VERTEX_ATTRIB_ARRAY_DIVISOR_ANGLE: 0x88fe,
        UNMASKED_VENDOR_WEBGL: 0x9245,
        UNMASKED_RENDERER_WEBGL: 0x9246,
        MAX_TEXTURE_MAX_ANISOTROPY_EXT: 0x84ff,
        TEXTURE_MAX_ANISOTROPY_EXT: 0x84fe,
        COMPRESSED_RGB_S3TC_DXT1_EXT: 0x83f0,
        COMPRESSED_RGBA_S3TC_DXT1_EXT: 0x83f1,
        COMPRESSED_RGBA_S3TC_DXT3_EXT: 0x83f2,
        COMPRESSED_RGBA_S3TC_DXT5_EXT: 0x83f3,
        COMPRESSED_R11_EAC: 0x9270,
        COMPRESSED_SIGNED_R11_EAC: 0x9271,
        COMPRESSED_RG11_EAC: 0x9272,
        COMPRESSED_SIGNED_RG11_EAC: 0x9273,
        COMPRESSED_RGB8_ETC2: 0x9274,
        COMPRESSED_RGBA8_ETC2_EAC: 0x9275,
        COMPRESSED_SRGB8_ETC2: 0x9276,
        COMPRESSED_SRGB8_ALPHA8_ETC2_EAC: 0x9277,
        COMPRESSED_RGB8_PUNCHTHROUGH_ALPHA1_ETC2: 0x9278,
        COMPRESSED_SRGB8_PUNCHTHROUGH_ALPHA1_ETC2: 0x9279,
        COMPRESSED_RGB_PVRTC_4BPPV1_IMG: 0x8c00,
        COMPRESSED_RGBA_PVRTC_4BPPV1_IMG: 0x8c02,
        COMPRESSED_RGB_PVRTC_2BPPV1_IMG: 0x8c01,
        COMPRESSED_RGBA_PVRTC_2BPPV1_IMG: 0x8c03,
        COMPRESSED_RGB_ETC1_WEBGL: 0x8d64,
        COMPRESSED_RGB_ATC_WEBGL: 0x8c92,
        COMPRESSED_RGBA_ATC_EXPLICIT_ALPHA_WEBGL: 0x8c92,
        COMPRESSED_RGBA_ATC_INTERPOLATED_ALPHA_WEBGL: 0x87ee,
        UNSIGNED_INT_24_8_WEBGL: 0x84fa,
        HALF_FLOAT_OES: 0x8d61,
        RGBA32F_EXT: 0x8814,
        RGB32F_EXT: 0x8815,
        FRAMEBUFFER_ATTACHMENT_COMPONENT_TYPE_EXT: 0x8211,
        UNSIGNED_NORMALIZED_EXT: 0x8c17,
        MIN_EXT: 0x8007,
        MAX_EXT: 0x8008,
        SRGB_EXT: 0x8c40,
        SRGB_ALPHA_EXT: 0x8c42,
        SRGB8_ALPHA8_EXT: 0x8c43,
        FRAMEBUFFER_ATTACHMENT_COLOR_ENCODING_EXT: 0x8210,
        FRAGMENT_SHADER_DERIVATIVE_HINT_OES: 0x8b8b,
        COLOR_ATTACHMENT0_WEBGL: 0x8ce0,
        COLOR_ATTACHMENT1_WEBGL: 0x8ce1,
        COLOR_ATTACHMENT2_WEBGL: 0x8ce2,
        COLOR_ATTACHMENT3_WEBGL: 0x8ce3,
        COLOR_ATTACHMENT4_WEBGL: 0x8ce4,
        COLOR_ATTACHMENT5_WEBGL: 0x8ce5,
        COLOR_ATTACHMENT6_WEBGL: 0x8ce6,
        COLOR_ATTACHMENT7_WEBGL: 0x8ce7,
        COLOR_ATTACHMENT8_WEBGL: 0x8ce8,
        COLOR_ATTACHMENT9_WEBGL: 0x8ce9,
        COLOR_ATTACHMENT10_WEBGL: 0x8cea,
        COLOR_ATTACHMENT11_WEBGL: 0x8ceb,
        COLOR_ATTACHMENT12_WEBGL: 0x8cec,
        COLOR_ATTACHMENT13_WEBGL: 0x8ced,
        COLOR_ATTACHMENT14_WEBGL: 0x8cee,
        COLOR_ATTACHMENT15_WEBGL: 0x8cef,
        DRAW_BUFFER0_WEBGL: 0x8825,
        DRAW_BUFFER1_WEBGL: 0x8826,
        DRAW_BUFFER2_WEBGL: 0x8827,
        DRAW_BUFFER3_WEBGL: 0x8828,
        DRAW_BUFFER4_WEBGL: 0x8829,
        DRAW_BUFFER5_WEBGL: 0x882a,
        DRAW_BUFFER6_WEBGL: 0x882b,
        DRAW_BUFFER7_WEBGL: 0x882c,
        DRAW_BUFFER8_WEBGL: 0x882d,
        DRAW_BUFFER9_WEBGL: 0x882e,
        DRAW_BUFFER10_WEBGL: 0x882f,
        DRAW_BUFFER11_WEBGL: 0x8830,
        DRAW_BUFFER12_WEBGL: 0x8831,
        DRAW_BUFFER13_WEBGL: 0x8832,
        DRAW_BUFFER14_WEBGL: 0x8833,
        DRAW_BUFFER15_WEBGL: 0x8834,
        MAX_COLOR_ATTACHMENTS_WEBGL: 0x8cdf,
        MAX_DRAW_BUFFERS_WEBGL: 0x8824,
        VERTEX_ARRAY_BINDING_OES: 0x85b5,
        QUERY_COUNTER_BITS_EXT: 0x8864,
        CURRENT_QUERY_EXT: 0x8865,
        QUERY_RESULT_EXT: 0x8866,
        QUERY_RESULT_AVAILABLE_EXT: 0x8867,
        TIME_ELAPSED_EXT: 0x88bf,
        TIMESTAMP_EXT: 0x8e28,
        GPU_DISJOINT_EXT: 0x8fbb
    };
},
"04cbffdfe0": /* models/echarts.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a, _b;
    __esModule();
    const bokeh_events_1 = require("@bokehjs/core/bokeh_events");
    const dom_1 = require("@bokehjs/core/dom");
    const event_to_object_1 = require("2cc1a33000") /* ./event-to-object */;
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    const mouse_events = [
        "click", "dblclick", "mousedown", "mousemove", "mouseup", "mouseover", "mouseout",
        "globalout", "contextmenu",
    ];
    const events = [
        "highlight", "downplay", "selectchanged", "legendselectchangedEvent", "legendselected",
        "legendunselected", "legendselectall", "legendinverseselect", "legendscroll", "datazoom",
        "datarangeselected", "timelineplaychanged", "restore", "dataviewchanged", "magictypechanged",
        "geoselectchanged", "geoselected", "geounselected", "axisareaselected", "brush", "brushEnd",
        "rushselected", "globalcursortaken", "rendered", "finished",
    ];
    const all_events = mouse_events.concat(events);
    class EChartsEvent extends bokeh_events_1.ModelEvent {
        constructor(type, data, query) {
            super();
            this.type = type;
            this.data = data;
            this.query = query;
        }
        get event_values() {
            return { model: this.origin, type: this.type, data: this.data, query: this.query };
        }
    }
    exports.EChartsEvent = EChartsEvent;
    _a = EChartsEvent;
    EChartsEvent.__name__ = "EChartsEvent";
    (() => {
        _a.prototype.event_name = "echarts_event";
    })();
    class EChartsView extends layout_1.HTMLBoxView {
        constructor() {
            super(...arguments);
            this._callbacks = [];
        }
        connect_signals() {
            super.connect_signals();
            const { width, height, renderer, theme, event_config, js_events, data } = this.model.properties;
            this.on_change(data, () => this._plot());
            this.on_change([width, height], () => this._resize());
            this.on_change([theme, renderer], () => {
                this.render();
                this._chart.resize();
            });
            this.on_change([event_config, js_events], () => this._subscribe());
        }
        render() {
            if (this._chart != null) {
                window.echarts.dispose(this._chart);
            }
            super.render();
            this.container = (0, dom_1.div)({ style: "height: 100%; width: 100%;" });
            const config = { width: this.model.width, height: this.model.height, renderer: this.model.renderer };
            this._chart = window.echarts.init(this.container, this.model.theme, config);
            this._plot();
            this._subscribe();
            this.shadow_el.append(this.container);
        }
        remove() {
            super.remove();
            if (this._chart != null) {
                window.echarts.dispose(this._chart);
            }
        }
        after_layout() {
            super.after_layout();
            this._chart.resize();
        }
        _plot() {
            if (window.echarts == null) {
                return;
            }
            this._chart.setOption(this.model.data, this.model.options);
        }
        _resize() {
            this._chart.resize({ width: this.model.width, height: this.model.height });
        }
        _subscribe() {
            if (window.echarts == null) {
                return;
            }
            for (const [event_type, callback] of this._callbacks) {
                this._chart.off(event_type, callback);
            }
            this._callbacks = [];
            for (const event_type in this.model.event_config) {
                if (!all_events.includes(event_type)) {
                    console.warn(`Could not subscribe to unknown Echarts event: ${event_type}.`);
                    continue;
                }
                const queries = this.model.event_config[event_type];
                for (const query of queries) {
                    const callback = (event) => {
                        const processed = { ...event };
                        processed.event = (0, event_to_object_1.serializeEvent)(event.event?.event);
                        const serialized = JSON.parse(JSON.stringify(processed));
                        this.model.trigger_event(new EChartsEvent(event_type, serialized, query));
                    };
                    if (query == null) {
                        this._chart.on(event_type, query, callback);
                    }
                    else {
                        this._chart.on(event_type, callback);
                    }
                    this._callbacks.push([event_type, callback]);
                }
            }
            for (const event_type in this.model.js_events) {
                if (!all_events.includes(event_type)) {
                    console.warn(`Could not subscribe to unknown Echarts event: ${event_type}.`);
                    continue;
                }
                const handlers = this.model.js_events[event_type];
                for (const handler of handlers) {
                    const callback = (event) => {
                        handler.callback.execute(this._chart, event);
                    };
                    if ("query" in handler) {
                        this._chart.on(event_type, handler.query, callback);
                    }
                    else {
                        this._chart.on(event_type, callback);
                    }
                    this._callbacks.push([event_type, callback]);
                }
            }
        }
    }
    exports.EChartsView = EChartsView;
    EChartsView.__name__ = "EChartsView";
    class ECharts extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.ECharts = ECharts;
    _b = ECharts;
    ECharts.__name__ = "ECharts";
    ECharts.__module__ = "panel.models.echarts";
    (() => {
        _b.prototype.default_view = EChartsView;
        _b.define(({ Any, Str }) => ({
            data: [Any, {}],
            options: [Any, {}],
            event_config: [Any, {}],
            js_events: [Any, {}],
            theme: [Str, "default"],
            renderer: [Str, "canvas"],
        }));
    })();
},
"2cc1a33000": /* models/event-to-object.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    /*
    The MIT License (MIT)
    
    Copyright (c) 2019 Ryan S. Morshead
    
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    */
    function serializeEvent(event) {
        const data = {};
        // support for CustomEvents: the whole `detail` object is serialized
        if (event.detail !== undefined) {
            Object.assign(data, { detail: JSON.parse(JSON.stringify(event.detail)) });
        }
        if (event.type in eventTransforms) {
            Object.assign(data, eventTransforms[event.type](event));
        }
        data.target = serializeDomElement(event.target);
        data.currentTarget =
            event.target === event.currentTarget
                ? data.target
                : serializeDomElement(event.currentTarget);
        data.relatedTarget = serializeDomElement(event.relatedTarget);
        return data;
    }
    exports.serializeEvent = serializeEvent;
    function serializeDomElement(element) {
        let elementData = null;
        if (element) {
            elementData = defaultElementTransform(element);
            if (element.tagName in elementTransforms) {
                elementTransforms[element.tagName].forEach((trans) => Object.assign(elementData, trans(element)));
            }
        }
        return elementData;
    }
    const elementTransformCategories = {
        hasValue: (element) => ({
            value: element.value,
        }),
        hasCurrentTime: (element) => ({
            currentTime: element.currentTime,
        }),
        hasFiles: (element) => {
            if (element.type === "file") {
                return {
                    files: [...element.files ?? []].map((file) => ({
                        lastModified: file.lastModified,
                        name: file.name,
                        size: file.size,
                        type: file.type,
                    })),
                };
            }
            else {
                return {};
            }
        },
    };
    function defaultElementTransform(element) {
        try {
            return { boundingClientRect: { ...element.getBoundingClientRect() } };
        }
        catch {
            return {};
        }
    }
    const elementTagCategories = {
        hasValue: [
            "BUTTON",
            "INPUT",
            "OPTION",
            "LI",
            "METER",
            "PROGRESS",
            "PARAM",
            "SELECT",
            "TEXTAREA",
        ],
        hasCurrentTime: ["AUDIO", "VIDEO"],
        hasFiles: ["INPUT"],
    };
    const elementTransforms = {};
    Object.keys(elementTagCategories).forEach((category) => {
        elementTagCategories[category].forEach((type) => {
            const transforms = elementTransforms[type] || (elementTransforms[type] = []);
            transforms.push(elementTransformCategories[category]);
        });
    });
    class EventTransformCategories {
        clipboard(event) {
            return {
                clipboardData: event.clipboardData,
            };
        }
        composition(event) {
            return {
                data: event.data,
            };
        }
        keyboard(event) {
            return {
                altKey: event.altKey,
                charCode: event.charCode,
                ctrlKey: event.ctrlKey,
                key: event.key,
                keyCode: event.keyCode,
                locale: event.locale,
                location: event.location,
                metaKey: event.metaKey,
                repeat: event.repeat,
                shiftKey: event.shiftKey,
                which: event.which,
            };
        }
        mouse(event) {
            return {
                altKey: event.altKey,
                button: event.button,
                buttons: event.buttons,
                clientX: event.clientX,
                clientY: event.clientY,
                ctrlKey: event.ctrlKey,
                metaKey: event.metaKey,
                pageX: event.pageX,
                pageY: event.pageY,
                screenX: event.screenX,
                screenY: event.screenY,
                shiftKey: event.shiftKey,
            };
        }
        pointer(event) {
            return {
                ...this.mouse(event),
                pointerId: event.pointerId,
                width: event.width,
                height: event.height,
                pressure: event.pressure,
                tiltX: event.tiltX,
                tiltY: event.tiltY,
                pointerType: event.pointerType,
                isPrimary: event.isPrimary,
            };
        }
        selection() {
            return {
                selectedText: window.getSelection().toString(),
            };
        }
        ;
        touch(event) {
            return {
                altKey: event.altKey,
                ctrlKey: event.ctrlKey,
                metaKey: event.metaKey,
                shiftKey: event.shiftKey,
            };
        }
        ui(event) {
            return {
                detail: event.detail,
            };
        }
        wheel(event) {
            return {
                deltaMode: event.deltaMode,
                deltaX: event.deltaX,
                deltaY: event.deltaY,
                deltaZ: event.deltaZ,
            };
        }
        animation(event) {
            return {
                animationName: event.animationName,
                pseudoElement: event.pseudoElement,
                elapsedTime: event.elapsedTime,
            };
        }
        transition(event) {
            return {
                propertyName: event.propertyName,
                pseudoElement: event.pseudoElement,
                elapsedTime: event.elapsedTime,
            };
        }
    }
    EventTransformCategories.__name__ = "EventTransformCategories";
    const eventTypeCategories = {
        clipboard: ["copy", "cut", "paste"],
        composition: ["compositionend", "compositionstart", "compositionupdate"],
        keyboard: ["keydown", "keypress", "keyup"],
        mouse: [
            "click",
            "contextmenu",
            "doubleclick",
            "drag",
            "dragend",
            "dragenter",
            "dragexit",
            "dragleave",
            "dragover",
            "dragstart",
            "drop",
            "mousedown",
            "mouseenter",
            "mouseleave",
            "mousemove",
            "mouseout",
            "mouseover",
            "mouseup",
        ],
        pointer: [
            "pointerdown",
            "pointermove",
            "pointerup",
            "pointercancel",
            "gotpointercapture",
            "lostpointercapture",
            "pointerenter",
            "pointerleave",
            "pointerover",
            "pointerout",
        ],
        selection: ["select"],
        touch: ["touchcancel", "touchend", "touchmove", "touchstart"],
        ui: ["scroll"],
        wheel: ["wheel"],
        animation: ["animationstart", "animationend", "animationiteration"],
        transition: ["transitionend"],
    };
    const eventTransforms = {};
    const eventTransformCategories = new EventTransformCategories();
    Object.keys(eventTypeCategories).forEach((category) => {
        eventTypeCategories[category].forEach((type) => {
            eventTransforms[type] = eventTransformCategories[category];
        });
    });
},
"976c02c0a8": /* models/feed.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a, _b;
    __esModule();
    const column_1 = require("879751b529") /* ./column */;
    const build_views_1 = require("@bokehjs/core/build_views");
    const bokeh_events_1 = require("@bokehjs/core/bokeh_events");
    class ScrollButtonClick extends bokeh_events_1.ModelEvent {
    }
    exports.ScrollButtonClick = ScrollButtonClick;
    _a = ScrollButtonClick;
    ScrollButtonClick.__name__ = "ScrollButtonClick";
    (() => {
        _a.prototype.event_name = "scroll_button_click";
    })();
    class FeedView extends column_1.ColumnView {
        initialize() {
            super.initialize();
            this._sync = true;
            this._intersection_observer = new IntersectionObserver((entries) => {
                const visible = [...this.model.visible_children];
                const nodes = this.node_map;
                for (const entry of entries) {
                    const id = nodes.get(entry.target).id;
                    if (entry.isIntersecting) {
                        if (!visible.includes(id)) {
                            visible.push(id);
                        }
                    }
                    else if (visible.includes(id)) {
                        visible.splice(visible.indexOf(id), 1);
                    }
                }
                if (this._sync) {
                    this.model.visible_children = visible;
                }
                if (visible.length > 0) {
                    const refs = this.child_models.map((model) => model.id);
                    const indices = visible.map((ref) => refs.indexOf(ref));
                    this._last_visible = this.child_views[Math.min(...indices)];
                }
                else {
                    this._last_visible = null;
                }
            }, {
                root: this.el,
                threshold: 0.01,
            });
        }
        get node_map() {
            const nodes = new Map();
            for (const view of this.child_views) {
                nodes.set(view.el, view.model);
            }
            return nodes;
        }
        async update_children() {
            this._sync = false;
            await super.update_children();
            this._sync = true;
            this._last_visible?.el.scrollIntoView(true);
        }
        async build_child_views() {
            const { created, removed } = await (0, build_views_1.build_views)(this._child_views, this.child_models, { parent: this });
            const visible = this.model.visible_children;
            for (const view of removed) {
                if (visible.includes(view.model.id)) {
                    visible.splice(visible.indexOf(view.model.id), 1);
                }
                this._resize_observer.unobserve(view.el);
                this._intersection_observer.unobserve(view.el);
            }
            this.model.visible_children = [...visible];
            for (const view of created) {
                this._resize_observer.observe(view.el, { box: "border-box" });
                this._intersection_observer.observe(view.el);
            }
            return created;
        }
        scroll_to_latest(emit_event = true) {
            if (emit_event) {
                this.model.trigger_event(new ScrollButtonClick());
            }
            super.scroll_to_latest();
        }
        trigger_auto_scroll() {
            const limit = this.model.auto_scroll_limit;
            const within_limit = this.distance_from_latest <= limit;
            if (limit == 0 || !within_limit) {
                return;
            }
            this.scroll_to_latest(false);
        }
    }
    exports.FeedView = FeedView;
    FeedView.__name__ = "FeedView";
    class Feed extends column_1.Column {
        constructor(attrs) {
            super(attrs);
        }
        on_click(callback) {
            this.on_event(ScrollButtonClick, callback);
        }
    }
    exports.Feed = Feed;
    _b = Feed;
    Feed.__name__ = "Feed";
    Feed.__module__ = "panel.models.feed";
    (() => {
        _b.prototype.default_view = FeedView;
        _b.define(({ List, Str }) => ({
            visible_children: [List(Str), []],
        }));
    })();
},
"3ead851ca6": /* models/file_download.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tslib_1 = require("tslib");
    const build_views_1 = require("@bokehjs/core/build_views");
    const enums_1 = require("@bokehjs/core/enums");
    const input_widget_1 = require("@bokehjs/models/widgets/input_widget");
    const icon_1 = require("@bokehjs/models/ui/icons/icon");
    const buttons_css_1 = tslib_1.__importStar(require("@bokehjs/styles/buttons.css")), buttons = buttons_css_1;
    const dom_1 = require("@bokehjs/core/dom");
    function dataURItoBlob(dataURI) {
        // convert base64 to raw binary data held in a string
        const byteString = atob(dataURI.split(",")[1]);
        // separate out the mime component
        const mimeString = dataURI.split(",")[0].split(":")[1].split(";")[0];
        // write the bytes of the string to an ArrayBuffer
        const ab = new ArrayBuffer(byteString.length);
        const ia = new Uint8Array(ab);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        // write the ArrayBuffer to a blob, and you're done
        const bb = new Blob([ab], { type: mimeString });
        return bb;
    }
    class FileDownloadView extends input_widget_1.InputWidgetView {
        constructor() {
            super(...arguments);
            this._downloadable = false;
            this._prev_href = "";
            this._prev_download = "";
        }
        *children() {
            yield* super.children();
            if (this.icon_view != null) {
                yield this.icon_view;
            }
        }
        *controls() {
            yield this.anchor_el;
            yield this.button_el;
        }
        connect_signals() {
            super.connect_signals();
            const { button_type, filename, _transfers, label } = this.model.properties;
            this.on_change(button_type, () => this._update_button_style());
            this.on_change(filename, () => this._update_download());
            this.on_change(_transfers, () => this._handle_click());
            this.on_change(label, () => this._update_label());
        }
        remove() {
            if (this.icon_view != null) {
                this.icon_view.remove();
            }
            super.remove();
        }
        async lazy_initialize() {
            await super.lazy_initialize();
            const { icon } = this.model;
            if (icon != null) {
                this.icon_view = await (0, build_views_1.build_view)(icon, { parent: this });
            }
        }
        _render_input() {
            // Create an anchor HTML element that is styled as a bokeh button.
            // When its 'href' and 'download' attributes are set, it's a downloadable link:
            // * A click triggers a download
            // * A right click allows to "Save as" the file
            // There are three main cases:
            // 1. embed=True: The widget is a download link
            // 2. auto=False: The widget is first a button and becomes a download link after the first click
            // 3. auto=True: The widget is a button, i.e right click to "Save as..." won't work
            this.anchor_el = document.createElement("a");
            this.button_el = (0, dom_1.button)({
                disabled: this.model.disabled,
            });
            if (this.icon_view != null) {
                const separator = this.model.label != "" ? (0, dom_1.nbsp)() : (0, dom_1.text)("");
                (0, dom_1.prepend)(this.button_el, this.icon_view.el, separator);
                this.icon_view.render();
            }
            this._update_button_style();
            this._update_label();
            // Changing the disabled property calls render() so it needs to be handled here.
            // This callback is inherited from ControlView in bokehjs.
            if (this.model.disabled) {
                this.anchor_el.setAttribute("disabled", "");
                this._downloadable = false;
            }
            else {
                this.anchor_el.removeAttribute("disabled");
                // auto=False + toggle Disabled ==> Needs to reset the link as it was.
                if (this._prev_download) {
                    this.anchor_el.download = this._prev_download;
                }
                if (this._prev_href) {
                    this.anchor_el.href = this._prev_href;
                }
                if (this.anchor_el.download && this.anchor_el.download) {
                    this._downloadable = true;
                }
            }
            // If embedded the button is just a download link.
            // Otherwise clicks will be handled by the code itself, allowing for more interactivity.
            if (this.model.embed) {
                this._make_link_downloadable();
            }
            else {
                // Add a "click" listener, note that it's not going to
                // handle right clicks (they won't increment 'clicks')
                this._click_listener = this._increment_clicks.bind(this);
                this.anchor_el.addEventListener("click", this._click_listener);
            }
            this.button_el.appendChild(this.anchor_el);
            this.input_el = (0, dom_1.input)(); // HACK: So this.input_el.id = "input" can be set in Bokeh 3.4
            return this.button_el;
        }
        render() {
            super.render();
            this.group_el.style.display = "flex";
            this.group_el.style.alignItems = "stretch";
        }
        stylesheets() {
            return [...super.stylesheets(), buttons_css_1.default];
        }
        _increment_clicks() {
            this.model.clicks = this.model.clicks + 1;
        }
        _handle_click() {
            // When auto=False the button becomes a link which no longer
            // requires being updated.
            if ((!this.model.auto && this._downloadable) || this.anchor_el.hasAttribute("disabled")) {
                return;
            }
            this._make_link_downloadable();
            if (!this.model.embed && this.model.auto) {
                // Temporarily removing the event listener to emulate a click
                // event on the anchor link which will trigger a download.
                this.anchor_el.removeEventListener("click", this._click_listener);
                this.anchor_el.click();
                // In this case #3 the widget is not a link so these attributes are removed.
                this.anchor_el.removeAttribute("href");
                this.anchor_el.removeAttribute("download");
                this.anchor_el.addEventListener("click", this._click_listener);
            }
            // Store the current state for handling changes of the disabled property.
            this._prev_href = this.anchor_el.getAttribute("href");
            this._prev_download = this.anchor_el.getAttribute("download");
        }
        _make_link_downloadable() {
            this._update_href();
            this._update_download();
            if (this.anchor_el.download && this.anchor_el.href) {
                this._downloadable = true;
            }
        }
        _update_href() {
            if (this.model.data) {
                const blob = dataURItoBlob(this.model.data);
                this.anchor_el.href = URL.createObjectURL(blob);
            }
        }
        _update_download() {
            if (this.model.filename) {
                this.anchor_el.download = this.model.filename;
            }
        }
        _update_label() {
            this.anchor_el.textContent = this.model.label;
        }
        _update_button_style() {
            const btn_type = buttons[`btn_${this.model.button_type}`];
            if (!this.button_el.hasAttribute("class")) { // When the widget is rendered.
                this.button_el.classList.add(buttons.btn);
                this.button_el.classList.add(btn_type);
            }
            else { // When the button type is changed.
                const prev_button_type = this.anchor_el.classList.item(1);
                if (prev_button_type) {
                    this.button_el.classList.replace(prev_button_type, btn_type);
                }
            }
        }
    }
    exports.FileDownloadView = FileDownloadView;
    FileDownloadView.__name__ = "FileDownloadView";
    class FileDownload extends input_widget_1.InputWidget {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.FileDownload = FileDownload;
    _a = FileDownload;
    FileDownload.__name__ = "FileDownload";
    FileDownload.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = FileDownloadView;
        _a.define(({ Bool, Int, Nullable, Ref, Str }) => ({
            auto: [Bool, false],
            clicks: [Int, 0],
            data: [Nullable(Str), null],
            embed: [Bool, false],
            icon: [Nullable(Ref(icon_1.Icon)), null],
            label: [Str, "Download"],
            filename: [Nullable(Str), null],
            button_type: [enums_1.ButtonType, "default"], // TODO (bev)
            _transfers: [Int, 0],
        }));
        _a.override({
            title: "",
        });
    })();
},
"89d2d3667a": /* models/html.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a, _b;
    __esModule();
    const bokeh_events_1 = require("@bokehjs/core/bokeh_events");
    const markup_1 = require("@bokehjs/models/widgets/markup");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    const event_to_object_1 = require("2cc1a33000") /* ./event-to-object */;
    class DOMEvent extends bokeh_events_1.ModelEvent {
        constructor(node, data) {
            super();
            this.node = node;
            this.data = data;
        }
        get event_values() {
            return { model: this.origin, node: this.node, data: this.data };
        }
    }
    exports.DOMEvent = DOMEvent;
    _a = DOMEvent;
    DOMEvent.__name__ = "DOMEvent";
    (() => {
        _a.prototype.event_name = "dom_event";
    })();
    function htmlDecode(input) {
        const doc = new DOMParser().parseFromString(input, "text/html");
        return doc.documentElement.textContent;
    }
    exports.htmlDecode = htmlDecode;
    function runScripts(node) {
        Array.from(node.querySelectorAll("script")).forEach((oldScript) => {
            const newScript = document.createElement("script");
            Array.from(oldScript.attributes)
                .forEach((attr) => newScript.setAttribute(attr.name, attr.value));
            newScript.appendChild(document.createTextNode(oldScript.innerHTML));
            if (oldScript.parentNode) {
                oldScript.parentNode.replaceChild(newScript, oldScript);
            }
        });
    }
    exports.runScripts = runScripts;
    class HTMLView extends layout_1.PanelMarkupView {
        constructor() {
            super(...arguments);
            this._event_listeners = {};
        }
        connect_signals() {
            super.connect_signals();
            const { text, visible, events } = this.model.properties;
            this.on_change(text, () => {
                const html = this.process_tex();
                this.set_html(html);
            });
            this.on_change(visible, () => {
                if (this.model.visible) {
                    this.container.style.visibility = "visible";
                }
            });
            this.on_change(events, () => {
                this._remove_event_listeners();
                this._setup_event_listeners();
            });
        }
        rerender() {
            this.render();
            this.invalidate_layout();
        }
        set_html(html) {
            if (html !== null) {
                this.container.innerHTML = html;
                if (this.model.run_scripts) {
                    runScripts(this.container);
                }
                this._setup_event_listeners();
            }
        }
        render() {
            super.render();
            this.container.style.visibility = "hidden";
            this.shadow_el.appendChild(this.container);
            if (this.provider.status == "failed" || this.provider.status == "loaded") {
                this._has_finished = true;
            }
            const html = this.process_tex();
            this.watch_stylesheets();
            this.set_html(html);
        }
        style_redraw() {
            if (this.model.visible) {
                this.container.style.visibility = "visible";
            }
        }
        process_tex() {
            const decoded = htmlDecode(this.model.text);
            const text = decoded || this.model.text;
            if (this.model.disable_math || !this.contains_tex(text)) {
                return text;
            }
            const tex_parts = this.provider.MathJax.find_tex(text);
            const processed_text = [];
            let last_index = 0;
            for (const part of tex_parts) {
                processed_text.push(text.slice(last_index, part.start.n));
                processed_text.push(this.provider.MathJax.tex2svg(part.math, { display: part.display }).outerHTML);
                last_index = part.end.n;
            }
            if (last_index < text.length) {
                processed_text.push(text.slice(last_index));
            }
            return processed_text.join("");
        }
        contains_tex(html) {
            if (!this.provider.MathJax) {
                return false;
            }
            return this.provider.MathJax.find_tex(html).length > 0;
        }
        _remove_event_listeners() {
            for (const node in this._event_listeners) {
                const el = document.getElementById(node);
                if (el == null) {
                    console.warn(`DOM node '${node}' could not be found. Cannot subscribe to DOM events.`);
                    continue;
                }
                for (const event_name in this._event_listeners[node]) {
                    const event_callback = this._event_listeners[node][event_name];
                    el.removeEventListener(event_name, event_callback);
                }
            }
            this._event_listeners = {};
        }
        _setup_event_listeners() {
            for (const node in this.model.events) {
                const el = document.getElementById(node);
                if (el == null) {
                    console.warn(`DOM node '${node}' could not be found. Cannot subscribe to DOM events.`);
                    continue;
                }
                for (const event_name of this.model.events[node]) {
                    const callback = (event) => {
                        this.model.trigger_event(new DOMEvent(node, (0, event_to_object_1.serializeEvent)(event)));
                    };
                    el.addEventListener(event_name, callback);
                    if (!(node in this._event_listeners)) {
                        this._event_listeners[node] = {};
                    }
                    this._event_listeners[node][event_name] = callback;
                }
            }
        }
    }
    exports.HTMLView = HTMLView;
    HTMLView.__name__ = "HTMLView";
    class HTML extends markup_1.Markup {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.HTML = HTML;
    _b = HTML;
    HTML.__name__ = "HTML";
    HTML.__module__ = "panel.models.markup";
    (() => {
        _b.prototype.default_view = HTMLView;
        _b.define(({ Any, Bool }) => ({
            events: [Any, {}],
            run_scripts: [Bool, true],
        }));
    })();
},
"8a8089cbf3": /* models/ipywidget.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const dom_1 = require("@bokehjs/core/dom");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    const Jupyter = window.Jupyter;
    class IPyWidgetView extends layout_1.HTMLBoxView {
        initialize() {
            super.initialize();
            let manager;
            if ((Jupyter != null) && (Jupyter.notebook != null)) {
                manager = Jupyter.notebook.kernel.widget_manager;
            }
            else if (window.PyViz.widget_manager != null) {
                manager = window.PyViz.widget_manager;
            }
            else {
                console.warn("Panel IPyWidget model could not find a WidgetManager");
                return;
            }
            this.manager = manager;
            this.ipychildren = [];
        }
        remove() {
            this.ipyview.remove();
            super.remove();
        }
        _ipy_stylesheets() {
            const stylesheets = [];
            for (const child of document.head.children) {
                if (child instanceof HTMLStyleElement) {
                    const raw_css = child.textContent;
                    if (raw_css != null) {
                        const css = raw_css.replace(/:root/g, ":host");
                        stylesheets.push(new dom_1.InlineStyleSheet(css));
                    }
                }
            }
            return stylesheets;
        }
        stylesheets() {
            return [...super.stylesheets(), ...this._ipy_stylesheets()];
        }
        render() {
            super.render();
            const { spec, state } = this.model.bundle;
            this.manager.set_state(state).then(async (models) => {
                const model = models.find((item) => item.model_id == spec.model_id);
                if (model == null) {
                    return;
                }
                const view = await this.manager.create_view(model, { el: this.el });
                this.ipyview = view;
                this.ipychildren = [];
                if (view.children_views) {
                    for (const child of view.children_views.views) {
                        this.ipychildren.push(await child);
                    }
                }
                this.shadow_el.appendChild(this.ipyview.el);
                this.ipyview.trigger("displayed", this.ipyview);
                for (const child of this.ipychildren) {
                    child.trigger("displayed", child);
                }
                this.invalidate_layout();
            });
        }
    }
    exports.IPyWidgetView = IPyWidgetView;
    IPyWidgetView.__name__ = "IPyWidgetView";
    class IPyWidget extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.IPyWidget = IPyWidget;
    _a = IPyWidget;
    IPyWidget.__name__ = "IPyWidget";
    IPyWidget.__module__ = "panel.models.ipywidget";
    (() => {
        _a.prototype.default_view = IPyWidgetView;
        _a.define(({ Any }) => ({
            bundle: [Any, {}],
        }));
    })();
},
"7eff964d3e": /* models/json.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tslib_1 = require("tslib");
    const kinds_1 = require("@bokehjs/core/kinds");
    const markup_1 = require("@bokehjs/models/widgets/markup");
    const json_formatter_js_1 = tslib_1.__importDefault(require("18bba7b7e1") /* json-formatter-js */);
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    class JSONView extends layout_1.PanelMarkupView {
        connect_signals() {
            super.connect_signals();
            const { depth, hover_preview, text, theme } = this.model.properties;
            this.on_change([depth, hover_preview, text, theme], () => this.render());
        }
        render() {
            super.render();
            const text = this.model.text.replace(/(\r\n|\n|\r)/gm, "");
            let json;
            try {
                json = window.JSON.parse(text);
            }
            catch (err) {
                this.container.innerHTML = `<b>Invalid JSON:</b> ${err}`;
                return;
            }
            const config = { hoverPreviewEnabled: this.model.hover_preview, theme: this.model.theme };
            const depth = this.model.depth == null ? Infinity : this.model.depth;
            const formatter = new json_formatter_js_1.default(json, depth, config);
            const rendered = formatter.render();
            const style = "border-radius: 5px; padding: 10px; width: 100%; height: 100%;";
            if (this.model.theme == "dark") {
                rendered.style.cssText = `background-color: rgb(30, 30, 30);${style}`;
            }
            else {
                rendered.style.cssText = style;
            }
            this.container.append(rendered);
        }
    }
    exports.JSONView = JSONView;
    JSONView.__name__ = "JSONView";
    exports.JSONTheme = (0, kinds_1.Enum)("dark", "light");
    class JSON extends markup_1.Markup {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.JSON = JSON;
    _a = JSON;
    JSON.__name__ = "JSON";
    JSON.__module__ = "panel.models.markup";
    (() => {
        _a.prototype.default_view = JSONView;
        _a.define(({ List, Bool, Int, Nullable, Str }) => ({
            css: [List(Str), []],
            depth: [Nullable(Int), 1],
            hover_preview: [Bool, false],
            theme: [exports.JSONTheme, "dark"],
        }));
    })();
},
"18bba7b7e1": /* json-formatter-js/dist/json-formatter.esm.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    function t(t) { return null === t ? "null" : typeof t; }
    function e(t) { return !!t && "object" == typeof t; }
    function r(t) {
        if (void 0 === t)
            return "";
        if (null === t)
            return "Object";
        if ("object" == typeof t && !t.constructor)
            return "Object";
        var e = /function ([^(]*)/.exec(t.constructor.toString());
        return e && e.length > 1 ? e[1] : "";
    }
    function n(t, e, r) { return "null" === t || "undefined" === t ? t : ("string" !== t && "stringifiable" !== t || (r = '"' + r.replace(/"/g, '\\"') + '"'), "function" === t ? e.toString().replace(/[\r\n]/g, "").replace(/\{.*\}/, "") + "{…}" : r); }
    function o(o) { var i = ""; return e(o) ? (i = r(o), Array.isArray(o) && (i += "[" + o.length + "]")) : i = n(t(o), o, o), i; }
    function i(t) { return "json-formatter-" + t; }
    function s(t, e, r) { var n = document.createElement(t); return e && n.classList.add(i(e)), void 0 !== r && (r instanceof Node ? n.appendChild(r) : n.appendChild(document.createTextNode(String(r)))), n; }
    !function (t) {
        if (t && "undefined" != typeof window) {
            var e = document.createElement("style");
            e.setAttribute("media", "screen"), e.innerHTML = t, document.head.appendChild(e);
        }
    }('.json-formatter-row {\n  font-family: monospace;\n}\n.json-formatter-row,\n.json-formatter-row a,\n.json-formatter-row a:hover {\n  color: black;\n  text-decoration: none;\n}\n.json-formatter-row .json-formatter-row {\n  margin-left: 1rem;\n}\n.json-formatter-row .json-formatter-children.json-formatter-empty {\n  opacity: 0.5;\n  margin-left: 1rem;\n}\n.json-formatter-row .json-formatter-children.json-formatter-empty:after {\n  display: none;\n}\n.json-formatter-row .json-formatter-children.json-formatter-empty.json-formatter-object:after {\n  content: "No properties";\n}\n.json-formatter-row .json-formatter-children.json-formatter-empty.json-formatter-array:after {\n  content: "[]";\n}\n.json-formatter-row .json-formatter-string,\n.json-formatter-row .json-formatter-stringifiable {\n  color: green;\n  white-space: pre;\n  word-wrap: break-word;\n}\n.json-formatter-row .json-formatter-number {\n  color: blue;\n}\n.json-formatter-row .json-formatter-boolean {\n  color: red;\n}\n.json-formatter-row .json-formatter-null {\n  color: #855A00;\n}\n.json-formatter-row .json-formatter-undefined {\n  color: #ca0b69;\n}\n.json-formatter-row .json-formatter-function {\n  color: #FF20ED;\n}\n.json-formatter-row .json-formatter-date {\n  background-color: rgba(0, 0, 0, 0.05);\n}\n.json-formatter-row .json-formatter-url {\n  text-decoration: underline;\n  color: blue;\n  cursor: pointer;\n}\n.json-formatter-row .json-formatter-bracket {\n  color: blue;\n}\n.json-formatter-row .json-formatter-key {\n  color: #00008B;\n  padding-right: 0.2rem;\n}\n.json-formatter-row .json-formatter-toggler-link {\n  cursor: pointer;\n}\n.json-formatter-row .json-formatter-toggler {\n  line-height: 1.2rem;\n  font-size: 0.7rem;\n  vertical-align: middle;\n  opacity: 0.6;\n  cursor: pointer;\n  padding-right: 0.2rem;\n}\n.json-formatter-row .json-formatter-toggler:after {\n  display: inline-block;\n  transition: transform 100ms ease-in;\n  content: "►";\n}\n.json-formatter-row > a > .json-formatter-preview-text {\n  opacity: 0;\n  transition: opacity 0.15s ease-in;\n  font-style: italic;\n}\n.json-formatter-row:hover > a > .json-formatter-preview-text {\n  opacity: 0.6;\n}\n.json-formatter-row.json-formatter-open > .json-formatter-toggler-link .json-formatter-toggler:after {\n  transform: rotate(90deg);\n}\n.json-formatter-row.json-formatter-open > .json-formatter-children:after {\n  display: inline-block;\n}\n.json-formatter-row.json-formatter-open > a > .json-formatter-preview-text {\n  display: none;\n}\n.json-formatter-row.json-formatter-open.json-formatter-empty:after {\n  display: block;\n}\n.json-formatter-dark.json-formatter-row {\n  font-family: monospace;\n}\n.json-formatter-dark.json-formatter-row,\n.json-formatter-dark.json-formatter-row a,\n.json-formatter-dark.json-formatter-row a:hover {\n  color: white;\n  text-decoration: none;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-row {\n  margin-left: 1rem;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-children.json-formatter-empty {\n  opacity: 0.5;\n  margin-left: 1rem;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-children.json-formatter-empty:after {\n  display: none;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-children.json-formatter-empty.json-formatter-object:after {\n  content: "No properties";\n}\n.json-formatter-dark.json-formatter-row .json-formatter-children.json-formatter-empty.json-formatter-array:after {\n  content: "[]";\n}\n.json-formatter-dark.json-formatter-row .json-formatter-string,\n.json-formatter-dark.json-formatter-row .json-formatter-stringifiable {\n  color: #31F031;\n  white-space: pre;\n  word-wrap: break-word;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-number {\n  color: #66C2FF;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-boolean {\n  color: #EC4242;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-null {\n  color: #EEC97D;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-undefined {\n  color: #ef8fbe;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-function {\n  color: #FD48CB;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-date {\n  background-color: rgba(255, 255, 255, 0.05);\n}\n.json-formatter-dark.json-formatter-row .json-formatter-url {\n  text-decoration: underline;\n  color: #027BFF;\n  cursor: pointer;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-bracket {\n  color: #9494FF;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-key {\n  color: #23A0DB;\n  padding-right: 0.2rem;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-toggler-link {\n  cursor: pointer;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-toggler {\n  line-height: 1.2rem;\n  font-size: 0.7rem;\n  vertical-align: middle;\n  opacity: 0.6;\n  cursor: pointer;\n  padding-right: 0.2rem;\n}\n.json-formatter-dark.json-formatter-row .json-formatter-toggler:after {\n  display: inline-block;\n  transition: transform 100ms ease-in;\n  content: "►";\n}\n.json-formatter-dark.json-formatter-row > a > .json-formatter-preview-text {\n  opacity: 0;\n  transition: opacity 0.15s ease-in;\n  font-style: italic;\n}\n.json-formatter-dark.json-formatter-row:hover > a > .json-formatter-preview-text {\n  opacity: 0.6;\n}\n.json-formatter-dark.json-formatter-row.json-formatter-open > .json-formatter-toggler-link .json-formatter-toggler:after {\n  transform: rotate(90deg);\n}\n.json-formatter-dark.json-formatter-row.json-formatter-open > .json-formatter-children:after {\n  display: inline-block;\n}\n.json-formatter-dark.json-formatter-row.json-formatter-open > a > .json-formatter-preview-text {\n  display: none;\n}\n.json-formatter-dark.json-formatter-row.json-formatter-open.json-formatter-empty:after {\n  display: block;\n}\n');
    var a = /(^\d{1,4}[\.|\\/|-]\d{1,2}[\.|\\/|-]\d{1,4})(\s*(?:0?[1-9]:[0-5]|1(?=[012])\d:[0-5])\d\s*[ap]m)?$/, f = /\d{2}:\d{2}:\d{2} GMT-\d{4}/, m = /\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z/, l = window.requestAnimationFrame || function (t) { return t(), 0; }, d = { hoverPreviewEnabled: !1, hoverPreviewArrayCount: 100, hoverPreviewFieldCount: 5, animateOpen: !0, animateClose: !0, theme: null, useToJSON: !0, sortPropertiesBy: null }, c = function () {
        function c(t, e, r, n) { void 0 === e && (e = 1), void 0 === r && (r = d), this.json = t, this.open = e, this.config = r, this.key = n, this._isOpen = null, void 0 === this.config.hoverPreviewEnabled && (this.config.hoverPreviewEnabled = d.hoverPreviewEnabled), void 0 === this.config.hoverPreviewArrayCount && (this.config.hoverPreviewArrayCount = d.hoverPreviewArrayCount), void 0 === this.config.hoverPreviewFieldCount && (this.config.hoverPreviewFieldCount = d.hoverPreviewFieldCount), void 0 === this.config.useToJSON && (this.config.useToJSON = d.useToJSON), "" === this.key && (this.key = '""'); }
        return Object.defineProperty(c.prototype, "isOpen", { get: function () { return null !== this._isOpen ? this._isOpen : this.open > 0; }, set: function (t) { this._isOpen = t; }, enumerable: !0, configurable: !0 }), Object.defineProperty(c.prototype, "isDate", { get: function () { return this.json instanceof Date || "string" === this.type && (a.test(this.json) || m.test(this.json) || f.test(this.json)); }, enumerable: !0, configurable: !0 }), Object.defineProperty(c.prototype, "isUrl", { get: function () { return "string" === this.type && 0 === this.json.indexOf("http"); }, enumerable: !0, configurable: !0 }), Object.defineProperty(c.prototype, "isArray", { get: function () { return Array.isArray(this.json); }, enumerable: !0, configurable: !0 }), Object.defineProperty(c.prototype, "isObject", { get: function () { return e(this.json); }, enumerable: !0, configurable: !0 }), Object.defineProperty(c.prototype, "isEmptyObject", { get: function () { return !this.keys.length && !this.isArray; }, enumerable: !0, configurable: !0 }), Object.defineProperty(c.prototype, "isEmpty", { get: function () { return this.isEmptyObject || this.keys && !this.keys.length && this.isArray; }, enumerable: !0, configurable: !0 }), Object.defineProperty(c.prototype, "useToJSON", { get: function () { return this.config.useToJSON && "stringifiable" === this.type; }, enumerable: !0, configurable: !0 }), Object.defineProperty(c.prototype, "hasKey", { get: function () { return void 0 !== this.key; }, enumerable: !0, configurable: !0 }), Object.defineProperty(c.prototype, "constructorName", { get: function () { return r(this.json); }, enumerable: !0, configurable: !0 }), Object.defineProperty(c.prototype, "type", { get: function () { return this.config.useToJSON && this.json && this.json.toJSON ? "stringifiable" : t(this.json); }, enumerable: !0, configurable: !0 }), Object.defineProperty(c.prototype, "keys", { get: function () {
                if (this.isObject) {
                    var t = Object.keys(this.json);
                    return !this.isArray && this.config.sortPropertiesBy ? t.sort(this.config.sortPropertiesBy) : t;
                }
                return [];
            }, enumerable: !0, configurable: !0 }), c.prototype.toggleOpen = function () { this.isOpen = !this.isOpen, this.element && (this.isOpen ? this.appendChildren(this.config.animateOpen) : this.removeChildren(this.config.animateClose), this.element.classList.toggle(i("open"))); }, c.prototype.openAtDepth = function (t) { void 0 === t && (t = 1), t < 0 || (this.open = t, this.isOpen = 0 !== t, this.element && (this.removeChildren(!1), 0 === t ? this.element.classList.remove(i("open")) : (this.appendChildren(this.config.animateOpen), this.element.classList.add(i("open"))))); }, c.prototype.getInlinepreview = function () {
            var t = this;
            if (this.isArray)
                return this.json.length > this.config.hoverPreviewArrayCount ? "Array[" + this.json.length + "]" : "[" + this.json.map(o).join(", ") + "]";
            var e = this.keys, r = e.slice(0, this.config.hoverPreviewFieldCount).map((function (e) { return e + ":" + o(t.json[e]); })), n = e.length >= this.config.hoverPreviewFieldCount ? "…" : "";
            return "{" + r.join(", ") + n + "}";
        }, c.prototype.render = function () {
            this.element = s("div", "row");
            var t = this.isObject ? s("a", "toggler-link") : s("span");
            if (this.isObject && !this.useToJSON && t.appendChild(s("span", "toggler")), this.hasKey && t.appendChild(s("span", "key", this.key + ":")), this.isObject && !this.useToJSON) {
                var e = s("span", "value"), r = s("span"), o = s("span", "constructor-name", this.constructorName);
                if (r.appendChild(o), this.isArray) {
                    var a = s("span");
                    a.appendChild(s("span", "bracket", "[")), a.appendChild(s("span", "number", this.json.length)), a.appendChild(s("span", "bracket", "]")), r.appendChild(a);
                }
                e.appendChild(r), t.appendChild(e);
            }
            else {
                (e = this.isUrl ? s("a") : s("span")).classList.add(i(this.type)), this.isDate && e.classList.add(i("date")), this.isUrl && (e.classList.add(i("url")), e.setAttribute("href", this.json));
                var f = n(this.type, this.json, this.useToJSON ? this.json.toJSON() : this.json);
                e.appendChild(document.createTextNode(f)), t.appendChild(e);
            }
            if (this.isObject && this.config.hoverPreviewEnabled) {
                var m = s("span", "preview-text");
                m.appendChild(document.createTextNode(this.getInlinepreview())), t.appendChild(m);
            }
            var l = s("div", "children");
            return this.isObject && l.classList.add(i("object")), this.isArray && l.classList.add(i("array")), this.isEmpty && l.classList.add(i("empty")), this.config && this.config.theme && this.element.classList.add(i(this.config.theme)), this.isOpen && this.element.classList.add(i("open")), this.element.appendChild(t), this.element.appendChild(l), this.isObject && this.isOpen && this.appendChildren(), this.isObject && !this.useToJSON && t.addEventListener("click", this.toggleOpen.bind(this)), this.element;
        }, c.prototype.appendChildren = function (t) {
            var e = this;
            void 0 === t && (t = !1);
            var r = this.element.querySelector("div." + i("children"));
            if (r && !this.isEmpty)
                if (t) {
                    var n = 0, o = function () { var t = e.keys[n], i = new c(e.json[t], e.open - 1, e.config, t); r.appendChild(i.render()), (n += 1) < e.keys.length && (n > 10 ? o() : l(o)); };
                    l(o);
                }
                else
                    this.keys.forEach((function (t) { var n = new c(e.json[t], e.open - 1, e.config, t); r.appendChild(n.render()); }));
        }, c.prototype.removeChildren = function (t) {
            void 0 === t && (t = !1);
            var e = this.element.querySelector("div." + i("children"));
            if (t) {
                var r = 0, n = function () { e && e.children.length && (e.removeChild(e.children[0]), (r += 1) > 10 ? n() : l(n)); };
                l(n);
            }
            else
                e && (e.innerHTML = "");
        }, c;
    }();
    exports.default = c;
},
"d57683bd1f": /* models/jsoneditor.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a, _b;
    __esModule();
    const dom_1 = require("@bokehjs/core/dom");
    const bokeh_events_1 = require("@bokehjs/core/bokeh_events");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    class JSONEditEvent extends bokeh_events_1.ModelEvent {
        constructor(data) {
            super();
            this.data = data;
        }
        get event_values() {
            return { model: this.origin, data: this.data };
        }
    }
    exports.JSONEditEvent = JSONEditEvent;
    _a = JSONEditEvent;
    JSONEditEvent.__name__ = "JSONEditEvent";
    (() => {
        _a.prototype.event_name = "json_edit";
    })();
    class JSONEditorView extends layout_1.HTMLBoxView {
        connect_signals() {
            super.connect_signals();
            const { data, disabled, templates, menu, mode, search, schema } = this.model.properties;
            this.on_change([data], () => this.editor.update(this.model.data));
            this.on_change([templates], () => {
                this.editor.options.templates = this.model.templates;
            });
            this.on_change([menu], () => {
                this.editor.options.menu = this.model.menu;
            });
            this.on_change([search], () => {
                this.editor.options.search = this.model.search;
            });
            this.on_change([schema], () => {
                this.editor.options.schema = this.model.schema;
            });
            this.on_change([disabled, mode], () => {
                const mode = this.model.disabled ? "view" : this.model.mode;
                this.editor.setMode(mode);
            });
        }
        stylesheets() {
            const styles = super.stylesheets();
            for (const css of this.model.css) {
                styles.push(new dom_1.ImportedStyleSheet(css));
            }
            return styles;
        }
        remove() {
            super.remove();
            this.editor.destroy();
        }
        render() {
            super.render();
            const mode = this.model.disabled ? "view" : this.model.mode;
            this.editor = new window.JSONEditor(this.shadow_el, {
                menu: this.model.menu,
                mode,
                onChangeJSON: (json) => {
                    this.model.data = json;
                },
                onSelectionChange: (start, end) => {
                    this.model.selection = [start, end];
                },
                search: this.model.search,
                schema: this.model.schema,
                templates: this.model.templates,
            });
            this.editor.set(this.model.data);
        }
    }
    exports.JSONEditorView = JSONEditorView;
    JSONEditorView.__name__ = "JSONEditorView";
    class JSONEditor extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.JSONEditor = JSONEditor;
    _b = JSONEditor;
    JSONEditor.__name__ = "JSONEditor";
    JSONEditor.__module__ = "panel.models.jsoneditor";
    (() => {
        _b.prototype.default_view = JSONEditorView;
        _b.define(({ Any, List, Bool, Str }) => ({
            css: [List(Str), []],
            data: [Any, {}],
            mode: [Str, "tree"],
            menu: [Bool, true],
            search: [Bool, true],
            selection: [List(Any), []],
            schema: [Any, null],
            templates: [List(Any), []],
        }));
    })();
},
"f672d71a9f": /* models/katex.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const markup_1 = require("@bokehjs/models/widgets/markup");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    class KaTeXView extends layout_1.PanelMarkupView {
        connect_signals() {
            super.connect_signals();
            const { text } = this.model.properties;
            this.on_change(text, () => this.render());
        }
        render() {
            super.render();
            this.container.innerHTML = this.model.text;
            if (!window.renderMathInElement) {
                return;
            }
            window.renderMathInElement(this.shadow_el, {
                delimiters: [
                    { left: "$$", right: "$$", display: true },
                    { left: "\\[", right: "\\]", display: true },
                    { left: "$", right: "$", display: false },
                    { left: "\\(", right: "\\)", display: false },
                ],
            });
        }
    }
    exports.KaTeXView = KaTeXView;
    KaTeXView.__name__ = "KaTeXView";
    class KaTeX extends markup_1.Markup {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.KaTeX = KaTeX;
    _a = KaTeX;
    KaTeX.__name__ = "KaTeX";
    KaTeX.__module__ = "panel.models.katex";
    (() => {
        _a.prototype.default_view = KaTeXView;
    })();
},
"bd8e0fe48b": /* models/location.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const view_1 = require("@bokehjs/core/view");
    const model_1 = require("@bokehjs/model");
    class LocationView extends view_1.View {
        initialize() {
            super.initialize();
            this.model.pathname = window.location.pathname;
            this.model.search = window.location.search;
            this.model.hash = window.location.hash;
            // Readonly parameters on python side
            this.model.href = window.location.href;
            this.model.hostname = window.location.hostname;
            this.model.protocol = window.location.protocol;
            this.model.port = window.location.port;
            this._hash_listener = () => {
                this.model.hash = window.location.hash;
            };
            window.addEventListener("hashchange", this._hash_listener);
            this._has_finished = true;
            this.notify_finished();
        }
        connect_signals() {
            super.connect_signals();
            const { pathname, search, hash, reload } = this.model.properties;
            this.on_change(pathname, () => this.update("pathname"));
            this.on_change(search, () => this.update("search"));
            this.on_change(hash, () => this.update("hash"));
            this.on_change(reload, () => this.update("reload"));
        }
        remove() {
            super.remove();
            window.removeEventListener("hashchange", this._hash_listener);
        }
        update(change) {
            if (!this.model.reload || (change === "reload")) {
                window.history.pushState({}, "", `${this.model.pathname}${this.model.search}${this.model.hash}`);
                this.model.href = window.location.href;
                if (change === "reload") {
                    window.location.reload();
                }
            }
            else {
                if (change == "pathname") {
                    window.location.pathname = (this.model.pathname);
                }
                if (change == "search") {
                    window.location.search = (this.model.search);
                }
                if (change == "hash") {
                    window.location.hash = (this.model.hash);
                }
            }
        }
    }
    exports.LocationView = LocationView;
    LocationView.__name__ = "LocationView";
    class Location extends model_1.Model {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.Location = Location;
    _a = Location;
    Location.__name__ = "Location";
    Location.__module__ = "panel.models.location";
    (() => {
        _a.prototype.default_view = LocationView;
        _a.define(({ Bool, Str }) => ({
            href: [Str, ""],
            hostname: [Str, ""],
            pathname: [Str, ""],
            protocol: [Str, ""],
            port: [Str, ""],
            search: [Str, ""],
            hash: [Str, ""],
            reload: [Bool, false],
        }));
    })();
},
"ec353a3d9a": /* models/mathjax.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const markup_1 = require("@bokehjs/models/widgets/markup");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    class MathJaxView extends layout_1.PanelMarkupView {
        connect_signals() {
            super.connect_signals();
            const { text } = this.model.properties;
            this.on_change(text, () => this.render());
        }
        render() {
            super.render();
            this.container.innerHTML = this.has_math_disabled() ? this.model.text : this.process_tex(this.model.text);
        }
    }
    exports.MathJaxView = MathJaxView;
    MathJaxView.__name__ = "MathJaxView";
    class MathJax extends markup_1.Markup {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.MathJax = MathJax;
    _a = MathJax;
    MathJax.__name__ = "MathJax";
    MathJax.__module__ = "panel.models.mathjax";
    (() => {
        _a.prototype.default_view = MathJaxView;
    })();
},
"cf33f23f5c": /* models/pdf.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const markup_1 = require("@bokehjs/models/widgets/markup");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    const html_1 = require("89d2d3667a") /* ./html */;
    class PDFView extends layout_1.PanelMarkupView {
        connect_signals() {
            super.connect_signals();
            const { text, width, height, embed, start_page } = this.model.properties;
            this.on_change([text, width, height, embed, start_page], () => { this.update(); });
        }
        render() {
            super.render();
            this.update();
        }
        update() {
            if (this.model.embed) {
                const blob = this.convert_base64_to_blob();
                const url = URL.createObjectURL(blob);
                this.container.innerHTML = `<embed src="${url}#page=${this.model.start_page}" type="application/pdf" width="100%" height="100%"></embed>`;
            }
            else {
                const html = (0, html_1.htmlDecode)(this.model.text);
                this.container.innerHTML = html || "";
            }
        }
        convert_base64_to_blob() {
            const byte_characters = atob(this.model.text);
            const slice_size = 512;
            const byte_arrays = [];
            for (let offset = 0; offset < byte_characters.length; offset += slice_size) {
                const slice = byte_characters.slice(offset, offset + slice_size);
                const byte_numbers = new Uint8Array(slice.length);
                for (let i = 0; i < slice.length; i++) {
                    byte_numbers[i] = slice.charCodeAt(i);
                }
                byte_arrays.push(byte_numbers);
            }
            return new Blob(byte_arrays, { type: "application/pdf" });
        }
    }
    exports.PDFView = PDFView;
    PDFView.__name__ = "PDFView";
    class PDF extends markup_1.Markup {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.PDF = PDF;
    _a = PDF;
    PDF.__name__ = "PDF";
    PDF.__module__ = "panel.models.markup";
    (() => {
        _a.prototype.default_view = PDFView;
        _a.define(({ Int, Bool }) => ({
            embed: [Bool, false],
            start_page: [Int, 1],
        }));
    })();
},
"54dac9b7a1": /* models/perspective.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a, _b;
    __esModule();
    const bokeh_events_1 = require("@bokehjs/core/bokeh_events");
    const dom_1 = require("@bokehjs/core/dom");
    const column_data_source_1 = require("@bokehjs/models/sources/column_data_source");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    const THEMES = {
        "pro-dark": "Pro Dark",
        pro: "Pro Light",
        vaporwave: "Vaporwave",
        solarized: "Solarized",
        "solarized-dark": "Solarized Dark",
        monokai: "Monokai",
    };
    const PLUGINS = {
        datagrid: "Datagrid",
        d3_x_bar: "X Bar",
        d3_y_bar: "Y Bar",
        d3_xy_line: "X/Y Line",
        d3_y_line: "Y Line",
        d3_y_area: "Y Area",
        d3_y_scatter: "Y Scatter",
        d3_xy_scatter: "X/Y Scatter",
        d3_treemap: "Treemap",
        d3_candlestick: "Candlestick",
        d3_sunburst: "Sunburst",
        d3_heatmap: "Heatmap",
        d3_ohlc: "OHLC",
    };
    function objectFlip(obj) {
        const ret = {};
        Object.keys(obj).forEach(key => {
            ret[obj[key]] = key;
        });
        return ret;
    }
    const PLUGINS_REVERSE = objectFlip(PLUGINS);
    const THEMES_REVERSE = objectFlip(THEMES);
    class PerspectiveClickEvent extends bokeh_events_1.ModelEvent {
        constructor(config, column_names, row) {
            super();
            this.config = config;
            this.column_names = column_names;
            this.row = row;
        }
        get event_values() {
            return { model: this.origin, config: this.config, column_names: this.column_names, row: this.row };
        }
    }
    exports.PerspectiveClickEvent = PerspectiveClickEvent;
    _a = PerspectiveClickEvent;
    PerspectiveClickEvent.__name__ = "PerspectiveClickEvent";
    (() => {
        _a.prototype.event_name = "perspective-click";
    })();
    class PerspectiveView extends layout_1.HTMLBoxView {
        constructor() {
            super(...arguments);
            this._updating = false;
            this._config_listener = null;
            this._current_config = null;
            this._loaded = false;
        }
        connect_signals() {
            super.connect_signals();
            this.connect(this.model.source.properties.data.change, () => this.setData());
            this.connect(this.model.source.streaming, () => this.stream());
            this.connect(this.model.source.patching, () => this.patch());
            const { schema, toggle_config, columns, expressions, split_by, group_by, aggregates, filters, sort, plugin, selectable, editable, theme, title, settings, } = this.model.properties;
            const not_updating = (fn) => {
                return () => {
                    if (this._updating) {
                        return;
                    }
                    fn();
                };
            };
            this.on_change(schema, () => {
                this.worker.table(this.model.schema).then((table) => {
                    this.table = table;
                    this.table.update(this.data);
                    this.perspective_element.load(this.table);
                });
            });
            this.on_change(toggle_config, () => {
                this.perspective_element.toggleConfig();
            });
            this.on_change(columns, not_updating(() => {
                this.perspective_element.restore({ columns: this.model.columns });
            }));
            this.on_change(expressions, not_updating(() => {
                this.perspective_element.restore({ expressions: this.model.expressions });
            }));
            this.on_change(split_by, not_updating(() => {
                this.perspective_element.restore({ split_by: this.model.split_by });
            }));
            this.on_change(group_by, not_updating(() => {
                this.perspective_element.restore({ group_by: this.model.group_by });
            }));
            this.on_change(aggregates, not_updating(() => {
                this.perspective_element.restore({ aggregates: this.model.aggregates });
            }));
            this.on_change(filters, not_updating(() => {
                this.perspective_element.restore({ filter: this.model.filters });
            }));
            this.on_change(settings, not_updating(() => {
                this.perspective_element.restore({ settings: this.model.settings });
            }));
            this.on_change(title, not_updating(() => {
                this.perspective_element.restore({ title: this.model.title });
            }));
            this.on_change(sort, not_updating(() => {
                this.perspective_element.restore({ sort: this.model.sort });
            }));
            this.on_change(plugin, not_updating(() => {
                this.perspective_element.restore({ plugin: PLUGINS[this.model.plugin] });
            }));
            this.on_change(selectable, not_updating(() => {
                this.perspective_element.restore({ plugin_config: { ...this._current_config, selectable: this.model.selectable } });
            }));
            this.on_change(editable, not_updating(() => {
                this.perspective_element.restore({ plugin_config: { ...this._current_config, editable: this.model.editable } });
            }));
            this.on_change(theme, not_updating(() => {
                this.perspective_element.restore({ theme: THEMES[this.model.theme] }).catch(() => { });
            }));
        }
        disconnect_signals() {
            if (this._config_listener != null) {
                this.perspective_element.removeEventListener("perspective-config-update", this._config_listener);
            }
            this._config_listener = null;
            super.disconnect_signals();
        }
        remove() {
            this.perspective_element.delete(() => this.worker.terminate());
            super.remove();
        }
        render() {
            super.render();
            this.worker = window.perspective.worker();
            const container = (0, dom_1.div)({
                class: "pnx-perspective-viewer",
                style: {
                    zIndex: 0,
                },
            });
            container.innerHTML = "<perspective-viewer style='height:100%; width:100%;'></perspective-viewer>";
            this.perspective_element = container.children[0];
            this.perspective_element.resetThemes([...Object.values(THEMES)]).catch(() => { });
            if (this.model.toggle_config) {
                this.perspective_element.toggleConfig();
            }
            (0, layout_1.set_size)(container, this.model);
            this.shadow_el.appendChild(container);
            this.worker.table(this.model.schema).then((table) => {
                this.table = table;
                this.table.update(this.data);
                this.perspective_element.load(this.table);
                const plugin_config = {
                    ...this.model.plugin_config,
                    editable: this.model.editable,
                    selectable: this.model.selectable,
                };
                this.perspective_element.restore({
                    aggregates: this.model.aggregates,
                    columns: this.model.columns,
                    columns_config: this.model.columns_config,
                    expressions: this.model.expressions,
                    filter: this.model.filters,
                    split_by: this.model.split_by,
                    group_by: this.model.group_by,
                    plugin: PLUGINS[this.model.plugin],
                    plugin_config,
                    settings: this.model.settings,
                    sort: this.model.sort,
                    theme: THEMES[this.model.theme],
                    title: this.model.title,
                }).catch(() => { });
                this.perspective_element.save().then((config) => {
                    this._current_config = config;
                });
                this._config_listener = () => this.sync_config();
                this.perspective_element.addEventListener("perspective-config-update", this._config_listener);
                this.perspective_element.addEventListener("perspective-click", (event) => {
                    this.model.trigger_event(new PerspectiveClickEvent(event.detail.config, event.detail.column_names, event.detail.row));
                });
                this._loaded = true;
            });
        }
        sync_config() {
            if (this._updating) {
                return true;
            }
            this.perspective_element.save().then((config) => {
                this._current_config = config;
                const props = {};
                for (let option in config) {
                    let value = config[option];
                    if (value === undefined || (option == "plugin" && value === "debug") || option == "version" || this.model.properties.hasOwnProperty(option) === undefined) {
                        continue;
                    }
                    if (option === "filter") {
                        option = "filters";
                    }
                    else if (option === "plugin") {
                        value = PLUGINS_REVERSE[value];
                    }
                    else if (option === "theme") {
                        value = THEMES_REVERSE[value];
                    }
                    props[option] = value;
                }
                this._updating = true;
                this.model.setv(props);
                this._updating = false;
            });
            return true;
        }
        get data() {
            const data = {};
            for (const column of this.model.source.columns()) {
                let array = this.model.source.get_array(column);
                if (this.model.schema[column] == "datetime" && array.includes(-9223372036854776)) {
                    array = array.map((v) => v === -9223372036854776 ? null : v);
                }
                data[column] = array;
            }
            return data;
        }
        setData() {
            if (!this._loaded) {
                return;
            }
            for (const col of this.model.source.columns()) {
                if (!(col in this.model.schema)) {
                    return;
                }
            }
            this.table.replace(this.data);
        }
        stream() {
            if (this._loaded) {
                this.table.replace(this.data);
            }
        }
        patch() {
            if (this._loaded) {
                this.table.replace(this.data);
            }
        }
    }
    exports.PerspectiveView = PerspectiveView;
    PerspectiveView.__name__ = "PerspectiveView";
    class Perspective extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.Perspective = Perspective;
    _b = Perspective;
    Perspective.__name__ = "Perspective";
    Perspective.__module__ = "panel.models.perspective";
    (() => {
        _b.prototype.default_view = PerspectiveView;
        _b.define(({ Any, List, Bool, Ref, Nullable, Str }) => ({
            aggregates: [Any, {}],
            columns: [List(Nullable(Str)), []],
            columns_config: [Any, {}],
            expressions: [Any, {}],
            split_by: [Nullable(List(Str)), null],
            editable: [Bool, true],
            filters: [Nullable(List(Any)), null],
            group_by: [Nullable(List(Str)), null],
            plugin: [Str],
            plugin_config: [Any, {}],
            selectable: [Bool, true],
            settings: [Bool, true],
            schema: [Any, {}],
            toggle_config: [Bool, true],
            sort: [Nullable(List(List(Str))), null],
            source: [Ref(column_data_source_1.ColumnDataSource)],
            theme: [Str, "pro"],
            title: [Nullable(Str), null],
        }));
    })();
},
"f06104d237": /* models/player.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const kinds_1 = require("@bokehjs/core/kinds");
    const dom_1 = require("@bokehjs/core/dom");
    const widget_1 = require("@bokehjs/models/widgets/widget");
    const SVG_STRINGS = {
        slower: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-minus" width="24" \
 height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none"\
  stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" \
   fill="none"/><path d="M5 12l14 0" /></svg>',
        first: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-track-prev-filled" \
 width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" \
  stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/>\
   <path d="M20.341 4.247l-8 7a1 1 0 0 0 0 1.506l8 7c.647 .565 1.659 .106 1.659 -.753v-14c0 -.86 \
    -1.012 -1.318 -1.659 -.753z" stroke-width="0" fill="currentColor" /><path d="M9.341 4.247l-8 7a1 \
     1 0 0 0 0 1.506l8 7c.647 .565 1.659 .106 1.659 -.753v-14c0 -.86 -1.012 -1.318 -1.659 -.753z" \
      stroke-width="0" fill="currentColor" /></svg>',
        previous: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-skip-back-filled" \
 width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" \
  stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/> \
   <path d="M19.496 4.136l-12 7a1 1 0 0 0 0 1.728l12 7a1 1 0 0 0 1.504 -.864v-14a1 1 0 0 0 -1.504 -.864z" \
    stroke-width="0" fill="currentColor" /><path d="M4 4a1 1 0 0 1 .993 .883l.007 .117v14a1 1 0 0 1 -1.993 \
     .117l-.007 -.117v-14a1 1 0 0 1 1 -1z" stroke-width="0" fill="currentColor" /></svg>',
        reverse: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-play-filled"\
 width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none"\
  stroke-linecap="round" stroke-linejoin="round" style="transform: scaleX(-1);"><path stroke="none"\
   d="M0 0h24v24H0z" fill="none"/><path d="M6 4v16a1 1 0 0 0 1.524 .852l13 -8a1 1 0 0 0 0 -1.704l-13\
    -8a1 1 0 0 0 -1.524 .852z" stroke-width="0" fill="currentColor" /></svg>',
        pause: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-pause-filled" \
 width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" \
  stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" \
   fill="none"/><path d="M9 4h-2a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h2a2 2 0 0 0 2 -2v-12a2 2 0 \
    0 0 -2 -2z" stroke-width="0" fill="currentColor" /><path d="M17 4h-2a2 2 0 0 0 -2 2v12a2 \
     2 0 0 0 2 2h2a2 2 0 0 0 2 -2v-12a2 2 0 0 0 -2 -2z" stroke-width="0" fill="currentColor" /></svg>',
        play: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-play-filled" \
 width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" \
  stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" \
   fill="none"/><path d="M6 4v16a1 1 0 0 0 1.524 .852l13 -8a1 1 0 0 0 0 -1.704l-13 -8a1 \
    1 0 0 0 -1.524 .852z" stroke-width="0" fill="currentColor" /></svg>',
        next: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-skip-forward-filled" \
 width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" \
  stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"/> \
  <path d="M3 5v14a1 1 0 0 0 1.504 .864l12 -7a1 1 0 0 0 0 -1.728l-12 -7a1 1 0 0 0 -1.504 .864z" \
   stroke-width="0" fill="currentColor" /><path d="M20 4a1 1 0 0 1 .993 .883l.007 .117v14a1 1 0 0 \
    1 -1.993 .117l-.007 -.117v-14a1 1 0 0 1 1 -1z" stroke-width="0" fill="currentColor" /></svg>',
        last: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-player-track-next-filled" \
 width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" \
  stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" \
   fill="none"/><path d="M2 5v14c0 .86 1.012 1.318 1.659 .753l8 -7a1 1 0 0 0 0 -1.506l-8 \
   -7c-.647 -.565 -1.659 -.106 -1.659 .753z" stroke-width="0" fill="currentColor" /><path \
    d="M13 5v14c0 .86 1.012 1.318 1.659 .753l8 -7a1 1 0 0 0 0 -1.506l-8 -7c-.647 -.565 -1.659 \
     -.106 -1.659 .753z" stroke-width="0" fill="currentColor" /></svg>',
        faster: '<svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-plus" \
 width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" \
  stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" \
   fill="none"/><path d="M12 5l0 14" /><path d="M5 12l14 0" /></svg>',
    };
    function press(btn_list) {
        btn_list.forEach((btn) => btn.style.borderStyle = "inset");
    }
    function unpress(btn_list) {
        btn_list.forEach((btn) => btn.style.borderStyle = "outset");
    }
    class PlayerView extends widget_1.WidgetView {
        constructor() {
            super(...arguments);
            this._changing = false;
        }
        connect_signals() {
            super.connect_signals();
            const { direction, value, loop_policy, disabled, show_loop_controls } = this.model.properties;
            this.on_change(direction, () => this.set_direction());
            this.on_change(value, () => this.render());
            this.on_change(loop_policy, () => this.set_loop_state(this.model.loop_policy));
            this.on_change(disabled, () => this.toggle_disable());
            this.on_change(show_loop_controls, () => {
                if (this.model.show_loop_controls && this.loop_state.parentNode != this.groupEl) {
                    this.groupEl.appendChild(this.loop_state);
                }
                else if (!this.model.show_loop_controls && this.loop_state.parentNode == this.groupEl) {
                    this.groupEl.removeChild(this.loop_state);
                }
            });
        }
        toggle_disable() {
            this.sliderEl.disabled = this.model.disabled;
            for (const el of this.buttonEl.children) {
                const anyEl = el;
                anyEl.disabled = this.model.disabled;
            }
            for (const el of this.loop_state.children) {
                if (el.tagName == "input") {
                    const anyEl = el;
                    anyEl.disabled = this.model.disabled;
                }
            }
        }
        get_height() {
            return 250;
        }
        render() {
            if (this.sliderEl == null) {
                super.render();
            }
            else {
                this.sliderEl.min = String(this.model.start);
                this.sliderEl.max = String(this.model.end);
                this.sliderEl.value = String(this.model.value);
                return;
            }
            // Layout to group the elements
            this.groupEl = (0, dom_1.div)();
            this.groupEl.style.display = "flex";
            this.groupEl.style.flexDirection = "column";
            this.groupEl.style.alignItems = "center";
            // Slider
            this.sliderEl = document.createElement("input");
            this.sliderEl.style.width = "100%";
            this.sliderEl.setAttribute("type", "range");
            this.sliderEl.value = String(this.model.value);
            this.sliderEl.min = String(this.model.start);
            this.sliderEl.max = String(this.model.end);
            this.sliderEl.addEventListener("input", (ev) => {
                this.set_frame(parseInt(ev.target.value), false);
            });
            this.sliderEl.addEventListener("change", (ev) => {
                this.set_frame(parseInt(ev.target.value));
            });
            // Buttons
            const button_div = (0, dom_1.div)();
            this.buttonEl = button_div;
            button_div.style.cssText = "margin: 0 auto; display: flex; padding: 5px; align-items: stretch; width: 100%;";
            const button_style_small = "text-align: center; min-width: 20px; flex-grow: 1; margin: 2px";
            const button_style = "text-align: center; min-width: 40px; flex-grow: 2; margin: 2px";
            const slower = document.createElement("button");
            slower.style.cssText = button_style_small;
            slower.innerHTML = SVG_STRINGS.slower;
            slower.onclick = () => this.slower();
            button_div.appendChild(slower);
            const first = document.createElement("button");
            first.style.cssText = button_style;
            first.innerHTML = SVG_STRINGS.first;
            first.onclick = () => this.first_frame();
            button_div.appendChild(first);
            const previous = document.createElement("button");
            previous.style.cssText = button_style;
            previous.innerHTML = SVG_STRINGS.previous;
            previous.onclick = () => this.previous_frame();
            button_div.appendChild(previous);
            const reverse = document.createElement("button");
            reverse.style.cssText = button_style;
            reverse.innerHTML = SVG_STRINGS.reverse;
            reverse.onclick = () => this.reverse_animation();
            button_div.appendChild(reverse);
            const pause = document.createElement("button");
            pause.style.cssText = button_style;
            pause.innerHTML = SVG_STRINGS.pause;
            pause.onclick = () => this.pause_animation();
            button_div.appendChild(pause);
            const play = document.createElement("button");
            play.style.cssText = button_style;
            play.innerHTML = SVG_STRINGS.play;
            play.onclick = () => this.play_animation();
            button_div.appendChild(play);
            const next = document.createElement("button");
            next.style.cssText = button_style;
            next.innerHTML = SVG_STRINGS.next;
            next.onclick = () => this.next_frame();
            button_div.appendChild(next);
            const last = document.createElement("button");
            last.style.cssText = button_style;
            last.innerHTML = SVG_STRINGS.last;
            last.onclick = () => this.last_frame();
            button_div.appendChild(last);
            const faster = document.createElement("button");
            faster.style.cssText = button_style_small;
            faster.innerHTML = SVG_STRINGS.faster;
            faster.onclick = () => this.faster();
            button_div.appendChild(faster);
            // toggle
            this._toggle_reverse = () => {
                unpress([pause, play]);
                press([reverse]);
            };
            this._toogle_pause = () => {
                unpress([reverse, play]);
                press([pause]);
            };
            this._toggle_play = () => {
                unpress([reverse, pause]);
                press([play]);
            };
            // Loop control
            this.loop_state = document.createElement("form");
            this.loop_state.style.cssText = "margin: 0 auto; display: table";
            const once = document.createElement("input");
            once.type = "radio";
            once.value = "once";
            once.name = "state";
            const once_label = document.createElement("label");
            once_label.innerHTML = "Once";
            once_label.style.cssText = "padding: 0 10px 0 5px; user-select:none;";
            const loop = document.createElement("input");
            loop.setAttribute("type", "radio");
            loop.setAttribute("value", "loop");
            loop.setAttribute("name", "state");
            const loop_label = document.createElement("label");
            loop_label.innerHTML = "Loop";
            loop_label.style.cssText = "padding: 0 10px 0 5px; user-select:none;";
            const reflect = document.createElement("input");
            reflect.setAttribute("type", "radio");
            reflect.setAttribute("value", "reflect");
            reflect.setAttribute("name", "state");
            const reflect_label = document.createElement("label");
            reflect_label.innerHTML = "Reflect";
            reflect_label.style.cssText = "padding: 0 10px 0 5px; user-select:none;";
            if (this.model.loop_policy == "once") {
                once.checked = true;
            }
            else if (this.model.loop_policy == "loop") {
                loop.checked = true;
            }
            else {
                reflect.checked = true;
            }
            // Compose everything
            this.loop_state.appendChild(once);
            this.loop_state.appendChild(once_label);
            this.loop_state.appendChild(loop);
            this.loop_state.appendChild(loop_label);
            this.loop_state.appendChild(reflect);
            this.loop_state.appendChild(reflect_label);
            this.groupEl.appendChild(this.sliderEl);
            this.groupEl.appendChild(button_div);
            if (this.model.show_loop_controls) {
                this.groupEl.appendChild(this.loop_state);
            }
            this.toggle_disable();
            this.shadow_el.appendChild(this.groupEl);
        }
        set_frame(frame, throttled = true) {
            this.model.value = frame;
            if (throttled) {
                this.model.value_throttled = frame;
            }
            if (this.sliderEl.value != String(frame)) {
                this.sliderEl.value = String(frame);
            }
        }
        get_loop_state() {
            const button_group = this.loop_state.state;
            for (let i = 0; i < button_group.length; i++) {
                const button = button_group[i];
                if (button.checked) {
                    return button.value;
                }
            }
            return "once";
        }
        set_loop_state(state) {
            const button_group = this.loop_state.state;
            for (let i = 0; i < button_group.length; i++) {
                const button = button_group[i];
                if (button.value == state) {
                    button.checked = true;
                }
            }
        }
        next_frame() {
            this.set_frame(Math.min(this.model.end, this.model.value + this.model.step));
        }
        previous_frame() {
            this.set_frame(Math.max(this.model.start, this.model.value - this.model.step));
        }
        first_frame() {
            this.set_frame(this.model.start);
        }
        last_frame() {
            this.set_frame(this.model.end);
        }
        slower() {
            this.model.interval = Math.round(this.model.interval / 0.7);
            if (this.model.direction > 0) {
                this.play_animation();
            }
            else if (this.model.direction < 0) {
                this.reverse_animation();
            }
        }
        faster() {
            this.model.interval = Math.round(this.model.interval * 0.7);
            if (this.model.direction > 0) {
                this.play_animation();
            }
            else if (this.model.direction < 0) {
                this.reverse_animation();
            }
        }
        anim_step_forward() {
            if (this.model.value < this.model.end) {
                this.next_frame();
            }
            else {
                const loop_state = this.get_loop_state();
                if (loop_state == "loop") {
                    this.first_frame();
                }
                else if (loop_state == "reflect") {
                    this.last_frame();
                    this.reverse_animation();
                }
                else {
                    this.pause_animation();
                    this.last_frame();
                }
            }
        }
        anim_step_reverse() {
            if (this.model.value > this.model.start) {
                this.previous_frame();
            }
            else {
                const loop_state = this.get_loop_state();
                if (loop_state == "loop") {
                    this.last_frame();
                }
                else if (loop_state == "reflect") {
                    this.first_frame();
                    this.play_animation();
                }
                else {
                    this.pause_animation();
                    this.first_frame();
                }
            }
        }
        set_direction() {
            if (this._changing) {
                return;
            }
            else if (this.model.direction === 0) {
                this.pause_animation();
            }
            else if (this.model.direction === 1) {
                this.play_animation();
            }
            else if (this.model.direction === -1) {
                this.reverse_animation();
            }
        }
        pause_animation() {
            this._toogle_pause();
            this._changing = true;
            this.model.direction = 0;
            this._changing = false;
            if (this.timer) {
                clearInterval(this.timer);
                this.timer = null;
            }
        }
        play_animation() {
            this.pause_animation();
            this._toggle_play();
            this._changing = true;
            this.model.direction = 1;
            this._changing = false;
            if (!this.timer) {
                this.timer = setInterval(() => this.anim_step_forward(), this.model.interval);
            }
        }
        reverse_animation() {
            this.pause_animation();
            this._toggle_reverse();
            this._changing = true;
            this.model.direction = -1;
            this._changing = false;
            if (!this.timer) {
                this.timer = setInterval(() => this.anim_step_reverse(), this.model.interval);
            }
        }
    }
    exports.PlayerView = PlayerView;
    PlayerView.__name__ = "PlayerView";
    exports.LoopPolicy = (0, kinds_1.Enum)("once", "loop", "reflect");
    class Player extends widget_1.Widget {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.Player = Player;
    _a = Player;
    Player.__name__ = "Player";
    Player.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = PlayerView;
        _a.define(({ Bool, Int }) => ({
            direction: [Int, 0],
            interval: [Int, 500],
            start: [Int, 0],
            end: [Int, 10],
            step: [Int, 1],
            loop_policy: [exports.LoopPolicy, "once"],
            value: [Int, 0],
            value_throttled: [Int, 0],
            show_loop_controls: [Bool, true],
        }));
        _a.override({ width: 400 });
    })();
},
"c08950da15": /* models/plotly.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tslib_1 = require("tslib");
    const dom_1 = require("@bokehjs/core/dom");
    const types_1 = require("@bokehjs/core/util/types");
    const object_1 = require("@bokehjs/core/util/object");
    const eq_1 = require("@bokehjs/core/util/eq");
    const column_data_source_1 = require("@bokehjs/models/sources/column_data_source");
    const debounce_1 = require("99a25e6992") /* debounce */;
    const util_1 = require("27e2a99e99") /* ./util */;
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    const plotly_css_1 = tslib_1.__importDefault(require("ce7c8e2a4f") /* ../styles/models/plotly.css */);
    function convertUndefined(obj) {
        Object
            .entries(obj)
            .forEach(([key, value]) => {
            if ((0, types_1.isPlainObject)(value)) {
                convertUndefined(value);
            }
            else if (value === undefined) {
                obj[key] = null;
            }
        });
        return obj;
    }
    const filterEventData = (gd, eventData, event) => {
        // Ported from dash-core-components/src/components/Graph.react.js
        const filteredEventData = Array.isArray(eventData) ? [] : {};
        if (event === "click" || event === "hover" || event === "selected") {
            const points = [];
            if (eventData === undefined || eventData === null) {
                return null;
            }
            /*
             * remove `data`, `layout`, `xaxis`, etc
             * objects from the event data since they're so big
             * and cause JSON stringify circular structure errors.
             *
             * also, pull down the `customdata` point from the data array
             * into the event object
             */
            const data = gd.data;
            for (let i = 0; i < eventData.points.length; i++) {
                const fullPoint = eventData.points[i];
                const pointData = {};
                for (const property in fullPoint) {
                    const val = fullPoint[property];
                    if (fullPoint.hasOwnProperty(property) &&
                        !Array.isArray(val) && !(0, types_1.isPlainObject)(val) &&
                        val !== undefined) {
                        pointData[property] = val;
                    }
                }
                if (fullPoint !== undefined && fullPoint !== null) {
                    if (fullPoint.hasOwnProperty("curveNumber") &&
                        fullPoint.hasOwnProperty("pointNumber") &&
                        data[fullPoint.curveNumber].hasOwnProperty("customdata")) {
                        pointData.customdata =
                            data[fullPoint.curveNumber].customdata[fullPoint.pointNumber];
                    }
                    // specific to histogram. see https://github.com/plotly/plotly.js/pull/2113/
                    if (fullPoint.hasOwnProperty("pointNumbers")) {
                        pointData.pointNumbers = fullPoint.pointNumbers;
                    }
                }
                points[i] = pointData;
            }
            filteredEventData.points = points;
        }
        else if (event === "relayout" || event === "restyle") {
            /*
             * relayout shouldn't include any big objects
             * it will usually just contain the ranges of the axes like
             * "xaxis.range[0]": 0.7715822247381828,
             * "xaxis.range[1]": 3.0095292008680063`
             */
            for (const property in eventData) {
                if (eventData.hasOwnProperty(property)) {
                    filteredEventData[property] = eventData[property];
                }
            }
        }
        if (eventData.hasOwnProperty("range")) {
            filteredEventData.range = eventData.range;
        }
        if (eventData.hasOwnProperty("lassoPoints")) {
            filteredEventData.lassoPoints = eventData.lassoPoints;
        }
        return convertUndefined(filteredEventData);
    };
    const _isHidden = (gd) => {
        const display = window.getComputedStyle(gd).display;
        return !display || display === "none";
    };
    class PlotlyPlotView extends layout_1.HTMLBoxView {
        constructor() {
            super(...arguments);
            this._settingViewport = false;
            this._plotInitialized = false;
            this._rendered = false;
            this._reacting = false;
            this._relayouting = false;
            this._end_relayouting = (0, debounce_1.debounce)(() => {
                this._relayouting = false;
            }, 2000, false);
        }
        connect_signals() {
            super.connect_signals();
            const { data, data_sources, layout, relayout, restyle, viewport_update_policy, viewport_update_throttle, _render_count, frames, viewport, } = this.model.properties;
            this.on_change([data, data_sources, layout], () => {
                const render_count = this.model._render_count;
                setTimeout(() => {
                    if (this.model._render_count === render_count) {
                        this.model._render_count += 1;
                    }
                }, 250);
            });
            this.on_change(relayout, () => {
                if (this.model.relayout == null) {
                    return;
                }
                window.Plotly.relayout(this.container, this.model.relayout);
                this.model.relayout = null;
            });
            this.on_change(restyle, () => {
                if (this.model.restyle == null) {
                    return;
                }
                window.Plotly.restyle(this.container, this.model.restyle.data, this.model.restyle.traces);
                this.model.restyle = null;
            });
            this.on_change(viewport_update_policy, () => {
                this._updateSetViewportFunction();
            });
            this.on_change(viewport_update_throttle, () => {
                this._updateSetViewportFunction();
            });
            this.on_change(_render_count, () => {
                this.plot();
            });
            this.on_change(frames, () => {
                this.plot(true);
            });
            this.on_change(viewport, () => {
                this._updateViewportFromProperty();
            });
        }
        stylesheets() {
            return [...super.stylesheets(), plotly_css_1.default];
        }
        remove() {
            if (this.container != null) {
                window.Plotly.purge(this.container);
            }
            super.remove();
        }
        render() {
            super.render();
            this.container = (0, dom_1.div)();
            (0, layout_1.set_size)(this.container, this.model);
            this._rendered = false;
            this.shadow_el.appendChild(this.container);
            this.watch_stylesheets();
            this.plot().then(() => {
                this._rendered = true;
                if (this.model.relayout != null) {
                    window.Plotly.relayout(this.container, this.model.relayout);
                }
                window.Plotly.Plots.resize(this.container);
            });
        }
        style_redraw() {
            if (this._rendered && this.container != null) {
                window.Plotly.Plots.resize(this.container);
            }
        }
        after_layout() {
            super.after_layout();
            if (this._rendered && this.container != null) {
                window.Plotly.Plots.resize(this.container);
            }
        }
        _trace_data() {
            const data = [];
            for (let i = 0; i < this.model.data.length; i++) {
                data.push(this._get_trace(i, false));
            }
            return data;
        }
        _layout_data() {
            const newLayout = (0, util_1.deepCopy)(this.model.layout);
            if (this._relayouting) {
                const { layout } = this.container;
                // For each xaxis* and yaxis* property of layout, if the value has a 'range'
                // property then use this in newLayout
                Object.keys(layout).reduce((value, key) => {
                    if (key.slice(1, 5) === "axis" && "range" in value) {
                        newLayout[key].range = value.range;
                    }
                }, {});
            }
            return newLayout;
        }
        _install_callbacks() {
            //  - plotly_relayout
            this.container.on("plotly_relayout", (eventData) => {
                if (eventData._update_from_property !== true) {
                    this.model.relayout_data = filterEventData(this.container, eventData, "relayout");
                    this._updateViewportProperty();
                    this._end_relayouting();
                }
            });
            //  - plotly_relayouting
            this.container.on("plotly_relayouting", () => {
                if (this.model.viewport_update_policy !== "mouseup") {
                    this._relayouting = true;
                    this._updateViewportProperty();
                }
            });
            //  - plotly_restyle
            this.container.on("plotly_restyle", (eventData) => {
                this.model.restyle_data = filterEventData(this.container, eventData, "restyle");
                this._updateViewportProperty();
            });
            //  - plotly_click
            this.container.on("plotly_click", (eventData) => {
                this.model.click_data = filterEventData(this.container, eventData, "click");
            });
            //  - plotly_hover
            this.container.on("plotly_hover", (eventData) => {
                this.model.hover_data = filterEventData(this.container, eventData, "hover");
            });
            //  - plotly_selected
            this.container.on("plotly_selected", (eventData) => {
                this.model.selected_data = filterEventData(this.container, eventData, "selected");
            });
            //  - plotly_clickannotation
            this.container.on("plotly_clickannotation", (eventData) => {
                delete eventData.event;
                delete eventData.fullAnnotation;
                this.model.clickannotation_data = eventData;
            });
            //  - plotly_deselect
            this.container.on("plotly_deselect", () => {
                this.model.selected_data = null;
            });
            //  - plotly_unhover
            this.container.on("plotly_unhover", () => {
                this.model.hover_data = null;
            });
        }
        async plot(new_plot = false) {
            if (!window.Plotly) {
                return;
            }
            const data = this._trace_data();
            const newLayout = this._layout_data();
            this._reacting = true;
            if (new_plot) {
                const obj = { data, layout: newLayout, config: this.model.config, frames: this.model.frames };
                await window.Plotly.newPlot(this.container, obj);
            }
            else {
                await window.Plotly.react(this.container, data, newLayout, this.model.config);
                if (this.model.frames != null) {
                    await window.Plotly.addFrames(this.container, this.model.frames);
                }
            }
            this._updateSetViewportFunction();
            this._updateViewportProperty();
            if (!this._plotInitialized) {
                this._install_callbacks();
            }
            else if (!_isHidden(this.container)) {
                window.Plotly.Plots.resize(this.container);
            }
            this._reacting = false;
            this._plotInitialized = true;
        }
        _get_trace(index, update) {
            const trace = (0, object_1.clone)(this.model.data[index]);
            const cds = this.model.data_sources[index];
            for (const column of cds.columns()) {
                let array = cds.get_array(column)[0];
                if (array.shape != null && array.shape.length > 1) {
                    array = (0, util_1.reshape)(array, array.shape);
                }
                const prop_path = column.split(".");
                const prop = prop_path[prop_path.length - 1];
                let prop_parent = trace;
                for (const k of prop_path.slice(0, -1)) {
                    prop_parent = (prop_parent[k]);
                }
                if (update && prop_path.length == 1) {
                    prop_parent[prop] = [array];
                }
                else {
                    prop_parent[prop] = array;
                }
            }
            return trace;
        }
        _updateViewportFromProperty() {
            if (!window.Plotly || this._settingViewport || this._reacting || !this.model.viewport) {
                return;
            }
            const fullLayout = this.container._fullLayout;
            // Call relayout if viewport differs from fullLayout
            Object.keys(this.model.viewport).reduce((value, key) => {
                if (!(0, eq_1.is_equal)((0, util_1.get)(fullLayout, key), value)) {
                    const clonedViewport = (0, util_1.deepCopy)(this.model.viewport);
                    clonedViewport._update_from_property = true;
                    this._settingViewport = true;
                    window.Plotly.relayout(this.el, clonedViewport).then(() => {
                        this._settingViewport = false;
                    });
                    return false;
                }
                else {
                    return true;
                }
            }, {});
        }
        _updateViewportProperty() {
            const fullLayout = this.container._fullLayout;
            const viewport = {};
            // Get range for all xaxis and yaxis properties
            for (const prop in fullLayout) {
                if (!fullLayout.hasOwnProperty(prop)) {
                    continue;
                }
                const maybe_axis = prop.slice(0, 5);
                if (maybe_axis === "xaxis" || maybe_axis === "yaxis") {
                    viewport[`${prop}.range`] = (0, util_1.deepCopy)(fullLayout[prop].range);
                }
            }
            if (!(0, eq_1.is_equal)(viewport, this.model.viewport)) {
                this._setViewport(viewport);
            }
        }
        _updateSetViewportFunction() {
            if (this.model.viewport_update_policy === "continuous" ||
                this.model.viewport_update_policy === "mouseup") {
                this._setViewport = (viewport) => {
                    if (!this._settingViewport) {
                        this._settingViewport = true;
                        this.model.viewport = viewport;
                        this._settingViewport = false;
                    }
                };
            }
            else {
                this._setViewport = (0, util_1.throttle)((viewport) => {
                    if (!this._settingViewport) {
                        this._settingViewport = true;
                        this.model.viewport = viewport;
                        this._settingViewport = false;
                    }
                }, this.model.viewport_update_throttle);
            }
        }
    }
    exports.PlotlyPlotView = PlotlyPlotView;
    PlotlyPlotView.__name__ = "PlotlyPlotView";
    class PlotlyPlot extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.PlotlyPlot = PlotlyPlot;
    _a = PlotlyPlot;
    PlotlyPlot.__name__ = "PlotlyPlot";
    PlotlyPlot.__module__ = "panel.models.plotly";
    (() => {
        _a.prototype.default_view = PlotlyPlotView;
        _a.define(({ List, Any, Nullable, Float, Ref, Str }) => ({
            data: [List(Any), []],
            layout: [Any, {}],
            config: [Any, {}],
            frames: [Nullable(List(Any)), null],
            data_sources: [List(Ref(column_data_source_1.ColumnDataSource)), []],
            relayout: [Nullable(Any), {}],
            restyle: [Nullable(Any), {}],
            relayout_data: [Any, {}],
            restyle_data: [List(Any), []],
            click_data: [Any, {}],
            hover_data: [Any, {}],
            clickannotation_data: [Any, {}],
            selected_data: [Any, {}],
            viewport: [Any, {}],
            viewport_update_policy: [Str, "mouseup"],
            viewport_update_throttle: [Float, 200],
            _render_count: [Float, 0],
        }));
    })();
},
"27e2a99e99": /* models/util.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const array_1 = require("@bokehjs/core/util/array");
    const get = (obj, path, defaultValue = undefined) => {
        const travel = (regexp) => String.prototype.split
            .call(path, regexp)
            .filter(Boolean)
            .reduce((res, key) => (res !== null && res !== undefined ? res[key] : res), obj);
        const result = travel(/[,[\]]+?/) || travel(/[,[\].]+?/);
        return result === undefined || result === obj ? defaultValue : result;
    };
    exports.get = get;
    function throttle(func, timeFrame) {
        let lastTime = 0;
        return function () {
            const now = Number(new Date());
            if (now - lastTime >= timeFrame) {
                func();
                lastTime = now;
            }
        };
    }
    exports.throttle = throttle;
    function deepCopy(obj) {
        let copy;
        // Handle the 3 simple types, and null or undefined
        if (null == obj || "object" != typeof obj) {
            return obj;
        }
        // Handle Array
        if (obj instanceof Array) {
            copy = [];
            for (let i = 0, len = obj.length; i < len; i++) {
                copy[i] = deepCopy(obj[i]);
            }
            return copy;
        }
        // Handle Object
        if (obj instanceof Object) {
            const copy = {};
            for (const attr in obj) {
                const key = attr;
                if (obj.hasOwnProperty(key)) {
                    copy[key] = deepCopy(obj[key]);
                }
            }
            return copy;
        }
        throw new Error("Unable to copy obj! Its type isn't supported.");
    }
    exports.deepCopy = deepCopy;
    function reshape(arr, dim) {
        let elemIndex = 0;
        if (!dim || !arr) {
            return [];
        }
        function _nest(dimIndex) {
            let result = [];
            if (dimIndex === dim.length - 1) {
                result = (0, array_1.concat)(arr.slice(elemIndex, elemIndex + dim[dimIndex]));
                elemIndex += dim[dimIndex];
            }
            else {
                for (let i = 0; i < dim[dimIndex]; i++) {
                    result.push(_nest(dimIndex + 1));
                }
            }
            return result;
        }
        return _nest(0);
    }
    exports.reshape = reshape;
},
"ce7c8e2a4f": /* styles/models/plotly.css.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    exports.default = `.js-plotly-plot .plotly,.js-plotly-plot .plotly div{direction:ltr;font-family:'Open Sans', verdana, arial, sans-serif;margin:0;padding:0;}.js-plotly-plot .plotly input,.js-plotly-plot .plotly button{font-family:'Open Sans', verdana, arial, sans-serif;}.js-plotly-plot .plotly input:focus,.js-plotly-plot .plotly button:focus{outline:none;}.js-plotly-plot .plotly a{text-decoration:none;}.js-plotly-plot .plotly a:hover{text-decoration:none;}.js-plotly-plot .plotly .crisp{shape-rendering:crispEdges;}.js-plotly-plot .plotly .user-select-none{-webkit-user-select:none;-moz-user-select:none;-ms-user-select:none;-o-user-select:none;user-select:none;}.js-plotly-plot .plotly svg{overflow:hidden;}.js-plotly-plot .plotly svg a{fill:#447adb;}.js-plotly-plot .plotly svg a:hover{fill:#3c6dc5;}.js-plotly-plot .plotly .main-svg{position:absolute;top:0;left:0;pointer-events:none;}.js-plotly-plot .plotly .main-svg .draglayer{pointer-events:all;}.js-plotly-plot .plotly .cursor-default{cursor:default;}.js-plotly-plot .plotly .cursor-pointer{cursor:pointer;}.js-plotly-plot .plotly .cursor-crosshair{cursor:crosshair;}.js-plotly-plot .plotly .cursor-move{cursor:move;}.js-plotly-plot .plotly .cursor-col-resize{cursor:col-resize;}.js-plotly-plot .plotly .cursor-row-resize{cursor:row-resize;}.js-plotly-plot .plotly .cursor-ns-resize{cursor:ns-resize;}.js-plotly-plot .plotly .cursor-ew-resize{cursor:ew-resize;}.js-plotly-plot .plotly .cursor-sw-resize{cursor:sw-resize;}.js-plotly-plot .plotly .cursor-s-resize{cursor:s-resize;}.js-plotly-plot .plotly .cursor-se-resize{cursor:se-resize;}.js-plotly-plot .plotly .cursor-w-resize{cursor:w-resize;}.js-plotly-plot .plotly .cursor-e-resize{cursor:e-resize;}.js-plotly-plot .plotly .cursor-nw-resize{cursor:nw-resize;}.js-plotly-plot .plotly .cursor-n-resize{cursor:n-resize;}.js-plotly-plot .plotly .cursor-ne-resize{cursor:ne-resize;}.js-plotly-plot .plotly .cursor-grab{cursor:-webkit-grab;cursor:grab;}.js-plotly-plot .plotly .modebar{position:absolute;top:2px;right:2px;}.js-plotly-plot .plotly .ease-bg{-webkit-transition:background-color 0.3s ease 0s;-moz-transition:background-color 0.3s ease 0s;-ms-transition:background-color 0.3s ease 0s;-o-transition:background-color 0.3s ease 0s;transition:background-color 0.3s ease 0s;}.js-plotly-plot .plotly .modebar--hover > :not(.watermark){opacity:0;-webkit-transition:opacity 0.3s ease 0s;-moz-transition:opacity 0.3s ease 0s;-ms-transition:opacity 0.3s ease 0s;-o-transition:opacity 0.3s ease 0s;transition:opacity 0.3s ease 0s;}.js-plotly-plot .plotly:hover .modebar--hover .modebar-group{opacity:1;}.js-plotly-plot .plotly .modebar-group{float:left;display:inline-block;box-sizing:border-box;padding-left:8px;position:relative;vertical-align:middle;white-space:nowrap;}.js-plotly-plot .plotly .modebar-btn{fill:var(--plotly-icon-color);position:relative;font-size:16px;padding:3px 4px;height:22px;cursor:pointer;line-height:normal;box-sizing:border-box;}.js-plotly-plot .plotly .modebar-btn.active{fill:var(--plotly-active-icon-color);}.js-plotly-plot .plotly .modebar-btn svg{position:relative;top:2px;}.js-plotly-plot .plotly .modebar.vertical{display:flex;flex-direction:column;flex-wrap:wrap;align-content:flex-end;max-height:100%;}.js-plotly-plot .plotly .modebar.vertical svg{top:-1px;}.js-plotly-plot .plotly .modebar.vertical .modebar-group{display:block;float:none;padding-left:0px;padding-bottom:8px;}.js-plotly-plot .plotly .modebar.vertical .modebar-group .modebar-btn{display:block;text-align:center;}.js-plotly-plot .plotly [data-title]{}.js-plotly-plot .plotly [data-title]:before,.js-plotly-plot .plotly [data-title]:after{position:absolute;-webkit-transform:translate3d(0, 0, 0);-moz-transform:translate3d(0, 0, 0);-ms-transform:translate3d(0, 0, 0);-o-transform:translate3d(0, 0, 0);transform:translate3d(0, 0, 0);display:none;opacity:0;z-index:1001;pointer-events:none;top:110%;right:50%;}.js-plotly-plot .plotly [data-title]:hover:before,.js-plotly-plot .plotly [data-title]:hover:after{display:block;opacity:1;}.js-plotly-plot .plotly [data-title]:before{content:'';position:absolute;background:transparent;border:6px solid transparent;z-index:1002;margin-top:-12px;border-bottom-color:#69738a;margin-right:-6px;}.js-plotly-plot .plotly [data-title]:after{content:attr(data-title);background:#69738a;color:white;padding:8px 10px;font-size:12px;line-height:12px;white-space:nowrap;margin-right:-18px;border-radius:2px;}.js-plotly-plot .plotly .vertical [data-title]:before,.js-plotly-plot .plotly .vertical [data-title]:after{top:0%;right:200%;}.js-plotly-plot .plotly .vertical [data-title]:before{border:6px solid transparent;border-left-color:#69738a;margin-top:8px;margin-right:-30px;}.plotly-notifier{font-family:'Open Sans', verdana, arial, sans-serif;position:fixed;top:50px;right:20px;z-index:10000;font-size:10pt;max-width:180px;}.plotly-notifier p{margin:0;}.plotly-notifier .notifier-note{min-width:180px;max-width:250px;border:1px solid #fff;z-index:3000;margin:0;background-color:#8c97af;background-color:rgba(140, 151, 175, 0.9);color:#fff;padding:10px;overflow-wrap:break-word;word-wrap:break-word;-ms-hyphens:auto;-webkit-hyphens:auto;hyphens:auto;}.plotly-notifier .notifier-close{color:#fff;opacity:0.8;float:right;padding:0 5px;background:none;border:none;font-size:20px;font-weight:bold;line-height:20px;}.plotly-notifier .notifier-close:hover{color:#444;text-decoration:none;cursor:pointer;}`;
},
"aded75e266": /* models/progress.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const dom_1 = require("@bokehjs/core/dom");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    class ProgressView extends layout_1.HTMLBoxView {
        connect_signals() {
            super.connect_signals();
            const { width, height, height_policy, width_policy, sizing_mode, active, bar_color, css_classes, value, max, } = this.model.properties;
            this.on_change([width, height, height_policy, width_policy, sizing_mode], () => this.render());
            this.on_change([active, bar_color, css_classes], () => this.setCSS());
            this.on_change(value, () => this.setValue());
            this.on_change(max, () => this.setMax());
        }
        render() {
            super.render();
            const style = { ...this.model.styles, display: "inline-block" };
            this.progressEl = document.createElement("progress");
            this.setValue();
            this.setMax();
            // Set styling
            this.setCSS();
            for (const prop in style) {
                this.progressEl.style.setProperty(prop, style[prop]);
            }
            this.shadow_el.appendChild(this.progressEl);
        }
        stylesheets() {
            const styles = super.stylesheets();
            for (const css of this.model.css) {
                styles.push(new dom_1.ImportedStyleSheet(css));
            }
            return styles;
        }
        setCSS() {
            let css = `${this.model.css_classes.join(" ")} ${this.model.bar_color}`;
            if (this.model.active) {
                css = `${css} active`;
            }
            this.progressEl.className = css;
        }
        setValue() {
            if (this.model.value == null) {
                this.progressEl.value = 0;
            }
            else if (this.model.value >= 0) {
                this.progressEl.value = this.model.value;
            }
            else if (this.model.value < 0) {
                this.progressEl.removeAttribute("value");
            }
        }
        setMax() {
            if (this.model.max != null) {
                this.progressEl.max = this.model.max;
            }
        }
    }
    exports.ProgressView = ProgressView;
    ProgressView.__name__ = "ProgressView";
    class Progress extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.Progress = Progress;
    _a = Progress;
    Progress.__name__ = "Progress";
    Progress.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = ProgressView;
        _a.define(({ Any, List, Bool, Float, Str }) => ({
            active: [Bool, true],
            bar_color: [Str, "primary"],
            css: [List(Str), []],
            max: [Float, 100],
            value: [Any, null],
        }));
    })();
},
"c72e00086f": /* models/quill.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const dom_1 = require("@bokehjs/core/dom");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    class QuillInputView extends layout_1.HTMLBoxView {
        connect_signals() {
            super.connect_signals();
            const { disabled, visible, text, mode, toolbar, placeholder } = this.model.properties;
            this.on_change(disabled, () => {
                this.quill.enable(!this.model.disabled);
            });
            this.on_change(visible, () => {
                if (this.model.visible) {
                    this.container.style.visibility = "visible";
                }
            });
            this.on_change(text, () => {
                if (this._editing) {
                    return;
                }
                this._editing = true;
                this.quill.enable(false);
                this.quill.setContents([]);
                this.quill.clipboard.dangerouslyPasteHTML(this.model.text);
                this.quill.enable(!this.model.disabled);
                this._editing = false;
            });
            this.on_change(placeholder, () => {
                this.quill.root.setAttribute("data-placeholder", this.model.placeholder);
            });
            this.on_change([mode, toolbar], () => {
                this.render();
                this._layout_toolbar();
            });
        }
        _layout_toolbar() {
            if (this._toolbar == null) {
                this.el.style.removeProperty("padding-top");
            }
            else {
                const height = this._toolbar.getBoundingClientRect().height + 1;
                this.el.style.paddingTop = `${height}px`;
                this._toolbar.style.marginTop = `${-height}px`;
            }
        }
        render() {
            super.render();
            this.container = (0, dom_1.div)({ style: "visibility: hidden;" });
            this.shadow_el.appendChild(this.container);
            const theme = (this.model.mode === "bubble") ? "bubble" : "snow";
            this.watch_stylesheets();
            this.quill = new window.Quill(this.container, {
                modules: {
                    toolbar: this.model.toolbar,
                },
                readOnly: true,
                placeholder: this.model.placeholder,
                theme,
            });
            // Apply ShadowDOM patch found at:
            // https://github.com/quilljs/quill/issues/2961#issuecomment-1775999845
            const hasShadowRootSelection = !!(document.createElement("div").attachShadow({ mode: "open" }).getSelection);
            // Each browser engine has a different implementation for retrieving the Range
            const getNativeRange = (rootNode) => {
                try {
                    if (hasShadowRootSelection) {
                        // In Chromium, the shadow root has a getSelection function which returns the range
                        return rootNode.getSelection().getRangeAt(0);
                    }
                    else {
                        const selection = window.getSelection();
                        if (selection.getComposedRanges) {
                            // Webkit range retrieval is done with getComposedRanges (see: https://bugs.webkit.org/show_bug.cgi?id=163921)
                            return selection.getComposedRanges(rootNode)[0];
                        }
                        else {
                            // Gecko implements the range API properly in Native Shadow: https://developer.mozilla.org/en-US/docs/Web/API/Selection/getRangeAt
                            return selection.getRangeAt(0);
                        }
                    }
                }
                catch {
                    return null;
                }
            };
            /**
             * Original implementation uses document.active element which does not work in Native Shadow.
             * Replace document.activeElement with shadowRoot.activeElement
             **/
            this.quill.selection.hasFocus = () => {
                const rootNode = this.quill.root.getRootNode();
                return rootNode.activeElement === this.quill.root;
            };
            /**
             * Original implementation uses document.getSelection which does not work in Native Shadow.
             * Replace document.getSelection with shadow dom equivalent (different for each browser)
             **/
            this.quill.selection.getNativeRange = () => {
                const rootNode = this.quill.root.getRootNode();
                const nativeRange = getNativeRange(rootNode);
                return !!nativeRange ? this.quill.selection.normalizeNative(nativeRange) : null;
            };
            /**
             * Original implementation relies on Selection.addRange to programmatically set the range, which does not work
             * in Webkit with Native Shadow. Selection.addRange works fine in Chromium and Gecko.
             **/
            this.quill.selection.setNativeRange = (startNode, startOffset) => {
                let endNode = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : startNode;
                let endOffset = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : startOffset;
                const force = arguments.length > 4 && arguments[4] !== undefined ? arguments[4] : false;
                if (startNode != null && (this.quill.selection.root.parentNode == null || startNode.parentNode == null || endNode.parentNode == null)) {
                    return;
                }
                const selection = document.getSelection();
                if (selection == null) {
                    return;
                }
                if (startNode != null) {
                    if (!this.quill.selection.hasFocus()) {
                        this.quill.selection.root.focus();
                    }
                    const native = (this.quill.selection.getNativeRange() || {}).native;
                    if (native == null || force || startNode !== native.startContainer || startOffset !== native.startOffset || endNode !== native.endContainer || endOffset !== native.endOffset) {
                        if (startNode.tagName == "BR") {
                            startOffset = Array.prototype.indexOf.call(startNode.parentNode?.childNodes ?? [], startNode);
                            startNode = startNode.parentNode;
                        }
                        if (endNode.tagName == "BR") {
                            endOffset = Array.prototype.indexOf(endNode.parentNode?.childNodes ?? [], endNode);
                            endNode = endNode.parentNode;
                        }
                        selection.setBaseAndExtent(startNode, startOffset, endNode, endOffset);
                    }
                }
                else {
                    selection.removeAllRanges();
                    this.quill.selection.root.blur();
                    document.body.focus();
                }
            };
            this._editor = this.shadow_el.querySelector(".ql-editor");
            this._toolbar = this.shadow_el.querySelector(".ql-toolbar");
            const delta = this.quill.clipboard.convert(this.model.text);
            this.quill.setContents(delta);
            this.quill.on("text-change", () => {
                if (this._editing) {
                    return;
                }
                this._editing = true;
                this.model.text = this._editor.innerHTML;
                this._editing = false;
            });
            if (!this.model.disabled) {
                this.quill.enable(!this.model.disabled);
            }
            document.addEventListener("selectionchange", (..._args) => {
                // Update selection and some other properties
                this.quill.selection.update();
            });
        }
        style_redraw() {
            if (this.model.visible) {
                this.container.style.visibility = "visible";
            }
            const delta = this.quill.clipboard.convert(this.model.text);
            this.quill.setContents(delta);
            this.invalidate_layout();
        }
        after_layout() {
            super.after_layout();
            this._layout_toolbar();
        }
    }
    exports.QuillInputView = QuillInputView;
    QuillInputView.__name__ = "QuillInputView";
    class QuillInput extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.QuillInput = QuillInput;
    _a = QuillInput;
    QuillInput.__name__ = "QuillInput";
    QuillInput.__module__ = "panel.models.quill";
    (() => {
        _a.prototype.default_view = QuillInputView;
        _a.define(({ Any, Str }) => ({
            mode: [Str, "toolbar"],
            placeholder: [Str, ""],
            text: [Str, ""],
            toolbar: [Any, null],
        }));
        _a.override({
            height: 300,
        });
    })();
},
"361b5f089c": /* models/radio_button_group.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tooltip_1 = require("@bokehjs/models/ui/tooltip");
    const build_views_1 = require("@bokehjs/core/build_views");
    const radio_button_group_1 = require("@bokehjs/models/widgets/radio_button_group");
    class RadioButtonGroupView extends radio_button_group_1.RadioButtonGroupView {
        *children() {
            yield* super.children();
            if (this.tooltip != null) {
                yield this.tooltip;
            }
        }
        async lazy_initialize() {
            await super.lazy_initialize();
            const { tooltip } = this.model;
            if (tooltip != null) {
                this.tooltip = await (0, build_views_1.build_view)(tooltip, { parent: this });
            }
        }
        remove() {
            this.tooltip?.remove();
            super.remove();
        }
        render() {
            super.render();
            const toggle = (visible) => {
                this.tooltip?.model.setv({
                    visible,
                });
            };
            let timer;
            this.el.addEventListener("mouseenter", () => {
                timer = setTimeout(() => toggle(true), this.model.tooltip_delay);
            });
            this.el.addEventListener("mouseleave", () => {
                clearTimeout(timer);
                toggle(false);
            });
        }
    }
    exports.RadioButtonGroupView = RadioButtonGroupView;
    RadioButtonGroupView.__name__ = "RadioButtonGroupView";
    class RadioButtonGroup extends radio_button_group_1.RadioButtonGroup {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.RadioButtonGroup = RadioButtonGroup;
    _a = RadioButtonGroup;
    RadioButtonGroup.__name__ = "RadioButtonGroup";
    RadioButtonGroup.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = RadioButtonGroupView;
        _a.define(({ Nullable, Ref, Float }) => ({
            tooltip: [Nullable(Ref(tooltip_1.Tooltip)), null],
            tooltip_delay: [Float, 500],
        }));
    })();
},
"6cfc3f348e": /* models/reactive_html.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const preact_1 = require("bfac992a64") /* preact */;
    const hooks_1 = require("d952f1d8b6") /* preact/hooks */;
    const preact_2 = require("b3f51db71c") /* htm/preact */;
    const dom_1 = require("@bokehjs/core/dom");
    const types_1 = require("@bokehjs/core/util/types");
    const data_1 = require("be689f0377") /* ./data */;
    const event_to_object_1 = require("2cc1a33000") /* ./event-to-object */;
    const html_1 = require("89d2d3667a") /* ./html */;
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    function serialize_attrs(attrs) {
        const serialized = {};
        for (const attr in attrs) {
            let value = attrs[attr];
            if (!(0, types_1.isString)(value)) {
            }
            else if (value !== "" && (value === "NaN" || !isNaN(Number(value)))) {
                value = Number(value);
            }
            else if (value === "false" || value === "true") {
                value = value === "true" ? true : false;
            }
            serialized[attr] = value;
        }
        return serialized;
    }
    function escapeRegex(string) {
        return string.replace(/[-\/\\^$*+?.()|[\]]/g, "\\$&");
    }
    function extractToken(template, str, tokens) {
        const tokenMapping = {};
        for (const match of tokens) {
            tokenMapping[`{${match}}`] = "(.*)";
        }
        const tokenList = [];
        let regexpTemplate = `^${escapeRegex(template)}$`;
        // Find the order of the tokens
        let i, tokenIndex, tokenEntry;
        for (const m in tokenMapping) {
            tokenIndex = template.indexOf(m);
            // Token found
            if (tokenIndex > -1) {
                regexpTemplate = regexpTemplate.replace(m, tokenMapping[m]);
                tokenEntry = {
                    index: tokenIndex,
                    token: m,
                };
                for (i = 0; i < tokenList.length && tokenList[i].index < tokenIndex; i++) {
                    ;
                }
                // Insert it at index i
                if (i < tokenList.length) {
                    tokenList.splice(i, 0, tokenEntry);
                }
                else {
                    tokenList.push(tokenEntry);
                }
            }
        }
        regexpTemplate = regexpTemplate.replace(/\{[^{}]+\}/g, ".*");
        const match = new RegExp(regexpTemplate).exec(str);
        let result = null;
        if (match) {
            result = {};
            // Find your token entry
            for (i = 0; i < tokenList.length; i++) {
                result[tokenList[i].token.slice(1, -1)] = match[i + 1];
            }
        }
        return result;
    }
    function element_lookup(root, el_id) {
        let el = root.getElementById(el_id);
        if (el == null) {
            el = document.getElementById(el_id);
        }
        return el;
    }
    class ReactiveHTMLView extends layout_1.HTMLBoxView {
        constructor() {
            super(...arguments);
            this._parent = null;
            this._changing = false;
            this._event_listeners = {};
            this._mutation_observers = [];
            this._script_fns = {};
            this._state = {};
        }
        initialize() {
            super.initialize();
            this.html = (0, html_1.htmlDecode)(this.model.html) || this.model.html;
        }
        _recursive_connect(model, update_children, path) {
            for (const prop in model.properties) {
                let subpath;
                if (path.length) {
                    subpath = `${path}.${prop}`;
                }
                else {
                    subpath = prop;
                }
                const obj = model[prop];
                if (obj == null) {
                    continue;
                }
                if (obj.properties != null) {
                    this._recursive_connect(obj, true, subpath);
                }
                this.on_change(model.properties[prop], () => {
                    if (update_children) {
                        for (const node in this.model.children) {
                            if (this.model.children[node] == prop) {
                                let children = model[prop];
                                if (!(0, types_1.isArray)(children)) {
                                    children = [children];
                                }
                                this._render_node(node, children);
                                return;
                            }
                        }
                    }
                    if (!this._changing) {
                        this._update(subpath);
                    }
                });
            }
        }
        connect_signals() {
            super.connect_signals();
            const { children, events } = this.model.properties;
            this.on_change(children, async () => {
                this.html = (0, html_1.htmlDecode)(this.model.html) || this.model.html;
                await this.build_child_views();
                this.invalidate_render();
            });
            this._recursive_connect(this.model.data, true, "");
            this.on_change(events, () => {
                this._remove_event_listeners();
                this._setup_event_listeners();
            });
            this.connect_scripts();
        }
        connect_scripts() {
            const id = this.model.data.id;
            for (const prop in this.model.scripts) {
                const scripts = this.model.scripts[prop];
                let data_model = this.model.data;
                let attr;
                if (prop.indexOf(".") >= 0) {
                    const path = prop.split(".");
                    attr = path[path.length - 1];
                    for (const p of path.slice(0, -1)) {
                        data_model = data_model[p];
                    }
                }
                else {
                    attr = prop;
                }
                for (const script of scripts) {
                    const decoded_script = (0, html_1.htmlDecode)(script) || script;
                    const script_fn = this._render_script(decoded_script, id);
                    this._script_fns[prop] = script_fn;
                    const property = data_model.properties[attr];
                    if (property == null) {
                        continue;
                    }
                    const is_event_param = this.model.event_params.includes(prop);
                    this.on_change(property, () => {
                        if (!this._changing && !(is_event_param && !data_model[prop])) {
                            this.run_script(prop);
                            if (is_event_param) {
                                data_model.setv({ [prop]: false });
                            }
                        }
                    });
                }
            }
        }
        run_script(property, silent = false) {
            const script_fn = this._script_fns[property];
            if (script_fn === undefined) {
                if (!silent) {
                    console.log(`Script '${property}' could not be found.`);
                }
                return;
            }
            const this_obj = {
                get_records: (property, index) => this.get_records(property, index),
            };
            for (const name in this._script_fns) {
                this_obj[name] = () => this.run_script(name);
            }
            return script_fn(this.model, this.model.data, this._state, this, (s) => this.run_script(s), this_obj);
        }
        get_records(property, index = true) {
            return (0, data_1.dict_to_records)(this.model.data[property], index);
        }
        disconnect_signals() {
            super.disconnect_signals();
            this._remove_event_listeners();
            this._remove_mutation_observers();
        }
        remove() {
            this.run_script("remove", true);
            super.remove();
        }
        get child_models() {
            const models = [];
            for (const parent in this.model.children) {
                for (const model of this.model.children[parent]) {
                    if (!(0, types_1.isString)(model)) {
                        models.push(model);
                    }
                }
            }
            return models;
        }
        _after_layout() {
            this.run_script("after_layout", true);
        }
        render() {
            this.empty();
            this._update_stylesheets();
            this._update_css_classes();
            this._apply_styles();
            this._apply_visible();
            this.container = (0, dom_1.div)({ style: "display: contents;" });
            this.shadow_el.append(this.container);
            this._update();
            this._render_children();
            this._setup_mutation_observers();
            this._setup_event_listeners();
            this.run_script("render", true);
        }
        _send_event(elname, attr, event) {
            const serialized = (0, event_to_object_1.serializeEvent)(event);
            serialized.type = attr;
            for (const key in serialized) {
                if (serialized[key] === undefined) {
                    delete serialized[key];
                }
            }
            this.model.trigger_event(new html_1.DOMEvent(elname, serialized));
        }
        _render_child(model, el) {
            const view = this._child_views.get(model);
            if (view == null) {
                el.innerHTML = (0, html_1.htmlDecode)(model) || model;
            }
            else {
                el.appendChild(view.el);
                view.render();
                view.after_render();
            }
        }
        _render_node(node, children) {
            const id = this.model.data.id;
            if (this.model.looped.indexOf(node) > -1) {
                for (let i = 0; i < children.length; i++) {
                    const el = element_lookup(this.shadow_el, `${node}-${i}-${id}`);
                    if (el == null) {
                        console.warn(`DOM node '${node}-${i}-${id}' could not be found. Cannot render children.`);
                        continue;
                    }
                    this._render_child(children[i], el);
                }
            }
            else {
                const el = element_lookup(this.shadow_el, `${node}-${id}`);
                if (el == null) {
                    console.warn(`DOM node '${node}-${id}' could not be found. Cannot render children.`);
                    return;
                }
                for (const child of children) {
                    this._render_child(child, el);
                }
            }
        }
        _render_children() {
            for (const node in this.model.children) {
                let children = this.model.children[node];
                if ((0, types_1.isString)(children)) {
                    children = this.model.data[children];
                    if (!(0, types_1.isArray)(children)) {
                        children = [children];
                    }
                }
                this._render_node(node, children);
            }
        }
        _render_html(literal, state = {}) {
            let htm = literal.replace(/[`]/g, "\\$&");
            let callbacks = "";
            const methods = [];
            for (const elname in this.model.callbacks) {
                for (const callback of this.model.callbacks[elname]) {
                    const [cb, method] = callback;
                    let definition;
                    htm = htm.replaceAll(`\${${method}}`, `$--{${method}}`);
                    if (method.startsWith("script(")) {
                        const meth = (method
                            .replace("('", "_").replace("')", "")
                            .replace('("', "_").replace('")', "")
                            .replace("-", "_"));
                        const script_name = meth.replaceAll("script_", "");
                        htm = htm.replaceAll(method, meth);
                        definition = `
          const ${meth} = (event) => {
            view._state.event = event
            view.run_script("${script_name}")
            delete view._state.event
          }
          `;
                    }
                    else {
                        definition = `
          const ${method} = (event) => {
            let elname = "${elname}"
            if (RegExp("\{\{.*loop\.index.*\}\}").test(elname)) {
              const pattern = RegExp(elname.replace(/\{\{(.+?)\}\}/g, String.fromCharCode(92) + "d+"))
              for (const p of event.path) {
                if (pattern.exec(p.id) != null) {
                  elname = p.id.split("-").slice(null, -1).join("-")
                  break
                }
              }
            }
            view._send_event(elname, "${cb}", event)
          }
          `;
                    }
                    if (methods.indexOf(method) > -1) {
                        continue;
                    }
                    methods.push(method);
                    callbacks = callbacks + definition;
                }
            }
            htm = (htm
                .replaceAll("${model.", "$-{model.")
                .replaceAll("${", "${data.")
                .replaceAll("$-{model.", "${model.")
                .replaceAll("$--{", "${"));
            return new Function("view, model, data, state, html, useCallback", `${callbacks}return html\`${htm}\`;`)(this, this.model, this.model.data, state, preact_2.html, hooks_1.useCallback);
        }
        _render_script(literal, id) {
            const scripts = [];
            for (const elname of this.model.nodes) {
                const elvar = elname.replace("-", "_");
                if (literal.indexOf(elvar) === -1) {
                    continue;
                }
                const script = `
      let ${elvar} = view.shadow_el.getElementById('${elname}-${id}')
      if (${elvar} == null)
        ${elvar} = document.getElementById('${elname}-${id}')
      if (${elvar} == null) {
        console.warn("DOM node '${elname}' could not be found. Cannot execute callback.")
        return
      }
      `;
                scripts.push(script);
            }
            const event = `
    let event = null
    if (state.event !== undefined) {
      event = state.event
    }
    `;
            scripts.push(event);
            scripts.push(literal);
            return new Function("model, data, state, view, script, self", scripts.join("\n"));
        }
        _remove_mutation_observers() {
            for (const observer of this._mutation_observers) {
                observer.disconnect();
            }
            this._mutation_observers = [];
        }
        _setup_mutation_observers() {
            const id = this.model.data.id;
            for (const name in this.model.attrs) {
                const el = element_lookup(this.shadow_el, `${name}-${id}`);
                if (el == null) {
                    console.warn(`DOM node '${name}-${id}' could not be found. Cannot set up MutationObserver.`);
                    continue;
                }
                const observer = new MutationObserver(() => {
                    this._update_model(el, name);
                });
                observer.observe(el, { attributes: true });
                this._mutation_observers.push(observer);
            }
        }
        _remove_event_listeners() {
            const id = this.model.data.id;
            for (const node in this._event_listeners) {
                const el = element_lookup(this.shadow_el, `${node}-${id}`);
                if (el == null) {
                    continue;
                }
                for (const event_name in this._event_listeners[node]) {
                    const event_callback = this._event_listeners[node][event_name];
                    el.removeEventListener(event_name, event_callback);
                }
            }
            this._event_listeners = {};
        }
        _setup_event_listeners() {
            const id = this.model.data.id;
            for (const node in this.model.events) {
                const el = element_lookup(this.shadow_el, `${node}-${id}`);
                if (el == null) {
                    console.warn(`DOM node '${node}-${id}' could not be found. Cannot subscribe to DOM events.`);
                    continue;
                }
                const node_events = this.model.events[node];
                for (const event_name in node_events) {
                    const event_callback = (event) => {
                        this._send_event(node, event_name, event);
                        if (node in this.model.attrs && node_events[event_name]) {
                            this._update_model(el, node);
                        }
                    };
                    el.addEventListener(event_name, event_callback);
                    if (!(node in this._event_listeners)) {
                        this._event_listeners[node] = {};
                    }
                    this._event_listeners[node][event_name] = event_callback;
                }
            }
        }
        _update(property = null) {
            if (property == null || (this.html.indexOf(`\${${property}}`) > -1)) {
                const rendered = this._render_html(this.html);
                if (rendered == null) {
                    return;
                }
                try {
                    this._changing = true;
                    (0, preact_1.render)(rendered, this.container);
                }
                finally {
                    this._changing = false;
                }
            }
        }
        _update_model(el, name) {
            if (this._changing) {
                return;
            }
            const attrs = {};
            for (const attr_info of this.model.attrs[name]) {
                const [attr, tokens, template] = attr_info;
                let value = attr === "children" ? el.innerHTML : el[attr];
                if (tokens.length === 1 && (`{${tokens[0]}}` === template)) {
                    attrs[tokens[0]] = value;
                }
                else if ((0, types_1.isString)(value)) {
                    value = extractToken(template, value, tokens);
                    if (value == null) {
                        console.warn(`Could not resolve parameters in ${name} element ${attr} attribute value ${value}.`);
                    }
                    else {
                        for (const param in value) {
                            if (value[param] === undefined) {
                                console.warn(`Could not resolve ${param} in ${name} element ${attr} attribute value ${value}.`);
                            }
                            else {
                                attrs[param] = value[param];
                            }
                        }
                    }
                }
            }
            try {
                this._changing = true;
                this.model.data.setv(serialize_attrs(attrs));
            }
            catch {
                console.log("Could not serialize", attrs);
            }
            finally {
                this._changing = false;
            }
        }
    }
    exports.ReactiveHTMLView = ReactiveHTMLView;
    ReactiveHTMLView.__name__ = "ReactiveHTMLView";
    class ReactiveHTML extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.ReactiveHTML = ReactiveHTML;
    _a = ReactiveHTML;
    ReactiveHTML.__name__ = "ReactiveHTML";
    ReactiveHTML.__module__ = "panel.models.reactive_html";
    (() => {
        _a.prototype.default_view = ReactiveHTMLView;
        _a.define(({ List, Any, Str }) => ({
            attrs: [Any, {}],
            callbacks: [Any, {}],
            children: [Any, {}],
            data: [Any],
            event_params: [List(Str), []],
            events: [Any, {}],
            html: [Str, ""],
            looped: [List(Str), []],
            nodes: [List(Str), []],
            scripts: [Any, {}],
        }));
    })();
},
"bfac992a64": /* preact/dist/preact.module.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    var n, l, u, t, i, o, r, f, e, c = {}, s = [], a = /acit|ex(?:s|g|n|p|$)|rph|grid|ows|mnc|ntw|ine[ch]|zoo|^ord|itera/i, h = Array.isArray;
    function v(n, l) {
        for (var u in l)
            n[u] = l[u];
        return n;
    }
    function p(n) { var l = n.parentNode; l && l.removeChild(n); }
    function y(l, u, t) {
        var i, o, r, f = {};
        for (r in u)
            "key" == r ? i = u[r] : "ref" == r ? o = u[r] : f[r] = u[r];
        if (arguments.length > 2 && (f.children = arguments.length > 3 ? n.call(arguments, 2) : t), "function" == typeof l && null != l.defaultProps)
            for (r in l.defaultProps)
                void 0 === f[r] && (f[r] = l.defaultProps[r]);
        return d(l, f, i, o, null);
    }
    exports.createElement = y;
    exports.h = y;
    function d(n, t, i, o, r) { var f = { type: n, props: t, key: i, ref: o, __k: null, __: null, __b: 0, __e: null, __d: void 0, __c: null, constructor: void 0, __v: null == r ? ++u : r, __i: -1, __u: 0 }; return null == r && null != l.vnode && l.vnode(f), f; }
    function _() { return { current: null }; }
    exports.createRef = _;
    function g(n) { return n.children; }
    exports.Fragment = g;
    function b(n, l) { this.props = n, this.context = l; }
    exports.Component = b;
    function m(n, l) {
        if (null == l)
            return n.__ ? m(n.__, n.__i + 1) : null;
        for (var u; l < n.__k.length; l++)
            if (null != (u = n.__k[l]) && null != u.__e)
                return u.__e;
        return "function" == typeof n.type ? m(n) : null;
    }
    function k(n) {
        var l, u;
        if (null != (n = n.__) && null != n.__c) {
            for (n.__e = n.__c.base = null, l = 0; l < n.__k.length; l++)
                if (null != (u = n.__k[l]) && null != u.__e) {
                    n.__e = n.__c.base = u.__e;
                    break;
                }
            return k(n);
        }
    }
    function w(n) { (!n.__d && (n.__d = !0) && i.push(n) && !x.__r++ || o !== l.debounceRendering) && ((o = l.debounceRendering) || r)(x); }
    function x() {
        var n, u, t, o, r, e, c, s, a;
        for (i.sort(f); n = i.shift();)
            n.__d && (u = i.length, o = void 0, e = (r = (t = n).__v).__e, s = [], a = [], (c = t.__P) && ((o = v({}, r)).__v = r.__v + 1, l.vnode && l.vnode(o), L(c, o, r, t.__n, void 0 !== c.ownerSVGElement, 32 & r.__u ? [e] : null, s, null == e ? m(r) : e, !!(32 & r.__u), a), o.__.__k[o.__i] = o, M(s, o, a), o.__e != e && k(o)), i.length > u && i.sort(f));
        x.__r = 0;
    }
    function C(n, l, u, t, i, o, r, f, e, a, h) {
        var v, p, y, d, _, g = t && t.__k || s, b = l.length;
        for (u.__d = e, P(u, l, g), e = u.__d, v = 0; v < b; v++)
            null != (y = u.__k[v]) && "boolean" != typeof y && "function" != typeof y && (p = -1 === y.__i ? c : g[y.__i] || c, y.__i = v, L(n, y, p, i, o, r, f, e, a, h), d = y.__e, y.ref && p.ref != y.ref && (p.ref && z(p.ref, null, y), h.push(y.ref, y.__c || d, y)), null == _ && null != d && (_ = d), 65536 & y.__u || p.__k === y.__k ? e = S(y, e, n) : "function" == typeof y.type && void 0 !== y.__d ? e = y.__d : d && (e = d.nextSibling), y.__d = void 0, y.__u &= -196609);
        u.__d = e, u.__e = _;
    }
    function P(n, l, u) {
        var t, i, o, r, f, e = l.length, c = u.length, s = c, a = 0;
        for (n.__k = [], t = 0; t < e; t++)
            null != (i = n.__k[t] = null == (i = l[t]) || "boolean" == typeof i || "function" == typeof i ? null : "string" == typeof i || "number" == typeof i || "bigint" == typeof i || i.constructor == String ? d(null, i, null, null, i) : h(i) ? d(g, { children: i }, null, null, null) : void 0 === i.constructor && i.__b > 0 ? d(i.type, i.props, i.key, i.ref ? i.ref : null, i.__v) : i) ? (i.__ = n, i.__b = n.__b + 1, f = H(i, u, r = t + a, s), i.__i = f, o = null, -1 !== f && (s--, (o = u[f]) && (o.__u |= 131072)), null == o || null === o.__v ? (-1 == f && a--, "function" != typeof i.type && (i.__u |= 65536)) : f !== r && (f === r + 1 ? a++ : f > r ? s > e - r ? a += f - r : a-- : a = f < r && f == r - 1 ? f - r : 0, f !== t + a && (i.__u |= 65536))) : (o = u[t]) && null == o.key && o.__e && (o.__e == n.__d && (n.__d = m(o)), N(o, o, !1), u[t] = null, s--);
        if (s)
            for (t = 0; t < c; t++)
                null != (o = u[t]) && 0 == (131072 & o.__u) && (o.__e == n.__d && (n.__d = m(o)), N(o, o));
    }
    function S(n, l, u) {
        var t, i;
        if ("function" == typeof n.type) {
            for (t = n.__k, i = 0; t && i < t.length; i++)
                t[i] && (t[i].__ = n, l = S(t[i], l, u));
            return l;
        }
        return n.__e != l && (u.insertBefore(n.__e, l || null), l = n.__e), l && l.nextSibling;
    }
    function $(n, l) { return l = l || [], null == n || "boolean" == typeof n || (h(n) ? n.some(function (n) { $(n, l); }) : l.push(n)), l; }
    exports.toChildArray = $;
    function H(n, l, u, t) {
        var i = n.key, o = n.type, r = u - 1, f = u + 1, e = l[u];
        if (null === e || e && i == e.key && o === e.type)
            return u;
        if (t > (null != e && 0 == (131072 & e.__u) ? 1 : 0))
            for (; r >= 0 || f < l.length;) {
                if (r >= 0) {
                    if ((e = l[r]) && 0 == (131072 & e.__u) && i == e.key && o === e.type)
                        return r;
                    r--;
                }
                if (f < l.length) {
                    if ((e = l[f]) && 0 == (131072 & e.__u) && i == e.key && o === e.type)
                        return f;
                    f++;
                }
            }
        return -1;
    }
    function I(n, l, u) { "-" === l[0] ? n.setProperty(l, null == u ? "" : u) : n[l] = null == u ? "" : "number" != typeof u || a.test(l) ? u : u + "px"; }
    function T(n, l, u, t, i) {
        var o;
        n: if ("style" === l)
            if ("string" == typeof u)
                n.style.cssText = u;
            else {
                if ("string" == typeof t && (n.style.cssText = t = ""), t)
                    for (l in t)
                        u && l in u || I(n.style, l, "");
                if (u)
                    for (l in u)
                        t && u[l] === t[l] || I(n.style, l, u[l]);
            }
        else if ("o" === l[0] && "n" === l[1])
            o = l !== (l = l.replace(/(PointerCapture)$|Capture$/, "$1")), l = l.toLowerCase() in n ? l.toLowerCase().slice(2) : l.slice(2), n.l || (n.l = {}), n.l[l + o] = u, u ? t ? u.u = t.u : (u.u = Date.now(), n.addEventListener(l, o ? D : A, o)) : n.removeEventListener(l, o ? D : A, o);
        else {
            if (i)
                l = l.replace(/xlink(H|:h)/, "h").replace(/sName$/, "s");
            else if ("width" !== l && "height" !== l && "href" !== l && "list" !== l && "form" !== l && "tabIndex" !== l && "download" !== l && "rowSpan" !== l && "colSpan" !== l && "role" !== l && l in n)
                try {
                    n[l] = null == u ? "" : u;
                    break n;
                }
                catch (n) { }
            "function" == typeof u || (null == u || !1 === u && "-" !== l[4] ? n.removeAttribute(l) : n.setAttribute(l, u));
        }
    }
    function A(n) {
        var u = this.l[n.type + !1];
        if (n.t) {
            if (n.t <= u.u)
                return;
        }
        else
            n.t = Date.now();
        return u(l.event ? l.event(n) : n);
    }
    function D(n) { return this.l[n.type + !0](l.event ? l.event(n) : n); }
    function L(n, u, t, i, o, r, f, e, c, s) {
        var a, p, y, d, _, m, k, w, x, P, S, $, H, I, T, A = u.type;
        if (void 0 !== u.constructor)
            return null;
        128 & t.__u && (c = !!(32 & t.__u), r = [e = u.__e = t.__e]), (a = l.__b) && a(u);
        n: if ("function" == typeof A)
            try {
                if (w = u.props, x = (a = A.contextType) && i[a.__c], P = a ? x ? x.props.value : a.__ : i, t.__c ? k = (p = u.__c = t.__c).__ = p.__E : ("prototype" in A && A.prototype.render ? u.__c = p = new A(w, P) : (u.__c = p = new b(w, P), p.constructor = A, p.render = O), x && x.sub(p), p.props = w, p.state || (p.state = {}), p.context = P, p.__n = i, y = p.__d = !0, p.__h = [], p._sb = []), null == p.__s && (p.__s = p.state), null != A.getDerivedStateFromProps && (p.__s == p.state && (p.__s = v({}, p.__s)), v(p.__s, A.getDerivedStateFromProps(w, p.__s))), d = p.props, _ = p.state, p.__v = u, y)
                    null == A.getDerivedStateFromProps && null != p.componentWillMount && p.componentWillMount(), null != p.componentDidMount && p.__h.push(p.componentDidMount);
                else {
                    if (null == A.getDerivedStateFromProps && w !== d && null != p.componentWillReceiveProps && p.componentWillReceiveProps(w, P), !p.__e && (null != p.shouldComponentUpdate && !1 === p.shouldComponentUpdate(w, p.__s, P) || u.__v === t.__v)) {
                        for (u.__v !== t.__v && (p.props = w, p.state = p.__s, p.__d = !1), u.__e = t.__e, u.__k = t.__k, u.__k.forEach(function (n) { n && (n.__ = u); }), S = 0; S < p._sb.length; S++)
                            p.__h.push(p._sb[S]);
                        p._sb = [], p.__h.length && f.push(p);
                        break n;
                    }
                    null != p.componentWillUpdate && p.componentWillUpdate(w, p.__s, P), null != p.componentDidUpdate && p.__h.push(function () { p.componentDidUpdate(d, _, m); });
                }
                if (p.context = P, p.props = w, p.__P = n, p.__e = !1, $ = l.__r, H = 0, "prototype" in A && A.prototype.render) {
                    for (p.state = p.__s, p.__d = !1, $ && $(u), a = p.render(p.props, p.state, p.context), I = 0; I < p._sb.length; I++)
                        p.__h.push(p._sb[I]);
                    p._sb = [];
                }
                else
                    do {
                        p.__d = !1, $ && $(u), a = p.render(p.props, p.state, p.context), p.state = p.__s;
                    } while (p.__d && ++H < 25);
                p.state = p.__s, null != p.getChildContext && (i = v(v({}, i), p.getChildContext())), y || null == p.getSnapshotBeforeUpdate || (m = p.getSnapshotBeforeUpdate(d, _)), C(n, h(T = null != a && a.type === g && null == a.key ? a.props.children : a) ? T : [T], u, t, i, o, r, f, e, c, s), p.base = u.__e, u.__u &= -161, p.__h.length && f.push(p), k && (p.__E = p.__ = null);
            }
            catch (n) {
                u.__v = null, c || null != r ? (u.__e = e, u.__u |= c ? 160 : 32, r[r.indexOf(e)] = null) : (u.__e = t.__e, u.__k = t.__k), l.__e(n, u, t);
            }
        else
            null == r && u.__v === t.__v ? (u.__k = t.__k, u.__e = t.__e) : u.__e = j(t.__e, u, t, i, o, r, f, c, s);
        (a = l.diffed) && a(u);
    }
    function M(n, u, t) {
        u.__d = void 0;
        for (var i = 0; i < t.length; i++)
            z(t[i], t[++i], t[++i]);
        l.__c && l.__c(u, n), n.some(function (u) {
            try {
                n = u.__h, u.__h = [], n.some(function (n) { n.call(u); });
            }
            catch (n) {
                l.__e(n, u.__v);
            }
        });
    }
    function j(l, u, t, i, o, r, f, e, s) {
        var a, v, y, d, _, g, b, k = t.props, w = u.props, x = u.type;
        if ("svg" === x && (o = !0), null != r)
            for (a = 0; a < r.length; a++)
                if ((_ = r[a]) && "setAttribute" in _ == !!x && (x ? _.localName === x : 3 === _.nodeType)) {
                    l = _, r[a] = null;
                    break;
                }
        if (null == l) {
            if (null === x)
                return document.createTextNode(w);
            l = o ? document.createElementNS("http://www.w3.org/2000/svg", x) : document.createElement(x, w.is && w), r = null, e = !1;
        }
        if (null === x)
            k === w || e && l.data === w || (l.data = w);
        else {
            if (r = r && n.call(l.childNodes), k = t.props || c, !e && null != r)
                for (k = {}, a = 0; a < l.attributes.length; a++)
                    k[(_ = l.attributes[a]).name] = _.value;
            for (a in k)
                _ = k[a], "children" == a || ("dangerouslySetInnerHTML" == a ? y = _ : "key" === a || a in w || T(l, a, null, _, o));
            for (a in w)
                _ = w[a], "children" == a ? d = _ : "dangerouslySetInnerHTML" == a ? v = _ : "value" == a ? g = _ : "checked" == a ? b = _ : "key" === a || e && "function" != typeof _ || k[a] === _ || T(l, a, _, k[a], o);
            if (v)
                e || y && (v.__html === y.__html || v.__html === l.innerHTML) || (l.innerHTML = v.__html), u.__k = [];
            else if (y && (l.innerHTML = ""), C(l, h(d) ? d : [d], u, t, i, o && "foreignObject" !== x, r, f, r ? r[0] : t.__k && m(t, 0), e, s), null != r)
                for (a = r.length; a--;)
                    null != r[a] && p(r[a]);
            e || (a = "value", void 0 !== g && (g !== l[a] || "progress" === x && !g || "option" === x && g !== k[a]) && T(l, a, g, k[a], !1), a = "checked", void 0 !== b && b !== l[a] && T(l, a, b, k[a], !1));
        }
        return l;
    }
    function z(n, u, t) {
        try {
            "function" == typeof n ? n(u) : n.current = u;
        }
        catch (n) {
            l.__e(n, t);
        }
    }
    function N(n, u, t) {
        var i, o;
        if (l.unmount && l.unmount(n), (i = n.ref) && (i.current && i.current !== n.__e || z(i, null, u)), null != (i = n.__c)) {
            if (i.componentWillUnmount)
                try {
                    i.componentWillUnmount();
                }
                catch (n) {
                    l.__e(n, u);
                }
            i.base = i.__P = null, n.__c = void 0;
        }
        if (i = n.__k)
            for (o = 0; o < i.length; o++)
                i[o] && N(i[o], u, t || "function" != typeof n.type);
        t || null == n.__e || p(n.__e), n.__ = n.__e = n.__d = void 0;
    }
    function O(n, l, u) { return this.constructor(n, u); }
    function q(u, t, i) { var o, r, f, e; l.__ && l.__(u, t), r = (o = "function" == typeof i) ? null : i && i.__k || t.__k, f = [], e = [], L(t, u = (!o && i || t).__k = y(g, null, [u]), r || c, c, void 0 !== t.ownerSVGElement, !o && i ? [i] : r ? null : t.firstChild ? n.call(t.childNodes) : null, f, !o && i ? i : r ? r.__e : t.firstChild, o, e), M(f, u, e); }
    exports.render = q;
    function B(n, l) { q(n, l, B); }
    exports.hydrate = B;
    function E(l, u, t) {
        var i, o, r, f, e = v({}, l.props);
        for (r in l.type && l.type.defaultProps && (f = l.type.defaultProps), u)
            "key" == r ? i = u[r] : "ref" == r ? o = u[r] : e[r] = void 0 === u[r] && void 0 !== f ? f[r] : u[r];
        return arguments.length > 2 && (e.children = arguments.length > 3 ? n.call(arguments, 2) : t), d(l.type, e, i || l.key, o || l.ref, null);
    }
    exports.cloneElement = E;
    function F(n, l) { var u = { __c: l = "__cC" + e++, __: n, Consumer: function (n, l) { return n.children(l); }, Provider: function (n) { var u, t; return this.getChildContext || (u = [], (t = {})[l] = this, this.getChildContext = function () { return t; }, this.shouldComponentUpdate = function (n) { this.props.value !== n.value && u.some(function (n) { n.__e = !0, w(n); }); }, this.sub = function (n) { u.push(n); var l = n.componentWillUnmount; n.componentWillUnmount = function () { u.splice(u.indexOf(n), 1), l && l.call(n); }; }), n.children; } }; return u.Provider.__ = u.Consumer.contextType = u; }
    exports.createContext = F;
    n = s.slice, exports.options = l = { __e: function (n, l, u, t) {
            for (var i, o, r; l = l.__;)
                if ((i = l.__c) && !i.__)
                    try {
                        if ((o = i.constructor) && null != o.getDerivedStateFromError && (i.setState(o.getDerivedStateFromError(n)), r = i.__d), null != i.componentDidCatch && (i.componentDidCatch(n, t || {}), r = i.__d), r)
                            return i.__E = i;
                    }
                    catch (l) {
                        n = l;
                    }
            throw n;
        } }, u = 0, exports.isValidElement = t = function (n) { return null != n && null == n.constructor; }, b.prototype.setState = function (n, l) { var u; u = null != this.__s && this.__s !== this.state ? this.__s : this.__s = v({}, this.state), "function" == typeof n && (n = n(v({}, u), this.props)), n && v(u, n), null != n && this.__v && (l && this._sb.push(l), w(this)); }, b.prototype.forceUpdate = function (n) { this.__v && (this.__e = !0, n && this.__h.push(n), w(this)); }, b.prototype.render = g, i = [], r = "function" == typeof Promise ? Promise.prototype.then.bind(Promise.resolve()) : setTimeout, f = function (n, l) { return n.__v.__b - l.__v.__b; }, x.__r = 0, e = 0;
},
"d952f1d8b6": /* preact/hooks/dist/hooks.module.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const preact_1 = require("bfac992a64") /* preact */;
    var t, r, u, i, o = 0, f = [], c = [], e = preact_1.options.__b, a = preact_1.options.__r, v = preact_1.options.diffed, l = preact_1.options.__c, m = preact_1.options.unmount;
    function d(t, u) { preact_1.options.__h && preact_1.options.__h(r, t, o || u), o = 0; var i = r.__H || (r.__H = { __: [], __h: [] }); return t >= i.__.length && i.__.push({ __V: c }), i.__[t]; }
    function h(n) { return o = 1, s(B, n); }
    exports.useState = h;
    function s(n, u, i) {
        var o = d(t++, 2);
        if (o.t = n, !o.__c && (o.__ = [i ? i(u) : B(void 0, u), function (n) { var t = o.__N ? o.__N[0] : o.__[0], r = o.t(t, n); t !== r && (o.__N = [r, o.__[1]], o.__c.setState({})); }], o.__c = r, !r.u)) {
            var f = function (n, t, r) {
                if (!o.__c.__H)
                    return !0;
                var u = o.__c.__H.__.filter(function (n) { return n.__c; });
                if (u.every(function (n) { return !n.__N; }))
                    return !c || c.call(this, n, t, r);
                var i = !1;
                return u.forEach(function (n) {
                    if (n.__N) {
                        var t = n.__[0];
                        n.__ = n.__N, n.__N = void 0, t !== n.__[0] && (i = !0);
                    }
                }), !(!i && o.__c.props === n) && (!c || c.call(this, n, t, r));
            };
            r.u = !0;
            var c = r.shouldComponentUpdate, e = r.componentWillUpdate;
            r.componentWillUpdate = function (n, t, r) {
                if (this.__e) {
                    var u = c;
                    c = void 0, f(n, t, r), c = u;
                }
                e && e.call(this, n, t, r);
            }, r.shouldComponentUpdate = f;
        }
        return o.__N || o.__;
    }
    exports.useReducer = s;
    function p(u, i) { var o = d(t++, 3); !preact_1.options.__s && z(o.__H, i) && (o.__ = u, o.i = i, r.__H.__h.push(o)); }
    exports.useEffect = p;
    function y(u, i) { var o = d(t++, 4); !preact_1.options.__s && z(o.__H, i) && (o.__ = u, o.i = i, r.__h.push(o)); }
    exports.useLayoutEffect = y;
    function _(n) { return o = 5, F(function () { return { current: n }; }, []); }
    exports.useRef = _;
    function A(n, t, r) { o = 6, y(function () { return "function" == typeof n ? (n(t()), function () { return n(null); }) : n ? (n.current = t(), function () { return n.current = null; }) : void 0; }, null == r ? r : r.concat(n)); }
    exports.useImperativeHandle = A;
    function F(n, r) { var u = d(t++, 7); return z(u.__H, r) ? (u.__V = n(), u.i = r, u.__h = n, u.__V) : u.__; }
    exports.useMemo = F;
    function T(n, t) { return o = 8, F(function () { return n; }, t); }
    exports.useCallback = T;
    function q(n) { var u = r.context[n.__c], i = d(t++, 9); return i.c = n, u ? (null == i.__ && (i.__ = !0, u.sub(r)), u.props.value) : n.__; }
    exports.useContext = q;
    function x(t, r) { preact_1.options.useDebugValue && preact_1.options.useDebugValue(r ? r(t) : t); }
    exports.useDebugValue = x;
    function P(n) { var u = d(t++, 10), i = h(); return u.__ = n, r.componentDidCatch || (r.componentDidCatch = function (n, t) { u.__ && u.__(n, t), i[1](n); }), [i[0], function () { i[1](void 0); }]; }
    exports.useErrorBoundary = P;
    function V() {
        var n = d(t++, 11);
        if (!n.__) {
            for (var u = r.__v; null !== u && !u.__m && null !== u.__;)
                u = u.__;
            var i = u.__m || (u.__m = [0, 0]);
            n.__ = "P" + i[0] + "-" + i[1]++;
        }
        return n.__;
    }
    exports.useId = V;
    function b() {
        for (var t; t = f.shift();)
            if (t.__P && t.__H)
                try {
                    t.__H.__h.forEach(k), t.__H.__h.forEach(w), t.__H.__h = [];
                }
                catch (r) {
                    t.__H.__h = [], preact_1.options.__e(r, t.__v);
                }
    }
    preact_1.options.__b = function (n) { r = null, e && e(n); }, preact_1.options.__r = function (n) { a && a(n), t = 0; var i = (r = n.__c).__H; i && (u === r ? (i.__h = [], r.__h = [], i.__.forEach(function (n) { n.__N && (n.__ = n.__N), n.__V = c, n.__N = n.i = void 0; })) : (i.__h.forEach(k), i.__h.forEach(w), i.__h = [], t = 0)), u = r; }, preact_1.options.diffed = function (t) { v && v(t); var o = t.__c; o && o.__H && (o.__H.__h.length && (1 !== f.push(o) && i === preact_1.options.requestAnimationFrame || ((i = preact_1.options.requestAnimationFrame) || j)(b)), o.__H.__.forEach(function (n) { n.i && (n.__H = n.i), n.__V !== c && (n.__ = n.__V), n.i = void 0, n.__V = c; })), u = r = null; }, preact_1.options.__c = function (t, r) {
        r.some(function (t) {
            try {
                t.__h.forEach(k), t.__h = t.__h.filter(function (n) { return !n.__ || w(n); });
            }
            catch (u) {
                r.some(function (n) { n.__h && (n.__h = []); }), r = [], preact_1.options.__e(u, t.__v);
            }
        }), l && l(t, r);
    }, preact_1.options.unmount = function (t) {
        m && m(t);
        var r, u = t.__c;
        u && u.__H && (u.__H.__.forEach(function (n) {
            try {
                k(n);
            }
            catch (n) {
                r = n;
            }
        }), u.__H = void 0, r && preact_1.options.__e(r, u.__v));
    };
    var g = "function" == typeof requestAnimationFrame;
    function j(n) { var t, r = function () { clearTimeout(u), g && cancelAnimationFrame(t), setTimeout(n); }, u = setTimeout(r, 100); g && (t = requestAnimationFrame(r)); }
    function k(n) { var t = r, u = n.__c; "function" == typeof u && (n.__c = void 0, u()), r = t; }
    function w(n) { var t = r; n.__c = n.__(), r = t; }
    function z(n, t) { return !n || n.length !== t.length || t.some(function (t, r) { return t !== n[r]; }); }
    function B(n, t) { return "function" == typeof t ? t(n) : t; }
},
"b3f51db71c": /* htm/preact/index.module.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const preact_1 = require("bfac992a64") /* preact */;
    var preact_2 = require("bfac992a64") /* preact */;
    __esExport("h", preact_2.h);
    __esExport("render", preact_2.render);
    __esExport("Component", preact_2.Component);
    const htm_1 = tslib_1.__importDefault(require("ab33dd3f38") /* htm */);
    var m = htm_1.default.bind(preact_1.h);
    exports.html = m;
},
"ab33dd3f38": /* htm/dist/htm.module.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    var n = function (t, s, r, e) {
        var u;
        s[0] = 0;
        for (var h = 1; h < s.length; h++) {
            var p = s[h++], a = s[h] ? (s[0] |= p ? 1 : 2, r[s[h++]]) : s[++h];
            3 === p ? e[0] = a : 4 === p ? e[1] = Object.assign(e[1] || {}, a) : 5 === p ? (e[1] = e[1] || {})[s[++h]] = a : 6 === p ? e[1][s[++h]] += a + "" : p ? (u = t.apply(a, n(t, a, r, ["", null])), e.push(u), a[0] ? s[0] |= 2 : (s[h - 2] = 0, s[h] = u)) : e.push(a);
        }
        return e;
    }, t = new Map;
    function default_1(s) {
        var r = t.get(this);
        return r || (r = new Map, t.set(this, r)), (r = n(this, r.get(s) || (r.set(s, r = function (n) {
            for (var t, s, r = 1, e = "", u = "", h = [0], p = function (n) { 1 === r && (n || (e = e.replace(/^\s*\n\s*|\s*\n\s*$/g, ""))) ? h.push(0, n, e) : 3 === r && (n || e) ? (h.push(3, n, e), r = 2) : 2 === r && "..." === e && n ? h.push(4, n, 0) : 2 === r && e && !n ? h.push(5, 0, !0, e) : r >= 5 && ((e || !n && 5 === r) && (h.push(r, 0, e, s), r = 6), n && (h.push(r, n, 0, s), r = 6)), e = ""; }, a = 0; a < n.length; a++) {
                a && (1 === r && p(), p(a));
                for (var l = 0; l < n[a].length; l++)
                    t = n[a][l], 1 === r ? "<" === t ? (p(), h = [h], r = 3) : e += t : 4 === r ? "--" === e && ">" === t ? (r = 1, e = "") : e = t + e[0] : u ? t === u ? u = "" : e += t : '"' === t || "'" === t ? u = t : ">" === t ? (p(), r = 1) : r && ("=" === t ? (r = 5, s = e, e = "") : "/" === t && (r < 5 || ">" === n[a][l + 1]) ? (p(), 3 === r && (h = h[0]), r = h, (h = h[0]).push(2, 0, r), r = 0) : " " === t || "\t" === t || "\n" === t || "\r" === t ? (p(), r = 2) : e += t), 3 === r && "!--" === e && (r = 4, h = h[0]);
            }
            return p(), h;
        }(s)), r), arguments, [])).length > 1 ? r : r[0];
    }
    exports.default = default_1;
},
"168c4d0ebd": /* models/singleselect.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tslib_1 = require("tslib");
    const dom_1 = require("@bokehjs/core/dom");
    const types_1 = require("@bokehjs/core/util/types");
    const input_widget_1 = require("@bokehjs/models/widgets/input_widget");
    const inputs = tslib_1.__importStar(require("@bokehjs/styles/widgets/inputs.css"));
    class SingleSelectView extends input_widget_1.InputWidgetView {
        connect_signals() {
            super.connect_signals();
            const { value, options, disabled_options, size, disabled } = this.model.properties;
            this.on_change(value, () => this.render_selection());
            this.on_change(options, () => this.render());
            this.on_change(disabled_options, () => this.render());
            this.on_change(size, () => this.render());
            this.on_change(disabled, () => this.render());
        }
        render() {
            super.render();
            this.render_selection();
        }
        _render_input() {
            const options = this.model.options.map((opt) => {
                let value, _label;
                if ((0, types_1.isString)(opt)) {
                    value = _label = opt;
                }
                else {
                    [value, _label] = opt;
                }
                const disabled = this.model.disabled_options.includes(value);
                return (0, dom_1.option)({ value, disabled }, _label);
            });
            this.input_el = (0, dom_1.select)({
                multiple: false,
                class: inputs.input,
                name: this.model.name,
                disabled: this.model.disabled,
            }, options);
            this.input_el.style.backgroundImage = "none";
            this.input_el.addEventListener("change", () => this.change_input());
            return this.input_el;
        }
        render_selection() {
            const selected = this.model.value;
            for (const el of this.input_el.querySelectorAll("option")) {
                if (el.value === selected) {
                    el.selected = true;
                }
            }
            // Note that some browser implementations might not reduce
            // the number of visible options for size <= 3.
            this.input_el.size = this.model.size;
        }
        change_input() {
            const is_focused = this.el.querySelector("select:focus") != null;
            let value = null;
            for (const el of this.shadow_el.querySelectorAll("option")) {
                if (el.selected) {
                    value = el.value;
                    break;
                }
            }
            this.model.value = value;
            super.change_input();
            // Restore focus back to the <select> afterwards,
            // so that even if python on_change callback is invoked,
            // focus remains on <select> and one can seamlessly scroll
            // up/down.
            if (is_focused) {
                this.input_el.focus();
            }
        }
    }
    exports.SingleSelectView = SingleSelectView;
    SingleSelectView.__name__ = "SingleSelectView";
    class SingleSelect extends input_widget_1.InputWidget {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.SingleSelect = SingleSelect;
    _a = SingleSelect;
    SingleSelect.__name__ = "SingleSelect";
    SingleSelect.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = SingleSelectView;
        _a.define(({ Any, List, Int, Nullable, Str }) => ({
            disabled_options: [List(Str), []],
            options: [List(Any), []],
            size: [Int, 4], // 4 is the HTML default
            value: [Nullable(Str), null],
        }));
    })();
},
"739cca6576": /* models/speech_to_text.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    const iconStarted = `<svg xmlns="http://www.w3.org/2000/svg" height="22px" style="vertical-align: middle;" fill="currentColor" class="bi bi-mic" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z"/>
  <path fill-rule="evenodd" d="M10 8V3a2 2 0 1 0-4 0v5a2 2 0 1 0 4 0zM8 0a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V3a3 3 0 0 0-3-3z"/>
</svg>`;
    const iconNotStarted = `<svg xmlns="http://www.w3.org/2000/svg" height="22px" style="vertical-align: middle;" fill="currentColor" class="bi bi-mic-mute" viewBox="0 0 16 16">
<path fill-rule="evenodd" d="M12.734 9.613A4.995 4.995 0 0 0 13 8V7a.5.5 0 0 0-1 0v1c0 .274-.027.54-.08.799l.814.814zm-2.522 1.72A4 4 0 0 1 4 8V7a.5.5 0 0 0-1 0v1a5 5 0 0 0 4.5 4.975V15h-3a.5.5 0 0 0 0 1h7a.5.5 0 0 0 0-1h-3v-2.025a4.973 4.973 0 0 0 2.43-.923l-.718-.719zM11 7.88V3a3 3 0 0 0-5.842-.963l.845.845A2 2 0 0 1 10 3v3.879l1 1zM8.738 9.86l.748.748A3 3 0 0 1 5 8V6.121l1 1V8a2 2 0 0 0 2.738 1.86zm4.908 3.494l-12-12 .708-.708 12 12-.708.707z"/>
</svg>`;
    const titleStarted = "Click to STOP the speech recognition.";
    const titleNotStarted = "Click to START the speech recognition.";
    const { webkitSpeechRecognition } = window;
    const { webkitSpeechGrammarList } = window;
    function htmlToElement(html) {
        const template = document.createElement("template");
        html = html.trim(); // Never return a text node of whitespace as the result
        template.innerHTML = html;
        return template.content.firstChild;
    }
    function deserializeGrammars(grammars) {
        if (grammars) {
            const speechRecognitionList = new webkitSpeechGrammarList();
            for (const grammar of grammars) {
                if (grammar.src) {
                    speechRecognitionList.addFromString(grammar.src, grammar.weight);
                }
                else if (grammar.uri) {
                    speechRecognitionList.addFromURI(grammar.uri, grammar.weight);
                }
            }
            return speechRecognitionList;
        }
        else {
            return null;
        }
    }
    function round(value) {
        return Math.round((value + Number.EPSILON) * 100) / 100;
    }
    function serializeResults(results_) {
        const results = [];
        for (const result of results_) {
            const alternatives = [];
            const item = { is_final: result.isFinal, alternatives };
            for (let i = 0; i < result.length; i++) {
                const alternative = {
                    confidence: round(result[i].confidence),
                    transcript: result[i].transcript,
                };
                alternatives.push(alternative);
            }
            item.alternatives = alternatives;
            results.push(item);
        }
        return results;
    }
    class SpeechToTextView extends layout_1.HTMLBoxView {
        initialize() {
            super.initialize();
            this.recognition = new webkitSpeechRecognition();
            this.recognition.lang = this.model.lang;
            this.recognition.continuous = this.model.continuous;
            this.recognition.interimResults = this.model.interim_results;
            this.recognition.maxAlternatives = this.model.max_alternatives;
            this.recognition.serviceURI = this.model.service_uri;
            this.setGrammars();
            this.recognition.onresult = (event) => {
                this.model.results = serializeResults(event.results);
            };
            this.recognition.onerror = (event) => {
                console.log("SpeechToText Error");
                console.log(event);
            };
            this.recognition.onnomatch = (event) => {
                console.log("SpeechToText No Match");
                console.log(event);
            };
            this.recognition.onaudiostart = () => this.model.audio_started = true;
            this.recognition.onaudioend = () => this.model.audio_started = false;
            this.recognition.onsoundstart = () => this.model.sound_started = true;
            this.recognition.onsoundend = () => this.model.sound_started = false;
            this.recognition.onspeechstart = () => this.model.speech_started = true;
            this.recognition.onspeechend = () => this.model.speech_started = false;
            this.recognition.onstart = () => {
                this.buttonEl.onclick = () => {
                    this.recognition.stop();
                };
                this.buttonEl.innerHTML = this.iconStarted();
                this.buttonEl.setAttribute("title", titleStarted);
                this.model.started = true;
            };
            this.recognition.onend = () => {
                this.buttonEl.onclick = () => {
                    this.recognition.start();
                };
                this.buttonEl.innerHTML = this.iconNotStarted();
                this.buttonEl.setAttribute("title", titleNotStarted);
                this.model.started = false;
            };
            this.buttonEl = htmlToElement(`<button class="bk bk-btn bk-btn-${this.model.button_type}" type="button" title="${titleNotStarted}"></button>`);
            this.buttonEl.innerHTML = this.iconNotStarted();
            this.buttonEl.onclick = () => this.recognition.start();
        }
        iconStarted() {
            if (this.model.button_started !== "") {
                return this.model.button_started;
            }
            else {
                return iconStarted;
            }
        }
        iconNotStarted() {
            if (this.model.button_not_started !== "") {
                return this.model.button_not_started;
            }
            else {
                return iconNotStarted;
            }
        }
        setIcon() {
            if (this.model.started) {
                this.buttonEl.innerHTML = this.iconStarted();
            }
            else {
                this.buttonEl.innerHTML = this.iconNotStarted();
            }
        }
        connect_signals() {
            super.connect_signals();
            const { start, stop, abort, grammars, lang, continuous, interim_results, max_alternatives, service_uri, button_type, button_hide, button_not_started, button_started, } = this.model.properties;
            this.on_change(start, () => {
                this.model.start = false;
                this.recognition.start();
            });
            this.on_change(stop, () => {
                this.model.stop = false;
                this.recognition.stop();
            });
            this.on_change(abort, () => {
                this.model.abort = false;
                this.recognition.abort();
            });
            this.on_change(grammars, () => this.setGrammars());
            this.on_change(lang, () => this.recognition.lang = this.model.lang);
            this.on_change(continuous, () => this.recognition.continuous = this.model.continuous);
            this.on_change(interim_results, () => this.recognition.interimResults = this.model.interim_results);
            this.on_change(max_alternatives, () => this.recognition.maxAlternatives = this.model.max_alternatives);
            this.on_change(service_uri, () => this.recognition.serviceURI = this.model.service_uri);
            this.on_change(button_type, () => this.buttonEl.className = `bk bk-btn bk-btn-${this.model.button_type}`);
            this.on_change(button_hide, () => this.render());
            this.on_change([button_not_started, button_started], () => this.setIcon());
        }
        setGrammars() {
            this.recognition.grammars = deserializeGrammars(this.model.grammars);
        }
        render() {
            super.render();
            if (!this.model.button_hide) {
                this.shadow_el.appendChild(this.buttonEl);
            }
        }
    }
    exports.SpeechToTextView = SpeechToTextView;
    SpeechToTextView.__name__ = "SpeechToTextView";
    class SpeechToText extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.SpeechToText = SpeechToText;
    _a = SpeechToText;
    SpeechToText.__name__ = "SpeechToText";
    SpeechToText.__module__ = "panel.models.speech_to_text";
    (() => {
        _a.prototype.default_view = SpeechToTextView;
        _a.define(({ Any, List, Bool, Float, Str }) => ({
            start: [Bool, false],
            stop: [Bool, false],
            abort: [Bool, false],
            grammars: [List(Any), []],
            lang: [Str, ""],
            continuous: [Bool, false],
            interim_results: [Bool, false],
            max_alternatives: [Float, 1],
            service_uri: [Str, ""],
            started: [Bool, false],
            audio_started: [Bool, false],
            sound_started: [Bool, false],
            speech_started: [Bool, false],
            button_type: [Str, "light"],
            button_hide: [Bool, false],
            button_not_started: [Str, ""],
            button_started: [Str, ""],
            results: [List(Any), []],
        }));
    })();
},
"92822cb73a": /* models/state.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const view_1 = require("@bokehjs/core/view");
    const array_1 = require("@bokehjs/core/util/array");
    const model_1 = require("@bokehjs/model");
    const receiver_1 = require("@bokehjs/protocol/receiver");
    function get_json(file, callback) {
        const xobj = new XMLHttpRequest();
        xobj.overrideMimeType("application/json");
        xobj.open("GET", file, true);
        xobj.onreadystatechange = function () {
            if (xobj.readyState == 4 && xobj.status == 200) {
                callback(xobj.responseText);
            }
        };
        xobj.send(null);
    }
    class StateView extends view_1.View {
    }
    exports.StateView = StateView;
    StateView.__name__ = "StateView";
    class State extends model_1.Model {
        constructor(attrs) {
            super(attrs);
            this._receiver = new receiver_1.Receiver();
            this._cache = {};
        }
        apply_state(state) {
            this._receiver.consume(state.header);
            this._receiver.consume(state.metadata);
            this._receiver.consume(state.content);
            if (this._receiver.message && this.document) {
                this.document.apply_json_patch(this._receiver.message.content);
            }
        }
        _receive_json(result, path) {
            const state = JSON.parse(result);
            this._cache[path] = state;
            let current = this.state;
            for (const i of this.values) {
                if (current instanceof Map) {
                    current = current.get(i);
                }
                else {
                    current = current[i];
                }
            }
            if (current === path) {
                this.apply_state(state);
            }
            else if (this._cache[current]) {
                this.apply_state(this._cache[current]);
            }
        }
        set_state(widget, value) {
            const values = (0, array_1.copy)(this.values);
            const index = this.widgets[widget.id];
            values[index] = value;
            let state = this.state;
            for (const i of values) {
                if (state instanceof Map) {
                    state = state.get(i);
                }
                else {
                    state = state[i];
                }
            }
            this.values = values;
            if (this.json) {
                if (this._cache[state]) {
                    this.apply_state(this._cache[state]);
                }
                else {
                    get_json(state, (result) => this._receive_json(result, state));
                }
            }
            else {
                this.apply_state(state);
            }
        }
    }
    exports.State = State;
    _a = State;
    State.__name__ = "State";
    State.__module__ = "panel.models.state";
    (() => {
        _a.prototype.default_view = StateView;
        _a.define(({ Any, Bool }) => ({
            json: [Bool, false],
            state: [Any, {}],
            widgets: [Any, {}],
            values: [Any, []],
        }));
    })();
},
"2231cdc549": /* models/tabs.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tslib_1 = require("tslib");
    const tabs = tslib_1.__importStar(require("@bokehjs/styles/tabs.css"));
    const grid_1 = require("@bokehjs/core/layout/grid");
    const enums_1 = require("@bokehjs/core/enums");
    const alignments_1 = require("@bokehjs/models/layouts/alignments");
    const tabs_1 = require("@bokehjs/models/layouts/tabs");
    const layout_dom_1 = require("@bokehjs/models/layouts/layout_dom");
    function show(element) {
        element.style.visibility = "";
        element.style.opacity = "";
    }
    function hide(element) {
        element.style.visibility = "hidden";
        element.style.opacity = "0";
    }
    class TabsView extends tabs_1.TabsView {
        connect_signals() {
            super.connect_signals();
            let view = this;
            while (view != null) {
                if (view.model.type.endsWith("Tabs")) {
                    view.connect(view.model.properties.active.change, () => this.update_zindex());
                }
                view = view.parent || view._parent; // Handle ReactiveHTML
            }
        }
        get is_visible() {
            let parent = this.parent;
            let current_view = this;
            while (parent != null) {
                if (parent.model.type.endsWith("Tabs")) {
                    if (parent.child_views.indexOf(current_view) !== parent.model.active) {
                        return false;
                    }
                }
                current_view = parent;
                parent = parent.parent || parent._parent; // Handle ReactiveHTML
            }
            return true;
        }
        render() {
            super.render();
            this.update_zindex();
        }
        update_zindex() {
            const { child_views } = this;
            for (const child_view of child_views) {
                if (child_view != null && child_view.el != null) {
                    child_view.el.style.zIndex = "";
                }
            }
            if (this.is_visible) {
                const active = child_views[this.model.active];
                if (active != null && active.el != null) {
                    active.el.style.zIndex = "1";
                }
            }
        }
        _after_layout() {
            layout_dom_1.LayoutDOMView.prototype._after_layout.call(this);
            const { child_views } = this;
            for (const child_view of child_views) {
                if (child_view !== undefined) {
                    hide(child_view.el);
                }
            }
            const { active } = this.model;
            if (active in child_views) {
                const tab = child_views[active];
                if (tab !== undefined) {
                    show(tab.el);
                }
            }
        }
        _update_layout() {
            layout_dom_1.LayoutDOMView.prototype._update_layout.call(this);
            const loc = this.model.tabs_location;
            this.class_list.remove([...enums_1.Location].map((loc) => tabs[loc]));
            this.class_list.add(tabs[loc]);
            const layoutable = new grid_1.Container();
            for (const view of this.child_views) {
                if (view == undefined) {
                    continue;
                }
                view.style.append(":host", { grid_area: "stack" });
                if (view instanceof layout_dom_1.LayoutDOMView && view.layout != null) {
                    layoutable.add({ r0: 0, c0: 0, r1: 1, c1: 1 }, view);
                }
            }
            if (layoutable.size != 0) {
                this.layout = new alignments_1.GridAlignmentLayout(layoutable);
                this.layout.set_sizing();
            }
            else {
                delete this.layout;
            }
        }
        update_active() {
            const i = this.model.active;
            const { header_els } = this;
            for (const el of header_els) {
                el.classList.remove(tabs.active);
            }
            if (i in header_els) {
                header_els[i].classList.add(tabs.active);
            }
            const { child_views } = this;
            for (const child_view of child_views) {
                hide(child_view.el);
            }
            if (i in child_views) {
                const view = child_views[i];
                show(view.el);
                if (view.invalidate_render == null) {
                    view.invalidate_render();
                }
            }
        }
    }
    exports.TabsView = TabsView;
    TabsView.__name__ = "TabsView";
    class Tabs extends tabs_1.Tabs {
    }
    exports.Tabs = Tabs;
    _a = Tabs;
    Tabs.__name__ = "Tabs";
    Tabs.__module__ = "panel.models.tabs";
    (() => {
        _a.prototype.default_view = TabsView;
    })();
},
"121f00bd6f": /* models/terminal.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a, _b;
    __esModule();
    const dom_1 = require("@bokehjs/core/dom");
    const bokeh_events_1 = require("@bokehjs/core/bokeh_events");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    class KeystrokeEvent extends bokeh_events_1.ModelEvent {
        constructor(key) {
            super();
            this.key = key;
        }
        get event_values() {
            return { model: this.origin, key: this.key };
        }
    }
    exports.KeystrokeEvent = KeystrokeEvent;
    _a = KeystrokeEvent;
    KeystrokeEvent.__name__ = "KeystrokeEvent";
    (() => {
        _a.prototype.event_name = "keystroke";
    })();
    class TerminalView extends layout_1.HTMLBoxView {
        connect_signals() {
            super.connect_signals();
            const { output, _clears } = this.model.properties;
            this.on_change(output, this.write);
            this.on_change(_clears, this.clear);
        }
        render() {
            super.render();
            this.container = (0, dom_1.div)({ class: "terminal-container" });
            (0, layout_1.set_size)(this.container, this.model);
            this.term = this.getNewTerminal();
            this.term.onData((value) => {
                this.handleOnData(value);
            });
            this.webLinksAddon = this.getNewWebLinksAddon();
            this.term.loadAddon(this.webLinksAddon);
            this.term.open(this.container);
            this.term.onRender(() => {
                if (!this._rendered) {
                    this.fit();
                }
            });
            this.write();
            this.shadow_el.appendChild(this.container);
        }
        getNewTerminal() {
            const wn = window;
            if (wn.Terminal) {
                return new wn.Terminal(this.model.options);
            }
            else {
                return new wn.xtermjs.Terminal(this.model.options);
            }
        }
        getNewWebLinksAddon() {
            const wn = window;
            return new wn.WebLinksAddon.WebLinksAddon();
        }
        handleOnData(value) {
            this.model.trigger_event(new KeystrokeEvent(value));
        }
        write() {
            const text = this.model.output;
            if (text == null || !text.length) {
                return;
            }
            // https://stackoverflow.com/questions/65367607/how-to-handle-new-line-in-xterm-js-while-writing-data-into-the-terminal
            const cleaned = text.replace(/\r?\n/g, "\r\n");
            // var text = Array.from(cleaned, (x) => x.charCodeAt(0))
            this.term.write(cleaned);
        }
        clear() {
            this.term.clear();
        }
        fit() {
            const width = this.container.offsetWidth;
            const height = this.container.offsetHeight;
            const renderer = this.term._core._renderService;
            const cell_width = renderer.dimensions.actualCellWidth || 9;
            const cell_height = renderer.dimensions.actualCellHeight || 18;
            if (width == null || height == null || width <= 0 || height <= 0) {
                return;
            }
            const cols = Math.max(2, Math.floor(width / cell_width));
            const rows = Math.max(1, Math.floor(height / cell_height));
            if (this.term.rows !== rows || this.term.cols !== cols) {
                this.term.resize(cols, rows);
            }
            this.model.ncols = cols;
            this.model.nrows = rows;
            this._rendered = true;
        }
        after_layout() {
            super.after_layout();
            if (this.container != null) {
                this.fit();
            }
        }
    }
    exports.TerminalView = TerminalView;
    TerminalView.__name__ = "TerminalView";
    // The Bokeh .ts model corresponding to the Bokeh .py model
    class Terminal extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.Terminal = Terminal;
    _b = Terminal;
    Terminal.__name__ = "Terminal";
    Terminal.__module__ = "panel.models.terminal";
    (() => {
        _b.prototype.default_view = TerminalView;
        _b.define(({ Any, Int, Str }) => ({
            _clears: [Int, 0],
            options: [Any, {}],
            output: [Str, ""],
            ncols: [Int, 0],
            nrows: [Int, 0],
        }));
    })();
},
"a04eb51988": /* models/text_to_speech.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    function toVoicesList(voices) {
        const voicesList = [];
        for (const voice of voices) {
            const item = {
                default: voice.default,
                lang: voice.lang,
                local_service: voice.localService,
                name: voice.name,
                voice_uri: voice.voiceURI,
            };
            voicesList.push(item);
        }
        return voicesList;
    }
    class TextToSpeechView extends layout_1.HTMLBoxView {
        initialize() {
            super.initialize();
            this.model.paused = speechSynthesis.paused;
            this.model.pending = speechSynthesis.pending;
            this.model.speaking = speechSynthesis.speaking;
            // Hack: Keeps speeking for longer texts
            // https://stackoverflow.com/questions/21947730/chrome-speech-synthesis-with-longer-texts
            this._callback = window.setInterval(function () {
                if (!speechSynthesis.paused && speechSynthesis.speaking) {
                    window.speechSynthesis.resume();
                }
            }, 10000);
            const populateVoiceList = () => {
                if (typeof speechSynthesis === "undefined") {
                    return;
                }
                // According to https://talkrapp.com/speechSynthesis.html not all voices are available
                // The article includes code for ios to handle this. Might be useful.
                this.voices = speechSynthesis.getVoices();
                if (!this.voices) {
                    return;
                }
                this.model.voices = toVoicesList(this.voices);
            };
            populateVoiceList();
            if (typeof speechSynthesis !== "undefined" && speechSynthesis.onvoiceschanged !== undefined) {
                speechSynthesis.onvoiceschanged = populateVoiceList;
            }
        }
        remove() {
            if (this._callback != null) {
                clearInterval(this._callback);
            }
            speechSynthesis.cancel();
            super.remove();
        }
        connect_signals() {
            super.connect_signals();
            const { speak, pause, resume, cancel } = this.model.properties;
            this.on_change(speak, () => {
                this.speak();
            });
            this.on_change(pause, () => {
                this.model.pause = false;
                speechSynthesis.pause();
            });
            this.on_change(resume, () => {
                this.model.resume = false;
                speechSynthesis.resume();
            });
            this.on_change(cancel, () => {
                this.model.cancel = false;
                speechSynthesis.cancel();
            });
        }
        speak() {
            const utterance = new SpeechSynthesisUtterance(this.model.speak.text);
            utterance.pitch = this.model.speak.pitch;
            utterance.volume = this.model.speak.volume;
            utterance.rate = this.model.speak.rate;
            if (this.model.voices) {
                for (const voice of this.voices) {
                    if (voice.name === this.model.speak.voice) {
                        utterance.voice = voice;
                    }
                }
            }
            utterance.onpause = () => this.model.paused = true;
            utterance.onstart = () => {
                this.model.speaking = true;
                this.model.paused = false;
                this.model.pending = speechSynthesis.pending;
            };
            utterance.onresume = () => this.model.paused = false;
            utterance.onend = () => {
                this.model.speaking = false;
                this.model.paused = false;
                this.model.pending = speechSynthesis.pending;
            };
            speechSynthesis.speak(utterance);
            this.model.paused = speechSynthesis.paused;
            this.model.pending = speechSynthesis.pending;
        }
        render() {
            super.render();
            // Hack: This will make sure voices are assigned when
            // Bokeh/ Panel is served first time with --show option.
            if (!this.model.voices) {
                this.model.voices = toVoicesList(this.voices);
            }
            if (this.model.speak != null && this.model.speak.text) {
                this.speak();
            }
        }
    }
    exports.TextToSpeechView = TextToSpeechView;
    TextToSpeechView.__name__ = "TextToSpeechView";
    class TextToSpeech extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.TextToSpeech = TextToSpeech;
    _a = TextToSpeech;
    TextToSpeech.__name__ = "TextToSpeech";
    TextToSpeech.__module__ = "panel.models.text_to_speech";
    (() => {
        _a.prototype.default_view = TextToSpeechView;
        _a.define(({ Any, List, Bool }) => ({
            paused: [Bool, false],
            pending: [Bool, false],
            speaking: [Bool, false],
            voices: [List(Any), []],
            cancel: [Bool, false],
            pause: [Bool, false],
            resume: [Bool, false],
            speak: [Any, {}],
        }));
    })();
},
"ad985f285e": /* models/toggle_icon.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const icon_1 = require("a97a38b997") /* ./icon */;
    class ToggleIconView extends icon_1.ClickableIconView {
        *controls() { }
        click() {
            if (this.model.disabled) {
                return;
            }
            super.click();
            this.model.value = !this.model.value;
        }
    }
    exports.ToggleIconView = ToggleIconView;
    ToggleIconView.__name__ = "ToggleIconView";
    class ToggleIcon extends icon_1.ClickableIcon {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.ToggleIcon = ToggleIcon;
    _a = ToggleIcon;
    ToggleIcon.__name__ = "ToggleIcon";
    ToggleIcon.__module__ = "panel.models.icon";
    (() => {
        _a.prototype.default_view = ToggleIconView;
        _a.define(({}) => ({}));
    })();
},
"ae3a172647": /* models/tooltip_icon.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tslib_1 = require("tslib");
    const tooltip_1 = require("@bokehjs/models/ui/tooltip");
    const layout_dom_1 = require("@bokehjs/models/layouts/layout_dom");
    const dom_1 = require("@bokehjs/core/dom");
    const inputs_css_1 = tslib_1.__importStar(require("@bokehjs/styles/widgets/inputs.css")), inputs = inputs_css_1;
    const icons_css_1 = tslib_1.__importDefault(require("@bokehjs/styles/icons.css"));
    class TooltipIconView extends layout_dom_1.LayoutDOMView {
        get child_models() {
            if (this.model.description == null) {
                return [];
            }
            return [this.model.description];
        }
        connect_signals() {
            super.connect_signals();
            const { description } = this.model.properties;
            this.on_change(description, () => this.update_children());
        }
        stylesheets() {
            return [...super.stylesheets(), inputs_css_1.default, icons_css_1.default];
        }
        render() {
            super.render();
            const icon_el = (0, dom_1.div)({ class: inputs.icon });
            this.desc_el = (0, dom_1.div)({ class: inputs.description }, icon_el);
            this.model.description.target = this.desc_el;
            let persistent = false;
            const toggle = (visible) => {
                this.model.description.setv({
                    visible,
                    closable: persistent,
                });
                icon_el.classList.toggle(inputs.opaque, visible && persistent);
            };
            this.on_change(this.model.description.properties.visible, () => {
                const { visible } = this.model.description;
                if (!visible) {
                    persistent = false;
                }
                toggle(visible);
            });
            this.desc_el.addEventListener("mouseenter", () => {
                toggle(true);
            });
            this.desc_el.addEventListener("mouseleave", () => {
                if (!persistent) {
                    toggle(false);
                }
            });
            document.addEventListener("mousedown", (event) => {
                const path = event.composedPath();
                const tooltip_view = this._child_views.get(this.model.description);
                if (tooltip_view !== undefined && path.includes(tooltip_view.el)) {
                    return;
                }
                else if (path.includes(this.desc_el)) {
                    persistent = !persistent;
                    toggle(persistent);
                }
                else {
                    persistent = false;
                    toggle(false);
                }
            });
            window.addEventListener("blur", () => {
                persistent = false;
                toggle(false);
            });
            // Label to get highlight when icon is hovered
            this.shadow_el.appendChild((0, dom_1.label)(this.desc_el));
        }
    }
    exports.TooltipIconView = TooltipIconView;
    TooltipIconView.__name__ = "TooltipIconView";
    class TooltipIcon extends layout_dom_1.LayoutDOM {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.TooltipIcon = TooltipIcon;
    _a = TooltipIcon;
    TooltipIcon.__name__ = "TooltipIcon";
    TooltipIcon.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = TooltipIconView;
        _a.define(({ Ref }) => ({
            description: [Ref(tooltip_1.Tooltip), new tooltip_1.Tooltip()],
        }));
    })();
},
"3584638c04": /* models/trend.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    const build_views_1 = require("@bokehjs/core/build_views");
    const plots_1 = require("@bokehjs/models/plots");
    const glyphs_1 = require("@bokehjs/models/glyphs");
    const dom_1 = require("@bokehjs/core/dom");
    const column_data_source_1 = require("@bokehjs/models/sources/column_data_source");
    const formatters_1 = require("@bokehjs/models/formatters");
    const red = "#d9534f";
    const green = "#5cb85c";
    const blue = "#428bca";
    class TrendIndicatorView extends layout_1.HTMLBoxView {
        initialize() {
            super.initialize();
            this.containerDiv = (0, dom_1.div)({ style: "height:100%; width:100%;" });
            this.titleDiv = (0, dom_1.div)({ style: "font-size: 1em; word-wrap: break-word;" });
            this.valueDiv = (0, dom_1.div)({ style: "font-size: 2em" });
            this.value2Div = (0, dom_1.div)({ style: "font-size: 1em; opacity: 0.5; display: inline" });
            this.changeDiv = (0, dom_1.div)({ style: "font-size: 1em; opacity: 0.5; display: inline" });
            this.textDiv = (0, dom_1.div)({}, this.titleDiv, this.valueDiv, (0, dom_1.div)({}, this.changeDiv, this.value2Div));
            this.updateTitle();
            this.updateValue();
            this.updateValue2();
            this.updateValueChange();
            this.updateTextFontSize();
            this.plotDiv = (0, dom_1.div)({});
            this.containerDiv = (0, dom_1.div)({ style: "height:100%; width:100%" }, this.textDiv, this.plotDiv);
            this.updateLayout();
        }
        connect_signals() {
            super.connect_signals();
            const { pos_color, neg_color, plot_color, plot_type, width, height, sizing_mode, title, value, value_change, layout, } = this.model.properties;
            this.on_change([pos_color, neg_color], () => this.updateValueChange());
            this.on_change([plot_color, plot_type, width, height, sizing_mode], () => this.render());
            this.on_change(title, () => this.updateTitle(true));
            this.on_change(value, () => this.updateValue(true));
            this.on_change(value_change, () => this.updateValue2(true));
            this.on_change(layout, () => this.updateLayout());
        }
        async render() {
            super.render();
            this.shadow_el.appendChild(this.containerDiv);
            await this.setPlot();
        }
        async setPlot() {
            this.plot = new plots_1.Plot({
                background_fill_color: null,
                border_fill_color: null,
                outline_line_color: null,
                min_border: 0,
                sizing_mode: "stretch_both",
                toolbar_location: null,
            });
            const source = this.model.source;
            if (this.model.plot_type === "line") {
                const line = new glyphs_1.Line({
                    x: { field: this.model.plot_x },
                    y: { field: this.model.plot_y },
                    line_width: 4,
                    line_color: this.model.plot_color,
                });
                this.plot.add_glyph(line, source);
            }
            else if (this.model.plot_type === "step") {
                const step = new glyphs_1.Step({
                    x: { field: this.model.plot_x },
                    y: { field: this.model.plot_y },
                    line_width: 3,
                    line_color: this.model.plot_color,
                });
                this.plot.add_glyph(step, source);
            }
            else if (this.model.plot_type === "area") {
                const varea = new glyphs_1.VArea({
                    x: { field: this.model.plot_x },
                    y1: { field: this.model.plot_y },
                    y2: 0,
                    fill_color: this.model.plot_color,
                    fill_alpha: 0.5,
                });
                this.plot.add_glyph(varea, source);
                const line = new glyphs_1.Line({
                    x: { field: this.model.plot_x },
                    y: { field: this.model.plot_y },
                    line_width: 3,
                    line_color: this.model.plot_color,
                });
                this.plot.add_glyph(line, source);
            }
            else {
                const vbar = new glyphs_1.VBar({
                    x: { field: this.model.plot_x },
                    top: { field: this.model.plot_y },
                    width: 0.9,
                    line_color: null,
                    fill_color: this.model.plot_color,
                });
                this.plot.add_glyph(vbar, source);
            }
            const view = await (0, build_views_1.build_view)(this.plot);
            this.plotDiv.innerHTML = "";
            view.render_to(this.plotDiv);
        }
        after_layout() {
            super.after_layout();
            this.updateTextFontSize();
        }
        updateTextFontSize() {
            this.updateTextFontSizeColumn();
        }
        updateTextFontSizeColumn() {
            let elWidth = this.containerDiv.clientWidth;
            let elHeight = this.containerDiv.clientHeight;
            if (this.model.layout === "column") {
                elHeight = Math.round(elHeight / 2);
            }
            else {
                elWidth = Math.round(elWidth / 2);
            }
            const widthTitle = this.model.title.length;
            const widthValue = 2 * this._value_format.length;
            const widthValue2 = this._value_change_format.length + 1;
            const widthConstraint1 = elWidth / widthTitle * 2.0;
            const widthConstraint2 = elWidth / widthValue * 1.8;
            const widthConstraint3 = elWidth / widthValue2 * 2.0;
            const heightConstraint = elHeight / 6;
            const fontSize = Math.min(widthConstraint1, widthConstraint2, widthConstraint3, heightConstraint);
            this.textDiv.style.fontSize = `${Math.trunc(fontSize)}px`;
            this.textDiv.style.lineHeight = "1.3";
        }
        updateTitle(update_fontsize = false) {
            this.titleDiv.innerText = this.model.title;
            if (update_fontsize) {
                this.updateTextFontSize();
            }
        }
        updateValue(update_fontsize = false) {
            this._value_format = this.model.formatter.doFormat([this.model.value], { loc: 0 })[0];
            this.valueDiv.innerText = this._value_format;
            if (update_fontsize) {
                this.updateTextFontSize();
            }
        }
        updateValue2(update_fontsize = false) {
            this._value_change_format = this.model.change_formatter.doFormat([this.model.value_change], { loc: 0 })[0];
            this.value2Div.innerText = this._value_change_format;
            this.updateValueChange();
            if (update_fontsize) {
                this.updateTextFontSize();
            }
        }
        updateValueChange() {
            if (this.model.value_change > 0) {
                this.changeDiv.innerHTML = "&#9650;";
                this.changeDiv.style.color = this.model.pos_color;
            }
            else if (this.model.value_change < 0) {
                this.changeDiv.innerHTML = "&#9660;";
                this.changeDiv.style.color = this.model.neg_color;
            }
            else {
                this.changeDiv.innerHTML = "&nbsp;";
                this.changeDiv.style.color = "inherit";
            }
        }
        updateLayout() {
            if (this.model.layout === "column") {
                this.containerDiv.style.display = "block";
                this.textDiv.style.height = "50%";
                this.textDiv.style.width = "100%";
                this.plotDiv.style.height = "50%";
                this.plotDiv.style.width = "100%";
            }
            else {
                this.containerDiv.style.display = "flex";
                this.textDiv.style.height = "100%";
                this.textDiv.style.width = "";
                this.plotDiv.style.height = "100%";
                this.plotDiv.style.width = "";
                this.textDiv.style.flex = "1";
                this.plotDiv.style.flex = "1";
            }
            if (this._has_finished) {
                this.invalidate_layout();
            }
        }
    }
    exports.TrendIndicatorView = TrendIndicatorView;
    TrendIndicatorView.__name__ = "TrendIndicatorView";
    class TrendIndicator extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.TrendIndicator = TrendIndicator;
    _a = TrendIndicator;
    TrendIndicator.__name__ = "TrendIndicator";
    TrendIndicator.__module__ = "panel.models.trend";
    (() => {
        _a.prototype.default_view = TrendIndicatorView;
        _a.define(({ Float, Str, Ref }) => ({
            description: [Str, ""],
            formatter: [Ref(formatters_1.TickFormatter), () => new formatters_1.BasicTickFormatter()],
            change_formatter: [Ref(formatters_1.TickFormatter), () => new formatters_1.NumeralTickFormatter()],
            layout: [Str, "column"],
            source: [Ref(column_data_source_1.ColumnDataSource)],
            plot_x: [Str, "x"],
            plot_y: [Str, "y"],
            plot_color: [Str, blue],
            plot_type: [Str, "bar"],
            pos_color: [Str, green],
            neg_color: [Str, red],
            title: [Str, ""],
            value: [Float, 0],
            value_change: [Float, 0],
        }));
    })();
},
"119dc23765": /* models/vega.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a, _b;
    __esModule();
    const dom_1 = require("@bokehjs/core/dom");
    const bokeh_events_1 = require("@bokehjs/core/bokeh_events");
    const types_1 = require("@bokehjs/core/util/types");
    const layout_dom_1 = require("@bokehjs/models/layouts/layout_dom");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    const debounce_1 = require("99a25e6992") /* debounce */;
    class VegaEvent extends bokeh_events_1.ModelEvent {
        constructor(data) {
            super();
            this.data = data;
        }
        get event_values() {
            return { model: this.origin, data: this.data };
        }
    }
    exports.VegaEvent = VegaEvent;
    _a = VegaEvent;
    VegaEvent.__name__ = "VegaEvent";
    (() => {
        _a.prototype.event_name = "vega_event";
    })();
    class VegaPlotView extends layout_dom_1.LayoutDOMView {
        constructor() {
            super(...arguments);
            this._rendered = false;
        }
        connect_signals() {
            super.connect_signals();
            const { data, show_actions, theme, data_sources, events } = this.model.properties;
            this._replot = (0, debounce_1.debounce)(() => this._plot(), 20);
            this.on_change([data, show_actions, theme], () => {
                this._replot();
            });
            this.on_change(data_sources, () => this._connect_sources());
            this.on_change(events, () => {
                for (const event of this.model.events) {
                    if (this._callbacks.indexOf(event) > -1) {
                        continue;
                    }
                    this._callbacks.push(event);
                    const callback = (name, value) => this._dispatch_event(name, value);
                    const timeout = this.model.throttle[event] || 20;
                    this.vega_view.addSignalListener(event, (0, debounce_1.debounce)(callback, timeout, false));
                }
            });
            this._connected = [];
            this._connect_sources();
        }
        _connect_sources() {
            for (const ds in this.model.data_sources) {
                const cds = this.model.data_sources[ds];
                if (this._connected.indexOf(ds) < 0) {
                    this.connect(cds.properties.data.change, () => this._replot());
                    this._connected.push(ds);
                }
            }
        }
        remove() {
            if (this.vega_view) {
                this.vega_view.finalize();
            }
            super.remove();
        }
        _dispatch_event(name, value) {
            if ("vlPoint" in value && value.vlPoint.or != null) {
                const indexes = [];
                for (const index of value.vlPoint.or) {
                    if (index._vgsid_ !== undefined) { // If "_vgsid_" property exists
                        indexes.push(index._vgsid_);
                    }
                    else { // If "_vgsid_" property doesn't exist
                        // Iterate through all properties in the "index" object
                        for (const key in index) {
                            if (index.hasOwnProperty(key)) { // To ensure key comes from "index" object itself, not its prototype
                                indexes.push({ [key]: index[key] }); // Push a new object with this key-value pair into the array
                            }
                        }
                    }
                }
                value = indexes;
            }
            this.model.trigger_event(new VegaEvent({ type: name, value }));
        }
        _fetch_datasets() {
            const datasets = {};
            for (const ds in this.model.data_sources) {
                const cds = this.model.data_sources[ds];
                const data = [];
                const columns = cds.columns();
                for (let i = 0; i < cds.get_length(); i++) {
                    const item = {};
                    for (const column of columns) {
                        item[column] = cds.data[column][i];
                    }
                    data.push(item);
                }
                datasets[ds] = data;
            }
            return datasets;
        }
        get child_models() {
            return [];
        }
        render() {
            super.render();
            this._rendered = false;
            this.container = (0, dom_1.div)();
            (0, layout_1.set_size)(this.container, this.model);
            this._callbacks = [];
            this._plot();
            this.shadow_el.append(this.container);
        }
        _plot() {
            const data = this.model.data;
            if ((data == null) || !window.vegaEmbed) {
                return;
            }
            if (this.model.data_sources && (Object.keys(this.model.data_sources).length > 0)) {
                const datasets = this._fetch_datasets();
                if ("data" in datasets) {
                    data.data.values = datasets.data;
                    delete datasets.data;
                }
                if (data.data != null) {
                    const data_objs = (0, types_1.isArray)(data.data) ? data.data : [data.data];
                    for (const d of data_objs) {
                        if (d.name in datasets) {
                            d.values = datasets[d.name];
                            delete datasets[d.name];
                        }
                    }
                }
                this.model.data.datasets = datasets;
            }
            const config = { actions: this.model.show_actions, theme: this.model.theme };
            window.vegaEmbed(this.container, this.model.data, config).then((result) => {
                this.vega_view = result.view;
                this._resize = (0, debounce_1.debounce)(() => this.resize_view(result.view), 50);
                const callback = (name, value) => this._dispatch_event(name, value);
                for (const event of this.model.events) {
                    this._callbacks.push(event);
                    const timeout = this.model.throttle[event] || 20;
                    this.vega_view.addSignalListener(event, (0, debounce_1.debounce)(callback, timeout, false));
                }
            });
        }
        after_layout() {
            super.after_layout();
            if (this.vega_view != null) {
                this._resize();
            }
        }
        resize_view(view) {
            const canvas = view._renderer.canvas();
            if (!this._rendered && canvas !== null) {
                for (const listener of view._eventListeners) {
                    if (listener.type === "resize") {
                        listener.handler(new Event("resize"));
                    }
                }
                this._rendered = true;
            }
        }
    }
    exports.VegaPlotView = VegaPlotView;
    VegaPlotView.__name__ = "VegaPlotView";
    class VegaPlot extends layout_dom_1.LayoutDOM {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.VegaPlot = VegaPlot;
    _b = VegaPlot;
    VegaPlot.__name__ = "VegaPlot";
    VegaPlot.__module__ = "panel.models.vega";
    (() => {
        _b.prototype.default_view = VegaPlotView;
        _b.define(({ Any, List, Bool, Nullable, Str }) => ({
            data: [Any, {}],
            data_sources: [Any, {}],
            events: [List(Str), []],
            show_actions: [Bool, false],
            theme: [Nullable(Str), null],
            throttle: [Any, {}],
        }));
    })();
},
"79dc37b888": /* models/video.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const tslib_1 = require("tslib");
    const dom_1 = require("@bokehjs/core/dom");
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    const video_css_1 = tslib_1.__importDefault(require("dfe21e6f1b") /* ../styles/models/video.css */);
    class VideoView extends layout_1.HTMLBoxView {
        constructor() {
            super(...arguments);
            this._blocked = false;
            this._setting = false;
        }
        initialize() {
            super.initialize();
            this._time = Date.now();
        }
        connect_signals() {
            super.connect_signals();
            const { loop, paused, muted, autoplay, time, value, volume } = this.model.properties;
            this.on_change(loop, () => this.set_loop());
            this.on_change(paused, () => this.set_paused());
            this.on_change(muted, () => this.set_muted());
            this.on_change(autoplay, () => this.set_autoplay());
            this.on_change(time, () => this.set_time());
            this.on_change(value, () => this.set_value());
            this.on_change(volume, () => this.set_volume());
        }
        stylesheets() {
            return [...super.stylesheets(), video_css_1.default];
        }
        render() {
            super.render();
            this.video_el = document.createElement("video");
            const container_el = document.createElement("div");
            container_el.className = "pn-video-container";
            container_el.style.height = "100%";
            container_el.style.width = "100%";
            const { sizing_mode } = this.model;
            if (sizing_mode == null || sizing_mode === "fixed") {
                const { width, height } = this.model;
                if (width != null) {
                    this.video_el.width = width;
                }
                if (height != null) {
                    this.video_el.height = height;
                }
            }
            const { max_width, max_height } = this.model;
            if (max_width != null) {
                this.video_el.style.maxWidth = (0, dom_1.px)(max_width);
            }
            if (max_height != null) {
                this.video_el.style.maxHeight = (0, dom_1.px)(max_height);
            }
            this.video_el.controls = true;
            this.video_el.src = this.model.value;
            this.video_el.currentTime = this.model.time;
            this.video_el.loop = this.model.loop;
            this.video_el.muted = this.model.muted;
            this.video_el.autoplay = this.model.autoplay;
            if (this.model.volume != null) {
                this.video_el.volume = this.model.volume / 100;
            }
            else {
                this.model.volume = this.video_el.volume * 100;
            }
            this.video_el.onpause = () => this.model.paused = true;
            this.video_el.onplay = () => this.model.paused = false;
            this.video_el.ontimeupdate = () => this.update_time();
            this.video_el.onvolumechange = () => this.update_volume();
            container_el.append(this.video_el);
            this.shadow_el.append(container_el);
            if (!this.model.paused) {
                void this.video_el.play();
            }
        }
        update_time() {
            if (this._setting) {
                this._setting = false;
                return;
            }
            if ((Date.now() - this._time) < this.model.throttle) {
                return;
            }
            this._blocked = true;
            this.model.time = this.video_el.currentTime;
            this._time = Date.now();
        }
        update_volume() {
            if (this._setting) {
                this._setting = false;
                return;
            }
            this._blocked = true;
            this.model.volume = this.video_el.volume * 100;
        }
        set_loop() {
            this.video_el.loop = this.model.loop;
        }
        set_muted() {
            this.video_el.muted = this.model.muted;
        }
        set_autoplay() {
            this.video_el.autoplay = this.model.autoplay;
        }
        set_paused() {
            const { paused } = this.model;
            if (!this.video_el.paused && paused) {
                this.video_el.pause();
            }
            if (this.video_el.paused && !paused) {
                void this.video_el.play();
            }
        }
        set_volume() {
            if (this._blocked) {
                this._blocked = false;
                return;
            }
            this._setting = true;
            const { volume } = this.model;
            if (volume != null) {
                this.video_el.volume = volume / 100;
            }
        }
        set_time() {
            if (this._blocked) {
                this._blocked = false;
                return;
            }
            this._setting = true;
            this.video_el.currentTime = this.model.time;
        }
        set_value() {
            this.video_el.src = this.model.value;
        }
    }
    exports.VideoView = VideoView;
    VideoView.__name__ = "VideoView";
    class Video extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.Video = Video;
    _a = Video;
    Video.__name__ = "Video";
    Video.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = VideoView;
        _a.define(({ Bool, Int, Float, Str, Nullable }) => ({
            loop: [Bool, false],
            paused: [Bool, true],
            muted: [Bool, false],
            autoplay: [Bool, false],
            time: [Float, 0],
            throttle: [Int, 250],
            value: [Str, ""],
            volume: [Nullable(Int), null],
        }));
    })();
},
"dfe21e6f1b": /* styles/models/video.css.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    exports.default = `video{object-fit:fill;width:100%;height:100%;}`;
},
"f8afc4e661": /* models/videostream.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    class VideoStreamView extends layout_1.HTMLBoxView {
        constructor() {
            super(...arguments);
            this.constraints = {
                audio: false,
                video: true,
            };
        }
        initialize() {
            super.initialize();
            if (this.model.timeout !== null) {
                this.set_timeout();
            }
        }
        connect_signals() {
            super.connect_signals();
            const { timeout, snapshot, paused } = this.model.properties;
            this.on_change(timeout, () => this.set_timeout());
            this.on_change(snapshot, () => this.snapshot());
            this.on_change(paused, () => this.pause());
        }
        pause() {
            if (this.model.paused) {
                if (this.timer != null) {
                    clearInterval(this.timer);
                    this.timer = null;
                }
                this.videoEl.pause();
            }
            else {
                this.videoEl.play();
            }
            this.set_timeout();
        }
        set_timeout() {
            if (this.timer) {
                clearInterval(this.timer);
                this.timer = null;
            }
            if (this.model.timeout != null && this.model.timeout > 0) {
                this.timer = setInterval(() => this.snapshot(), this.model.timeout);
            }
        }
        snapshot() {
            this.canvasEl.width = this.videoEl.videoWidth;
            this.canvasEl.height = this.videoEl.videoHeight;
            const context = this.canvasEl.getContext("2d");
            if (context) {
                context.drawImage(this.videoEl, 0, 0, this.canvasEl.width, this.canvasEl.height);
            }
            this.model.value = this.canvasEl.toDataURL(`image/${this.model.format}`, 0.95);
        }
        remove() {
            super.remove();
            if (this.timer) {
                clearInterval(this.timer);
                this.timer = null;
            }
        }
        render() {
            super.render();
            if (this.videoEl) {
                return;
            }
            this.videoEl = document.createElement("video");
            if (!this.model.sizing_mode || this.model.sizing_mode === "fixed") {
                if (this.model.height) {
                    this.videoEl.height = this.model.height;
                }
                if (this.model.width) {
                    this.videoEl.width = this.model.width;
                }
            }
            this.videoEl.style.objectFit = "fill";
            this.videoEl.style.minWidth = "100%";
            this.videoEl.style.minHeight = "100%";
            this.canvasEl = document.createElement("canvas");
            this.shadow_el.appendChild(this.videoEl);
            if (navigator.mediaDevices.getUserMedia) {
                navigator.mediaDevices.getUserMedia(this.constraints)
                    .then(stream => {
                    this.videoEl.srcObject = stream;
                    if (!this.model.paused) {
                        this.videoEl.play();
                    }
                })
                    .catch(console.error);
            }
        }
    }
    exports.VideoStreamView = VideoStreamView;
    VideoStreamView.__name__ = "VideoStreamView";
    class VideoStream extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.VideoStream = VideoStream;
    _a = VideoStream;
    VideoStream.__name__ = "VideoStream";
    VideoStream.__module__ = "panel.models.widgets";
    (() => {
        _a.prototype.default_view = VideoStreamView;
        _a.define(({ Any, Bool, Int, Nullable, Str }) => ({
            format: [Str, "png"],
            paused: [Bool, false],
            snapshot: [Bool, false],
            timeout: [Nullable(Int), null],
            value: [Any],
        }));
        _a.override({
            height: 240,
            width: 320,
        });
    })();
},
"470ce1dcbc": /* models/vizzu.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const dom_1 = require("@bokehjs/core/dom");
    const types_1 = require("@bokehjs/core/util/types");
    const column_data_source_1 = require("@bokehjs/models/sources/column_data_source");
    const bokeh_events_1 = require("@bokehjs/core/bokeh_events");
    const debounce_1 = require("99a25e6992") /* debounce */;
    const layout_1 = require("73d6aee8f5") /* ./layout */;
    class VizzuEvent extends bokeh_events_1.ModelEvent {
        constructor(data) {
            super();
            this.event_name = "vizzu_event";
            this.publish = true;
            this.data = data;
        }
        get event_values() {
            return { model: this.origin, data: this.data };
        }
    }
    exports.VizzuEvent = VizzuEvent;
    VizzuEvent.__name__ = "VizzuEvent";
    const VECTORIZED_PROPERTIES = ["x", "y", "color", "label", "lightness", "size", "splittedBy", "dividedBy"];
    class VizzuChartView extends layout_1.HTMLBoxView {
        constructor() {
            super(...arguments);
            this.update = [];
            this._animating = false;
        }
        connect_signals() {
            super.connect_signals();
            const update = (0, debounce_1.debounce)(() => {
                if (!this.valid_config) {
                    console.warn("Vizzu config not valid given current data.");
                    return;
                }
                else if ((this.update.length === 0) || this._animating) {
                    return;
                }
                else {
                    let change = {};
                    for (const prop of this.update) {
                        if (prop === "config") {
                            change = { ...change, config: this.config() };
                        }
                        else if (prop === "data") {
                            change = { ...change, data: this.data() };
                        }
                        else {
                            change = { ...change, style: this.model.style };
                        }
                    }
                    this._animating = true;
                    this.vizzu_view.animate(change, `${this.model.duration}ms`).then(() => {
                        this._animating = false;
                        if (this.update.length > 0) {
                            update();
                        }
                    });
                    this.update = [];
                }
            }, 20);
            const update_prop = (prop) => {
                if (!this.update.includes(prop)) {
                    this.update.push(prop);
                }
                update();
            };
            const { config, tooltip, style } = this.model.properties;
            this.on_change(config, () => update_prop("config"));
            this.on_change(this.model.source.properties.data, () => update_prop("data"));
            this.connect(this.model.source.streaming, () => update_prop("data"));
            this.connect(this.model.source.patching, () => update_prop("data"));
            this.on_change(tooltip, () => {
                this.vizzu_view.feature("tooltip", this.model.tooltip);
            });
            this.on_change(style, () => update_prop("style"));
        }
        get valid_config() {
            const columns = this.model.source.columns();
            if ("channels" in this.model.config) {
                for (const col of Object.values(this.model.config.channels)) {
                    if ((0, types_1.isArray)(col)) {
                        for (const c of col) {
                            if (col != null && !columns.includes(c)) {
                                return false;
                            }
                        }
                    }
                    else if ((0, types_1.isObject)(col)) {
                        for (const prop of Object.keys(col)) {
                            for (const c of col[prop]) {
                                if (col != null && !columns.includes(c)) {
                                    return false;
                                }
                            }
                        }
                    }
                    else if (col != null && !columns.includes(col)) {
                        return false;
                    }
                }
            }
            else {
                for (const prop of VECTORIZED_PROPERTIES) {
                    if (prop in this.model.config && !columns.includes(this.model.config[prop])) {
                        return false;
                    }
                }
            }
            return true;
        }
        config() {
            let config = { ...this.model.config };
            if ("channels" in config) {
                config.channels = { ...config.channels };
            }
            if (config.preset != undefined) {
                config = window.Vizzu.presets[config.preset](config);
            }
            return config;
        }
        data() {
            const series = [];
            for (const column of this.model.columns) {
                let array = [...this.model.source.get_array(column.name)];
                if (column.type === "datetime" || column.type == "date") {
                    column.type = "dimension";
                }
                if (column.type === "dimension") {
                    array = array.map(String);
                }
                series.push({ ...column, values: array });
            }
            return { series };
        }
        render() {
            super.render();
            this.container = (0, dom_1.div)({ style: "display: contents;" });
            this.shadow_el.append(this.container);
            const state = { config: this.config(), data: this.data(), style: this.model.style };
            this.vizzu_view = new window.Vizzu(this.container, state);
            this._animating = true;
            this.vizzu_view.initializing.then((chart) => {
                chart.on("click", (event) => {
                    this.model.trigger_event(new VizzuEvent({ ...event.target, ...event.detail }));
                });
                chart.feature("tooltip", this.model.tooltip);
                this._animating = false;
            });
        }
        remove() {
            if (this.vizzu_view) {
                this.vizzu_view.detach();
            }
            super.remove();
        }
    }
    exports.VizzuChartView = VizzuChartView;
    VizzuChartView.__name__ = "VizzuChartView";
    class VizzuChart extends layout_1.HTMLBox {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.VizzuChart = VizzuChart;
    _a = VizzuChart;
    VizzuChart.__name__ = "VizzuChart";
    VizzuChart.__module__ = "panel.models.vizzu";
    (() => {
        _a.prototype.default_view = VizzuChartView;
        _a.define(({ Any, List, Bool, Float, Ref }) => ({
            animation: [Any, {}],
            config: [Any, {}],
            columns: [List(Any), []],
            source: [Ref(column_data_source_1.ColumnDataSource)],
            duration: [Float, 500],
            style: [Any, {}],
            tooltip: [Bool, false],
        }));
    })();
},
"c51f25e2a7": /* models/vtk/index.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    var vtkjs_1 = require("ac55912dc1") /* ./vtkjs */;
    __esExport("VTKJSPlot", vtkjs_1.VTKJSPlot);
    var vtkvolume_1 = require("4797a2858f") /* ./vtkvolume */;
    __esExport("VTKVolumePlot", vtkvolume_1.VTKVolumePlot);
    var vtkaxes_1 = require("0379dcf1cd") /* ./vtkaxes */;
    __esExport("VTKAxes", vtkaxes_1.VTKAxes);
    var vtksynchronized_1 = require("a4e5946204") /* ./vtksynchronized */;
    __esExport("VTKSynchronizedPlot", vtksynchronized_1.VTKSynchronizedPlot);
},
"ac55912dc1": /* models/vtk/vtkjs.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const vtklayout_1 = require("b06d05fa3e") /* ./vtklayout */;
    const util_1 = require("df9946ff52") /* ./util */;
    class VTKJSPlotView extends vtklayout_1.AbstractVTKView {
        connect_signals() {
            super.connect_signals();
            const { data } = this.model.properties;
            this.on_change(data, () => {
                this.invalidate_render();
            });
        }
        render() {
            super.render();
            this._create_orientation_widget();
            this._set_axes();
        }
        invalidate_render() {
            this._vtk_renwin = null;
            super.invalidate_render();
        }
        init_vtk_renwin() {
            this._vtk_renwin = util_1.vtkns.FullScreenRenderWindow.newInstance({
                rootContainer: this._vtk_container,
                container: this._vtk_container,
            });
        }
        plot() {
            if (this.model.data == null && this.model.data_url == null) {
                this._vtk_renwin.getRenderWindow().render();
                return;
            }
            let bytes_promise;
            if (this.model.data_url) {
                bytes_promise = util_1.vtkns.DataAccessHelper.get("http").fetchBinary(this.model.data_url);
            }
            else {
                bytes_promise = async () => { this.model.data; };
            }
            bytes_promise.then((zipContent) => {
                const dataAccessHelper = util_1.vtkns.DataAccessHelper.get("zip", {
                    zipContent,
                    callback: (_zip) => {
                        const sceneImporter = util_1.vtkns.HttpSceneLoader.newInstance({
                            renderer: this._vtk_renwin.getRenderer(),
                            dataAccessHelper,
                        });
                        const fn = window.vtk.macro.debounce(() => {
                            setTimeout(() => {
                                if (this._axes == null && this.model.axes) {
                                    this._set_axes();
                                }
                                this._set_camera_state();
                                this._get_camera_state();
                                this._vtk_renwin.getRenderWindow().render();
                            }, 100);
                        }, 100);
                        sceneImporter.setUrl("index.json");
                        sceneImporter.onReady(fn);
                    },
                });
            });
        }
    }
    exports.VTKJSPlotView = VTKJSPlotView;
    VTKJSPlotView.__name__ = "VTKJSPlotView";
    class VTKJSPlot extends vtklayout_1.AbstractVTKPlot {
    }
    exports.VTKJSPlot = VTKJSPlot;
    _a = VTKJSPlot;
    VTKJSPlot.__name__ = "VTKJSPlot";
    (() => {
        _a.prototype.default_view = VTKJSPlotView;
        _a.define(({ Boolean, Bytes, Nullable, String }) => ({
            data: [Nullable(Bytes), null],
            data_url: [Nullable(String), null],
            enable_keybindings: [Boolean, false],
        }));
    })();
},
"b06d05fa3e": /* models/vtk/vtklayout.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const dom_1 = require("@bokehjs/core/dom");
    const object_1 = require("@bokehjs/core/util/object");
    const color_mapper_1 = require("@bokehjs/models/mappers/color_mapper");
    const kinds_1 = require("@bokehjs/core/kinds");
    const layout_1 = require("73d6aee8f5") /* ../layout */;
    const util_1 = require("df9946ff52") /* ./util */;
    const vtkcolorbar_1 = require("b1d68776a9") /* ./vtkcolorbar */;
    const vtkaxes_1 = require("0379dcf1cd") /* ./vtkaxes */;
    const INFO_DIV_STYLE = {
        padding: "0px 2px 0px 2px",
        maxHeight: "150px",
        height: "auto",
        backgroundColor: "rgba(255, 255, 255, 0.4)",
        borderRadius: "10px",
        margin: "2px",
        boxSizing: "border-box",
        overflow: "hidden",
        overflowY: "auto",
        transition: "width 0.1s linear",
        bottom: "0px",
        position: "absolute",
    };
    const textPositions = (0, kinds_1.Enum)("LowerLeft", "LowerRight", "UpperLeft", "UpperRight", "LowerEdge", "RightEdge", "LeftEdge", "UpperEdge");
    class AbstractVTKView extends layout_1.HTMLBoxView {
        initialize() {
            super.initialize();
            this._camera_callbacks = [];
            this._renderable = true;
            this._setting_camera = false;
            this._rendered = false;
        }
        _add_colorbars() {
            //construct colorbars
            const old_info_div = this.shadow_el.querySelector(".vtk_info");
            if (old_info_div) {
                this.shadow_el.removeChild(old_info_div);
            }
            if (this.model.color_mappers.length < 1) {
                return;
            }
            const info_div = document.createElement("div");
            const expand_width = "350px";
            const collapsed_width = "30px";
            info_div.classList.add("vtk_info");
            (0, util_1.applyStyle)(info_div, INFO_DIV_STYLE);
            (0, util_1.applyStyle)(info_div, { width: expand_width });
            this.shadow_el.appendChild(info_div);
            //construct colorbars
            const colorbars = [];
            this.model.color_mappers.forEach((mapper) => {
                const cb = new vtkcolorbar_1.VTKColorBar(info_div, mapper);
                colorbars.push(cb);
            });
            //content when collapsed
            const dots = document.createElement("div");
            (0, util_1.applyStyle)(dots, { textAlign: "center", fontSize: "20px" });
            dots.innerText = "...";
            info_div.addEventListener("click", () => {
                if (info_div.style.width === collapsed_width) {
                    info_div.removeChild(dots);
                    (0, util_1.applyStyle)(info_div, { height: "auto", width: expand_width });
                    colorbars.forEach((cb) => info_div.appendChild(cb.canvas));
                }
                else {
                    colorbars.forEach((cb) => info_div.removeChild(cb.canvas));
                    (0, util_1.applyStyle)(info_div, { height: collapsed_width, width: collapsed_width });
                    info_div.appendChild(dots);
                }
            });
            info_div.click();
        }
        _init_annotations_container() {
            if (!this._annotations_container) {
                this._annotations_container = document.createElement("div");
                this._annotations_container.style.position = "absolute";
                this._annotations_container.style.width = "100%";
                this._annotations_container.style.height = "100%";
                this._annotations_container.style.top = "0";
                this._annotations_container.style.left = "0";
                this._annotations_container.style.pointerEvents = "none";
            }
        }
        _clean_annotations() {
            if (this._annotations_container) {
                while (this._annotations_container.firstElementChild) {
                    this._annotations_container.firstElementChild.remove();
                }
            }
        }
        _add_annotations() {
            this._clean_annotations();
            const { annotations } = this.model;
            if (annotations != null) {
                for (const annotation of annotations) {
                    const { viewport, color, fontSize, fontFamily } = annotation;
                    textPositions.values.forEach((pos) => {
                        const text = annotation[pos];
                        if (text) {
                            const div = document.createElement("div");
                            div.textContent = text;
                            const { style } = div;
                            style.position = "absolute";
                            style.color = `rgb(${color.map((val) => 255 * val).join(",")})`;
                            style.fontSize = `${fontSize}px`;
                            style.padding = "5px";
                            style.fontFamily = fontFamily;
                            style.width = "fit-content";
                            if (pos == "UpperLeft") {
                                style.top = `${(1 - viewport[3]) * 100}%`;
                                style.left = `${viewport[0] * 100}%`;
                            }
                            if (pos == "UpperRight") {
                                style.top = `${(1 - viewport[3]) * 100}%`;
                                style.right = `${(1 - viewport[2]) * 100}%`;
                            }
                            if (pos == "LowerLeft") {
                                style.bottom = `${viewport[1] * 100}%`;
                                style.left = `${viewport[0] * 100}%`;
                            }
                            if (pos == "LowerRight") {
                                style.bottom = `${viewport[1] * 100}%`;
                                style.right = `${(1 - viewport[2]) * 100}%`;
                            }
                            if (pos == "UpperEdge") {
                                style.top = `${(1 - viewport[3]) * 100}%`;
                                style.left = `${(viewport[0] + (viewport[2] - viewport[0]) / 2) * 100}%`;
                                style.transform = "translateX(-50%)";
                            }
                            if (pos == "LowerEdge") {
                                style.bottom = `${viewport[1] * 100}%`;
                                style.left = `${(viewport[0] + (viewport[2] - viewport[0]) / 2) * 100}%`;
                                style.transform = "translateX(-50%)";
                            }
                            if (pos == "LeftEdge") {
                                style.left = `${viewport[0] * 100}%`;
                                style.top = `${(1 - viewport[3] + (viewport[3] - viewport[1]) / 2) * 100}%`;
                                style.transform = "translateY(-50%)";
                            }
                            if (pos == "RightEdge") {
                                style.right = `${(1 - viewport[2]) * 100}%`;
                                style.top = `${(1 - viewport[3] + (viewport[3] - viewport[1]) / 2) * 100}%`;
                                style.transform = "translateY(-50%)";
                            }
                            this._annotations_container.appendChild(div);
                        }
                    });
                }
            }
        }
        connect_signals() {
            super.connect_signals();
            this.on_change(this.model.properties.orientation_widget, () => {
                this._orientation_widget_visibility(this.model.orientation_widget);
            });
            this.on_change(this.model.properties.camera, () => this._set_camera_state());
            this.on_change(this.model.properties.axes, () => {
                this._delete_axes();
                if (this.model.axes) {
                    this._set_axes();
                }
                this._vtk_render();
            });
            this.on_change(this.model.properties.color_mappers, () => this._add_colorbars());
            this.on_change(this.model.properties.annotations, () => this._add_annotations());
        }
        render() {
            super.render();
            this._rendered = false;
            this._orientationWidget = null;
            this._axes = null;
            this._vtk_container = (0, dom_1.div)();
            this.init_vtk_renwin();
            this._init_annotations_container();
            (0, layout_1.set_size)(this._vtk_container, this.model);
            this.shadow_el.appendChild(this._vtk_container);
            // update camera model state only at the end of the interaction
            // with the scene (avoid bouncing events and large amount of events)
            this._vtk_renwin.getInteractor().onEndAnimation(() => this._get_camera_state());
            this._remove_default_key_binding();
            this._bind_key_events();
            this.plot();
            this.model.renderer_el = this._vtk_renwin;
            this.shadow_el.appendChild(this._annotations_container);
        }
        after_layout() {
            super.after_layout();
            if (this._renderable) {
                this._vtk_renwin.resize(); // resize call render method
            }
            this._vtk_render();
            if (!this._rendered) {
                this._add_colorbars();
                this._add_annotations();
                this._rendered = true;
            }
        }
        invalidate_render() {
            this._unsubscribe_camera_cb();
            super.invalidate_render();
        }
        remove() {
            this._unsubscribe_camera_cb();
            window.removeEventListener("resize", this._vtk_renwin.resize);
            if (this._orientationWidget != null) {
                this._orientationWidget.delete();
            }
            this._vtk_renwin.getRenderWindow().getInteractor().delete();
            this._vtk_renwin.delete();
            super.remove();
        }
        get _vtk_camera_state() {
            const vtk_camera = this._vtk_renwin.getRenderer().getActiveCamera();
            let state;
            if (vtk_camera) {
                state = (0, object_1.clone)(vtk_camera.get());
                delete state.cameraLightTransform;
                delete state.classHierarchy;
                delete state.vtkObject;
                delete state.vtkCamera;
                delete state.viewPlaneNormal;
                delete state.flattenedDepIds;
                delete state.managedInstanceId;
                delete state.directionOfProjection;
            }
            return state;
        }
        get _axes_canvas() {
            let axes_canvas = this._vtk_container.querySelector(".axes-canvas");
            if (!axes_canvas) {
                axes_canvas = (0, dom_1.canvas)({
                    style: {
                        position: "absolute",
                        top: "0",
                        left: "0",
                        width: "100%",
                        height: "100%",
                    },
                });
                axes_canvas.classList.add("axes-canvas");
                this._vtk_container.appendChild(axes_canvas);
                this._vtk_renwin.setResizeCallback(() => {
                    if (this._axes_canvas) {
                        const dims = this._vtk_container.getBoundingClientRect();
                        const width = Math.floor(dims.width * window.devicePixelRatio);
                        const height = Math.floor(dims.height * window.devicePixelRatio);
                        this._axes_canvas.setAttribute("width", width.toFixed());
                        this._axes_canvas.setAttribute("height", height.toFixed());
                    }
                });
            }
            return axes_canvas;
        }
        _bind_key_events() {
            this.el.addEventListener("mouseenter", () => {
                const interactor = this._vtk_renwin.getInteractor();
                if (this.model.enable_keybindings) {
                    document
                        .querySelector("body")
                        .addEventListener("keypress", interactor.handleKeyPress);
                    document
                        .querySelector("body")
                        .addEventListener("keydown", interactor.handleKeyDown);
                    document
                        .querySelector("body")
                        .addEventListener("keyup", interactor.handleKeyUp);
                }
            });
            this.el.addEventListener("mouseleave", () => {
                const interactor = this._vtk_renwin.getInteractor();
                document
                    .querySelector("body")
                    .removeEventListener("keypress", interactor.handleKeyPress);
                document
                    .querySelector("body")
                    .removeEventListener("keydown", interactor.handleKeyDown);
                document
                    .querySelector("body")
                    .removeEventListener("keyup", interactor.handleKeyUp);
            });
        }
        _create_orientation_widget() {
            const axes = util_1.vtkns.AxesActor.newInstance();
            // add orientation widget
            this._orientationWidget = util_1.vtkns.OrientationMarkerWidget.newInstance({
                actor: axes,
                interactor: this._vtk_renwin.getInteractor(),
            });
            this._orientationWidget.setEnabled(true);
            this._orientationWidget.setViewportCorner(util_1.vtkns.OrientationMarkerWidget.Corners.BOTTOM_RIGHT);
            this._orientationWidget.setViewportSize(0.15);
            this._orientationWidget.setMinPixelSize(75);
            this._orientationWidget.setMaxPixelSize(300);
            if (this.model.interactive_orientation_widget) {
                this._make_orientation_widget_interactive();
            }
            this._orientation_widget_visibility(this.model.orientation_widget);
        }
        _make_orientation_widget_interactive() {
            this._widgetManager = util_1.vtkns.WidgetManager.newInstance();
            this._widgetManager.setRenderer(this._orientationWidget.getRenderer());
            const axes = this._orientationWidget.getActor();
            const widget = util_1.vtkns.InteractiveOrientationWidget.newInstance();
            widget.placeWidget(axes.getBounds());
            widget.setBounds(axes.getBounds());
            widget.setPlaceFactor(1);
            const vw = this._widgetManager.addWidget(widget);
            // Manage user interaction
            vw.onOrientationChange(({ direction }) => {
                const camera = this._vtk_renwin.getRenderer().getActiveCamera();
                const focalPoint = camera.getFocalPoint();
                const position = camera.getPosition();
                const viewUp = camera.getViewUp();
                const distance = Math.sqrt((position[0] - focalPoint[0]) ** 2 +
                    (position[1] - focalPoint[1]) ** 2 +
                    (position[2] - focalPoint[2]) ** 2);
                camera.setPosition(focalPoint[0] + direction[0] * distance, focalPoint[1] + direction[1] * distance, focalPoint[2] + direction[2] * distance);
                if (direction[0]) {
                    camera.setViewUp((0, util_1.majorAxis)(viewUp, 1, 2));
                }
                if (direction[1]) {
                    camera.setViewUp((0, util_1.majorAxis)(viewUp, 0, 2));
                }
                if (direction[2]) {
                    camera.setViewUp((0, util_1.majorAxis)(viewUp, 0, 1));
                }
                this._vtk_renwin.getRenderer().resetCameraClippingRange();
                this._vtk_render();
                this._get_camera_state();
            });
        }
        _delete_axes() {
            if (this._axes) {
                Object.keys(this._axes).forEach((key) => {
                    this._vtk_renwin.getRenderer().removeActor(this._axes[key]);
                });
                this._axes = null;
                const textCtx = this._axes_canvas.getContext("2d");
                if (textCtx) {
                    textCtx.clearRect(0, 0, this._axes_canvas.clientWidth * window.devicePixelRatio, this._axes_canvas.clientHeight * window.devicePixelRatio);
                }
            }
        }
        _get_camera_state() {
            if (!this._setting_camera) {
                this._setting_camera = true;
                this.model.camera = this._vtk_camera_state;
                this._setting_camera = false;
            }
        }
        _orientation_widget_visibility(visibility) {
            this._orientationWidget.setEnabled(visibility);
            if (this._widgetManager != null) {
                if (visibility) {
                    this._widgetManager.enablePicking();
                }
                else {
                    this._widgetManager.disablePicking();
                }
            }
            this._vtk_render();
        }
        _remove_default_key_binding() {
            const interactor = this._vtk_renwin.getInteractor();
            document
                .querySelector("body")
                .removeEventListener("keypress", interactor.handleKeyPress);
            document
                .querySelector("body")
                .removeEventListener("keydown", interactor.handleKeyDown);
            document
                .querySelector("body")
                .removeEventListener("keyup", interactor.handleKeyUp);
        }
        _set_axes() {
            if (this.model.axes && this._vtk_renwin.getRenderer()) {
                const { psActor, axesActor, gridActor } = this.model.axes.create_axes(this._axes_canvas);
                this._axes = { psActor, axesActor, gridActor };
                if (psActor) {
                    this._vtk_renwin.getRenderer().addActor(psActor);
                }
                if (axesActor) {
                    this._vtk_renwin.getRenderer().addActor(axesActor);
                }
                if (gridActor) {
                    this._vtk_renwin.getRenderer().addActor(gridActor);
                }
            }
        }
        _set_camera_state() {
            if (!this._setting_camera && this._vtk_renwin.getRenderer() !== undefined) {
                this._setting_camera = true;
                if (this.model.camera &&
                    JSON.stringify(this.model.camera) != JSON.stringify(this._vtk_camera_state)) {
                    this._vtk_renwin
                        .getRenderer()
                        .getActiveCamera()
                        .set(this.model.camera);
                }
                this._vtk_renwin.getRenderer().resetCameraClippingRange();
                this._setting_camera = false;
            }
        }
        _unsubscribe_camera_cb() {
            this._camera_callbacks
                .splice(0, this._camera_callbacks.length)
                .map((cb) => cb.unsubscribe());
        }
        _vtk_render() {
            if (this._renderable) {
                if (this._orientationWidget) {
                    this._orientationWidget.updateMarkerOrientation();
                }
                this._vtk_renwin.getRenderWindow().render();
            }
        }
    }
    exports.AbstractVTKView = AbstractVTKView;
    AbstractVTKView.__name__ = "AbstractVTKView";
    class AbstractVTKPlot extends layout_1.HTMLBox {
        constructor(attrs) {
            (0, util_1.setup_vtkns)();
            super(attrs);
        }
        getActors() {
            return this.renderer_el.getRenderer().getActors();
        }
    }
    exports.AbstractVTKPlot = AbstractVTKPlot;
    _a = AbstractVTKPlot;
    AbstractVTKPlot.__name__ = "AbstractVTKPlot";
    AbstractVTKPlot.__module__ = "panel.models.vtk";
    (() => {
        _a.define(({ Any, Ref, Array, Boolean, Nullable }) => ({
            axes: [Nullable(Ref(vtkaxes_1.VTKAxes)), null],
            camera: [Any, {}],
            color_mappers: [Array(Ref(color_mapper_1.ColorMapper)), []],
            orientation_widget: [Boolean, false],
            interactive_orientation_widget: [Boolean, false],
            annotations: [Nullable(Array(Any)), null],
        }));
        _a.override({
            height: 300,
            width: 300,
        });
    })();
},
"df9946ff52": /* models/vtk/util.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const array_1 = require("@bokehjs/core/util/array");
    const kinds_1 = require("@bokehjs/core/kinds");
    exports.ARRAY_TYPES = {
        uint8: Uint8Array,
        int8: Int8Array,
        uint16: Uint16Array,
        int16: Int16Array,
        uint32: Uint32Array,
        int32: Int32Array,
        float32: Float32Array,
        float64: Float64Array,
    };
    exports.vtkns = {};
    function setup_vtkns() {
        if (exports.vtkns.Actor != null) {
            return;
        }
        const vtk = window.vtk;
        Object.assign(exports.vtkns, {
            Actor: vtk.Rendering.Core.vtkActor,
            AxesActor: vtk.Rendering.Core.vtkAxesActor,
            Base64: vtk.Common.Core.vtkBase64,
            BoundingBox: vtk.Common.DataModel.vtkBoundingBox,
            Camera: vtk.Rendering.Core.vtkCamera,
            ColorTransferFunction: vtk.Rendering.Core.vtkColorTransferFunction,
            CubeSource: vtk.Filters.Sources.vtkCubeSource,
            DataAccessHelper: vtk.IO.Core.DataAccessHelper,
            DataArray: vtk.Common.Core.vtkDataArray,
            Follower: vtk.Rendering.Core.vtkFollower,
            FullScreenRenderWindow: vtk.Rendering.Misc.vtkFullScreenRenderWindow,
            Glyph3DMapper: vtk.Rendering.Core.vtkGlyph3DMapper,
            HttpSceneLoader: vtk.IO.Core.vtkHttpSceneLoader,
            ImageData: vtk.Common.DataModel.vtkImageData,
            ImageMapper: vtk.Rendering.Core.vtkImageMapper,
            ImageProperty: vtk.Rendering.Core.vtkImageProperty,
            ImageSlice: vtk.Rendering.Core.vtkImageSlice,
            InteractiveOrientationWidget: vtk.Widgets.Widgets3D.vtkInteractiveOrientationWidget,
            InteractorStyleTrackballCamera: vtk.Interaction.Style.vtkInteractorStyleTrackballCamera,
            Light: vtk.Rendering.Core.vtkLight,
            LineSource: vtk.Filters.Sources.vtkLineSource,
            LookupTable: vtk.Common.Core.vtkLookupTable,
            macro: vtk.macro,
            Mapper: vtk.Rendering.Core.vtkMapper,
            OpenGLRenderWindow: vtk.Rendering.OpenGL.vtkRenderWindow,
            OrientationMarkerWidget: vtk.Interaction.Widgets.vtkOrientationMarkerWidget,
            OutlineFilter: vtk.Filters.General.vtkOutlineFilter,
            PiecewiseFunction: vtk.Common.DataModel.vtkPiecewiseFunction,
            PixelSpaceCallbackMapper: vtk.Rendering.Core.vtkPixelSpaceCallbackMapper,
            PlaneSource: vtk.Filters.Sources.vtkPlaneSource,
            PointSource: vtk.Filters.Sources.vtkPointSource,
            PolyData: vtk.Common.DataModel.vtkPolyData,
            Property: vtk.Rendering.Core.vtkProperty,
            Renderer: vtk.Rendering.Core.vtkRenderer,
            RenderWindow: vtk.Rendering.Core.vtkRenderWindow,
            RenderWindowInteractor: vtk.Rendering.Core.vtkRenderWindowInteractor,
            SphereMapper: vtk.Rendering.Core.vtkSphereMapper,
            SynchronizableRenderWindow: vtk.Rendering.Misc.vtkSynchronizableRenderWindow,
            Texture: vtk.Rendering.Core.vtkTexture,
            Volume: vtk.Rendering.Core.vtkVolume,
            VolumeController: vtk.Interaction.UI.vtkVolumeController,
            VolumeMapper: vtk.Rendering.Core.vtkVolumeMapper,
            VolumeProperty: vtk.Rendering.Core.vtkVolumeProperty,
            WidgetManager: vtk.Widgets.Core.vtkWidgetManager,
        });
        const { vtkObjectManager } = exports.vtkns.SynchronizableRenderWindow;
        vtkObjectManager.setTypeMapping("vtkVolumeMapper", exports.vtkns.VolumeMapper.newInstance, vtkObjectManager.oneTimeGenericUpdater);
        vtkObjectManager.setTypeMapping("vtkSmartVolumeMapper", exports.vtkns.VolumeMapper.newInstance, vtkObjectManager.oneTimeGenericUpdater);
        vtkObjectManager.setTypeMapping("vtkFollower", exports.vtkns.Follower.newInstance, vtkObjectManager.genericUpdater);
        vtkObjectManager.setTypeMapping("vtkOpenGLGlyph3DMapper", exports.vtkns.Glyph3DMapper.newInstance, vtkObjectManager.genericUpdater);
    }
    exports.setup_vtkns = setup_vtkns;
    if (window.vtk) {
        setup_vtkns();
    }
    exports.Interpolation = (0, kinds_1.Enum)("fast_linear", "linear", "nearest");
    function applyStyle(el, style) {
        Object.keys(style).forEach((key) => {
            el.style[key] = style[key];
        });
    }
    exports.applyStyle = applyStyle;
    function hexToRGB(color) {
        return [
            parseInt(color.slice(1, 3), 16) / 255,
            parseInt(color.slice(3, 5), 16) / 255,
            parseInt(color.slice(5, 7), 16) / 255,
        ];
    }
    exports.hexToRGB = hexToRGB;
    function valToHex(val) {
        const hex = Math.min(Math.max(Math.round(val), 0), 255).toString(16);
        return hex.length == 2 ? hex : `0${hex}`;
    }
    function rgbToHex(r, g, b) {
        return `#${valToHex(r)}${valToHex(g)}${valToHex(b)}`;
    }
    exports.rgbToHex = rgbToHex;
    function vtkLutToMapper(vtk_lut) {
        //For the moment only linear colormapper are handle
        const { scale, nodes } = vtk_lut.get("scale", "nodes");
        if (scale !== exports.vtkns.ColorTransferFunction.Scale.LINEAR) {
            throw new Error("Error transfer function scale not handle");
        }
        const x = nodes.map((a) => a.x);
        const low = Math.min(...x);
        const high = Math.max(...x);
        const vals = (0, array_1.linspace)(low, high, 255);
        const rgb = [0, 0, 0];
        const palette = vals.map((val) => {
            vtk_lut.getColor(val, rgb);
            return rgbToHex(rgb[0] * 255, rgb[1] * 255, rgb[2] * 255);
        });
        return { low, high, palette };
    }
    exports.vtkLutToMapper = vtkLutToMapper;
    function utf8ToAB(utf8_str) {
        const buf = new ArrayBuffer(utf8_str.length); // 2 bytes for each char
        const bufView = new Uint8Array(buf);
        for (let i = 0, strLen = utf8_str.length; i < strLen; i++) {
            bufView[i] = utf8_str.charCodeAt(i);
        }
        return buf;
    }
    function data2VTKImageData(data) {
        const source = exports.vtkns.ImageData.newInstance({
            spacing: data.spacing,
        });
        source.setDimensions(data.dims);
        source.setOrigin(data.origin != null ? data.origin : data.dims.map((v) => v / 2));
        const dataArray = exports.vtkns.DataArray.newInstance({
            name: "scalars",
            numberOfComponents: 1,
            values: new exports.ARRAY_TYPES[data.dtype](utf8ToAB(atob(data.buffer))),
        });
        source.getPointData().setScalars(dataArray);
        return source;
    }
    exports.data2VTKImageData = data2VTKImageData;
    function majorAxis(vec3, idxA, idxB) {
        const axis = [0, 0, 0];
        const idx = Math.abs(vec3[idxA]) > Math.abs(vec3[idxB]) ? idxA : idxB;
        const value = vec3[idx] > 0 ? 1 : -1;
        axis[idx] = value;
        return axis;
    }
    exports.majorAxis = majorAxis;
    function cartesian_product(...arrays) {
        return arrays.reduce((acc, curr) => {
            return [...acc].flatMap((c) => curr.map((n) => [].concat(c, n)));
        });
    }
    exports.cartesian_product = cartesian_product;
},
"b1d68776a9": /* models/vtk/vtkcolorbar.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const mappers_1 = require("@bokehjs/models/mappers");
    const array_1 = require("@bokehjs/core/util/array");
    class VTKColorBar {
        constructor(parent, mapper, options = {}) {
            this.parent = parent;
            this.mapper = mapper;
            this.options = options;
            if (!options.ticksNum) {
                options.ticksNum = 5;
            }
            if (!options.fontFamily) {
                options.fontFamily = "Arial";
            }
            if (!options.fontSize) {
                options.fontSize = "12px";
            }
            if (!options.ticksSize) {
                options.ticksSize = 2;
            }
            this.canvas = document.createElement("canvas");
            this.canvas.style.width = "100%";
            this.parent.appendChild(this.canvas);
            this.ctx = this.canvas.getContext("2d");
            this.ctx.font = `${this.options.fontSize} ${this.options.fontFamily}`;
            this.ctx.lineWidth = options.ticksSize;
            if (!options.height) {
                options.height = `${(this.font_height + 1) * 4}px`; //title/ticks/colorbar
            }
            this.canvas.style.height = options.height;
            this.draw_colorbar();
        }
        get values() {
            const { min, max } = this.mapper.metrics;
            return (0, array_1.linspace)(min, max, this.options.ticksNum);
        }
        get ticks() {
            return this.values.map((v) => v.toExponential(3));
        }
        get title() {
            return this.mapper.name ?? "scalars";
        }
        get font_height() {
            let font_height = 0;
            this.values.forEach((val) => {
                const { actualBoundingBoxAscent, actualBoundingBoxDescent, } = this.ctx.measureText(`${val}`);
                const height = actualBoundingBoxAscent + actualBoundingBoxDescent;
                if (font_height < height) {
                    font_height = height;
                }
            });
            return font_height;
        }
        draw_colorbar() {
            this.canvas.width = this.canvas.clientWidth;
            this.canvas.height = this.canvas.clientHeight;
            const { palette } = this.mapper;
            this.ctx.font = `${this.options.fontSize} ${this.options.fontFamily}`;
            const font_height = this.font_height;
            this.ctx.save();
            //colorbar
            const image = document.createElement("canvas");
            const h = 1;
            const w = palette.length;
            image.width = w;
            image.height = h;
            const image_ctx = image.getContext("2d");
            const image_data = image_ctx.getImageData(0, 0, w, h);
            const cmap = new mappers_1.LinearColorMapper({ palette }).rgba_mapper;
            const buf8 = cmap.v_compute((0, array_1.range)(0, palette.length));
            image_data.data.set(buf8);
            image_ctx.putImageData(image_data, 0, 0);
            this.ctx.drawImage(image, 0, 2 * (this.font_height + 1) + 1, this.canvas.width, this.canvas.height);
            this.ctx.restore();
            this.ctx.save();
            //title
            this.ctx.textAlign = "center";
            this.ctx.fillText(this.title, this.canvas.width / 2, font_height + 1);
            this.ctx.restore();
            this.ctx.save();
            //ticks
            const tick_x_positions = (0, array_1.linspace)(0, this.canvas.width, 5);
            tick_x_positions.forEach((xpos, idx) => {
                let xpos_tick = xpos;
                if (idx == 0) {
                    xpos_tick = xpos + Math.ceil(this.ctx.lineWidth / 2);
                    this.ctx.textAlign = "left";
                }
                else if (idx == tick_x_positions.length - 1) {
                    xpos_tick = xpos - Math.ceil(this.ctx.lineWidth / 2);
                    this.ctx.textAlign = "right";
                }
                else {
                    this.ctx.textAlign = "center";
                }
                this.ctx.moveTo(xpos_tick, 2 * (font_height + 1));
                this.ctx.lineTo(xpos_tick, 2 * (font_height + 1) + 5);
                this.ctx.stroke();
                this.ctx.fillText(`${this.ticks[idx]}`, xpos, 2 * (font_height + 1));
            });
            this.ctx.restore();
        }
    }
    exports.VTKColorBar = VTKColorBar;
    VTKColorBar.__name__ = "VTKColorBar";
},
"0379dcf1cd": /* models/vtk/vtkaxes.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const model_1 = require("@bokehjs/model");
    const gl_matrix_1 = require("2f3fd5db07") /* gl-matrix */;
    const util_1 = require("df9946ff52") /* ./util */;
    class VTKAxes extends model_1.Model {
        constructor(attrs) {
            super(attrs);
        }
        get xticks() {
            if (this.xticker) {
                return this.xticker.ticks;
            }
            else {
                return [];
            }
        }
        get yticks() {
            if (this.yticker) {
                return this.yticker.ticks;
            }
            else {
                return [];
            }
        }
        get zticks() {
            if (this.zticker) {
                return this.zticker.ticks;
            }
            else {
                return [];
            }
        }
        get xlabels() {
            return this.xticker?.labels
                ? this.xticker.labels
                : this.xticks.map((elem) => elem.toFixed(this.digits));
        }
        get ylabels() {
            return this.yticker?.labels
                ? this.yticker.labels
                : this.yticks.map((elem) => elem.toFixed(this.digits));
        }
        get zlabels() {
            return this.zticker?.labels
                ? this.zticker.labels
                : this.zticks.map((elem) => elem.toFixed(this.digits));
        }
        _make_grid_lines(n, m, offset) {
            const out = [];
            for (let i = 0; i < n - 1; i++) {
                for (let j = 0; j < m - 1; j++) {
                    const v0 = i * m + j + offset;
                    const v1 = i * m + j + 1 + offset;
                    const v2 = (i + 1) * m + j + 1 + offset;
                    const v3 = (i + 1) * m + j + offset;
                    const line = [5, v0, v1, v2, v3, v0];
                    out.push(line);
                }
            }
            return out;
        }
        _create_grid_axes() {
            const pts = [];
            pts.push((0, util_1.cartesian_product)(this.xticks, this.yticks, [this.origin[2]])); //xy
            pts.push((0, util_1.cartesian_product)([this.origin[0]], this.yticks, this.zticks)); //yz
            pts.push((0, util_1.cartesian_product)(this.xticks, [this.origin[1]], this.zticks)); //xz
            const polys = [];
            let offset = 0;
            polys.push(this._make_grid_lines(this.xticks.length, this.yticks.length, offset)); //xy
            offset += this.xticks.length * this.yticks.length;
            polys.push(this._make_grid_lines(this.yticks.length, this.zticks.length, offset)); //yz
            offset += this.yticks.length * this.zticks.length;
            polys.push(this._make_grid_lines(this.xticks.length, this.zticks.length, offset)); //xz
            const gridPolyData = window.vtk({
                vtkClass: "vtkPolyData",
                points: {
                    vtkClass: "vtkPoints",
                    dataType: "Float32Array",
                    numberOfComponents: 3,
                    values: pts.flat(2),
                },
                lines: {
                    vtkClass: "vtkCellArray",
                    dataType: "Uint32Array",
                    values: polys.flat(2),
                },
            });
            const gridMapper = util_1.vtkns.Mapper.newInstance();
            const gridActor = util_1.vtkns.Actor.newInstance();
            gridMapper.setInputData(gridPolyData);
            gridActor.setMapper(gridMapper);
            gridActor.getProperty().setOpacity(this.grid_opacity);
            gridActor.setVisibility(this.show_grid);
            return gridActor;
        }
        create_axes(canvas) {
            if (this.origin == null) {
                return { psActor: null, axesActor: null, gridActor: null };
            }
            const points = [this.xticks, this.yticks, this.zticks].map((arr, axis) => {
                let coords = null;
                switch (axis) {
                    case 0:
                        coords = (0, util_1.cartesian_product)(arr, [this.origin[1]], [this.origin[2]]);
                        break;
                    case 1:
                        coords = (0, util_1.cartesian_product)([this.origin[0]], arr, [this.origin[2]]);
                        break;
                    case 2:
                        coords = (0, util_1.cartesian_product)([this.origin[0]], [this.origin[1]], arr);
                        break;
                }
                return coords;
            }).flat(2);
            const axesPolyData = window.vtk({
                vtkClass: "vtkPolyData",
                points: {
                    vtkClass: "vtkPoints",
                    dataType: "Float32Array",
                    numberOfComponents: 3,
                    values: points,
                },
                lines: {
                    vtkClass: "vtkCellArray",
                    dataType: "Uint32Array",
                    values: [
                        2,
                        0,
                        this.xticks.length - 1,
                        2,
                        this.xticks.length,
                        this.xticks.length + this.yticks.length - 1,
                        2,
                        this.xticks.length + this.yticks.length,
                        this.xticks.length + this.yticks.length + this.zticks.length - 1,
                    ],
                },
            });
            const psMapper = util_1.vtkns.PixelSpaceCallbackMapper.newInstance();
            psMapper.setInputData(axesPolyData);
            psMapper.setUseZValues(true);
            psMapper.setCallback((coordsList, camera, aspect) => {
                const textCtx = canvas.getContext("2d");
                if (textCtx) {
                    const dims = {
                        height: canvas.clientHeight * window.devicePixelRatio,
                        width: canvas.clientWidth * window.devicePixelRatio,
                    };
                    const dataPoints = psMapper.getInputData().getPoints();
                    const viewMatrix = camera.getViewMatrix();
                    gl_matrix_1.mat4.transpose(viewMatrix, viewMatrix);
                    const projMatrix = camera.getProjectionMatrix(aspect, -1, 1);
                    gl_matrix_1.mat4.transpose(projMatrix, projMatrix);
                    textCtx.clearRect(0, 0, dims.width, dims.height);
                    coordsList.forEach((xy, idx) => {
                        const pdPoint = dataPoints.getPoint(idx);
                        const vc = gl_matrix_1.vec3.fromValues(pdPoint[0], pdPoint[1], pdPoint[2]);
                        gl_matrix_1.vec3.transformMat4(vc, vc, viewMatrix);
                        vc[2] += 0.05; // sensibility
                        gl_matrix_1.vec3.transformMat4(vc, vc, projMatrix);
                        if (vc[2] - 0.001 < xy[3]) {
                            textCtx.font = "30px serif";
                            textCtx.textAlign = "center";
                            textCtx.textBaseline = "alphabetic";
                            textCtx.fillText(".", xy[0], dims.height - xy[1] + 2);
                            textCtx.font = `${this.fontsize * window.devicePixelRatio}px serif`;
                            textCtx.textAlign = "right";
                            textCtx.textBaseline = "top";
                            let label;
                            if (idx < this.xticks.length) {
                                label = this.xlabels[idx];
                            }
                            else if (idx >= this.xticks.length &&
                                idx < this.xticks.length + this.yticks.length) {
                                label = this.ylabels[idx - this.xticks.length];
                            }
                            else {
                                label = this.zlabels[idx - (this.xticks.length + this.yticks.length)];
                            }
                            textCtx.fillText(`${label}`, xy[0], dims.height - xy[1]);
                        }
                    });
                }
            });
            const psActor = util_1.vtkns.Actor.newInstance(); //PixelSpace
            psActor.setMapper(psMapper);
            const axesMapper = util_1.vtkns.Mapper.newInstance();
            axesMapper.setInputData(axesPolyData);
            const axesActor = util_1.vtkns.Actor.newInstance();
            axesActor.setMapper(axesMapper);
            axesActor.getProperty().setOpacity(this.axes_opacity);
            const gridActor = this._create_grid_axes();
            return { psActor, axesActor, gridActor };
        }
    }
    exports.VTKAxes = VTKAxes;
    _a = VTKAxes;
    VTKAxes.__name__ = "VTKAxes";
    VTKAxes.__module__ = "panel.models.vtk";
    (() => {
        _a.define(({ Any, Array, Boolean, Number }) => ({
            origin: [Array(Number), [0, 0, 0]],
            xticker: [Any, null],
            yticker: [Any, null],
            zticker: [Any, null],
            digits: [Number, 1],
            show_grid: [Boolean, true],
            grid_opacity: [Number, 0.1],
            axes_opacity: [Number, 1],
            fontsize: [Number, 12],
        }));
    })();
},
"2f3fd5db07": /* gl-matrix/esm/index.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const glMatrix = tslib_1.__importStar(require("7d825b979e") /* ./common.js */);
    exports.glMatrix = glMatrix;
    const mat2 = tslib_1.__importStar(require("d77e165b60") /* ./mat2.js */);
    exports.mat2 = mat2;
    const mat2d = tslib_1.__importStar(require("33a5f6cb7a") /* ./mat2d.js */);
    exports.mat2d = mat2d;
    const mat3 = tslib_1.__importStar(require("a025ef02dc") /* ./mat3.js */);
    exports.mat3 = mat3;
    const mat4 = tslib_1.__importStar(require("83bad9e639") /* ./mat4.js */);
    exports.mat4 = mat4;
    const quat = tslib_1.__importStar(require("f83fe7c413") /* ./quat.js */);
    exports.quat = quat;
    const quat2 = tslib_1.__importStar(require("fb9294db61") /* ./quat2.js */);
    exports.quat2 = quat2;
    const vec2 = tslib_1.__importStar(require("58c71a9bd3") /* ./vec2.js */);
    exports.vec2 = vec2;
    const vec3 = tslib_1.__importStar(require("63eddc5433") /* ./vec3.js */);
    exports.vec3 = vec3;
    const vec4 = tslib_1.__importStar(require("11562bccc5") /* ./vec4.js */);
    exports.vec4 = vec4;
},
"7d825b979e": /* gl-matrix/esm/common.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    /**
     * Common utilities
     * @module glMatrix
     */
    // Configuration Constants
    exports.EPSILON = 0.000001;
    exports.ARRAY_TYPE = typeof Float32Array !== 'undefined' ? Float32Array : Array;
    exports.RANDOM = Math.random;
    /**
     * Sets the type of array used when creating new vectors and matrices
     *
     * @param {Float32ArrayConstructor | ArrayConstructor} type Array type, such as Float32Array or Array
     */
    function setMatrixArrayType(type) {
        exports.ARRAY_TYPE = type;
    }
    exports.setMatrixArrayType = setMatrixArrayType;
    var degree = Math.PI / 180;
    /**
     * Convert Degree To Radian
     *
     * @param {Number} a Angle in Degrees
     */
    function toRadian(a) {
        return a * degree;
    }
    exports.toRadian = toRadian;
    /**
     * Tests whether or not the arguments have approximately the same value, within an absolute
     * or relative tolerance of glMatrix.EPSILON (an absolute tolerance is used for values less
     * than or equal to 1.0, and a relative tolerance is used for larger values)
     *
     * @param {Number} a The first number to test.
     * @param {Number} b The second number to test.
     * @returns {Boolean} True if the numbers are approximately equal, false otherwise.
     */
    function equals(a, b) {
        return Math.abs(a - b) <= exports.EPSILON * Math.max(1.0, Math.abs(a), Math.abs(b));
    }
    exports.equals = equals;
    if (!Math.hypot)
        Math.hypot = function () {
            var y = 0, i = arguments.length;
            while (i--) {
                y += arguments[i] * arguments[i];
            }
            return Math.sqrt(y);
        };
},
"d77e165b60": /* gl-matrix/esm/mat2.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const glMatrix = tslib_1.__importStar(require("7d825b979e") /* ./common.js */);
    /**
     * 2x2 Matrix
     * @module mat2
     */
    /**
     * Creates a new identity mat2
     *
     * @returns {mat2} a new 2x2 matrix
     */
    function create() {
        var out = new glMatrix.ARRAY_TYPE(4);
        if (glMatrix.ARRAY_TYPE != Float32Array) {
            out[1] = 0;
            out[2] = 0;
        }
        out[0] = 1;
        out[3] = 1;
        return out;
    }
    exports.create = create;
    /**
     * Creates a new mat2 initialized with values from an existing matrix
     *
     * @param {ReadonlyMat2} a matrix to clone
     * @returns {mat2} a new 2x2 matrix
     */
    function clone(a) {
        var out = new glMatrix.ARRAY_TYPE(4);
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[3];
        return out;
    }
    exports.clone = clone;
    /**
     * Copy the values from one mat2 to another
     *
     * @param {mat2} out the receiving matrix
     * @param {ReadonlyMat2} a the source matrix
     * @returns {mat2} out
     */
    function copy(out, a) {
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[3];
        return out;
    }
    exports.copy = copy;
    /**
     * Set a mat2 to the identity matrix
     *
     * @param {mat2} out the receiving matrix
     * @returns {mat2} out
     */
    function identity(out) {
        out[0] = 1;
        out[1] = 0;
        out[2] = 0;
        out[3] = 1;
        return out;
    }
    exports.identity = identity;
    /**
     * Create a new mat2 with the given values
     *
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m10 Component in column 1, row 0 position (index 2)
     * @param {Number} m11 Component in column 1, row 1 position (index 3)
     * @returns {mat2} out A new 2x2 matrix
     */
    function fromValues(m00, m01, m10, m11) {
        var out = new glMatrix.ARRAY_TYPE(4);
        out[0] = m00;
        out[1] = m01;
        out[2] = m10;
        out[3] = m11;
        return out;
    }
    exports.fromValues = fromValues;
    /**
     * Set the components of a mat2 to the given values
     *
     * @param {mat2} out the receiving matrix
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m10 Component in column 1, row 0 position (index 2)
     * @param {Number} m11 Component in column 1, row 1 position (index 3)
     * @returns {mat2} out
     */
    function set(out, m00, m01, m10, m11) {
        out[0] = m00;
        out[1] = m01;
        out[2] = m10;
        out[3] = m11;
        return out;
    }
    exports.set = set;
    /**
     * Transpose the values of a mat2
     *
     * @param {mat2} out the receiving matrix
     * @param {ReadonlyMat2} a the source matrix
     * @returns {mat2} out
     */
    function transpose(out, a) {
        // If we are transposing ourselves we can skip a few steps but have to cache
        // some values
        if (out === a) {
            var a1 = a[1];
            out[1] = a[2];
            out[2] = a1;
        }
        else {
            out[0] = a[0];
            out[1] = a[2];
            out[2] = a[1];
            out[3] = a[3];
        }
        return out;
    }
    exports.transpose = transpose;
    /**
     * Inverts a mat2
     *
     * @param {mat2} out the receiving matrix
     * @param {ReadonlyMat2} a the source matrix
     * @returns {mat2} out
     */
    function invert(out, a) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3]; // Calculate the determinant
        var det = a0 * a3 - a2 * a1;
        if (!det) {
            return null;
        }
        det = 1.0 / det;
        out[0] = a3 * det;
        out[1] = -a1 * det;
        out[2] = -a2 * det;
        out[3] = a0 * det;
        return out;
    }
    exports.invert = invert;
    /**
     * Calculates the adjugate of a mat2
     *
     * @param {mat2} out the receiving matrix
     * @param {ReadonlyMat2} a the source matrix
     * @returns {mat2} out
     */
    function adjoint(out, a) {
        // Caching this value is nessecary if out == a
        var a0 = a[0];
        out[0] = a[3];
        out[1] = -a[1];
        out[2] = -a[2];
        out[3] = a0;
        return out;
    }
    exports.adjoint = adjoint;
    /**
     * Calculates the determinant of a mat2
     *
     * @param {ReadonlyMat2} a the source matrix
     * @returns {Number} determinant of a
     */
    function determinant(a) {
        return a[0] * a[3] - a[2] * a[1];
    }
    exports.determinant = determinant;
    /**
     * Multiplies two mat2's
     *
     * @param {mat2} out the receiving matrix
     * @param {ReadonlyMat2} a the first operand
     * @param {ReadonlyMat2} b the second operand
     * @returns {mat2} out
     */
    function multiply(out, a, b) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3];
        var b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3];
        out[0] = a0 * b0 + a2 * b1;
        out[1] = a1 * b0 + a3 * b1;
        out[2] = a0 * b2 + a2 * b3;
        out[3] = a1 * b2 + a3 * b3;
        return out;
    }
    exports.multiply = multiply;
    /**
     * Rotates a mat2 by the given angle
     *
     * @param {mat2} out the receiving matrix
     * @param {ReadonlyMat2} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat2} out
     */
    function rotate(out, a, rad) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3];
        var s = Math.sin(rad);
        var c = Math.cos(rad);
        out[0] = a0 * c + a2 * s;
        out[1] = a1 * c + a3 * s;
        out[2] = a0 * -s + a2 * c;
        out[3] = a1 * -s + a3 * c;
        return out;
    }
    exports.rotate = rotate;
    /**
     * Scales the mat2 by the dimensions in the given vec2
     *
     * @param {mat2} out the receiving matrix
     * @param {ReadonlyMat2} a the matrix to rotate
     * @param {ReadonlyVec2} v the vec2 to scale the matrix by
     * @returns {mat2} out
     **/
    function scale(out, a, v) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3];
        var v0 = v[0], v1 = v[1];
        out[0] = a0 * v0;
        out[1] = a1 * v0;
        out[2] = a2 * v1;
        out[3] = a3 * v1;
        return out;
    }
    exports.scale = scale;
    /**
     * Creates a matrix from a given angle
     * This is equivalent to (but much faster than):
     *
     *     mat2.identity(dest);
     *     mat2.rotate(dest, dest, rad);
     *
     * @param {mat2} out mat2 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat2} out
     */
    function fromRotation(out, rad) {
        var s = Math.sin(rad);
        var c = Math.cos(rad);
        out[0] = c;
        out[1] = s;
        out[2] = -s;
        out[3] = c;
        return out;
    }
    exports.fromRotation = fromRotation;
    /**
     * Creates a matrix from a vector scaling
     * This is equivalent to (but much faster than):
     *
     *     mat2.identity(dest);
     *     mat2.scale(dest, dest, vec);
     *
     * @param {mat2} out mat2 receiving operation result
     * @param {ReadonlyVec2} v Scaling vector
     * @returns {mat2} out
     */
    function fromScaling(out, v) {
        out[0] = v[0];
        out[1] = 0;
        out[2] = 0;
        out[3] = v[1];
        return out;
    }
    exports.fromScaling = fromScaling;
    /**
     * Returns a string representation of a mat2
     *
     * @param {ReadonlyMat2} a matrix to represent as a string
     * @returns {String} string representation of the matrix
     */
    function str(a) {
        return "mat2(" + a[0] + ", " + a[1] + ", " + a[2] + ", " + a[3] + ")";
    }
    exports.str = str;
    /**
     * Returns Frobenius norm of a mat2
     *
     * @param {ReadonlyMat2} a the matrix to calculate Frobenius norm of
     * @returns {Number} Frobenius norm
     */
    function frob(a) {
        return Math.hypot(a[0], a[1], a[2], a[3]);
    }
    exports.frob = frob;
    /**
     * Returns L, D and U matrices (Lower triangular, Diagonal and Upper triangular) by factorizing the input matrix
     * @param {ReadonlyMat2} L the lower triangular matrix
     * @param {ReadonlyMat2} D the diagonal matrix
     * @param {ReadonlyMat2} U the upper triangular matrix
     * @param {ReadonlyMat2} a the input matrix to factorize
     */
    function LDU(L, D, U, a) {
        L[2] = a[2] / a[0];
        U[0] = a[0];
        U[1] = a[1];
        U[3] = a[3] - L[2] * U[1];
        return [L, D, U];
    }
    exports.LDU = LDU;
    /**
     * Adds two mat2's
     *
     * @param {mat2} out the receiving matrix
     * @param {ReadonlyMat2} a the first operand
     * @param {ReadonlyMat2} b the second operand
     * @returns {mat2} out
     */
    function add(out, a, b) {
        out[0] = a[0] + b[0];
        out[1] = a[1] + b[1];
        out[2] = a[2] + b[2];
        out[3] = a[3] + b[3];
        return out;
    }
    exports.add = add;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat2} out the receiving matrix
     * @param {ReadonlyMat2} a the first operand
     * @param {ReadonlyMat2} b the second operand
     * @returns {mat2} out
     */
    function subtract(out, a, b) {
        out[0] = a[0] - b[0];
        out[1] = a[1] - b[1];
        out[2] = a[2] - b[2];
        out[3] = a[3] - b[3];
        return out;
    }
    exports.subtract = subtract;
    /**
     * Returns whether or not the matrices have exactly the same elements in the same position (when compared with ===)
     *
     * @param {ReadonlyMat2} a The first matrix.
     * @param {ReadonlyMat2} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    function exactEquals(a, b) {
        return a[0] === b[0] && a[1] === b[1] && a[2] === b[2] && a[3] === b[3];
    }
    exports.exactEquals = exactEquals;
    /**
     * Returns whether or not the matrices have approximately the same elements in the same position.
     *
     * @param {ReadonlyMat2} a The first matrix.
     * @param {ReadonlyMat2} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    function equals(a, b) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3];
        var b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3];
        return Math.abs(a0 - b0) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a0), Math.abs(b0)) && Math.abs(a1 - b1) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a1), Math.abs(b1)) && Math.abs(a2 - b2) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a2), Math.abs(b2)) && Math.abs(a3 - b3) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a3), Math.abs(b3));
    }
    exports.equals = equals;
    /**
     * Multiply each element of the matrix by a scalar.
     *
     * @param {mat2} out the receiving matrix
     * @param {ReadonlyMat2} a the matrix to scale
     * @param {Number} b amount to scale the matrix's elements by
     * @returns {mat2} out
     */
    function multiplyScalar(out, a, b) {
        out[0] = a[0] * b;
        out[1] = a[1] * b;
        out[2] = a[2] * b;
        out[3] = a[3] * b;
        return out;
    }
    exports.multiplyScalar = multiplyScalar;
    /**
     * Adds two mat2's after multiplying each element of the second operand by a scalar value.
     *
     * @param {mat2} out the receiving vector
     * @param {ReadonlyMat2} a the first operand
     * @param {ReadonlyMat2} b the second operand
     * @param {Number} scale the amount to scale b's elements by before adding
     * @returns {mat2} out
     */
    function multiplyScalarAndAdd(out, a, b, scale) {
        out[0] = a[0] + b[0] * scale;
        out[1] = a[1] + b[1] * scale;
        out[2] = a[2] + b[2] * scale;
        out[3] = a[3] + b[3] * scale;
        return out;
    }
    exports.multiplyScalarAndAdd = multiplyScalarAndAdd;
    /**
     * Alias for {@link mat2.multiply}
     * @function
     */
    exports.mul = multiply;
    /**
     * Alias for {@link mat2.subtract}
     * @function
     */
    exports.sub = subtract;
},
"33a5f6cb7a": /* gl-matrix/esm/mat2d.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const glMatrix = tslib_1.__importStar(require("7d825b979e") /* ./common.js */);
    /**
     * 2x3 Matrix
     * @module mat2d
     * @description
     * A mat2d contains six elements defined as:
     * <pre>
     * [a, b,
     *  c, d,
     *  tx, ty]
     * </pre>
     * This is a short form for the 3x3 matrix:
     * <pre>
     * [a, b, 0,
     *  c, d, 0,
     *  tx, ty, 1]
     * </pre>
     * The last column is ignored so the array is shorter and operations are faster.
     */
    /**
     * Creates a new identity mat2d
     *
     * @returns {mat2d} a new 2x3 matrix
     */
    function create() {
        var out = new glMatrix.ARRAY_TYPE(6);
        if (glMatrix.ARRAY_TYPE != Float32Array) {
            out[1] = 0;
            out[2] = 0;
            out[4] = 0;
            out[5] = 0;
        }
        out[0] = 1;
        out[3] = 1;
        return out;
    }
    exports.create = create;
    /**
     * Creates a new mat2d initialized with values from an existing matrix
     *
     * @param {ReadonlyMat2d} a matrix to clone
     * @returns {mat2d} a new 2x3 matrix
     */
    function clone(a) {
        var out = new glMatrix.ARRAY_TYPE(6);
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[3];
        out[4] = a[4];
        out[5] = a[5];
        return out;
    }
    exports.clone = clone;
    /**
     * Copy the values from one mat2d to another
     *
     * @param {mat2d} out the receiving matrix
     * @param {ReadonlyMat2d} a the source matrix
     * @returns {mat2d} out
     */
    function copy(out, a) {
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[3];
        out[4] = a[4];
        out[5] = a[5];
        return out;
    }
    exports.copy = copy;
    /**
     * Set a mat2d to the identity matrix
     *
     * @param {mat2d} out the receiving matrix
     * @returns {mat2d} out
     */
    function identity(out) {
        out[0] = 1;
        out[1] = 0;
        out[2] = 0;
        out[3] = 1;
        out[4] = 0;
        out[5] = 0;
        return out;
    }
    exports.identity = identity;
    /**
     * Create a new mat2d with the given values
     *
     * @param {Number} a Component A (index 0)
     * @param {Number} b Component B (index 1)
     * @param {Number} c Component C (index 2)
     * @param {Number} d Component D (index 3)
     * @param {Number} tx Component TX (index 4)
     * @param {Number} ty Component TY (index 5)
     * @returns {mat2d} A new mat2d
     */
    function fromValues(a, b, c, d, tx, ty) {
        var out = new glMatrix.ARRAY_TYPE(6);
        out[0] = a;
        out[1] = b;
        out[2] = c;
        out[3] = d;
        out[4] = tx;
        out[5] = ty;
        return out;
    }
    exports.fromValues = fromValues;
    /**
     * Set the components of a mat2d to the given values
     *
     * @param {mat2d} out the receiving matrix
     * @param {Number} a Component A (index 0)
     * @param {Number} b Component B (index 1)
     * @param {Number} c Component C (index 2)
     * @param {Number} d Component D (index 3)
     * @param {Number} tx Component TX (index 4)
     * @param {Number} ty Component TY (index 5)
     * @returns {mat2d} out
     */
    function set(out, a, b, c, d, tx, ty) {
        out[0] = a;
        out[1] = b;
        out[2] = c;
        out[3] = d;
        out[4] = tx;
        out[5] = ty;
        return out;
    }
    exports.set = set;
    /**
     * Inverts a mat2d
     *
     * @param {mat2d} out the receiving matrix
     * @param {ReadonlyMat2d} a the source matrix
     * @returns {mat2d} out
     */
    function invert(out, a) {
        var aa = a[0], ab = a[1], ac = a[2], ad = a[3];
        var atx = a[4], aty = a[5];
        var det = aa * ad - ab * ac;
        if (!det) {
            return null;
        }
        det = 1.0 / det;
        out[0] = ad * det;
        out[1] = -ab * det;
        out[2] = -ac * det;
        out[3] = aa * det;
        out[4] = (ac * aty - ad * atx) * det;
        out[5] = (ab * atx - aa * aty) * det;
        return out;
    }
    exports.invert = invert;
    /**
     * Calculates the determinant of a mat2d
     *
     * @param {ReadonlyMat2d} a the source matrix
     * @returns {Number} determinant of a
     */
    function determinant(a) {
        return a[0] * a[3] - a[1] * a[2];
    }
    exports.determinant = determinant;
    /**
     * Multiplies two mat2d's
     *
     * @param {mat2d} out the receiving matrix
     * @param {ReadonlyMat2d} a the first operand
     * @param {ReadonlyMat2d} b the second operand
     * @returns {mat2d} out
     */
    function multiply(out, a, b) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3], a4 = a[4], a5 = a[5];
        var b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3], b4 = b[4], b5 = b[5];
        out[0] = a0 * b0 + a2 * b1;
        out[1] = a1 * b0 + a3 * b1;
        out[2] = a0 * b2 + a2 * b3;
        out[3] = a1 * b2 + a3 * b3;
        out[4] = a0 * b4 + a2 * b5 + a4;
        out[5] = a1 * b4 + a3 * b5 + a5;
        return out;
    }
    exports.multiply = multiply;
    /**
     * Rotates a mat2d by the given angle
     *
     * @param {mat2d} out the receiving matrix
     * @param {ReadonlyMat2d} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat2d} out
     */
    function rotate(out, a, rad) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3], a4 = a[4], a5 = a[5];
        var s = Math.sin(rad);
        var c = Math.cos(rad);
        out[0] = a0 * c + a2 * s;
        out[1] = a1 * c + a3 * s;
        out[2] = a0 * -s + a2 * c;
        out[3] = a1 * -s + a3 * c;
        out[4] = a4;
        out[5] = a5;
        return out;
    }
    exports.rotate = rotate;
    /**
     * Scales the mat2d by the dimensions in the given vec2
     *
     * @param {mat2d} out the receiving matrix
     * @param {ReadonlyMat2d} a the matrix to translate
     * @param {ReadonlyVec2} v the vec2 to scale the matrix by
     * @returns {mat2d} out
     **/
    function scale(out, a, v) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3], a4 = a[4], a5 = a[5];
        var v0 = v[0], v1 = v[1];
        out[0] = a0 * v0;
        out[1] = a1 * v0;
        out[2] = a2 * v1;
        out[3] = a3 * v1;
        out[4] = a4;
        out[5] = a5;
        return out;
    }
    exports.scale = scale;
    /**
     * Translates the mat2d by the dimensions in the given vec2
     *
     * @param {mat2d} out the receiving matrix
     * @param {ReadonlyMat2d} a the matrix to translate
     * @param {ReadonlyVec2} v the vec2 to translate the matrix by
     * @returns {mat2d} out
     **/
    function translate(out, a, v) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3], a4 = a[4], a5 = a[5];
        var v0 = v[0], v1 = v[1];
        out[0] = a0;
        out[1] = a1;
        out[2] = a2;
        out[3] = a3;
        out[4] = a0 * v0 + a2 * v1 + a4;
        out[5] = a1 * v0 + a3 * v1 + a5;
        return out;
    }
    exports.translate = translate;
    /**
     * Creates a matrix from a given angle
     * This is equivalent to (but much faster than):
     *
     *     mat2d.identity(dest);
     *     mat2d.rotate(dest, dest, rad);
     *
     * @param {mat2d} out mat2d receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat2d} out
     */
    function fromRotation(out, rad) {
        var s = Math.sin(rad), c = Math.cos(rad);
        out[0] = c;
        out[1] = s;
        out[2] = -s;
        out[3] = c;
        out[4] = 0;
        out[5] = 0;
        return out;
    }
    exports.fromRotation = fromRotation;
    /**
     * Creates a matrix from a vector scaling
     * This is equivalent to (but much faster than):
     *
     *     mat2d.identity(dest);
     *     mat2d.scale(dest, dest, vec);
     *
     * @param {mat2d} out mat2d receiving operation result
     * @param {ReadonlyVec2} v Scaling vector
     * @returns {mat2d} out
     */
    function fromScaling(out, v) {
        out[0] = v[0];
        out[1] = 0;
        out[2] = 0;
        out[3] = v[1];
        out[4] = 0;
        out[5] = 0;
        return out;
    }
    exports.fromScaling = fromScaling;
    /**
     * Creates a matrix from a vector translation
     * This is equivalent to (but much faster than):
     *
     *     mat2d.identity(dest);
     *     mat2d.translate(dest, dest, vec);
     *
     * @param {mat2d} out mat2d receiving operation result
     * @param {ReadonlyVec2} v Translation vector
     * @returns {mat2d} out
     */
    function fromTranslation(out, v) {
        out[0] = 1;
        out[1] = 0;
        out[2] = 0;
        out[3] = 1;
        out[4] = v[0];
        out[5] = v[1];
        return out;
    }
    exports.fromTranslation = fromTranslation;
    /**
     * Returns a string representation of a mat2d
     *
     * @param {ReadonlyMat2d} a matrix to represent as a string
     * @returns {String} string representation of the matrix
     */
    function str(a) {
        return "mat2d(" + a[0] + ", " + a[1] + ", " + a[2] + ", " + a[3] + ", " + a[4] + ", " + a[5] + ")";
    }
    exports.str = str;
    /**
     * Returns Frobenius norm of a mat2d
     *
     * @param {ReadonlyMat2d} a the matrix to calculate Frobenius norm of
     * @returns {Number} Frobenius norm
     */
    function frob(a) {
        return Math.hypot(a[0], a[1], a[2], a[3], a[4], a[5], 1);
    }
    exports.frob = frob;
    /**
     * Adds two mat2d's
     *
     * @param {mat2d} out the receiving matrix
     * @param {ReadonlyMat2d} a the first operand
     * @param {ReadonlyMat2d} b the second operand
     * @returns {mat2d} out
     */
    function add(out, a, b) {
        out[0] = a[0] + b[0];
        out[1] = a[1] + b[1];
        out[2] = a[2] + b[2];
        out[3] = a[3] + b[3];
        out[4] = a[4] + b[4];
        out[5] = a[5] + b[5];
        return out;
    }
    exports.add = add;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat2d} out the receiving matrix
     * @param {ReadonlyMat2d} a the first operand
     * @param {ReadonlyMat2d} b the second operand
     * @returns {mat2d} out
     */
    function subtract(out, a, b) {
        out[0] = a[0] - b[0];
        out[1] = a[1] - b[1];
        out[2] = a[2] - b[2];
        out[3] = a[3] - b[3];
        out[4] = a[4] - b[4];
        out[5] = a[5] - b[5];
        return out;
    }
    exports.subtract = subtract;
    /**
     * Multiply each element of the matrix by a scalar.
     *
     * @param {mat2d} out the receiving matrix
     * @param {ReadonlyMat2d} a the matrix to scale
     * @param {Number} b amount to scale the matrix's elements by
     * @returns {mat2d} out
     */
    function multiplyScalar(out, a, b) {
        out[0] = a[0] * b;
        out[1] = a[1] * b;
        out[2] = a[2] * b;
        out[3] = a[3] * b;
        out[4] = a[4] * b;
        out[5] = a[5] * b;
        return out;
    }
    exports.multiplyScalar = multiplyScalar;
    /**
     * Adds two mat2d's after multiplying each element of the second operand by a scalar value.
     *
     * @param {mat2d} out the receiving vector
     * @param {ReadonlyMat2d} a the first operand
     * @param {ReadonlyMat2d} b the second operand
     * @param {Number} scale the amount to scale b's elements by before adding
     * @returns {mat2d} out
     */
    function multiplyScalarAndAdd(out, a, b, scale) {
        out[0] = a[0] + b[0] * scale;
        out[1] = a[1] + b[1] * scale;
        out[2] = a[2] + b[2] * scale;
        out[3] = a[3] + b[3] * scale;
        out[4] = a[4] + b[4] * scale;
        out[5] = a[5] + b[5] * scale;
        return out;
    }
    exports.multiplyScalarAndAdd = multiplyScalarAndAdd;
    /**
     * Returns whether or not the matrices have exactly the same elements in the same position (when compared with ===)
     *
     * @param {ReadonlyMat2d} a The first matrix.
     * @param {ReadonlyMat2d} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    function exactEquals(a, b) {
        return a[0] === b[0] && a[1] === b[1] && a[2] === b[2] && a[3] === b[3] && a[4] === b[4] && a[5] === b[5];
    }
    exports.exactEquals = exactEquals;
    /**
     * Returns whether or not the matrices have approximately the same elements in the same position.
     *
     * @param {ReadonlyMat2d} a The first matrix.
     * @param {ReadonlyMat2d} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    function equals(a, b) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3], a4 = a[4], a5 = a[5];
        var b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3], b4 = b[4], b5 = b[5];
        return Math.abs(a0 - b0) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a0), Math.abs(b0)) && Math.abs(a1 - b1) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a1), Math.abs(b1)) && Math.abs(a2 - b2) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a2), Math.abs(b2)) && Math.abs(a3 - b3) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a3), Math.abs(b3)) && Math.abs(a4 - b4) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a4), Math.abs(b4)) && Math.abs(a5 - b5) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a5), Math.abs(b5));
    }
    exports.equals = equals;
    /**
     * Alias for {@link mat2d.multiply}
     * @function
     */
    exports.mul = multiply;
    /**
     * Alias for {@link mat2d.subtract}
     * @function
     */
    exports.sub = subtract;
},
"a025ef02dc": /* gl-matrix/esm/mat3.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const glMatrix = tslib_1.__importStar(require("7d825b979e") /* ./common.js */);
    /**
     * 3x3 Matrix
     * @module mat3
     */
    /**
     * Creates a new identity mat3
     *
     * @returns {mat3} a new 3x3 matrix
     */
    function create() {
        var out = new glMatrix.ARRAY_TYPE(9);
        if (glMatrix.ARRAY_TYPE != Float32Array) {
            out[1] = 0;
            out[2] = 0;
            out[3] = 0;
            out[5] = 0;
            out[6] = 0;
            out[7] = 0;
        }
        out[0] = 1;
        out[4] = 1;
        out[8] = 1;
        return out;
    }
    exports.create = create;
    /**
     * Copies the upper-left 3x3 values into the given mat3.
     *
     * @param {mat3} out the receiving 3x3 matrix
     * @param {ReadonlyMat4} a   the source 4x4 matrix
     * @returns {mat3} out
     */
    function fromMat4(out, a) {
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[4];
        out[4] = a[5];
        out[5] = a[6];
        out[6] = a[8];
        out[7] = a[9];
        out[8] = a[10];
        return out;
    }
    exports.fromMat4 = fromMat4;
    /**
     * Creates a new mat3 initialized with values from an existing matrix
     *
     * @param {ReadonlyMat3} a matrix to clone
     * @returns {mat3} a new 3x3 matrix
     */
    function clone(a) {
        var out = new glMatrix.ARRAY_TYPE(9);
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[3];
        out[4] = a[4];
        out[5] = a[5];
        out[6] = a[6];
        out[7] = a[7];
        out[8] = a[8];
        return out;
    }
    exports.clone = clone;
    /**
     * Copy the values from one mat3 to another
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat3} a the source matrix
     * @returns {mat3} out
     */
    function copy(out, a) {
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[3];
        out[4] = a[4];
        out[5] = a[5];
        out[6] = a[6];
        out[7] = a[7];
        out[8] = a[8];
        return out;
    }
    exports.copy = copy;
    /**
     * Create a new mat3 with the given values
     *
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m02 Component in column 0, row 2 position (index 2)
     * @param {Number} m10 Component in column 1, row 0 position (index 3)
     * @param {Number} m11 Component in column 1, row 1 position (index 4)
     * @param {Number} m12 Component in column 1, row 2 position (index 5)
     * @param {Number} m20 Component in column 2, row 0 position (index 6)
     * @param {Number} m21 Component in column 2, row 1 position (index 7)
     * @param {Number} m22 Component in column 2, row 2 position (index 8)
     * @returns {mat3} A new mat3
     */
    function fromValues(m00, m01, m02, m10, m11, m12, m20, m21, m22) {
        var out = new glMatrix.ARRAY_TYPE(9);
        out[0] = m00;
        out[1] = m01;
        out[2] = m02;
        out[3] = m10;
        out[4] = m11;
        out[5] = m12;
        out[6] = m20;
        out[7] = m21;
        out[8] = m22;
        return out;
    }
    exports.fromValues = fromValues;
    /**
     * Set the components of a mat3 to the given values
     *
     * @param {mat3} out the receiving matrix
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m02 Component in column 0, row 2 position (index 2)
     * @param {Number} m10 Component in column 1, row 0 position (index 3)
     * @param {Number} m11 Component in column 1, row 1 position (index 4)
     * @param {Number} m12 Component in column 1, row 2 position (index 5)
     * @param {Number} m20 Component in column 2, row 0 position (index 6)
     * @param {Number} m21 Component in column 2, row 1 position (index 7)
     * @param {Number} m22 Component in column 2, row 2 position (index 8)
     * @returns {mat3} out
     */
    function set(out, m00, m01, m02, m10, m11, m12, m20, m21, m22) {
        out[0] = m00;
        out[1] = m01;
        out[2] = m02;
        out[3] = m10;
        out[4] = m11;
        out[5] = m12;
        out[6] = m20;
        out[7] = m21;
        out[8] = m22;
        return out;
    }
    exports.set = set;
    /**
     * Set a mat3 to the identity matrix
     *
     * @param {mat3} out the receiving matrix
     * @returns {mat3} out
     */
    function identity(out) {
        out[0] = 1;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 1;
        out[5] = 0;
        out[6] = 0;
        out[7] = 0;
        out[8] = 1;
        return out;
    }
    exports.identity = identity;
    /**
     * Transpose the values of a mat3
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat3} a the source matrix
     * @returns {mat3} out
     */
    function transpose(out, a) {
        // If we are transposing ourselves we can skip a few steps but have to cache some values
        if (out === a) {
            var a01 = a[1], a02 = a[2], a12 = a[5];
            out[1] = a[3];
            out[2] = a[6];
            out[3] = a01;
            out[5] = a[7];
            out[6] = a02;
            out[7] = a12;
        }
        else {
            out[0] = a[0];
            out[1] = a[3];
            out[2] = a[6];
            out[3] = a[1];
            out[4] = a[4];
            out[5] = a[7];
            out[6] = a[2];
            out[7] = a[5];
            out[8] = a[8];
        }
        return out;
    }
    exports.transpose = transpose;
    /**
     * Inverts a mat3
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat3} a the source matrix
     * @returns {mat3} out
     */
    function invert(out, a) {
        var a00 = a[0], a01 = a[1], a02 = a[2];
        var a10 = a[3], a11 = a[4], a12 = a[5];
        var a20 = a[6], a21 = a[7], a22 = a[8];
        var b01 = a22 * a11 - a12 * a21;
        var b11 = -a22 * a10 + a12 * a20;
        var b21 = a21 * a10 - a11 * a20; // Calculate the determinant
        var det = a00 * b01 + a01 * b11 + a02 * b21;
        if (!det) {
            return null;
        }
        det = 1.0 / det;
        out[0] = b01 * det;
        out[1] = (-a22 * a01 + a02 * a21) * det;
        out[2] = (a12 * a01 - a02 * a11) * det;
        out[3] = b11 * det;
        out[4] = (a22 * a00 - a02 * a20) * det;
        out[5] = (-a12 * a00 + a02 * a10) * det;
        out[6] = b21 * det;
        out[7] = (-a21 * a00 + a01 * a20) * det;
        out[8] = (a11 * a00 - a01 * a10) * det;
        return out;
    }
    exports.invert = invert;
    /**
     * Calculates the adjugate of a mat3
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat3} a the source matrix
     * @returns {mat3} out
     */
    function adjoint(out, a) {
        var a00 = a[0], a01 = a[1], a02 = a[2];
        var a10 = a[3], a11 = a[4], a12 = a[5];
        var a20 = a[6], a21 = a[7], a22 = a[8];
        out[0] = a11 * a22 - a12 * a21;
        out[1] = a02 * a21 - a01 * a22;
        out[2] = a01 * a12 - a02 * a11;
        out[3] = a12 * a20 - a10 * a22;
        out[4] = a00 * a22 - a02 * a20;
        out[5] = a02 * a10 - a00 * a12;
        out[6] = a10 * a21 - a11 * a20;
        out[7] = a01 * a20 - a00 * a21;
        out[8] = a00 * a11 - a01 * a10;
        return out;
    }
    exports.adjoint = adjoint;
    /**
     * Calculates the determinant of a mat3
     *
     * @param {ReadonlyMat3} a the source matrix
     * @returns {Number} determinant of a
     */
    function determinant(a) {
        var a00 = a[0], a01 = a[1], a02 = a[2];
        var a10 = a[3], a11 = a[4], a12 = a[5];
        var a20 = a[6], a21 = a[7], a22 = a[8];
        return a00 * (a22 * a11 - a12 * a21) + a01 * (-a22 * a10 + a12 * a20) + a02 * (a21 * a10 - a11 * a20);
    }
    exports.determinant = determinant;
    /**
     * Multiplies two mat3's
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat3} a the first operand
     * @param {ReadonlyMat3} b the second operand
     * @returns {mat3} out
     */
    function multiply(out, a, b) {
        var a00 = a[0], a01 = a[1], a02 = a[2];
        var a10 = a[3], a11 = a[4], a12 = a[5];
        var a20 = a[6], a21 = a[7], a22 = a[8];
        var b00 = b[0], b01 = b[1], b02 = b[2];
        var b10 = b[3], b11 = b[4], b12 = b[5];
        var b20 = b[6], b21 = b[7], b22 = b[8];
        out[0] = b00 * a00 + b01 * a10 + b02 * a20;
        out[1] = b00 * a01 + b01 * a11 + b02 * a21;
        out[2] = b00 * a02 + b01 * a12 + b02 * a22;
        out[3] = b10 * a00 + b11 * a10 + b12 * a20;
        out[4] = b10 * a01 + b11 * a11 + b12 * a21;
        out[5] = b10 * a02 + b11 * a12 + b12 * a22;
        out[6] = b20 * a00 + b21 * a10 + b22 * a20;
        out[7] = b20 * a01 + b21 * a11 + b22 * a21;
        out[8] = b20 * a02 + b21 * a12 + b22 * a22;
        return out;
    }
    exports.multiply = multiply;
    /**
     * Translate a mat3 by the given vector
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat3} a the matrix to translate
     * @param {ReadonlyVec2} v vector to translate by
     * @returns {mat3} out
     */
    function translate(out, a, v) {
        var a00 = a[0], a01 = a[1], a02 = a[2], a10 = a[3], a11 = a[4], a12 = a[5], a20 = a[6], a21 = a[7], a22 = a[8], x = v[0], y = v[1];
        out[0] = a00;
        out[1] = a01;
        out[2] = a02;
        out[3] = a10;
        out[4] = a11;
        out[5] = a12;
        out[6] = x * a00 + y * a10 + a20;
        out[7] = x * a01 + y * a11 + a21;
        out[8] = x * a02 + y * a12 + a22;
        return out;
    }
    exports.translate = translate;
    /**
     * Rotates a mat3 by the given angle
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat3} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat3} out
     */
    function rotate(out, a, rad) {
        var a00 = a[0], a01 = a[1], a02 = a[2], a10 = a[3], a11 = a[4], a12 = a[5], a20 = a[6], a21 = a[7], a22 = a[8], s = Math.sin(rad), c = Math.cos(rad);
        out[0] = c * a00 + s * a10;
        out[1] = c * a01 + s * a11;
        out[2] = c * a02 + s * a12;
        out[3] = c * a10 - s * a00;
        out[4] = c * a11 - s * a01;
        out[5] = c * a12 - s * a02;
        out[6] = a20;
        out[7] = a21;
        out[8] = a22;
        return out;
    }
    exports.rotate = rotate;
    /**
     * Scales the mat3 by the dimensions in the given vec2
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat3} a the matrix to rotate
     * @param {ReadonlyVec2} v the vec2 to scale the matrix by
     * @returns {mat3} out
     **/
    function scale(out, a, v) {
        var x = v[0], y = v[1];
        out[0] = x * a[0];
        out[1] = x * a[1];
        out[2] = x * a[2];
        out[3] = y * a[3];
        out[4] = y * a[4];
        out[5] = y * a[5];
        out[6] = a[6];
        out[7] = a[7];
        out[8] = a[8];
        return out;
    }
    exports.scale = scale;
    /**
     * Creates a matrix from a vector translation
     * This is equivalent to (but much faster than):
     *
     *     mat3.identity(dest);
     *     mat3.translate(dest, dest, vec);
     *
     * @param {mat3} out mat3 receiving operation result
     * @param {ReadonlyVec2} v Translation vector
     * @returns {mat3} out
     */
    function fromTranslation(out, v) {
        out[0] = 1;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 1;
        out[5] = 0;
        out[6] = v[0];
        out[7] = v[1];
        out[8] = 1;
        return out;
    }
    exports.fromTranslation = fromTranslation;
    /**
     * Creates a matrix from a given angle
     * This is equivalent to (but much faster than):
     *
     *     mat3.identity(dest);
     *     mat3.rotate(dest, dest, rad);
     *
     * @param {mat3} out mat3 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat3} out
     */
    function fromRotation(out, rad) {
        var s = Math.sin(rad), c = Math.cos(rad);
        out[0] = c;
        out[1] = s;
        out[2] = 0;
        out[3] = -s;
        out[4] = c;
        out[5] = 0;
        out[6] = 0;
        out[7] = 0;
        out[8] = 1;
        return out;
    }
    exports.fromRotation = fromRotation;
    /**
     * Creates a matrix from a vector scaling
     * This is equivalent to (but much faster than):
     *
     *     mat3.identity(dest);
     *     mat3.scale(dest, dest, vec);
     *
     * @param {mat3} out mat3 receiving operation result
     * @param {ReadonlyVec2} v Scaling vector
     * @returns {mat3} out
     */
    function fromScaling(out, v) {
        out[0] = v[0];
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = v[1];
        out[5] = 0;
        out[6] = 0;
        out[7] = 0;
        out[8] = 1;
        return out;
    }
    exports.fromScaling = fromScaling;
    /**
     * Copies the values from a mat2d into a mat3
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat2d} a the matrix to copy
     * @returns {mat3} out
     **/
    function fromMat2d(out, a) {
        out[0] = a[0];
        out[1] = a[1];
        out[2] = 0;
        out[3] = a[2];
        out[4] = a[3];
        out[5] = 0;
        out[6] = a[4];
        out[7] = a[5];
        out[8] = 1;
        return out;
    }
    exports.fromMat2d = fromMat2d;
    /**
     * Calculates a 3x3 matrix from the given quaternion
     *
     * @param {mat3} out mat3 receiving operation result
     * @param {ReadonlyQuat} q Quaternion to create matrix from
     *
     * @returns {mat3} out
     */
    function fromQuat(out, q) {
        var x = q[0], y = q[1], z = q[2], w = q[3];
        var x2 = x + x;
        var y2 = y + y;
        var z2 = z + z;
        var xx = x * x2;
        var yx = y * x2;
        var yy = y * y2;
        var zx = z * x2;
        var zy = z * y2;
        var zz = z * z2;
        var wx = w * x2;
        var wy = w * y2;
        var wz = w * z2;
        out[0] = 1 - yy - zz;
        out[3] = yx - wz;
        out[6] = zx + wy;
        out[1] = yx + wz;
        out[4] = 1 - xx - zz;
        out[7] = zy - wx;
        out[2] = zx - wy;
        out[5] = zy + wx;
        out[8] = 1 - xx - yy;
        return out;
    }
    exports.fromQuat = fromQuat;
    /**
     * Calculates a 3x3 normal matrix (transpose inverse) from the 4x4 matrix
     *
     * @param {mat3} out mat3 receiving operation result
     * @param {ReadonlyMat4} a Mat4 to derive the normal matrix from
     *
     * @returns {mat3} out
     */
    function normalFromMat4(out, a) {
        var a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
        var a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
        var a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
        var a30 = a[12], a31 = a[13], a32 = a[14], a33 = a[15];
        var b00 = a00 * a11 - a01 * a10;
        var b01 = a00 * a12 - a02 * a10;
        var b02 = a00 * a13 - a03 * a10;
        var b03 = a01 * a12 - a02 * a11;
        var b04 = a01 * a13 - a03 * a11;
        var b05 = a02 * a13 - a03 * a12;
        var b06 = a20 * a31 - a21 * a30;
        var b07 = a20 * a32 - a22 * a30;
        var b08 = a20 * a33 - a23 * a30;
        var b09 = a21 * a32 - a22 * a31;
        var b10 = a21 * a33 - a23 * a31;
        var b11 = a22 * a33 - a23 * a32; // Calculate the determinant
        var det = b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06;
        if (!det) {
            return null;
        }
        det = 1.0 / det;
        out[0] = (a11 * b11 - a12 * b10 + a13 * b09) * det;
        out[1] = (a12 * b08 - a10 * b11 - a13 * b07) * det;
        out[2] = (a10 * b10 - a11 * b08 + a13 * b06) * det;
        out[3] = (a02 * b10 - a01 * b11 - a03 * b09) * det;
        out[4] = (a00 * b11 - a02 * b08 + a03 * b07) * det;
        out[5] = (a01 * b08 - a00 * b10 - a03 * b06) * det;
        out[6] = (a31 * b05 - a32 * b04 + a33 * b03) * det;
        out[7] = (a32 * b02 - a30 * b05 - a33 * b01) * det;
        out[8] = (a30 * b04 - a31 * b02 + a33 * b00) * det;
        return out;
    }
    exports.normalFromMat4 = normalFromMat4;
    /**
     * Generates a 2D projection matrix with the given bounds
     *
     * @param {mat3} out mat3 frustum matrix will be written into
     * @param {number} width Width of your gl context
     * @param {number} height Height of gl context
     * @returns {mat3} out
     */
    function projection(out, width, height) {
        out[0] = 2 / width;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = -2 / height;
        out[5] = 0;
        out[6] = -1;
        out[7] = 1;
        out[8] = 1;
        return out;
    }
    exports.projection = projection;
    /**
     * Returns a string representation of a mat3
     *
     * @param {ReadonlyMat3} a matrix to represent as a string
     * @returns {String} string representation of the matrix
     */
    function str(a) {
        return "mat3(" + a[0] + ", " + a[1] + ", " + a[2] + ", " + a[3] + ", " + a[4] + ", " + a[5] + ", " + a[6] + ", " + a[7] + ", " + a[8] + ")";
    }
    exports.str = str;
    /**
     * Returns Frobenius norm of a mat3
     *
     * @param {ReadonlyMat3} a the matrix to calculate Frobenius norm of
     * @returns {Number} Frobenius norm
     */
    function frob(a) {
        return Math.hypot(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8]);
    }
    exports.frob = frob;
    /**
     * Adds two mat3's
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat3} a the first operand
     * @param {ReadonlyMat3} b the second operand
     * @returns {mat3} out
     */
    function add(out, a, b) {
        out[0] = a[0] + b[0];
        out[1] = a[1] + b[1];
        out[2] = a[2] + b[2];
        out[3] = a[3] + b[3];
        out[4] = a[4] + b[4];
        out[5] = a[5] + b[5];
        out[6] = a[6] + b[6];
        out[7] = a[7] + b[7];
        out[8] = a[8] + b[8];
        return out;
    }
    exports.add = add;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat3} a the first operand
     * @param {ReadonlyMat3} b the second operand
     * @returns {mat3} out
     */
    function subtract(out, a, b) {
        out[0] = a[0] - b[0];
        out[1] = a[1] - b[1];
        out[2] = a[2] - b[2];
        out[3] = a[3] - b[3];
        out[4] = a[4] - b[4];
        out[5] = a[5] - b[5];
        out[6] = a[6] - b[6];
        out[7] = a[7] - b[7];
        out[8] = a[8] - b[8];
        return out;
    }
    exports.subtract = subtract;
    /**
     * Multiply each element of the matrix by a scalar.
     *
     * @param {mat3} out the receiving matrix
     * @param {ReadonlyMat3} a the matrix to scale
     * @param {Number} b amount to scale the matrix's elements by
     * @returns {mat3} out
     */
    function multiplyScalar(out, a, b) {
        out[0] = a[0] * b;
        out[1] = a[1] * b;
        out[2] = a[2] * b;
        out[3] = a[3] * b;
        out[4] = a[4] * b;
        out[5] = a[5] * b;
        out[6] = a[6] * b;
        out[7] = a[7] * b;
        out[8] = a[8] * b;
        return out;
    }
    exports.multiplyScalar = multiplyScalar;
    /**
     * Adds two mat3's after multiplying each element of the second operand by a scalar value.
     *
     * @param {mat3} out the receiving vector
     * @param {ReadonlyMat3} a the first operand
     * @param {ReadonlyMat3} b the second operand
     * @param {Number} scale the amount to scale b's elements by before adding
     * @returns {mat3} out
     */
    function multiplyScalarAndAdd(out, a, b, scale) {
        out[0] = a[0] + b[0] * scale;
        out[1] = a[1] + b[1] * scale;
        out[2] = a[2] + b[2] * scale;
        out[3] = a[3] + b[3] * scale;
        out[4] = a[4] + b[4] * scale;
        out[5] = a[5] + b[5] * scale;
        out[6] = a[6] + b[6] * scale;
        out[7] = a[7] + b[7] * scale;
        out[8] = a[8] + b[8] * scale;
        return out;
    }
    exports.multiplyScalarAndAdd = multiplyScalarAndAdd;
    /**
     * Returns whether or not the matrices have exactly the same elements in the same position (when compared with ===)
     *
     * @param {ReadonlyMat3} a The first matrix.
     * @param {ReadonlyMat3} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    function exactEquals(a, b) {
        return a[0] === b[0] && a[1] === b[1] && a[2] === b[2] && a[3] === b[3] && a[4] === b[4] && a[5] === b[5] && a[6] === b[6] && a[7] === b[7] && a[8] === b[8];
    }
    exports.exactEquals = exactEquals;
    /**
     * Returns whether or not the matrices have approximately the same elements in the same position.
     *
     * @param {ReadonlyMat3} a The first matrix.
     * @param {ReadonlyMat3} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    function equals(a, b) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3], a4 = a[4], a5 = a[5], a6 = a[6], a7 = a[7], a8 = a[8];
        var b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3], b4 = b[4], b5 = b[5], b6 = b[6], b7 = b[7], b8 = b[8];
        return Math.abs(a0 - b0) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a0), Math.abs(b0)) && Math.abs(a1 - b1) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a1), Math.abs(b1)) && Math.abs(a2 - b2) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a2), Math.abs(b2)) && Math.abs(a3 - b3) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a3), Math.abs(b3)) && Math.abs(a4 - b4) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a4), Math.abs(b4)) && Math.abs(a5 - b5) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a5), Math.abs(b5)) && Math.abs(a6 - b6) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a6), Math.abs(b6)) && Math.abs(a7 - b7) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a7), Math.abs(b7)) && Math.abs(a8 - b8) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a8), Math.abs(b8));
    }
    exports.equals = equals;
    /**
     * Alias for {@link mat3.multiply}
     * @function
     */
    exports.mul = multiply;
    /**
     * Alias for {@link mat3.subtract}
     * @function
     */
    exports.sub = subtract;
},
"83bad9e639": /* gl-matrix/esm/mat4.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    exports.sub = void 0;
    const tslib_1 = require("tslib");
    const glMatrix = tslib_1.__importStar(require("7d825b979e") /* ./common.js */);
    /**
     * 4x4 Matrix<br>Format: column-major, when typed out it looks like row-major<br>The matrices are being post multiplied.
     * @module mat4
     */
    /**
     * Creates a new identity mat4
     *
     * @returns {mat4} a new 4x4 matrix
     */
    function create() {
        var out = new glMatrix.ARRAY_TYPE(16);
        if (glMatrix.ARRAY_TYPE != Float32Array) {
            out[1] = 0;
            out[2] = 0;
            out[3] = 0;
            out[4] = 0;
            out[6] = 0;
            out[7] = 0;
            out[8] = 0;
            out[9] = 0;
            out[11] = 0;
            out[12] = 0;
            out[13] = 0;
            out[14] = 0;
        }
        out[0] = 1;
        out[5] = 1;
        out[10] = 1;
        out[15] = 1;
        return out;
    }
    exports.create = create;
    /**
     * Creates a new mat4 initialized with values from an existing matrix
     *
     * @param {ReadonlyMat4} a matrix to clone
     * @returns {mat4} a new 4x4 matrix
     */
    function clone(a) {
        var out = new glMatrix.ARRAY_TYPE(16);
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[3];
        out[4] = a[4];
        out[5] = a[5];
        out[6] = a[6];
        out[7] = a[7];
        out[8] = a[8];
        out[9] = a[9];
        out[10] = a[10];
        out[11] = a[11];
        out[12] = a[12];
        out[13] = a[13];
        out[14] = a[14];
        out[15] = a[15];
        return out;
    }
    exports.clone = clone;
    /**
     * Copy the values from one mat4 to another
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the source matrix
     * @returns {mat4} out
     */
    function copy(out, a) {
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[3];
        out[4] = a[4];
        out[5] = a[5];
        out[6] = a[6];
        out[7] = a[7];
        out[8] = a[8];
        out[9] = a[9];
        out[10] = a[10];
        out[11] = a[11];
        out[12] = a[12];
        out[13] = a[13];
        out[14] = a[14];
        out[15] = a[15];
        return out;
    }
    exports.copy = copy;
    /**
     * Create a new mat4 with the given values
     *
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m02 Component in column 0, row 2 position (index 2)
     * @param {Number} m03 Component in column 0, row 3 position (index 3)
     * @param {Number} m10 Component in column 1, row 0 position (index 4)
     * @param {Number} m11 Component in column 1, row 1 position (index 5)
     * @param {Number} m12 Component in column 1, row 2 position (index 6)
     * @param {Number} m13 Component in column 1, row 3 position (index 7)
     * @param {Number} m20 Component in column 2, row 0 position (index 8)
     * @param {Number} m21 Component in column 2, row 1 position (index 9)
     * @param {Number} m22 Component in column 2, row 2 position (index 10)
     * @param {Number} m23 Component in column 2, row 3 position (index 11)
     * @param {Number} m30 Component in column 3, row 0 position (index 12)
     * @param {Number} m31 Component in column 3, row 1 position (index 13)
     * @param {Number} m32 Component in column 3, row 2 position (index 14)
     * @param {Number} m33 Component in column 3, row 3 position (index 15)
     * @returns {mat4} A new mat4
     */
    function fromValues(m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33) {
        var out = new glMatrix.ARRAY_TYPE(16);
        out[0] = m00;
        out[1] = m01;
        out[2] = m02;
        out[3] = m03;
        out[4] = m10;
        out[5] = m11;
        out[6] = m12;
        out[7] = m13;
        out[8] = m20;
        out[9] = m21;
        out[10] = m22;
        out[11] = m23;
        out[12] = m30;
        out[13] = m31;
        out[14] = m32;
        out[15] = m33;
        return out;
    }
    exports.fromValues = fromValues;
    /**
     * Set the components of a mat4 to the given values
     *
     * @param {mat4} out the receiving matrix
     * @param {Number} m00 Component in column 0, row 0 position (index 0)
     * @param {Number} m01 Component in column 0, row 1 position (index 1)
     * @param {Number} m02 Component in column 0, row 2 position (index 2)
     * @param {Number} m03 Component in column 0, row 3 position (index 3)
     * @param {Number} m10 Component in column 1, row 0 position (index 4)
     * @param {Number} m11 Component in column 1, row 1 position (index 5)
     * @param {Number} m12 Component in column 1, row 2 position (index 6)
     * @param {Number} m13 Component in column 1, row 3 position (index 7)
     * @param {Number} m20 Component in column 2, row 0 position (index 8)
     * @param {Number} m21 Component in column 2, row 1 position (index 9)
     * @param {Number} m22 Component in column 2, row 2 position (index 10)
     * @param {Number} m23 Component in column 2, row 3 position (index 11)
     * @param {Number} m30 Component in column 3, row 0 position (index 12)
     * @param {Number} m31 Component in column 3, row 1 position (index 13)
     * @param {Number} m32 Component in column 3, row 2 position (index 14)
     * @param {Number} m33 Component in column 3, row 3 position (index 15)
     * @returns {mat4} out
     */
    function set(out, m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33) {
        out[0] = m00;
        out[1] = m01;
        out[2] = m02;
        out[3] = m03;
        out[4] = m10;
        out[5] = m11;
        out[6] = m12;
        out[7] = m13;
        out[8] = m20;
        out[9] = m21;
        out[10] = m22;
        out[11] = m23;
        out[12] = m30;
        out[13] = m31;
        out[14] = m32;
        out[15] = m33;
        return out;
    }
    exports.set = set;
    /**
     * Set a mat4 to the identity matrix
     *
     * @param {mat4} out the receiving matrix
     * @returns {mat4} out
     */
    function identity(out) {
        out[0] = 1;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 0;
        out[5] = 1;
        out[6] = 0;
        out[7] = 0;
        out[8] = 0;
        out[9] = 0;
        out[10] = 1;
        out[11] = 0;
        out[12] = 0;
        out[13] = 0;
        out[14] = 0;
        out[15] = 1;
        return out;
    }
    exports.identity = identity;
    /**
     * Transpose the values of a mat4
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the source matrix
     * @returns {mat4} out
     */
    function transpose(out, a) {
        // If we are transposing ourselves we can skip a few steps but have to cache some values
        if (out === a) {
            var a01 = a[1], a02 = a[2], a03 = a[3];
            var a12 = a[6], a13 = a[7];
            var a23 = a[11];
            out[1] = a[4];
            out[2] = a[8];
            out[3] = a[12];
            out[4] = a01;
            out[6] = a[9];
            out[7] = a[13];
            out[8] = a02;
            out[9] = a12;
            out[11] = a[14];
            out[12] = a03;
            out[13] = a13;
            out[14] = a23;
        }
        else {
            out[0] = a[0];
            out[1] = a[4];
            out[2] = a[8];
            out[3] = a[12];
            out[4] = a[1];
            out[5] = a[5];
            out[6] = a[9];
            out[7] = a[13];
            out[8] = a[2];
            out[9] = a[6];
            out[10] = a[10];
            out[11] = a[14];
            out[12] = a[3];
            out[13] = a[7];
            out[14] = a[11];
            out[15] = a[15];
        }
        return out;
    }
    exports.transpose = transpose;
    /**
     * Inverts a mat4
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the source matrix
     * @returns {mat4} out
     */
    function invert(out, a) {
        var a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
        var a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
        var a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
        var a30 = a[12], a31 = a[13], a32 = a[14], a33 = a[15];
        var b00 = a00 * a11 - a01 * a10;
        var b01 = a00 * a12 - a02 * a10;
        var b02 = a00 * a13 - a03 * a10;
        var b03 = a01 * a12 - a02 * a11;
        var b04 = a01 * a13 - a03 * a11;
        var b05 = a02 * a13 - a03 * a12;
        var b06 = a20 * a31 - a21 * a30;
        var b07 = a20 * a32 - a22 * a30;
        var b08 = a20 * a33 - a23 * a30;
        var b09 = a21 * a32 - a22 * a31;
        var b10 = a21 * a33 - a23 * a31;
        var b11 = a22 * a33 - a23 * a32; // Calculate the determinant
        var det = b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06;
        if (!det) {
            return null;
        }
        det = 1.0 / det;
        out[0] = (a11 * b11 - a12 * b10 + a13 * b09) * det;
        out[1] = (a02 * b10 - a01 * b11 - a03 * b09) * det;
        out[2] = (a31 * b05 - a32 * b04 + a33 * b03) * det;
        out[3] = (a22 * b04 - a21 * b05 - a23 * b03) * det;
        out[4] = (a12 * b08 - a10 * b11 - a13 * b07) * det;
        out[5] = (a00 * b11 - a02 * b08 + a03 * b07) * det;
        out[6] = (a32 * b02 - a30 * b05 - a33 * b01) * det;
        out[7] = (a20 * b05 - a22 * b02 + a23 * b01) * det;
        out[8] = (a10 * b10 - a11 * b08 + a13 * b06) * det;
        out[9] = (a01 * b08 - a00 * b10 - a03 * b06) * det;
        out[10] = (a30 * b04 - a31 * b02 + a33 * b00) * det;
        out[11] = (a21 * b02 - a20 * b04 - a23 * b00) * det;
        out[12] = (a11 * b07 - a10 * b09 - a12 * b06) * det;
        out[13] = (a00 * b09 - a01 * b07 + a02 * b06) * det;
        out[14] = (a31 * b01 - a30 * b03 - a32 * b00) * det;
        out[15] = (a20 * b03 - a21 * b01 + a22 * b00) * det;
        return out;
    }
    exports.invert = invert;
    /**
     * Calculates the adjugate of a mat4
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the source matrix
     * @returns {mat4} out
     */
    function adjoint(out, a) {
        var a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
        var a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
        var a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
        var a30 = a[12], a31 = a[13], a32 = a[14], a33 = a[15];
        out[0] = a11 * (a22 * a33 - a23 * a32) - a21 * (a12 * a33 - a13 * a32) + a31 * (a12 * a23 - a13 * a22);
        out[1] = -(a01 * (a22 * a33 - a23 * a32) - a21 * (a02 * a33 - a03 * a32) + a31 * (a02 * a23 - a03 * a22));
        out[2] = a01 * (a12 * a33 - a13 * a32) - a11 * (a02 * a33 - a03 * a32) + a31 * (a02 * a13 - a03 * a12);
        out[3] = -(a01 * (a12 * a23 - a13 * a22) - a11 * (a02 * a23 - a03 * a22) + a21 * (a02 * a13 - a03 * a12));
        out[4] = -(a10 * (a22 * a33 - a23 * a32) - a20 * (a12 * a33 - a13 * a32) + a30 * (a12 * a23 - a13 * a22));
        out[5] = a00 * (a22 * a33 - a23 * a32) - a20 * (a02 * a33 - a03 * a32) + a30 * (a02 * a23 - a03 * a22);
        out[6] = -(a00 * (a12 * a33 - a13 * a32) - a10 * (a02 * a33 - a03 * a32) + a30 * (a02 * a13 - a03 * a12));
        out[7] = a00 * (a12 * a23 - a13 * a22) - a10 * (a02 * a23 - a03 * a22) + a20 * (a02 * a13 - a03 * a12);
        out[8] = a10 * (a21 * a33 - a23 * a31) - a20 * (a11 * a33 - a13 * a31) + a30 * (a11 * a23 - a13 * a21);
        out[9] = -(a00 * (a21 * a33 - a23 * a31) - a20 * (a01 * a33 - a03 * a31) + a30 * (a01 * a23 - a03 * a21));
        out[10] = a00 * (a11 * a33 - a13 * a31) - a10 * (a01 * a33 - a03 * a31) + a30 * (a01 * a13 - a03 * a11);
        out[11] = -(a00 * (a11 * a23 - a13 * a21) - a10 * (a01 * a23 - a03 * a21) + a20 * (a01 * a13 - a03 * a11));
        out[12] = -(a10 * (a21 * a32 - a22 * a31) - a20 * (a11 * a32 - a12 * a31) + a30 * (a11 * a22 - a12 * a21));
        out[13] = a00 * (a21 * a32 - a22 * a31) - a20 * (a01 * a32 - a02 * a31) + a30 * (a01 * a22 - a02 * a21);
        out[14] = -(a00 * (a11 * a32 - a12 * a31) - a10 * (a01 * a32 - a02 * a31) + a30 * (a01 * a12 - a02 * a11));
        out[15] = a00 * (a11 * a22 - a12 * a21) - a10 * (a01 * a22 - a02 * a21) + a20 * (a01 * a12 - a02 * a11);
        return out;
    }
    exports.adjoint = adjoint;
    /**
     * Calculates the determinant of a mat4
     *
     * @param {ReadonlyMat4} a the source matrix
     * @returns {Number} determinant of a
     */
    function determinant(a) {
        var a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
        var a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
        var a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
        var a30 = a[12], a31 = a[13], a32 = a[14], a33 = a[15];
        var b00 = a00 * a11 - a01 * a10;
        var b01 = a00 * a12 - a02 * a10;
        var b02 = a00 * a13 - a03 * a10;
        var b03 = a01 * a12 - a02 * a11;
        var b04 = a01 * a13 - a03 * a11;
        var b05 = a02 * a13 - a03 * a12;
        var b06 = a20 * a31 - a21 * a30;
        var b07 = a20 * a32 - a22 * a30;
        var b08 = a20 * a33 - a23 * a30;
        var b09 = a21 * a32 - a22 * a31;
        var b10 = a21 * a33 - a23 * a31;
        var b11 = a22 * a33 - a23 * a32; // Calculate the determinant
        return b00 * b11 - b01 * b10 + b02 * b09 + b03 * b08 - b04 * b07 + b05 * b06;
    }
    exports.determinant = determinant;
    /**
     * Multiplies two mat4s
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the first operand
     * @param {ReadonlyMat4} b the second operand
     * @returns {mat4} out
     */
    function multiply(out, a, b) {
        var a00 = a[0], a01 = a[1], a02 = a[2], a03 = a[3];
        var a10 = a[4], a11 = a[5], a12 = a[6], a13 = a[7];
        var a20 = a[8], a21 = a[9], a22 = a[10], a23 = a[11];
        var a30 = a[12], a31 = a[13], a32 = a[14], a33 = a[15]; // Cache only the current line of the second matrix
        var b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3];
        out[0] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
        out[1] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
        out[2] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
        out[3] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;
        b0 = b[4];
        b1 = b[5];
        b2 = b[6];
        b3 = b[7];
        out[4] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
        out[5] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
        out[6] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
        out[7] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;
        b0 = b[8];
        b1 = b[9];
        b2 = b[10];
        b3 = b[11];
        out[8] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
        out[9] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
        out[10] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
        out[11] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;
        b0 = b[12];
        b1 = b[13];
        b2 = b[14];
        b3 = b[15];
        out[12] = b0 * a00 + b1 * a10 + b2 * a20 + b3 * a30;
        out[13] = b0 * a01 + b1 * a11 + b2 * a21 + b3 * a31;
        out[14] = b0 * a02 + b1 * a12 + b2 * a22 + b3 * a32;
        out[15] = b0 * a03 + b1 * a13 + b2 * a23 + b3 * a33;
        return out;
    }
    exports.multiply = multiply;
    /**
     * Translate a mat4 by the given vector
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the matrix to translate
     * @param {ReadonlyVec3} v vector to translate by
     * @returns {mat4} out
     */
    function translate(out, a, v) {
        var x = v[0], y = v[1], z = v[2];
        var a00, a01, a02, a03;
        var a10, a11, a12, a13;
        var a20, a21, a22, a23;
        if (a === out) {
            out[12] = a[0] * x + a[4] * y + a[8] * z + a[12];
            out[13] = a[1] * x + a[5] * y + a[9] * z + a[13];
            out[14] = a[2] * x + a[6] * y + a[10] * z + a[14];
            out[15] = a[3] * x + a[7] * y + a[11] * z + a[15];
        }
        else {
            a00 = a[0];
            a01 = a[1];
            a02 = a[2];
            a03 = a[3];
            a10 = a[4];
            a11 = a[5];
            a12 = a[6];
            a13 = a[7];
            a20 = a[8];
            a21 = a[9];
            a22 = a[10];
            a23 = a[11];
            out[0] = a00;
            out[1] = a01;
            out[2] = a02;
            out[3] = a03;
            out[4] = a10;
            out[5] = a11;
            out[6] = a12;
            out[7] = a13;
            out[8] = a20;
            out[9] = a21;
            out[10] = a22;
            out[11] = a23;
            out[12] = a00 * x + a10 * y + a20 * z + a[12];
            out[13] = a01 * x + a11 * y + a21 * z + a[13];
            out[14] = a02 * x + a12 * y + a22 * z + a[14];
            out[15] = a03 * x + a13 * y + a23 * z + a[15];
        }
        return out;
    }
    exports.translate = translate;
    /**
     * Scales the mat4 by the dimensions in the given vec3 not using vectorization
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the matrix to scale
     * @param {ReadonlyVec3} v the vec3 to scale the matrix by
     * @returns {mat4} out
     **/
    function scale(out, a, v) {
        var x = v[0], y = v[1], z = v[2];
        out[0] = a[0] * x;
        out[1] = a[1] * x;
        out[2] = a[2] * x;
        out[3] = a[3] * x;
        out[4] = a[4] * y;
        out[5] = a[5] * y;
        out[6] = a[6] * y;
        out[7] = a[7] * y;
        out[8] = a[8] * z;
        out[9] = a[9] * z;
        out[10] = a[10] * z;
        out[11] = a[11] * z;
        out[12] = a[12];
        out[13] = a[13];
        out[14] = a[14];
        out[15] = a[15];
        return out;
    }
    exports.scale = scale;
    /**
     * Rotates a mat4 by the given angle around the given axis
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @param {ReadonlyVec3} axis the axis to rotate around
     * @returns {mat4} out
     */
    function rotate(out, a, rad, axis) {
        var x = axis[0], y = axis[1], z = axis[2];
        var len = Math.hypot(x, y, z);
        var s, c, t;
        var a00, a01, a02, a03;
        var a10, a11, a12, a13;
        var a20, a21, a22, a23;
        var b00, b01, b02;
        var b10, b11, b12;
        var b20, b21, b22;
        if (len < glMatrix.EPSILON) {
            return null;
        }
        len = 1 / len;
        x *= len;
        y *= len;
        z *= len;
        s = Math.sin(rad);
        c = Math.cos(rad);
        t = 1 - c;
        a00 = a[0];
        a01 = a[1];
        a02 = a[2];
        a03 = a[3];
        a10 = a[4];
        a11 = a[5];
        a12 = a[6];
        a13 = a[7];
        a20 = a[8];
        a21 = a[9];
        a22 = a[10];
        a23 = a[11]; // Construct the elements of the rotation matrix
        b00 = x * x * t + c;
        b01 = y * x * t + z * s;
        b02 = z * x * t - y * s;
        b10 = x * y * t - z * s;
        b11 = y * y * t + c;
        b12 = z * y * t + x * s;
        b20 = x * z * t + y * s;
        b21 = y * z * t - x * s;
        b22 = z * z * t + c; // Perform rotation-specific matrix multiplication
        out[0] = a00 * b00 + a10 * b01 + a20 * b02;
        out[1] = a01 * b00 + a11 * b01 + a21 * b02;
        out[2] = a02 * b00 + a12 * b01 + a22 * b02;
        out[3] = a03 * b00 + a13 * b01 + a23 * b02;
        out[4] = a00 * b10 + a10 * b11 + a20 * b12;
        out[5] = a01 * b10 + a11 * b11 + a21 * b12;
        out[6] = a02 * b10 + a12 * b11 + a22 * b12;
        out[7] = a03 * b10 + a13 * b11 + a23 * b12;
        out[8] = a00 * b20 + a10 * b21 + a20 * b22;
        out[9] = a01 * b20 + a11 * b21 + a21 * b22;
        out[10] = a02 * b20 + a12 * b21 + a22 * b22;
        out[11] = a03 * b20 + a13 * b21 + a23 * b22;
        if (a !== out) {
            // If the source and destination differ, copy the unchanged last row
            out[12] = a[12];
            out[13] = a[13];
            out[14] = a[14];
            out[15] = a[15];
        }
        return out;
    }
    exports.rotate = rotate;
    /**
     * Rotates a matrix by the given angle around the X axis
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    function rotateX(out, a, rad) {
        var s = Math.sin(rad);
        var c = Math.cos(rad);
        var a10 = a[4];
        var a11 = a[5];
        var a12 = a[6];
        var a13 = a[7];
        var a20 = a[8];
        var a21 = a[9];
        var a22 = a[10];
        var a23 = a[11];
        if (a !== out) {
            // If the source and destination differ, copy the unchanged rows
            out[0] = a[0];
            out[1] = a[1];
            out[2] = a[2];
            out[3] = a[3];
            out[12] = a[12];
            out[13] = a[13];
            out[14] = a[14];
            out[15] = a[15];
        } // Perform axis-specific matrix multiplication
        out[4] = a10 * c + a20 * s;
        out[5] = a11 * c + a21 * s;
        out[6] = a12 * c + a22 * s;
        out[7] = a13 * c + a23 * s;
        out[8] = a20 * c - a10 * s;
        out[9] = a21 * c - a11 * s;
        out[10] = a22 * c - a12 * s;
        out[11] = a23 * c - a13 * s;
        return out;
    }
    exports.rotateX = rotateX;
    /**
     * Rotates a matrix by the given angle around the Y axis
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    function rotateY(out, a, rad) {
        var s = Math.sin(rad);
        var c = Math.cos(rad);
        var a00 = a[0];
        var a01 = a[1];
        var a02 = a[2];
        var a03 = a[3];
        var a20 = a[8];
        var a21 = a[9];
        var a22 = a[10];
        var a23 = a[11];
        if (a !== out) {
            // If the source and destination differ, copy the unchanged rows
            out[4] = a[4];
            out[5] = a[5];
            out[6] = a[6];
            out[7] = a[7];
            out[12] = a[12];
            out[13] = a[13];
            out[14] = a[14];
            out[15] = a[15];
        } // Perform axis-specific matrix multiplication
        out[0] = a00 * c - a20 * s;
        out[1] = a01 * c - a21 * s;
        out[2] = a02 * c - a22 * s;
        out[3] = a03 * c - a23 * s;
        out[8] = a00 * s + a20 * c;
        out[9] = a01 * s + a21 * c;
        out[10] = a02 * s + a22 * c;
        out[11] = a03 * s + a23 * c;
        return out;
    }
    exports.rotateY = rotateY;
    /**
     * Rotates a matrix by the given angle around the Z axis
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the matrix to rotate
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    function rotateZ(out, a, rad) {
        var s = Math.sin(rad);
        var c = Math.cos(rad);
        var a00 = a[0];
        var a01 = a[1];
        var a02 = a[2];
        var a03 = a[3];
        var a10 = a[4];
        var a11 = a[5];
        var a12 = a[6];
        var a13 = a[7];
        if (a !== out) {
            // If the source and destination differ, copy the unchanged last row
            out[8] = a[8];
            out[9] = a[9];
            out[10] = a[10];
            out[11] = a[11];
            out[12] = a[12];
            out[13] = a[13];
            out[14] = a[14];
            out[15] = a[15];
        } // Perform axis-specific matrix multiplication
        out[0] = a00 * c + a10 * s;
        out[1] = a01 * c + a11 * s;
        out[2] = a02 * c + a12 * s;
        out[3] = a03 * c + a13 * s;
        out[4] = a10 * c - a00 * s;
        out[5] = a11 * c - a01 * s;
        out[6] = a12 * c - a02 * s;
        out[7] = a13 * c - a03 * s;
        return out;
    }
    exports.rotateZ = rotateZ;
    /**
     * Creates a matrix from a vector translation
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.translate(dest, dest, vec);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {ReadonlyVec3} v Translation vector
     * @returns {mat4} out
     */
    function fromTranslation(out, v) {
        out[0] = 1;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 0;
        out[5] = 1;
        out[6] = 0;
        out[7] = 0;
        out[8] = 0;
        out[9] = 0;
        out[10] = 1;
        out[11] = 0;
        out[12] = v[0];
        out[13] = v[1];
        out[14] = v[2];
        out[15] = 1;
        return out;
    }
    exports.fromTranslation = fromTranslation;
    /**
     * Creates a matrix from a vector scaling
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.scale(dest, dest, vec);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {ReadonlyVec3} v Scaling vector
     * @returns {mat4} out
     */
    function fromScaling(out, v) {
        out[0] = v[0];
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 0;
        out[5] = v[1];
        out[6] = 0;
        out[7] = 0;
        out[8] = 0;
        out[9] = 0;
        out[10] = v[2];
        out[11] = 0;
        out[12] = 0;
        out[13] = 0;
        out[14] = 0;
        out[15] = 1;
        return out;
    }
    exports.fromScaling = fromScaling;
    /**
     * Creates a matrix from a given angle around a given axis
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.rotate(dest, dest, rad, axis);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @param {ReadonlyVec3} axis the axis to rotate around
     * @returns {mat4} out
     */
    function fromRotation(out, rad, axis) {
        var x = axis[0], y = axis[1], z = axis[2];
        var len = Math.hypot(x, y, z);
        var s, c, t;
        if (len < glMatrix.EPSILON) {
            return null;
        }
        len = 1 / len;
        x *= len;
        y *= len;
        z *= len;
        s = Math.sin(rad);
        c = Math.cos(rad);
        t = 1 - c; // Perform rotation-specific matrix multiplication
        out[0] = x * x * t + c;
        out[1] = y * x * t + z * s;
        out[2] = z * x * t - y * s;
        out[3] = 0;
        out[4] = x * y * t - z * s;
        out[5] = y * y * t + c;
        out[6] = z * y * t + x * s;
        out[7] = 0;
        out[8] = x * z * t + y * s;
        out[9] = y * z * t - x * s;
        out[10] = z * z * t + c;
        out[11] = 0;
        out[12] = 0;
        out[13] = 0;
        out[14] = 0;
        out[15] = 1;
        return out;
    }
    exports.fromRotation = fromRotation;
    /**
     * Creates a matrix from the given angle around the X axis
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.rotateX(dest, dest, rad);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    function fromXRotation(out, rad) {
        var s = Math.sin(rad);
        var c = Math.cos(rad); // Perform axis-specific matrix multiplication
        out[0] = 1;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 0;
        out[5] = c;
        out[6] = s;
        out[7] = 0;
        out[8] = 0;
        out[9] = -s;
        out[10] = c;
        out[11] = 0;
        out[12] = 0;
        out[13] = 0;
        out[14] = 0;
        out[15] = 1;
        return out;
    }
    exports.fromXRotation = fromXRotation;
    /**
     * Creates a matrix from the given angle around the Y axis
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.rotateY(dest, dest, rad);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    function fromYRotation(out, rad) {
        var s = Math.sin(rad);
        var c = Math.cos(rad); // Perform axis-specific matrix multiplication
        out[0] = c;
        out[1] = 0;
        out[2] = -s;
        out[3] = 0;
        out[4] = 0;
        out[5] = 1;
        out[6] = 0;
        out[7] = 0;
        out[8] = s;
        out[9] = 0;
        out[10] = c;
        out[11] = 0;
        out[12] = 0;
        out[13] = 0;
        out[14] = 0;
        out[15] = 1;
        return out;
    }
    exports.fromYRotation = fromYRotation;
    /**
     * Creates a matrix from the given angle around the Z axis
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.rotateZ(dest, dest, rad);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {Number} rad the angle to rotate the matrix by
     * @returns {mat4} out
     */
    function fromZRotation(out, rad) {
        var s = Math.sin(rad);
        var c = Math.cos(rad); // Perform axis-specific matrix multiplication
        out[0] = c;
        out[1] = s;
        out[2] = 0;
        out[3] = 0;
        out[4] = -s;
        out[5] = c;
        out[6] = 0;
        out[7] = 0;
        out[8] = 0;
        out[9] = 0;
        out[10] = 1;
        out[11] = 0;
        out[12] = 0;
        out[13] = 0;
        out[14] = 0;
        out[15] = 1;
        return out;
    }
    exports.fromZRotation = fromZRotation;
    /**
     * Creates a matrix from a quaternion rotation and vector translation
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.translate(dest, vec);
     *     let quatMat = mat4.create();
     *     quat4.toMat4(quat, quatMat);
     *     mat4.multiply(dest, quatMat);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {quat4} q Rotation quaternion
     * @param {ReadonlyVec3} v Translation vector
     * @returns {mat4} out
     */
    function fromRotationTranslation(out, q, v) {
        // Quaternion math
        var x = q[0], y = q[1], z = q[2], w = q[3];
        var x2 = x + x;
        var y2 = y + y;
        var z2 = z + z;
        var xx = x * x2;
        var xy = x * y2;
        var xz = x * z2;
        var yy = y * y2;
        var yz = y * z2;
        var zz = z * z2;
        var wx = w * x2;
        var wy = w * y2;
        var wz = w * z2;
        out[0] = 1 - (yy + zz);
        out[1] = xy + wz;
        out[2] = xz - wy;
        out[3] = 0;
        out[4] = xy - wz;
        out[5] = 1 - (xx + zz);
        out[6] = yz + wx;
        out[7] = 0;
        out[8] = xz + wy;
        out[9] = yz - wx;
        out[10] = 1 - (xx + yy);
        out[11] = 0;
        out[12] = v[0];
        out[13] = v[1];
        out[14] = v[2];
        out[15] = 1;
        return out;
    }
    exports.fromRotationTranslation = fromRotationTranslation;
    /**
     * Creates a new mat4 from a dual quat.
     *
     * @param {mat4} out Matrix
     * @param {ReadonlyQuat2} a Dual Quaternion
     * @returns {mat4} mat4 receiving operation result
     */
    function fromQuat2(out, a) {
        var translation = new glMatrix.ARRAY_TYPE(3);
        var bx = -a[0], by = -a[1], bz = -a[2], bw = a[3], ax = a[4], ay = a[5], az = a[6], aw = a[7];
        var magnitude = bx * bx + by * by + bz * bz + bw * bw; //Only scale if it makes sense
        if (magnitude > 0) {
            translation[0] = (ax * bw + aw * bx + ay * bz - az * by) * 2 / magnitude;
            translation[1] = (ay * bw + aw * by + az * bx - ax * bz) * 2 / magnitude;
            translation[2] = (az * bw + aw * bz + ax * by - ay * bx) * 2 / magnitude;
        }
        else {
            translation[0] = (ax * bw + aw * bx + ay * bz - az * by) * 2;
            translation[1] = (ay * bw + aw * by + az * bx - ax * bz) * 2;
            translation[2] = (az * bw + aw * bz + ax * by - ay * bx) * 2;
        }
        fromRotationTranslation(out, a, translation);
        return out;
    }
    exports.fromQuat2 = fromQuat2;
    /**
     * Returns the translation vector component of a transformation
     *  matrix. If a matrix is built with fromRotationTranslation,
     *  the returned vector will be the same as the translation vector
     *  originally supplied.
     * @param  {vec3} out Vector to receive translation component
     * @param  {ReadonlyMat4} mat Matrix to be decomposed (input)
     * @return {vec3} out
     */
    function getTranslation(out, mat) {
        out[0] = mat[12];
        out[1] = mat[13];
        out[2] = mat[14];
        return out;
    }
    exports.getTranslation = getTranslation;
    /**
     * Returns the scaling factor component of a transformation
     *  matrix. If a matrix is built with fromRotationTranslationScale
     *  with a normalized Quaternion paramter, the returned vector will be
     *  the same as the scaling vector
     *  originally supplied.
     * @param  {vec3} out Vector to receive scaling factor component
     * @param  {ReadonlyMat4} mat Matrix to be decomposed (input)
     * @return {vec3} out
     */
    function getScaling(out, mat) {
        var m11 = mat[0];
        var m12 = mat[1];
        var m13 = mat[2];
        var m21 = mat[4];
        var m22 = mat[5];
        var m23 = mat[6];
        var m31 = mat[8];
        var m32 = mat[9];
        var m33 = mat[10];
        out[0] = Math.hypot(m11, m12, m13);
        out[1] = Math.hypot(m21, m22, m23);
        out[2] = Math.hypot(m31, m32, m33);
        return out;
    }
    exports.getScaling = getScaling;
    /**
     * Returns a quaternion representing the rotational component
     *  of a transformation matrix. If a matrix is built with
     *  fromRotationTranslation, the returned quaternion will be the
     *  same as the quaternion originally supplied.
     * @param {quat} out Quaternion to receive the rotation component
     * @param {ReadonlyMat4} mat Matrix to be decomposed (input)
     * @return {quat} out
     */
    function getRotation(out, mat) {
        var scaling = new glMatrix.ARRAY_TYPE(3);
        getScaling(scaling, mat);
        var is1 = 1 / scaling[0];
        var is2 = 1 / scaling[1];
        var is3 = 1 / scaling[2];
        var sm11 = mat[0] * is1;
        var sm12 = mat[1] * is2;
        var sm13 = mat[2] * is3;
        var sm21 = mat[4] * is1;
        var sm22 = mat[5] * is2;
        var sm23 = mat[6] * is3;
        var sm31 = mat[8] * is1;
        var sm32 = mat[9] * is2;
        var sm33 = mat[10] * is3;
        var trace = sm11 + sm22 + sm33;
        var S = 0;
        if (trace > 0) {
            S = Math.sqrt(trace + 1.0) * 2;
            out[3] = 0.25 * S;
            out[0] = (sm23 - sm32) / S;
            out[1] = (sm31 - sm13) / S;
            out[2] = (sm12 - sm21) / S;
        }
        else if (sm11 > sm22 && sm11 > sm33) {
            S = Math.sqrt(1.0 + sm11 - sm22 - sm33) * 2;
            out[3] = (sm23 - sm32) / S;
            out[0] = 0.25 * S;
            out[1] = (sm12 + sm21) / S;
            out[2] = (sm31 + sm13) / S;
        }
        else if (sm22 > sm33) {
            S = Math.sqrt(1.0 + sm22 - sm11 - sm33) * 2;
            out[3] = (sm31 - sm13) / S;
            out[0] = (sm12 + sm21) / S;
            out[1] = 0.25 * S;
            out[2] = (sm23 + sm32) / S;
        }
        else {
            S = Math.sqrt(1.0 + sm33 - sm11 - sm22) * 2;
            out[3] = (sm12 - sm21) / S;
            out[0] = (sm31 + sm13) / S;
            out[1] = (sm23 + sm32) / S;
            out[2] = 0.25 * S;
        }
        return out;
    }
    exports.getRotation = getRotation;
    /**
     * Creates a matrix from a quaternion rotation, vector translation and vector scale
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.translate(dest, vec);
     *     let quatMat = mat4.create();
     *     quat4.toMat4(quat, quatMat);
     *     mat4.multiply(dest, quatMat);
     *     mat4.scale(dest, scale)
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {quat4} q Rotation quaternion
     * @param {ReadonlyVec3} v Translation vector
     * @param {ReadonlyVec3} s Scaling vector
     * @returns {mat4} out
     */
    function fromRotationTranslationScale(out, q, v, s) {
        // Quaternion math
        var x = q[0], y = q[1], z = q[2], w = q[3];
        var x2 = x + x;
        var y2 = y + y;
        var z2 = z + z;
        var xx = x * x2;
        var xy = x * y2;
        var xz = x * z2;
        var yy = y * y2;
        var yz = y * z2;
        var zz = z * z2;
        var wx = w * x2;
        var wy = w * y2;
        var wz = w * z2;
        var sx = s[0];
        var sy = s[1];
        var sz = s[2];
        out[0] = (1 - (yy + zz)) * sx;
        out[1] = (xy + wz) * sx;
        out[2] = (xz - wy) * sx;
        out[3] = 0;
        out[4] = (xy - wz) * sy;
        out[5] = (1 - (xx + zz)) * sy;
        out[6] = (yz + wx) * sy;
        out[7] = 0;
        out[8] = (xz + wy) * sz;
        out[9] = (yz - wx) * sz;
        out[10] = (1 - (xx + yy)) * sz;
        out[11] = 0;
        out[12] = v[0];
        out[13] = v[1];
        out[14] = v[2];
        out[15] = 1;
        return out;
    }
    exports.fromRotationTranslationScale = fromRotationTranslationScale;
    /**
     * Creates a matrix from a quaternion rotation, vector translation and vector scale, rotating and scaling around the given origin
     * This is equivalent to (but much faster than):
     *
     *     mat4.identity(dest);
     *     mat4.translate(dest, vec);
     *     mat4.translate(dest, origin);
     *     let quatMat = mat4.create();
     *     quat4.toMat4(quat, quatMat);
     *     mat4.multiply(dest, quatMat);
     *     mat4.scale(dest, scale)
     *     mat4.translate(dest, negativeOrigin);
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {quat4} q Rotation quaternion
     * @param {ReadonlyVec3} v Translation vector
     * @param {ReadonlyVec3} s Scaling vector
     * @param {ReadonlyVec3} o The origin vector around which to scale and rotate
     * @returns {mat4} out
     */
    function fromRotationTranslationScaleOrigin(out, q, v, s, o) {
        // Quaternion math
        var x = q[0], y = q[1], z = q[2], w = q[3];
        var x2 = x + x;
        var y2 = y + y;
        var z2 = z + z;
        var xx = x * x2;
        var xy = x * y2;
        var xz = x * z2;
        var yy = y * y2;
        var yz = y * z2;
        var zz = z * z2;
        var wx = w * x2;
        var wy = w * y2;
        var wz = w * z2;
        var sx = s[0];
        var sy = s[1];
        var sz = s[2];
        var ox = o[0];
        var oy = o[1];
        var oz = o[2];
        var out0 = (1 - (yy + zz)) * sx;
        var out1 = (xy + wz) * sx;
        var out2 = (xz - wy) * sx;
        var out4 = (xy - wz) * sy;
        var out5 = (1 - (xx + zz)) * sy;
        var out6 = (yz + wx) * sy;
        var out8 = (xz + wy) * sz;
        var out9 = (yz - wx) * sz;
        var out10 = (1 - (xx + yy)) * sz;
        out[0] = out0;
        out[1] = out1;
        out[2] = out2;
        out[3] = 0;
        out[4] = out4;
        out[5] = out5;
        out[6] = out6;
        out[7] = 0;
        out[8] = out8;
        out[9] = out9;
        out[10] = out10;
        out[11] = 0;
        out[12] = v[0] + ox - (out0 * ox + out4 * oy + out8 * oz);
        out[13] = v[1] + oy - (out1 * ox + out5 * oy + out9 * oz);
        out[14] = v[2] + oz - (out2 * ox + out6 * oy + out10 * oz);
        out[15] = 1;
        return out;
    }
    exports.fromRotationTranslationScaleOrigin = fromRotationTranslationScaleOrigin;
    /**
     * Calculates a 4x4 matrix from the given quaternion
     *
     * @param {mat4} out mat4 receiving operation result
     * @param {ReadonlyQuat} q Quaternion to create matrix from
     *
     * @returns {mat4} out
     */
    function fromQuat(out, q) {
        var x = q[0], y = q[1], z = q[2], w = q[3];
        var x2 = x + x;
        var y2 = y + y;
        var z2 = z + z;
        var xx = x * x2;
        var yx = y * x2;
        var yy = y * y2;
        var zx = z * x2;
        var zy = z * y2;
        var zz = z * z2;
        var wx = w * x2;
        var wy = w * y2;
        var wz = w * z2;
        out[0] = 1 - yy - zz;
        out[1] = yx + wz;
        out[2] = zx - wy;
        out[3] = 0;
        out[4] = yx - wz;
        out[5] = 1 - xx - zz;
        out[6] = zy + wx;
        out[7] = 0;
        out[8] = zx + wy;
        out[9] = zy - wx;
        out[10] = 1 - xx - yy;
        out[11] = 0;
        out[12] = 0;
        out[13] = 0;
        out[14] = 0;
        out[15] = 1;
        return out;
    }
    exports.fromQuat = fromQuat;
    /**
     * Generates a frustum matrix with the given bounds
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {Number} left Left bound of the frustum
     * @param {Number} right Right bound of the frustum
     * @param {Number} bottom Bottom bound of the frustum
     * @param {Number} top Top bound of the frustum
     * @param {Number} near Near bound of the frustum
     * @param {Number} far Far bound of the frustum
     * @returns {mat4} out
     */
    function frustum(out, left, right, bottom, top, near, far) {
        var rl = 1 / (right - left);
        var tb = 1 / (top - bottom);
        var nf = 1 / (near - far);
        out[0] = near * 2 * rl;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 0;
        out[5] = near * 2 * tb;
        out[6] = 0;
        out[7] = 0;
        out[8] = (right + left) * rl;
        out[9] = (top + bottom) * tb;
        out[10] = (far + near) * nf;
        out[11] = -1;
        out[12] = 0;
        out[13] = 0;
        out[14] = far * near * 2 * nf;
        out[15] = 0;
        return out;
    }
    exports.frustum = frustum;
    /**
     * Generates a perspective projection matrix with the given bounds.
     * The near/far clip planes correspond to a normalized device coordinate Z range of [-1, 1],
     * which matches WebGL/OpenGL's clip volume.
     * Passing null/undefined/no value for far will generate infinite projection matrix.
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {number} fovy Vertical field of view in radians
     * @param {number} aspect Aspect ratio. typically viewport width/height
     * @param {number} near Near bound of the frustum
     * @param {number} far Far bound of the frustum, can be null or Infinity
     * @returns {mat4} out
     */
    function perspectiveNO(out, fovy, aspect, near, far) {
        var f = 1.0 / Math.tan(fovy / 2), nf;
        out[0] = f / aspect;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 0;
        out[5] = f;
        out[6] = 0;
        out[7] = 0;
        out[8] = 0;
        out[9] = 0;
        out[11] = -1;
        out[12] = 0;
        out[13] = 0;
        out[15] = 0;
        if (far != null && far !== Infinity) {
            nf = 1 / (near - far);
            out[10] = (far + near) * nf;
            out[14] = 2 * far * near * nf;
        }
        else {
            out[10] = -1;
            out[14] = -2 * near;
        }
        return out;
    }
    exports.perspectiveNO = perspectiveNO;
    /**
     * Alias for {@link mat4.perspectiveNO}
     * @function
     */
    exports.perspective = perspectiveNO;
    /**
     * Generates a perspective projection matrix suitable for WebGPU with the given bounds.
     * The near/far clip planes correspond to a normalized device coordinate Z range of [0, 1],
     * which matches WebGPU/Vulkan/DirectX/Metal's clip volume.
     * Passing null/undefined/no value for far will generate infinite projection matrix.
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {number} fovy Vertical field of view in radians
     * @param {number} aspect Aspect ratio. typically viewport width/height
     * @param {number} near Near bound of the frustum
     * @param {number} far Far bound of the frustum, can be null or Infinity
     * @returns {mat4} out
     */
    function perspectiveZO(out, fovy, aspect, near, far) {
        var f = 1.0 / Math.tan(fovy / 2), nf;
        out[0] = f / aspect;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 0;
        out[5] = f;
        out[6] = 0;
        out[7] = 0;
        out[8] = 0;
        out[9] = 0;
        out[11] = -1;
        out[12] = 0;
        out[13] = 0;
        out[15] = 0;
        if (far != null && far !== Infinity) {
            nf = 1 / (near - far);
            out[10] = far * nf;
            out[14] = far * near * nf;
        }
        else {
            out[10] = -1;
            out[14] = -near;
        }
        return out;
    }
    exports.perspectiveZO = perspectiveZO;
    /**
     * Generates a perspective projection matrix with the given field of view.
     * This is primarily useful for generating projection matrices to be used
     * with the still experiemental WebVR API.
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {Object} fov Object containing the following values: upDegrees, downDegrees, leftDegrees, rightDegrees
     * @param {number} near Near bound of the frustum
     * @param {number} far Far bound of the frustum
     * @returns {mat4} out
     */
    function perspectiveFromFieldOfView(out, fov, near, far) {
        var upTan = Math.tan(fov.upDegrees * Math.PI / 180.0);
        var downTan = Math.tan(fov.downDegrees * Math.PI / 180.0);
        var leftTan = Math.tan(fov.leftDegrees * Math.PI / 180.0);
        var rightTan = Math.tan(fov.rightDegrees * Math.PI / 180.0);
        var xScale = 2.0 / (leftTan + rightTan);
        var yScale = 2.0 / (upTan + downTan);
        out[0] = xScale;
        out[1] = 0.0;
        out[2] = 0.0;
        out[3] = 0.0;
        out[4] = 0.0;
        out[5] = yScale;
        out[6] = 0.0;
        out[7] = 0.0;
        out[8] = -((leftTan - rightTan) * xScale * 0.5);
        out[9] = (upTan - downTan) * yScale * 0.5;
        out[10] = far / (near - far);
        out[11] = -1.0;
        out[12] = 0.0;
        out[13] = 0.0;
        out[14] = far * near / (near - far);
        out[15] = 0.0;
        return out;
    }
    exports.perspectiveFromFieldOfView = perspectiveFromFieldOfView;
    /**
     * Generates a orthogonal projection matrix with the given bounds.
     * The near/far clip planes correspond to a normalized device coordinate Z range of [-1, 1],
     * which matches WebGL/OpenGL's clip volume.
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {number} left Left bound of the frustum
     * @param {number} right Right bound of the frustum
     * @param {number} bottom Bottom bound of the frustum
     * @param {number} top Top bound of the frustum
     * @param {number} near Near bound of the frustum
     * @param {number} far Far bound of the frustum
     * @returns {mat4} out
     */
    function orthoNO(out, left, right, bottom, top, near, far) {
        var lr = 1 / (left - right);
        var bt = 1 / (bottom - top);
        var nf = 1 / (near - far);
        out[0] = -2 * lr;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 0;
        out[5] = -2 * bt;
        out[6] = 0;
        out[7] = 0;
        out[8] = 0;
        out[9] = 0;
        out[10] = 2 * nf;
        out[11] = 0;
        out[12] = (left + right) * lr;
        out[13] = (top + bottom) * bt;
        out[14] = (far + near) * nf;
        out[15] = 1;
        return out;
    }
    exports.orthoNO = orthoNO;
    /**
     * Alias for {@link mat4.orthoNO}
     * @function
     */
    exports.ortho = orthoNO;
    /**
     * Generates a orthogonal projection matrix with the given bounds.
     * The near/far clip planes correspond to a normalized device coordinate Z range of [0, 1],
     * which matches WebGPU/Vulkan/DirectX/Metal's clip volume.
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {number} left Left bound of the frustum
     * @param {number} right Right bound of the frustum
     * @param {number} bottom Bottom bound of the frustum
     * @param {number} top Top bound of the frustum
     * @param {number} near Near bound of the frustum
     * @param {number} far Far bound of the frustum
     * @returns {mat4} out
     */
    function orthoZO(out, left, right, bottom, top, near, far) {
        var lr = 1 / (left - right);
        var bt = 1 / (bottom - top);
        var nf = 1 / (near - far);
        out[0] = -2 * lr;
        out[1] = 0;
        out[2] = 0;
        out[3] = 0;
        out[4] = 0;
        out[5] = -2 * bt;
        out[6] = 0;
        out[7] = 0;
        out[8] = 0;
        out[9] = 0;
        out[10] = nf;
        out[11] = 0;
        out[12] = (left + right) * lr;
        out[13] = (top + bottom) * bt;
        out[14] = near * nf;
        out[15] = 1;
        return out;
    }
    exports.orthoZO = orthoZO;
    /**
     * Generates a look-at matrix with the given eye position, focal point, and up axis.
     * If you want a matrix that actually makes an object look at another object, you should use targetTo instead.
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {ReadonlyVec3} eye Position of the viewer
     * @param {ReadonlyVec3} center Point the viewer is looking at
     * @param {ReadonlyVec3} up vec3 pointing up
     * @returns {mat4} out
     */
    function lookAt(out, eye, center, up) {
        var x0, x1, x2, y0, y1, y2, z0, z1, z2, len;
        var eyex = eye[0];
        var eyey = eye[1];
        var eyez = eye[2];
        var upx = up[0];
        var upy = up[1];
        var upz = up[2];
        var centerx = center[0];
        var centery = center[1];
        var centerz = center[2];
        if (Math.abs(eyex - centerx) < glMatrix.EPSILON && Math.abs(eyey - centery) < glMatrix.EPSILON && Math.abs(eyez - centerz) < glMatrix.EPSILON) {
            return identity(out);
        }
        z0 = eyex - centerx;
        z1 = eyey - centery;
        z2 = eyez - centerz;
        len = 1 / Math.hypot(z0, z1, z2);
        z0 *= len;
        z1 *= len;
        z2 *= len;
        x0 = upy * z2 - upz * z1;
        x1 = upz * z0 - upx * z2;
        x2 = upx * z1 - upy * z0;
        len = Math.hypot(x0, x1, x2);
        if (!len) {
            x0 = 0;
            x1 = 0;
            x2 = 0;
        }
        else {
            len = 1 / len;
            x0 *= len;
            x1 *= len;
            x2 *= len;
        }
        y0 = z1 * x2 - z2 * x1;
        y1 = z2 * x0 - z0 * x2;
        y2 = z0 * x1 - z1 * x0;
        len = Math.hypot(y0, y1, y2);
        if (!len) {
            y0 = 0;
            y1 = 0;
            y2 = 0;
        }
        else {
            len = 1 / len;
            y0 *= len;
            y1 *= len;
            y2 *= len;
        }
        out[0] = x0;
        out[1] = y0;
        out[2] = z0;
        out[3] = 0;
        out[4] = x1;
        out[5] = y1;
        out[6] = z1;
        out[7] = 0;
        out[8] = x2;
        out[9] = y2;
        out[10] = z2;
        out[11] = 0;
        out[12] = -(x0 * eyex + x1 * eyey + x2 * eyez);
        out[13] = -(y0 * eyex + y1 * eyey + y2 * eyez);
        out[14] = -(z0 * eyex + z1 * eyey + z2 * eyez);
        out[15] = 1;
        return out;
    }
    exports.lookAt = lookAt;
    /**
     * Generates a matrix that makes something look at something else.
     *
     * @param {mat4} out mat4 frustum matrix will be written into
     * @param {ReadonlyVec3} eye Position of the viewer
     * @param {ReadonlyVec3} center Point the viewer is looking at
     * @param {ReadonlyVec3} up vec3 pointing up
     * @returns {mat4} out
     */
    function targetTo(out, eye, target, up) {
        var eyex = eye[0], eyey = eye[1], eyez = eye[2], upx = up[0], upy = up[1], upz = up[2];
        var z0 = eyex - target[0], z1 = eyey - target[1], z2 = eyez - target[2];
        var len = z0 * z0 + z1 * z1 + z2 * z2;
        if (len > 0) {
            len = 1 / Math.sqrt(len);
            z0 *= len;
            z1 *= len;
            z2 *= len;
        }
        var x0 = upy * z2 - upz * z1, x1 = upz * z0 - upx * z2, x2 = upx * z1 - upy * z0;
        len = x0 * x0 + x1 * x1 + x2 * x2;
        if (len > 0) {
            len = 1 / Math.sqrt(len);
            x0 *= len;
            x1 *= len;
            x2 *= len;
        }
        out[0] = x0;
        out[1] = x1;
        out[2] = x2;
        out[3] = 0;
        out[4] = z1 * x2 - z2 * x1;
        out[5] = z2 * x0 - z0 * x2;
        out[6] = z0 * x1 - z1 * x0;
        out[7] = 0;
        out[8] = z0;
        out[9] = z1;
        out[10] = z2;
        out[11] = 0;
        out[12] = eyex;
        out[13] = eyey;
        out[14] = eyez;
        out[15] = 1;
        return out;
    }
    exports.targetTo = targetTo;
    /**
     * Returns a string representation of a mat4
     *
     * @param {ReadonlyMat4} a matrix to represent as a string
     * @returns {String} string representation of the matrix
     */
    function str(a) {
        return "mat4(" + a[0] + ", " + a[1] + ", " + a[2] + ", " + a[3] + ", " + a[4] + ", " + a[5] + ", " + a[6] + ", " + a[7] + ", " + a[8] + ", " + a[9] + ", " + a[10] + ", " + a[11] + ", " + a[12] + ", " + a[13] + ", " + a[14] + ", " + a[15] + ")";
    }
    exports.str = str;
    /**
     * Returns Frobenius norm of a mat4
     *
     * @param {ReadonlyMat4} a the matrix to calculate Frobenius norm of
     * @returns {Number} Frobenius norm
     */
    function frob(a) {
        return Math.hypot(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], a[11], a[12], a[13], a[14], a[15]);
    }
    exports.frob = frob;
    /**
     * Adds two mat4's
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the first operand
     * @param {ReadonlyMat4} b the second operand
     * @returns {mat4} out
     */
    function add(out, a, b) {
        out[0] = a[0] + b[0];
        out[1] = a[1] + b[1];
        out[2] = a[2] + b[2];
        out[3] = a[3] + b[3];
        out[4] = a[4] + b[4];
        out[5] = a[5] + b[5];
        out[6] = a[6] + b[6];
        out[7] = a[7] + b[7];
        out[8] = a[8] + b[8];
        out[9] = a[9] + b[9];
        out[10] = a[10] + b[10];
        out[11] = a[11] + b[11];
        out[12] = a[12] + b[12];
        out[13] = a[13] + b[13];
        out[14] = a[14] + b[14];
        out[15] = a[15] + b[15];
        return out;
    }
    exports.add = add;
    /**
     * Subtracts matrix b from matrix a
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the first operand
     * @param {ReadonlyMat4} b the second operand
     * @returns {mat4} out
     */
    function subtract(out, a, b) {
        out[0] = a[0] - b[0];
        out[1] = a[1] - b[1];
        out[2] = a[2] - b[2];
        out[3] = a[3] - b[3];
        out[4] = a[4] - b[4];
        out[5] = a[5] - b[5];
        out[6] = a[6] - b[6];
        out[7] = a[7] - b[7];
        out[8] = a[8] - b[8];
        out[9] = a[9] - b[9];
        out[10] = a[10] - b[10];
        out[11] = a[11] - b[11];
        out[12] = a[12] - b[12];
        out[13] = a[13] - b[13];
        out[14] = a[14] - b[14];
        out[15] = a[15] - b[15];
        return out;
    }
    exports.subtract = subtract;
    /**
     * Multiply each element of the matrix by a scalar.
     *
     * @param {mat4} out the receiving matrix
     * @param {ReadonlyMat4} a the matrix to scale
     * @param {Number} b amount to scale the matrix's elements by
     * @returns {mat4} out
     */
    function multiplyScalar(out, a, b) {
        out[0] = a[0] * b;
        out[1] = a[1] * b;
        out[2] = a[2] * b;
        out[3] = a[3] * b;
        out[4] = a[4] * b;
        out[5] = a[5] * b;
        out[6] = a[6] * b;
        out[7] = a[7] * b;
        out[8] = a[8] * b;
        out[9] = a[9] * b;
        out[10] = a[10] * b;
        out[11] = a[11] * b;
        out[12] = a[12] * b;
        out[13] = a[13] * b;
        out[14] = a[14] * b;
        out[15] = a[15] * b;
        return out;
    }
    exports.multiplyScalar = multiplyScalar;
    /**
     * Adds two mat4's after multiplying each element of the second operand by a scalar value.
     *
     * @param {mat4} out the receiving vector
     * @param {ReadonlyMat4} a the first operand
     * @param {ReadonlyMat4} b the second operand
     * @param {Number} scale the amount to scale b's elements by before adding
     * @returns {mat4} out
     */
    function multiplyScalarAndAdd(out, a, b, scale) {
        out[0] = a[0] + b[0] * scale;
        out[1] = a[1] + b[1] * scale;
        out[2] = a[2] + b[2] * scale;
        out[3] = a[3] + b[3] * scale;
        out[4] = a[4] + b[4] * scale;
        out[5] = a[5] + b[5] * scale;
        out[6] = a[6] + b[6] * scale;
        out[7] = a[7] + b[7] * scale;
        out[8] = a[8] + b[8] * scale;
        out[9] = a[9] + b[9] * scale;
        out[10] = a[10] + b[10] * scale;
        out[11] = a[11] + b[11] * scale;
        out[12] = a[12] + b[12] * scale;
        out[13] = a[13] + b[13] * scale;
        out[14] = a[14] + b[14] * scale;
        out[15] = a[15] + b[15] * scale;
        return out;
    }
    exports.multiplyScalarAndAdd = multiplyScalarAndAdd;
    /**
     * Returns whether or not the matrices have exactly the same elements in the same position (when compared with ===)
     *
     * @param {ReadonlyMat4} a The first matrix.
     * @param {ReadonlyMat4} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    function exactEquals(a, b) {
        return a[0] === b[0] && a[1] === b[1] && a[2] === b[2] && a[3] === b[3] && a[4] === b[4] && a[5] === b[5] && a[6] === b[6] && a[7] === b[7] && a[8] === b[8] && a[9] === b[9] && a[10] === b[10] && a[11] === b[11] && a[12] === b[12] && a[13] === b[13] && a[14] === b[14] && a[15] === b[15];
    }
    exports.exactEquals = exactEquals;
    /**
     * Returns whether or not the matrices have approximately the same elements in the same position.
     *
     * @param {ReadonlyMat4} a The first matrix.
     * @param {ReadonlyMat4} b The second matrix.
     * @returns {Boolean} True if the matrices are equal, false otherwise.
     */
    function equals(a, b) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3];
        var a4 = a[4], a5 = a[5], a6 = a[6], a7 = a[7];
        var a8 = a[8], a9 = a[9], a10 = a[10], a11 = a[11];
        var a12 = a[12], a13 = a[13], a14 = a[14], a15 = a[15];
        var b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3];
        var b4 = b[4], b5 = b[5], b6 = b[6], b7 = b[7];
        var b8 = b[8], b9 = b[9], b10 = b[10], b11 = b[11];
        var b12 = b[12], b13 = b[13], b14 = b[14], b15 = b[15];
        return Math.abs(a0 - b0) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a0), Math.abs(b0)) && Math.abs(a1 - b1) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a1), Math.abs(b1)) && Math.abs(a2 - b2) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a2), Math.abs(b2)) && Math.abs(a3 - b3) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a3), Math.abs(b3)) && Math.abs(a4 - b4) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a4), Math.abs(b4)) && Math.abs(a5 - b5) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a5), Math.abs(b5)) && Math.abs(a6 - b6) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a6), Math.abs(b6)) && Math.abs(a7 - b7) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a7), Math.abs(b7)) && Math.abs(a8 - b8) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a8), Math.abs(b8)) && Math.abs(a9 - b9) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a9), Math.abs(b9)) && Math.abs(a10 - b10) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a10), Math.abs(b10)) && Math.abs(a11 - b11) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a11), Math.abs(b11)) && Math.abs(a12 - b12) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a12), Math.abs(b12)) && Math.abs(a13 - b13) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a13), Math.abs(b13)) && Math.abs(a14 - b14) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a14), Math.abs(b14)) && Math.abs(a15 - b15) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a15), Math.abs(b15));
    }
    exports.equals = equals;
    /**
     * Alias for {@link mat4.multiply}
     * @function
     */
    exports.mul = multiply;
    /**
     * Alias for {@link mat4.subtract}
     * @function
     */
    exports.sub = subtract;
},
"f83fe7c413": /* gl-matrix/esm/quat.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const glMatrix = tslib_1.__importStar(require("7d825b979e") /* ./common.js */);
    const mat3 = tslib_1.__importStar(require("a025ef02dc") /* ./mat3.js */);
    const vec3 = tslib_1.__importStar(require("63eddc5433") /* ./vec3.js */);
    const vec4 = tslib_1.__importStar(require("11562bccc5") /* ./vec4.js */);
    /**
     * Quaternion
     * @module quat
     */
    /**
     * Creates a new identity quat
     *
     * @returns {quat} a new quaternion
     */
    function create() {
        var out = new glMatrix.ARRAY_TYPE(4);
        if (glMatrix.ARRAY_TYPE != Float32Array) {
            out[0] = 0;
            out[1] = 0;
            out[2] = 0;
        }
        out[3] = 1;
        return out;
    }
    exports.create = create;
    /**
     * Set a quat to the identity quaternion
     *
     * @param {quat} out the receiving quaternion
     * @returns {quat} out
     */
    function identity(out) {
        out[0] = 0;
        out[1] = 0;
        out[2] = 0;
        out[3] = 1;
        return out;
    }
    exports.identity = identity;
    /**
     * Sets a quat from the given angle and rotation axis,
     * then returns it.
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyVec3} axis the axis around which to rotate
     * @param {Number} rad the angle in radians
     * @returns {quat} out
     **/
    function setAxisAngle(out, axis, rad) {
        rad = rad * 0.5;
        var s = Math.sin(rad);
        out[0] = s * axis[0];
        out[1] = s * axis[1];
        out[2] = s * axis[2];
        out[3] = Math.cos(rad);
        return out;
    }
    exports.setAxisAngle = setAxisAngle;
    /**
     * Gets the rotation axis and angle for a given
     *  quaternion. If a quaternion is created with
     *  setAxisAngle, this method will return the same
     *  values as providied in the original parameter list
     *  OR functionally equivalent values.
     * Example: The quaternion formed by axis [0, 0, 1] and
     *  angle -90 is the same as the quaternion formed by
     *  [0, 0, 1] and 270. This method favors the latter.
     * @param  {vec3} out_axis  Vector receiving the axis of rotation
     * @param  {ReadonlyQuat} q     Quaternion to be decomposed
     * @return {Number}     Angle, in radians, of the rotation
     */
    function getAxisAngle(out_axis, q) {
        var rad = Math.acos(q[3]) * 2.0;
        var s = Math.sin(rad / 2.0);
        if (s > glMatrix.EPSILON) {
            out_axis[0] = q[0] / s;
            out_axis[1] = q[1] / s;
            out_axis[2] = q[2] / s;
        }
        else {
            // If s is zero, return any axis (no rotation - axis does not matter)
            out_axis[0] = 1;
            out_axis[1] = 0;
            out_axis[2] = 0;
        }
        return rad;
    }
    exports.getAxisAngle = getAxisAngle;
    /**
     * Gets the angular distance between two unit quaternions
     *
     * @param  {ReadonlyQuat} a     Origin unit quaternion
     * @param  {ReadonlyQuat} b     Destination unit quaternion
     * @return {Number}     Angle, in radians, between the two quaternions
     */
    function getAngle(a, b) {
        var dotproduct = (0, exports.dot)(a, b);
        return Math.acos(2 * dotproduct * dotproduct - 1);
    }
    exports.getAngle = getAngle;
    /**
     * Multiplies two quat's
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a the first operand
     * @param {ReadonlyQuat} b the second operand
     * @returns {quat} out
     */
    function multiply(out, a, b) {
        var ax = a[0], ay = a[1], az = a[2], aw = a[3];
        var bx = b[0], by = b[1], bz = b[2], bw = b[3];
        out[0] = ax * bw + aw * bx + ay * bz - az * by;
        out[1] = ay * bw + aw * by + az * bx - ax * bz;
        out[2] = az * bw + aw * bz + ax * by - ay * bx;
        out[3] = aw * bw - ax * bx - ay * by - az * bz;
        return out;
    }
    exports.multiply = multiply;
    /**
     * Rotates a quaternion by the given angle about the X axis
     *
     * @param {quat} out quat receiving operation result
     * @param {ReadonlyQuat} a quat to rotate
     * @param {number} rad angle (in radians) to rotate
     * @returns {quat} out
     */
    function rotateX(out, a, rad) {
        rad *= 0.5;
        var ax = a[0], ay = a[1], az = a[2], aw = a[3];
        var bx = Math.sin(rad), bw = Math.cos(rad);
        out[0] = ax * bw + aw * bx;
        out[1] = ay * bw + az * bx;
        out[2] = az * bw - ay * bx;
        out[3] = aw * bw - ax * bx;
        return out;
    }
    exports.rotateX = rotateX;
    /**
     * Rotates a quaternion by the given angle about the Y axis
     *
     * @param {quat} out quat receiving operation result
     * @param {ReadonlyQuat} a quat to rotate
     * @param {number} rad angle (in radians) to rotate
     * @returns {quat} out
     */
    function rotateY(out, a, rad) {
        rad *= 0.5;
        var ax = a[0], ay = a[1], az = a[2], aw = a[3];
        var by = Math.sin(rad), bw = Math.cos(rad);
        out[0] = ax * bw - az * by;
        out[1] = ay * bw + aw * by;
        out[2] = az * bw + ax * by;
        out[3] = aw * bw - ay * by;
        return out;
    }
    exports.rotateY = rotateY;
    /**
     * Rotates a quaternion by the given angle about the Z axis
     *
     * @param {quat} out quat receiving operation result
     * @param {ReadonlyQuat} a quat to rotate
     * @param {number} rad angle (in radians) to rotate
     * @returns {quat} out
     */
    function rotateZ(out, a, rad) {
        rad *= 0.5;
        var ax = a[0], ay = a[1], az = a[2], aw = a[3];
        var bz = Math.sin(rad), bw = Math.cos(rad);
        out[0] = ax * bw + ay * bz;
        out[1] = ay * bw - ax * bz;
        out[2] = az * bw + aw * bz;
        out[3] = aw * bw - az * bz;
        return out;
    }
    exports.rotateZ = rotateZ;
    /**
     * Calculates the W component of a quat from the X, Y, and Z components.
     * Assumes that quaternion is 1 unit in length.
     * Any existing W component will be ignored.
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a quat to calculate W component of
     * @returns {quat} out
     */
    function calculateW(out, a) {
        var x = a[0], y = a[1], z = a[2];
        out[0] = x;
        out[1] = y;
        out[2] = z;
        out[3] = Math.sqrt(Math.abs(1.0 - x * x - y * y - z * z));
        return out;
    }
    exports.calculateW = calculateW;
    /**
     * Calculate the exponential of a unit quaternion.
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a quat to calculate the exponential of
     * @returns {quat} out
     */
    function exp(out, a) {
        var x = a[0], y = a[1], z = a[2], w = a[3];
        var r = Math.sqrt(x * x + y * y + z * z);
        var et = Math.exp(w);
        var s = r > 0 ? et * Math.sin(r) / r : 0;
        out[0] = x * s;
        out[1] = y * s;
        out[2] = z * s;
        out[3] = et * Math.cos(r);
        return out;
    }
    exports.exp = exp;
    /**
     * Calculate the natural logarithm of a unit quaternion.
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a quat to calculate the exponential of
     * @returns {quat} out
     */
    function ln(out, a) {
        var x = a[0], y = a[1], z = a[2], w = a[3];
        var r = Math.sqrt(x * x + y * y + z * z);
        var t = r > 0 ? Math.atan2(r, w) / r : 0;
        out[0] = x * t;
        out[1] = y * t;
        out[2] = z * t;
        out[3] = 0.5 * Math.log(x * x + y * y + z * z + w * w);
        return out;
    }
    exports.ln = ln;
    /**
     * Calculate the scalar power of a unit quaternion.
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a quat to calculate the exponential of
     * @param {Number} b amount to scale the quaternion by
     * @returns {quat} out
     */
    function pow(out, a, b) {
        ln(out, a);
        (0, exports.scale)(out, out, b);
        exp(out, out);
        return out;
    }
    exports.pow = pow;
    /**
     * Performs a spherical linear interpolation between two quat
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a the first operand
     * @param {ReadonlyQuat} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {quat} out
     */
    function slerp(out, a, b, t) {
        // benchmarks:
        //    http://jsperf.com/quaternion-slerp-implementations
        var ax = a[0], ay = a[1], az = a[2], aw = a[3];
        var bx = b[0], by = b[1], bz = b[2], bw = b[3];
        var omega, cosom, sinom, scale0, scale1; // calc cosine
        cosom = ax * bx + ay * by + az * bz + aw * bw; // adjust signs (if necessary)
        if (cosom < 0.0) {
            cosom = -cosom;
            bx = -bx;
            by = -by;
            bz = -bz;
            bw = -bw;
        } // calculate coefficients
        if (1.0 - cosom > glMatrix.EPSILON) {
            // standard case (slerp)
            omega = Math.acos(cosom);
            sinom = Math.sin(omega);
            scale0 = Math.sin((1.0 - t) * omega) / sinom;
            scale1 = Math.sin(t * omega) / sinom;
        }
        else {
            // "from" and "to" quaternions are very close
            //  ... so we can do a linear interpolation
            scale0 = 1.0 - t;
            scale1 = t;
        } // calculate final values
        out[0] = scale0 * ax + scale1 * bx;
        out[1] = scale0 * ay + scale1 * by;
        out[2] = scale0 * az + scale1 * bz;
        out[3] = scale0 * aw + scale1 * bw;
        return out;
    }
    exports.slerp = slerp;
    /**
     * Generates a random unit quaternion
     *
     * @param {quat} out the receiving quaternion
     * @returns {quat} out
     */
    function random(out) {
        // Implementation of http://planning.cs.uiuc.edu/node198.html
        // TODO: Calling random 3 times is probably not the fastest solution
        var u1 = glMatrix.RANDOM();
        var u2 = glMatrix.RANDOM();
        var u3 = glMatrix.RANDOM();
        var sqrt1MinusU1 = Math.sqrt(1 - u1);
        var sqrtU1 = Math.sqrt(u1);
        out[0] = sqrt1MinusU1 * Math.sin(2.0 * Math.PI * u2);
        out[1] = sqrt1MinusU1 * Math.cos(2.0 * Math.PI * u2);
        out[2] = sqrtU1 * Math.sin(2.0 * Math.PI * u3);
        out[3] = sqrtU1 * Math.cos(2.0 * Math.PI * u3);
        return out;
    }
    exports.random = random;
    /**
     * Calculates the inverse of a quat
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a quat to calculate inverse of
     * @returns {quat} out
     */
    function invert(out, a) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3];
        var dot = a0 * a0 + a1 * a1 + a2 * a2 + a3 * a3;
        var invDot = dot ? 1.0 / dot : 0; // TODO: Would be faster to return [0,0,0,0] immediately if dot == 0
        out[0] = -a0 * invDot;
        out[1] = -a1 * invDot;
        out[2] = -a2 * invDot;
        out[3] = a3 * invDot;
        return out;
    }
    exports.invert = invert;
    /**
     * Calculates the conjugate of a quat
     * If the quaternion is normalized, this function is faster than quat.inverse and produces the same result.
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a quat to calculate conjugate of
     * @returns {quat} out
     */
    function conjugate(out, a) {
        out[0] = -a[0];
        out[1] = -a[1];
        out[2] = -a[2];
        out[3] = a[3];
        return out;
    }
    exports.conjugate = conjugate;
    /**
     * Creates a quaternion from the given 3x3 rotation matrix.
     *
     * NOTE: The resultant quaternion is not normalized, so you should be sure
     * to renormalize the quaternion yourself where necessary.
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyMat3} m rotation matrix
     * @returns {quat} out
     * @function
     */
    function fromMat3(out, m) {
        // Algorithm in Ken Shoemake's article in 1987 SIGGRAPH course notes
        // article "Quaternion Calculus and Fast Animation".
        var fTrace = m[0] + m[4] + m[8];
        var fRoot;
        if (fTrace > 0.0) {
            // |w| > 1/2, may as well choose w > 1/2
            fRoot = Math.sqrt(fTrace + 1.0); // 2w
            out[3] = 0.5 * fRoot;
            fRoot = 0.5 / fRoot; // 1/(4w)
            out[0] = (m[5] - m[7]) * fRoot;
            out[1] = (m[6] - m[2]) * fRoot;
            out[2] = (m[1] - m[3]) * fRoot;
        }
        else {
            // |w| <= 1/2
            var i = 0;
            if (m[4] > m[0])
                i = 1;
            if (m[8] > m[i * 3 + i])
                i = 2;
            var j = (i + 1) % 3;
            var k = (i + 2) % 3;
            fRoot = Math.sqrt(m[i * 3 + i] - m[j * 3 + j] - m[k * 3 + k] + 1.0);
            out[i] = 0.5 * fRoot;
            fRoot = 0.5 / fRoot;
            out[3] = (m[j * 3 + k] - m[k * 3 + j]) * fRoot;
            out[j] = (m[j * 3 + i] + m[i * 3 + j]) * fRoot;
            out[k] = (m[k * 3 + i] + m[i * 3 + k]) * fRoot;
        }
        return out;
    }
    exports.fromMat3 = fromMat3;
    /**
     * Creates a quaternion from the given euler angle x, y, z.
     *
     * @param {quat} out the receiving quaternion
     * @param {x} Angle to rotate around X axis in degrees.
     * @param {y} Angle to rotate around Y axis in degrees.
     * @param {z} Angle to rotate around Z axis in degrees.
     * @returns {quat} out
     * @function
     */
    function fromEuler(out, x, y, z) {
        var halfToRad = 0.5 * Math.PI / 180.0;
        x *= halfToRad;
        y *= halfToRad;
        z *= halfToRad;
        var sx = Math.sin(x);
        var cx = Math.cos(x);
        var sy = Math.sin(y);
        var cy = Math.cos(y);
        var sz = Math.sin(z);
        var cz = Math.cos(z);
        out[0] = sx * cy * cz - cx * sy * sz;
        out[1] = cx * sy * cz + sx * cy * sz;
        out[2] = cx * cy * sz - sx * sy * cz;
        out[3] = cx * cy * cz + sx * sy * sz;
        return out;
    }
    exports.fromEuler = fromEuler;
    /**
     * Returns a string representation of a quatenion
     *
     * @param {ReadonlyQuat} a vector to represent as a string
     * @returns {String} string representation of the vector
     */
    function str(a) {
        return "quat(" + a[0] + ", " + a[1] + ", " + a[2] + ", " + a[3] + ")";
    }
    exports.str = str;
    /**
     * Creates a new quat initialized with values from an existing quaternion
     *
     * @param {ReadonlyQuat} a quaternion to clone
     * @returns {quat} a new quaternion
     * @function
     */
    exports.clone = vec4.clone;
    /**
     * Creates a new quat initialized with the given values
     *
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @param {Number} w W component
     * @returns {quat} a new quaternion
     * @function
     */
    exports.fromValues = vec4.fromValues;
    /**
     * Copy the values from one quat to another
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a the source quaternion
     * @returns {quat} out
     * @function
     */
    exports.copy = vec4.copy;
    /**
     * Set the components of a quat to the given values
     *
     * @param {quat} out the receiving quaternion
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @param {Number} w W component
     * @returns {quat} out
     * @function
     */
    exports.set = vec4.set;
    /**
     * Adds two quat's
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a the first operand
     * @param {ReadonlyQuat} b the second operand
     * @returns {quat} out
     * @function
     */
    exports.add = vec4.add;
    /**
     * Alias for {@link quat.multiply}
     * @function
     */
    exports.mul = multiply;
    /**
     * Scales a quat by a scalar number
     *
     * @param {quat} out the receiving vector
     * @param {ReadonlyQuat} a the vector to scale
     * @param {Number} b amount to scale the vector by
     * @returns {quat} out
     * @function
     */
    exports.scale = vec4.scale;
    /**
     * Calculates the dot product of two quat's
     *
     * @param {ReadonlyQuat} a the first operand
     * @param {ReadonlyQuat} b the second operand
     * @returns {Number} dot product of a and b
     * @function
     */
    exports.dot = vec4.dot;
    /**
     * Performs a linear interpolation between two quat's
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a the first operand
     * @param {ReadonlyQuat} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {quat} out
     * @function
     */
    exports.lerp = vec4.lerp;
    /**
     * Calculates the length of a quat
     *
     * @param {ReadonlyQuat} a vector to calculate length of
     * @returns {Number} length of a
     */
    exports.length = vec4.length;
    /**
     * Alias for {@link quat.length}
     * @function
     */
    exports.len = exports.length;
    /**
     * Calculates the squared length of a quat
     *
     * @param {ReadonlyQuat} a vector to calculate squared length of
     * @returns {Number} squared length of a
     * @function
     */
    exports.squaredLength = vec4.squaredLength;
    /**
     * Alias for {@link quat.squaredLength}
     * @function
     */
    exports.sqrLen = exports.squaredLength;
    /**
     * Normalize a quat
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a quaternion to normalize
     * @returns {quat} out
     * @function
     */
    exports.normalize = vec4.normalize;
    /**
     * Returns whether or not the quaternions have exactly the same elements in the same position (when compared with ===)
     *
     * @param {ReadonlyQuat} a The first quaternion.
     * @param {ReadonlyQuat} b The second quaternion.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    exports.exactEquals = vec4.exactEquals;
    /**
     * Returns whether or not the quaternions have approximately the same elements in the same position.
     *
     * @param {ReadonlyQuat} a The first vector.
     * @param {ReadonlyQuat} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    exports.equals = vec4.equals;
    /**
     * Sets a quaternion to represent the shortest rotation from one
     * vector to another.
     *
     * Both vectors are assumed to be unit length.
     *
     * @param {quat} out the receiving quaternion.
     * @param {ReadonlyVec3} a the initial vector
     * @param {ReadonlyVec3} b the destination vector
     * @returns {quat} out
     */
    exports.rotationTo = function () {
        var tmpvec3 = vec3.create();
        var xUnitVec3 = vec3.fromValues(1, 0, 0);
        var yUnitVec3 = vec3.fromValues(0, 1, 0);
        return function (out, a, b) {
            var dot = vec3.dot(a, b);
            if (dot < -0.999999) {
                vec3.cross(tmpvec3, xUnitVec3, a);
                if (vec3.len(tmpvec3) < 0.000001)
                    vec3.cross(tmpvec3, yUnitVec3, a);
                vec3.normalize(tmpvec3, tmpvec3);
                setAxisAngle(out, tmpvec3, Math.PI);
                return out;
            }
            else if (dot > 0.999999) {
                out[0] = 0;
                out[1] = 0;
                out[2] = 0;
                out[3] = 1;
                return out;
            }
            else {
                vec3.cross(tmpvec3, a, b);
                out[0] = tmpvec3[0];
                out[1] = tmpvec3[1];
                out[2] = tmpvec3[2];
                out[3] = 1 + dot;
                return (0, exports.normalize)(out, out);
            }
        };
    }();
    /**
     * Performs a spherical linear interpolation with two control points
     *
     * @param {quat} out the receiving quaternion
     * @param {ReadonlyQuat} a the first operand
     * @param {ReadonlyQuat} b the second operand
     * @param {ReadonlyQuat} c the third operand
     * @param {ReadonlyQuat} d the fourth operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {quat} out
     */
    exports.sqlerp = function () {
        var temp1 = create();
        var temp2 = create();
        return function (out, a, b, c, d, t) {
            slerp(temp1, a, d, t);
            slerp(temp2, b, c, t);
            slerp(out, temp1, temp2, 2 * t * (1 - t));
            return out;
        };
    }();
    /**
     * Sets the specified quaternion with values corresponding to the given
     * axes. Each axis is a vec3 and is expected to be unit length and
     * perpendicular to all other specified axes.
     *
     * @param {ReadonlyVec3} view  the vector representing the viewing direction
     * @param {ReadonlyVec3} right the vector representing the local "right" direction
     * @param {ReadonlyVec3} up    the vector representing the local "up" direction
     * @returns {quat} out
     */
    exports.setAxes = function () {
        var matr = mat3.create();
        return function (out, view, right, up) {
            matr[0] = right[0];
            matr[3] = right[1];
            matr[6] = right[2];
            matr[1] = up[0];
            matr[4] = up[1];
            matr[7] = up[2];
            matr[2] = -view[0];
            matr[5] = -view[1];
            matr[8] = -view[2];
            return (0, exports.normalize)(out, fromMat3(out, matr));
        };
    }();
},
"63eddc5433": /* gl-matrix/esm/vec3.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const glMatrix = tslib_1.__importStar(require("7d825b979e") /* ./common.js */);
    /**
     * 3 Dimensional Vector
     * @module vec3
     */
    /**
     * Creates a new, empty vec3
     *
     * @returns {vec3} a new 3D vector
     */
    function create() {
        var out = new glMatrix.ARRAY_TYPE(3);
        if (glMatrix.ARRAY_TYPE != Float32Array) {
            out[0] = 0;
            out[1] = 0;
            out[2] = 0;
        }
        return out;
    }
    exports.create = create;
    /**
     * Creates a new vec3 initialized with values from an existing vector
     *
     * @param {ReadonlyVec3} a vector to clone
     * @returns {vec3} a new 3D vector
     */
    function clone(a) {
        var out = new glMatrix.ARRAY_TYPE(3);
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        return out;
    }
    exports.clone = clone;
    /**
     * Calculates the length of a vec3
     *
     * @param {ReadonlyVec3} a vector to calculate length of
     * @returns {Number} length of a
     */
    function length(a) {
        var x = a[0];
        var y = a[1];
        var z = a[2];
        return Math.hypot(x, y, z);
    }
    exports.length = length;
    /**
     * Creates a new vec3 initialized with the given values
     *
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @returns {vec3} a new 3D vector
     */
    function fromValues(x, y, z) {
        var out = new glMatrix.ARRAY_TYPE(3);
        out[0] = x;
        out[1] = y;
        out[2] = z;
        return out;
    }
    exports.fromValues = fromValues;
    /**
     * Copy the values from one vec3 to another
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the source vector
     * @returns {vec3} out
     */
    function copy(out, a) {
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        return out;
    }
    exports.copy = copy;
    /**
     * Set the components of a vec3 to the given values
     *
     * @param {vec3} out the receiving vector
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @returns {vec3} out
     */
    function set(out, x, y, z) {
        out[0] = x;
        out[1] = y;
        out[2] = z;
        return out;
    }
    exports.set = set;
    /**
     * Adds two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @returns {vec3} out
     */
    function add(out, a, b) {
        out[0] = a[0] + b[0];
        out[1] = a[1] + b[1];
        out[2] = a[2] + b[2];
        return out;
    }
    exports.add = add;
    /**
     * Subtracts vector b from vector a
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @returns {vec3} out
     */
    function subtract(out, a, b) {
        out[0] = a[0] - b[0];
        out[1] = a[1] - b[1];
        out[2] = a[2] - b[2];
        return out;
    }
    exports.subtract = subtract;
    /**
     * Multiplies two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @returns {vec3} out
     */
    function multiply(out, a, b) {
        out[0] = a[0] * b[0];
        out[1] = a[1] * b[1];
        out[2] = a[2] * b[2];
        return out;
    }
    exports.multiply = multiply;
    /**
     * Divides two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @returns {vec3} out
     */
    function divide(out, a, b) {
        out[0] = a[0] / b[0];
        out[1] = a[1] / b[1];
        out[2] = a[2] / b[2];
        return out;
    }
    exports.divide = divide;
    /**
     * Math.ceil the components of a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a vector to ceil
     * @returns {vec3} out
     */
    function ceil(out, a) {
        out[0] = Math.ceil(a[0]);
        out[1] = Math.ceil(a[1]);
        out[2] = Math.ceil(a[2]);
        return out;
    }
    exports.ceil = ceil;
    /**
     * Math.floor the components of a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a vector to floor
     * @returns {vec3} out
     */
    function floor(out, a) {
        out[0] = Math.floor(a[0]);
        out[1] = Math.floor(a[1]);
        out[2] = Math.floor(a[2]);
        return out;
    }
    exports.floor = floor;
    /**
     * Returns the minimum of two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @returns {vec3} out
     */
    function min(out, a, b) {
        out[0] = Math.min(a[0], b[0]);
        out[1] = Math.min(a[1], b[1]);
        out[2] = Math.min(a[2], b[2]);
        return out;
    }
    exports.min = min;
    /**
     * Returns the maximum of two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @returns {vec3} out
     */
    function max(out, a, b) {
        out[0] = Math.max(a[0], b[0]);
        out[1] = Math.max(a[1], b[1]);
        out[2] = Math.max(a[2], b[2]);
        return out;
    }
    exports.max = max;
    /**
     * Math.round the components of a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a vector to round
     * @returns {vec3} out
     */
    function round(out, a) {
        out[0] = Math.round(a[0]);
        out[1] = Math.round(a[1]);
        out[2] = Math.round(a[2]);
        return out;
    }
    exports.round = round;
    /**
     * Scales a vec3 by a scalar number
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the vector to scale
     * @param {Number} b amount to scale the vector by
     * @returns {vec3} out
     */
    function scale(out, a, b) {
        out[0] = a[0] * b;
        out[1] = a[1] * b;
        out[2] = a[2] * b;
        return out;
    }
    exports.scale = scale;
    /**
     * Adds two vec3's after scaling the second operand by a scalar value
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @param {Number} scale the amount to scale b by before adding
     * @returns {vec3} out
     */
    function scaleAndAdd(out, a, b, scale) {
        out[0] = a[0] + b[0] * scale;
        out[1] = a[1] + b[1] * scale;
        out[2] = a[2] + b[2] * scale;
        return out;
    }
    exports.scaleAndAdd = scaleAndAdd;
    /**
     * Calculates the euclidian distance between two vec3's
     *
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @returns {Number} distance between a and b
     */
    function distance(a, b) {
        var x = b[0] - a[0];
        var y = b[1] - a[1];
        var z = b[2] - a[2];
        return Math.hypot(x, y, z);
    }
    exports.distance = distance;
    /**
     * Calculates the squared euclidian distance between two vec3's
     *
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @returns {Number} squared distance between a and b
     */
    function squaredDistance(a, b) {
        var x = b[0] - a[0];
        var y = b[1] - a[1];
        var z = b[2] - a[2];
        return x * x + y * y + z * z;
    }
    exports.squaredDistance = squaredDistance;
    /**
     * Calculates the squared length of a vec3
     *
     * @param {ReadonlyVec3} a vector to calculate squared length of
     * @returns {Number} squared length of a
     */
    function squaredLength(a) {
        var x = a[0];
        var y = a[1];
        var z = a[2];
        return x * x + y * y + z * z;
    }
    exports.squaredLength = squaredLength;
    /**
     * Negates the components of a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a vector to negate
     * @returns {vec3} out
     */
    function negate(out, a) {
        out[0] = -a[0];
        out[1] = -a[1];
        out[2] = -a[2];
        return out;
    }
    exports.negate = negate;
    /**
     * Returns the inverse of the components of a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a vector to invert
     * @returns {vec3} out
     */
    function inverse(out, a) {
        out[0] = 1.0 / a[0];
        out[1] = 1.0 / a[1];
        out[2] = 1.0 / a[2];
        return out;
    }
    exports.inverse = inverse;
    /**
     * Normalize a vec3
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a vector to normalize
     * @returns {vec3} out
     */
    function normalize(out, a) {
        var x = a[0];
        var y = a[1];
        var z = a[2];
        var len = x * x + y * y + z * z;
        if (len > 0) {
            //TODO: evaluate use of glm_invsqrt here?
            len = 1 / Math.sqrt(len);
        }
        out[0] = a[0] * len;
        out[1] = a[1] * len;
        out[2] = a[2] * len;
        return out;
    }
    exports.normalize = normalize;
    /**
     * Calculates the dot product of two vec3's
     *
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @returns {Number} dot product of a and b
     */
    function dot(a, b) {
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    }
    exports.dot = dot;
    /**
     * Computes the cross product of two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @returns {vec3} out
     */
    function cross(out, a, b) {
        var ax = a[0], ay = a[1], az = a[2];
        var bx = b[0], by = b[1], bz = b[2];
        out[0] = ay * bz - az * by;
        out[1] = az * bx - ax * bz;
        out[2] = ax * by - ay * bx;
        return out;
    }
    exports.cross = cross;
    /**
     * Performs a linear interpolation between two vec3's
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {vec3} out
     */
    function lerp(out, a, b, t) {
        var ax = a[0];
        var ay = a[1];
        var az = a[2];
        out[0] = ax + t * (b[0] - ax);
        out[1] = ay + t * (b[1] - ay);
        out[2] = az + t * (b[2] - az);
        return out;
    }
    exports.lerp = lerp;
    /**
     * Performs a hermite interpolation with two control points
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @param {ReadonlyVec3} c the third operand
     * @param {ReadonlyVec3} d the fourth operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {vec3} out
     */
    function hermite(out, a, b, c, d, t) {
        var factorTimes2 = t * t;
        var factor1 = factorTimes2 * (2 * t - 3) + 1;
        var factor2 = factorTimes2 * (t - 2) + t;
        var factor3 = factorTimes2 * (t - 1);
        var factor4 = factorTimes2 * (3 - 2 * t);
        out[0] = a[0] * factor1 + b[0] * factor2 + c[0] * factor3 + d[0] * factor4;
        out[1] = a[1] * factor1 + b[1] * factor2 + c[1] * factor3 + d[1] * factor4;
        out[2] = a[2] * factor1 + b[2] * factor2 + c[2] * factor3 + d[2] * factor4;
        return out;
    }
    exports.hermite = hermite;
    /**
     * Performs a bezier interpolation with two control points
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the first operand
     * @param {ReadonlyVec3} b the second operand
     * @param {ReadonlyVec3} c the third operand
     * @param {ReadonlyVec3} d the fourth operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {vec3} out
     */
    function bezier(out, a, b, c, d, t) {
        var inverseFactor = 1 - t;
        var inverseFactorTimesTwo = inverseFactor * inverseFactor;
        var factorTimes2 = t * t;
        var factor1 = inverseFactorTimesTwo * inverseFactor;
        var factor2 = 3 * t * inverseFactorTimesTwo;
        var factor3 = 3 * factorTimes2 * inverseFactor;
        var factor4 = factorTimes2 * t;
        out[0] = a[0] * factor1 + b[0] * factor2 + c[0] * factor3 + d[0] * factor4;
        out[1] = a[1] * factor1 + b[1] * factor2 + c[1] * factor3 + d[1] * factor4;
        out[2] = a[2] * factor1 + b[2] * factor2 + c[2] * factor3 + d[2] * factor4;
        return out;
    }
    exports.bezier = bezier;
    /**
     * Generates a random vector with the given scale
     *
     * @param {vec3} out the receiving vector
     * @param {Number} [scale] Length of the resulting vector. If ommitted, a unit vector will be returned
     * @returns {vec3} out
     */
    function random(out, scale) {
        scale = scale || 1.0;
        var r = glMatrix.RANDOM() * 2.0 * Math.PI;
        var z = glMatrix.RANDOM() * 2.0 - 1.0;
        var zScale = Math.sqrt(1.0 - z * z) * scale;
        out[0] = Math.cos(r) * zScale;
        out[1] = Math.sin(r) * zScale;
        out[2] = z * scale;
        return out;
    }
    exports.random = random;
    /**
     * Transforms the vec3 with a mat4.
     * 4th vector component is implicitly '1'
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the vector to transform
     * @param {ReadonlyMat4} m matrix to transform with
     * @returns {vec3} out
     */
    function transformMat4(out, a, m) {
        var x = a[0], y = a[1], z = a[2];
        var w = m[3] * x + m[7] * y + m[11] * z + m[15];
        w = w || 1.0;
        out[0] = (m[0] * x + m[4] * y + m[8] * z + m[12]) / w;
        out[1] = (m[1] * x + m[5] * y + m[9] * z + m[13]) / w;
        out[2] = (m[2] * x + m[6] * y + m[10] * z + m[14]) / w;
        return out;
    }
    exports.transformMat4 = transformMat4;
    /**
     * Transforms the vec3 with a mat3.
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the vector to transform
     * @param {ReadonlyMat3} m the 3x3 matrix to transform with
     * @returns {vec3} out
     */
    function transformMat3(out, a, m) {
        var x = a[0], y = a[1], z = a[2];
        out[0] = x * m[0] + y * m[3] + z * m[6];
        out[1] = x * m[1] + y * m[4] + z * m[7];
        out[2] = x * m[2] + y * m[5] + z * m[8];
        return out;
    }
    exports.transformMat3 = transformMat3;
    /**
     * Transforms the vec3 with a quat
     * Can also be used for dual quaternions. (Multiply it with the real part)
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec3} a the vector to transform
     * @param {ReadonlyQuat} q quaternion to transform with
     * @returns {vec3} out
     */
    function transformQuat(out, a, q) {
        // benchmarks: https://jsperf.com/quaternion-transform-vec3-implementations-fixed
        var qx = q[0], qy = q[1], qz = q[2], qw = q[3];
        var x = a[0], y = a[1], z = a[2]; // var qvec = [qx, qy, qz];
        // var uv = vec3.cross([], qvec, a);
        var uvx = qy * z - qz * y, uvy = qz * x - qx * z, uvz = qx * y - qy * x; // var uuv = vec3.cross([], qvec, uv);
        var uuvx = qy * uvz - qz * uvy, uuvy = qz * uvx - qx * uvz, uuvz = qx * uvy - qy * uvx; // vec3.scale(uv, uv, 2 * w);
        var w2 = qw * 2;
        uvx *= w2;
        uvy *= w2;
        uvz *= w2; // vec3.scale(uuv, uuv, 2);
        uuvx *= 2;
        uuvy *= 2;
        uuvz *= 2; // return vec3.add(out, a, vec3.add(out, uv, uuv));
        out[0] = x + uvx + uuvx;
        out[1] = y + uvy + uuvy;
        out[2] = z + uvz + uuvz;
        return out;
    }
    exports.transformQuat = transformQuat;
    /**
     * Rotate a 3D vector around the x-axis
     * @param {vec3} out The receiving vec3
     * @param {ReadonlyVec3} a The vec3 point to rotate
     * @param {ReadonlyVec3} b The origin of the rotation
     * @param {Number} rad The angle of rotation in radians
     * @returns {vec3} out
     */
    function rotateX(out, a, b, rad) {
        var p = [], r = []; //Translate point to the origin
        p[0] = a[0] - b[0];
        p[1] = a[1] - b[1];
        p[2] = a[2] - b[2]; //perform rotation
        r[0] = p[0];
        r[1] = p[1] * Math.cos(rad) - p[2] * Math.sin(rad);
        r[2] = p[1] * Math.sin(rad) + p[2] * Math.cos(rad); //translate to correct position
        out[0] = r[0] + b[0];
        out[1] = r[1] + b[1];
        out[2] = r[2] + b[2];
        return out;
    }
    exports.rotateX = rotateX;
    /**
     * Rotate a 3D vector around the y-axis
     * @param {vec3} out The receiving vec3
     * @param {ReadonlyVec3} a The vec3 point to rotate
     * @param {ReadonlyVec3} b The origin of the rotation
     * @param {Number} rad The angle of rotation in radians
     * @returns {vec3} out
     */
    function rotateY(out, a, b, rad) {
        var p = [], r = []; //Translate point to the origin
        p[0] = a[0] - b[0];
        p[1] = a[1] - b[1];
        p[2] = a[2] - b[2]; //perform rotation
        r[0] = p[2] * Math.sin(rad) + p[0] * Math.cos(rad);
        r[1] = p[1];
        r[2] = p[2] * Math.cos(rad) - p[0] * Math.sin(rad); //translate to correct position
        out[0] = r[0] + b[0];
        out[1] = r[1] + b[1];
        out[2] = r[2] + b[2];
        return out;
    }
    exports.rotateY = rotateY;
    /**
     * Rotate a 3D vector around the z-axis
     * @param {vec3} out The receiving vec3
     * @param {ReadonlyVec3} a The vec3 point to rotate
     * @param {ReadonlyVec3} b The origin of the rotation
     * @param {Number} rad The angle of rotation in radians
     * @returns {vec3} out
     */
    function rotateZ(out, a, b, rad) {
        var p = [], r = []; //Translate point to the origin
        p[0] = a[0] - b[0];
        p[1] = a[1] - b[1];
        p[2] = a[2] - b[2]; //perform rotation
        r[0] = p[0] * Math.cos(rad) - p[1] * Math.sin(rad);
        r[1] = p[0] * Math.sin(rad) + p[1] * Math.cos(rad);
        r[2] = p[2]; //translate to correct position
        out[0] = r[0] + b[0];
        out[1] = r[1] + b[1];
        out[2] = r[2] + b[2];
        return out;
    }
    exports.rotateZ = rotateZ;
    /**
     * Get the angle between two 3D vectors
     * @param {ReadonlyVec3} a The first operand
     * @param {ReadonlyVec3} b The second operand
     * @returns {Number} The angle in radians
     */
    function angle(a, b) {
        var ax = a[0], ay = a[1], az = a[2], bx = b[0], by = b[1], bz = b[2], mag1 = Math.sqrt(ax * ax + ay * ay + az * az), mag2 = Math.sqrt(bx * bx + by * by + bz * bz), mag = mag1 * mag2, cosine = mag && dot(a, b) / mag;
        return Math.acos(Math.min(Math.max(cosine, -1), 1));
    }
    exports.angle = angle;
    /**
     * Set the components of a vec3 to zero
     *
     * @param {vec3} out the receiving vector
     * @returns {vec3} out
     */
    function zero(out) {
        out[0] = 0.0;
        out[1] = 0.0;
        out[2] = 0.0;
        return out;
    }
    exports.zero = zero;
    /**
     * Returns a string representation of a vector
     *
     * @param {ReadonlyVec3} a vector to represent as a string
     * @returns {String} string representation of the vector
     */
    function str(a) {
        return "vec3(" + a[0] + ", " + a[1] + ", " + a[2] + ")";
    }
    exports.str = str;
    /**
     * Returns whether or not the vectors have exactly the same elements in the same position (when compared with ===)
     *
     * @param {ReadonlyVec3} a The first vector.
     * @param {ReadonlyVec3} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    function exactEquals(a, b) {
        return a[0] === b[0] && a[1] === b[1] && a[2] === b[2];
    }
    exports.exactEquals = exactEquals;
    /**
     * Returns whether or not the vectors have approximately the same elements in the same position.
     *
     * @param {ReadonlyVec3} a The first vector.
     * @param {ReadonlyVec3} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    function equals(a, b) {
        var a0 = a[0], a1 = a[1], a2 = a[2];
        var b0 = b[0], b1 = b[1], b2 = b[2];
        return Math.abs(a0 - b0) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a0), Math.abs(b0)) && Math.abs(a1 - b1) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a1), Math.abs(b1)) && Math.abs(a2 - b2) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a2), Math.abs(b2));
    }
    exports.equals = equals;
    /**
     * Alias for {@link vec3.subtract}
     * @function
     */
    exports.sub = subtract;
    /**
     * Alias for {@link vec3.multiply}
     * @function
     */
    exports.mul = multiply;
    /**
     * Alias for {@link vec3.divide}
     * @function
     */
    exports.div = divide;
    /**
     * Alias for {@link vec3.distance}
     * @function
     */
    exports.dist = distance;
    /**
     * Alias for {@link vec3.squaredDistance}
     * @function
     */
    exports.sqrDist = squaredDistance;
    /**
     * Alias for {@link vec3.length}
     * @function
     */
    exports.len = length;
    /**
     * Alias for {@link vec3.squaredLength}
     * @function
     */
    exports.sqrLen = squaredLength;
    /**
     * Perform some operation over an array of vec3s.
     *
     * @param {Array} a the array of vectors to iterate over
     * @param {Number} stride Number of elements between the start of each vec3. If 0 assumes tightly packed
     * @param {Number} offset Number of elements to skip at the beginning of the array
     * @param {Number} count Number of vec3s to iterate over. If 0 iterates over entire array
     * @param {Function} fn Function to call for each vector in the array
     * @param {Object} [arg] additional argument to pass to fn
     * @returns {Array} a
     * @function
     */
    exports.forEach = function () {
        var vec = create();
        return function (a, stride, offset, count, fn, arg) {
            var i, l;
            if (!stride) {
                stride = 3;
            }
            if (!offset) {
                offset = 0;
            }
            if (count) {
                l = Math.min(count * stride + offset, a.length);
            }
            else {
                l = a.length;
            }
            for (i = offset; i < l; i += stride) {
                vec[0] = a[i];
                vec[1] = a[i + 1];
                vec[2] = a[i + 2];
                fn(vec, vec, arg);
                a[i] = vec[0];
                a[i + 1] = vec[1];
                a[i + 2] = vec[2];
            }
            return a;
        };
    }();
},
"11562bccc5": /* gl-matrix/esm/vec4.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const glMatrix = tslib_1.__importStar(require("7d825b979e") /* ./common.js */);
    /**
     * 4 Dimensional Vector
     * @module vec4
     */
    /**
     * Creates a new, empty vec4
     *
     * @returns {vec4} a new 4D vector
     */
    function create() {
        var out = new glMatrix.ARRAY_TYPE(4);
        if (glMatrix.ARRAY_TYPE != Float32Array) {
            out[0] = 0;
            out[1] = 0;
            out[2] = 0;
            out[3] = 0;
        }
        return out;
    }
    exports.create = create;
    /**
     * Creates a new vec4 initialized with values from an existing vector
     *
     * @param {ReadonlyVec4} a vector to clone
     * @returns {vec4} a new 4D vector
     */
    function clone(a) {
        var out = new glMatrix.ARRAY_TYPE(4);
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[3];
        return out;
    }
    exports.clone = clone;
    /**
     * Creates a new vec4 initialized with the given values
     *
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @param {Number} w W component
     * @returns {vec4} a new 4D vector
     */
    function fromValues(x, y, z, w) {
        var out = new glMatrix.ARRAY_TYPE(4);
        out[0] = x;
        out[1] = y;
        out[2] = z;
        out[3] = w;
        return out;
    }
    exports.fromValues = fromValues;
    /**
     * Copy the values from one vec4 to another
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the source vector
     * @returns {vec4} out
     */
    function copy(out, a) {
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[3];
        return out;
    }
    exports.copy = copy;
    /**
     * Set the components of a vec4 to the given values
     *
     * @param {vec4} out the receiving vector
     * @param {Number} x X component
     * @param {Number} y Y component
     * @param {Number} z Z component
     * @param {Number} w W component
     * @returns {vec4} out
     */
    function set(out, x, y, z, w) {
        out[0] = x;
        out[1] = y;
        out[2] = z;
        out[3] = w;
        return out;
    }
    exports.set = set;
    /**
     * Adds two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the first operand
     * @param {ReadonlyVec4} b the second operand
     * @returns {vec4} out
     */
    function add(out, a, b) {
        out[0] = a[0] + b[0];
        out[1] = a[1] + b[1];
        out[2] = a[2] + b[2];
        out[3] = a[3] + b[3];
        return out;
    }
    exports.add = add;
    /**
     * Subtracts vector b from vector a
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the first operand
     * @param {ReadonlyVec4} b the second operand
     * @returns {vec4} out
     */
    function subtract(out, a, b) {
        out[0] = a[0] - b[0];
        out[1] = a[1] - b[1];
        out[2] = a[2] - b[2];
        out[3] = a[3] - b[3];
        return out;
    }
    exports.subtract = subtract;
    /**
     * Multiplies two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the first operand
     * @param {ReadonlyVec4} b the second operand
     * @returns {vec4} out
     */
    function multiply(out, a, b) {
        out[0] = a[0] * b[0];
        out[1] = a[1] * b[1];
        out[2] = a[2] * b[2];
        out[3] = a[3] * b[3];
        return out;
    }
    exports.multiply = multiply;
    /**
     * Divides two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the first operand
     * @param {ReadonlyVec4} b the second operand
     * @returns {vec4} out
     */
    function divide(out, a, b) {
        out[0] = a[0] / b[0];
        out[1] = a[1] / b[1];
        out[2] = a[2] / b[2];
        out[3] = a[3] / b[3];
        return out;
    }
    exports.divide = divide;
    /**
     * Math.ceil the components of a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a vector to ceil
     * @returns {vec4} out
     */
    function ceil(out, a) {
        out[0] = Math.ceil(a[0]);
        out[1] = Math.ceil(a[1]);
        out[2] = Math.ceil(a[2]);
        out[3] = Math.ceil(a[3]);
        return out;
    }
    exports.ceil = ceil;
    /**
     * Math.floor the components of a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a vector to floor
     * @returns {vec4} out
     */
    function floor(out, a) {
        out[0] = Math.floor(a[0]);
        out[1] = Math.floor(a[1]);
        out[2] = Math.floor(a[2]);
        out[3] = Math.floor(a[3]);
        return out;
    }
    exports.floor = floor;
    /**
     * Returns the minimum of two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the first operand
     * @param {ReadonlyVec4} b the second operand
     * @returns {vec4} out
     */
    function min(out, a, b) {
        out[0] = Math.min(a[0], b[0]);
        out[1] = Math.min(a[1], b[1]);
        out[2] = Math.min(a[2], b[2]);
        out[3] = Math.min(a[3], b[3]);
        return out;
    }
    exports.min = min;
    /**
     * Returns the maximum of two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the first operand
     * @param {ReadonlyVec4} b the second operand
     * @returns {vec4} out
     */
    function max(out, a, b) {
        out[0] = Math.max(a[0], b[0]);
        out[1] = Math.max(a[1], b[1]);
        out[2] = Math.max(a[2], b[2]);
        out[3] = Math.max(a[3], b[3]);
        return out;
    }
    exports.max = max;
    /**
     * Math.round the components of a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a vector to round
     * @returns {vec4} out
     */
    function round(out, a) {
        out[0] = Math.round(a[0]);
        out[1] = Math.round(a[1]);
        out[2] = Math.round(a[2]);
        out[3] = Math.round(a[3]);
        return out;
    }
    exports.round = round;
    /**
     * Scales a vec4 by a scalar number
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the vector to scale
     * @param {Number} b amount to scale the vector by
     * @returns {vec4} out
     */
    function scale(out, a, b) {
        out[0] = a[0] * b;
        out[1] = a[1] * b;
        out[2] = a[2] * b;
        out[3] = a[3] * b;
        return out;
    }
    exports.scale = scale;
    /**
     * Adds two vec4's after scaling the second operand by a scalar value
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the first operand
     * @param {ReadonlyVec4} b the second operand
     * @param {Number} scale the amount to scale b by before adding
     * @returns {vec4} out
     */
    function scaleAndAdd(out, a, b, scale) {
        out[0] = a[0] + b[0] * scale;
        out[1] = a[1] + b[1] * scale;
        out[2] = a[2] + b[2] * scale;
        out[3] = a[3] + b[3] * scale;
        return out;
    }
    exports.scaleAndAdd = scaleAndAdd;
    /**
     * Calculates the euclidian distance between two vec4's
     *
     * @param {ReadonlyVec4} a the first operand
     * @param {ReadonlyVec4} b the second operand
     * @returns {Number} distance between a and b
     */
    function distance(a, b) {
        var x = b[0] - a[0];
        var y = b[1] - a[1];
        var z = b[2] - a[2];
        var w = b[3] - a[3];
        return Math.hypot(x, y, z, w);
    }
    exports.distance = distance;
    /**
     * Calculates the squared euclidian distance between two vec4's
     *
     * @param {ReadonlyVec4} a the first operand
     * @param {ReadonlyVec4} b the second operand
     * @returns {Number} squared distance between a and b
     */
    function squaredDistance(a, b) {
        var x = b[0] - a[0];
        var y = b[1] - a[1];
        var z = b[2] - a[2];
        var w = b[3] - a[3];
        return x * x + y * y + z * z + w * w;
    }
    exports.squaredDistance = squaredDistance;
    /**
     * Calculates the length of a vec4
     *
     * @param {ReadonlyVec4} a vector to calculate length of
     * @returns {Number} length of a
     */
    function length(a) {
        var x = a[0];
        var y = a[1];
        var z = a[2];
        var w = a[3];
        return Math.hypot(x, y, z, w);
    }
    exports.length = length;
    /**
     * Calculates the squared length of a vec4
     *
     * @param {ReadonlyVec4} a vector to calculate squared length of
     * @returns {Number} squared length of a
     */
    function squaredLength(a) {
        var x = a[0];
        var y = a[1];
        var z = a[2];
        var w = a[3];
        return x * x + y * y + z * z + w * w;
    }
    exports.squaredLength = squaredLength;
    /**
     * Negates the components of a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a vector to negate
     * @returns {vec4} out
     */
    function negate(out, a) {
        out[0] = -a[0];
        out[1] = -a[1];
        out[2] = -a[2];
        out[3] = -a[3];
        return out;
    }
    exports.negate = negate;
    /**
     * Returns the inverse of the components of a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a vector to invert
     * @returns {vec4} out
     */
    function inverse(out, a) {
        out[0] = 1.0 / a[0];
        out[1] = 1.0 / a[1];
        out[2] = 1.0 / a[2];
        out[3] = 1.0 / a[3];
        return out;
    }
    exports.inverse = inverse;
    /**
     * Normalize a vec4
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a vector to normalize
     * @returns {vec4} out
     */
    function normalize(out, a) {
        var x = a[0];
        var y = a[1];
        var z = a[2];
        var w = a[3];
        var len = x * x + y * y + z * z + w * w;
        if (len > 0) {
            len = 1 / Math.sqrt(len);
        }
        out[0] = x * len;
        out[1] = y * len;
        out[2] = z * len;
        out[3] = w * len;
        return out;
    }
    exports.normalize = normalize;
    /**
     * Calculates the dot product of two vec4's
     *
     * @param {ReadonlyVec4} a the first operand
     * @param {ReadonlyVec4} b the second operand
     * @returns {Number} dot product of a and b
     */
    function dot(a, b) {
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3];
    }
    exports.dot = dot;
    /**
     * Returns the cross-product of three vectors in a 4-dimensional space
     *
     * @param {ReadonlyVec4} result the receiving vector
     * @param {ReadonlyVec4} U the first vector
     * @param {ReadonlyVec4} V the second vector
     * @param {ReadonlyVec4} W the third vector
     * @returns {vec4} result
     */
    function cross(out, u, v, w) {
        var A = v[0] * w[1] - v[1] * w[0], B = v[0] * w[2] - v[2] * w[0], C = v[0] * w[3] - v[3] * w[0], D = v[1] * w[2] - v[2] * w[1], E = v[1] * w[3] - v[3] * w[1], F = v[2] * w[3] - v[3] * w[2];
        var G = u[0];
        var H = u[1];
        var I = u[2];
        var J = u[3];
        out[0] = H * F - I * E + J * D;
        out[1] = -(G * F) + I * C - J * B;
        out[2] = G * E - H * C + J * A;
        out[3] = -(G * D) + H * B - I * A;
        return out;
    }
    exports.cross = cross;
    /**
     * Performs a linear interpolation between two vec4's
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the first operand
     * @param {ReadonlyVec4} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {vec4} out
     */
    function lerp(out, a, b, t) {
        var ax = a[0];
        var ay = a[1];
        var az = a[2];
        var aw = a[3];
        out[0] = ax + t * (b[0] - ax);
        out[1] = ay + t * (b[1] - ay);
        out[2] = az + t * (b[2] - az);
        out[3] = aw + t * (b[3] - aw);
        return out;
    }
    exports.lerp = lerp;
    /**
     * Generates a random vector with the given scale
     *
     * @param {vec4} out the receiving vector
     * @param {Number} [scale] Length of the resulting vector. If ommitted, a unit vector will be returned
     * @returns {vec4} out
     */
    function random(out, scale) {
        scale = scale || 1.0; // Marsaglia, George. Choosing a Point from the Surface of a
        // Sphere. Ann. Math. Statist. 43 (1972), no. 2, 645--646.
        // http://projecteuclid.org/euclid.aoms/1177692644;
        var v1, v2, v3, v4;
        var s1, s2;
        do {
            v1 = glMatrix.RANDOM() * 2 - 1;
            v2 = glMatrix.RANDOM() * 2 - 1;
            s1 = v1 * v1 + v2 * v2;
        } while (s1 >= 1);
        do {
            v3 = glMatrix.RANDOM() * 2 - 1;
            v4 = glMatrix.RANDOM() * 2 - 1;
            s2 = v3 * v3 + v4 * v4;
        } while (s2 >= 1);
        var d = Math.sqrt((1 - s1) / s2);
        out[0] = scale * v1;
        out[1] = scale * v2;
        out[2] = scale * v3 * d;
        out[3] = scale * v4 * d;
        return out;
    }
    exports.random = random;
    /**
     * Transforms the vec4 with a mat4.
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the vector to transform
     * @param {ReadonlyMat4} m matrix to transform with
     * @returns {vec4} out
     */
    function transformMat4(out, a, m) {
        var x = a[0], y = a[1], z = a[2], w = a[3];
        out[0] = m[0] * x + m[4] * y + m[8] * z + m[12] * w;
        out[1] = m[1] * x + m[5] * y + m[9] * z + m[13] * w;
        out[2] = m[2] * x + m[6] * y + m[10] * z + m[14] * w;
        out[3] = m[3] * x + m[7] * y + m[11] * z + m[15] * w;
        return out;
    }
    exports.transformMat4 = transformMat4;
    /**
     * Transforms the vec4 with a quat
     *
     * @param {vec4} out the receiving vector
     * @param {ReadonlyVec4} a the vector to transform
     * @param {ReadonlyQuat} q quaternion to transform with
     * @returns {vec4} out
     */
    function transformQuat(out, a, q) {
        var x = a[0], y = a[1], z = a[2];
        var qx = q[0], qy = q[1], qz = q[2], qw = q[3]; // calculate quat * vec
        var ix = qw * x + qy * z - qz * y;
        var iy = qw * y + qz * x - qx * z;
        var iz = qw * z + qx * y - qy * x;
        var iw = -qx * x - qy * y - qz * z; // calculate result * inverse quat
        out[0] = ix * qw + iw * -qx + iy * -qz - iz * -qy;
        out[1] = iy * qw + iw * -qy + iz * -qx - ix * -qz;
        out[2] = iz * qw + iw * -qz + ix * -qy - iy * -qx;
        out[3] = a[3];
        return out;
    }
    exports.transformQuat = transformQuat;
    /**
     * Set the components of a vec4 to zero
     *
     * @param {vec4} out the receiving vector
     * @returns {vec4} out
     */
    function zero(out) {
        out[0] = 0.0;
        out[1] = 0.0;
        out[2] = 0.0;
        out[3] = 0.0;
        return out;
    }
    exports.zero = zero;
    /**
     * Returns a string representation of a vector
     *
     * @param {ReadonlyVec4} a vector to represent as a string
     * @returns {String} string representation of the vector
     */
    function str(a) {
        return "vec4(" + a[0] + ", " + a[1] + ", " + a[2] + ", " + a[3] + ")";
    }
    exports.str = str;
    /**
     * Returns whether or not the vectors have exactly the same elements in the same position (when compared with ===)
     *
     * @param {ReadonlyVec4} a The first vector.
     * @param {ReadonlyVec4} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    function exactEquals(a, b) {
        return a[0] === b[0] && a[1] === b[1] && a[2] === b[2] && a[3] === b[3];
    }
    exports.exactEquals = exactEquals;
    /**
     * Returns whether or not the vectors have approximately the same elements in the same position.
     *
     * @param {ReadonlyVec4} a The first vector.
     * @param {ReadonlyVec4} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    function equals(a, b) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3];
        var b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3];
        return Math.abs(a0 - b0) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a0), Math.abs(b0)) && Math.abs(a1 - b1) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a1), Math.abs(b1)) && Math.abs(a2 - b2) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a2), Math.abs(b2)) && Math.abs(a3 - b3) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a3), Math.abs(b3));
    }
    exports.equals = equals;
    /**
     * Alias for {@link vec4.subtract}
     * @function
     */
    exports.sub = subtract;
    /**
     * Alias for {@link vec4.multiply}
     * @function
     */
    exports.mul = multiply;
    /**
     * Alias for {@link vec4.divide}
     * @function
     */
    exports.div = divide;
    /**
     * Alias for {@link vec4.distance}
     * @function
     */
    exports.dist = distance;
    /**
     * Alias for {@link vec4.squaredDistance}
     * @function
     */
    exports.sqrDist = squaredDistance;
    /**
     * Alias for {@link vec4.length}
     * @function
     */
    exports.len = length;
    /**
     * Alias for {@link vec4.squaredLength}
     * @function
     */
    exports.sqrLen = squaredLength;
    /**
     * Perform some operation over an array of vec4s.
     *
     * @param {Array} a the array of vectors to iterate over
     * @param {Number} stride Number of elements between the start of each vec4. If 0 assumes tightly packed
     * @param {Number} offset Number of elements to skip at the beginning of the array
     * @param {Number} count Number of vec4s to iterate over. If 0 iterates over entire array
     * @param {Function} fn Function to call for each vector in the array
     * @param {Object} [arg] additional argument to pass to fn
     * @returns {Array} a
     * @function
     */
    exports.forEach = function () {
        var vec = create();
        return function (a, stride, offset, count, fn, arg) {
            var i, l;
            if (!stride) {
                stride = 4;
            }
            if (!offset) {
                offset = 0;
            }
            if (count) {
                l = Math.min(count * stride + offset, a.length);
            }
            else {
                l = a.length;
            }
            for (i = offset; i < l; i += stride) {
                vec[0] = a[i];
                vec[1] = a[i + 1];
                vec[2] = a[i + 2];
                vec[3] = a[i + 3];
                fn(vec, vec, arg);
                a[i] = vec[0];
                a[i + 1] = vec[1];
                a[i + 2] = vec[2];
                a[i + 3] = vec[3];
            }
            return a;
        };
    }();
},
"fb9294db61": /* gl-matrix/esm/quat2.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const glMatrix = tslib_1.__importStar(require("7d825b979e") /* ./common.js */);
    const quat = tslib_1.__importStar(require("f83fe7c413") /* ./quat.js */);
    const mat4 = tslib_1.__importStar(require("83bad9e639") /* ./mat4.js */);
    /**
     * Dual Quaternion<br>
     * Format: [real, dual]<br>
     * Quaternion format: XYZW<br>
     * Make sure to have normalized dual quaternions, otherwise the functions may not work as intended.<br>
     * @module quat2
     */
    /**
     * Creates a new identity dual quat
     *
     * @returns {quat2} a new dual quaternion [real -> rotation, dual -> translation]
     */
    function create() {
        var dq = new glMatrix.ARRAY_TYPE(8);
        if (glMatrix.ARRAY_TYPE != Float32Array) {
            dq[0] = 0;
            dq[1] = 0;
            dq[2] = 0;
            dq[4] = 0;
            dq[5] = 0;
            dq[6] = 0;
            dq[7] = 0;
        }
        dq[3] = 1;
        return dq;
    }
    exports.create = create;
    /**
     * Creates a new quat initialized with values from an existing quaternion
     *
     * @param {ReadonlyQuat2} a dual quaternion to clone
     * @returns {quat2} new dual quaternion
     * @function
     */
    function clone(a) {
        var dq = new glMatrix.ARRAY_TYPE(8);
        dq[0] = a[0];
        dq[1] = a[1];
        dq[2] = a[2];
        dq[3] = a[3];
        dq[4] = a[4];
        dq[5] = a[5];
        dq[6] = a[6];
        dq[7] = a[7];
        return dq;
    }
    exports.clone = clone;
    /**
     * Creates a new dual quat initialized with the given values
     *
     * @param {Number} x1 X component
     * @param {Number} y1 Y component
     * @param {Number} z1 Z component
     * @param {Number} w1 W component
     * @param {Number} x2 X component
     * @param {Number} y2 Y component
     * @param {Number} z2 Z component
     * @param {Number} w2 W component
     * @returns {quat2} new dual quaternion
     * @function
     */
    function fromValues(x1, y1, z1, w1, x2, y2, z2, w2) {
        var dq = new glMatrix.ARRAY_TYPE(8);
        dq[0] = x1;
        dq[1] = y1;
        dq[2] = z1;
        dq[3] = w1;
        dq[4] = x2;
        dq[5] = y2;
        dq[6] = z2;
        dq[7] = w2;
        return dq;
    }
    exports.fromValues = fromValues;
    /**
     * Creates a new dual quat from the given values (quat and translation)
     *
     * @param {Number} x1 X component
     * @param {Number} y1 Y component
     * @param {Number} z1 Z component
     * @param {Number} w1 W component
     * @param {Number} x2 X component (translation)
     * @param {Number} y2 Y component (translation)
     * @param {Number} z2 Z component (translation)
     * @returns {quat2} new dual quaternion
     * @function
     */
    function fromRotationTranslationValues(x1, y1, z1, w1, x2, y2, z2) {
        var dq = new glMatrix.ARRAY_TYPE(8);
        dq[0] = x1;
        dq[1] = y1;
        dq[2] = z1;
        dq[3] = w1;
        var ax = x2 * 0.5, ay = y2 * 0.5, az = z2 * 0.5;
        dq[4] = ax * w1 + ay * z1 - az * y1;
        dq[5] = ay * w1 + az * x1 - ax * z1;
        dq[6] = az * w1 + ax * y1 - ay * x1;
        dq[7] = -ax * x1 - ay * y1 - az * z1;
        return dq;
    }
    exports.fromRotationTranslationValues = fromRotationTranslationValues;
    /**
     * Creates a dual quat from a quaternion and a translation
     *
     * @param {ReadonlyQuat2} dual quaternion receiving operation result
     * @param {ReadonlyQuat} q a normalized quaternion
     * @param {ReadonlyVec3} t tranlation vector
     * @returns {quat2} dual quaternion receiving operation result
     * @function
     */
    function fromRotationTranslation(out, q, t) {
        var ax = t[0] * 0.5, ay = t[1] * 0.5, az = t[2] * 0.5, bx = q[0], by = q[1], bz = q[2], bw = q[3];
        out[0] = bx;
        out[1] = by;
        out[2] = bz;
        out[3] = bw;
        out[4] = ax * bw + ay * bz - az * by;
        out[5] = ay * bw + az * bx - ax * bz;
        out[6] = az * bw + ax * by - ay * bx;
        out[7] = -ax * bx - ay * by - az * bz;
        return out;
    }
    exports.fromRotationTranslation = fromRotationTranslation;
    /**
     * Creates a dual quat from a translation
     *
     * @param {ReadonlyQuat2} dual quaternion receiving operation result
     * @param {ReadonlyVec3} t translation vector
     * @returns {quat2} dual quaternion receiving operation result
     * @function
     */
    function fromTranslation(out, t) {
        out[0] = 0;
        out[1] = 0;
        out[2] = 0;
        out[3] = 1;
        out[4] = t[0] * 0.5;
        out[5] = t[1] * 0.5;
        out[6] = t[2] * 0.5;
        out[7] = 0;
        return out;
    }
    exports.fromTranslation = fromTranslation;
    /**
     * Creates a dual quat from a quaternion
     *
     * @param {ReadonlyQuat2} dual quaternion receiving operation result
     * @param {ReadonlyQuat} q the quaternion
     * @returns {quat2} dual quaternion receiving operation result
     * @function
     */
    function fromRotation(out, q) {
        out[0] = q[0];
        out[1] = q[1];
        out[2] = q[2];
        out[3] = q[3];
        out[4] = 0;
        out[5] = 0;
        out[6] = 0;
        out[7] = 0;
        return out;
    }
    exports.fromRotation = fromRotation;
    /**
     * Creates a new dual quat from a matrix (4x4)
     *
     * @param {quat2} out the dual quaternion
     * @param {ReadonlyMat4} a the matrix
     * @returns {quat2} dual quat receiving operation result
     * @function
     */
    function fromMat4(out, a) {
        //TODO Optimize this
        var outer = quat.create();
        mat4.getRotation(outer, a);
        var t = new glMatrix.ARRAY_TYPE(3);
        mat4.getTranslation(t, a);
        fromRotationTranslation(out, outer, t);
        return out;
    }
    exports.fromMat4 = fromMat4;
    /**
     * Copy the values from one dual quat to another
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat2} a the source dual quaternion
     * @returns {quat2} out
     * @function
     */
    function copy(out, a) {
        out[0] = a[0];
        out[1] = a[1];
        out[2] = a[2];
        out[3] = a[3];
        out[4] = a[4];
        out[5] = a[5];
        out[6] = a[6];
        out[7] = a[7];
        return out;
    }
    exports.copy = copy;
    /**
     * Set a dual quat to the identity dual quaternion
     *
     * @param {quat2} out the receiving quaternion
     * @returns {quat2} out
     */
    function identity(out) {
        out[0] = 0;
        out[1] = 0;
        out[2] = 0;
        out[3] = 1;
        out[4] = 0;
        out[5] = 0;
        out[6] = 0;
        out[7] = 0;
        return out;
    }
    exports.identity = identity;
    /**
     * Set the components of a dual quat to the given values
     *
     * @param {quat2} out the receiving quaternion
     * @param {Number} x1 X component
     * @param {Number} y1 Y component
     * @param {Number} z1 Z component
     * @param {Number} w1 W component
     * @param {Number} x2 X component
     * @param {Number} y2 Y component
     * @param {Number} z2 Z component
     * @param {Number} w2 W component
     * @returns {quat2} out
     * @function
     */
    function set(out, x1, y1, z1, w1, x2, y2, z2, w2) {
        out[0] = x1;
        out[1] = y1;
        out[2] = z1;
        out[3] = w1;
        out[4] = x2;
        out[5] = y2;
        out[6] = z2;
        out[7] = w2;
        return out;
    }
    exports.set = set;
    /**
     * Gets the real part of a dual quat
     * @param  {quat} out real part
     * @param  {ReadonlyQuat2} a Dual Quaternion
     * @return {quat} real part
     */
    exports.getReal = quat.copy;
    /**
     * Gets the dual part of a dual quat
     * @param  {quat} out dual part
     * @param  {ReadonlyQuat2} a Dual Quaternion
     * @return {quat} dual part
     */
    function getDual(out, a) {
        out[0] = a[4];
        out[1] = a[5];
        out[2] = a[6];
        out[3] = a[7];
        return out;
    }
    exports.getDual = getDual;
    /**
     * Set the real component of a dual quat to the given quaternion
     *
     * @param {quat2} out the receiving quaternion
     * @param {ReadonlyQuat} q a quaternion representing the real part
     * @returns {quat2} out
     * @function
     */
    exports.setReal = quat.copy;
    /**
     * Set the dual component of a dual quat to the given quaternion
     *
     * @param {quat2} out the receiving quaternion
     * @param {ReadonlyQuat} q a quaternion representing the dual part
     * @returns {quat2} out
     * @function
     */
    function setDual(out, q) {
        out[4] = q[0];
        out[5] = q[1];
        out[6] = q[2];
        out[7] = q[3];
        return out;
    }
    exports.setDual = setDual;
    /**
     * Gets the translation of a normalized dual quat
     * @param  {vec3} out translation
     * @param  {ReadonlyQuat2} a Dual Quaternion to be decomposed
     * @return {vec3} translation
     */
    function getTranslation(out, a) {
        var ax = a[4], ay = a[5], az = a[6], aw = a[7], bx = -a[0], by = -a[1], bz = -a[2], bw = a[3];
        out[0] = (ax * bw + aw * bx + ay * bz - az * by) * 2;
        out[1] = (ay * bw + aw * by + az * bx - ax * bz) * 2;
        out[2] = (az * bw + aw * bz + ax * by - ay * bx) * 2;
        return out;
    }
    exports.getTranslation = getTranslation;
    /**
     * Translates a dual quat by the given vector
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat2} a the dual quaternion to translate
     * @param {ReadonlyVec3} v vector to translate by
     * @returns {quat2} out
     */
    function translate(out, a, v) {
        var ax1 = a[0], ay1 = a[1], az1 = a[2], aw1 = a[3], bx1 = v[0] * 0.5, by1 = v[1] * 0.5, bz1 = v[2] * 0.5, ax2 = a[4], ay2 = a[5], az2 = a[6], aw2 = a[7];
        out[0] = ax1;
        out[1] = ay1;
        out[2] = az1;
        out[3] = aw1;
        out[4] = aw1 * bx1 + ay1 * bz1 - az1 * by1 + ax2;
        out[5] = aw1 * by1 + az1 * bx1 - ax1 * bz1 + ay2;
        out[6] = aw1 * bz1 + ax1 * by1 - ay1 * bx1 + az2;
        out[7] = -ax1 * bx1 - ay1 * by1 - az1 * bz1 + aw2;
        return out;
    }
    exports.translate = translate;
    /**
     * Rotates a dual quat around the X axis
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat2} a the dual quaternion to rotate
     * @param {number} rad how far should the rotation be
     * @returns {quat2} out
     */
    function rotateX(out, a, rad) {
        var bx = -a[0], by = -a[1], bz = -a[2], bw = a[3], ax = a[4], ay = a[5], az = a[6], aw = a[7], ax1 = ax * bw + aw * bx + ay * bz - az * by, ay1 = ay * bw + aw * by + az * bx - ax * bz, az1 = az * bw + aw * bz + ax * by - ay * bx, aw1 = aw * bw - ax * bx - ay * by - az * bz;
        quat.rotateX(out, a, rad);
        bx = out[0];
        by = out[1];
        bz = out[2];
        bw = out[3];
        out[4] = ax1 * bw + aw1 * bx + ay1 * bz - az1 * by;
        out[5] = ay1 * bw + aw1 * by + az1 * bx - ax1 * bz;
        out[6] = az1 * bw + aw1 * bz + ax1 * by - ay1 * bx;
        out[7] = aw1 * bw - ax1 * bx - ay1 * by - az1 * bz;
        return out;
    }
    exports.rotateX = rotateX;
    /**
     * Rotates a dual quat around the Y axis
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat2} a the dual quaternion to rotate
     * @param {number} rad how far should the rotation be
     * @returns {quat2} out
     */
    function rotateY(out, a, rad) {
        var bx = -a[0], by = -a[1], bz = -a[2], bw = a[3], ax = a[4], ay = a[5], az = a[6], aw = a[7], ax1 = ax * bw + aw * bx + ay * bz - az * by, ay1 = ay * bw + aw * by + az * bx - ax * bz, az1 = az * bw + aw * bz + ax * by - ay * bx, aw1 = aw * bw - ax * bx - ay * by - az * bz;
        quat.rotateY(out, a, rad);
        bx = out[0];
        by = out[1];
        bz = out[2];
        bw = out[3];
        out[4] = ax1 * bw + aw1 * bx + ay1 * bz - az1 * by;
        out[5] = ay1 * bw + aw1 * by + az1 * bx - ax1 * bz;
        out[6] = az1 * bw + aw1 * bz + ax1 * by - ay1 * bx;
        out[7] = aw1 * bw - ax1 * bx - ay1 * by - az1 * bz;
        return out;
    }
    exports.rotateY = rotateY;
    /**
     * Rotates a dual quat around the Z axis
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat2} a the dual quaternion to rotate
     * @param {number} rad how far should the rotation be
     * @returns {quat2} out
     */
    function rotateZ(out, a, rad) {
        var bx = -a[0], by = -a[1], bz = -a[2], bw = a[3], ax = a[4], ay = a[5], az = a[6], aw = a[7], ax1 = ax * bw + aw * bx + ay * bz - az * by, ay1 = ay * bw + aw * by + az * bx - ax * bz, az1 = az * bw + aw * bz + ax * by - ay * bx, aw1 = aw * bw - ax * bx - ay * by - az * bz;
        quat.rotateZ(out, a, rad);
        bx = out[0];
        by = out[1];
        bz = out[2];
        bw = out[3];
        out[4] = ax1 * bw + aw1 * bx + ay1 * bz - az1 * by;
        out[5] = ay1 * bw + aw1 * by + az1 * bx - ax1 * bz;
        out[6] = az1 * bw + aw1 * bz + ax1 * by - ay1 * bx;
        out[7] = aw1 * bw - ax1 * bx - ay1 * by - az1 * bz;
        return out;
    }
    exports.rotateZ = rotateZ;
    /**
     * Rotates a dual quat by a given quaternion (a * q)
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat2} a the dual quaternion to rotate
     * @param {ReadonlyQuat} q quaternion to rotate by
     * @returns {quat2} out
     */
    function rotateByQuatAppend(out, a, q) {
        var qx = q[0], qy = q[1], qz = q[2], qw = q[3], ax = a[0], ay = a[1], az = a[2], aw = a[3];
        out[0] = ax * qw + aw * qx + ay * qz - az * qy;
        out[1] = ay * qw + aw * qy + az * qx - ax * qz;
        out[2] = az * qw + aw * qz + ax * qy - ay * qx;
        out[3] = aw * qw - ax * qx - ay * qy - az * qz;
        ax = a[4];
        ay = a[5];
        az = a[6];
        aw = a[7];
        out[4] = ax * qw + aw * qx + ay * qz - az * qy;
        out[5] = ay * qw + aw * qy + az * qx - ax * qz;
        out[6] = az * qw + aw * qz + ax * qy - ay * qx;
        out[7] = aw * qw - ax * qx - ay * qy - az * qz;
        return out;
    }
    exports.rotateByQuatAppend = rotateByQuatAppend;
    /**
     * Rotates a dual quat by a given quaternion (q * a)
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat} q quaternion to rotate by
     * @param {ReadonlyQuat2} a the dual quaternion to rotate
     * @returns {quat2} out
     */
    function rotateByQuatPrepend(out, q, a) {
        var qx = q[0], qy = q[1], qz = q[2], qw = q[3], bx = a[0], by = a[1], bz = a[2], bw = a[3];
        out[0] = qx * bw + qw * bx + qy * bz - qz * by;
        out[1] = qy * bw + qw * by + qz * bx - qx * bz;
        out[2] = qz * bw + qw * bz + qx * by - qy * bx;
        out[3] = qw * bw - qx * bx - qy * by - qz * bz;
        bx = a[4];
        by = a[5];
        bz = a[6];
        bw = a[7];
        out[4] = qx * bw + qw * bx + qy * bz - qz * by;
        out[5] = qy * bw + qw * by + qz * bx - qx * bz;
        out[6] = qz * bw + qw * bz + qx * by - qy * bx;
        out[7] = qw * bw - qx * bx - qy * by - qz * bz;
        return out;
    }
    exports.rotateByQuatPrepend = rotateByQuatPrepend;
    /**
     * Rotates a dual quat around a given axis. Does the normalisation automatically
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat2} a the dual quaternion to rotate
     * @param {ReadonlyVec3} axis the axis to rotate around
     * @param {Number} rad how far the rotation should be
     * @returns {quat2} out
     */
    function rotateAroundAxis(out, a, axis, rad) {
        //Special case for rad = 0
        if (Math.abs(rad) < glMatrix.EPSILON) {
            return copy(out, a);
        }
        var axisLength = Math.hypot(axis[0], axis[1], axis[2]);
        rad = rad * 0.5;
        var s = Math.sin(rad);
        var bx = s * axis[0] / axisLength;
        var by = s * axis[1] / axisLength;
        var bz = s * axis[2] / axisLength;
        var bw = Math.cos(rad);
        var ax1 = a[0], ay1 = a[1], az1 = a[2], aw1 = a[3];
        out[0] = ax1 * bw + aw1 * bx + ay1 * bz - az1 * by;
        out[1] = ay1 * bw + aw1 * by + az1 * bx - ax1 * bz;
        out[2] = az1 * bw + aw1 * bz + ax1 * by - ay1 * bx;
        out[3] = aw1 * bw - ax1 * bx - ay1 * by - az1 * bz;
        var ax = a[4], ay = a[5], az = a[6], aw = a[7];
        out[4] = ax * bw + aw * bx + ay * bz - az * by;
        out[5] = ay * bw + aw * by + az * bx - ax * bz;
        out[6] = az * bw + aw * bz + ax * by - ay * bx;
        out[7] = aw * bw - ax * bx - ay * by - az * bz;
        return out;
    }
    exports.rotateAroundAxis = rotateAroundAxis;
    /**
     * Adds two dual quat's
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat2} a the first operand
     * @param {ReadonlyQuat2} b the second operand
     * @returns {quat2} out
     * @function
     */
    function add(out, a, b) {
        out[0] = a[0] + b[0];
        out[1] = a[1] + b[1];
        out[2] = a[2] + b[2];
        out[3] = a[3] + b[3];
        out[4] = a[4] + b[4];
        out[5] = a[5] + b[5];
        out[6] = a[6] + b[6];
        out[7] = a[7] + b[7];
        return out;
    }
    exports.add = add;
    /**
     * Multiplies two dual quat's
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat2} a the first operand
     * @param {ReadonlyQuat2} b the second operand
     * @returns {quat2} out
     */
    function multiply(out, a, b) {
        var ax0 = a[0], ay0 = a[1], az0 = a[2], aw0 = a[3], bx1 = b[4], by1 = b[5], bz1 = b[6], bw1 = b[7], ax1 = a[4], ay1 = a[5], az1 = a[6], aw1 = a[7], bx0 = b[0], by0 = b[1], bz0 = b[2], bw0 = b[3];
        out[0] = ax0 * bw0 + aw0 * bx0 + ay0 * bz0 - az0 * by0;
        out[1] = ay0 * bw0 + aw0 * by0 + az0 * bx0 - ax0 * bz0;
        out[2] = az0 * bw0 + aw0 * bz0 + ax0 * by0 - ay0 * bx0;
        out[3] = aw0 * bw0 - ax0 * bx0 - ay0 * by0 - az0 * bz0;
        out[4] = ax0 * bw1 + aw0 * bx1 + ay0 * bz1 - az0 * by1 + ax1 * bw0 + aw1 * bx0 + ay1 * bz0 - az1 * by0;
        out[5] = ay0 * bw1 + aw0 * by1 + az0 * bx1 - ax0 * bz1 + ay1 * bw0 + aw1 * by0 + az1 * bx0 - ax1 * bz0;
        out[6] = az0 * bw1 + aw0 * bz1 + ax0 * by1 - ay0 * bx1 + az1 * bw0 + aw1 * bz0 + ax1 * by0 - ay1 * bx0;
        out[7] = aw0 * bw1 - ax0 * bx1 - ay0 * by1 - az0 * bz1 + aw1 * bw0 - ax1 * bx0 - ay1 * by0 - az1 * bz0;
        return out;
    }
    exports.multiply = multiply;
    /**
     * Alias for {@link quat2.multiply}
     * @function
     */
    exports.mul = multiply;
    /**
     * Scales a dual quat by a scalar number
     *
     * @param {quat2} out the receiving dual quat
     * @param {ReadonlyQuat2} a the dual quat to scale
     * @param {Number} b amount to scale the dual quat by
     * @returns {quat2} out
     * @function
     */
    function scale(out, a, b) {
        out[0] = a[0] * b;
        out[1] = a[1] * b;
        out[2] = a[2] * b;
        out[3] = a[3] * b;
        out[4] = a[4] * b;
        out[5] = a[5] * b;
        out[6] = a[6] * b;
        out[7] = a[7] * b;
        return out;
    }
    exports.scale = scale;
    /**
     * Calculates the dot product of two dual quat's (The dot product of the real parts)
     *
     * @param {ReadonlyQuat2} a the first operand
     * @param {ReadonlyQuat2} b the second operand
     * @returns {Number} dot product of a and b
     * @function
     */
    exports.dot = quat.dot;
    /**
     * Performs a linear interpolation between two dual quats's
     * NOTE: The resulting dual quaternions won't always be normalized (The error is most noticeable when t = 0.5)
     *
     * @param {quat2} out the receiving dual quat
     * @param {ReadonlyQuat2} a the first operand
     * @param {ReadonlyQuat2} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {quat2} out
     */
    function lerp(out, a, b, t) {
        var mt = 1 - t;
        if ((0, exports.dot)(a, b) < 0)
            t = -t;
        out[0] = a[0] * mt + b[0] * t;
        out[1] = a[1] * mt + b[1] * t;
        out[2] = a[2] * mt + b[2] * t;
        out[3] = a[3] * mt + b[3] * t;
        out[4] = a[4] * mt + b[4] * t;
        out[5] = a[5] * mt + b[5] * t;
        out[6] = a[6] * mt + b[6] * t;
        out[7] = a[7] * mt + b[7] * t;
        return out;
    }
    exports.lerp = lerp;
    /**
     * Calculates the inverse of a dual quat. If they are normalized, conjugate is cheaper
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat2} a dual quat to calculate inverse of
     * @returns {quat2} out
     */
    function invert(out, a) {
        var sqlen = (0, exports.squaredLength)(a);
        out[0] = -a[0] / sqlen;
        out[1] = -a[1] / sqlen;
        out[2] = -a[2] / sqlen;
        out[3] = a[3] / sqlen;
        out[4] = -a[4] / sqlen;
        out[5] = -a[5] / sqlen;
        out[6] = -a[6] / sqlen;
        out[7] = a[7] / sqlen;
        return out;
    }
    exports.invert = invert;
    /**
     * Calculates the conjugate of a dual quat
     * If the dual quaternion is normalized, this function is faster than quat2.inverse and produces the same result.
     *
     * @param {quat2} out the receiving quaternion
     * @param {ReadonlyQuat2} a quat to calculate conjugate of
     * @returns {quat2} out
     */
    function conjugate(out, a) {
        out[0] = -a[0];
        out[1] = -a[1];
        out[2] = -a[2];
        out[3] = a[3];
        out[4] = -a[4];
        out[5] = -a[5];
        out[6] = -a[6];
        out[7] = a[7];
        return out;
    }
    exports.conjugate = conjugate;
    /**
     * Calculates the length of a dual quat
     *
     * @param {ReadonlyQuat2} a dual quat to calculate length of
     * @returns {Number} length of a
     * @function
     */
    exports.length = quat.length;
    /**
     * Alias for {@link quat2.length}
     * @function
     */
    exports.len = exports.length;
    /**
     * Calculates the squared length of a dual quat
     *
     * @param {ReadonlyQuat2} a dual quat to calculate squared length of
     * @returns {Number} squared length of a
     * @function
     */
    exports.squaredLength = quat.squaredLength;
    /**
     * Alias for {@link quat2.squaredLength}
     * @function
     */
    exports.sqrLen = exports.squaredLength;
    /**
     * Normalize a dual quat
     *
     * @param {quat2} out the receiving dual quaternion
     * @param {ReadonlyQuat2} a dual quaternion to normalize
     * @returns {quat2} out
     * @function
     */
    function normalize(out, a) {
        var magnitude = (0, exports.squaredLength)(a);
        if (magnitude > 0) {
            magnitude = Math.sqrt(magnitude);
            var a0 = a[0] / magnitude;
            var a1 = a[1] / magnitude;
            var a2 = a[2] / magnitude;
            var a3 = a[3] / magnitude;
            var b0 = a[4];
            var b1 = a[5];
            var b2 = a[6];
            var b3 = a[7];
            var a_dot_b = a0 * b0 + a1 * b1 + a2 * b2 + a3 * b3;
            out[0] = a0;
            out[1] = a1;
            out[2] = a2;
            out[3] = a3;
            out[4] = (b0 - a0 * a_dot_b) / magnitude;
            out[5] = (b1 - a1 * a_dot_b) / magnitude;
            out[6] = (b2 - a2 * a_dot_b) / magnitude;
            out[7] = (b3 - a3 * a_dot_b) / magnitude;
        }
        return out;
    }
    exports.normalize = normalize;
    /**
     * Returns a string representation of a dual quatenion
     *
     * @param {ReadonlyQuat2} a dual quaternion to represent as a string
     * @returns {String} string representation of the dual quat
     */
    function str(a) {
        return "quat2(" + a[0] + ", " + a[1] + ", " + a[2] + ", " + a[3] + ", " + a[4] + ", " + a[5] + ", " + a[6] + ", " + a[7] + ")";
    }
    exports.str = str;
    /**
     * Returns whether or not the dual quaternions have exactly the same elements in the same position (when compared with ===)
     *
     * @param {ReadonlyQuat2} a the first dual quaternion.
     * @param {ReadonlyQuat2} b the second dual quaternion.
     * @returns {Boolean} true if the dual quaternions are equal, false otherwise.
     */
    function exactEquals(a, b) {
        return a[0] === b[0] && a[1] === b[1] && a[2] === b[2] && a[3] === b[3] && a[4] === b[4] && a[5] === b[5] && a[6] === b[6] && a[7] === b[7];
    }
    exports.exactEquals = exactEquals;
    /**
     * Returns whether or not the dual quaternions have approximately the same elements in the same position.
     *
     * @param {ReadonlyQuat2} a the first dual quat.
     * @param {ReadonlyQuat2} b the second dual quat.
     * @returns {Boolean} true if the dual quats are equal, false otherwise.
     */
    function equals(a, b) {
        var a0 = a[0], a1 = a[1], a2 = a[2], a3 = a[3], a4 = a[4], a5 = a[5], a6 = a[6], a7 = a[7];
        var b0 = b[0], b1 = b[1], b2 = b[2], b3 = b[3], b4 = b[4], b5 = b[5], b6 = b[6], b7 = b[7];
        return Math.abs(a0 - b0) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a0), Math.abs(b0)) && Math.abs(a1 - b1) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a1), Math.abs(b1)) && Math.abs(a2 - b2) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a2), Math.abs(b2)) && Math.abs(a3 - b3) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a3), Math.abs(b3)) && Math.abs(a4 - b4) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a4), Math.abs(b4)) && Math.abs(a5 - b5) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a5), Math.abs(b5)) && Math.abs(a6 - b6) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a6), Math.abs(b6)) && Math.abs(a7 - b7) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a7), Math.abs(b7));
    }
    exports.equals = equals;
},
"58c71a9bd3": /* gl-matrix/esm/vec2.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const tslib_1 = require("tslib");
    const glMatrix = tslib_1.__importStar(require("7d825b979e") /* ./common.js */);
    /**
     * 2 Dimensional Vector
     * @module vec2
     */
    /**
     * Creates a new, empty vec2
     *
     * @returns {vec2} a new 2D vector
     */
    function create() {
        var out = new glMatrix.ARRAY_TYPE(2);
        if (glMatrix.ARRAY_TYPE != Float32Array) {
            out[0] = 0;
            out[1] = 0;
        }
        return out;
    }
    exports.create = create;
    /**
     * Creates a new vec2 initialized with values from an existing vector
     *
     * @param {ReadonlyVec2} a vector to clone
     * @returns {vec2} a new 2D vector
     */
    function clone(a) {
        var out = new glMatrix.ARRAY_TYPE(2);
        out[0] = a[0];
        out[1] = a[1];
        return out;
    }
    exports.clone = clone;
    /**
     * Creates a new vec2 initialized with the given values
     *
     * @param {Number} x X component
     * @param {Number} y Y component
     * @returns {vec2} a new 2D vector
     */
    function fromValues(x, y) {
        var out = new glMatrix.ARRAY_TYPE(2);
        out[0] = x;
        out[1] = y;
        return out;
    }
    exports.fromValues = fromValues;
    /**
     * Copy the values from one vec2 to another
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the source vector
     * @returns {vec2} out
     */
    function copy(out, a) {
        out[0] = a[0];
        out[1] = a[1];
        return out;
    }
    exports.copy = copy;
    /**
     * Set the components of a vec2 to the given values
     *
     * @param {vec2} out the receiving vector
     * @param {Number} x X component
     * @param {Number} y Y component
     * @returns {vec2} out
     */
    function set(out, x, y) {
        out[0] = x;
        out[1] = y;
        return out;
    }
    exports.set = set;
    /**
     * Adds two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @returns {vec2} out
     */
    function add(out, a, b) {
        out[0] = a[0] + b[0];
        out[1] = a[1] + b[1];
        return out;
    }
    exports.add = add;
    /**
     * Subtracts vector b from vector a
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @returns {vec2} out
     */
    function subtract(out, a, b) {
        out[0] = a[0] - b[0];
        out[1] = a[1] - b[1];
        return out;
    }
    exports.subtract = subtract;
    /**
     * Multiplies two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @returns {vec2} out
     */
    function multiply(out, a, b) {
        out[0] = a[0] * b[0];
        out[1] = a[1] * b[1];
        return out;
    }
    exports.multiply = multiply;
    /**
     * Divides two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @returns {vec2} out
     */
    function divide(out, a, b) {
        out[0] = a[0] / b[0];
        out[1] = a[1] / b[1];
        return out;
    }
    exports.divide = divide;
    /**
     * Math.ceil the components of a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a vector to ceil
     * @returns {vec2} out
     */
    function ceil(out, a) {
        out[0] = Math.ceil(a[0]);
        out[1] = Math.ceil(a[1]);
        return out;
    }
    exports.ceil = ceil;
    /**
     * Math.floor the components of a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a vector to floor
     * @returns {vec2} out
     */
    function floor(out, a) {
        out[0] = Math.floor(a[0]);
        out[1] = Math.floor(a[1]);
        return out;
    }
    exports.floor = floor;
    /**
     * Returns the minimum of two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @returns {vec2} out
     */
    function min(out, a, b) {
        out[0] = Math.min(a[0], b[0]);
        out[1] = Math.min(a[1], b[1]);
        return out;
    }
    exports.min = min;
    /**
     * Returns the maximum of two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @returns {vec2} out
     */
    function max(out, a, b) {
        out[0] = Math.max(a[0], b[0]);
        out[1] = Math.max(a[1], b[1]);
        return out;
    }
    exports.max = max;
    /**
     * Math.round the components of a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a vector to round
     * @returns {vec2} out
     */
    function round(out, a) {
        out[0] = Math.round(a[0]);
        out[1] = Math.round(a[1]);
        return out;
    }
    exports.round = round;
    /**
     * Scales a vec2 by a scalar number
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the vector to scale
     * @param {Number} b amount to scale the vector by
     * @returns {vec2} out
     */
    function scale(out, a, b) {
        out[0] = a[0] * b;
        out[1] = a[1] * b;
        return out;
    }
    exports.scale = scale;
    /**
     * Adds two vec2's after scaling the second operand by a scalar value
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @param {Number} scale the amount to scale b by before adding
     * @returns {vec2} out
     */
    function scaleAndAdd(out, a, b, scale) {
        out[0] = a[0] + b[0] * scale;
        out[1] = a[1] + b[1] * scale;
        return out;
    }
    exports.scaleAndAdd = scaleAndAdd;
    /**
     * Calculates the euclidian distance between two vec2's
     *
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @returns {Number} distance between a and b
     */
    function distance(a, b) {
        var x = b[0] - a[0], y = b[1] - a[1];
        return Math.hypot(x, y);
    }
    exports.distance = distance;
    /**
     * Calculates the squared euclidian distance between two vec2's
     *
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @returns {Number} squared distance between a and b
     */
    function squaredDistance(a, b) {
        var x = b[0] - a[0], y = b[1] - a[1];
        return x * x + y * y;
    }
    exports.squaredDistance = squaredDistance;
    /**
     * Calculates the length of a vec2
     *
     * @param {ReadonlyVec2} a vector to calculate length of
     * @returns {Number} length of a
     */
    function length(a) {
        var x = a[0], y = a[1];
        return Math.hypot(x, y);
    }
    exports.length = length;
    /**
     * Calculates the squared length of a vec2
     *
     * @param {ReadonlyVec2} a vector to calculate squared length of
     * @returns {Number} squared length of a
     */
    function squaredLength(a) {
        var x = a[0], y = a[1];
        return x * x + y * y;
    }
    exports.squaredLength = squaredLength;
    /**
     * Negates the components of a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a vector to negate
     * @returns {vec2} out
     */
    function negate(out, a) {
        out[0] = -a[0];
        out[1] = -a[1];
        return out;
    }
    exports.negate = negate;
    /**
     * Returns the inverse of the components of a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a vector to invert
     * @returns {vec2} out
     */
    function inverse(out, a) {
        out[0] = 1.0 / a[0];
        out[1] = 1.0 / a[1];
        return out;
    }
    exports.inverse = inverse;
    /**
     * Normalize a vec2
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a vector to normalize
     * @returns {vec2} out
     */
    function normalize(out, a) {
        var x = a[0], y = a[1];
        var len = x * x + y * y;
        if (len > 0) {
            //TODO: evaluate use of glm_invsqrt here?
            len = 1 / Math.sqrt(len);
        }
        out[0] = a[0] * len;
        out[1] = a[1] * len;
        return out;
    }
    exports.normalize = normalize;
    /**
     * Calculates the dot product of two vec2's
     *
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @returns {Number} dot product of a and b
     */
    function dot(a, b) {
        return a[0] * b[0] + a[1] * b[1];
    }
    exports.dot = dot;
    /**
     * Computes the cross product of two vec2's
     * Note that the cross product must by definition produce a 3D vector
     *
     * @param {vec3} out the receiving vector
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @returns {vec3} out
     */
    function cross(out, a, b) {
        var z = a[0] * b[1] - a[1] * b[0];
        out[0] = out[1] = 0;
        out[2] = z;
        return out;
    }
    exports.cross = cross;
    /**
     * Performs a linear interpolation between two vec2's
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the first operand
     * @param {ReadonlyVec2} b the second operand
     * @param {Number} t interpolation amount, in the range [0-1], between the two inputs
     * @returns {vec2} out
     */
    function lerp(out, a, b, t) {
        var ax = a[0], ay = a[1];
        out[0] = ax + t * (b[0] - ax);
        out[1] = ay + t * (b[1] - ay);
        return out;
    }
    exports.lerp = lerp;
    /**
     * Generates a random vector with the given scale
     *
     * @param {vec2} out the receiving vector
     * @param {Number} [scale] Length of the resulting vector. If ommitted, a unit vector will be returned
     * @returns {vec2} out
     */
    function random(out, scale) {
        scale = scale || 1.0;
        var r = glMatrix.RANDOM() * 2.0 * Math.PI;
        out[0] = Math.cos(r) * scale;
        out[1] = Math.sin(r) * scale;
        return out;
    }
    exports.random = random;
    /**
     * Transforms the vec2 with a mat2
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the vector to transform
     * @param {ReadonlyMat2} m matrix to transform with
     * @returns {vec2} out
     */
    function transformMat2(out, a, m) {
        var x = a[0], y = a[1];
        out[0] = m[0] * x + m[2] * y;
        out[1] = m[1] * x + m[3] * y;
        return out;
    }
    exports.transformMat2 = transformMat2;
    /**
     * Transforms the vec2 with a mat2d
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the vector to transform
     * @param {ReadonlyMat2d} m matrix to transform with
     * @returns {vec2} out
     */
    function transformMat2d(out, a, m) {
        var x = a[0], y = a[1];
        out[0] = m[0] * x + m[2] * y + m[4];
        out[1] = m[1] * x + m[3] * y + m[5];
        return out;
    }
    exports.transformMat2d = transformMat2d;
    /**
     * Transforms the vec2 with a mat3
     * 3rd vector component is implicitly '1'
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the vector to transform
     * @param {ReadonlyMat3} m matrix to transform with
     * @returns {vec2} out
     */
    function transformMat3(out, a, m) {
        var x = a[0], y = a[1];
        out[0] = m[0] * x + m[3] * y + m[6];
        out[1] = m[1] * x + m[4] * y + m[7];
        return out;
    }
    exports.transformMat3 = transformMat3;
    /**
     * Transforms the vec2 with a mat4
     * 3rd vector component is implicitly '0'
     * 4th vector component is implicitly '1'
     *
     * @param {vec2} out the receiving vector
     * @param {ReadonlyVec2} a the vector to transform
     * @param {ReadonlyMat4} m matrix to transform with
     * @returns {vec2} out
     */
    function transformMat4(out, a, m) {
        var x = a[0];
        var y = a[1];
        out[0] = m[0] * x + m[4] * y + m[12];
        out[1] = m[1] * x + m[5] * y + m[13];
        return out;
    }
    exports.transformMat4 = transformMat4;
    /**
     * Rotate a 2D vector
     * @param {vec2} out The receiving vec2
     * @param {ReadonlyVec2} a The vec2 point to rotate
     * @param {ReadonlyVec2} b The origin of the rotation
     * @param {Number} rad The angle of rotation in radians
     * @returns {vec2} out
     */
    function rotate(out, a, b, rad) {
        //Translate point to the origin
        var p0 = a[0] - b[0], p1 = a[1] - b[1], sinC = Math.sin(rad), cosC = Math.cos(rad); //perform rotation and translate to correct position
        out[0] = p0 * cosC - p1 * sinC + b[0];
        out[1] = p0 * sinC + p1 * cosC + b[1];
        return out;
    }
    exports.rotate = rotate;
    /**
     * Get the angle between two 2D vectors
     * @param {ReadonlyVec2} a The first operand
     * @param {ReadonlyVec2} b The second operand
     * @returns {Number} The angle in radians
     */
    function angle(a, b) {
        var x1 = a[0], y1 = a[1], x2 = b[0], y2 = b[1], 
        // mag is the product of the magnitudes of a and b
        mag = Math.sqrt(x1 * x1 + y1 * y1) * Math.sqrt(x2 * x2 + y2 * y2), 
        // mag &&.. short circuits if mag == 0
        cosine = mag && (x1 * x2 + y1 * y2) / mag; // Math.min(Math.max(cosine, -1), 1) clamps the cosine between -1 and 1
        return Math.acos(Math.min(Math.max(cosine, -1), 1));
    }
    exports.angle = angle;
    /**
     * Set the components of a vec2 to zero
     *
     * @param {vec2} out the receiving vector
     * @returns {vec2} out
     */
    function zero(out) {
        out[0] = 0.0;
        out[1] = 0.0;
        return out;
    }
    exports.zero = zero;
    /**
     * Returns a string representation of a vector
     *
     * @param {ReadonlyVec2} a vector to represent as a string
     * @returns {String} string representation of the vector
     */
    function str(a) {
        return "vec2(" + a[0] + ", " + a[1] + ")";
    }
    exports.str = str;
    /**
     * Returns whether or not the vectors exactly have the same elements in the same position (when compared with ===)
     *
     * @param {ReadonlyVec2} a The first vector.
     * @param {ReadonlyVec2} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    function exactEquals(a, b) {
        return a[0] === b[0] && a[1] === b[1];
    }
    exports.exactEquals = exactEquals;
    /**
     * Returns whether or not the vectors have approximately the same elements in the same position.
     *
     * @param {ReadonlyVec2} a The first vector.
     * @param {ReadonlyVec2} b The second vector.
     * @returns {Boolean} True if the vectors are equal, false otherwise.
     */
    function equals(a, b) {
        var a0 = a[0], a1 = a[1];
        var b0 = b[0], b1 = b[1];
        return Math.abs(a0 - b0) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a0), Math.abs(b0)) && Math.abs(a1 - b1) <= glMatrix.EPSILON * Math.max(1.0, Math.abs(a1), Math.abs(b1));
    }
    exports.equals = equals;
    /**
     * Alias for {@link vec2.length}
     * @function
     */
    exports.len = length;
    /**
     * Alias for {@link vec2.subtract}
     * @function
     */
    exports.sub = subtract;
    /**
     * Alias for {@link vec2.multiply}
     * @function
     */
    exports.mul = multiply;
    /**
     * Alias for {@link vec2.divide}
     * @function
     */
    exports.div = divide;
    /**
     * Alias for {@link vec2.distance}
     * @function
     */
    exports.dist = distance;
    /**
     * Alias for {@link vec2.squaredDistance}
     * @function
     */
    exports.sqrDist = squaredDistance;
    /**
     * Alias for {@link vec2.squaredLength}
     * @function
     */
    exports.sqrLen = squaredLength;
    /**
     * Perform some operation over an array of vec2s.
     *
     * @param {Array} a the array of vectors to iterate over
     * @param {Number} stride Number of elements between the start of each vec2. If 0 assumes tightly packed
     * @param {Number} offset Number of elements to skip at the beginning of the array
     * @param {Number} count Number of vec2s to iterate over. If 0 iterates over entire array
     * @param {Function} fn Function to call for each vector in the array
     * @param {Object} [arg] additional argument to pass to fn
     * @returns {Array} a
     * @function
     */
    exports.forEach = function () {
        var vec = create();
        return function (a, stride, offset, count, fn, arg) {
            var i, l;
            if (!stride) {
                stride = 2;
            }
            if (!offset) {
                offset = 0;
            }
            if (count) {
                l = Math.min(count * stride + offset, a.length);
            }
            else {
                l = a.length;
            }
            for (i = offset; i < l; i += stride) {
                vec[0] = a[i];
                vec[1] = a[i + 1];
                fn(vec, vec, arg);
                a[i] = vec[0];
                a[i + 1] = vec[1];
            }
            return a;
        };
    }();
},
"4797a2858f": /* models/vtk/vtkvolume.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const vtklayout_1 = require("b06d05fa3e") /* ./vtklayout */;
    const util_1 = require("df9946ff52") /* ./util */;
    class VTKVolumePlotView extends vtklayout_1.AbstractVTKView {
        connect_signals() {
            super.connect_signals();
            const { data, colormap, shadow, sampling, edge_gradient, rescale, ambient, diffuse, camera, specular, specular_power, display_volume, display_slices, slice_i, slice_j, slice_k, render_background, interpolation, controller_expanded, nan_opacity, } = this.model.properties;
            this.on_change(data, () => {
                this._vtk_image_data = (0, util_1.data2VTKImageData)(this.model.data);
                this.invalidate_render();
            });
            this.on_change(colormap, () => {
                this.colormap_selector.value = this.model.colormap;
                const event = new Event("change");
                this.colormap_selector.dispatchEvent(event);
            });
            this.on_change(shadow, () => {
                this.shadow_selector.value = this.model.shadow ? "1" : "0";
                const event = new Event("change");
                this.shadow_selector.dispatchEvent(event);
            });
            this.on_change(sampling, () => {
                this.sampling_slider.value = this.model.sampling.toFixed(2);
                const event = new Event("input");
                this.sampling_slider.dispatchEvent(event);
            });
            this.on_change(edge_gradient, () => {
                this.edge_gradient_slider.value = this.model.edge_gradient.toFixed(2);
                const event = new Event("input");
                this.edge_gradient_slider.dispatchEvent(event);
            });
            this.on_change(rescale, () => {
                this._controllerWidget.setRescaleColorMap(this.model.rescale);
                this._vtk_renwin.getRenderWindow().render();
            });
            this.on_change(ambient, () => {
                this.volume.getProperty().setAmbient(this.model.ambient);
                this._vtk_renwin.getRenderWindow().render();
            });
            this.on_change(diffuse, () => {
                this.volume.getProperty().setDiffuse(this.model.diffuse);
                this._vtk_renwin.getRenderWindow().render();
            });
            this.on_change(camera, () => {
                if (!this._setting_camera) {
                    this._set_camera_state();
                    this._vtk_renwin.getRenderWindow().render();
                }
            });
            this.on_change(specular, () => {
                this.volume.getProperty().setSpecular(this.model.specular);
                this._vtk_renwin.getRenderWindow().render();
            });
            this.on_change(specular_power, () => {
                this.volume.getProperty().setSpecularPower(this.model.specular_power);
                this._vtk_renwin.getRenderWindow().render();
            });
            this.on_change(display_volume, () => {
                this._set_volume_visibility(this.model.display_volume);
                this._vtk_renwin.getRenderWindow().render();
            });
            this.on_change(display_slices, () => {
                this._set_slices_visibility(this.model.display_slices);
                this._vtk_renwin.getRenderWindow().render();
            });
            this.on_change(slice_i, () => {
                if (this.image_actor_i !== undefined) {
                    this.image_actor_i.getMapper().setISlice(this.model.slice_i);
                    this._vtk_renwin.getRenderWindow().render();
                }
            });
            this.on_change(slice_j, () => {
                if (this.image_actor_j !== undefined) {
                    this.image_actor_j.getMapper().setJSlice(this.model.slice_j);
                    this._vtk_renwin.getRenderWindow().render();
                }
            });
            this.on_change(slice_k, () => {
                if (this.image_actor_k !== undefined) {
                    this.image_actor_k.getMapper().setKSlice(this.model.slice_k);
                    this._vtk_renwin.getRenderWindow().render();
                }
            });
            this.on_change(render_background, () => {
                this._vtk_renwin
                    .getRenderer()
                    .setBackground(...(0, util_1.hexToRGB)(this.model.render_background));
                this._vtk_renwin.getRenderWindow().render();
            });
            this.on_change(interpolation, () => {
                this._set_interpolation(this.model.interpolation);
                this._vtk_renwin.getRenderWindow().render();
            });
            this.on_change(controller_expanded, () => {
                if (this._controllerWidget != null) {
                    this._controllerWidget.setExpanded(this.model.controller_expanded);
                }
            });
            this.on_change(nan_opacity, () => {
                const scalar_opacity = this.image_actor_i.getProperty().getScalarOpacity();
                scalar_opacity.get(["nodes"]).nodes[0].y = this.model.nan_opacity;
                scalar_opacity.modified();
                this._vtk_renwin.getRenderWindow().render();
            });
        }
        render() {
            this._vtk_renwin = null;
            this._orientationWidget = null;
            this._axes = null;
            super.render();
            this._create_orientation_widget();
            this._set_axes();
            this._vtk_renwin.getRenderer().resetCamera();
            if (Object.keys(this.model.camera).length) {
                this._set_camera_state();
            }
            this._get_camera_state();
        }
        invalidate_render() {
            this._vtk_renwin = null;
            super.invalidate_render();
        }
        init_vtk_renwin() {
            this._vtk_renwin = util_1.vtkns.FullScreenRenderWindow.newInstance({
                rootContainer: this.shadow_el,
                container: this._vtk_container,
            });
        }
        plot() {
            this._controllerWidget = util_1.vtkns.VolumeController.newInstance({
                size: [400, 150],
                rescaleColorMap: this.model.rescale,
            });
            this._plot_volume();
            this._plot_slices();
            this._controllerWidget.setupContent(this._vtk_renwin.getRenderWindow(), this.volume, true);
            this._controllerWidget.setContainer(this.el);
            this._controllerWidget.setExpanded(this.model.controller_expanded);
            this._connect_js_controls();
            this._vtk_renwin.getRenderWindow().getInteractor();
            this._vtk_renwin.getRenderWindow().getInteractor().setDesiredUpdateRate(45);
            this._set_volume_visibility(this.model.display_volume);
            this._set_slices_visibility(this.model.display_slices);
            this._vtk_renwin
                .getRenderer()
                .setBackground(...(0, util_1.hexToRGB)(this.model.render_background));
            this._set_interpolation(this.model.interpolation);
            this._set_camera_state();
        }
        get vtk_image_data() {
            if (!this._vtk_image_data) {
                this._vtk_image_data = (0, util_1.data2VTKImageData)(this.model.data);
            }
            return this._vtk_image_data;
        }
        get volume() {
            return this._vtk_renwin.getRenderer().getVolumes()[0];
        }
        get image_actor_i() {
            return this._vtk_renwin.getRenderer().getActors()[0];
        }
        get image_actor_j() {
            return this._vtk_renwin.getRenderer().getActors()[1];
        }
        get image_actor_k() {
            return this._vtk_renwin.getRenderer().getActors()[2];
        }
        get shadow_selector() {
            return this.el.querySelector(".js-shadow");
        }
        get edge_gradient_slider() {
            return this.el.querySelector(".js-edge");
        }
        get sampling_slider() {
            return this.el.querySelector(".js-spacing");
        }
        get colormap_selector() {
            return this.el.querySelector(".js-color-preset");
        }
        _connect_js_controls() {
            const { el: controller_el } = this._controllerWidget.get("el");
            if (controller_el !== undefined) {
                const controller_button = controller_el.querySelector(".js-button");
                controller_button.addEventListener("click", () => this.model.controller_expanded = this._controllerWidget.getExpanded());
            }
            // Colormap selector
            this.colormap_selector.addEventListener("change", () => {
                this.model.colormap = this.colormap_selector.value;
            });
            if (!this.model.colormap) {
                this.model.colormap = this.colormap_selector.value;
            }
            else {
                this.model.properties.colormap.change.emit();
            }
            // Shadow selector
            this.shadow_selector.addEventListener("change", () => {
                this.model.shadow = !!Number(this.shadow_selector.value);
            });
            if ((this.model.shadow = !!Number(this.shadow_selector.value))) {
                this.model.properties.shadow.change.emit();
            }
            // Sampling slider
            this.sampling_slider.addEventListener("input", () => {
                const js_sampling_value = Number(this.sampling_slider.value);
                if (Math.abs(this.model.sampling - js_sampling_value) >= 5e-3) {
                    this.model.sampling = js_sampling_value;
                }
            });
            if (Math.abs(this.model.sampling - Number(this.shadow_selector.value)) >= 5e-3) {
                this.model.properties.sampling.change.emit();
            }
            // Edge Gradient slider
            this.edge_gradient_slider.addEventListener("input", () => {
                const js_edge_gradient_value = Number(this.edge_gradient_slider.value);
                if (Math.abs(this.model.edge_gradient - js_edge_gradient_value) >= 5e-3) {
                    this.model.edge_gradient = js_edge_gradient_value;
                }
            });
            if (Math.abs(this.model.edge_gradient - Number(this.edge_gradient_slider.value)) >= 5e-3) {
                this.model.properties.edge_gradient.change.emit();
            }
        }
        _plot_slices() {
            const source = this._vtk_image_data;
            const image_actor_i = util_1.vtkns.ImageSlice.newInstance();
            const image_actor_j = util_1.vtkns.ImageSlice.newInstance();
            const image_actor_k = util_1.vtkns.ImageSlice.newInstance();
            const image_mapper_i = util_1.vtkns.ImageMapper.newInstance();
            const image_mapper_j = util_1.vtkns.ImageMapper.newInstance();
            const image_mapper_k = util_1.vtkns.ImageMapper.newInstance();
            image_mapper_i.setInputData(source);
            image_mapper_i.setISlice(this.model.slice_i);
            image_actor_i.setMapper(image_mapper_i);
            image_mapper_j.setInputData(source);
            image_mapper_j.setJSlice(this.model.slice_j);
            image_actor_j.setMapper(image_mapper_j);
            image_mapper_k.setInputData(source);
            image_mapper_k.setKSlice(this.model.slice_k);
            image_actor_k.setMapper(image_mapper_k);
            // set_color and opacity
            const piecewiseFunction = util_1.vtkns.PiecewiseFunction.newInstance();
            const lookupTable = this.volume.getProperty().getRGBTransferFunction(0);
            const range = this.volume.getMapper().getInputData().getPointData().getScalars().getRange();
            piecewiseFunction.removeAllPoints();
            piecewiseFunction.addPoint(range[0] - 1, this.model.nan_opacity);
            piecewiseFunction.addPoint(range[0], 1);
            piecewiseFunction.addPoint(range[1], 1);
            const property = image_actor_i.getProperty();
            image_actor_j.setProperty(property);
            image_actor_k.setProperty(property);
            property.setRGBTransferFunction(lookupTable);
            property.setScalarOpacity(piecewiseFunction);
            const renderer = this._vtk_renwin.getRenderer();
            renderer.addActor(image_actor_i);
            renderer.addActor(image_actor_j);
            renderer.addActor(image_actor_k);
        }
        _plot_volume() {
            //Create vtk volume and add it to the scene
            const source = this.vtk_image_data;
            const actor = util_1.vtkns.Volume.newInstance();
            const mapper = util_1.vtkns.VolumeMapper.newInstance();
            actor.setMapper(mapper);
            mapper.setInputData(source);
            const dataArray = source.getPointData().getScalars() || source.getPointData().getArrays()[0];
            const dataRange = dataArray.getRange();
            const lookupTable = util_1.vtkns.ColorTransferFunction.newInstance();
            if (this.model.colormap != null) {
                const preset = util_1.vtkns.ColorTransferFunction.vtkColorMaps.getPresetByName(this.model.colormap);
                lookupTable.applyColorMap(preset);
            }
            lookupTable.onModified(() => (this.model.mapper = (0, util_1.vtkLutToMapper)(lookupTable)));
            const piecewiseFunction = util_1.vtkns.PiecewiseFunction.newInstance();
            const sampleDistance = 0.7 *
                Math.sqrt(source
                    .getSpacing()
                    .map((v) => v * v)
                    .reduce((a, b) => a + b, 0));
            mapper.setSampleDistance(sampleDistance);
            actor.getProperty().setRGBTransferFunction(0, lookupTable);
            actor.getProperty().setScalarOpacity(0, piecewiseFunction);
            actor.getProperty().setInterpolationTypeToFastLinear();
            // actor.getProperty().setInterpolationTypeToLinear();
            // For better looking volume rendering
            // - distance in world coordinates a scalar opacity of 1.0
            actor
                .getProperty()
                .setScalarOpacityUnitDistance(0, util_1.vtkns.BoundingBox.getDiagonalLength(source.getBounds()) /
                Math.max(...source.getDimensions()));
            // - control how we emphasize surface boundaries
            //  => max should be around the average gradient magnitude for the
            //     volume or maybe average plus one std dev of the gradient magnitude
            //     (adjusted for spacing, this is a world coordinate gradient, not a
            //     pixel gradient)
            //  => max hack: (dataRange[1] - dataRange[0]) * 0.05
            actor.getProperty().setGradientOpacityMinimumValue(0, 0);
            actor
                .getProperty()
                .setGradientOpacityMaximumValue(0, (dataRange[1] - dataRange[0]) * 0.05);
            // - Use shading based on gradient
            actor.getProperty().setShade(this.model.shadow);
            actor.getProperty().setUseGradientOpacity(0, true);
            // - generic good default
            actor.getProperty().setGradientOpacityMinimumOpacity(0, 0.0);
            actor.getProperty().setGradientOpacityMaximumOpacity(0, 1.0);
            actor.getProperty().setAmbient(this.model.ambient);
            actor.getProperty().setDiffuse(this.model.diffuse);
            actor.getProperty().setSpecular(this.model.specular);
            actor.getProperty().setSpecularPower(this.model.specular_power);
            this._vtk_renwin.getRenderer().addVolume(actor);
        }
        _set_interpolation(interpolation) {
            if (interpolation == "fast_linear") {
                this.volume.getProperty().setInterpolationTypeToFastLinear();
                this.image_actor_i.getProperty().setInterpolationTypeToLinear();
            }
            else if (interpolation == "linear") {
                this.volume.getProperty().setInterpolationTypeToLinear();
                this.image_actor_i.getProperty().setInterpolationTypeToLinear();
            }
            else {
                //nearest
                this.volume.getProperty().setInterpolationTypeToNearest();
                this.image_actor_i.getProperty().setInterpolationTypeToNearest();
            }
        }
        _set_slices_visibility(visibility) {
            this.image_actor_i.setVisibility(visibility);
            this.image_actor_j.setVisibility(visibility);
            this.image_actor_k.setVisibility(visibility);
        }
        _set_volume_visibility(visibility) {
            this.volume.setVisibility(visibility);
        }
    }
    exports.VTKVolumePlotView = VTKVolumePlotView;
    VTKVolumePlotView.__name__ = "VTKVolumePlotView";
    class VTKVolumePlot extends vtklayout_1.AbstractVTKPlot {
        constructor(attrs) {
            super(attrs);
        }
    }
    exports.VTKVolumePlot = VTKVolumePlot;
    _a = VTKVolumePlot;
    VTKVolumePlot.__name__ = "VTKVolumePlot";
    (() => {
        _a.prototype.default_view = VTKVolumePlotView;
        _a.define(({ Any, Array, Boolean, Int, Number, String, Struct }) => ({
            ambient: [Number, 0.2],
            colormap: [String],
            data: [Any],
            diffuse: [Number, 0.7],
            display_slices: [Boolean, false],
            display_volume: [Boolean, true],
            edge_gradient: [Number, 0.2],
            interpolation: [util_1.Interpolation, "fast_linear"],
            mapper: [Struct({ palette: Array(String), low: Number, high: Number }), { palette: [], low: 0, high: 0 }],
            nan_opacity: [Number, 1],
            render_background: [String, "#52576e"],
            rescale: [Boolean, false],
            sampling: [Number, 0.4],
            shadow: [Boolean, true],
            slice_i: [Int, 0],
            slice_j: [Int, 0],
            slice_k: [Int, 0],
            specular: [Number, 0.3],
            specular_power: [Number, 8.0],
            controller_expanded: [Boolean, true],
        }));
        _a.override({
            height: 300,
            width: 300,
        });
    })();
},
"a4e5946204": /* models/vtk/vtksynchronized.js */ function _(require, module, exports, __esModule, __esExport) {
    var _a;
    __esModule();
    const object_1 = require("@bokehjs/core/util/object");
    const debounce_1 = require("99a25e6992") /* debounce */;
    const vtklayout_1 = require("b06d05fa3e") /* ./vtklayout */;
    const panel_fullscreen_renwin_sync_1 = require("5e89c7b3eb") /* ./panel_fullscreen_renwin_sync */;
    const util_1 = require("df9946ff52") /* ./util */;
    const CONTEXT_NAME = "panel";
    class VTKSynchronizedPlotView extends vtklayout_1.AbstractVTKView {
        initialize() {
            super.initialize();
            this._renderable = false;
            // Context initialization
            this._synchronizer_context = util_1.vtkns.SynchronizableRenderWindow.getSynchronizerContext(`${CONTEXT_NAME}-{this.model.id}`);
        }
        connect_signals() {
            super.connect_signals();
            const { arrays, scene, one_time_reset } = this.model.properties;
            this.on_change([arrays, scene], (0, debounce_1.debounce)(() => {
                this._vtk_renwin.delete();
                this._vtk_renwin = null;
                this.invalidate_render();
            }, 20));
            this.on_change(one_time_reset, () => {
                this._vtk_renwin.getRenderWindow().clearOneTimeUpdaters();
            });
        }
        init_vtk_renwin() {
            this._vtk_renwin = util_1.vtkns.FullScreenRenderWindowSynchronized.newInstance({
                rootContainer: this.el,
                container: this._vtk_container,
                synchronizerContext: this._synchronizer_context,
            });
        }
        remove() {
            if (this._vtk_renwin) {
                this._vtk_renwin.delete();
            }
            super.remove();
        }
        plot() {
            this._vtk_renwin.getRenderWindow().clearOneTimeUpdaters();
            const state = (0, object_1.clone)(this.model.scene);
            this._sync_plot(state, () => this._on_scene_ready()).then(() => {
                this._set_camera_state();
                this._get_camera_state();
            });
        }
        _on_scene_ready() {
            this._renderable = true;
            this._camera_callbacks.push(this._vtk_renwin
                .getRenderer()
                .getActiveCamera()
                .onModified(() => this._vtk_render()));
            if (!this._orientationWidget) {
                this._create_orientation_widget();
            }
            if (!this._axes) {
                this._set_axes();
            }
            this._vtk_renwin.resize();
            this._vtk_render();
        }
        _sync_plot(state, onSceneReady) {
            // Need to ensure all promises are resolved before calling this function
            this._renderable = false;
            this._unsubscribe_camera_cb();
            this._synchronizer_context.setFetchArrayFunction((hash) => {
                return Promise.resolve(this.model.arrays[hash]);
            });
            const renderer = this._synchronizer_context.getInstance(this.model.scene.dependencies[0].id);
            if (renderer && !this._vtk_renwin.getRenderer()) {
                this._vtk_renwin.getRenderWindow().addRenderer(renderer);
            }
            return this._vtk_renwin
                .getRenderWindow()
                .synchronize(state).then(onSceneReady);
        }
    }
    exports.VTKSynchronizedPlotView = VTKSynchronizedPlotView;
    VTKSynchronizedPlotView.__name__ = "VTKSynchronizedPlotView";
    class VTKSynchronizedPlot extends vtklayout_1.AbstractVTKPlot {
        constructor(attrs) {
            super(attrs);
            (0, panel_fullscreen_renwin_sync_1.initialize_fullscreen_render)();
            this.outline = util_1.vtkns.OutlineFilter.newInstance(); //use to display bounding box of a selected actor
            const mapper = util_1.vtkns.Mapper.newInstance();
            mapper.setInputConnection(this.outline.getOutputPort());
            this.outline_actor = util_1.vtkns.Actor.newInstance();
            this.outline_actor.setMapper(mapper);
        }
        getActors(ptr_ref) {
            let actors = this.renderer_el.getRenderer().getActors();
            if (ptr_ref) {
                const context = this.renderer_el.getSynchronizerContext(CONTEXT_NAME);
                actors = actors.filter((actor) => {
                    const id_actor = context.getInstanceId(actor);
                    return id_actor ? id_actor.slice(-16) == ptr_ref.slice(1, 17) : false;
                });
            }
            return actors;
        }
    }
    exports.VTKSynchronizedPlot = VTKSynchronizedPlot;
    _a = VTKSynchronizedPlot;
    VTKSynchronizedPlot.__name__ = "VTKSynchronizedPlot";
    VTKSynchronizedPlot.__module__ = "panel.models.vtk";
    (() => {
        _a.prototype.default_view = VTKSynchronizedPlotView;
        _a.define(({ Any, Array, Boolean, Bytes, Dict, String }) => ({
            arrays: [Dict(Bytes), {}],
            arrays_processed: [Array(String), []],
            enable_keybindings: [Boolean, false],
            one_time_reset: [Boolean, false],
            rebuild: [Boolean, false],
            scene: [Any, {}],
        }));
        _a.override({
            height: 300,
            width: 300,
        });
    })();
},
"5e89c7b3eb": /* models/vtk/panel_fullscreen_renwin_sync.js */ function _(require, module, exports, __esModule, __esExport) {
    __esModule();
    const util_1 = require("df9946ff52") /* ./util */;
    //------------------------//
    //Custom Extended Classes
    //------------------------//
    const DEFAULT_VALUES = {
        containerStyle: null,
        controlPanelStyle: null,
        listenWindowResize: true,
        resizeCallback: null,
        controllerVisibility: true,
        synchronizerContextName: "default",
    };
    const STYLE_CONTROL_PANEL = {
        position: "absolute",
        left: "25px",
        top: "25px",
        backgroundColor: "white",
        borderRadius: "5px",
        listStyle: "none",
        padding: "5px 10px",
        margin: "0",
        display: "block",
        border: "solid 1px black",
        maxWidth: "calc(100vw - 70px)",
        maxHeight: "calc(100vh - 60px)",
        overflow: "auto",
    };
    function panelFullScreenRenderWindowSynchronized(publicAPI, model) {
        // Panel (modification) synchronizable renderWindow
        model.renderWindow = util_1.vtkns.SynchronizableRenderWindow.newInstance({
            synchronizerContext: model.synchronizerContext,
        });
        // OpenGlRenderWindow
        model.openGLRenderWindow = util_1.vtkns.OpenGLRenderWindow.newInstance();
        model.openGLRenderWindow.setContainer(model.container);
        model.renderWindow.addView(model.openGLRenderWindow);
        // Interactor
        model.interactor = util_1.vtkns.RenderWindowInteractor.newInstance();
        model.interactor.setInteractorStyle(util_1.vtkns.InteractorStyleTrackballCamera.newInstance());
        model.interactor.setView(model.openGLRenderWindow);
        model.interactor.initialize();
        model.interactor.bindEvents(model.container);
        publicAPI.getRenderer = () => model.renderWindow.getRenderers()[0];
        publicAPI.removeController = () => {
            const el = model.controlContainer;
            if (el) {
                el.parentNode.removeChild(el);
            }
        };
        publicAPI.setControllerVisibility = (visible) => {
            model.controllerVisibility = visible;
            if (model.controlContainer) {
                if (visible) {
                    model.controlContainer.style.display = "block";
                }
                else {
                    model.controlContainer.style.display = "none";
                }
            }
        };
        publicAPI.toggleControllerVisibility = () => {
            publicAPI.setControllerVisibility(!model.controllerVisibility);
        };
        publicAPI.addController = (html) => {
            model.controlContainer = document.createElement("div");
            (0, util_1.applyStyle)(model.controlContainer, model.controlPanelStyle || STYLE_CONTROL_PANEL);
            model.rootContainer.appendChild(model.controlContainer);
            model.controlContainer.innerHTML = html;
            publicAPI.setControllerVisibility(model.controllerVisibility);
            model.rootContainer.addEventListener("keypress", (e) => {
                if (String.fromCharCode(e.charCode) === "c") {
                    publicAPI.toggleControllerVisibility();
                }
            });
        };
        // Properly release GL context
        publicAPI.delete = window.vtk.macro.chain(publicAPI.setContainer, model.openGLRenderWindow.delete, publicAPI.delete);
        // Handle window resize
        publicAPI.resize = () => {
            const dims = model.container.getBoundingClientRect();
            const devicePixelRatio = window.devicePixelRatio || 1;
            model.openGLRenderWindow.setSize(Math.floor(dims.width * devicePixelRatio), Math.floor(dims.height * devicePixelRatio));
            if (model.resizeCallback) {
                model.resizeCallback(dims);
            }
            model.renderWindow.render();
        };
        publicAPI.setResizeCallback = (cb) => {
            model.resizeCallback = cb;
            publicAPI.resize();
        };
        if (model.listenWindowResize) {
            window.addEventListener("resize", publicAPI.resize);
        }
        publicAPI.resize();
    }
    function initialize_fullscreen_render() {
        const FullScreenRenderWindowSynchronized = {
            newInstance: window.vtk.macro.newInstance((publicAPI, model, initialValues = {}) => {
                Object.assign(model, DEFAULT_VALUES, initialValues);
                // Object methods
                window.vtk.macro.obj(publicAPI, model);
                window.vtk.macro.get(publicAPI, model, [
                    "renderWindow",
                    "openGLRenderWindow",
                    "interactor",
                    "rootContainer",
                    "container",
                    "controlContainer",
                    "synchronizerContext",
                ]);
                // Object specific methods
                panelFullScreenRenderWindowSynchronized(publicAPI, model);
            }),
        };
        util_1.vtkns.FullScreenRenderWindowSynchronized = FullScreenRenderWindowSynchronized;
    }
    exports.initialize_fullscreen_render = initialize_fullscreen_render;
},
}, "4e90918c0a", {"index":"4e90918c0a","models/index":"38670592ce","models/ace":"c780fc99fd","models/layout":"73d6aee8f5","models/audio":"fd59c985b3","models/browser":"85211a0a5b","models/button":"bda381b012","models/button_icon":"1738ddeb3a","models/icon":"a97a38b997","models/card":"4bed810d7e","models/column":"879751b529","styles/models/card.css":"2d2b7d250a","models/checkbox_button_group":"363b62b1db","models/chatarea_input":"30fb939eca","models/textarea_input":"b7d595d74a","models/comm_manager":"352943c042","models/customselect":"92bbd30bd1","models/tabulator":"f89f0e6802","models/data":"be689f0377","models/datetime_picker":"ddf98634bb","models/deckgl":"dc03aab885","models/tooltips":"f8f8ea4284","models/echarts":"04cbffdfe0","models/event-to-object":"2cc1a33000","models/feed":"976c02c0a8","models/file_download":"3ead851ca6","models/html":"89d2d3667a","models/ipywidget":"8a8089cbf3","models/json":"7eff964d3e","models/jsoneditor":"d57683bd1f","models/katex":"f672d71a9f","models/location":"bd8e0fe48b","models/mathjax":"ec353a3d9a","models/pdf":"cf33f23f5c","models/perspective":"54dac9b7a1","models/player":"f06104d237","models/plotly":"c08950da15","models/util":"27e2a99e99","styles/models/plotly.css":"ce7c8e2a4f","models/progress":"aded75e266","models/quill":"c72e00086f","models/radio_button_group":"361b5f089c","models/reactive_html":"6cfc3f348e","models/singleselect":"168c4d0ebd","models/speech_to_text":"739cca6576","models/state":"92822cb73a","models/tabs":"2231cdc549","models/terminal":"121f00bd6f","models/text_to_speech":"a04eb51988","models/toggle_icon":"ad985f285e","models/tooltip_icon":"ae3a172647","models/trend":"3584638c04","models/vega":"119dc23765","models/video":"79dc37b888","styles/models/video.css":"dfe21e6f1b","models/videostream":"f8afc4e661","models/vizzu":"470ce1dcbc","models/vtk/index":"c51f25e2a7","models/vtk/vtkjs":"ac55912dc1","models/vtk/vtklayout":"b06d05fa3e","models/vtk/util":"df9946ff52","models/vtk/vtkcolorbar":"b1d68776a9","models/vtk/vtkaxes":"0379dcf1cd","models/vtk/vtkvolume":"4797a2858f","models/vtk/vtksynchronized":"a4e5946204","models/vtk/panel_fullscreen_renwin_sync":"5e89c7b3eb"}, {});});
//# sourceMappingURL=panel.js.map
