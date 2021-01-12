import * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import {ModelEvent, JSON} from "@bokehjs/core/bokeh_events"
import {PanelMarkupView} from "./layout"
import {serializeEvent} from "./event-to-object";

export class DOMEvent extends ModelEvent {
  event_name: string = "dom_event"

  constructor(readonly node: string, readonly data: any) {
    super()
  }

  protected _to_json(): JSON {
    return {model: this.origin, node: this.node, data: this.data}
  }
}

export function htmlDecode(input: string): string | null {
  var doc = new DOMParser().parseFromString(input, "text/html");
  return doc.documentElement.textContent;
}

export function runScripts(node: any): void {
  Array.from(node.querySelectorAll("script")).forEach((oldScript: any) => {
    const newScript = document.createElement("script");
    Array.from(oldScript.attributes)
      .forEach((attr: any) => newScript.setAttribute(attr.name, attr.value) );
    newScript.appendChild(document.createTextNode(oldScript.innerHTML));
    if (oldScript.parentNode)
      oldScript.parentNode.replaceChild(newScript, oldScript);
  });
}

export class HTMLView extends PanelMarkupView {
  model: HTML

  render(): void {
    super.render()
    const decoded = htmlDecode(this.model.text);
    const html = decoded || this.model.text
    if (!html) {
      this.markup_el.innerHTML = '';
      return;
    }
    this.markup_el.innerHTML = html
	runScripts(this.markup_el)
	this._setup_event_listeners()
  }

  _setup_event_listeners(): void {
    for (const name in this.model.events) {
      const el: any = document.getElementById(name)
      if (el == null) {
        console.warn(`DOM node '${name}' could not be found. Cannot subscribe to DOM events.`)
        continue
      }
      for (const event_name of this.model.events[name]) {
        el.addEventListener(event_name, (event: any) => {
          this.model.trigger_event(new DOMEvent(name, serializeEvent(event)))
		})
	  }
	}
  }
}

export namespace HTML {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Markup.Props & {
	events: p.Property<any>
  }
}

export interface HTML extends HTML.Attrs {}

export class HTML extends Markup {
  properties: HTML.Props

  constructor(attrs?: Partial<HTML.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.markup"

  static init_HTML(): void {
    this.prototype.default_view = HTMLView
    this.define<HTML.Props>({
	  events: [p.Any, {} ]
	})
  }
}
