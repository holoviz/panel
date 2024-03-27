import { Column, ColumnView } from "./column";
import type * as p from "@bokehjs/core/properties";
import type { UIElementView } from "@bokehjs/models/ui/ui_element";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { EventCallback } from "@bokehjs/model";
export declare class ScrollButtonClick extends ModelEvent {
}
export declare class FeedView extends ColumnView {
    model: Feed;
    _intersection_observer: IntersectionObserver;
    _last_visible: UIElementView | null;
    _sync: boolean;
    initialize(): void;
    get node_map(): any;
    update_children(): Promise<void>;
    build_child_views(): Promise<UIElementView[]>;
    scroll_to_latest(emit_event?: boolean): void;
    trigger_auto_scroll(): void;
}
export declare namespace Feed {
    type Attrs = p.AttrsOf<Props>;
    type Props = Column.Props & {
        visible_children: p.Property<string[]>;
    };
}
export interface Feed extends Feed.Attrs {
}
export declare class Feed extends Column {
    properties: Feed.Props;
    constructor(attrs?: Partial<Feed.Attrs>);
    static __module__: string;
    on_click(callback: EventCallback<ScrollButtonClick>): void;
}
//# sourceMappingURL=feed.d.ts.map