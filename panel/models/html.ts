import {ModelEvent, server_event} from "@bokehjs/core/bokeh_events"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"
import type {Attrs, Dict} from "@bokehjs/core/types"
import {entries} from "@bokehjs/core/util/object"
import {Markup} from "@bokehjs/models/widgets/markup"
import {PanelMarkupView} from "./layout"
import {serializeEvent} from "./event-to-object"
import {throttle} from "./util"

import html_css from "styles/models/html.css"

const COPY_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"  fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-clipboard"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M9 5h-2a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-12a2 2 0 0 0 -2 -2h-2" /><path d="M9 3m0 2a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2v0a2 2 0 0 1 -2 2h-2a2 2 0 0 1 -2 -2z"/></svg>`

const CHECK_ICON = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"  fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"  class="icon icon-tabler icons-tabler-outline icon-tabler-check"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M5 12l5 5l10 -10"/></svg>`

function searchAllDOMs(node: Element | ShadowRoot, selector: string): (Element | ShadowRoot)[] {
  let found: (Element | ShadowRoot)[] = []
  if (node instanceof Element && node.matches(selector)) {
    found.push(node)
  }
  node.children && Array.from(node.children).forEach(child => {
    found = found.concat(searchAllDOMs(child, selector))
  })
  if (node instanceof Element && node.shadowRoot) {
    found = found.concat(searchAllDOMs(node.shadowRoot, selector))
  }
  return found
}

@server_event("html_stream")
export class HTMLStreamEvent extends ModelEvent {
  constructor(readonly model: HTML, readonly patch: string, readonly start: number) {
    super()
    this.patch = patch
    this.start = start
    this.origin = model
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, patch: this.patch, start: this.start}
  }

  static override from_values(values: object) {
    const {model, patch, start} = values as {model: HTML, patch: string, start: number}
    return new HTMLStreamEvent(model, patch, start)
  }
}

export class DOMEvent extends ModelEvent {
  constructor(readonly node: string, readonly data: unknown) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, node: this.node, data: this.data}
  }

  static {
    this.prototype.event_name = "dom_event"
  }
}

export function html_decode(input: string): string | null {
  const doc = new DOMParser().parseFromString(input, "text/html")
  return doc.documentElement.textContent
}

export function run_scripts(node: Element): void {
  for (const old_script of node.querySelectorAll("script")) {
    const new_script = document.createElement("script")
    for (const attr of old_script.attributes) {
      new_script.setAttribute(attr.name, attr.value)
    }
    new_script.append(document.createTextNode(old_script.innerHTML))
    const parent_node = old_script.parentNode
    if (parent_node != null) {
      parent_node.replaceChild(new_script, old_script)
    }
  }
}

export class HTMLView extends PanelMarkupView {
  declare model: HTML
  _buffer: string | null = null

  protected readonly _event_listeners: Map<string, Map<string, (event: Event) => void>> = new Map()

