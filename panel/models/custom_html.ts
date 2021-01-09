import * as p from "@bokehjs/core/properties"
import {ModelEvent, JSON} from "@bokehjs/core/bokeh_events"
import {HTMLBox, HTMLBoxView} from "@bokehjs/models/layouts/html_box"

import {CachedVariadicBox, set_size} from "./layout"

class CustomEvent extends ModelEvent {
  event_name: string = "custom"

  constructor(readonly event: any) {
    super()
  }

  protected _to_json(): JSON {
	return {model: this.origin, event: this.event}
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

export class CustomHTMLView extends HTMLBoxView {
  model: CustomHTML
  _prev_sizing_mode: string | null
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
  }

  private _render_html(literal: string, params: any): string {
    return new Function("ns", "with (ns) { return `"+literal+"`; }")(params)
  }

  render(): void {
    super.render()
    this.divEl = document.createElement('div')
    this.divEl.innerHTML = this._render_html(this.model.html, this.model.model)

    set_size(this.divEl, this.model)
    this.el.appendChild(this.divEl)

	const model = this.model.model
	const id = model.id
    for (const name in this.model.events) {
	  const el: any = document.getElementById(`${name}-${id}`)
	  if (el == null) {
		console.warn(`DOM node '${name}-${id}' could not be found.`)
        continue
      }
	  const names = el.id.split('-')
	  const elname = names.slice(0, names.length-1).join('-')
	  for (const event of this.model.events[name]) {
		el.addEventListener(event, (event: any) => {
		  this.model.trigger_event(new CustomEvent(simplify(event)))
		  const attrs = this.model.attrs[elname]
		  if (attrs != null) {
			for (const attr of attrs) {
			  let value = el[attr[0]]
			  if (isNumeric(value))
				value = Number(value)
			  else if (value === 'false' || value === 'true')
				value = value === 'true' ? true : false
			  model[attr[1]] = value 
			}
		  }
		})
	  }
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

export namespace CustomHTML {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
	attrs: p.Property<any>  
    events: p.Property<any>
    html: p.Property<string>
    model: p.Property<any>
  }
}

export interface CustomHTML extends CustomHTML.Attrs {}

export class CustomHTML extends HTMLBox {
  properties: CustomHTML.Props

  constructor(attrs?: Partial<CustomHTML.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.custom_html"

  static init_CustomHTML(): void {
    this.prototype.default_view = CustomHTMLView
    this.define<CustomHTML.Props>({
	  attrs:   [ p.Any, {} ],
      events:  [ p.Any, {}  ],
      html:    [ p.String, "" ],
      model:   [ p.Any,  ]
    })
  }
}
