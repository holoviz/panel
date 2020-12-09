import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import {div} from "@bokehjs/core/dom"
import * as p from "@bokehjs/core/properties";
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";
import {TableColumn} from "@bokehjs/models/widgets/tables"

import {transform_cds_to_records} from "./data"
import {PanelHTMLBoxView, set_size} from "./layout"


declare const Tabulator: any;

// The view of the Bokeh extension/ HTML element
// Here you can define how to render the model as well as react to model changes or View events.
export class DataTabulatorView extends PanelHTMLBoxView {
  model: DataTabulator;
  tabulator: any;
  _tabulator_cell_updating: boolean=false;
  _selection_updating: boolean=false;
  _styled_cells: any[] = []
  _initializing: boolean

  connect_signals(): void {
    super.connect_signals()

    const resize = () => {
      this.render()
      this.root.compute_layout() // XXX: invalidate_layout?
    }

    const {configuration, layout, columns} = this.model.properties;
    this.on_change([configuration, layout, columns], () => resize())

    this.connect(this.model.properties.page_size.change, () => {
      this.setPageSize();
    })

    this.connect(this.model.properties.page.change, () => {
      this.setPage();
    })

    this.connect(this.model.properties.max_page.change, () => {
      this.setMaxPage();
    })

    this.connect(this.model.properties.frozen_rows.change, () => {
      this.freezeRows()
    })

    this.connect(this.model.properties.styles.change, () => {
      this.updateStyles()
    })

    this.connect(this.model.source.properties.data.change, () => {
      this.setData();
    })
    this.connect(this.model.source.streaming, () => this.addData())
    this.connect(this.model.source.patching, () => this.updateOrAddData())
    this.connect(this.model.source.selected.change, () => this.updateSelection())
    this.connect(this.model.source.selected.properties.indices.change, () => this.updateSelection())
  }

  render(): void {
    super.render()
    this._initializing = true
    const container = div({class: "pnx-tabulator"});
    set_size(container, this.model)
    let configuration = this.getConfiguration();
    this.tabulator = new Tabulator(container, configuration)

    // Patch the ajax request method
    const ajax = this.tabulator.modules.ajax
    this.tabulator.modules.ajax.sendRequest = () => this.requestPage(ajax.params.page)

    // Set up page
    if (this.model.pagination) {
      this.setMaxPage()
      this.setData()
    } else {
      this.freezeRows()
    }
    this.el.appendChild(container)
  }

  requestPage(page: number): Promise<void> {
    return new Promise((resolve: any, reject: any) => {
      try {
        this.model.page = page || 1
        resolve({data: [], last_page: this.model.max_page})
      } catch(err) {
        reject(err)
      }
    })
  }

  renderComplete(): void {
    // Only have to set up styles after initial render subsequent
    // styling is handled by change event on styles property
    if (this._initializing) {
      this.updateStyles()
      this.updateSelection()
    }
    this._initializing = false
  }

  freezeRows(): void {
    for (const row of this.model.frozen_rows) {
      this.tabulator.getRow(row).freeze()
    }
  }

  getLayout(): string {
    let layout = this.model.layout
    switch (layout) {
      case "fit_data":
        return "fitData"
      case "fit_data_fill":
        return "fitDataFill"
      case "fit_data_stretch":
        return "fitDataStretch"
      case "fit_data_table":
        return "fitDataTable"
      case "fit_columns":
        return "fitColumns"
    }
  }

  getConfiguration(): any {
    let configuration = {
      ...this.model.configuration,
      index: "_index",
      renderComplete: () => this.renderComplete(),
      rowSelectionChanged: (data: any, rows: any) => this.rowSelectionChanged(data, rows),
      cellEdited: (cell: any) => this.cellEdited(cell),
      columns: this.getColumns(),
      layout: this.getLayout(),
      ajaxURL: "http://panel.pyviz.org",
      pagination: this.model.pagination,
      paginationSize: this.model.page_size,
      paginationInitialPage: null,
    }
    let data = this.model.source;
    if (data === null || Object.keys(data.data).length===0)
      return configuration;
    else {
      data = transform_cds_to_records(data, true)
      return {
        ...configuration,
        "data": data,
      }
    }
  }

