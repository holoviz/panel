import { AbstractVTKPlot, AbstractVTKView } from "./vtklayout";
import { Interpolation, vtkns, data2VTKImageData, hexToRGB, vtkLutToMapper, } from "./util";
export class VTKVolumePlotView extends AbstractVTKView {
    static __name__ = "VTKVolumePlotView";
    _controllerWidget;
    _vtk_image_data;
    connect_signals() {
        super.connect_signals();
        const { data, colormap, shadow, sampling, edge_gradient, rescale, ambient, diffuse, camera, specular, specular_power, display_volume, display_slices, slice_i, slice_j, slice_k, render_background, interpolation, controller_expanded, nan_opacity, } = this.model.properties;
        this.on_change(data, () => {
            this._vtk_image_data = data2VTKImageData(this.model.data);
            this.invalidate_render();
        });
        this.on_change(colormap, () => {
            this.colormap_selector.value = this.model.colormap;
            const event = new Event("change");
            this.colormap_selector.dispatchEvent(event);
        });
        this.on_change(shadow, () => {
            this.shadow_selector.value = this.model.shadow ? "1" : "0";
            const event = new Event("change");
            this.shadow_selector.dispatchEvent(event);
        });
        this.on_change(sampling, () => {
            this.sampling_slider.value = this.model.sampling.toFixed(2);
            const event = new Event("input");
            this.sampling_slider.dispatchEvent(event);
        });
        this.on_change(edge_gradient, () => {
            this.edge_gradient_slider.value = this.model.edge_gradient.toFixed(2);
            const event = new Event("input");
            this.edge_gradient_slider.dispatchEvent(event);
        });
        this.on_change(rescale, () => {
            this._controllerWidget.setRescaleColorMap(this.model.rescale);
            this._vtk_renwin.getRenderWindow().render();
        });
        this.on_change(ambient, () => {
            this.volume.getProperty().setAmbient(this.model.ambient);
            this._vtk_renwin.getRenderWindow().render();
        });
        this.on_change(diffuse, () => {
            this.volume.getProperty().setDiffuse(this.model.diffuse);
            this._vtk_renwin.getRenderWindow().render();
        });
        this.on_change(camera, () => {
            if (!this._setting_camera) {
                this._set_camera_state();
                this._vtk_renwin.getRenderWindow().render();
            }
        });
        this.on_change(specular, () => {
            this.volume.getProperty().setSpecular(this.model.specular);
            this._vtk_renwin.getRenderWindow().render();
        });
        this.on_change(specular_power, () => {
            this.volume.getProperty().setSpecularPower(this.model.specular_power);
            this._vtk_renwin.getRenderWindow().render();
        });
        this.on_change(display_volume, () => {
            this._set_volume_visibility(this.model.display_volume);
            this._vtk_renwin.getRenderWindow().render();
        });
        this.on_change(display_slices, () => {
            this._set_slices_visibility(this.model.display_slices);
            this._vtk_renwin.getRenderWindow().render();
        });
        this.on_change(slice_i, () => {
            if (this.image_actor_i !== undefined) {
                this.image_actor_i.getMapper().setISlice(this.model.slice_i);
                this._vtk_renwin.getRenderWindow().render();
            }
        });
        this.on_change(slice_j, () => {
            if (this.image_actor_j !== undefined) {
                this.image_actor_j.getMapper().setJSlice(this.model.slice_j);
                this._vtk_renwin.getRenderWindow().render();
            }
        });
        this.on_change(slice_k, () => {
            if (this.image_actor_k !== undefined) {
                this.image_actor_k.getMapper().setKSlice(this.model.slice_k);
                this._vtk_renwin.getRenderWindow().render();
            }
        });
        this.on_change(render_background, () => {
            this._vtk_renwin
                .getRenderer()
                .setBackground(...hexToRGB(this.model.render_background));
            this._vtk_renwin.getRenderWindow().render();
        });
        this.on_change(interpolation, () => {
            this._set_interpolation(this.model.interpolation);
            this._vtk_renwin.getRenderWindow().render();
        });
        this.on_change(controller_expanded, () => {
            if (this._controllerWidget != null) {
                this._controllerWidget.setExpanded(this.model.controller_expanded);
            }
        });
        this.on_change(nan_opacity, () => {
            const scalar_opacity = this.image_actor_i.getProperty().getScalarOpacity();
            scalar_opacity.get(["nodes"]).nodes[0].y = this.model.nan_opacity;
            scalar_opacity.modified();
            this._vtk_renwin.getRenderWindow().render();
        });
    }
    render() {
        this._vtk_renwin = null;
        this._orientationWidget = null;
        this._axes = null;
        super.render();
        this._create_orientation_widget();
        this._set_axes();
        this._vtk_renwin.getRenderer().resetCamera();
        if (Object.keys(this.model.camera).length > 0) {
            this._set_camera_state();
        }
        this._get_camera_state();
    }
    invalidate_render() {
        this._vtk_renwin = null;
        super.invalidate_render();
    }
    init_vtk_renwin() {
        this._vtk_renwin = vtkns.FullScreenRenderWindow.newInstance({
            rootContainer: this.shadow_el,
            container: this._vtk_container,
        });
    }
    plot() {
        this._controllerWidget = vtkns.VolumeController.newInstance({
            size: [400, 150],
            rescaleColorMap: this.model.rescale,
        });
        this._plot_volume();
        this._plot_slices();
        this._controllerWidget.setupContent(this._vtk_renwin.getRenderWindow(), this.volume, true);
        this._controllerWidget.setContainer(this.el);
        this._controllerWidget.setExpanded(this.model.controller_expanded);
        this._connect_js_controls();
        this._vtk_renwin.getRenderWindow().getInteractor();
        this._vtk_renwin.getRenderWindow().getInteractor().setDesiredUpdateRate(45);
        this._set_volume_visibility(this.model.display_volume);
        this._set_slices_visibility(this.model.display_slices);
        this._vtk_renwin
            .getRenderer()
            .setBackground(...hexToRGB(this.model.render_background));
        this._set_interpolation(this.model.interpolation);
        this._set_camera_state();
    }
    get vtk_image_data() {
        if (!this._vtk_image_data) {
            this._vtk_image_data = data2VTKImageData(this.model.data);
        }
        return this._vtk_image_data;
    }
    get volume() {
        return this._vtk_renwin.getRenderer().getVolumes()[0];
    }
    get image_actor_i() {
        return this._vtk_renwin.getRenderer().getActors()[0];
    }
    get image_actor_j() {
        return this._vtk_renwin.getRenderer().getActors()[1];
    }
    get image_actor_k() {
        return this._vtk_renwin.getRenderer().getActors()[2];
    }
    get shadow_selector() {
        return this.el.querySelector(".js-shadow");
    }
    get edge_gradient_slider() {
        return this.el.querySelector(".js-edge");
    }
    get sampling_slider() {
        return this.el.querySelector(".js-spacing");
    }
    get colormap_selector() {
        return this.el.querySelector(".js-color-preset");
    }
    _connect_js_controls() {
        const { el: controller_el } = this._controllerWidget.get("el");
        if (controller_el !== undefined) {
            const controller_button = controller_el.querySelector(".js-button");
            controller_button.addEventListener("click", () => this.model.controller_expanded = this._controllerWidget.getExpanded());
        }
        // Colormap selector
        this.colormap_selector.addEventListener("change", () => {
            this.model.colormap = this.colormap_selector.value;
        });
        if (!this.model.colormap) {
            this.model.colormap = this.colormap_selector.value;
        }
        else {
            this.model.properties.colormap.change.emit();
        }
        // Shadow selector
        this.shadow_selector.addEventListener("change", () => {
            this.model.shadow = !!Number(this.shadow_selector.value);
        });
        if ((this.model.shadow = !!Number(this.shadow_selector.value))) {
            this.model.properties.shadow.change.emit();
        }
        // Sampling slider
        this.sampling_slider.addEventListener("input", () => {
            const js_sampling_value = Number(this.sampling_slider.value);
            if (Math.abs(this.model.sampling - js_sampling_value) >= 5e-3) {
                this.model.sampling = js_sampling_value;
            }
        });
        if (Math.abs(this.model.sampling - Number(this.shadow_selector.value)) >= 5e-3) {
            this.model.properties.sampling.change.emit();
        }
        // Edge Gradient slider
        this.edge_gradient_slider.addEventListener("input", () => {
            const js_edge_gradient_value = Number(this.edge_gradient_slider.value);
            if (Math.abs(this.model.edge_gradient - js_edge_gradient_value) >= 5e-3) {
                this.model.edge_gradient = js_edge_gradient_value;
            }
        });
        if (Math.abs(this.model.edge_gradient - Number(this.edge_gradient_slider.value)) >= 5e-3) {
            this.model.properties.edge_gradient.change.emit();
        }
    }
    _plot_slices() {
        const source = this._vtk_image_data;
        const image_actor_i = vtkns.ImageSlice.newInstance();
        const image_actor_j = vtkns.ImageSlice.newInstance();
        const image_actor_k = vtkns.ImageSlice.newInstance();
        const image_mapper_i = vtkns.ImageMapper.newInstance();
        const image_mapper_j = vtkns.ImageMapper.newInstance();
        const image_mapper_k = vtkns.ImageMapper.newInstance();
        image_mapper_i.setInputData(source);
        image_mapper_i.setISlice(this.model.slice_i);
        image_actor_i.setMapper(image_mapper_i);
        image_mapper_j.setInputData(source);
        image_mapper_j.setJSlice(this.model.slice_j);
        image_actor_j.setMapper(image_mapper_j);
        image_mapper_k.setInputData(source);
        image_mapper_k.setKSlice(this.model.slice_k);
        image_actor_k.setMapper(image_mapper_k);
        // set_color and opacity
        const piecewiseFunction = vtkns.PiecewiseFunction.newInstance();
        const lookupTable = this.volume.getProperty().getRGBTransferFunction(0);
        const range = this.volume.getMapper().getInputData().getPointData().getScalars().getRange();
        piecewiseFunction.removeAllPoints();
        piecewiseFunction.addPoint(range[0] - 1, this.model.nan_opacity);
        piecewiseFunction.addPoint(range[0], 1);
        piecewiseFunction.addPoint(range[1], 1);
        const property = image_actor_i.getProperty();
        image_actor_j.setProperty(property);
        image_actor_k.setProperty(property);
        property.setRGBTransferFunction(lookupTable);
        property.setScalarOpacity(piecewiseFunction);
        const renderer = this._vtk_renwin.getRenderer();
        renderer.addActor(image_actor_i);
        renderer.addActor(image_actor_j);
        renderer.addActor(image_actor_k);
    }
    _plot_volume() {
        //Create vtk volume and add it to the scene
        const source = this.vtk_image_data;
        const actor = vtkns.Volume.newInstance();
        const mapper = vtkns.VolumeMapper.newInstance();
        actor.setMapper(mapper);
        mapper.setInputData(source);
        const dataArray = source.getPointData().getScalars() || source.getPointData().getArrays()[0];
        const dataRange = dataArray.getRange();
        const lookupTable = vtkns.ColorTransferFunction.newInstance();
        if (this.model.colormap != null) {
            const preset = vtkns.ColorTransferFunction.vtkColorMaps.getPresetByName(this.model.colormap);
            lookupTable.applyColorMap(preset);
        }
        lookupTable.onModified(() => (this.model.mapper = vtkLutToMapper(lookupTable)));
        const piecewiseFunction = vtkns.PiecewiseFunction.newInstance();
        const sampleDistance = 0.7 *
            Math.sqrt(source
                .getSpacing()
                .map((v) => v * v)
                .reduce((a, b) => a + b, 0));
        mapper.setSampleDistance(sampleDistance);
        actor.getProperty().setRGBTransferFunction(0, lookupTable);
        actor.getProperty().setScalarOpacity(0, piecewiseFunction);
        actor.getProperty().setInterpolationTypeToFastLinear();
        // actor.getProperty().setInterpolationTypeToLinear();
        // For better looking volume rendering
        // - distance in world coordinates a scalar opacity of 1.0
        actor
            .getProperty()
            .setScalarOpacityUnitDistance(0, vtkns.BoundingBox.getDiagonalLength(source.getBounds()) /
            Math.max(...source.getDimensions()));
        // - control how we emphasize surface boundaries
        //  => max should be around the average gradient magnitude for the
        //     volume or maybe average plus one std dev of the gradient magnitude
        //     (adjusted for spacing, this is a world coordinate gradient, not a
        //     pixel gradient)
        //  => max hack: (dataRange[1] - dataRange[0]) * 0.05
        actor.getProperty().setGradientOpacityMinimumValue(0, 0);
        actor
            .getProperty()
            .setGradientOpacityMaximumValue(0, (dataRange[1] - dataRange[0]) * 0.05);
        // - Use shading based on gradient
        actor.getProperty().setShade(this.model.shadow);
        actor.getProperty().setUseGradientOpacity(0, true);
        // - generic good default
        actor.getProperty().setGradientOpacityMinimumOpacity(0, 0.0);
        actor.getProperty().setGradientOpacityMaximumOpacity(0, 1.0);
        actor.getProperty().setAmbient(this.model.ambient);
        actor.getProperty().setDiffuse(this.model.diffuse);
        actor.getProperty().setSpecular(this.model.specular);
        actor.getProperty().setSpecularPower(this.model.specular_power);
        this._vtk_renwin.getRenderer().addVolume(actor);
    }
    _set_interpolation(interpolation) {
        if (interpolation == "fast_linear") {
            this.volume.getProperty().setInterpolationTypeToFastLinear();
            this.image_actor_i.getProperty().setInterpolationTypeToLinear();
        }
        else if (interpolation == "linear") {
            this.volume.getProperty().setInterpolationTypeToLinear();
            this.image_actor_i.getProperty().setInterpolationTypeToLinear();
        }
        else {
            //nearest
            this.volume.getProperty().setInterpolationTypeToNearest();
            this.image_actor_i.getProperty().setInterpolationTypeToNearest();
        }
    }
    _set_slices_visibility(visibility) {
        this.image_actor_i.setVisibility(visibility);
        this.image_actor_j.setVisibility(visibility);
        this.image_actor_k.setVisibility(visibility);
    }
    _set_volume_visibility(visibility) {
        this.volume.setVisibility(visibility);
    }
}
export class VTKVolumePlot extends AbstractVTKPlot {
    static __name__ = "VTKVolumePlot";
    constructor(attrs) {
        super(attrs);
    }
    static {
        this.prototype.default_view = VTKVolumePlotView;
        this.define(({ Any, Array, Boolean, Int, Number, String, Struct }) => ({
            ambient: [Number, 0.2],
            colormap: [String],
            data: [Any],
            diffuse: [Number, 0.7],
            display_slices: [Boolean, false],
            display_volume: [Boolean, true],
            edge_gradient: [Number, 0.2],
            interpolation: [Interpolation, "fast_linear"],
            mapper: [Struct({ palette: Array(String), low: Number, high: Number }), { palette: [], low: 0, high: 0 }],
            nan_opacity: [Number, 1],
            render_background: [String, "#52576e"],
            rescale: [Boolean, false],
            sampling: [Number, 0.4],
            shadow: [Boolean, true],
            slice_i: [Int, 0],
            slice_j: [Int, 0],
            slice_k: [Int, 0],
            specular: [Number, 0.3],
            specular_power: [Number, 8.0],
            controller_expanded: [Boolean, true],
        }));
        this.override({
            height: 300,
            width: 300,
        });
    }
}
//# sourceMappingURL=vtkvolume.js.map