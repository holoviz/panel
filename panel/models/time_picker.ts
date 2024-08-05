import {TimePicker as BkTimePicker, TimePickerView as BkTimePickerView} from "@bokehjs/models/widgets/time_picker"
import type * as p from "@bokehjs/core/properties"



export class TimePickerView extends BkTimePickerView {
    declare model: TimePicker

    // Override the render method or any method where time rendering is done
    override render(): void {
        // Fix time zone difference; add back 8 hours
        const date = this.model.value ? new Date(this.model.value) : new Date();
        date.setHours(date.getHours() + 8);

        console.log(date);

        // get type of date
        console.log(this.model.value)
        console.log("Type of Date:", typeof this.model.value);

        console.log("Converted Date:", date.toISOString());
        console.log("Converted Time:", date.getTime());
        this.model.value = 72000000

        super.render();
    }
  }

  export namespace TimePicker {
    export type Attrs = p.AttrsOf<Props>
    export type Props = BkTimePicker.Props & {
    }
  }

  export interface TimePicker extends TimePicker.Attrs { }

  export class TimePicker extends BkTimePicker {
    declare properties: TimePicker.Props

    constructor(attrs?: Partial<TimePicker.Attrs>) {
      super(attrs)
    }

    static override __module__ = "panel.models.time_picker"

    static {
      this.prototype.default_view = TimePickerView

      this.define<TimePicker.Props>(({}) => ({
      }))
    }
  }
