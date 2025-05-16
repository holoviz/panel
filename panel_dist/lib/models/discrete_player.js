import { PlayerView, Player } from "./player";
import { span } from "@bokehjs/core/dom";
import { to_string } from "@bokehjs/core/util/pretty";
export class DiscretePlayerView extends PlayerView {
    static __name__ = "DiscretePlayerView";
    append_value_to_title_el() {
        let label = this.model.options[this.model.value];
        if (typeof label !== "string") {
            label = to_string(label);
        }
        this.titleEl.appendChild(span({ class: "pn-player-value" }, label));
    }
}
export class DiscretePlayer extends Player {
    static __name__ = "DiscretePlayer";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.widgets";
    static {
        this.prototype.default_view = DiscretePlayerView;
        this.define(({ List, Any }) => ({
            options: [List(Any), []],
        }));
        this.override({ width: 400 });
    }
}
//# sourceMappingURL=discrete_player.js.map