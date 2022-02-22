import * as p from "@bokehjs/core/properties"
import {HTMLBox, HTMLBoxView} from "@bokehjs/models/layouts/html_box"

export class PyIodideView extends HTMLBoxView {
  model: PyIodide

  override async lazy_initialize(): Promise<void> {
    super.lazy_initialize()
    if (!(window as any).pyiodide) {
      (window as any).pyiodide = await (window as any).loadPyodide({
	indexURL : "https://cdn.jsdelivr.net/pyodide/v0.19.0/full/"
      });
    }
  }

  render(): void {
    if (!(window as any).pyiodide) { return }
    (window as any).pyiodide.runPython(this.model.code)
  }
}

export namespace PyIodide {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    code: p.Property<string>
  }
}

export interface PyIodide extends PyIodide.Attrs {}

export class PyIodide extends HTMLBox {
  properties: PyIodide.Props

  constructor(attrs?: Partial<PyIodide.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.pyiodide"

  static init_PyIodide(): void {
    this.prototype.default_view = PyIodideView
    this.define<PyIodide.Props>(({String}) => ({
      code: [ String, '']
    }))
  }
}
