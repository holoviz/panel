import type * as p from "@bokehjs/core/properties"
import {View} from "@bokehjs/core/view"
import {Model} from "@bokehjs/model"

export class LocationView extends View {
  declare model: Location

  _hash_listener: any
  private _idle_ready = false
  private _pending_url: string | null = null
  private _idle_connected = false

  override initialize(): void {
    super.initialize()

    this.model.pathname = window.location.pathname
    this.model.search = window.location.search
    this.model.hash = window.location.hash

    // Readonly parameters on python side
    this.model.href = window.location.href
    this.model.hostname = window.location.hostname
    this.model.protocol = window.location.protocol
    this.model.port = window.location.port

    this._hash_listener = () => {
      this.model.hash = window.location.hash
    }
    window.addEventListener("hashchange", this._hash_listener)

    this._has_finished = true
    this.notify_finished()
  }

  override connect_signals(): void {
    super.connect_signals()

    const {pathname, search, hash, reload} = this.model.properties
    this.on_change(pathname, () => this.update("pathname"))
    this.on_change(search, () => this.update("search"))
    this.on_change(hash, () => this.update("hash"))
    this.on_change(reload, () => this.update("reload"))
  }

  override remove(): void {
    super.remove()
    window.removeEventListener("hashchange", this._hash_listener)
  }

  private _ensure_idle_gate(): void {
    if (this._idle_connected) {
      return
    }
    this._idle_connected = true

    const doc = this.model.document as any
    if (doc.is_idle) {
      this._idle_ready = true
      return
    }

    doc.idle.connect(() => {
      this._idle_ready = true
      if (this._pending_url != null) {
        const url = this._pending_url
        this._pending_url = null
        window.history.pushState({}, "", url)
        this.model.href = window.location.href
      }
    })
  }

  private _set_url_gated(url: string): void {
    this._ensure_idle_gate()
    if (this._idle_ready) {
      window.history.pushState({}, "", url)
      this.model.href = window.location.href
    } else {
      this._pending_url = url
    }
  }

  update(change: string): void {
    const url = `${this.model.pathname}${this.model.search}${this.model.hash}`

    if (change === "reload") {
      window.history.pushState({}, "", url)
      this.model.href = window.location.href
      window.location.reload()
      return
    }

    if (!this.model.reload) {
      this._set_url_gated(url)
      return
    }

    if (change === "hash") {
      window.location.hash = this.model.hash
      return
    }

    window.location.href = url
  }
}

export namespace Location {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Model.Props & {
    href: p.Property<string>
    hostname: p.Property<string>
    pathname: p.Property<string>
    protocol: p.Property<string>
    port: p.Property<string>
    search: p.Property<string>
    hash: p.Property<string>
    reload: p.Property<boolean>
  }
}

export interface Location extends Location.Attrs { }

export class Location extends Model {
  declare properties: Location.Props

  static override __module__ = "panel.models.location"

  constructor(attrs?: Partial<Location.Attrs>) {
    super(attrs)
  }

  static {
    this.prototype.default_view = LocationView

    this.define<Location.Props>(({Bool, Str}) => ({
      href:     [ Str,     "" ],
      hostname: [ Str,     "" ],
      pathname: [ Str,     "" ],
      protocol: [ Str,     "" ],
      port:     [ Str,     "" ],
      search:   [ Str,     "" ],
      hash:     [ Str,     "" ],
      reload:   [ Bool, false ],
    }))
  }
}
