import {render} from 'preact';
import {useCallback} from 'preact/hooks';
import {html} from 'htm/preact';

import {build_views} from "@bokehjs/core/build_views"
import {isArray, isNumber} from "@bokehjs/core/util/types"
import * as p from "@bokehjs/core/properties"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import {LayoutDOM} from "@bokehjs/models/layouts/layout_dom"
import {empty, classes} from "@bokehjs/core/dom"
import {color2css} from "@bokehjs/core/util/color"

import {dict_to_records} from "./data"
import {serializeEvent} from "./event-to-object"
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
  let regexpTemplate = "^" + escapeRegex(template) + "$";

  // Find the order of the tokens
  let i, tokenIndex, tokenEntry;
  for (const m in tokenMapping) {
    tokenIndex = template.indexOf(m);

    // Token found
    if (tokenIndex > -1) {
      regexpTemplate = regexpTemplate.replace(m, tokenMapping[m]);
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
  _parent: any = null
  _changing: boolean = false
  _event_listeners: any = {}
  _mutation_observers: MutationObserver[] = []
  _script_fns: any = {}
  _state: any = {}

  initialize(): void {
    super.initialize()
    this.html = htmlDecode(this.model.html) || this.model.html
  }

  _recursive_connect(model: any, update_children: boolean, path: string): void {
    for (const prop in model.properties) {
      let subpath: string
      if (path.length)
        subpath = `${path}.${prop}`
      else
        subpath = prop
      const obj = model[prop]
      if (obj == null)
        continue
      if (obj.properties != null)
        this._recursive_connect(obj, true, subpath)
      this.connect(model.properties[prop].change, () => {
        if (update_children) {
          for (const node in this.model.children) {
            if (this.model.children[node] == prop) {
              let children = model[prop]
              if (!isArray(children))
                children = [children]
              this._render_node(node, children)
              this.invalidate_layout()
              return
            }
          }
        }
        if (!this._changing) {
          this._update(subpath)
          this.invalidate_layout()
        }
      })
    }
  }

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.children.change, async () => {
      this.html = htmlDecode(this.model.html) || this.model.html
      await this.rebuild()
      this.invalidate_layout()
    })
    this._recursive_connect(this.model.data, true, '')
    this.connect(this.model.properties.events.change, () => {
      this._remove_event_listeners()
      this._setup_event_listeners()
    })
    this.connect_scripts()
  }

  connect_scripts(): void {
    const id = this.model.data.id
    for (let prop in this.model.scripts) {
      const scripts = this.model.scripts[prop]
      let data_model = this.model.data
      let attr: string
      if (prop.indexOf('.') >= 0) {
        const path = prop.split('.')
        attr = path[path.length-1]
        for (const p of path.slice(0, -1))
          data_model = data_model[p]
      } else {
        attr = prop
      }
      for (const script of scripts) {
        const decoded_script = htmlDecode(script) || script
        const script_fn = this._render_script(decoded_script, id)
        this._script_fns[prop] = script_fn
        const property = data_model.properties[attr]
        if (property == null)
          continue
        this.connect(property.change, () => {
          if (!this._changing)
            this.run_script(prop)
        })
      }
    }
  }

  run_script(property: string, silent: boolean=false): void {
    const script_fn = this._script_fns[property]
    if (script_fn === undefined) {
      if (!silent)
        console.log(`Script '${property}' could not be found.`)
      return
    }
    const this_obj: any = {
      get_records: (property: string, index: boolean) => this.get_records(property, index)
    }
    for (const name in this._script_fns)
      this_obj[name] = () => this.run_script(name)
    return script_fn(
      this.model,
      this.model.data,
      this._state,
      this,
      (s: any) => this.run_script(s),
      this_obj
    )
  }

  get_records(property: string, index: boolean=true): any[] {
    return dict_to_records(this.model.data[property], index)
  }

  disconnect_signals(): void {
    super.disconnect_signals()
    this._remove_event_listeners()
    this._remove_mutation_observers()
    this.run_script('remove', true)
  }

  get child_models(): LayoutDOM[] {
    const models = []
    for (const parent in this.model.children) {
      for (const model of this.model.children[parent])
        if (typeof model !== 'string')
          models.push(model)
    }
    return models
  }

  async build_child_views(): Promise<void> {
    await build_views(this._child_views, this.child_models, {parent: (null as any)})
  }

  compute_layout(): void {
    if (this.root != this)
      super.compute_layout()
    else {
      this.update_position()
      this.after_layout()
      this.notify_finished()
    }
  }

  after_layout(): void {
    for (const child_view of this.child_views)
      child_view.after_layout()

    this.run_script('after_layout', true)
    this._has_finished = true
  }

  update_layout(): void {
    for (const child_view of this.child_views) {
      this._align_view(child_view)
      child_view.compute_viewport()
      child_view.update_layout()
      child_view.compute_layout()
    }
    if (this.root != this)
      this._update_layout()
  }

  private _align_view(view: any): void {
    const {align} = view.model
    let halign, valign: string
    if (isArray(align))
      [halign, valign] = (align as any)
    else
      halign = valign = align
    if (halign === 'center') {
      view.el.style.marginLeft = 'auto';
      view.el.style.marginRight = 'auto';
    } else if (halign === 'end')
      view.el.style.marginLeft = 'auto';
    if (valign === 'center') {
      view.el.style.marginTop = 'auto';
      view.el.style.marginBottom = 'auto';
    } else if (valign === 'end')
      view.el.style.marginTop = 'auto';
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
    this.run_script('render', true)
  }

  private _send_event(elname: string, attr: string, event: any) {
    let serialized = serializeEvent(event)
    serialized.type = attr
    this.model.trigger_event(new DOMEvent(elname, serialized))
  }

  private _render_child(model: any, el: Element): void {
    const view: any = this._child_views.get(model)
    if (view == null)
      el.innerHTML = htmlDecode(model) || model
    else {
      view._parent = this
      view.renderTo(el)
    }
  }

  resize_layout(): void {
    if (this._parent != null)
      this._parent.resize_layout()
    if (this.root != this)
      super.resize_layout()
  }

  invalidate_layout(): void {
    if (this._parent != null)
      this._parent.invalidate_layout()
    if (this.root != this)
      super.invalidate_layout()
  }

  update_position(): void {
    if (this.root != this) {
      super.update_position()
      return
    }
    this.el.style.display = this.model.visible ? "block" : "none"
    set_size(this.el, this.model)

    let {margin} = this.model
    let margin_spec = null
    if (margin == null)
      this.el.style.margin = ""
    else {
      if (isNumber(margin))
        margin_spec = {top: margin, right: margin, bottom: margin, left: margin}
      else if (margin.length == 2) {
        const [vertical, horizontal] = margin
        margin_spec = {top: vertical, right: horizontal, bottom: vertical, left: horizontal}
      } else {
        const [top, right, bottom, left] = margin
        margin_spec = {top, right, bottom, left}
      }
      const {top, right, bottom, left} = margin_spec
      this.el.style.padding = `${top}px ${right}px ${bottom}px ${left}px`
    }

    for (const child_view of this.child_views)
      child_view.update_position()
  }

  _render_node(node: any, children: any[]): void {
    const id = this.model.data.id
    if (this.model.looped.indexOf(node) > -1) {
      for (let i = 0; i < children.length; i++) {
        let el: any = document.getElementById(`${node}-${i}-${id}`)
        if (el == null) {
          console.warn(`DOM node '${node}-${i}-${id}' could not be found. Cannot render children.`)
          continue
        }
        this._render_child(children[i], el)
      }
    } else {
      let el: any = document.getElementById(`${node}-${id}`)
      if (el == null) {
        console.warn(`DOM node '${node}-${id}' could not be found. Cannot render children.`)
        return
      }
      for (const child of children)
        this._render_child(child, el)
    }
  }

  private _render_children(): void {
    for (const node in this.model.children) {
      let children = this.model.children[node]
      if (typeof children == "string") {
        children = this.model.data[children]
        if (!isArray(children))
          children = [children]
      }
      this._render_node(node, children)
    }
  }

  private _render_html(literal: any, state: any={}): any {
    let htm = literal
    let callbacks = ''
    const methods: string[] = []
    for (const elname in this.model.callbacks) {
      for (const callback of this.model.callbacks[elname]) {
        const [cb, method] = callback;
        let definition: string
        htm = htm.replace('${'+method, '$--{'+method)
        if (method.startsWith('script(')) {
          const meth = (
            method
              .replace("('", "_").replace("')", "")
              .replace('("', "_").replace('")', "")
              .replace('-', '_')
          )
          const script_name = meth.replace("script_", "")
          htm = htm.replace(method, meth)
          definition = `
          const ${meth} = (event) => {
            view._state.event = event
            view.run_script("${script_name}")
            delete view._state.event
          }
          `
        } else {
          definition = `
          const ${method} = (event) => {
            view._send_event("${elname}", "${cb}", event)
          }
          `
        }
        if (methods.indexOf(method) > -1)
          continue
        methods.push(method)
        callbacks = callbacks + definition
      }
    }
    htm = (
      htm
        .replaceAll('${model.', '$-{model.')
        .replaceAll('${', '${data.')
        .replaceAll('$-{model.', '${model.')
        .replaceAll('$--{', '${')
    )
    return new Function("view, model, data, state, html, useCallback", callbacks+"return html`"+htm+"`;")(
      this, this.model, this.model.data, state, html, useCallback
    )
  }

  private _render_script(literal: any, id: string) {
    const scripts = []
    for (const elname of this.model.nodes) {
      if (elname in this.model.children && typeof this.model.children[elname] !== "string")
        continue
      const elvar = elname.replace('-', '_')
      if (literal.indexOf(elvar) === -1)
        continue
      const script = `
      const ${elvar} = document.getElementById('${elname}-${id}')
      if (${elvar} == null) {
        console.warn("DOM node '${elname}' could not be found. Cannot execute callback.")
        return
      }
      `
      scripts.push(script)
    }
    const event = `
    if (state.event !== undefined) {
      const event = state.event
    }
    `
    scripts.push(event)
    scripts.push(literal)
    return new Function("model, data, state, view, script, self", scripts.join('\n'))
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
      if (el == null)
        continue
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
      const node_events = this.model.events[node]
      for (const event_name in node_events) {
        const event_callback = (event: any) => {
          this._send_event(node, event_name, event)
          if (node in this.model.attrs && node_events[event_name])
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
      try {
        this._changing = true
        render(rendered, this.el)
      } finally {
        this._changing = false
      }
    }
  }

  private _update_model(el: any, name: string): void {
    if (this._changing)
      return
    const attrs: any = {}
    for (const attr_info of this.model.attrs[name]) {
      const [attr, tokens, template] = attr_info
      let value = attr === 'children' ? el.innerHTML : el[attr]
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

    try {
      this._changing = true
      this.model.data.setv(serialize_attrs(attrs))
    } catch {
      console.log('Could not serialize', attrs)
    } finally {
      this._changing = false
    }
  }
}

export namespace ReactiveHTML {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    attrs: p.Property<any>
    callbacks: p.Property<any>
    children: p.Property<any>
    data: p.Property<any>
    events: p.Property<any>
    html: p.Property<string>
    looped: p.Property<string[]>
    nodes: p.Property<string[]>
    scripts: p.Property<any>
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
    this.define<ReactiveHTML.Props>(({Array, Any, String}) => ({
      attrs:     [ Any,    {} ],
      callbacks: [ Any,    {} ],
      children:  [ Any,    {} ],
      data:      [ Any,       ],
      events:    [ Any,    {} ],
      html:      [ String, "" ],
      looped:    [ Array(String), [] ],
      nodes:     [ Array(String), [] ],
      scripts:   [ Any,    {} ],
    }))
  }
}
