import { Column, ColumnView } from "./column";
// import * as DOM from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties";

export class LogsView extends ColumnView {
    model: Logs;

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

export namespace Logs {
    export type Attrs = p.AttrsOf<Props>;
    export type Props = Column.Props & {
        min_visible: p.Property<number>;
    };
}

export interface Logs extends Logs.Attrs { }

export class Logs extends Column {
    properties: Logs.Props;

    constructor(attrs?: Partial<Logs.Attrs>) {
        super(attrs);
    }

    static __module__ = "panel.models.layout";

    static {
        this.prototype.default_view = LogsView;

        this.define<Logs.Props>(({ Int }) => ({
            min_visible: [Int, 0],
        }));
    }
}
