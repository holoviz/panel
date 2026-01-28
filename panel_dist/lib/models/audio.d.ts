import type * as p from "@bokehjs/core/properties";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class AudioView extends HTMLBoxView {
    model: Audio;
    protected audioEl: HTMLAudioElement;
    protected dialogEl: HTMLElement;
    private _blocked;
    private _time;
    private _setting;
    initialize(): void;
    connect_signals(): void;
    render(): void;
    update_time(view: AudioView): void;
    update_volume(view: AudioView): void;
    set_loop(): void;
    set_muted(): void;
    set_autoplay(): void;
    set_paused(): void;
    set_volume(): void;
    set_time(): void;
    set_value(): void;
}
export declare namespace Audio {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        loop: p.Property<boolean>;
        paused: p.Property<boolean>;
        muted: p.Property<boolean>;
        autoplay: p.Property<boolean>;
        time: p.Property<number>;
        throttle: p.Property<number>;
        value: p.Property<any>;
        volume: p.Property<number | null>;
    };
}
export interface Audio extends Audio.Attrs {
}
export declare class Audio extends HTMLBox {
    properties: Audio.Props;
    constructor(attrs?: Partial<Audio.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=audio.d.ts.map