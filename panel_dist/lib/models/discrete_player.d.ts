import type * as p from "@bokehjs/core/properties";
import { PlayerView, Player } from "./player";
export declare class DiscretePlayerView extends PlayerView {
    model: DiscretePlayer;
    append_value_to_title_el(): void;
}
export declare namespace DiscretePlayer {
    type Attrs = p.AttrsOf<Props>;
    type Props = Player.Props & {
        options: p.Property<any>;
    };
}
export interface DiscretePlayer extends DiscretePlayer.Attrs {
}
export declare class DiscretePlayer extends Player {
    properties: DiscretePlayer.Props;
    constructor(attrs?: Partial<DiscretePlayer.Attrs>);
    static __module__: string;
}
//# sourceMappingURL=discrete_player.d.ts.map