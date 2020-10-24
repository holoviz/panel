// See https://docs.bokeh.org/en/latest/docs/reference/models/layouts.html
import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"
import {div} from "@bokehjs/core/dom"
// See https://docs.bokeh.org/en/latest/docs/reference/core/properties.html
import * as p from "@bokehjs/core/properties";
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";

export function set_size(el: HTMLElement, model: HTMLBox): void {
    let width_policy = model.width != null ? "fixed" : "fit"
    let height_policy = model.height != null ? "fixed" : "fit"
    const {sizing_mode} = model
    if (sizing_mode != null) {
      if (sizing_mode == "fixed")
        width_policy = height_policy = "fixed"
      else if (sizing_mode == "stretch_both")
        width_policy = height_policy = "max"
      else if (sizing_mode == "stretch_width")
        width_policy = "max"
      else if (sizing_mode == "stretch_height")
        height_policy = "max"
      else {
        switch (sizing_mode) {
        case "scale_width":
          width_policy = "max"
          height_policy = "min"
          break
        case "scale_height":
          width_policy = "min"
          height_policy = "max"
          break
        case "scale_both":
          width_policy = "max"
          height_policy = "max"
          break
        default:
          throw new Error("unreachable")
        }
      }
    }
    if (width_policy == "fixed" && model.width)
      el.style.width = model.width + "px";
    else if (width_policy == "max")
      el.style.width = "100%";

    if (height_policy == "fixed" && model.height)
      el.style.height = model.height + "px";
    else if (height_policy == "max")
      el.style.height = "100%";
  }

function transform_cds_to_records(cds: ColumnDataSource): any {
  const data: any = []
  const columns = cds.columns()
  const cdsLength = cds.get_length()
  if (columns.length === 0||cdsLength === null) {
    return [];
  }
  for (let i = 0; i < cdsLength; i++) {
    const item: any = {}
    for (const column of columns) {
      let array: any = cds.get_array(column);
      const shape = array[0].shape == null ? null : array[0].shape;
      if ((shape != null) && (shape.length > 1) && (typeof shape[0] == "number"))
        item[column] = array.slice(i*shape[1], i*shape[1]+shape[1])
      else
        item[column] = array[i]
    }
    data.push(item)
  }
  return data
}

declare var Tabulator: any;
// declare const requirejs: any;
declare const require: any;

// The view of the Bokeh extension/ HTML element
// Here you can define how to render the model as well as react to model changes or View events.
export class TabulatorModelView extends HTMLBoxView {
    model: TabulatorModel;
    tabulator: any;
    _tabulator_cell_updating: boolean=false;
    // objectElement: any // Element

    connect_signals(): void {
        super.connect_signals()

        this.connect(this.model.properties.configuration.change, () => {
            this.render();
        })
        // this.connect(this.model.source.change, () => this.setData())
        this.connect(this.model.source.properties.data.change, () => {
          this.setData();
        })
        this.connect(this.model.source.streaming, () => this.addData())
        this.connect(this.model.source.patching, () => this.updateOrAddData())

        // this.connect(this.model.source.selected.change, () => this.updateSelection())
        this.connect(this.model.source.selected.properties.indices.change, () => this.updateSelection())
    }

    render(): void {
        super.render()
        const container = div({class: "pnx-tabulator"});
        set_size(container, this.model)
        let configuration = this.getConfiguration();
        // I'm working on getting this working in the notebook but have not yet found the solution
        // See [Issue 1529](https://github.com/holoviz/panel/issues/15299)
        if (typeof Tabulator === 'undefined'){
          // Tabulator=require("tabulator-tables")
          // requirejs(["https://unpkg.com/tabulator-tables"]);
          // Tabulator=requirejs("https://unpkg.com/tabulator-tables");
          console.log("Tabulator not loaded. See https://github.com/holoviz/panel/issues/15299");
        }
        this.tabulator = new Tabulator(container, configuration)
        this.el.appendChild(container)
    }

    getConfiguration(): any {
      // I refer to this via _view because this is the tabulator element when cellEdited is used
      let _view = this;

      function rowSelectionChanged(data: any, _: any): void {
        let indices: any = data.map((row: any) => row.index)
        _view.model.source.selected.indices = indices;
      }

      function startUpdating(): void {
        _view._tabulator_cell_updating = true;
      }
      function endUpdating(): void {
        _view._tabulator_cell_updating = false;
      }
      function cellEdited(cell: any){
        const field = cell._cell.column.field;
        const index = cell._cell.row.data.index;
        const value = cell._cell.value;
        startUpdating();
        _view.model.source.patch({[field]: [[index, value]]});
        _view.model._cell_change = {"c": field, "i": index, "v": value}
        endUpdating();
      }
      let default_configuration = {
        "rowSelectionChanged": rowSelectionChanged,
        "cellEdited": cellEdited,
        "index": "index",
      }

      let configuration = {
        ...this.model.configuration,
        ...default_configuration
      }
      let data = this.model.source;
      if (data ===null || Object.keys(data.data).length===0){
        return configuration;
      }
      else {
        data = transform_cds_to_records(data)
        return {
          ...configuration,
          "data": data,
        }
      }
    }

    after_layout(): void {
        super.after_layout()
        this.tabulator.redraw(true);
    }

    setData(): void {
      let data = transform_cds_to_records(this.model.source);
      this.tabulator.setData(data);
    }

    addData(): void {
      let data = transform_cds_to_records(this.model.source);
      this.tabulator.setData(data);
    }

    updateOrAddData(): void {
      // To avoid double updating the tabulator data
      if (this._tabulator_cell_updating===true){return;}

      let data = transform_cds_to_records(this.model.source);
      this.tabulator.setData(data);
    }

    updateSelection(): void {
      if (this.tabulator==null){return}

      let indices: number[]= this.model.source.selected.indices;
      let selectedRows: any = this.tabulator.getSelectedRows();

      for (let row of selectedRows){
        if (!indices.includes(row.getData().index)){
          row.toggleSelect();
        }
      }

      for (let index of indices){
        // Improve this
        // Maybe tabulator should use id as index?
        this.tabulator.selectRow(index);
      }
    }
}

export namespace TabulatorModel {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        configuration: p.Property<any>,
        source: p.Property<ColumnDataSource>,
        _cell_change: p.Property<any>,
    }
}

export interface TabulatorModel extends TabulatorModel.Attrs { }

// The Bokeh .ts model corresponding to the Bokeh .py model
export class TabulatorModel extends HTMLBox {
    properties: TabulatorModel.Props

    constructor(attrs?: Partial<TabulatorModel.Attrs>) {
        super(attrs)
    }

    static __module__ = "panel.models.tabulator_model"

    static init_TabulatorModel(): void {
        this.prototype.default_view = TabulatorModelView;

        this.define<TabulatorModel.Props>({
            configuration: [p.Any, ],
            source: [p.Any, ],
            _cell_change: [p.Any, ],
        })
    }
}
