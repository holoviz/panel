import {render} from 'preact';
import {html} from 'htm/preact';

import * as p from "@bokehjs/core/properties"
import {ModelEvent, JSON} from "@bokehjs/core/bokeh_events"
import {build_view} from "@bokehjs/core/build_views"
import {HTMLBox, HTMLBoxView} from "@bokehjs/models/layouts/html_box"

import {htmlDecode} from "./html"
import {CachedVariadicBox, set_size} from "./layout"

class DOMEvent extends ModelEvent {
  event_name: string = "dom_event"

  constructor(readonly node: string, readonly event: any) {
    super()
  }

  protected _to_json(): JSON {
    return {model: this.origin, node: this.node, event: this.event}
  }
}

function simplify(event: any): any {
  const copy: any = {}
  for (const property in event) {
    const ptype = typeof event[property] 
    if(ptype === "function" || ptype === 'object')
      continue
    copy[property] = event[property];    
  }
  return copy
}

function isNumeric(str: any): any {
  if (typeof str != "string")
    return false  
  return !isNaN(str) && !isNaN(parseFloat(str))
}

export class ReactiveHTMLView extends HTMLBoxView {
  model: ReactiveHTML
  _prev_sizing_mode: string | null
  _changing: boolean = false
  protected divEl: HTMLElement

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
    this.connect(this.model.properties.html.change, () => this.render())
	this.connect(this.model.model.change, () => {
	  if (!this._changing)
	    this._update()
	})
  }

  private _render_html(literal: any, params: any): string {
	const htm = literal.replaceAll('${', '${params.')
	return new Function("params, html", "return html`"+htm+"`;")(params, html)
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
          this.model.trigger_event(new DOMEvent(elname, simplify(event)))
		  if (name in this.model.attrs)
		    this._update_model(el, name)
        })
      }
    }
  }

  _update(): void {
	const decoded = htmlDecode(this.model.html)
    const html = decoded || this.model.html
	const rendered = this._render_html(html, this.model.model)
	render(rendered, this.divEl)
  }

  async render(): Promise<void> {
    super.render()
    this.divEl = document.createElement('div')
	this._update()

    set_size(this.divEl, this.model)
    this.el.appendChild(this.divEl)

    const id = this.model.model.id
	await this._render_children(id)
	this._setup_mutation_observers(id)
	this._setup_event_listeners(id)
  }

  private _update_model(el: any, name: string): void {
	for (const attr of this.model.attrs[name]) {
	  let value = el[attr[0]]
      if (isNumeric(value))
        value = Number(value)
      else if (value === 'false' || value === 'true')
        value = value === 'true' ? true : false
      this._changing = true
      this.model.model[attr[1]] = value
      this._changing = false
	}
  }

  _update_layout(): void {
    let changed = ((this._prev_sizing_mode !== undefined) &&
                   (this._prev_sizing_mode !== this.model.sizing_mode))
    this._prev_sizing_mode = this.model.sizing_mode;
    this.layout = new CachedVariadicBox(this.el, this.model.sizing_mode, changed)
    this.layout.set_sizing(this.box_sizing())
  }
}

export namespace ReactiveHTML {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    attrs: p.Property<any>
    children: p.Property<any>
    events: p.Property<any>
    html: p.Property<string>
    model: p.Property<any>
	models: p.Property<any>
  }
}

export interface ReactiveHTML extends ReactiveHTML.Attrs {}

export class ReactiveHTML extends HTMLBox {
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
      events:   [ p.Any, {}  ],
      html:     [ p.String, "" ],
      model:    [ p.Any,  ],
	  models:   [ p.Any, {} ]
    })
  }
}
