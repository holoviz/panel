import {render} from "preact"
import {useCallback} from "preact/hooks"
import {html} from "htm/preact"

import {div} from "@bokehjs/core/dom"
import type {Dict, Attrs} from "@bokehjs/core/types"
import {assert, unreachable} from "@bokehjs/core/util/assert"
import {enumerate} from "@bokehjs/core/util/iterator"
import {isArray, isString} from "@bokehjs/core/util/types"
import {dict, keys, entries} from "@bokehjs/core/util/object"
import type * as p from "@bokehjs/core/properties"
import {Model} from "@bokehjs/model"
import {UIElement} from "@bokehjs/models/ui/ui_element"

import {dict_to_records} from "./data"
import {serializeEvent} from "./event-to-object"
import {DOMEvent, html_decode} from "./html"
import {HTMLBox, HTMLBoxView} from "./layout"
import {convertUndefined} from "./util"

function serialize_attrs(attrs: Attrs): Attrs {
  const serialized: Attrs = {}
  for (const [attr, value] of entries(attrs)) {
    const serialized_value = (() => {
      if (isString(value)) {
        if (value !== "" && (value === "NaN" || !isNaN(Number(value)))) {
          return Number(value)
        } else if (value === "false" || value === "true") {
          return value === "true" ? true : false
        }
      }
      return value
    })()
    serialized[attr] = serialized_value
  }
  return serialized
}

function escape_regex(string: string) {
  return string.replace(/[-\/\\^$*+?.()|[\]]/g, "\\$&")
}

function extract_token(template: string, str: string, tokens: string[]): {[key: string]: string} | null {
  const token_mapping: Map<string, string> = new Map()
  for (const match of tokens) {
    token_mapping.set(`{${match}}`, "(.*)")
  }

  const token_list = []
  let regexp_template = `^${escape_regex(template)}$`

  // Find the order of the tokens
  let i, token_index, token_entry
  for (const [m, replacement] of token_mapping) {
    token_index = template.indexOf(m)

    // Token found
    if (token_index > -1) {
      regexp_template = regexp_template.replace(m, replacement)
      token_entry = {
        index: token_index,
        token: m,
      }

      for (i = 0; i < token_list.length && token_list[i].index < token_index; i++) {}

      // Insert it at index i
      if (i < token_list.length) {
        token_list.splice(i, 0, token_entry)
      } else {
        token_list.push(token_entry)
      }
    }
  }

  regexp_template = regexp_template.replace(/\{[^{}]+\}/g, ".*")
  const match = new RegExp(regexp_template).exec(str)

  if (match != null) {
    const result: {[key: string]: string} = {}
    // Find your token entry
    for (i = 0; i < token_list.length; i++) {
      result[token_list[i].token.slice(1, -1)] = match[i + 1]
    }
    return result
  } else {
    return null
  }
}

function element_lookup(root: ShadowRoot, el_id: string): HTMLElement | null {
  let el = root.getElementById(el_id)
  if (el == null) {
    el = document.getElementById(el_id)
  }
  return el
}

export class ReactiveHTMLView extends HTMLBoxView {
  declare model: ReactiveHTML

  html: string
  container: HTMLDivElement
  protected _changing: boolean = false
  protected readonly _event_listeners: Map<string, Map<string, (event: Event) => void>> = new Map()
  protected _mutation_observers: MutationObserver[] = []
  protected _script_fns: Map<string, Function> = new Map()
  protected _state: any = {}

  override initialize(): void {
    super.initialize()
    this.html = html_decode(this.model.html) ?? this.model.html
  }

  _recursive_connect(model: Model, update_children: boolean, path: string): void {
    for (const prop of model) {
      const subpath = path.length != 0 ? `${path}.${prop.attr}` : prop.attr
      const obj = prop.get_value()
      if (obj == null) {
        continue
      }
      if (obj instanceof Model) {
        this._recursive_connect(obj, true, subpath)
      }
      this.on_change(prop, () => {
        if (update_children) {
          for (const [node, attr] of entries(this.model.children)) {
            if (attr == prop.attr) {
              let children = prop.get_value() as string | (string | UIElement)[]
              if (!isArray(children)) {
                children = [children]
              }
              this._render_node(node, children)
              return
            }
          }
        }
        if (!this._changing) {
          this._update(subpath)
        }
      })
    }
  }

