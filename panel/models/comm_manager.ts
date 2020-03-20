import * as p from "@bokehjs/core/properties"
import {View} from "@bokehjs/core/view"
import {Model} from "@bokehjs/model"
import {Receiver} from "@bokehjs/protocol/receiver"

export class CommManagerView extends View {
  model: CommManager

  renderTo(): void {
  }
}

export namespace CommManager {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Model.Props & {
    plot_id: p.Property<string | null>
    comm_id: p.Property<string | null>
  }
}

export interface CommManager extends CommManager.Attrs {}

export class CommManager extends Model {
  properties: CommManager.Props
  _receiver: Receiver

  constructor(attrs?: Partial<CommManager.Attrs>) {
    super(attrs)
    this._receiver = new Receiver()
    if (((window as any).PyViz == undefined) || (!(window as any).PyViz.comm_manager))
      console.log("Could not find comm manager")
    else
      (window as any).PyViz.comm_manager.register_target(this.plot_id, this.comm_id, (msg: any) => this.msg_handler(msg))
  }

  msg_handler(msg: any) {
    const metadata = msg.metadata
    const buffers = msg.buffers
    const content = msg.content.data
    const plot_id = this.plot_id
    console.log("NEW MSG")
    if ((metadata.msg_type == "Ready")) {
      if (metadata.content)
        console.log("Python callback returned following output:", metadata.content)
      else if (metadata.msg_type == "Error")
        console.log("Python failed with the following traceback:", metadata.traceback)
    } else if (plot_id != null) {
      if ((plot_id in (window as any).PyViz.plot_index) && ((window as any).PyViz.plot_index[plot_id] != null))
        var plot = (window as any).PyViz.plot_index[plot_id]
      else if (((window as any).Bokeh !== undefined) && (plot_id in (window as any).Bokeh.index))
        var plot = (window as any).Bokeh.index[plot_id]

      if (plot == null)
        return

      if ((buffers != undefined) && (buffers.length > 0))
        this._receiver.consume(buffers[0].buffer)
      else
        this._receiver.consume(content)

      const comm_msg = this._receiver.message
      if ((comm_msg != null) && (Object.keys(comm_msg.content).length > 0) && this.document != null)
        this.document.apply_json_patch(comm_msg.content, comm_msg.buffers)
    }
  }

  static __module__ = "panel.models.comm_manager"

  static init_CommManager(): void {
    this.prototype.default_view = CommManagerView

    this.define<CommManager.Props>({
      plot_id: [ p.String, null ],
      comm_id: [ p.String, null ],
    })
  }
}
