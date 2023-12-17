/*
This file was adapted from https://github.com/uber/deck.gl/ the LICENSE
below is preserved to comply with the original license.

Copyright (c) 2015 - 2017 Uber Technologies, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

/* global document */
let lastPickedObject: any;
let lastTooltip: any;

const DEFAULT_STYLE = {
  fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
  display: 'flex',
  flex: 'wrap',
  maxWidth: '500px',
  flexDirection: 'column',
  zIndex: 2
};

function getDiv() {
  return document.createElement('div');
}

export function getTooltipDefault(pickedInfo: any) {
  if (!pickedInfo.picked) {
    return null;
  }
  if (pickedInfo.object === lastPickedObject) {
    return lastTooltip;
  }
  const tooltip = {
    html: tabularize(pickedInfo.object),
    style: DEFAULT_STYLE
  };
  lastTooltip = tooltip;
  lastPickedObject = pickedInfo.object;
  return tooltip;
}

const EXCLUDES = new Set(['position', 'index']);

export function tabularize(json: any) {
  // Turns a JSON object of picked info into HTML for a tooltip
  const dataTable = getDiv();

  // Creates rows of two columns for the tooltip
  for (const key in json) {
    if (EXCLUDES.has(key)) {
      continue; // eslint-disable-line
    }
    const header = getDiv();
    header.className = 'header';
    header.textContent = key;

    const valueElement = getDiv();
    valueElement.className = 'value';

    valueElement.textContent = toText(json[key]);

    const row = getDiv();

    setStyles(row, header, valueElement);

    row.appendChild(header);
    row.appendChild(valueElement);
    dataTable.appendChild(row);
  }

  return dataTable.innerHTML;
}

function setStyles(row: any, header: any, value: any) {
  // Set default tooltip style
  Object.assign(header.style, {
    fontWeight: 700,
    marginRight: '10px',
    flex: '1 1 0%'
  });

  Object.assign(value.style, {
    flex: 'none',
    maxWidth: '250px',
    overflow: 'hidden',
    whiteSpace: 'nowrap',
    textOverflow: 'ellipsis'
  });

  Object.assign(row.style, {
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'stretch'
  });
}

export function toText(jsonValue: any) {
  // Set contents of table value, trimming for certain types of data
  let text;
  if (Array.isArray(jsonValue) && jsonValue.length > 4) {
    text = `Array<${jsonValue.length}>`;
  } else if (typeof jsonValue === 'string') {
    text = jsonValue;
  } else if (typeof jsonValue === 'number') {
    text = String(jsonValue);
  } else {
    try {
      text = JSON.stringify(jsonValue);
    } catch (err) {
      text = '<Non-Serializable Object>';
    }
  }
  const MAX_LENGTH = 50;
  if (text.length > MAX_LENGTH) {
    text = text.slice(0, MAX_LENGTH);
  }
  return text;
}

export function substituteIn(template: any, json: any) {
  let output = template;
  for (const key in json) {
    if (typeof json[key] === 'object') {
      for (const subkey in json[key])
        output = output.replace(`{${key}.${subkey}}`, json[key][subkey]);
    }
    output = output.replace(`{${key}}`, json[key]);
  }
  return output;
}

export function makeTooltip(tooltips: any, layers: any[]) {
  /*
   * If explicitly no tooltip passed by user, return null
   * If a JSON object passed, return a tooltip based on that object
   *   We expect the user has passed a string template that will take pickedInfo keywords
   * If a boolean passed, return the default tooltip
   */
  if (!tooltips) {
    return null;
  }

  let per_layer = false
  const layer_tooltips: any = {}
  for (let i = 0; i < layers.length; i++) {
    const layer = layers[i]
    const layer_id = (layer.id as string)
    if (typeof tooltips !== "boolean" && (i.toString() in tooltips || layer_id in tooltips)) {
      layer_tooltips[layer_id] = layer_id in tooltips ? tooltips[layer_id]: tooltips[i.toString()]
      per_layer = true
    }
  }

  if (tooltips.html || tooltips.text || per_layer) {
    return (pickedInfo: any) => {
      if (!pickedInfo.picked) {
        return null;
      }

      const tooltip = (per_layer) ? layer_tooltips[pickedInfo.layer.id]: tooltips
      if (tooltip == null)
        return
      else if (typeof tooltip === "boolean")
        return tooltip ? getTooltipDefault(pickedInfo) : null

      const formattedTooltip: any = {
        style: tooltip.style || DEFAULT_STYLE
      };

      if (tooltip.html) {
        formattedTooltip.html = substituteIn(tooltip.html, pickedInfo.object);
      } else {
        formattedTooltip.text = substituteIn(tooltip.text, pickedInfo.object);
      }

      return formattedTooltip;
    };
  }

  return getTooltipDefault;
}
