import {isArray} from "@bokehjs/core/util/types"
import {HTMLBox} from "@bokehjs/models/layouts/html_box"
import {div} from "@bokehjs/core/dom"
import {Enum} from "@bokehjs/core/kinds"
import * as p from "@bokehjs/core/properties";
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";
import {TableColumn} from "@bokehjs/models/widgets/tables"

import {debounce} from  "debounce"

import {transform_cds_to_records} from "./data"
import {PanelHTMLBoxView, set_size} from "./layout"


declare const Tabulator: any;

function find_group(key: any, value: string, records: any[]): any {
  for (const record of records) {
    if (record[key] == value)
      return record
  }
  return null
}

function summarize(grouped: any[], columns: any[], aggregators: string[], depth: number = 0): any {
  const summary: any = {}
  if (grouped.length == 0)
    return summary
  const agg = aggregators[depth]
  for (const group of grouped) {
    const subsummary = summarize(group._children, columns, aggregators, depth+1)
    for (const col in subsummary) {
      if (isArray(subsummary[col]))
        group[col] = subsummary[col].reduce((a: any, b: any) => a + b, 0) / subsummary[col].length
      else
        group[col] = subsummary[col]
    }
    for (const column of columns.slice(1)) {
      const val = group[column.field]
      if (column.field in summary) {
        const old_val = summary[column.field]
        if (agg === 'min')
          summary[column.field] = Math.min(val, old_val)
        else if (agg === 'max')
          summary[column.field] = Math.max(val, old_val)
        else if (agg === 'sum')
          summary[column.field] = val + old_val
        else if (agg === 'mean') {
          if (isArray(summary[column.field]))
            summary[column.field].push(val)
          else
            summary[column.field] = [old_val, val]
        }
      } else
        summary[column.field] = val
    }
  }
  return summary
}

function group_data(records: any[], columns: any[], indexes: string[], aggregators: any): any[] {
  const grouped = []
  const index_field = columns[0].field
  for (const record of records) {
    const value = record[indexes[0]]
    let group = find_group(index_field, value, grouped)
    if (group == null) {
      group = {_children: []}
      group[index_field] = value
      grouped.push(group)
    }
    let subgroup = group
    const groups: any = {}
    for (const index of indexes.slice(1)) {
      subgroup = find_group(index_field, record[index], subgroup._children)
      if (subgroup == null) {
        subgroup = {_children: []}
        subgroup[index_field] = record[index]
        group._children.push(subgroup)
      }
      groups[index] = group
      for (const column of columns.slice(1))
        subgroup[column.field] = record[column]
      group = subgroup
    }
    for (const column of columns.slice(1))
      subgroup[column.field] = record[column.field]
  }
  const aggs = []
  for (const index of indexes)
    aggs.push((index in aggregators) ? aggregators[index] : 'sum')
  summarize(grouped, columns, aggs)
  return grouped
}


// The view of the Bokeh extension/ HTML element
// Here you can define how to render the model as well as react to model changes or View events.
export class DataTabulatorView extends PanelHTMLBoxView {
  model: DataTabulator;
  tabulator: any;
  _tabulator_cell_updating: boolean=false
  _data_updating: boolean = true
  _selection_updating: boolean =false
  _styled_cells: any[] = []
  _styles: any;
  _initializing: boolean

