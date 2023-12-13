import { Column, ColumnView } from "./column";
// import * as DOM from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties";

export class LogView extends ColumnView {
    model: Log;
    loadedEntries: number;

    connect_signals(): void {
        super.connect_signals();

        const { children, min_entries, scroll_load_threshold } = this.model.properties;

        this.on_change(children, () => this.handle_new_entries());
        this.on_change(min_entries, () => this.hide_unloaded_entries());
        this.on_change(scroll_load_threshold, () => this.trigger_load_entries());
    }

    handle_new_entries(): void {
        this.loadedEntries = Math.min(this.model.children.length, this.loadedEntries);
        this.hide_unloaded_entries();
        this.trigger_load_entries();
    }

    hide_unloaded_entries(): void {
        for (let i = 0; i < this.model.children.length - this.loadedEntries; i++) {
            this.model.children[i].visible = false;
        }
    }

    show_loaded_entries(): void {
        for (let i = this.model.children.length - this.loadedEntries; i < this.model.children.length; i++) {
            this.model.children[i].visible = true;
        }
    }

    trigger_load_entries(): void {
        if (this.el.scrollTop < this.model.scroll_load_threshold && this.loadedEntries < this.model.children.length) {
            const entriesToAdd = Math.min(this.model.entries_per_load, this.model.children.length - this.loadedEntries);
            this.loadedEntries += entriesToAdd;

            const initialHeight = this.el.scrollHeight;
            this.show_loaded_entries();
            const newHeight = this.el.scrollHeight;
            const heightDifference = newHeight - initialHeight;
            this.model.scroll_position = Math.round(heightDifference);
        }
    }

    reset_loaded_entries(): void {
        this.loadedEntries = this.model.min_entries;
        this.hide_unloaded_entries();
    }

    render(): void {
        super.render()
        this.reset_loaded_entries()
        this.el.addEventListener("scroll", () => {
            this.trigger_load_entries();
        });
    }

    after_render(): void {
        super.after_render()
    }
}

export namespace Log {
    export type Attrs = p.AttrsOf<Props>;
    export type Props = Column.Props & {
        min_entries: p.Property<number>;
        entries_per_load: p.Property<number>;
        scroll_load_threshold: p.Property<number>;
    };
}

export interface Log extends Log.Attrs { }

export class Log extends Column {
    properties: Log.Props;

    constructor(attrs?: Partial<Log.Attrs>) {
        super(attrs);
    }

    static __module__ = "panel.models.layout";

    static {
        this.prototype.default_view = LogView;

        this.define<Log.Props>(({ Int }) => ({
            min_entries: [Int, 20],
            entries_per_load: [Int, 20],
            scroll_load_threshold: [Int, 40],
        }));
    }
}
