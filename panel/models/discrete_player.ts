import type * as p from "@bokehjs/core/properties"
import {PlayerView, Player} from "./player"
import {span} from "@bokehjs/core/dom"
import {to_string} from "@bokehjs/core/util/pretty"

export class DiscretePlayerView extends PlayerView {
  declare model: DiscretePlayer

  override append_value_to_title_el(): void {
    let label = this.model.options[this.model.value]
    if (typeof label !== "string") {
      label = to_string(label)
    }
    this.titleEl.appendChild(span({class: "pn-player-value"}, label))
  }
}

export namespace DiscretePlayer {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Player.Props & {
    options: p.Property<any>
  }
}

export interface DiscretePlayer extends DiscretePlayer.Attrs { }

export class DiscretePlayer extends Player {

  declare properties: DiscretePlayer.Props

  constructor(attrs?: Partial<DiscretePlayer.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = DiscretePlayerView

    this.define<DiscretePlayer.Props>(({List, Any}) => ({
      options: [List(Any), []],
    }))

    this.override<DiscretePlayer.Props>({width: 400})
  }
}
