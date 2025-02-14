import type * as p from "@bokehjs/core/properties";
import { ColorMapper } from "@bokehjs/models/mappers/color_mapper";
import { HTMLBox, HTMLBoxView } from "../layout";
import type { VolumeType, Annotation } from "./util";
import { VTKAxes } from "./vtkaxes";
export declare abstract class AbstractVTKView extends HTMLBoxView {
    model: AbstractVTKPlot;
    protected _axes: any;
    protected _camera_callbacks: any[];
    protected _orientationWidget: any;
    protected _renderable: boolean;
    protected _setting_camera: boolean;
    protected _vtk_container: HTMLDivElement;
    protected _vtk_renwin: any;
    protected _widgetManager: any;
    protected _annotations_container: HTMLDivElement;
    protected _rendered: boolean;
    initialize(): void;
    _add_colorbars(): void;
    _init_annotations_container(): void;
    _clean_annotations(): void;
    _add_annotations(): void;
    connect_signals(): void;
    render(): void;
    after_layout(): void;
    invalidate_render(): void;
    remove(): void;
    abstract init_vtk_renwin(): void;
    abstract plot(): void;
    get _vtk_camera_state(): any;
    get _axes_canvas(): HTMLCanvasElement;
    _bind_key_events(): void;
    _create_orientation_widget(): void;
    _make_orientation_widget_interactive(): void;
    _delete_axes(): void;
    _get_camera_state(): void;
    _orientation_widget_visibility(visibility: boolean): void;
    _remove_default_key_binding(): void;
    _set_axes(): void;
    _set_camera_state(): void;
    _unsubscribe_camera_cb(): void;
    _vtk_render(): void;
}
export declare namespace AbstractVTKPlot {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        axes: p.Property<VTKAxes | null>;
        camera: p.Property<any>;
        data: p.Property<string | VolumeType | ArrayBuffer | null>;
        enable_keybindings: p.Property<boolean>;
        orientation_widget: p.Property<boolean>;
        color_mappers: p.Property<ColorMapper[]>;
        interactive_orientation_widget: p.Property<boolean>;
        annotations: p.Property<Annotation[] | null>;
    };
}
export interface AbstractVTKPlot extends AbstractVTKPlot.Attrs {
}
export declare abstract class AbstractVTKPlot extends HTMLBox {
    properties: AbstractVTKPlot.Props;
    renderer_el: any;
    static __module__: string;
    constructor(attrs?: Partial<AbstractVTKPlot.Attrs>);
    getActors(): any[];
}
//# sourceMappingURL=vtklayout.d.ts.map