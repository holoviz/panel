// Bokeh model for perspective-viewer
// See https://github.com/finos/perspective/tree/master/packages/perspective-viewer

// See https://docs.bokeh.org/en/latest/docs/reference/models/layouts.html
import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"
import {div} from "@bokehjs/core/dom"
// See https://docs.bokeh.org/en/latest/docs/reference/core/properties.html
import * as p from "@bokehjs/core/properties";
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";
import {set_size, transform_cds_to_records} from "./shared";

declare var $: any;
// The view of the Bokeh extension/ HTML element
// Here you can define how to render the model as well as react to model changes or View events.
export class PivotTableView extends HTMLBoxView {
    model: PivotTable;
    container: any;
    pivot_table_element: any;

    connect_signals(): void {
        super.connect_signals()

        this.connect(this.model.source.properties.data.change, this.setData);
    }

    render(): void {
        super.render()
        this.container = div({class: "pnx-pivot-table"});
        set_size(this.container, this.model)
        this.el.appendChild(this.container)
        this.setData();
    }

    setData(): void {
      let data = transform_cds_to_records(this.model.source);
      this.pivot_table_element=$(this.container);
      this.pivot_table_element.pivotUI(
        data, {});
    }

  }

export namespace PivotTable {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        source: p.Property<ColumnDataSource>,
        source_stream: p.Property<ColumnDataSource>,
        source_patch: p.Property<ColumnDataSource>,
    }
}

export interface PivotTable extends PivotTable.Attrs { }

// The Bokeh .ts model corresponding to the Bokeh .py model
export class PivotTable extends HTMLBox {
    properties: PivotTable.Props

    constructor(attrs?: Partial<PivotTable.Attrs>) {
        super(attrs)
    }

    static __module__ = "panel.models.pivot_table"

    static init_PivotTable(): void {
        this.prototype.default_view = PivotTableView;

        this.define<PivotTable.Props>({
            source: [p.Any, ],
            source_stream: [p.Any, ],
            source_patch: [p.Any, ],
        })
    }
}
