import type { ColorMapper } from "@bokehjs/models/mappers";
export declare type ColorBarOptions = {
    ticksNum?: number;
    ticksSize?: number;
    fontFamily?: string;
    fontSize?: string;
    height?: string;
};
export declare class VTKColorBar {
    private parent;
    private mapper;
    private options;
    canvas: HTMLCanvasElement;
    private ctx;
    constructor(parent: HTMLElement, mapper: ColorMapper, options?: ColorBarOptions);
    get values(): number[];
    get ticks(): string[];
    get title(): string;
    get font_height(): number;
    draw_colorbar(): void;
}
//# sourceMappingURL=vtkcolorbar.d.ts.map