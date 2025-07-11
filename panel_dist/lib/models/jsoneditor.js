import { ImportedStyleSheet } from "@bokehjs/core/dom";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import { HTMLBox, HTMLBoxView } from "./layout";
export class JSONEditEvent extends ModelEvent {
    data;
    static __name__ = "JSONEditEvent";
    constructor(data) {
        super();
        this.data = data;
    }
    get event_values() {
        return { model: this.origin, data: this.data };
    }
    static {
        this.prototype.event_name = "json_edit";
    }
}
export class JSONEditorView extends HTMLBoxView {
    static __name__ = "JSONEditorView";
    editor;
    _menu_context;
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
            styles.push(new ImportedStyleSheet(css));
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
            onChangeText: (text) => {
                try {
                    this.model.data = JSON.parse(text);
                }
                catch (e) {
                    console.warn(e);
                }
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
export class JSONEditor extends HTMLBox {
    static __name__ = "JSONEditor";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.jsoneditor";
    static {
        this.prototype.default_view = JSONEditorView;
        this.define(({ Any, List, Bool, Str }) => ({
            css: [List(Str), []],
            data: [Any, {}],
            mode: [Str, "tree"],
            menu: [Bool, true],
            search: [Bool, true],
            selection: [List(Any), []],
            schema: [Any, null],
            templates: [List(Any), []],
        }));
    }
}
//# sourceMappingURL=jsoneditor.js.map