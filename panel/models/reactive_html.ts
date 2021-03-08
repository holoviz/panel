import {render} from 'preact';
import {useCallback} from 'preact/hooks';
import {html} from 'htm/preact';

import {build_views} from "@bokehjs/core/build_views"
import * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import {LayoutDOM} from "@bokehjs/models/layouts/layout_dom"
import {empty, classes} from "@bokehjs/core/dom"
import {color2css} from "@bokehjs/core/util/color"

import {serializeEvent} from "./event-to-object";
import {DOMEvent, htmlDecode} from "./html"
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

function escapeRegex(string: string) {
    return string.replace(/[-\/\\^$*+?.()|[\]]/g, '\\$&');
}

function extractToken(template: string, str: string, tokens: string[]) {
  const tokenMapping: any = {}
  for (const match of tokens)
    tokenMapping[`{${match}}`] = "(.*)"

  const tokenList = []
  let regexpTemplate = escapeRegex(template);

  // Find the order of the tokens
  let i, tokenIndex, tokenEntry;
  for (const m in tokenMapping) {
    tokenIndex = template.indexOf(m);

    // Token found
    if (tokenIndex > -1) {
      regexpTemplate = regexpTemplate.replace(m, '(' + tokenMapping[m] + ')');
      tokenEntry = {
	index: tokenIndex,
	token: m
      };

      for (i = 0; i < tokenList.length && tokenList[i].index < tokenIndex; i++);

      // Insert it at index i
      if (i < tokenList.length)
	tokenList.splice(i, 0, tokenEntry)
      else
	tokenList.push(tokenEntry)
    }
  }

  regexpTemplate = regexpTemplate.replace(/\{[^{}]+\}/g, '.*');

  var match = new RegExp(regexpTemplate).exec(str)
  let result: any = null;

  if (match) {
    result = {};
    // Find your token entry
    for (i = 0; i < tokenList.length; i++)
      result[tokenList[i].token.slice(1, -1)] = match[i + 1]
  }

  return result;
}


export class ReactiveHTMLView extends PanelHTMLBoxView {
  model: ReactiveHTML
  html: string
  _changing: boolean = false
  _event_listeners: any = {}
  _mutation_observers: MutationObserver[] = []

