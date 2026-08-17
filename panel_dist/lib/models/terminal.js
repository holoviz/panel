import { div } from "@bokehjs/core/dom";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import { HTMLBox, HTMLBoxView, set_size } from "./layout";
export class KeystrokeEvent extends ModelEvent {
    key;
    static __name__ = "KeystrokeEvent";
    constructor(key) {
        super();
        this.key = key;
    }
    get event_values() {
        return { model: this.origin, key: this.key };
    }
    static {
        this.prototype.event_name = "keystroke";
    }
}
export class TerminalView extends HTMLBoxView {
    static __name__ = "TerminalView";
    term; // Element
    webLinksAddon;
    container;
    _rendered;
    connect_signals() {
        super.connect_signals();
        const { width, height, min_height, max_height, margin, sizing_mode, output, _clears } = this.model.properties;
        this.on_change(output, this.write);
        this.on_change(_clears, this.clear);
        this.on_change([width, height, min_height, max_height, margin, sizing_mode], () => {
            set_size(this.el, this.model);
            set_size(this.container, this.model, false);
        });
    }
    render() {
        super.render();
        this.container = div({ class: "terminal-container" });
        set_size(this.container, this.model, false);
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
// The Bokeh .ts model corresponding to the Bokeh .py model
export class Terminal extends HTMLBox {
    static __name__ = "Terminal";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.terminal";
    static {
        this.prototype.default_view = TerminalView;
        this.define(({ Any, Int, Str }) => ({
            _clears: [Int, 0],
            options: [Any, {}],
            output: [Str, ""],
            ncols: [Int, 0],
            nrows: [Int, 0],
        }));
    }
}
//# sourceMappingURL=terminal.js.map