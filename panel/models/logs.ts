import { Column, ColumnView } from "./column";
// import * as DOM from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties";

export class LogsView extends ColumnView {
    model: Log;

    connect_signals(): void {
        super.connect_signals();
    }

    update_visible_children(): void {
        const totalChildren = this.model.children.length;

        // Hide all children initially
        this.model.children.forEach((child) => {
            child.visible = false;
        });

        // Make the last 'numberOfVisibleChildren' children visible
        this.model.children.slice(totalChildren - this.model.min_visible).forEach((child) => {
            child.visible = true;
        });
    }

    render(): void {
        super.render()
        this.update_visible_children()
    }

    after_render(): void {
        super.after_render()
    }
}

export namespace Log {
    export type Attrs = p.AttrsOf<Props>;
    export type Props = Column.Props & {
        min_visible: p.Property<number>;
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
        this.prototype.default_view = LogsView;

        this.define<Log.Props>(({ Int }) => ({
            min_visible: [Int, 0],
        }));
    }
}
