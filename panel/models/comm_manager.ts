import * as p from "@bokehjs/core/properties"
import {DocumentChangedEvent, ModelChangedEvent} from "@bokehjs/document"
import {View} from "@bokehjs/core/view"
import {Model} from "@bokehjs/model"
import {Message} from "@bokehjs/protocol/message"
import {Receiver} from "@bokehjs/protocol/receiver"
import {Patch} from "@bokehjs/document"

export const comm_settings: any = {
  debounce: true
}

export class CommManagerView extends View {
  override model: CommManager
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
  override properties: CommManager.Props
  override __view_type__: CommManagerView

  ns: any
  _receiver: Receiver
  _client_comm: any
  _event_buffer: DocumentChangedEvent[]
  _timeout: number
  _blocked: boolean

  constructor(attrs?: Partial<CommManager.Attrs>) {
    super(attrs)
  }

  override initialize(): void {
    super.initialize()
    this._receiver = new Receiver()
    this._event_buffer = []
    this._blocked = false
    this._timeout = Date.now()
    if (((window as any).PyViz == undefined) || (!(window as any).PyViz.comm_manager))
      console.log("Could not find comm manager on window.PyViz, ensure the extension is loaded.")
    else {
      this.ns = (window as any).PyViz
      this.ns.comm_manager.register_target(this.plot_id, this.comm_id, (msg: any) => {
	for (const view of this.ns.shared_views.get(this.plot_id)) {
	  if (view !== this)
	    view.msg_handler(msg)
	}
	try {
	  this.msg_handler(msg)
	} catch(e) {
	  console.error(e)
	}
      })
      this._client_comm = this.ns.comm_manager.get_client_comm(this.plot_id, this.client_comm_id, (msg: any) => this.on_ack(msg));
      if (this.ns.shared_views == null)
	this.ns.shared_views = new Map()
      if (this.ns.shared_views.has(this.plot_id))
	this.ns.shared_views.get(this.plot_id).push(this)
      else
	this.ns.shared_views.set(this.plot_id, [this])
    }
  }

  protected _document_listener: (event: DocumentChangedEvent) => void = (event) => this._document_changed(event)

  protected _doc_attached(): void {
    super._doc_attached()
    if (this.document != null)
      this.document.on_change(this._document_listener)
  }

  protected _document_changed(event: DocumentChangedEvent): void {
    // Filter out changes to attributes that aren't server-visible
    if (event instanceof ModelChangedEvent && !event.model.properties[event.attr].syncable)
      return

    this._event_buffer.push(event);
    if (!comm_settings.debounce) {
      this.process_events()
    } else if ((!this._blocked || (Date.now() > this._timeout))) {
      setTimeout(() => this.process_events(), this.debounce);
      this._blocked = true;
      this._timeout = Date.now()+this.timeout;
    }
  }

  protected _extract_buffers(value: any, buffers: ArrayBuffer[]): any {
    let extracted: any;
    if (value instanceof Array) {
      extracted = []
      for (const val of value)
	extracted.push(this._extract_buffers(val, buffers))
    } else if (value instanceof Object) {
      extracted = {}
      for (const key in value) {
	if (key === 'buffer' && value[key] instanceof ArrayBuffer) {
	  const id = Object.keys(buffers).length
	  extracted = {id}
	  buffers.push(value[key])
	  break
	}
	extracted[key] = this._extract_buffers(value[key], buffers)
      }
    } else {
      extracted = value
    }
    return extracted
  }

  process_events() {
    if ((this.document == null) || (this._client_comm == null))
      return
    const patch = this.document.create_json_patch(this._event_buffer)
    this._event_buffer = [];
    const message = {...Message.create('PATCH-DOC', {}, patch)}
    const buffers: ArrayBuffer[] = []
    message.content = this._extract_buffers(message.content, buffers)
    this._client_comm.send(message, {}, buffers)
    for (const view of this.ns.shared_views.get(this.plot_id)) {
      if (view !== this && view.document != null)
        view.document.apply_json_patch(patch, [], this.id)
    }
  }

  override disconnect_signals(): void {
    super.disconnect_signals()
    this.ns.shared_views.shared_views.delete(this.plot_id)
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

      if (content.length)
        this._receiver.consume(content)
      else if ((buffers != undefined) && (buffers.length > 0))
        this._receiver.consume(buffers[0].buffer)
      else
	return

      const comm_msg = this._receiver.message
      if ((comm_msg != null) && (Object.keys(comm_msg.content as Patch).length > 0) && this.document != null){
        const patch = comm_msg.content as Patch
        this.document.apply_json_patch(patch, comm_msg.buffers)
      }
    }
  }

  static __module__ = "panel.models.comm_manager"

  static {
    this.prototype.default_view = CommManagerView

    this.define<CommManager.Props>(({Int, String, Nullable}) => ({
      plot_id:        [ Nullable(String),  null ],
      comm_id:        [ Nullable(String),  null ],
      client_comm_id: [ Nullable(String),  null ],
      timeout:        [ Int, 5000 ],
      debounce:       [ Int,   50 ],
    }))
  }
}
