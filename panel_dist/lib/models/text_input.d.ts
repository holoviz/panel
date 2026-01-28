import { TextInput as BkTextInput, TextInputView as BkTextInputView } from "@bokehjs/models/widgets/text_input";
import type * as p from "@bokehjs/core/properties";
import { ModelEvent } from "@bokehjs/core/bokeh_events";
import type { Attrs } from "@bokehjs/core/types";
export declare class EnterEvent extends ModelEvent {
    readonly value_input: string;
    constructor(value_input: string);
    protected get event_values(): Attrs;
}
export declare class TextInputView extends BkTextInputView {
    model: TextInput;
    _keyup(event: KeyboardEvent): void;
}
export declare namespace TextInput {
    type Attrs = p.AttrsOf<Props>;
    type Props = BkTextInput.Props;
}
export interface TextInput extends TextInput.Attrs {
}
export declare class TextInput extends BkTextInput {
    properties: TextInput.Props;
    constructor(attrs?: Partial<TextInput.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=text_input.d.ts.map