import type * as p from "@bokehjs/core/properties";
import { AbstractVTKPlot, AbstractVTKView } from "./vtklayout";
import type { ColorMapper } from "./util";
import { Interpolation } from "./util";
export declare class VTKVolumePlotView extends AbstractVTKView {
    model: VTKVolumePlot;
    protected _controllerWidget: any;
    protected _vtk_image_data: any;
    connect_signals(): void;
    render(): void;
    invalidate_render(): void;
    init_vtk_renwin(): void;
    plot(): void;
    get vtk_image_data(): any;
    get volume(): any;
    get image_actor_i(): any;
    get image_actor_j(): any;
    get image_actor_k(): any;
    get shadow_selector(): HTMLSelectElement;
    get edge_gradient_slider(): HTMLInputElement;
    get sampling_slider(): HTMLInputElement;
    get colormap_selector(): HTMLSelectElement;
    _connect_js_controls(): void;
    _plot_slices(): void;
    _plot_volume(): void;
    _set_interpolation(interpolation: Interpolation): void;
    _set_slices_visibility(visibility: boolean): void;
    _set_volume_visibility(visibility: boolean): void;
}
export declare namespace VTKVolumePlot {
    type Attrs = p.AttrsOf<Props>;
    type Props = AbstractVTKPlot.Props & {
        ambient: p.Property<number>;
        colormap: p.Property<string>;
        diffuse: p.Property<number>;
        display_slices: p.Property<boolean>;
        display_volume: p.Property<boolean>;
        edge_gradient: p.Property<number>;
        interpolation: p.Property<Interpolation>;
        mapper: p.Property<ColorMapper>;
        nan_opacity: p.Property<number>;
        render_background: p.Property<string>;
        rescale: p.Property<boolean>;
        sampling: p.Property<number>;
        shadow: p.Property<boolean>;
        slice_i: p.Property<number>;
        slice_j: p.Property<number>;
        slice_k: p.Property<number>;
        specular: p.Property<number>;
        specular_power: p.Property<number>;
        controller_expanded: p.Property<boolean>;
    };
}
export interface VTKVolumePlot extends VTKVolumePlot.Attrs {
}
export declare class VTKVolumePlot extends AbstractVTKPlot {
    properties: VTKVolumePlot.Props;
    constructor(attrs?: Partial<VTKVolumePlot.Attrs>);
}
//# sourceMappingURL=vtkvolume.d.ts.map