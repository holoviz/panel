import * as p from "core/properties"
import {View} from "core/view"
import {copy} from "core/util/array"
import {Model} from "model"

export class StateView extends View {
  model: State

  renderTo(): void {
  }
}

export namespace State {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Model.Props & {
    state: p.Property<object>
    values: p.Property<any[]>
    widgets: p.Property<{[key: string]: number}>
  }
}

export interface State extends State.Attrs {}

export class State extends Model {
  properties: State.Props

  constructor(attrs?: Partial<State.Attrs>) {
    super(attrs)
  }

  get_state(widget: any): void {
	let values: any[] = copy(this.values)
	const index: any = this.widgets[widget.id]
	values[index] = widget.value
	let state: any = this.state
    for (const i of values) {
      state = state[i]
	}
	this.values = values
	return state
  }
  
  static initClass(): void {
    this.prototype.type = "State"
    this.prototype.default_view = StateView

    this.define<State.Props>({
      state:   [ p.Any, {}        ],
	  widgets: [ p.Any, {}        ],
	  values:  [ p.Any, []        ],
    })
  }
}
State.initClass()
