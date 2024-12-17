import type * as p from "@bokehjs/core/properties"
import {View} from "@bokehjs/core/view"
import {copy} from "@bokehjs/core/util/array"
import {Model} from "@bokehjs/model"
import {Receiver} from "@bokehjs/protocol/receiver"
import type {Patch} from "@bokehjs/document"

function get_json(file: string, callback: any): void {
  const xobj = new XMLHttpRequest()
  xobj.overrideMimeType("application/json")
  xobj.open("GET", file, true)
  xobj.onreadystatechange = function() {
    if (xobj.readyState == 4 && xobj.status == 200) {
      callback(xobj.responseText)
    }
  }
  xobj.send(null)
}

export class StateView extends View {
  declare model: State
}

export namespace State {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Model.Props & {
    json: p.Property<boolean>
    state: p.Property<object>
    values: p.Property<any[]>
    widgets: p.Property<{[key: string]: number}>
  }
}

export interface State extends State.Attrs {}

export class State extends Model {
  declare properties: State.Props
  _receiver: Receiver
  _cache: {[key: string]: string}

  constructor(attrs?: Partial<State.Attrs>) {
    super(attrs)
    this._receiver = new Receiver()
    this._cache = {}
  }

  apply_state(state: any): void {
    this._receiver.consume(state.header)
    this._receiver.consume(state.metadata)
    this._receiver.consume(state.content)
    if (this._receiver.message && this.document) {
      this.document.apply_json_patch(this._receiver.message.content as Patch)
    }
  }

  _receive_json(result: string, path: string): void {
    const state = JSON.parse(result)
    this._cache[path] = state
    let current: any = this.state
    for (const i of this.values) {
      if (current instanceof Map) {
        current = current.get(i)
      } else {
        current = current[i]
      }
    }
    if (current === path) {
      this.apply_state(state)
    } else if (this._cache[current]) {
      this.apply_state(this._cache[current])
    }
  }

  set_state(widget: any, value: any): void {
    const values: any[] = copy(this.values)
    const index: any = this.widgets[widget.id]
    values[index] = value
    let state: any = this.state
    for (const i of values) {
      if (state instanceof Map) {
        state = state.get(i)
      } else {
        state = state[i]
      }
    }
    this.values = values
    if (this.json) {
      if (this._cache[state]) {
        this.apply_state(this._cache[state])
      } else {
        get_json(state, (result: string) => this._receive_json(result, state))
      }
    } else {
      this.apply_state(state)
    }
  }

  static override __module__ = "panel.models.state"

  static {
    this.prototype.default_view = StateView

    this.define<State.Props>(({Any, Bool}) => ({
      json:    [ Bool, false ],
      state:   [ Any,        {} ],
      widgets: [ Any,        {} ],
      values:  [ Any,        [] ],
    }))
  }
}
