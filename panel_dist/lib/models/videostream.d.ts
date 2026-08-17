import type * as p from "@bokehjs/core/properties";
import { HTMLBox, HTMLBoxView } from "./layout";
export declare class VideoStreamView extends HTMLBoxView {
    model: VideoStream;
    protected videoEl: HTMLVideoElement;
    protected canvasEl: HTMLCanvasElement;
    protected constraints: {
        audio: boolean;
        video: boolean;
    };
    protected timer: any;
    initialize(): void;
    connect_signals(): void;
    pause(): void;
    set_timeout(): void;
    snapshot(): void;
    remove(): void;
    render(): void;
}
export declare namespace VideoStream {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        format: p.Property<string>;
        paused: p.Property<boolean>;
        snapshot: p.Property<boolean>;
        timeout: p.Property<number | null>;
        value: p.Property<any>;
    };
}
export interface VideoStream extends VideoStream.Attrs {
}
export declare class VideoStream extends HTMLBox {
    properties: VideoStream.Props;
    constructor(attrs?: Partial<VideoStream.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=videostream.d.ts.map