  getColumns(): any {
    const config_columns: (any[] | undefined) = this.model.configuration?.columns;
    let columns = []
    if (config_columns != null) {
      for (const column of config_columns)
        if (column.columns != null) {
          const group_columns = []
          for (const col of column.columns)
            group_columns.push({...col})
          columns.push({...column, columns: group_columns})
        } else {
          columns.push({...column})
        }
    }
    for (const column of this.model.columns) {
      let tab_column: any = null
      if (config_columns != null) {
        for (const col of columns) {
          if (col.columns != null) {
            for (const c of col.columns) {
              if (column.field === c.field) {
                tab_column = c
                break
              }
            }
            if (tab_column != null)
              break
          } else if (column.field === col.field) {
            tab_column = col
            break
          }
        }
      }
      if (tab_column == null)
        tab_column = {field: column.field}
      if (tab_column.title == null)
        tab_column.title = column.title
      if (tab_column.width == null && column.width != null)
        tab_column.width = column.width
      if (tab_column.formatter == null && column.formatter != null) {
        const formatter: any = column.formatter
        const ftype = formatter.type
        if (ftype === "BooleanFormatter")
          tab_column.formatter = "tickCross"
        else {
          tab_column.formatter = (cell: any) => {
            return column.formatter.doFormat(cell.getRow(), cell, cell.getValue(), null, null)
          }
        }
      }

      const editor: any = column.editor
      const ctype = editor.type
      if (tab_column.editor != null) {
      } else if (ctype === "StringEditor") {
        if (editor.completions) {
          tab_column.editor = "autocomplete"
          tab_column.editorParams = {values: editor.completions}
        } else
          tab_column.editor = "input"
      } else if (ctype === "TextEditor")
        tab_column.editor = "textarea"
      else if (ctype === "IntEditor" || ctype === "NumberEditor") {
        tab_column.editor = "number"
        tab_column.editorParams = {step: editor.step}
      } else if (ctype === "CheckboxEditor") {
        tab_column.editor = "tickCross"
      } else if (ctype === "SelectEditor") {
        tab_column.editor = "select"
        tab_column.editorParams = {values: editor.options}
      } else {
        tab_column.editor = (cell: any, onRendered: any, success: any, cancel: any) => this.renderEditor(column, cell, onRendered, success, cancel)
      }
      if (config_columns == null)
        columns.push(tab_column)
    }
    return columns
  }

  renderEditor(column: any, cell: any, onRendered: any, success: any, error: any): any {
    const editor = column.editor
    const view = new editor.default_view({column: column, model: editor, parent: this, container: cell._cell.element})
    view.initialize()
    view.connect_signals()
    onRendered(() => {
      view.setValue(cell.getValue())
    })

    view.inputEl.addEventListener('change', () => {
      const value = view.serializeValue()
      const old_value = cell.getValue()
      const validation = view.validate()
      if (!validation.valid)
        error(validation.msg)
      if (old_value != null && typeof value != typeof old_value)
        error("Mismatching type")
      else
        success(view.serializeValue())
    });

    return view.inputEl
  }

  after_layout(): void {
    super.after_layout()
    this.tabulator.redraw(true)
    this.updateStyles()
  }

  // Update table

  setData(): void {
    const data = transform_cds_to_records(this.model.source, true);
    if (this.model.pagination != null)
      this.tabulator.rowManager.setData(data, true, false)
    else
      this.tabulator.setData(data);
    this.freezeRows()
    this.updateSelection()
  }

