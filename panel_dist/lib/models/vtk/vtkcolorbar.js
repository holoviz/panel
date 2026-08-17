import { LinearColorMapper } from "@bokehjs/models/mappers";
import { range, linspace } from "@bokehjs/core/util/array";
export class VTKColorBar {
    parent;
    mapper;
    options;
    static __name__ = "VTKColorBar";
    canvas;
    ctx;
    constructor(parent, mapper, options = {}) {
        this.parent = parent;
        this.mapper = mapper;
        this.options = options;
        if (!options.ticksNum) {
            options.ticksNum = 5;
        }
        if (!options.fontFamily) {
            options.fontFamily = "Arial";
        }
        if (!options.fontSize) {
            options.fontSize = "12px";
        }
        if (!options.ticksSize) {
            options.ticksSize = 2;
        }
        this.canvas = document.createElement("canvas");
        this.canvas.style.width = "100%";
        this.parent.appendChild(this.canvas);
        this.ctx = this.canvas.getContext("2d");
        this.ctx.font = `${this.options.fontSize} ${this.options.fontFamily}`;
        this.ctx.lineWidth = options.ticksSize;
        if (!options.height) {
            options.height = `${(this.font_height + 1) * 4}px`; //title/ticks/colorbar
        }
        this.canvas.style.height = options.height;
        this.draw_colorbar();
    }
    get values() {
        const { min, max } = this.mapper.metrics;
        return linspace(min, max, this.options.ticksNum);
    }
    get ticks() {
        return this.values.map((v) => v.toExponential(3));
    }
    get title() {
        return this.mapper.name ?? "scalars";
    }
    get font_height() {
        let font_height = 0;
        this.values.forEach((val) => {
            const { actualBoundingBoxAscent, actualBoundingBoxDescent, } = this.ctx.measureText(`${val}`);
            const height = actualBoundingBoxAscent + actualBoundingBoxDescent;
            if (font_height < height) {
                font_height = height;
            }
        });
        return font_height;
    }
    draw_colorbar() {
        this.canvas.width = this.canvas.clientWidth;
        this.canvas.height = this.canvas.clientHeight;
        const { palette } = this.mapper;
        this.ctx.font = `${this.options.fontSize} ${this.options.fontFamily}`;
        const font_height = this.font_height;
        this.ctx.save();
        //colorbar
        const image = document.createElement("canvas");
        const h = 1;
        const w = palette.length;
        image.width = w;
        image.height = h;
        const image_ctx = image.getContext("2d");
        const image_data = image_ctx.getImageData(0, 0, w, h);
        const cmap = new LinearColorMapper({ palette }).rgba_mapper;
        const buf8 = cmap.v_compute(range(0, palette.length));
        image_data.data.set(buf8);
        image_ctx.putImageData(image_data, 0, 0);
        this.ctx.drawImage(image, 0, 2 * (this.font_height + 1) + 1, this.canvas.width, this.canvas.height);
        this.ctx.restore();
        this.ctx.save();
        //title
        this.ctx.textAlign = "center";
        this.ctx.fillText(this.title, this.canvas.width / 2, font_height + 1);
        this.ctx.restore();
        this.ctx.save();
        //ticks
        const tick_x_positions = linspace(0, this.canvas.width, 5);
        tick_x_positions.forEach((xpos, idx) => {
            let xpos_tick = xpos;
            if (idx == 0) {
                xpos_tick = xpos + Math.ceil(this.ctx.lineWidth / 2);
                this.ctx.textAlign = "left";
            }
            else if (idx == tick_x_positions.length - 1) {
                xpos_tick = xpos - Math.ceil(this.ctx.lineWidth / 2);
                this.ctx.textAlign = "right";
            }
            else {
                this.ctx.textAlign = "center";
            }
            this.ctx.moveTo(xpos_tick, 2 * (font_height + 1));
            this.ctx.lineTo(xpos_tick, 2 * (font_height + 1) + 5);
            this.ctx.stroke();
            this.ctx.fillText(`${this.ticks[idx]}`, xpos, 2 * (font_height + 1));
        });
        this.ctx.restore();
    }
}
//# sourceMappingURL=vtkcolorbar.js.map