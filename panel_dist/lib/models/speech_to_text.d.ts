import type * as p from "@bokehjs/core/properties";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class SpeechToTextView extends HTMLBoxView {
    model: SpeechToText;
    recognition: any;
    buttonEl: HTMLElement;
    initialize(): void;
    iconStarted(): string;
    iconNotStarted(): string;
    setIcon(): void;
    connect_signals(): void;
    setGrammars(): void;
    render(): void;
}
export declare namespace SpeechToText {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        start: p.Property<boolean>;
        stop: p.Property<boolean>;
        abort: p.Property<boolean>;
        grammars: p.Property<any[]>;
        lang: p.Property<string>;
        continuous: p.Property<boolean>;
        interim_results: p.Property<boolean>;
        max_alternatives: p.Property<number>;
        service_uri: p.Property<string>;
        started: p.Property<boolean>;
        audio_started: p.Property<boolean>;
        sound_started: p.Property<boolean>;
        speech_started: p.Property<boolean>;
        button_type: p.Property<string>;
        button_hide: p.Property<boolean>;
        button_not_started: p.Property<string>;
        button_started: p.Property<string>;
        results: p.Property<any[]>;
    };
}
export interface SpeechToText extends SpeechToText.Attrs {
}
export declare class SpeechToText extends HTMLBox {
    properties: SpeechToText.Props;
    constructor(attrs?: Partial<SpeechToText.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=speech_to_text.d.ts.map