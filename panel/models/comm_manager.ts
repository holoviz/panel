import * as p from "@bokehjs/core/properties"
import {DocumentChangedEvent, ModelChangedEvent} from "@bokehjs/document"
import {View} from "@bokehjs/core/view"
import {Model} from "@bokehjs/model"
import {Message} from "@bokehjs/protocol/message"
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
    client_comm_id: p.Property<string | null>
    timeout: p.Property<number>
    debounce: p.Property<number>
  }
}

export interface CommManager extends CommManager.Attrs {}

export class CommManager extends Model {
  properties: CommManager.Props
  ns: any
  _receiver: Receiver
  _client_comm: any
  _event_buffer: DocumentChangedEvent[]
  _timeout: number
  _blocked: boolean

  constructor(attrs?: Partial<CommManager.Attrs>) {
    super(attrs)
    this._receiver = new Receiver()
    this._event_buffer = []
    this._blocked = false
    this._timeout = Date.now()
    if (((window as any).PyViz == undefined) || (!(window as any).PyViz.comm_manager))
      console.log("Could not find comm manager on window.PyViz, ensure the extension is loaded.")
    else {
      this.ns = (window as any).PyViz
      this.ns.comm_manager.register_target(this.plot_id, this.comm_id, (msg: any) => this.msg_handler(msg))
      this._client_comm = this.ns.comm_manager.get_client_comm(this.plot_id, this.client_comm_id, (msg: any) => this.on_ack(msg));
    }
  }

  protected _document_listener: (event: DocumentChangedEvent) => void = (event) => this._document_changed(event)

  protected _doc_attached(): void {
    super._doc_attached()
    if (this.document != null)
      this.document.on_change(this._document_listener)
  }

  protected _document_changed(event: DocumentChangedEvent): void {
    // Filter out events that were initiated by the ClientSession itself
    if ((event as any).setter_id === this.id) // XXX: not all document events define this
      return

    // Filter out changes to attributes that aren't server-visible
    if (event instanceof ModelChangedEvent && !(event.attr in event.model.serializable_attributes()))
      return

    this._event_buffer.push(event);
    if ((!this._blocked || (Date.now() > this._timeout))) {
      setTimeout(() => this.process_events(), this.debounce);
      this._blocked = true;
      this._timeout = Date.now()+this.timeout;
    }
  }

  process_events() {
    if ((this.document == null) || (this._client_comm == null))
      return
    const patch = this.document.create_json_patch(this._event_buffer)
    this._event_buffer = [];
    const message = Message.create('PATCH-DOC', {}, patch)
    this._client_comm.send(message)
  }

  on_ack(msg: any) {
    // Receives acknowledgement from Python, processing event
    // and unblocking Comm if event queue empty
    const metadata = msg.metadata
    if (this._event_buffer.length) {
      this._blocked = true
      this._timeout = Date.now()+this.timeout
      this.process_events()
    } else
      this._blocked = false;
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
      let plot = null
      if ((plot_id in this.ns.plot_index) && (this.ns.plot_index[plot_id] != null))
        plot = this.ns.plot_index[plot_id]
      else if (((window as any).Bokeh !== undefined) && (plot_id in (window as any).Bokeh.index))
        plot = (window as any).Bokeh.index[plot_id]

      if (plot == null)
        return

      if ((buffers != undefined) && (buffers.length > 0))
        this._receiver.consume(buffers[0].buffer)
      else
        this._receiver.consume(content)

      const comm_msg = this._receiver.message
      if ((comm_msg != null) && (Object.keys(comm_msg.content).length > 0) && this.document != null)
        this.document.apply_json_patch(comm_msg.content, comm_msg.buffers, this.id)
    }
  }

  static __module__ = "panel.models.comm_manager"

  static init_CommManager(): void {
    this.prototype.default_view = CommManagerView

    this.define<CommManager.Props>(({Int, String}) => ({
      plot_id:        [ String    ],
      comm_id:        [ String    ],
      client_comm_id: [ String    ],
      timeout:        [ Int, 5000 ],
      debounce:       [ Int,   50 ],
    }))
  }
}