  override connect_signals(): void {
    super.connect_signals()

    const {children, events} = this.model.properties
    this.on_change(children, async () => {
      this.html = html_decode(this.model.html) ?? this.model.html
      await this.build_child_views()
      this.invalidate_render()
    })
    this._recursive_connect(this.model.data, true, "")
    this.on_change(events, () => {
      this._remove_event_listeners()
      this._setup_event_listeners()
    })
    this.connect_scripts()
  }

  connect_scripts(): void {
    const {id} = this.model.data
    for (const [prop, scripts] of entries(this.model.scripts)) {
      let data_model = this.model.data
      let attr: string
      if (prop.includes(".")) {
        const path = prop.split(".")
        attr = path[path.length - 1]
        for (const p of path.slice(0, -1)) {
          const value = data_model.property(p).get_value()
          assert(value instanceof Model)
          data_model = value
        }
      } else {
        attr = prop
      }
      for (const script of scripts) {
        const decoded_script = html_decode(script) ?? script
        const script_fn = this._render_script(decoded_script, id)
        this._script_fns.set(prop, script_fn)
        if (!(attr in data_model.properties)) {
          continue
        }
        const property = data_model.property(attr)
        const is_event_param = this.model.event_params.includes(prop)
        this.on_change(property, () => {
          if (!this._changing && !(is_event_param && !data_model.property(prop).get_value())) {
            this.run_script(prop)
            if (is_event_param) {
              data_model.setv({[prop]: false})
            }
          }
        })
      }
    }
  }

  run_script(property: string, silent: boolean = false): void {
    const script_fn = this._script_fns.get(property)
    if (script_fn === undefined) {
      if (!silent) {
        console.warn(`Script '${property}' could not be found.`)
      }
      return
    }
    const this_obj: any = {
      get_records(property: string, index: boolean): unknown[] {
        return this.get_records(property, index)
      },
    }
    for (const name of this._script_fns.keys()) {
      this_obj[name] = () => this.run_script(name)
    }
    return script_fn(
      this.model,
      this.model.data,
      this._state,
      this,
      (s: string) => this.run_script(s),
      this_obj,
    )
  }

  get_records(property_name: string, index: boolean = true): unknown[] {
    return dict_to_records(this.model.data.property(property_name), index)
  }

  override disconnect_signals(): void {
    super.disconnect_signals()
    this._remove_event_listeners()
    this._remove_mutation_observers()
  }

  override remove(): void {
    this.run_script("remove", true)
    super.remove()
  }

  override get child_models(): UIElement[] {
    const models = []
    for (const [_parent, children] of entries(this.model.children)) {
      for (const model of children) {
        if (!isString(model)) {
          models.push(model)
        }
      }
    }
    return models
  }

  override _after_layout(): void {
    this.run_script("after_layout", true)
  }

  override render(): void {
    this.empty()
    this._update_stylesheets()
    this._update_css_classes()
    this._apply_styles()
    this._apply_visible()

    this.container = div({style: {display: "contents"}})
    this.shadow_el.append(this.container)
    this._update()
    this._render_children()
    this._setup_mutation_observers()
    this._setup_event_listeners()
    this.run_script("render", true)
  }

  private _send_event(elname: string, attr: string, event: any) {
    const serialized = convertUndefined(serializeEvent(event))
    serialized.type = attr
    this.model.trigger_event(new DOMEvent(elname, serialized))
  }

  private _render_child(child: string | UIElement, el: Element): void {
    if (isString(child)) {
      el.innerHTML = html_decode(child) ?? child
    } else {
      const view = this._child_views.get(child)
      if (view == null) {
        el.innerHTML = ""
      } else {
        el.appendChild(view.el)
        view.render()
        view.r_after_render()
      }
    }
  }

  _render_node(node: string, children: (string | UIElement)[]): void {
    const {id} = this.model.data
    if (this.model.looped.includes(node)) {
      for (const [child, i] of enumerate(children)) {
        const el_id = `${node}-${i}-${id}`
        const el = element_lookup(this.shadow_el, el_id)
        if (el == null) {
          console.warn(`DOM node '${el_id}' could not be found. Cannot render children.`)
          continue
        }
        this._render_child(child, el)
      }
    } else {
      const el_id = `${node}-${id}`
      const el = element_lookup(this.shadow_el, el_id)
      if (el == null) {
        console.warn(`DOM node '${el_id}' could not be found. Cannot render children.`)
        return
      }
      for (const child of children) {
        this._render_child(child, el)
      }
    }
  }