  override connect_signals(): void {
    super.connect_signals()

    const {text, visible, events} = this.model.properties
    this.on_change(text, () => {
      this._buffer = null
      const html = this.process_tex()
      this.set_html(html)
    })
    this.on_change(visible, () => {
      if (this.model.visible) {
        this.container.style.visibility = "visible"
      }
    })
    this.on_change(events, () => {
      this._remove_event_listeners()
      this._setup_event_listeners()
    })

    const set_text = throttle(() => {
      const text = this._buffer
      this._buffer = null
      this.model.setv({text}, {silent: true})
      const html = this.process_tex()
      this.set_html(html)
    }, 10)
    this.model.on_event(HTMLStreamEvent, (event: HTMLStreamEvent) => {
      const beginning = this._buffer == null ? this.model.text : this._buffer
      this._buffer = beginning.slice(0, event.start)+event.patch
      set_text()
    })
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), html_css]
  }

  protected rerender() {
    this.render()
    this.invalidate_layout()
  }

  set_html(html: string | null): void {
    if (html === null) {
      return
    }
    this.container.innerHTML = html
    if (this.model.run_scripts) {
      run_scripts(this.container)
    }
    this._setup_event_listeners()
    for (const codeblock of this.container.querySelectorAll(".codehilite")) {
      const copy_button = document.createElement("button")
      const pre = (codeblock.children[0] as HTMLPreElement)
      copy_button.className = "copybtn"
      copy_button.innerHTML = COPY_ICON
      copy_button.addEventListener("click", () => {
        const code = pre.innerText
        navigator.clipboard.writeText(code).then(() => {
          copy_button.innerHTML = CHECK_ICON
          setTimeout(() => {
            copy_button.innerHTML = COPY_ICON
          }, 300)
        })
      })
      codeblock.insertBefore(copy_button, pre)
    }
    for (const anchor of this.container.querySelectorAll("a")) {
      const link = anchor.getAttribute("href")
      if (link && link.startsWith("#")) {
        anchor.addEventListener("click", () => {
          const found = searchAllDOMs(document.body, link)
          if ((found.length > 0) && found[0] instanceof Element) {
            found[0].scrollIntoView()
          }
        })
        if (!this.root.has_finished() && this.model.document && window.location.hash === link) {
          this.model.document.on_event("document_ready", () => {
            anchor.scrollIntoView()
            setTimeout(() => anchor.scrollIntoView(), 5)
          })
        }
      }
    }
  }

  override render(): void {
    super.render()
    this.container.style.visibility = "hidden"
    this.shadow_el.appendChild(this.container)

    if (this.provider.status == "failed" || this.provider.status == "loaded") {
      this._has_finished = true
    }

    const html = this.process_tex()
    this.watch_stylesheets()
    this.set_html(html)
  }

  override style_redraw(): void {
    if (this.model.visible) {
      this.container.style.visibility = "visible"
    }
  }

  override process_tex(): string {
    const decoded = html_decode(this.model.text)
    const text = decoded ?? this.model.text
    if (this.model.disable_math || !this.contains_tex(text)) {
      return text
    }

    const tex_parts = this.provider.MathJax.find_tex(text)
    const processed_text: string[] = []

    let last_index: number | undefined = 0
    for (const part of tex_parts) {
      processed_text.push(text.slice(last_index, part.start.n))
      processed_text.push(this.provider.MathJax.tex2svg(part.math, {display: part.display}).outerHTML)

      last_index = part.end.n
    }

    if (last_index! < text.length) {
      processed_text.push(text.slice(last_index))
    }

    return processed_text.join("")
  }

  private contains_tex(html: string): boolean {
    if (!this.provider.MathJax) {
      return false
    }

    return this.provider.MathJax.find_tex(html).length > 0
  }

  private _remove_event_listeners(): void {
    for (const [node, callbacks] of this._event_listeners) {
      const el = document.getElementById(node)
      if (el == null) {
        console.warn(`DOM node '${node}' could not be found. Cannot subscribe to DOM events.`)
        continue
      }
      for (const [event_name, event_callback] of callbacks) {
        el.removeEventListener(event_name, event_callback)
      }
    }
    this._event_listeners.clear()
  }

  private _setup_event_listeners(): void {
    for (const [node, event_names] of entries(this.model.events)) {
      const el = document.getElementById(node)
      if (el == null) {
        console.warn(`DOM node '${node}' could not be found. Cannot subscribe to DOM events.`)
        continue
      }
      for (const event_name of event_names) {
        const callback = (event: Event) => {
          this.model.trigger_event(new DOMEvent(node, serializeEvent(event)))
        }
        el.addEventListener(event_name, callback)
        let callbacks = this._event_listeners.get(node)
        if (callbacks === undefined) {
          this._event_listeners.set(node, callbacks = new Map())
        }
        callbacks.set(event_name, callback)
      }
    }
  }
}

export namespace HTML {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Markup.Props & {
    events: p.Property<Dict<string[]>>
    run_scripts: p.Property<boolean>
  }
}

export interface HTML extends HTML.Attrs {}

export class HTML extends Markup {
  declare properties: HTML.Props

  constructor(attrs?: Partial<HTML.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.markup"

  static {
    this.prototype.default_view = HTMLView
    this.define<HTML.Props>(({Bool, Str, List, Dict}) => ({
      events: [ Dict(List(Str)), {} ],
      run_scripts: [ Bool, true ],
    }))
  }
}
