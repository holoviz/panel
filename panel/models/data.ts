import {ColumnDataSource} from "@bokehjs/models/sources/column_data_source";

export function transform_cds_to_records(cds: ColumnDataSource, addId: boolean = false, start: number = 0): any {
  const data: any = []
  const columns = cds.columns()
  const cdsLength = cds.get_length()
  if (columns.length === 0||cdsLength === null)
    return []

  // Unpack typed arrays in a array
  // Workaround for https://github.com/bokeh/bokeh/issues/12788
  let total_length: number = 0
  let arrays: any = {}
  for (let i = start; i < cdsLength; i++) {
    for (const column of columns) {
      arrays[column] = []
      let unpack_array: any = cds.get_array(column);
      for (let i = start; i < unpack_array.length; i++) {
        if ((unpack_array[i].byteLength !== undefined) && unpack_array[i].length > 1)
          // A typed array
          arrays[column].push.apply(arrays[column], Array(...unpack_array[i]));
        else
          arrays[column].push(unpack_array[i])
        }
      total_length = Math.max(total_length, arrays[column].length);
      }
    }

  for (let i = start; i < total_length; i++) {
    const item: any = {}
    for (const column of columns) {
      let array: any = arrays[column];
      const shape = array[0].shape == null ? null : array[0].shape;
      if ((shape != null) && (shape.length > 1) && (typeof shape[0] == "number"))
        item[column] = array.slice(i*shape[1], i*shape[1]+shape[1])
      else
        item[column] = array[i]
    }
    if (addId)
      item['_index'] = i
    data.push(item)
  }
  return data
}

export function dict_to_records(data: any, index: boolean=true): any[] {
  const records: any[] = []
  for (let i = 0; i < data.index.length; i++) {
    const record: any = {}
    for (const col of data) {
      if (index || col !== "index")
        record[col] = data[col][i]
    }
  }
  return records
}
