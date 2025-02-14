import { div } from "@bokehjs/core/dom";
import { HTMLBox, HTMLBoxView } from "./layout";
import { ID } from "./util";
export class AcePlotView extends HTMLBoxView {
    static __name__ = "AcePlotView";
    _editor;
    _langTools;
    _modelist;
    _container;
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
        this._container = div({
            id: ID(),
            style: {
                width: "100%",
                height: "100%",
                zIndex: "0",
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
        // if on keyup, update code from editor
        if (this.model.on_keyup) {
            this._editor.on("change", () => this._update_code_from_editor());
        }
        else {
            this._editor.on("blur", () => this._update_code_from_editor());
            this._editor.commands.addCommand({
                name: "updateCodeFromEditor",
                bindKey: { win: "Ctrl-Enter", mac: "Command-Enter" },
                exec: () => {
                    this._update_code_from_editor();
                },
            });
        }
        this._editor.on("change", () => this._update_code_input_from_editor());
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
    _update_code_input_from_editor() {
        if (this._editor.getValue() != this.model.code_input) {
            this.model.code_input = this._editor.getValue();
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
export class AcePlot extends HTMLBox {
    static __name__ = "AcePlot";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.ace";
    static {
        this.prototype.default_view = AcePlotView;
        this.define(({ Any, List, Bool, Str, Nullable }) => ({
            code: [Str, ""],
            code_input: [Str, ""],
            on_keyup: [Bool, true],
            filename: [Nullable(Str), null],
            language: [Str, ""],
            theme: [Str, "chrome"],
            annotations: [List(Any), []],
            readonly: [Bool, false],
            print_margin: [Bool, false],
        }));
        this.override({
            height: 300,
            width: 300,
        });
    }
}
//# sourceMappingURL=ace.js.map