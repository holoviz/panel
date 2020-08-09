import * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import {PanelMarkupView} from "./layout"

export function htmlDecode(input: string): string | null {
  var doc = new DOMParser().parseFromString(input, "text/html");
  return doc.documentElement.textContent;
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
    Array.from(this.markup_el.querySelectorAll("script")).forEach( oldScript => {
      const newScript = document.createElement("script");
      Array.from(oldScript.attributes)
        .forEach( attr => newScript.setAttribute(attr.name, attr.value) );
      newScript.appendChild(document.createTextNode(oldScript.innerHTML));
      if (oldScript.parentNode)
        oldScript.parentNode.replaceChild(newScript, oldScript);
    });
  }
}

export namespace HTML {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Markup.Props
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
  }
}
