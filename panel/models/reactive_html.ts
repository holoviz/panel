import {render} from 'preact';
import {html} from 'htm/preact';

import * as p from "@bokehjs/core/properties"
import {ModelEvent, JSON} from "@bokehjs/core/bokeh_events"
import {Markup} from "@bokehjs/models/widgets/markup"
import {build_view} from "@bokehjs/core/build_views"

import {serializeEvent} from "./event-to-object";
import {htmlDecode} from "./html"
import {PanelHTMLBoxView, set_size} from "./layout"

class DOMEvent extends ModelEvent {
  event_name: string = "dom_event"

  constructor(readonly node: string, readonly event: any) {
    super()
  }

  protected _to_json(): JSON {
    return {model: this.origin, node: this.node, event: this.event}
  }
}

function serialize_attrs(attrs: any, model: any): any {
  const serialized: any = {}
  for (const attr in attrs) {
    let value = attrs[attr]
    const property = model.properties[attr]
    if (!property.valid(value)) {
      if (typeof value !== "string") {
        console.warn(`Model property '${attr}' value of ${value} could not be serialized.`)
        continue
      } else if (value === "NaN" || !isNaN(Number(value)))
        value = Number(value)
      else if (value === 'false' || value === 'true')
        value = value === 'true' ? true : false
      }
    serialized[attr] = value
  }
  return serialized
}

export class ReactiveHTMLView extends PanelHTMLBoxView {
  model: ReactiveHTML
  _changing: boolean = false
  _render_node: any = null

  connect_signals(): void {
    super.connect_signals()
    const resize = () => {
      this.render()
      this.root.compute_layout() // XXX: invalidate_layout?
    }

    this.connect(this.model.properties.height.change, resize)
    this.connect(this.model.properties.width.change, resize)
    this.connect(this.model.properties.height_policy.change, resize)
    this.connect(this.model.properties.width_policy.change, resize)
    this.connect(this.model.properties.sizing_mode.change, resize)
    this.connect(this.model.properties.html.change, resize)
    this.connect(this.model.data.change, () => {
      if (!this._changing)
        this._update()
    })
  }

  private _render_html(literal: any): string {
    let htm = literal.replaceAll('${model.', '$-{model.').replaceAll('${', '${data.').replaceAll('$-{model.', '${model.')
    return new Function("model, data, html", "return html`"+htm+"`;")(this.model, this.model.data, html)
  }

  async _render_children(id: string): Promise<void> {
    for (const name in this.model.children) {
      const el: any = document.getElementById(`${name}-${id}`)
      if (el == null) {
        console.warn(`DOM node '${name}-${id}' could not be found. Cannot render children.`)
        continue
      }
      const child_name = this.model.children[name]
      let child_models = this.model.models[child_name]
      for (const cm of child_models) {
        const view = await build_view(cm)
        view.renderTo(el)
      }
    }
  }

  _setup_mutation_observers(id: string): void {
    for (const name in this.model.attrs) {
      const el: any = document.getElementById(`${name}-${id}`)
      if (el == null) {
        console.warn(`DOM node '${name}-${id}' could not be found. Cannot set up MutationObserver.`)
        continue
      }
      const observer = new MutationObserver(() => {
        this._update_model(el, name)
      })
      observer.observe(el, {attributes: true});
    }
  }

  _setup_event_listeners(id: string): void {
    for (const name in this.model.events) {
      const el: any = document.getElementById(`${name}-${id}`)
      if (el == null) {
        console.warn(`DOM node '${name}-${id}' could not be found. Cannot subscribe to DOM events.`)
        continue
      }
      const names = el.id.split('-')
      const elname = names.slice(0, names.length-1).join('-')
      for (const event_name of this.model.events[name]) {
        el.addEventListener(event_name, (event: any) => {
          this.model.trigger_event(new DOMEvent(elname, serializeEvent(event)))
          if (name in this.model.attrs)
            this._update_model(el, name)
        })
      }
    }
  }

  _update(): void {
    const decoded = htmlDecode(this.model.html)
    const html = decoded || this.model.html
    const rendered = this._render_html(html)
    render(rendered, this.el, this._render_node)
    this._render_node = this.el.children[0]
    set_size(this._render_node, this.model)
  }

  async render(): Promise<void> {
    super.render()
    this._update()

    const id = this.model.data.id
    await this._render_children(id)
    this._setup_mutation_observers(id)
    this._setup_event_listeners(id)
  }

  private _update_model(el: any, name: string): void {
    const data_model = this.model.data
    const attrs: any = {}
    for (const attr of this.model.attrs[name])
      attrs[attr[1]] = el[attr[0]]
    this._changing = true
    data_model.setv(serialize_attrs(attrs, data_model))
    this._changing = false
  }
}

export namespace ReactiveHTML {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Markup.Props & {
    attrs: p.Property<any>
    children: p.Property<any>
    data: p.Property<any>
    events: p.Property<any>
    html: p.Property<string>
    models: p.Property<any>
  }
}

export interface ReactiveHTML extends ReactiveHTML.Attrs {}

export class ReactiveHTML extends Markup {
  properties: ReactiveHTML.Props

  constructor(attrs?: Partial<ReactiveHTML.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.reactive_html"

  static init_ReactiveHTML(): void {
    this.prototype.default_view = ReactiveHTMLView
    this.define<ReactiveHTML.Props>({
      attrs:    [ p.Any, {} ],
      children: [ p.Any, {} ],
      data:    [ p.Any,  ],
      events:   [ p.Any, {}  ],
      html:     [ p.String, "" ],
      models:   [ p.Any, {} ]
    })
  }
}
