import { TextAreaInput as BkTextAreaInput, TextAreaInputView as BkTextAreaInputView } from "@bokehjs/models/widgets/textarea_input";
import type * as p from "@bokehjs/core/properties";
export declare class TextAreaInputView extends BkTextAreaInputView {
    model: TextAreaInput;
    connect_signals(): void;
    update_rows(): void;
    render(): void;
}
export declare namespace TextAreaInput {
    type Attrs = p.AttrsOf<Props>;
    type Props = BkTextAreaInput.Props & {
        auto_grow: p.Property<boolean>;
        max_rows: p.Property<number | null>;
    };
}
export interface TextAreaInput extends TextAreaInput.Attrs {
}
export declare class TextAreaInput extends BkTextAreaInput {
    properties: TextAreaInput.Props;
    constructor(attrs?: Partial<TextAreaInput.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=textarea_input.d.ts.map