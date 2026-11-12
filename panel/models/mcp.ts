import type * as p from "@bokehjs/core/properties"
import type {Attrs} from "@bokehjs/core/types"
import {ModelEvent, server_event} from "@bokehjs/core/bokeh_events"
import {View} from "@bokehjs/core/view"
import {Model} from "@bokehjs/model"

type Bridge = {
  state: string
  hostContext: Record<string, unknown>
  hostCapabilities: Record<string, unknown>
  hostInfo: Record<string, unknown> | null
  protocolVersion: string | null
  ready: Promise<Record<string, unknown>>
  request: (method: string, params?: unknown) => Promise<unknown>
  notify: (method: string, params?: unknown) => void
  attach: (
    onNotification: (method: string, params: unknown) => void,
    onRequest: (method: string, params: unknown) => unknown,
  ) => {
    hostContext: Record<string, unknown>
    hostCapabilities: Record<string, unknown>
    hostInfo: Record<string, unknown> | null
    protocolVersion: string | null
  }
  detach: () => void
}

// Matches the Python side's DEFAULT_TIMEOUT: tool calls served by Python may
// legitimately take a while, but a host must not wait on a dead session forever.
const REQUEST_TIMEOUT = 60_000

export class MCPMessageEvent extends ModelEvent {
  constructor(
    readonly method: string,
    readonly params: unknown,
    readonly request_id: string | number | null,
  ) {
    super()
  }

  protected override get event_values(): Attrs {
    return {
      model: this.origin,
      method: this.method,
      params: this.params,
      request_id: this.request_id,
    }
  }

  static {
    this.prototype.event_name = "mcp_message"
  }
}

export class MCPReplyEvent extends ModelEvent {
  constructor(
    readonly msg_id: string,
    readonly result: unknown,
    readonly error: unknown,
  ) {
    super()
  }

  protected override get event_values(): Attrs {
    return {
      model: this.origin,
      msg_id: this.msg_id,
      result: this.result,
      error: this.error,
    }
  }

  static {
    this.prototype.event_name = "mcp_reply"
  }
}

@server_event("mcp_send")
export class MCPSendEvent extends ModelEvent {
  constructor(
    readonly kind: string,
    readonly method: string,
    readonly params: unknown,
    readonly msg_id: string | null,
  ) {
    super()
  }

  static override from_values(values: object) {
    const {model, kind, method, params, msg_id} = values as {
      model: MCPApp
      kind: string
      method: string
      params: unknown
      msg_id: string | null
    }
    const event = new MCPSendEvent(kind, method, params, msg_id)
    event.origin = model
    return event
  }

  protected override get event_values(): Attrs {
    return {
      model: this.origin,
      kind: this.kind,
      method: this.method,
      params: this.params,
      msg_id: this.msg_id,
    }
  }

  static {
    this.prototype.event_name = "mcp_send"
  }
}

export class MCPAppView extends View {
  declare model: MCPApp

  private _bridge: Bridge | null = null
  private _pending_requests: Map<string, (result: {value?: unknown, error?: unknown}) => void> = new Map()
  private _next_request_id = 0

  override initialize(): void {
    super.initialize()

    this._bridge = (window as any).__panelMCP__ ?? null

    this._has_finished = true
    this.notify_finished()

    if (this._bridge == null) {
      // Not embedded in an MCP host, e.g. the MCP view opened top-level: stay
      // inert, leaving `pn.state.mcp.connected` False on the Python side.
      this._signal_rendered()
      return
    }

    // The bridge completed (or is completing) the handshake on its own. Attach
    // once it resolves so buffered notifications replay into the session.
    this._bridge.ready.then(
      () => this._attach(),
      () => this._signal_rendered(),
    )
  }

  private _signal_rendered(): void {
    // Tells the MCP template's overlay that the document arrived and the app is
    // live, whether or not the handshake succeeded.
    window.dispatchEvent(new Event("pn-mcp-rendered"))
  }

