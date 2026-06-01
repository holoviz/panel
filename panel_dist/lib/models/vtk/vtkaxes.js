import { Model } from "@bokehjs/model";
import { mat4, vec3 } from "gl-matrix";
import { cartesian_product, vtkns } from "./util";
export class VTKAxes extends Model {
    static __name__ = "VTKAxes";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.vtk";
    static {
        this.define(({ Any, Array, Boolean, Number }) => ({
            origin: [Array(Number), [0, 0, 0]],
            xticker: [Any, null],
            yticker: [Any, null],
            zticker: [Any, null],
            digits: [Number, 1],
            show_grid: [Boolean, true],
            grid_opacity: [Number, 0.1],
            axes_opacity: [Number, 1],
            fontsize: [Number, 12],
        }));
    }
    get xticks() {
        if (this.xticker) {
            return this.xticker.ticks;
        }
        else {
            return [];
        }
    }
    get yticks() {
        if (this.yticker) {
            return this.yticker.ticks;
        }
        else {
            return [];
        }
    }
    get zticks() {
        if (this.zticker) {
            return this.zticker.ticks;
        }
        else {
            return [];
        }
    }
    get xlabels() {
        return this.xticker?.labels
            ? this.xticker.labels
            : this.xticks.map((elem) => elem.toFixed(this.digits));
    }
    get ylabels() {
        return this.yticker?.labels
            ? this.yticker.labels
            : this.yticks.map((elem) => elem.toFixed(this.digits));
    }
    get zlabels() {
        return this.zticker?.labels
            ? this.zticker.labels
            : this.zticks.map((elem) => elem.toFixed(this.digits));
    }
    _make_grid_lines(n, m, offset) {
        const out = [];
        for (let i = 0; i < n - 1; i++) {
            for (let j = 0; j < m - 1; j++) {
                const v0 = i * m + j + offset;
                const v1 = i * m + j + 1 + offset;
                const v2 = (i + 1) * m + j + 1 + offset;
                const v3 = (i + 1) * m + j + offset;
                const line = [5, v0, v1, v2, v3, v0];
                out.push(line);
            }
        }
        return out;
    }
    _create_grid_axes() {
        const pts = [];
        pts.push(cartesian_product(this.xticks, this.yticks, [this.origin[2]])); //xy
        pts.push(cartesian_product([this.origin[0]], this.yticks, this.zticks)); //yz
        pts.push(cartesian_product(this.xticks, [this.origin[1]], this.zticks)); //xz
        const polys = [];
        let offset = 0;
        polys.push(this._make_grid_lines(this.xticks.length, this.yticks.length, offset)); //xy
        offset += this.xticks.length * this.yticks.length;
        polys.push(this._make_grid_lines(this.yticks.length, this.zticks.length, offset)); //yz
        offset += this.yticks.length * this.zticks.length;
        polys.push(this._make_grid_lines(this.xticks.length, this.zticks.length, offset)); //xz
        const gridPolyData = window.vtk({
            vtkClass: "vtkPolyData",
            points: {
                vtkClass: "vtkPoints",
                dataType: "Float32Array",
                numberOfComponents: 3,
                values: pts.flat(2),
            },
            lines: {
                vtkClass: "vtkCellArray",
                dataType: "Uint32Array",
                values: polys.flat(2),
            },
        });
        const gridMapper = vtkns.Mapper.newInstance();
        const gridActor = vtkns.Actor.newInstance();
        gridMapper.setInputData(gridPolyData);
        gridActor.setMapper(gridMapper);
        gridActor.getProperty().setOpacity(this.grid_opacity);
        gridActor.setVisibility(this.show_grid);
        return gridActor;
    }
    create_axes(canvas) {
        if (this.origin == null) {
            return { psActor: null, axesActor: null, gridActor: null };
        }
        const points = [this.xticks, this.yticks, this.zticks].map((arr, axis) => {
            let coords = null;
            switch (axis) {
                case 0:
                    coords = cartesian_product(arr, [this.origin[1]], [this.origin[2]]);
                    break;
                case 1:
                    coords = cartesian_product([this.origin[0]], arr, [this.origin[2]]);
                    break;
                case 2:
                    coords = cartesian_product([this.origin[0]], [this.origin[1]], arr);
                    break;
            }
            return coords;
        }).flat(2);
        const axesPolyData = window.vtk({
            vtkClass: "vtkPolyData",
            points: {
                vtkClass: "vtkPoints",
                dataType: "Float32Array",
                numberOfComponents: 3,
                values: points,
            },
            lines: {
                vtkClass: "vtkCellArray",
                dataType: "Uint32Array",
                values: [
                    2,
                    0,
                    this.xticks.length - 1,
                    2,
                    this.xticks.length,
                    this.xticks.length + this.yticks.length - 1,
                    2,
                    this.xticks.length + this.yticks.length,
                    this.xticks.length + this.yticks.length + this.zticks.length - 1,
                ],
            },
        });
        const psMapper = vtkns.PixelSpaceCallbackMapper.newInstance();
        psMapper.setInputData(axesPolyData);
        psMapper.setUseZValues(true);
        psMapper.setCallback((coordsList, camera, aspect) => {
            const textCtx = canvas.getContext("2d");
            if (textCtx) {
                const dims = {
                    height: canvas.clientHeight * window.devicePixelRatio,
                    width: canvas.clientWidth * window.devicePixelRatio,
                };
                const dataPoints = psMapper.getInputData().getPoints();
                const viewMatrix = camera.getViewMatrix();
                mat4.transpose(viewMatrix, viewMatrix);
                const projMatrix = camera.getProjectionMatrix(aspect, -1, 1);
                mat4.transpose(projMatrix, projMatrix);
                textCtx.clearRect(0, 0, dims.width, dims.height);
                coordsList.forEach((xy, idx) => {
                    const pdPoint = dataPoints.getPoint(idx);
                    const vc = vec3.fromValues(pdPoint[0], pdPoint[1], pdPoint[2]);
                    vec3.transformMat4(vc, vc, viewMatrix);
                    vc[2] += 0.05; // sensibility
                    vec3.transformMat4(vc, vc, projMatrix);
                    if (vc[2] - 0.001 < xy[3]) {
                        textCtx.font = "30px serif";
                        textCtx.textAlign = "center";
                        textCtx.textBaseline = "alphabetic";
                        textCtx.fillText(".", xy[0], dims.height - xy[1] + 2);
                        textCtx.font = `${this.fontsize * window.devicePixelRatio}px serif`;
                        textCtx.textAlign = "right";
                        textCtx.textBaseline = "top";
                        let label;
                        if (idx < this.xticks.length) {
                            label = this.xlabels[idx];
                        }
                        else if (idx >= this.xticks.length &&
                            idx < this.xticks.length + this.yticks.length) {
                            label = this.ylabels[idx - this.xticks.length];
                        }
                        else {
                            label = this.zlabels[idx - (this.xticks.length + this.yticks.length)];
                        }
                        textCtx.fillText(`${label}`, xy[0], dims.height - xy[1]);
                    }
                });
            }
        });
        const psActor = vtkns.Actor.newInstance(); //PixelSpace
        psActor.setMapper(psMapper);
        const axesMapper = vtkns.Mapper.newInstance();
        axesMapper.setInputData(axesPolyData);
        const axesActor = vtkns.Actor.newInstance();
        axesActor.setMapper(axesMapper);
        axesActor.getProperty().setOpacity(this.axes_opacity);
        const gridActor = this._create_grid_axes();
        return { psActor, axesActor, gridActor };
    }
}
//# sourceMappingURL=vtkaxes.js.map