import {MultiSelect, MultiSelectView} from "@bokehjs/models/widgets/multiselect"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import type * as p from "@bokehjs/core/properties"
import type {Attrs} from "@bokehjs/core/types"

export class DoubleClickEvent extends ModelEvent {
  constructor(readonly option: any) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, option: this.option}
  }

  static {
    this.prototype.event_name = "dblclick_event"
  }
}

export class CustomMultiSelectView extends MultiSelectView {
  declare model: CustomMultiSelect

  override render(): void {
    super.render()
    for (const option of this.input_el.children) {
      option.addEventListener("dblclick", (event) => {
        if (event.target) {
          this.model.trigger_event(new DoubleClickEvent((event.target as HTMLOptionElement).value))
        }
      })

    }
  }
}

export namespace CustomMultiSelect {
  export type Attrs = p.AttrsOf<Props>

  export type Props = MultiSelect.Props
}

export interface CustomMultiSelect extends CustomMultiSelect.Attrs {}

export class CustomMultiSelect extends MultiSelect {
  declare properties: CustomMultiSelect.Props
  declare __view_type__: CustomMultiSelectView

  constructor(attrs?: Partial<CustomMultiSelect.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.widgets"

  static {
    this.prototype.default_view = CustomMultiSelectView
  }
}
