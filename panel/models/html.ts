import {ModelEvent, server_event} from "@bokehjs/core/bokeh_events"
import {Signal} from "@bokehjs/core/signaling"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import type * as p from "@bokehjs/core/properties"
import type {Attrs, Dict} from "@bokehjs/core/types"
import {entries} from "@bokehjs/core/util/object"
import {Markup} from "@bokehjs/models/widgets/markup"
import {PanelMarkupView} from "./layout"
import {serializeEvent} from "./event-to-object"

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

/**
 * Replaces the characters between `start` and `end` of the unescaped
 * text with the escaped `patch`, producing `version` of the text.
 */
@server_event("html_stream")
export class HTMLStreamEvent extends ModelEvent {
  constructor(readonly model: HTML, readonly patch: string, readonly start: number,
              readonly end: number | null = null, readonly version: number | null = null) {
    super()
    this.patch = patch
    this.start = start
    this.end = end
    this.version = version
    this.origin = model
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, patch: this.patch, start: this.start, end: this.end, version: this.version}
  }

  static override from_values(values: object) {
    type Values = {model: HTML, patch: string, start: number, end: number | null, version: number | null}
    const {model, patch, start, end, version} = values as Values
    return new HTMLStreamEvent(model, patch, start, end, version)
  }
}

const ESCAPES: {[key: string]: string} = {"&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#x27;"}
const UNESCAPES: {[key: string]: string} = Object.fromEntries(Object.entries(ESCAPES).map(([k, v]) => [v, k]))

