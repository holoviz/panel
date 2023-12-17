import {Enum} from "@bokehjs/core/kinds"
import * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import JSONFormatter from "json-formatter-js"
import {PanelMarkupView} from "./layout"

export class JSONView extends PanelMarkupView {
  model: JSON

  connect_signals(): void {
    super.connect_signals()
    const {depth, hover_preview, text, theme} = this.model.properties
    this.on_change([depth, hover_preview, text, theme], () => this.render())
  }

  render(): void {
    super.render()
    const text = this.model.text.replace(/(\r\n|\n|\r)/gm, "")
    let json;
    try {
      json = window.JSON.parse(text)
    } catch(err) {
      this.container.innerHTML = "<b>Invalid JSON:</b> " + err.toString()
      return
    }
    const config = {hoverPreviewEnabled: this.model.hover_preview, theme: this.model.theme}
    const depth = this.model.depth == null ? Infinity : this.model.depth
    const formatter = new JSONFormatter(json, depth, config)
    const rendered = formatter.render()
    let style = "border-radius: 5px; padding: 10px; width: 100%; height: 100%;";
    if (this.model.theme == "dark")
      rendered.style.cssText = "background-color: rgb(30, 30, 30);" + style;
    else
      rendered.style.cssText = style;
    this.container.append(rendered)
  }
}

export const JSONTheme = Enum("dark", "light")

export namespace JSON {
  export type Attrs = p.AttrsOf<Props>
  export type Props = Markup.Props & {
    css: p.Property<string[]>
    depth: p.Property<number | null>
    hover_preview: p.Property<boolean>
    theme: p.Property<typeof JSONTheme["__type__"]>
  }
}

export interface JSON extends JSON.Attrs {}

export class JSON extends Markup {
  properties: JSON.Props

  constructor(attrs?: Partial<JSON.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.markup"

  static {
    this.prototype.default_view = JSONView
    this.define<JSON.Props>(({Array, Boolean, Int, Nullable, String}) => ({
      css:           [ Array(String), [] ],
      depth:         [ Nullable(Int),  1 ],
      hover_preview: [ Boolean,    false ],
      theme:         [ JSONTheme, "dark" ],
    }))
  }
}
