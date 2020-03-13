import * as p from "@bokehjs/core/properties"
import {View} from "@bokehjs/core/view"
import {Model} from "@bokehjs/model"

export class LocationView extends View {
  model: Location

  initialize(): void {
    super.initialize();

    this.model.pathname = window.location.pathname;
    this.model.search = window.location.search;
    this.model.hash_ = window.location.hash;

    // Readonly parameters on python side
    this.model.href = window.location.href;
    this.model.hostname = window.location.hostname;
    this.model.protocol = window.location.protocol;
    this.model.port = window.location.port;
  }

  connect_signals(): void {
    super.connect_signals();

    this.connect(this.model.properties.pathname.change, () => this.update('pathname'));
    this.connect(this.model.properties.search.change, () => this.update('search'));
    this.connect(this.model.properties.hash_.change, () => this.update('hash'));
  }

  update(change: string): void {
    if (!this.model.reload) {
      window.history.pushState(
        {},
        '',
        `${this.model.pathname}${this.model.search}${this.model.hash_}`
      );
      this.model.href = window.location.href;
    } else {
      if (change == 'pathname')
        window.location.pathname = (this.model.pathname as string);
      if (change == 'search')
	    window.location.search = (this.model.search as string);
      if (change == 'hash')
        window.location.hash = (this.model.hash_ as string);
    }
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
    hash_: p.Property<string>
    reload: p.Property<boolean>
  }
}

export interface Location extends Location.Attrs { }

export class Location extends Model {
  properties: Location.Props

  static __module__ = "panel.models.location"

  constructor(attrs?: Partial<Location.Attrs>) {
    super(attrs)
  }

  static init_Location(): void {
    this.prototype.default_view = LocationView;

    this.define<Location.Props>({
      href: [p.String, window.location.href],
      hostname: [p.String, window.location.hostname],
      pathname: [p.String, window.location.pathname],
      protocol: [p.String, window.location.protocol],
      port: [p.String, window.location.port],
      search: [p.String, window.location.search],
      hash_: [p.String, window.location.hash],
      reload: [p.Boolean, true],
    })
  }
}
