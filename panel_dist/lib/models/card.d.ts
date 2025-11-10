import type { StyleSheetLike } from "@bokehjs/core/dom";
import * as DOM from "@bokehjs/core/dom";
import type * as p from "@bokehjs/core/properties";
import { Column, ColumnView } from "./column";
export declare class CardView extends ColumnView {
    model: Card;
    button_el: HTMLButtonElement;
    header_el: HTMLElement;
    readonly collapsed_style: DOM.InlineStyleSheet;
    connect_signals(): void;
    stylesheets(): StyleSheetLike[];
    protected _stylesheets(): Iterable<DOM.StyleSheetLike>;
    get header_background(): string | null;
    render(): void;
    update_children(): Promise<void>;
    _update_layout(): void;
    _toggle_button(e: MouseEvent): void;
    _collapse(): void;
    protected _create_element(): HTMLElement;
}
export declare namespace Card {
    type Attrs = p.AttrsOf<Props>;
    type Props = Column.Props & {
        active_header_background: p.Property<string | null>;
        button_css_classes: p.Property<string[]>;
        collapsed: p.Property<boolean>;
        collapsible: p.Property<boolean>;
        header_background: p.Property<string | null>;
        header_color: p.Property<string | null>;
        header_css_classes: p.Property<string[]>;
        header_tag: p.Property<string>;
        hide_header: p.Property<boolean>;
        tag: p.Property<string>;
    };
}
export interface Card extends Card.Attrs {
}
export declare class Card extends Column {
    properties: Card.Props;
    constructor(attrs?: Partial<Card.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=card.d.ts.map