  initialize(): void {
    super.initialize()
    this.html = htmlDecode(this.model.html) || this.model.html
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.children.change, () => this.rebuild())
    for (const prop in this.model.data.properties) {
      this.connect(this.model.data.properties[prop].change, () => {
        if (!this._changing) {
          this._update(prop)
	  this.invalidate_layout()
	}
      })
    }
    this.connect(this.model.properties.events.change, () => {
      this._remove_event_listeners()
      this._setup_event_listeners()
    })
    this.connect_scripts()
  }

  connect_scripts(): void {
    const id = this.model.data.id
    for (const elname in this.model.scripts) {
      const el_scripts = this.model.scripts[elname]
      for (const prop in el_scripts) {
        const script = el_scripts[prop]
        const decoded_script = htmlDecode(script) || script
	const script_fn = this._render_script(decoded_script, elname, id)
	this.connect(this.model.data.properties[prop].change, () => {
          if (!this._changing)
            script_fn(this.model, this.model.data)
	})
      }
    }
  }

  disconnect_signals(): void {
    super.disconnect_signals()
    this._remove_event_listeners()
    this._remove_mutation_observers()
  }

  get child_models(): LayoutDOM[] {
    const models = []
    for (const parent in this.model.children) {
      for (const model of this.model.children[parent])
	models.push(model)
    }
    return models
  }

  async build_child_views(): Promise<void> {
    await build_views(this._child_views, this.child_models, {parent: (null as any)})
  }

  update_layout(): void {
    this._update_layout()
  }

  render(): void {
    empty(this.el)

    const {background} = this.model
    this.el.style.backgroundColor = background != null ? color2css(background) : ""
    classes(this.el).clear().add(...this.css_classes())

    this._update()
    this._render_children()
    this._setup_mutation_observers()
    this._setup_event_listeners()
  }

  private _send_event(elname: string, attr: string, event: any) {
    let serialized = serializeEvent(event)
    serialized.type = attr
    this.model.trigger_event(new DOMEvent(elname, serialized))
  }

  private _render_children(): void {
    const id = this.model.data.id
    for (const name in this.model.children) {
      const el: any = document.getElementById(`${name}-${id}`)
      if (el == null) {
        console.warn(`DOM node '${name}-${id}' could not be found. Cannot render children.`)
        continue
      }
      for (const cm of this.model.children[name]) {
        const view: any = this._child_views.get(cm)
	view.renderTo(el)
      }
    }
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
    htm = (
      htm
	.replaceAll('${model.', '$-{model.')
	.replaceAll('${', '${data.')
	.replaceAll('$-{model.', '${model.')
	.replaceAll('$--{', '${')
    )
    return new Function("view, model, data, html, useCallback", callbacks+"return html`"+htm+"`;")(
      this, this.model, this.model.data, html, useCallback
    )
  }

  private _render_script(literal: any, elname: string, id: string) {
    const script = `
      const el = document.getElementById('${elname}-${id}')
      if (el == null) {
        console.warn("DOM node '${elname}-${id}' could not be found. Cannot execute callback.")
        return
      }
      ${literal}
    `
    return new Function("model, data", script)
  }
  private _remove_mutation_observers(): void {
    for (const observer of this._mutation_observers)
      observer.disconnect()
    this._mutation_observers = []
  }

  private _setup_mutation_observers(): void {
    const id = this.model.data.id
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
      this._mutation_observers.push(observer)
    }
  }

  private _remove_event_listeners(): void {
    const id = this.model.data.id
    for (const node in this._event_listeners) {
      const el: any = document.getElementById(`${node}-${id}`)
      if (el == null) {
        console.warn(`DOM node '${node}-${id}' could not be found. Cannot subscribe to DOM events.`)
        continue
      }
      for (const event_name in this._event_listeners[node]) {
	const event_callback = this._event_listeners[node][event_name]
	el.removeEventListener(event_name, event_callback)
      }
    }
    this._event_listeners = {}
  }

  private _setup_event_listeners(): void {
    const id = this.model.data.id
    for (const node in this.model.events) {
      const el: any = document.getElementById(`${node}-${id}`)
      if (el == null) {
        console.warn(`DOM node '${node}-${id}' could not be found. Cannot subscribe to DOM events.`)
        continue
      }
      for (const event_name of this.model.events[node]) {
	const event_callback = (event: any) => {
	  this._send_event(node, event_name, event)
          if (node in this.model.attrs)
            this._update_model(el, node)
        }
	el.addEventListener(event_name, event_callback)
	if (!(node in this._event_listeners))
	  this._event_listeners[node] = {}
	this._event_listeners[node][event_name] = event_callback
      }
    }
  }

  private _update(property: string | null = null): void {
    if (property == null || (this.html.indexOf(`\${${property}}`) > -1)) {
      const rendered = this._render_html(this.html)
      render(rendered, this.el)
      if (this.el.children.length)
	set_size((this.el.children[0] as any), this.model)
    }
  }

  private _update_model(el: any, name: string): void {
    const attrs: any = {}
    for (const attr_info of this.model.attrs[name]) {
      const [attr, tokens, template] = attr_info
      let value = el[attr]
      if (tokens.length === 1 && (`{${tokens[0]}}` === template))
        attrs[tokens[0]] = value
      else if (typeof value === 'string') {
	value = extractToken(template, value, tokens)
	if (value == null)
	  console.warn(`Could not resolve parameters in ${name} element ${attr} attribute value ${value}.`)
	else {
	  for (const param in value) {
	    if (value[param] === undefined)
	      console.warn(`Could not resolve ${param} in ${name} element ${attr} attribute value ${value}.`)
	    else
	      attrs[param] = value[param]
	  }
	}
      }
    }
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
    scripts: p.Property<any>
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
      scripts:  [ p.Any, {} ],
    })
  }
}
