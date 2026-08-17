import type { DOMView } from "@bokehjs/core/dom_view";
import { WidgetView } from "@bokehjs/models/widgets/widget";
import type { Markup } from "@bokehjs/models/widgets/markup";
import { LayoutDOM, LayoutDOMView } from "@bokehjs/models/layouts/layout_dom";
import type { UIElement } from "@bokehjs/models/ui/ui_element";
import type * as p from "@bokehjs/core/properties";
/**
 * Re-renders a view, including its layout.
 *
 * Bokeh's own `rerender` runs the whole render walk before `update_layout`,
 * which is wrong for anything that is positioned by the layout: `render`
 * re-parents annotation elements into the canvas layers and it is
 * `update_layout` that moves them into their side panels. Measuring in
 * between therefore caches a bbox for the container the element is about to
 * leave, e.g. a legend measuring the full canvas width instead of its side
 * panel. `compute_layout` then sizes the panel from that stale bbox and can
 * squeeze the frame to zero, which poisons everything derived from it (for
 * tile-based plots, a division by zero width puts NaN into the ranges with no
 * recovery path). Updating the layout first means `after_render` measures
 * elements where they will actually live.
 */
export declare function rerender_view(view: DOMView): void;
export declare class PanelMarkupView extends WidgetView {
    model: Markup;
    container: HTMLDivElement;
    protected _initialized_stylesheets: Map<string, boolean>;
    protected _stylesheets_watcher: AbortController | null;
    connect_signals(): void;
    lazy_initialize(): Promise<void>;
    /**
     * Schedules `style_redraw` for when all applied stylesheets have settled.
     *
     * A stylesheet counts as settled once it has loaded *or* failed: views
     * reveal their container from `style_redraw`, so a stylesheet that never
     * arrives must not hide them forever. Listeners registered by a previous
     * call are cancelled, since the elements they watch have been discarded.
     */
    watch_stylesheets(): void;
    /**
     * Bokeh recreates the stylesheet elements on every update, discarding the
     * ones `watch_stylesheets` listens on, so the watcher has to be re-armed.
     * Skipped until the view has armed it itself, as the update triggered from
     * `super.render()` precedes the creation of `this.container`.
     */
    protected _update_stylesheets(): void;
    rerender_(view?: DOMView | null): void;
    style_redraw(): void;
    has_math_disabled(): boolean;
    render(): void;
}
export declare function set_size(el: HTMLElement, model: HTMLBox, adjust_margin?: boolean): void;
export declare abstract class HTMLBoxView extends LayoutDOMView {
    model: HTMLBox;
    protected _initialized_stylesheets: Map<string, boolean>;
    connect_signals(): void;
    render(): void;
    rerender_(view?: DOMView | null): void;
    watch_stylesheets(): void;
    style_redraw(): void;
    get child_models(): UIElement[];
}
export declare namespace HTMLBox {
    type Attrs = p.AttrsOf<Props>;
    type Props = LayoutDOM.Props;
}
export interface HTMLBox extends HTMLBox.Attrs {
}
export declare abstract class HTMLBox extends LayoutDOM {
    properties: HTMLBox.Props;
    constructor(attrs?: Partial<HTMLBox.Attrs>);
}
//# sourceMappingURL=layout.d.ts.map