  private _render_children(): void {
    for (const [node, children] of entries(this.model.children)) {
      const computed_children = (() => {
        if (isString(children)) {
          const value = this.model.data.property(children).get_value() as string | (string | UIElement)[]
          if (isString(value)) {
            return [value]
          } else if (isArray(value)) {
            return value
          } else {
            unreachable()
          }
        } else {
          return children
        }
      })()
      this._render_node(node, computed_children)
    }
  }

  private _render_html(literal: string, state: any = {}): any {
    let htm = literal.replace(/[`]/g, "\\$&")
    let collected_callbacks = ""
    const methods: string[] = []
    for (const [el_name, callbacks] of entries(this.model.callbacks)) {
      for (const [cb, method] of callbacks) {
        let definition: string
        htm = htm.replaceAll(`\${${method}}`, `$--{${method}}`)
        if (method.startsWith("script(")) {
          const meth = (
            method
              .replace("('", "_").replace("')", "")
              .replace('("', "_").replace('")', "")
              .replace("-", "_")
          )
          const script_name = meth.replaceAll("script_", "")
          htm = htm.replaceAll(method, meth)
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
            let elname = "${el_name}"
            if (RegExp("\{\{.*loop\.index.*\}\}").test(elname)) {
              const pattern = RegExp(elname.replace(/\{\{(.+?)\}\}/g, String.fromCharCode(92) + "d+"))
              for (const p of event.path) {
                if (pattern.exec(p.id) != null) {
                  elname = p.id.split("-").slice(null, -1).join("-")
                  break
                }
              }
            }
            view._send_event(elname, "${cb}", event)
          }
          `
        }
        if (methods.indexOf(method) > -1) {
          continue
        }
        methods.push(method)
        collected_callbacks += definition
      }
    }
    htm = htm
      .replaceAll("${model.", "$-{model.")
      .replaceAll("${", "${data.")
      .replaceAll("$-{model.", "${model.")
      .replaceAll("$--{", "${")
    return new Function("view, model, data, state, html, useCallback", `${collected_callbacks}return html\`${htm}\`;`)(
      this, this.model, this.model.data, state, html, useCallback,
    )
  }

  private _render_script(literal: string, id: string) {
    const scripts = []
    for (const elname of this.model.nodes) {
      const elvar = elname.replace("-", "_")
      if (!literal.includes(elvar)) {
        continue
      }
      const script = `
      let ${elvar} = view.shadow_el.getElementById('${elname}-${id}')
      if (${elvar} == null) {
        ${elvar} = document.getElementById('${elname}-${id}')
      }
      if (${elvar} == null) {
        console.warn("DOM node '${elname}' could not be found. Cannot execute callback.")
        return
      }
      `
      scripts.push(script)
    }
    const event = `
    let event = null
    if (state.event !== undefined) {
      event = state.event
    }
    `
    scripts.push(event)
    scripts.push(literal)
    return new Function("model, data, state, view, script, self", scripts.join("\n"))
  }

  private _remove_mutation_observers(): void {
    for (const observer of this._mutation_observers) {
      observer.disconnect()
    }
    this._mutation_observers = []
  }

  private _setup_mutation_observers(): void {
    const {id} = this.model.data
    for (const name of keys(this.model.attrs)) {
      const el = element_lookup(this.shadow_el, `${name}-${id}`)
      if (el == null) {
        console.warn(`DOM node '${name}-${id}' could not be found. Cannot set up MutationObserver.`)
        continue
      }
      const observer = new MutationObserver(() => {
        this._update_model(el, name)
      })
      observer.observe(el, {attributes: true})
      this._mutation_observers.push(observer)
    }
  }

  private _remove_event_listeners(): void {
    const {id} = this.model.data
    for (const [node, callbacks] of this._event_listeners) {
      const el = element_lookup(this.shadow_el, `${node}-${id}`)
      if (el == null) {
        continue
      }
      for (const [event_name, event_callback] of callbacks) {
        el.removeEventListener(event_name, event_callback)
      }
    }
    this._event_listeners.clear()
  }

  private _setup_event_listeners(): void {
    const {id} = this.model.data
    const attrs = dict(this.model.attrs)
    for (const [node, node_events] of entries(this.model.events)) {
      const el = element_lookup(this.shadow_el, `${node}-${id}`)
      if (el == null) {
        console.warn(`DOM node '${node}-${id}' could not be found. Cannot subscribe to DOM events.`)
        continue
      }
      for (const [event_name, event_doit] of entries(node_events)) {
        const event_callback = (event: Event) => {
          this._send_event(node, event_name, event)
          if (attrs.has(node) && event_doit) {
            this._update_model(el, node)
          }
        }
        el.addEventListener(event_name, event_callback)
        let callbacks = this._event_listeners.get(node)
        if (callbacks === undefined) {
          this._event_listeners.set(node, callbacks = new Map())
        }
        callbacks.set(event_name, event_callback)
      }
    }
  }

  private _update(property: string | null = null): void {
    if (property == null || this.html.includes(`\${${property}}`)) {
      const rendered = this._render_html(this.html)
      if (rendered == null) {
        return
      }
      try {
        this._changing = true
        render(rendered, this.container)
      } finally {
        this._changing = false
      }
    }
  }

  private _update_model(el: HTMLElement, name: string): void {
    if (this._changing) {
      return
    }
    const attr_infos = dict(this.model.attrs).get(name) ?? []
    const attrs: {[key: string]: unknown} = {}
    for (const attr_info of attr_infos) {
      const [attr, tokens, template] = attr_info
      let value: unknown = attr == "children" ? el.innerHTML : (el as any)[attr]
      if (tokens.length === 1 && (`{${tokens[0]}}` === template)) {
        attrs[tokens[0]] = value
      } else if (isString(value)) {
        value = extract_token(template, value, tokens)
        if (value == null) {
          console.warn(`Could not resolve parameters in ${name} element ${attr} attribute value ${value}.`)
        } else {
          for (const [param, param_val] of entries(value)) {
            if (param_val === undefined) {
              console.warn(`Could not resolve ${param} in ${name} element ${attr} attribute value ${value}.`)
            } else {
              attrs[param] = param_val
            }
          }
        }
      }
    }

    try {
      this._changing = true
      this.model.data.setv(serialize_attrs(attrs))
    } catch {
      console.error("Could not serialize", attrs)
    } finally {
      this._changing = false
    }
  }
}

