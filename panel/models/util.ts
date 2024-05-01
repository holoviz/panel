import {concat} from "@bokehjs/core/util/array"
import {isPlainObject, isArray} from "@bokehjs/core/util/types"

export const get = (obj: any, path: string, defaultValue: any = undefined) => {
  const travel = (regexp: RegExp) =>
    String.prototype.split
      .call(path, regexp)
      .filter(Boolean)
      .reduce((res: any, key: any) => (res !== null && res !== undefined ? res[key] : res), obj)
  const result = travel(/[,[\]]+?/) || travel(/[,[\].]+?/)
  return result === undefined || result === obj ? defaultValue : result
}

export function throttle(func: any, timeFrame: number) {
  let lastTime: number = 0
  return function() {
    const now: number = Number(new Date())
    if (now - lastTime >= timeFrame) {
      func()
      lastTime = now
    }
  }
}

export function deepCopy(obj: any): any {
  let copy

  // Handle the 3 simple types, and null or undefined
  if (null == obj || "object" != typeof obj) {
    return obj
  }

  // Handle Array
  if (obj instanceof Array) {
    copy = []
    for (let i = 0, len = obj.length; i < len; i++) {
      copy[i] = deepCopy(obj[i])
    }
    return copy
  }

  // Handle Object
  if (obj instanceof Object) {
    const copy: any = {}
    for (const attr in obj) {
      const key: string = attr
      if (obj.hasOwnProperty(key)) {
        copy[key] = deepCopy(obj[key])
      }
    }
    return copy
  }

  throw new Error("Unable to copy obj! Its type isn't supported.")
}

export function reshape(arr: any[], dim: number[]) {
  let elemIndex = 0

  if (!dim || !arr) {
    return []
  }

  function _nest(dimIndex: number): any[] {
    let result = []

    if (dimIndex === dim.length - 1) {
      result = concat(arr.slice(elemIndex, elemIndex + dim[dimIndex]))
      elemIndex += dim[dimIndex]
    } else {
      for (let i = 0; i < dim[dimIndex]; i++) {
        result.push(_nest(dimIndex + 1))
      }
    }

    return result
  }
  return _nest(0)
}

export async function loadScript(type: string, src: string) {
  const script = document.createElement("script")
  script.type = type
  script.src = src
  script.defer = true
  document.head.appendChild(script)
  return new Promise<void>((resolve, reject) => {
    script.onload = () => {
      resolve()
    }
    script.onerror = () => {
      reject()
    }
  })
}

export function convertUndefined(obj: any): any {
  if (isArray(obj)) {
    return obj.map(convertUndefined)
  } else if (isPlainObject(obj)) {
    Object
      .entries(obj)
      .forEach(([key, value]) => {
        if (isPlainObject(value) || isArray(value)) {
          convertUndefined(value)
        } else if (value === undefined) {
          obj[key] = null
        }
      })
  }
  return obj
}
