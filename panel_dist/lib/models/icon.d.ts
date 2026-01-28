import type { TooltipView } from "@bokehjs/models/ui/tooltip";
import { Tooltip } from "@bokehjs/models/ui/tooltip";
import type { TablerIconView } from "@bokehjs/models/ui/icons/tabler_icon";
import type { SVGIconView } from "@bokehjs/models/ui/icons/svg_icon";
import { Control, ControlView } from "@bokehjs/models/widgets/control";
import type { IterViews } from "@bokehjs/core/build_views";
import type * as p from "@bokehjs/core/properties";
import { ButtonClick } from "@bokehjs/core/bokeh_events";
import type { EventCallback } from "@bokehjs/model";
export declare class ClickableIconView extends ControlView {
    model: ClickableIcon;
    icon_view: TablerIconView | SVGIconView;
    label_el: HTMLDivElement;
    was_svg_icon: boolean;
    row_div: HTMLDivElement;
    protected tooltip: TooltipView | null;
    controls(): Generator<never, void, unknown>;
    remove(): void;
    lazy_initialize(): Promise<void>;
    children(): IterViews;
    is_svg_icon(icon: string): boolean;
    connect_signals(): void;
    update_tooltip(): Promise<void>;
    render(): void;
    update_label(): void;
    update_cursor(): void;
    update_size(): void;
    build_icon_model(icon: string, is_svg_icon: boolean): Promise<TablerIconView | SVGIconView>;
    update_icon(): Promise<void>;
    get_active_icon(): string;
    calculate_size(factor?: number): string;
    click(): void;
}
export declare namespace ClickableIcon {
    type Attrs = p.AttrsOf<Props>;
    type Props = Control.Props & {
        active_icon: p.Property<string>;
        icon: p.Property<string>;
        size: p.Property<string | null>;
        value: p.Property<boolean>;
        title: p.Property<string>;
        tooltip: p.Property<Tooltip | null>;
        tooltip_delay: p.Property<number>;
    };
}
export interface ClickableIcon extends ClickableIcon.Attrs {
}
export declare class ClickableIcon extends Control {
    properties: ClickableIcon.Props;
    __view_type__: ClickableIconView;
    static __module__: string;
    constructor(attrs?: Partial<ClickableIcon.Attrs>);
    on_click(callback: EventCallback<ButtonClick>): void;
}
//# sourceMappingURL=icon.d.ts.map