import type * as p from "@bokehjs/core/properties";
import { AbstractVTKView, AbstractVTKPlot } from "./vtklayout";
export declare class VTKJSPlotView extends AbstractVTKView {
    model: VTKJSPlot;
    connect_signals(): void;
    render(): void;
    invalidate_render(): void;
    init_vtk_renwin(): void;
    plot(): void;
}
export declare namespace VTKJSPlot {
    type Attrs = p.AttrsOf<Props>;
    type Props = AbstractVTKPlot.Props & {
        data_url: p.Property<string | null>;
    };
}
export interface VTKJSPlot extends VTKJSPlot.Attrs {
}
export declare class VTKJSPlot extends AbstractVTKPlot {
    properties: VTKJSPlot.Props;
}
//# sourceMappingURL=vtkjs.d.ts.map