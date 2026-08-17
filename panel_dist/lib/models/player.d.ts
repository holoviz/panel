import type * as p from "@bokehjs/core/properties";
import { Widget, WidgetView } from "@bokehjs/models/widgets/widget";
export declare class PlayerView extends WidgetView {
    model: Player;
    protected buttonEl: HTMLDivElement;
    protected titleEl: HTMLDivElement;
    protected groupEl: HTMLDivElement;
    protected sliderEl: HTMLInputElement;
    protected loop_state: HTMLFormElement;
    protected timer: any;
    protected _toggle_reverse: CallableFunction;
    protected _toogle_pause: CallableFunction;
    protected _toggle_play: CallableFunction;
    protected _changing: boolean;
    protected slower: HTMLButtonElement;
    protected first: HTMLButtonElement;
    protected previous: HTMLButtonElement;
    protected reverse: HTMLButtonElement;
    protected pause: HTMLButtonElement;
    protected play: HTMLButtonElement;
    protected next: HTMLButtonElement;
    protected last: HTMLButtonElement;
    protected faster: HTMLButtonElement;
    connect_signals(): void;
    toggle_disable(): void;
    get_height(): number;
    update_css(): void;
    update_value(): void;
    render(): void;
    set_frame(frame: number, throttled?: boolean): void;
    get_loop_state(): string;
    update_title_and_value(): void;
    append_value_to_title_el(): void;
    set_value_align(): void;
    set_loop_state(state: string): void;
    next_frame(): void;
    previous_frame(): void;
    first_frame(): void;
    last_frame(): void;
    updateSpeedButton(button: HTMLButtonElement, interval: number, originalSVG: string): void;
    slower_speed(): void;
    faster_speed(): void;
    anim_step_forward(): void;
    anim_step_reverse(): void;
    set_direction(): void;
    pause_animation(): void;
    play_animation(): void;
    reverse_animation(): void;
}
export declare const LoopPolicy: import("@bokehjs/core/kinds").Kinds.Enum<"loop" | "once" | "reflect">;
export declare namespace Player {
    type Attrs = p.AttrsOf<Props>;
    type Props = Widget.Props & {
        direction: p.Property<number>;
        interval: p.Property<number>;
        start: p.Property<number>;
        end: p.Property<number>;
        step: p.Property<number>;
        loop_policy: p.Property<typeof LoopPolicy["__type__"]>;
        title: p.Property<string>;
        value: p.Property<any>;
        value_align: p.Property<string>;
        value_throttled: p.Property<any>;
        preview_duration: p.Property<number>;
        show_loop_controls: p.Property<boolean>;
        show_value: p.Property<boolean>;
        button_scale: p.Property<number>;
        scale_buttons: p.Property<number>;
        visible_buttons: p.Property<string[]>;
        visible_loop_options: p.Property<string[]>;
    };
}
export interface Player extends Player.Attrs {
}
export declare class Player extends Widget {
    properties: Player.Props;
    constructor(attrs?: Partial<Player.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=player.d.ts.map