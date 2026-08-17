import { div } from "@bokehjs/core/dom";
import { HTMLBox, HTMLBoxView } from "./layout";
export class QuillInputView extends HTMLBoxView {
    static __name__ = "QuillInputView";
    container;
    _editor;
    _editing;
    _toolbar;
    quill;
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
        this.container = div({ style: { visibility: "hidden" } });
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
            const range = getNativeRange(rootNode);
            return !!range ? this.quill.selection.normalizeNative(range) : null;
        };
        /**
         * Original implementation relies on Selection.addRange to programmatically set the range, which does not work
         * in Webkit with Native Shadow. Selection.addRange works fine in Chromium and Gecko.
         **/
        this.quill.selection.setNativeRange = (startNode, startOffset, endNode = undefined, endOffset = undefined, force = false) => {
            endNode = endNode === undefined ? startNode : endNode;
            endOffset = endOffset === undefined ? startOffset : endOffset;
            force = force || false;
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
        const delta = this.quill.clipboard.convert({ html: this.model.text });
        this.quill.setContents(delta);
        this.quill.on("text-change", () => {
            if (this._editing) {
                return;
            }
            this._editing = true;
            const html = this.quill.getSemanticHTML();
            this.model.text_input = html;
            if (this.model.on_keyup) {
                this.model.text = html;
            }
            this._editing = false;
        });
        // selection-change drives two behaviors:
        //   1. When range is null the editor has blurred; if on_keyup is false,
        //      commit the current content into text (deferred commit). Also
        //      clear the selection state.
        //   2. When range is non-null update the selection param with the
        //      visible text (or clear it if the selection collapsed).
        // The _editing guard avoids acting on selection-change events fired by
        // programmatic content replacement (pasteHTML / setContents).
        this.quill.on("selection-change", (range, _oldRange, _source) => {
            if (this._editing) {
                return;
            }
            if (range === null) {
                if (!this.model.on_keyup) {
                    this._editing = true;
                    this.model.text = this.quill.getSemanticHTML();
                    this._editing = false;
                }
                if (Object.keys(this.model.selection).length > 0) {
                    this.model.selection = {};
                }
                return;
            }
            if (range.length > 0) {
                const text = this.quill.getText(range.index, range.length);
                this.model.selection = { text };
            }
            else if (Object.keys(this.model.selection).length > 0) {
                this.model.selection = {};
            }
        });
        // Ctrl/Cmd+Enter commits text_input -> text when on_keyup is false.
        // preventDefault unconditionally so the shortcut doesn't insert a newline.
        this.quill.root.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                if (!this.model.on_keyup) {
                    this._editing = true;
                    this.model.text = this.quill.getSemanticHTML();
                    this._editing = false;
                }
            }
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
        const delta = this.quill.clipboard.convert({ html: this.model.text });
        this.quill.setContents(delta);
        this.invalidate_layout();
    }
    after_layout() {
        super.after_layout();
        this._layout_toolbar();
    }
}
export class QuillInput extends HTMLBox {
    static __name__ = "QuillInput";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.quill";
    static {
        this.prototype.default_view = QuillInputView;
        this.define(({ Any, Bool, Dict, Str }) => ({
            mode: [Str, "toolbar"],
            on_keyup: [Bool, true],
            placeholder: [Str, ""],
            selection: [Dict(Any), {}],
            text: [Str, ""],
            text_input: [Str, ""],
            toolbar: [Any, null],
        }));
        this.override({
            height: 300,
        });
    }
}
//# sourceMappingURL=quill.js.map