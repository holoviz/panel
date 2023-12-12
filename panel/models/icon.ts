import { TablerIcon, TablerIconView } from "@bokehjs/models/ui/icons/tabler_icon"
import { Control, ControlView } from '@bokehjs/models/widgets/control'
import type {IterViews} from '@bokehjs/core/build_views'
import * as p from "@bokehjs/core/properties";
import {build_view} from '@bokehjs/core/build_views'

export class ToggleIconView extends ControlView {
    model: ToggleIcon;
    icon_view: TablerIconView;

    public *controls() { }

    override remove(): void {
        this.icon_view?.remove()
        super.remove()
    }

    override async lazy_initialize(): Promise<void> {
        await super.lazy_initialize()

        const icon_model = new TablerIcon({ icon_name: this.model.icon_name })
        this.icon_view = await build_view(icon_model, { parent: this })
    }

    override *children(): IterViews {
        yield* super.children()
        yield this.icon_view
    }

    change_input(): void {}

    connect_signals(): void {
        super.connect_signals();
    }

    render(): void {
        super.render()

        this.icon_view.render()
        this.shadow_el.appendChild(this.icon_view.el)
    }
}

export namespace ToggleIcon {
    export type Attrs = p.AttrsOf<Props>;
    export type Props = Control.Props & {
        icon_name: p.Property<string>;
        value: p.Property<boolean>;
    };
}

export interface ToggleIcon extends ToggleIcon.Attrs { }

export class ToggleIcon extends Control {
    properties: ToggleIcon.Props;
    declare __view_type__: ToggleIconView
    static __module__ = "panel.models.icon";

    constructor(attrs?: Partial<ToggleIcon.Attrs>) {
        super(attrs);
    }

    static {
        this.prototype.default_view = ToggleIconView;

        this.define<ToggleIcon.Props>(({ String, Boolean }) => ({
            icon_name: [String, "heart"],
            value: [Boolean, false],
        }));
    }
}
