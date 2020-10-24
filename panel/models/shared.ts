import { HTMLBox, } from "@bokehjs/models/layouts/html_box"
import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";

/** Function copied from the panel\models\layout.ts file of Panel
 * It is used for some models like deckgl, progress and vtlklayout
 * I have not yet understood why
 * @param el
 * @param model
 */
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

/** Transform the data of the cds to 'records' format, i.e. a list of objects
 *
 *  For example transforms to [{"x": 1, "y": 2}, {"x": 3, "y": 4}]
 *
 *  Some js libraries like perspective-viewer uses this format to load data.
 *
 * @param cds
 */
export function transform_cds_to_records(cds: ColumnDataSource): any {
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

/** Helper function used to incrementally build a html element string
 *
 *  For example toAttribute("columns", ['x','y']) returns ' columns="['x','y']"
 *  For example toAttribute("columns", null) returns ""
 *
 * @param attribute
 * @param value
 */
export function toAttribute(attribute: string, value: any): string {
    if (value===null){return ""}

    if (typeof value !== "string"){
        value=JSON.stringify(value)}
    return " " + attribute + "='" + value + "'";
}