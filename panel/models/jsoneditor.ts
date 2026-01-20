import type * as p from "@bokehjs/core/properties"
import type {StyleSheetLike} from "@bokehjs/core/dom"
import {ImportedStyleSheet} from "@bokehjs/core/dom"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import {HTMLBox, HTMLBoxView} from "./layout"
import type {Attrs} from "@bokehjs/core/types"

export class JSONEditEvent extends ModelEvent {
  constructor(readonly data: any) {
    super()
  }

  protected override get event_values(): Attrs {
    return {model: this.origin, data: this.data}
  }

  static {
    this.prototype.event_name = "json_edit"
  }
}

export class JSONEditorView extends HTMLBoxView {
  declare model: JSONEditor

  editor: any
  _menu_context: any

  override connect_signals(): void {
    super.connect_signals()
    const {data, disabled, templates, menu, mode, search, schema} = this.model.properties
    this.on_change([data], () => this.editor.update(this.model.data))
    this.on_change([templates], () => {
      this.editor.options.templates = this.model.templates
    })
    this.on_change([menu], () => {
      this.editor.options.mainMenuBar = this.model.menu
    })
    this.on_change([search], () => {
      this.editor.options.search = this.model.search
    })
    this.on_change([schema], () => {
      this.editor.options.schema = this.model.schema
    })
    this.on_change([disabled, mode], () => {
      const mode = this.model.disabled ? "view": this.model.mode
      this.editor.setMode(mode)
    })
  }

  override stylesheets(): StyleSheetLike[] {
    const styles = super.stylesheets()
    for (const css of this.model.css) {
      styles.push(new ImportedStyleSheet(css))
    }
    return styles
  }

  override remove(): void {
    super.remove()
    this.editor.destroy()
  }

  override render(): void {
    super.render()
    const mode = this.model.disabled ? "view": this.model.mode
    this.editor = new (window as any).JSONEditor(this.shadow_el, {
      mainMenuBar: this.model.menu,
      mode,
      onChangeJSON: (json: any) => {
        this.model.trigger_event(new JSONEditEvent(json))
      },
      onChangeText: (text: any) => {
        try {
          this.model.trigger_event(new JSONEditEvent(JSON.parse(text)))
        } catch (e) {
          console.warn(e)
        }
      },
      onSelectionChange: (start: any, end: any) => {
        this.model.selection = [start, end]
      },
      search: this.model.search,
      schema: this.model.schema,
      templates: this.model.templates,
    })
    this.editor.set(this.model.data)
  }
}

export namespace JSONEditor {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    css: p.Property<string[]>
    data: p.Property<any>
    menu: p.Property<boolean>
    mode: p.Property<string>
    search: p.Property<boolean>
    selection: p.Property<any[]>
    schema: p.Property<any>
    templates: p.Property<any[]>
  }
}

export interface JSONEditor extends JSONEditor.Attrs {}

export class JSONEditor extends HTMLBox {
  declare properties: JSONEditor.Props

  constructor(attrs?: Partial<JSONEditor.Attrs>) {
    super(attrs)
  }

  static override __module__ = "panel.models.jsoneditor"

  static {
    this.prototype.default_view = JSONEditorView
    this.define<JSONEditor.Props>(({Any, List, Bool, Str}) => ({
      css:       [ List(Str), [] ],
      data:      [ Any,           {} ],
      mode:      [ Str,    "tree" ],
      menu:      [ Bool,     true ],
      search:    [ Bool,     true ],
      selection: [ List(Any),    [] ],
      schema:    [ Any,         null ],
      templates: [ List(Any),    [] ],
    }))
  }
}
