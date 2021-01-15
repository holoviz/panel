import {render} from 'preact';
import {useCallback} from 'preact/hooks';
import {html} from 'htm/preact';

import * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import {build_view} from "@bokehjs/core/build_views"

import {serializeEvent} from "./event-to-object";
import {DOMEvent, htmlDecode, runScripts} from "./html"
import {PanelHTMLBoxView, set_size} from "./layout"


function serialize_attrs(attrs: any): any {
  const serialized: any = {}
  for (const attr in attrs) {
    let value = attrs[attr]
    if (typeof value !== "string")
      value = value
    else if (value !== "" && (value === "NaN" || !isNaN(Number(value))))
      value = Number(value)
    else if (value === 'false' || value === 'true')
      value = value === 'true' ? true : false
    serialized[attr] = value
  }
  return serialized
}

export class ReactiveHTMLView extends PanelHTMLBoxView {
  model: ReactiveHTML
  _changing: boolean = false
  _render_el: any = null
  _script_els: any = {}

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
    this.connect(this.model.properties.scripts.change, () => this._update(null, false, true))
    for (const prop in this.model.data.properties) {
      this.connect(this.model.data.properties[prop].change, () => {
        if (!this._changing)
          this._update(prop)
      })
    }
  }

  _send_event(elname: string, attr: string, event: any) {
    let serialized = serializeEvent(event)
    serialized.type = attr
    this.model.trigger_event(new DOMEvent(elname, serialized))
  }

  private _render_html(literal: any): string {
    let htm = literal
    let callbacks = ''
    const methods: string[] = []
    for (const elname in this.model.callbacks) {
      for (const callback of this.model.callbacks[elname]) {
        const [cb, method] = callback;
        if (methods.indexOf(method) > -1)
          continue
        methods.push(method)
        callbacks = callbacks + `
        const ${method} = (event) => {
          view._send_event("${elname}", "${cb}", event)
        }
        `
        htm = htm.replace('${'+method, '$--{'+method)
      }
    }
    htm = htm.replaceAll('${model.', '$-{model.').replaceAll('${', '${data.').replaceAll('$-{model.', '${model.').replaceAll('$--{', '${')
    return new Function("view, model, data, html, useCallback", callbacks+"return html`"+htm+"`;")(this, this.model, this.model.data, html, useCallback)
  }

  private _render_script(literal: any): string {
    let js = literal.replaceAll('${model.', '$-{model.').replaceAll('${', '${data.').replaceAll('$-{model.', '${model.')
    return new Function("model, data, html", "return `<script>"+js+"</script>`;")(this.model, this.model.data, html)
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

  _update(property: string | null = null, js: boolean = true, html: boolean = true): void {
    if (html) {
      const decoded = htmlDecode(this.model.html) || this.model.html
      if (property == null || (decoded.indexOf(`\${${property}}`) > -1)) {
        const rendered = this._render_html(decoded)
        render(rendered, this.el)
        this._render_el = this.el.children[0]
        set_size(this._render_el, this.model)
      }
    }

    if (js) {
      for (const script_obj of this.model.scripts) {
        const name = script_obj[0]
        if (!(name in this._script_els)) {
          const script_el = document.createElement('div')
          this._script_els[name] = script_el
          this.el.appendChild(script_el)
        }
      }

      for (const script_obj of this.model.scripts) {
        const [name, script] = script_obj
        const decoded_script = htmlDecode(script) || script
        const rendered_script = this._render_script(decoded_script)

        const script_el = this._script_els[name]
        if (script_el.innerHTML !== rendered_script || name === property) {
          script_el.innerHTML = rendered_script
          runScripts(script_el)
        }
      }
    }
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
    const attrs: any = {}
    for (const attr of this.model.attrs[name])
      attrs[attr[1]] = el[attr[0]]
    this._changing = true
    this.model.data.setv(serialize_attrs(attrs))
    this._changing = false
  }
}

export namespace ReactiveHTML {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Markup.Props & {
    attrs: p.Property<any>
    callbacks: p.Property<any>
    children: p.Property<any>
    data: p.Property<any>
    events: p.Property<any>
    html: p.Property<string>
    models: p.Property<any>
    scripts: p.Property<string[][]>
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
      callbacks: [ p.Any, {} ],
      children: [ p.Any, {} ],
      data:    [ p.Any,  ],
      events:   [ p.Any, {}  ],
      html:     [ p.String, "" ],
      scripts:  [ p.Array, [] ],
      models:   [ p.Any, {} ]
    })
  }
}
