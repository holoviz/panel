import * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import JSONFormatter from "json-formatter-js"
import {PanelMarkupView} from "./layout"

export class JSONView extends PanelMarkupView {
  model: JSON

  render(): void {
    super.render();
    const text = this.model.text.replace(/(\r\n|\n|\r)/gm, "").replace("'", '"')
    let json;
    try {
      json = window.JSON.parse(text)
    } catch(err) {
      this.markup_el.innerHTML = "<b>Invalid JSON:</b> " + err.toString()
      return
    }
    const config = {hoverPreviewEnabled: this.model.hover_preview, theme: this.model.theme}
    const formatter = new JSONFormatter(json, this.model.depth, config)
    const rendered = formatter.render()
    let style = "border-radius: 5px; padding: 10px;";
    if (this.model.theme == "dark")
      rendered.style.cssText = "background-color: rgb(30, 30, 30);" + style;
    else
      rendered.style.cssText = style;
    this.markup_el.append(rendered)
  }
}

type Theme = "light" | "dark"
const Theme: Theme[] = ["dark", "light"]

export namespace JSON {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Markup.Props & {
    depth: p.Property<number>
    hover_preview: p.Property<boolean> 
    theme: p.Property<"light" | "dark">
  }
}

export interface JSON extends JSON.Attrs {}

export class JSON extends Markup {
  properties: JSON.Props

  constructor(attrs?: Partial<JSON.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.markup"

  static init_JSON(): void {
    this.prototype.default_view = JSONView
    this.define<JSON.Props>({
      depth: [p.Number, 1],
      hover_preview: [p.Boolean, false],
      theme: [p.Enum(Theme), "dark"],
    })
  }
}