export namespace ReactiveHTML {
  export type Attrs = p.AttrsOf<Props>

  export type Props = HTMLBox.Props & {
    attrs: p.Property<Dict<[string, string[], string][]>>
    callbacks: p.Property<Dict<[string, string][]>>
    children: p.Property<Dict<(UIElement | string)[] | string>>
    data: p.Property<Model>
    event_params: p.Property<string[]>
    events: p.Property<Dict<Dict<boolean>>>
    html: p.Property<string>
    looped: p.Property<string[]>
    nodes: p.Property<string[]>
    scripts: p.Property<Dict<string[]>>
  }
}

export interface ReactiveHTML extends ReactiveHTML.Attrs {}

export class ReactiveHTML extends HTMLBox {
  declare properties: ReactiveHTML.Props

  constructor(attrs?: Partial<ReactiveHTML.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.reactive_html"

  static {
    this.prototype.default_view = ReactiveHTMLView
    this.define<ReactiveHTML.Props>(({Bool, Str, List, Dict, Tuple, Or, Ref}) => ({
      attrs:        [ Dict(List(Tuple(Str, List(Str), Str))), {} ],
      callbacks:    [ Dict(List(Tuple(Str, Str))), {} ],
      children:     [ Dict(Or(List(Or(Ref(UIElement), Str)), Str)), {} ],
      data:         [ Ref(Model) ],
      event_params: [ List(Str), [] ],
      events:       [ Dict(Dict(Bool)), {} ],
      html:         [ Str, "" ],
      looped:       [ List(Str), [] ],
      nodes:        [ List(Str), [] ],
      scripts:      [ Dict(List(Str)), {} ],
    }))
  }
}
