// See https://docs.bokeh.org/en/latest/docs/reference/models/layouts.html
import { HTMLBox, HTMLBoxView } from "@bokehjs/models/layouts/html_box"

// See https://docs.bokeh.org/en/latest/docs/reference/core/properties.html
import * as p from "@bokehjs/core/properties"
import { canvas, div } from "@bokehjs/core/dom";

// Used to set size when no options specified
const responsiveOptions = {
    responsive: true,
    maintainAspectRatio: false,
}

// The view of the Bokeh extension/ HTML element
// Here you can define how to render the model as well as react to model changes or View events.
export class ChartJSView extends HTMLBoxView {
    model: ChartJS
    objectElement: any // Element

    connect_signals(): void {
        super.connect_signals()

        this.connect(this.model.properties.data.change, () => {
            this.render();
        })
    }

    render(): void {
        super.render()
        var chartContainer = div({class: "chartjs-container", style: "position: relative; height:100%; width:100%"})
        var chartCanvas = canvas({class: "chartjs"})
        chartContainer.appendChild(chartCanvas)
        var ctx: any = chartCanvas.getContext('2d');
        new (window as any).Chart(ctx, {options: responsiveOptions, ...this.model.data});

        this.el.appendChild(chartContainer)
    }
}

export namespace ChartJS {
    export type Attrs = p.AttrsOf<Props>
    export type Props = HTMLBox.Props & {
        data: p.Property<any>
    }
}

export interface ChartJS extends ChartJS.Attrs { }

// The Bokeh .ts model corresponding to the Bokeh .py model
export class ChartJS extends HTMLBox {
    properties: ChartJS.Props

    constructor(attrs?: Partial<ChartJS.Attrs>) {
        super(attrs)
    }

    static __module__ = "panel.models.chartjs"

    static init_ChartJS(): void {
        this.prototype.default_view = ChartJSView;

        this.define<ChartJS.Props>(({Any}) => ({
            data:     [ Any,           {} ]
          }))
    }
}