  connect_signals(): void {
    super.connect_signals()

    const {configuration, layout, columns, theme, groupby} = this.model.properties;
    this.on_change([configuration, layout, columns, groupby], () => this.render_and_resize())

    this.on_change([theme], () => this.setCSS())

    this.connect(this.model.properties.download.change, () => {
      const ftype = this.model.filename.endsWith('.json') ? "json" : "csv"
      this.tabulator.download(ftype, this.model.filename)
    })

    this.connect(this.model.properties.hidden_columns.change, () => {
      this.hideColumns()
    })

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
      this._styles = this.model.styles
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

  render_and_resize(): void {
    this.render()
    this.update_layout()
    this.compute_layout()
    if (this.root !== this)
      this.invalidate_layout()
  }

  render(): void {
    super.render()
    const wait = this.setCSS()
    if (wait)
      return
    this._initializing = true
    this._styles = this.model.styles
    const container = div({class: "pnx-tabulator"})
    set_size(container, this.model)
    let configuration = this.getConfiguration()

    this.tabulator = new Tabulator(container, configuration)

    // Swap pagination mode
    if (this.model.pagination === 'remote') {
      this.tabulator.options.pagination = this.model.pagination
      this.tabulator.modules.page.mode = 'remote'
    }

    this.setGroupBy()
    this.hideColumns()

    // Set up page
    if (this.model.pagination) {
      this.setMaxPage()
      this.tabulator.setPage(this.model.page)
      this.setData()
    } else {
      this.freezeRows()
    }
    this.el.appendChild(container)
  }

  tableInit(view: DataTabulatorView, tabulator: any): void {
    // Patch the ajax request and page data parsing methods
    const ajax = tabulator.modules.ajax
    ajax.sendRequest = () => {
      return view.requestPage(ajax.params.page, ajax.params.sorters)
    }
    tabulator.modules.page._parseRemoteData = () => {}
  }

  requestPage(page: number, sorters: any[]): Promise<void> {
    return new Promise((resolve: any, reject: any) => {
      try {
        if (page != null && sorters != null) {
          if (this._data_updating)
            this._data_updating = false
          else
            this.model.sorters = sorters
          this.model.page = page || 1
        }
        resolve([])
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
    for (const row of this.model.frozen_rows)
      this.tabulator.getRow(row).freeze()
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
    const pagination = this.model.pagination == 'remote' ? 'local': (this.model.pagination || false)
    // Only use selectable mode if explicitly requested otherwise manually handle selections
    let selectable = this.model.select_mode === 'toggle' ? true : NaN
    const that = this
    let configuration = {
      ...this.model.configuration,
      index: "_index",
      nestedFieldSeparator: false,
      selectable: selectable,
      tableBuilding: function() { that.tableInit(that, this) },
      renderComplete: () => this.renderComplete(),
      rowSelectionChanged: (data: any, rows: any) => this.rowSelectionChanged(data, rows),
      rowClick: (e: any, row: any) => this.rowClicked(e, row),
      cellEdited: (cell: any) => this.cellEdited(cell),
      columns: this.getColumns(),
      layout: this.getLayout(),
      pagination: pagination,
      paginationSize: this.model.page_size,
      paginationInitialPage: 1,
      selectableCheck: (row: any) => {
        const selectable = this.model.selectable_rows
        return (selectable == null) || (selectable.indexOf(row._row.data._index) >= 0)
      },
      tooltips: (cell: any) => {
        return  cell.getColumn().getField() + ": " + cell.getValue();
      },
      scrollVertical: debounce(() => {
        this.updateStyles()
      }, 50, false)
    }
    if (pagination) {
      configuration['ajaxURL'] = "http://panel.pyviz.org"
      configuration['ajaxSorting'] = true
    }
    const cds: any = this.model.source;
    let data: any[]
    if (cds === null || (cds.columns().length === 0))
      data = []
    else
      data = transform_cds_to_records(cds, true)
    if (configuration.dataTree)
      data = group_data(data, this.model.columns, this.model.indexes, this.model.aggregators)
    return {
      ...configuration,
      "data": data,
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
	  if (column.formatter === "rowSelection") {
	    column.cellClick = (_: any, cell: any) => {
	      cell.getRow().toggleSelect();
	    }
	  }
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
      if (tab_column.width == null && column.width != null && column.width != 0)
        tab_column.width = column.width
      if (tab_column.formatter == null && column.formatter != null) {
        const formatter: any = column.formatter
        const ftype = formatter.type
        if (ftype === "BooleanFormatter")
          tab_column.formatter = "tickCross"
        else {
          tab_column.formatter = (cell: any) => {
            const formatted = column.formatter.doFormat(cell.getRow(), cell, cell.getValue(), null, null)
            if (column.formatter.type === 'HTMLTemplateFormatter')
              return formatted
            const node = div()
            node.innerHTML = formatted
            return node.children[0].innerHTML
          }
        }
      }

      const editor: any = column.editor
      const ctype = editor.type
      if (tab_column.editor != null) {
      } else if (ctype === "StringEditor") {
        if (editor.completions.length > 0) {
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
      } else if (editor != null && editor.default_view != null) {
        tab_column.editor = (cell: any, onRendered: any, success: any, cancel: any) => this.renderEditor(column, cell, onRendered, success, cancel)
      }
      tab_column.editable = () => (this.model.editable && (editor.default_view != null))
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
    if (this.tabulator != null)
      this.tabulator.redraw(true)
    this.updateStyles()
  }

  // Update table

  setData(): void {
    let data = transform_cds_to_records(this.model.source, true);
    if (this.model.configuration.dataTree)
      data = group_data(data, this.model.columns, this.model.indexes, this.model.aggregators)
    this._data_updating = true
    if (this.model.pagination != null)
      this.tabulator.rowManager.setData(data, true, false)
    else {
      this.tabulator.setData(data)
      this._data_updating = false
    }
    this.freezeRows()
    this.updateSelection()
  }

  setGroupBy(): void {
    if (this.model.groupby.length == 0) {
      this.tabulator.setGroupBy(false)
      return
    }
    const groupby = (data: any) => {
      const groups = []
      for (const g of this.model.groupby) {
        const group = g + ': ' + data[g]
        groups.push(group)
      }
      return groups.join(', ')
    }
    this.tabulator.setGroupBy(groupby)
  }

  setCSS(): boolean {
    let theme: string
    if (this.model.theme == "default")
      theme = "tabulator"
    else
      theme = "tabulator_" + this.model.theme
    const css = this.model.theme_url + theme + ".min.css"

    let old_node: any = null
    const links = document.getElementsByTagName("link")
    const dist_index = this.model.theme_url.indexOf('dist/')
    const start_url = this.model.theme_url.slice(0, dist_index)
    for (const link of links) {
      if (link.href.indexOf(start_url) >= 0) {
        old_node = link
        break
      }
    }

    if (old_node != null) {
      if (old_node.href.endsWith(css))
        return false
      else {
        old_node.href = css
        setTimeout(() => this.render_and_resize(), 100)
        return true
      }
    }
    let parent_node = document.getElementsByTagName("head")[0]

    const css_node: any = document.createElement('link')
    css_node.type = 'text/css'
    css_node.rel = 'stylesheet'
    css_node.media = 'screen'
    css_node.href = css

    css_node.onload = () => {
      this.render_and_resize()
    }
    parent_node.appendChild(css_node)
    return true
  }

  updateStyles(): void {
    for (const cell_el of this._styled_cells)
      cell_el.cssText = ""
    this._styled_cells = []
    if (this._styles == null || this.tabulator == null || this.tabulator.getDataCount() == 0)
      return
    for (const r in this._styles) {
      const row_style = this._styles[r]
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
          let prop, value
          if (isArray(s))
            [prop, value] = s
          else if (!s.includes(':'))
            continue
          else
            [prop, value] = s.split(':')
          element.style.setProperty(prop, value.trimLeft())
        }
      }
    }
    const styles = this._styles
    this.model.styles = {}
    this._styles = styles
  }

  addData(): void {
    const rows = this.tabulator.rowManager.getRows()
    const last_row = rows[rows.length-1]
    const start = ((last_row?.data._index) || 0)
    this.setData()
    if (this.model.follow && last_row)
      this.tabulator.scrollToRow(start, "top", false)
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

  hideColumns(): void {
    for (const column of this.tabulator.getColumns()) {
      if (this.model.hidden_columns.indexOf(column._column.field) > -1)
        column.hide()
      else
        column.show()
    }
  }

  setMaxPage(): void {
    this.tabulator.setMaxPage(this.model.max_page)
    if (this.tabulator.modules.page.pagesElement)
      this.tabulator.modules.page._setPageButtons()
  }

  setPage(): void {
    this.tabulator.setPage(Math.min(this.model.max_page, this.model.page))
  }

  setPageSize(): void {
    this.tabulator.setPageSize(this.model.page_size)
  }

  updateSelection(): void {
    if (this.tabulator == null || this._selection_updating)
      return

    const indices = this.model.source.selected.indices;
    const current_indices: any = this.tabulator.getSelectedData().map((row: any) => row._index)
    if (JSON.stringify(indices) == JSON.stringify(current_indices))
      return
    this._selection_updating = true
    this.tabulator.deselectRow()
    this.tabulator.selectRow(indices)
    // This actually places the selected row at the top of the table
    this.tabulator.scrollToRow(indices[0], "bottom", false)
    this._selection_updating = false
  }

  // Update model

  rowClicked(e: any, row: any) {
    if (this._selection_updating || this._initializing || (typeof this.model.select_mode) === 'string' || this.model.select_mode === false)
      return
    let indices: number[] = []
    const selected = this.model.source.selected
    const index: number = row._row.data._index
    if (e.ctrlKey || e.metaKey) {
      indices = this.model.source.selected.indices
    } else if (e.shiftKey && selected.indices.length) {
      const start = selected.indices[selected.indices.length-1]
      if (index>start) {
        for (let i = start; i<index; i++)
          indices.push(i)
      } else {
        for (let i = start; i>index; i--)
          indices.push(i)
      }
    }
    if (indices.indexOf(index) < 0)
      indices.push(index)
    else
      indices.splice(indices.indexOf(index), 1)
    // Remove the first selected indices when selectable is an int.
    if (typeof this.model.select_mode === 'number') {
      while (indices.length > this.model.select_mode) {
        indices.shift()
      }
    }
    const filtered = this._filter_selected(indices)
    this.tabulator.deselectRow()
    this.tabulator.selectRow(filtered)
    this._selection_updating = true
    selected.indices = filtered
    this._selection_updating = false
  }

  _filter_selected(indices: number[]): number[] {
    const filtered = []
    for (const ind of indices) {
      if (this.model.selectable_rows == null ||
          this.model.selectable_rows.indexOf(ind) >= 0)
        filtered.push(ind)
    }
    return filtered
  }

  rowSelectionChanged(data: any, _: any): void {
    if (this._selection_updating || this._initializing || (typeof this.model.select_mode) === 'boolean' || (typeof this.model.select_mode) === 'number' || this.model.configuration.dataTree)
      return
    const indices: number[] = data.map((row: any) => row._index)
    const filtered = this._filter_selected(indices)
    this._selection_updating = indices.length === filtered.length
    this.model.source.selected.indices = filtered
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

export const TableLayout = Enum("fit_data", "fit_data_fill", "fit_data_stretch", "fit_data_table", "fit_columns")

export namespace DataTabulator {
  export type Attrs = p.AttrsOf<Props>
  export type Props = HTMLBox.Props & {
    aggregators: p.Property<any>
    columns: p.Property<TableColumn[]>
    configuration: p.Property<any>
    download: p.Property<boolean>
    filename: p.Property<string>
    editable: p.Property<boolean>
    follow: p.Property<boolean>
    frozen_rows: p.Property<number[]>
    groupby: p.Property<string[]>
    hidden_columns: p.Property<string[]>
    indexes: p.Property<string[]>
    layout: p.Property<typeof TableLayout["__type__"]>
    max_page: p.Property<number>
    page: p.Property<number>
    page_size: p.Property<number>
    pagination: p.Property<string | null>
    select_mode: p.Property<any>
    selectable_rows: p.Property<number[] | null>
    source: p.Property<ColumnDataSource>
    sorters: p.Property<any[]>
    styles: p.Property<any>
    theme: p.Property<string>
    theme_url: p.Property<string>
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

    this.define<DataTabulator.Props>(({Any, Array, Boolean, Nullable, Number, Ref, String}) => ({
      aggregators:    [ Any,                     {} ],
      configuration:  [ Any,                     {} ],
      columns:        [ Array(Ref(TableColumn)), [] ],
      download:       [ Boolean,               true ],
      editable:       [ Boolean,               true ],
      filename:       [ String,         "table.csv" ],
      follow:         [ Boolean,               true ],
      frozen_rows:    [ Array(Number),           [] ],
      groupby:        [ Array(String),           [] ],
      hidden_columns: [ Array(String),           [] ],
      indexes:        [ Array(String),           [] ],
      layout:         [ TableLayout,     "fit_data" ],
      max_page:       [ Number,                   0 ],
      pagination:     [ Nullable(String),      null ],
      page:           [ Number,                   0 ],
      page_size:      [ Number,                   0 ],
      select_mode:    [ Any,                   true ],
      selectable_rows: [ Nullable(Array(Number)), null ],
      source:         [ Ref(ColumnDataSource)       ],
      sorters:        [ Array(Any),              [] ],
      styles:         [ Any,                     {} ],
      theme:          [ String,            "simple" ],
      theme_url:      [ String, "https://unpkg.com/tabulator-tables@4.9.3/dist/css/"]
    }))
  }
}
