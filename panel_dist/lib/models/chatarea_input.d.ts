import { TextAreaInput as PnTextAreaInput, TextAreaInputView as PnTextAreaInputView } from "./textarea_input";
import type * as p from "@bokehjs/core/properties";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { Attrs } from "@bokehjs/core/types";
export declare class ChatMessageEvent extends ModelEvent {
    readonly value: string;
    constructor(value: string);
    get event_values(): Attrs;
}
export declare class ChatAreaInputView extends PnTextAreaInputView {
    model: ChatAreaInput;
    connect_signals(): void;
    render(): void;
}
export declare namespace ChatAreaInput {
    type Attrs = p.AttrsOf<Props>;
    type Props = PnTextAreaInput.Props & {
        disabled_enter: p.Property<boolean>;
        enter_sends: p.Property<boolean>;
    };
}
export interface ChatAreaInput extends ChatAreaInput.Attrs {
}
export declare class ChatAreaInput extends PnTextAreaInput {
    declare: ChatAreaInput.Props;
    constructor(attrs?: Partial<ChatAreaInput.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=chatarea_input.d.ts.map