  updateStyles(): void {
    for (const cell_el of this._styled_cells)
      cell_el.cssText = ""
    this._styled_cells = []
    if (this.model.styles == null || this.tabulator.getDataCount() == 0)
      return
    for (const r in this.model.styles) {
      const row_style = this.model.styles[r]
      const row = this.tabulator.getRow(r)
      if (!row)
        continue
      const cells = row._row.cells
      for (const c in row_style) {
        const style = row_style[c]
        const cell = cells[c]
        if (cell == null || !style.length)
          continue
        const element = cell.element
        this._styled_cells.push(element)
        element.cssText = ""
        for (const s of style) {
          if (!s.includes(':'))
            continue
          const [prop, value] = s.split(':')
          element.style.setProperty(prop, value.trimLeft())
        }
      }
    }
  }

  addData(): void {
    const rows = this.tabulator.rowManager.getRows();
    const last_row = rows[rows.length-1]

    let data = transform_cds_to_records(this.model.source, true);
    this.tabulator.setData(data);
    if (this.model.follow) {
      this.tabulator.scrollToRow((last_row.data._index || 0)+1, "top", false);
    }
    this.freezeRows()
    this.updateSelection()
  }

  updateOrAddData(): void {
    // To avoid double updating the tabulator data
    if (this._tabulator_cell_updating)
      return

    let data = transform_cds_to_records(this.model.source, true);
    this.tabulator.setData(data);
    this.freezeRows()
    this.updateSelection()
  }

  setMaxPage(): void {
    this.tabulator.setMaxPage(this.model.max_page)
    this.tabulator.modules.page._setPageButtons()
  }

  setPage(): void {
    this.tabulator.setPage(this.model.page)
  }

  setPageSize(): void {
    this.tabulator.setPageSize(this.model.page_size)
  }

  updateSelection(): void {
    if (this.tabulator == null || this._selection_updating)
      return

    const indices = this.model.source.selected.indices;
    this._selection_updating = true
    this.tabulator.deselectRow()
    this.tabulator.selectRow(indices)
    this._selection_updating = false
  }

  // Update model

  rowSelectionChanged(data: any, _: any): void {
    if (this._selection_updating || this._initializing)
      return
    this._selection_updating = true
    const indices: any = data.map((row: any) => row._index)
    this.model.source.selected.indices = indices;
    this._selection_updating = false
  }

  cellEdited(cell: any): void {
    const field = cell._cell.column.field;
    const index = cell._cell.row.data._index;
    const value = cell._cell.value;
    this._tabulator_cell_updating = true
    this.model.source.patch({[field]: [[index, value]]});
    this._tabulator_cell_updating = false
  }

}

export namespace DataTabulator {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    columns: p.Property<TableColumn[]>
    configuration: p.Property<any>
    follow: p.Property<boolean>
    frozen_rows: p.Property<number[]>
    layout: p.Property<"fit_data" | "fit_data_fill" | "fit_data_stretch" | "fit_data_table" | "fit_columns">
    max_page: p.Property<number>
    page: p.Property<number>
    page_size: p.Property<number>
    pagination: p.Property<string | null>
    source: p.Property<ColumnDataSource>,
    styles: p.Property<any>
  }
}

export interface DataTabulator extends DataTabulator.Attrs { }

// The Bokeh .ts model corresponding to the Bokeh .py model
export class DataTabulator extends HTMLBox {
  properties: DataTabulator.Props

  constructor(attrs?: Partial<DataTabulator.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.tabulator"

  static init_DataTabulator(): void {
    this.prototype.default_view = DataTabulatorView;

    this.define<DataTabulator.Props>({
      configuration: [p.Any, ],
      columns: [ p.Array, [] ],
      follow: [p.Boolean, ],
      frozen_rows: [ p.Array, []],
      layout: [ p.Any, "fit_data" ],
      max_page: [ p.Number, 0 ],
      pagination: [ p.String, null ],
      page: [ p.Number, 0],
      page_size: [ p.Number, 0],
      source: [ p.Any, ],
      styles: [ p.Any, ],
    })
  }
}
