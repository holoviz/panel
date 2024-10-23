import type * as p from "@bokehjs/core/properties";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class TextToSpeechView extends HTMLBoxView {
    model: TextToSpeech;
    voices: SpeechSynthesisVoice[];
    _callback: any;
    initialize(): void;
    remove(): void;
    connect_signals(): void;
    speak(): void;
    render(): void;
}
export declare namespace TextToSpeech {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        paused: p.Property<boolean>;
        pending: p.Property<boolean>;
        speaking: p.Property<boolean>;
        voices: p.Property<any[]>;
        cancel: p.Property<boolean>;
        pause: p.Property<boolean>;
        resume: p.Property<boolean>;
        speak: p.Property<any>;
    };
}
export interface TextToSpeech extends TextToSpeech.Attrs {
}
export declare class TextToSpeech extends HTMLBox {
    properties: TextToSpeech.Props;
    constructor(attrs?: Partial<TextToSpeech.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=text_to_speech.d.ts.map