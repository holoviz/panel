import { concat, uniq } from "@bokehjs/core/util/array";
import { isArray, isPlainObject } from "@bokehjs/core/util/types";
export const get = (obj, path, defaultValue = undefined) => {
    const travel = (regexp) => String.prototype.split
        .call(path, regexp)
        .filter(Boolean)
        .reduce((res, key) => (res !== null && res !== undefined ? res[key] : res), obj);
    const result = travel(/[,[\]]+?/) || travel(/[,[\].]+?/);
    return result === undefined || result === obj ? defaultValue : result;
};
export function throttle(func, limit) {
    let lastRan = 0;
    let trailingCall = null;
    return function (...args) {
        // @ts-ignore
        const context = this;
        const now = Date.now();
        if (trailingCall) {
            clearTimeout(trailingCall);
        }
        if ((now - lastRan) >= limit) {
            func.apply(context, args);
            lastRan = Date.now();
        }
        else {
            trailingCall = setTimeout(function () {
                func.apply(context, args);
                lastRan = Date.now();
                trailingCall = null;
            }, limit - (now - lastRan));
        }
    };
}
export function deepCopy(obj) {
    let copy;
    // Handle the 3 simple types, and null or undefined
    if (null == obj || "object" != typeof obj) {
        return obj;
    }
    // Handle Array
    if (obj instanceof Array) {
        copy = [];
        for (let i = 0, len = obj.length; i < len; i++) {
            copy[i] = deepCopy(obj[i]);
        }
        return copy;
    }
    // Handle Object
    if (obj instanceof Object) {
        const copy = {};
        for (const attr in obj) {
            const key = attr;
            if (obj.hasOwnProperty(key)) {
                copy[key] = deepCopy(obj[key]);
            }
        }
        return copy;
    }
    throw new Error("Unable to copy obj! Its type isn't supported.");
}
export function reshape(arr, dim) {
    let elemIndex = 0;
    if (!dim || !arr) {
        return [];
    }
    function _nest(dimIndex) {
        let result = [];
        if (dimIndex === dim.length - 1) {
            result = concat(arr.slice(elemIndex, elemIndex + dim[dimIndex]));
            elemIndex += dim[dimIndex];
        }
        else {
            for (let i = 0; i < dim[dimIndex]; i++) {
                result.push(_nest(dimIndex + 1));
            }
        }
        return result;
    }
    return _nest(0);
}
export async function loadScript(type, src) {
    const script = document.createElement("script");
    script.type = type;
    script.src = src;
    script.defer = true;
    document.head.appendChild(script);
    return new Promise((resolve, reject) => {
        script.onload = () => {
            resolve();
        };
        script.onerror = () => {
            reject();
        };
    });
}
export function ID() {
    // Math.random should be unique because of its seeding algorithm.
    // Convert it to base 36 (numbers + letters), and grab the first 9 characters
    // after the decimal.
    return `_${Math.random().toString(36).substring(2, 11)}`;
}
export function convertUndefined(obj) {
    if (isArray(obj)) {
        return obj.map(convertUndefined);
    }
    else if (isPlainObject(obj)) {
        Object
            .entries(obj)
            .forEach(([key, value]) => {
            if (isPlainObject(value) || isArray(value)) {
                convertUndefined(value);
            }
            else if (value === undefined) {
                obj[key] = null;
            }
        });
    }
    return obj;
}
export function formatError(error, code) {
    const regex = /\((\d+):(\d+)\)/;
    let msg = `<span class="msg">${error}</span>`;
    const match = msg.match(regex);
    if (!match) {
        return msg;
    }
    const line_num = parseInt(match[1]);
    const col = parseInt(match[2]);
    const start = Math.max(0, line_num - 5);
    const col_index = line_num - start;
    const lines = code.replace(">", "&lt;").replace("<", "&gt;").split(/\r?\n/).slice(start, line_num + 5);
    msg += "<br><br>";
    for (let i = 0; i < col_index; i++) {
        const cls = (i == (col_index - 1)) ? " class=\"highlight\"" : "";
        msg += `<pre${cls}>${lines[i]}</pre>`;
    }
    const indent = " ".repeat(col - 1);
    msg += `<pre class="highlight">${indent}^</pre>`;
    for (let i = col_index; i < lines.length; i++) {
        msg += `<pre>${lines[i]}</pre>`;
    }
    return msg;
}
export function find_attributes(text, obj, ignored) {
    const regex = RegExp(`\\b${obj}\\.([a-zA-Z_][a-zA-Z0-9_]*)\\b`, "g");
    const matches = [];
    let match, attr;
    while ((match = regex.exec(text)) !== null && (attr = match[0].slice(obj.length + 1)) !== null && !ignored.includes(attr)) {
        matches.push(attr);
    }
    return uniq(matches);
}
export function schedule_when(func, predicate, timeout = 10) {
    const scheduled = () => {
        if (predicate()) {
            func();
        }
        else {
            setTimeout(scheduled, timeout);
        }
    };
    scheduled();
}
//# sourceMappingURL=util.js.map