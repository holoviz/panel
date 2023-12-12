import { TablerIcon, TablerIconView } from "@bokehjs/models/ui/icons/tabler_icon"
// import * as DOM from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties";

export class ToggleIconView extends TablerIconView {
    model: TablerIcon

    connect_signals(): void {
        super.connect_signals();
    }

    render(): void {
        super.render()
    }
}

export namespace ToggleIcon {
    export type Attrs = p.AttrsOf<Props>;
    export type Props = TablerIcon.Props & {
        value: p.Property<boolean>;
    };
}

export interface ToggleIcon extends ToggleIcon.Attrs { }

export class ToggleIcon extends TablerIcon {
    properties: ToggleIcon.Props;

    constructor(attrs?: Partial<ToggleIcon.Attrs>) {
        super(attrs);
    }

    static __module__ = "panel.models.icon";

    static {
        this.prototype.default_view = ToggleIconView;

        this.define<ToggleIcon.Props>(({ String, Boolean }) => ({
            icon_name: [String],
            value: [Boolean, false],
        }));
    }
}