  private _attach(): void {
    const bridge = this._bridge
    if (bridge == null) {
      return
    }

    // Sync the host context before replaying buffered notifications so Python
    // sees a connected session by the time tool input arrives.
    this.model.setv({
      host_context: {...bridge.hostContext},
      host_capabilities: bridge.hostCapabilities,
      host_info: bridge.hostInfo,
      protocol_version: bridge.protocolVersion,
    })
    this.model.connected = true

    bridge.attach(
      (method, params) => this._on_notification(method, params),
      (method, params) => this._on_request(method, params),
    )

    this._signal_rendered()
  }

  override connect_signals(): void {
    super.connect_signals()

    this.model.on_event(MCPSendEvent, (event: MCPSendEvent) => this._send(event))
  }

  override remove(): void {
    this._bridge?.detach()
    super.remove()
  }

  private _on_notification(method: string, params: unknown): void {
    if (method === "ui/notifications/host-context-changed") {
      // The bridge already merged the patch; mirror the merged state so Python
      // sees whole context rather than a partial.
      this.model.host_context = {...this._bridge!.hostContext} as any
    }
    this.model.trigger_event(new MCPMessageEvent(method, params, null))
  }

  private _on_request(method: string, params: unknown): unknown {
    // Requests need a Python round-trip, so hand back a promise the bridge
    // resolves once Python replies with a matching mcp_send response.
    const request_id = `${method}-${this._next_request_id++}`
    const promise = new Promise<unknown>((resolve, reject) => {
      const timer = setTimeout(() => {
        if (this._pending_requests.delete(request_id)) {
          reject(new Error(`Panel session did not answer ${method} in time`))
        }
      }, REQUEST_TIMEOUT)
      this._pending_requests.set(request_id, ({value, error}) => {
        clearTimeout(timer)
        if (error === undefined) {
          resolve(value)
        } else {
          reject(error)
        }
      })
    })
    this.model.trigger_event(new MCPMessageEvent(method, params, request_id))
    return promise
  }

  private _send(event: MCPSendEvent): void {
    const bridge = this._bridge
    if (bridge == null) {
      return
    }
    const {kind, method, params, msg_id} = event

    if (kind === "notify") {
      bridge.notify(method, params)
      return
    }

    if (kind === "respond") {
      // A reply to a host request we forwarded to Python; msg_id carries the
      // request_id originally sent out on the MCPMessageEvent.
      if (msg_id != null) {
        const resolve = this._pending_requests.get(msg_id)
        if (resolve != null) {
          this._pending_requests.delete(msg_id)
          resolve({value: params})
        }
      }
      return
    }

    if (kind === "request") {
      bridge.request(method, params).then(
        (result) => {
          if (msg_id != null) {
            this.model.trigger_event(new MCPReplyEvent(msg_id, result, null))
          }
        },
        (error) => {
          if (msg_id != null) {
            const err = error instanceof Error
              ? {code: -32000, message: error.message}
              : error
            this.model.trigger_event(new MCPReplyEvent(msg_id, null, err))
          }
        },
      )
    }
  }
}

export namespace MCPApp {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Model.Props & {
    connected: p.Property<boolean>
    host_context: p.Property<Record<string, unknown>>
    host_capabilities: p.Property<Record<string, unknown>>
    host_info: p.Property<Record<string, unknown> | null>
    protocol_version: p.Property<string | null>
    tools: p.Property<Record<string, unknown>[]>
  }
}

export interface MCPApp extends MCPApp.Attrs { }

export class MCPApp extends Model {
  declare properties: MCPApp.Props

  static override __module__ = "panel.models.mcp"

  constructor(attrs?: Partial<MCPApp.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = MCPAppView

    this.define<MCPApp.Props>(({Any, Bool, List, Nullable, Str}) => ({
      connected:         [ Bool, false ],
      host_context:      [ Any, {} ],
      host_capabilities: [ Any, {} ],
      host_info:         [ Nullable(Any), null ],
      protocol_version:  [ Nullable(Str), null ],
      tools:             [ List(Any), [] ],
    }))
  }
}
