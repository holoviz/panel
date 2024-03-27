import { Tooltip } from "@bokehjs/models/ui/tooltip";
import type { UIElement } from "@bokehjs/models/ui/ui_element";
import { LayoutDOM, LayoutDOMView } from "@bokehjs/models/layouts/layout_dom";
import type { StyleSheetLike } from "@bokehjs/core/dom";
import type * as p from "@bokehjs/core/properties";
export declare class TooltipIconView extends LayoutDOMView {
    model: TooltipIcon;
    protected desc_el: HTMLElement;
    get child_models(): UIElement[];
    connect_signals(): void;
    stylesheets(): StyleSheetLike[];
    render(): void;
}
export declare namespace TooltipIcon {
    type Attrs = p.AttrsOf<Props>;
    type Props = LayoutDOM.Props & {
        description: p.Property<Tooltip>;
    };
}
export interface TooltipIcon extends TooltipIcon.Attrs {
}
export declare class TooltipIcon extends LayoutDOM {
    properties: TooltipIcon.Props;
    __view_type__: TooltipIconView;
    static __module__: string;
    constructor(attrs?: Partial<TooltipIcon.Attrs>);
}
//# sourceMappingURL=tooltip_icon.d.ts.map