// Exact inverses of Python's html.escape, unlike html_decode, which
// parses arbitrary entities and normalizes newlines.
export function escape_html(text: string): string {
  return text.replace(/[&<>"']/g, (c) => ESCAPES[c])
}

export function unescape_html(text: string): string {
  return text.replace(/&(?:amp|lt|gt|quot|#x27);/g, (e) => UNESCAPES[e])
}

const VOID_TAGS = new Set([
  "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
  "meta", "param", "source", "track", "wbr",
])
const RAW_TEXT_TAGS = new Set([
  "script", "style", "textarea", "title", "xmp", "iframe", "noembed",
  "noframes", "noscript", "plaintext",
])
const TAG_NAME = /[a-zA-Z][^\s/>]*/y

function find_tag_end(html: string, pos: number): number {
  let quote: string | null = null
  let prev = ""
  for (let i = pos; i < html.length; i++) {
    const c = html[i]
    if (quote != null) {
      if (c === quote) {
        quote = null
      }
    } else if ((c === "\"" || c === "'") && prev === "=") {
      quote = c
    } else if (c === ">") {
      return i + 1
    }
    if (c.trim() !== "") {
      prev = c
    }
  }
  return -1
}

/**
 * Splits HTML into top-level blocks, i.e. ranges ending where all
 * opened elements are closed again, starting the scan at `from`. HTML
 * that never closes an element (or ends mid-tag) yields one block for
 * the remainder, so malformed input degrades to a full re-render.
 */
export function split_blocks(html: string, from: number = 0): [number, number][] {
  const blocks: [number, number][] = []
  const stack: string[] = []
  let foreign = 0
  let start = from
  let i = from
  const boundary = () => {
    if (stack.length === 0) {
      blocks.push([start, i])
      start = i
    }
  }
  while (true) {
    const lt = html.indexOf("<", i)
    if (lt === -1) {
      break
    }
    i = lt
    const next = html[i + 1]
    if (next === "!" || next === "?") {
      const comment = html.startsWith("<!--", i)
      const close = comment ? html.indexOf("-->", i + 4) : html.indexOf(">", i + 2)
      if (close === -1) {
        break
      }
      i = close + (comment ? 3 : 1)
      boundary()
      continue
    }
    const closing = next === "/"
    TAG_NAME.lastIndex = i + (closing ? 2 : 1)
    const match = TAG_NAME.exec(html)
    if (match == null) {
      i += 1
      continue
    }
    const name = match[0].toLowerCase()
    const end = find_tag_end(html, TAG_NAME.lastIndex)
    if (end === -1) {
      break
    }
    i = end
    if (closing) {
      const index = stack.lastIndexOf(name)
      if (index !== -1) {
        for (const tag of stack.splice(index)) {
          if (tag === "svg" || tag === "math") {
            foreign--
          }
        }
        boundary()
      }
    } else if (VOID_TAGS.has(name) || (foreign > 0 && html[end - 2] === "/")) {
      boundary()
    } else if (foreign === 0 && RAW_TEXT_TAGS.has(name)) {
      const close_tag = new RegExp(`</${name}[\\s/>]`, "ig")
      close_tag.lastIndex = i
      const close = close_tag.exec(html)
      const close_end = close == null ? -1 : html.indexOf(">", close.index)
      if (close_end === -1) {
        break
      }
      i = close_end + 1
      boundary()
    } else {
      stack.push(name)
      if (name === "svg" || name === "math") {
        foreign++
      }
    }
  }
  if (start < html.length) {
    blocks.push([start, html.length])
  }
  return blocks
}

function select_all(nodes: Iterable<Node>, selector: string): Element[] {
  const found: Element[] = []
  for (const node of nodes) {
    if (node instanceof Element) {
      if (node.matches(selector)) {
        found.push(node)
      }
      found.push(...node.querySelectorAll(selector))
    }
  }
  return found
}

type Block = {end: number, nodes: ChildNode[]}

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
  replace_scripts(node.querySelectorAll("script"))
}

function replace_scripts(scripts: Iterable<Element>): void {
  for (const old_script of scripts) {
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

  // DOM nodes rendered from each top-level block of the streamed text,
  // or null if the container was rendered as a whole.
  protected _blocks: Block[] | null = null
  // Lowest offset of the text modified since the last DOM update
  protected _dirty: number | null = null
  protected _frame: number | null = null

  protected readonly _event_listeners: Map<string, Map<string, (event: Event) => void>> = new Map()

  override connect_signals(): void {
    super.connect_signals()

    const {text, visible, events} = this.model.properties
    this.on_change(text, () => {
      this.model.reset_stream()
      this._dirty = null
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

    this.model.on_event(HTMLStreamEvent, (event: HTMLStreamEvent) => this.model.apply_stream(event))
    this.connect(this.model.streamed, (start: number) => {
      this._dirty = Math.min(this._dirty ?? start, start)
      if (this._frame == null) {
        this._frame = requestAnimationFrame(() => this._flush_stream())
      }
    })
  }

  override remove(): void {
    if (this._frame != null) {
      cancelAnimationFrame(this._frame)
      this._frame = null
    }
    super.remove()
  }

  override stylesheets(): StyleSheetLike[] {
    return [...super.stylesheets(), html_css]
  }

  protected _flush_stream(): void {
    this._frame = null
    const dirty = this._dirty
    this._dirty = null
    if (dirty == null || this.container == null) {
      return
    }
    const html = this.model.stream_text
    if (!this.model.disable_math && this.contains_tex(html)) {
      this.set_html(this.process_tex())
    } else {
      this._update_blocks(html, dirty)
    }
  }

  /**
   * Re-renders only the top-level blocks at or after the first
   * modified offset, keeping the DOM (and any text selection) of the
   * preceding blocks intact.
   */
  protected _update_blocks(html: string, dirty: number): void {
    let blocks = this._blocks
    let keep = 0
    if (blocks == null) {
      this.container.replaceChildren()
      blocks = []
    } else {
      // The last block may still be growing even if it ends before dirty
      while (keep < blocks.length - 1 && blocks[keep].end <= dirty) {
        keep++
      }
      for (const block of blocks.splice(keep)) {
        for (const node of block.nodes) {
          node.remove()
        }
      }
    }
    const from = keep > 0 ? blocks[keep - 1].end : 0
    const fragment = document.createDocumentFragment()
    const parser = document.createElement("div")
    const added: ChildNode[] = []
    for (const [start, end] of split_blocks(html, from)) {
      parser.innerHTML = html.slice(start, end)
      const nodes = [...parser.childNodes]
      fragment.append(...nodes)
      added.push(...nodes)
      blocks.push({end, nodes})
    }
    this.container.append(fragment)
    this._blocks = blocks
    if (this.model.run_scripts) {
      replace_scripts(select_all(added, "script"))
    }
    if (Object.keys(this.model.events).length !== 0) {
      this._remove_event_listeners()
      this._setup_event_listeners()
    }
    this._decorate(added)
  }

  set_html(html: string | null): void {
    if (html === null || this.container == null) {
      return
    }
    this._blocks = null
    this.container.innerHTML = html
    if (this.model.run_scripts) {
      run_scripts(this.container)
    }
    this._setup_event_listeners()
    this._decorate([this.container])
  }

  protected _decorate(nodes: Iterable<Node>): void {
    for (const codeblock of select_all(nodes, ".codehilite")) {
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
    for (const anchor of select_all(nodes, "a")) {
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
    stream_version: p.Property<number>
  }
}

export interface HTML extends HTML.Attrs {}

export class HTML extends Markup {
  declare properties: HTML.Props

  // Unescaped text maintained from stream events and the events that
  // arrived ahead of the next version. Views share the model, so events
  // are applied here, once and in order, rather than by each view.
  protected _stream_text: string | null = null
  protected _stream_queue: Map<number, HTMLStreamEvent> = new Map()

  // Emits the lowest offset of the text modified by a stream event
  readonly streamed = new Signal<number, this>(this, "streamed")

  constructor(attrs?: Partial<HTML.Attrs>) {
    super(attrs)
  }

  get stream_text(): string {
    return this._stream_text ??= unescape_html(this.text)
  }

  apply_stream(event: HTMLStreamEvent): void {
    if (event.version == null) {
      this._apply_stream(event)
      return
    }
    if (event.version <= this.stream_version) {
      return
    }
    // Messages written to the socket via different paths on the
    // server may arrive out of order.
    this._stream_queue.set(event.version, event)
    let next: HTMLStreamEvent | undefined
    while ((next = this._stream_queue.get(this.stream_version + 1)) != null) {
      this._stream_queue.delete(next.version!)
      this._apply_stream(next)
    }
  }

  protected _apply_stream(event: HTMLStreamEvent): void {
    const text = this.stream_text
    const end = event.end ?? text.length
    this._stream_text = text.slice(0, event.start) + unescape_html(event.patch) + text.slice(end)
    const attrs: Partial<HTML.Attrs> = {text: escape_html(this._stream_text)}
    if (event.version != null) {
      attrs.stream_version = event.version
    }
    this.setv(attrs, {silent: true})
    this.streamed.emit(event.start)
  }

  reset_stream(): void {
    this._stream_text = null
  }

  static override __module__ = "panel.models.markup"

  static {
    this.prototype.default_view = HTMLView
    this.define<HTML.Props>(({Bool, Int, Str, List, Dict}) => ({
      events: [ Dict(List(Str)), {} ],
      run_scripts: [ Bool, true ],
      stream_version: [ Int, 0 ],
    }))
  }
}
