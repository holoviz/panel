export const get = (obj: any, path: string, defaultValue: any = undefined) => {
  const travel = (regexp: RegExp) =>
    String.prototype.split
      .call(path, regexp)
      .filter(Boolean)
    .reduce((res: any, key: any) => (res !== null && res !== undefined ? res[key] : res), obj);
  const result = travel(/[,[\]]+?/) || travel(/[,[\].]+?/);
  return result === undefined || result === obj ? defaultValue : result;
};

export function throttle(func: any, timeFrame: number) {
  var lastTime: number = 0;
  return function () {
    var now: number = Number(new Date());
      if (now - lastTime >= timeFrame) {
          func();
          lastTime = now;
      }
  };
}

export function deepCopy(obj: any): any {
  var copy;

  // Handle the 3 simple types, and null or undefined
  if (null == obj || "object" != typeof obj) return obj;

  // Handle Array
  if (obj instanceof Array) {
    copy = [];
    for (var i = 0, len = obj.length; i < len; i++) {
      copy[i] = deepCopy(obj[i]);
    }
    return copy;
  }

  // Handle Object
  if (obj instanceof Object) {
    const copy: any = {};
    for (const attr in obj) {
      const key: string = attr
      if (obj.hasOwnProperty(key))
        copy[key] = deepCopy(obj[key]);
    }
    return copy;
  }

  throw new Error("Unable to copy obj! Its type isn't supported.");
}

export function isPlainObject (obj: any) {
    return Object.prototype.toString.call(obj) === '[object Object]';
}
