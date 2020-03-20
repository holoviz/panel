import * as p from "@bokehjs/core/properties"
import {View} from "@bokehjs/core/view"
import {Model} from "@bokehjs/model"
import {Receiver} from "@bokehjs/protocol/receiver"

function unique_events(events: any[]) {
  // Processes the event queue ignoring duplicate events
  // of the same type
  const unique = [];
  const unique_events = [];
  for (let i=0; i<events.length; i++) {
    const _tmpevent = events[i];
    const event = _tmpevent[0];
    const data = _tmpevent[1];
    if (unique_events.indexOf(event)===-1) {
      unique.unshift(data);
      unique_events.push(event);
    }
  }
  return unique;
}

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
  _comm_status: any
  _comms: any

  constructor(attrs?: Partial<CommManager.Attrs>) {
    super(attrs)
    this._receiver = new Receiver()
    this._comm_status = {}
    this._comms = {}
    if (((window as any).PyViz == undefined) || (!(window as any).PyViz.comm_manager))
      console.log("Could not find comm manager")
    else
      (window as any).PyViz.comm_manager.register_target(this.plot_id, this.comm_id, (msg: any) => this.msg_handler(msg))
  }

  send(comm_id: string, data: any, event_name?: string) {
    if (((window as any).PyViz == undefined) || ((window as any).PyViz.comm_manager == undefined))
      return

    const receiver = (this._receiver as any)
    let events = [];
    if (receiver._partial && receiver._partial.content && receiver._partial.content.events)
      events = receiver._partial.content.events;

    for (const event of events) {
      if ((event.kind === 'ModelChanged') && (event.attr === event_name) &&
          (data.id === event.model.id) &&
          (JSON.stringify(data[(event_name as string)]) === JSON.stringify(event.new)))
        return
    }

    if (!(comm_id in this._comms)) {
      const comm = (window as any).PyViz.comm_manager.get_client_comm(this.plot_id, comm_id, (msg: any) => this.on_ack(msg));
      if (comm == null)
        return
      this._comms[comm_id] = comm
      this._comm_status[comm_id] = {event_buffer: [], blocked: false, time: Date.now()}
    }

    const comm_status = this._comm_status[comm_id]
    if (event_name === undefined)
      event_name = Object.keys(data).join(',') // we are a widget not an event... fake a key.
    data['comm_id'] = comm_id;
    var timeout = comm_status.time + 5000;

    comm_status.event_buffer.unshift([event_name, data]);
    if ((!comm_status.blocked || (Date.now() > timeout))) {
      setTimeout(() => this.process_events(comm_id), 50);
      comm_status.blocked = true;
      comm_status.time = Date.now()+50;
    }
  }

  process_events(comm_id: string) {
    const comm = this._comms[comm_id]
    const comm_status = this._comm_status[comm_id]
    // Iterates over event queue and sends events via Comm
    const events = unique_events(comm_status.event_buffer);
    for (let i=0; i<events.length; i++) {
      const data = events[i];
      comm.send(data);
    }
    comm_status.event_buffer = [];
  }

  on_ack(msg: any) {
    // Receives acknowledgement from Python, processing event
    // and unblocking Comm if event queue empty
    const metadata = msg.metadata;
    const comm_id = metadata.comm_id
    const comm_status = this._comm_status[comm_id]
    if (comm_status.event_buffer.length) {
      this.process_events(comm_id)
      comm_status.blocked = true
      comm_status.time = Date.now()+50
    } else
      comm_status.blocked = false;
    comm_status.event_buffer = [];
    if ((metadata.msg_type == "Ready") && metadata.content)
      console.log("Python callback returned following output:", metadata.content)
    else if (metadata.msg_type == "Error")
      console.log("Python failed with the following traceback:", metadata.traceback)
  }

  msg_handler(msg: any) {
    const metadata = msg.metadata
    const buffers = msg.buffers
    const content = msg.content.data
    const plot_id = this.plot_id
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
