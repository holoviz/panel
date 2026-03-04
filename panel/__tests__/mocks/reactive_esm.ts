// Stub for ./reactive_esm — provides minimal class shells
// so anywidget_component.ts can be imported in Vitest tests.

export class DataEvent {
  declare event_name: string
  data: unknown
  origin: any
  constructor(data: unknown) { this.data = data }
  protected get event_values(): any { return {model: this.origin, data: this.data} }
}
// Set event_name on the prototype (esbuild doesn't allow `static prototype`)
DataEvent.prototype.event_name = "data_event"

export class ReactiveESM {
  data: any = {attributes: {}}
  attributes: Record<string, any> = {}
  _pending_msg_handlers: any[] | null = null
  _anywidget_view: any = null
  esm: string = ""
  bundle: any = null
  compile_error: any = null

  // Signal system stubs used by the adapter's on/off
  _watchers: Map<string, Set<Function>> = new Map()

  watch(_view: any, prop: string, cb: Function): void {
    let cbs = this._watchers.get(prop)
    if (!cbs) {
      cbs = new Set()
      this._watchers.set(prop, cbs)
    }
    cbs.add(cb)
  }

  unwatch(_view: any, prop: string, cb: Function): void {
    const cbs = this._watchers.get(prop)
    if (cbs) {
      cbs.delete(cb)
    }
  }

  trigger_event(_event: any): void {}
  setv(_attrs: Record<string, any>): void {}

  compile(): string | null { return this.esm }
  protected get _render_cache_key(): string { return "reactive_esm" }
  protected _render_code(): string { return "" }
  protected _run_initializer(_init: Function): void {}

  static __module__: string = "panel.models.esm"
}

export class ReactiveESMView {
  model: any
  container: HTMLElement = document.createElement("div")
  el: HTMLElement = document.createElement("div")
  _rendered: boolean = false
  _event_handlers: Function[] = []

  initialize(): void {}
  connect_signals(): void {}
  remove(): void {}
  after_rendered(): void { this._rendered = true }
  render_children(): void {}

  on_event(handler: Function): void {
    this._event_handlers.push(handler)
  }

  remove_on_event(handler: Function): void {
    this._event_handlers = this._event_handlers.filter(h => h !== handler)
  }

  get_child_view(_model: any): any { return null }
}
