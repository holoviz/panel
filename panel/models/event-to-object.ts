/*
The MIT License (MIT)

Copyright (c) 2019 Ryan S. Morshead

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

export function serializeEvent(event: any): any {
  const data: any = {};

  // support for CustomEvents: the whole `detail` object is serialized
  if (event.detail !== undefined) {
    Object.assign(data, { detail: JSON.parse(JSON.stringify(event.detail)) } );
  }

  if (event.type in eventTransforms) {
    Object.assign(data, eventTransforms[event.type](event));
  }

  data.target = serializeDomElement(event.target);
  data.currentTarget =
    event.target === event.currentTarget
      ? data.target
      : serializeDomElement(event.currentTarget);
  data.relatedTarget = serializeDomElement(event.relatedTarget);

  return data;
}

function serializeDomElement(element: Element): any {
  let elementData: any = null;
  if (element) {
    elementData = defaultElementTransform(element);
    if (element.tagName in elementTransforms) {
      elementTransforms[element.tagName].forEach((trans: any) =>
        Object.assign(elementData, trans(element))
      );
    }
  }
  return elementData;
}

const elementTransformCategories: any = {
  hasValue: (element: any) => ({
    value: element.value,
  }),
  hasCurrentTime: (element: any) => ({
    currentTime: element.currentTime,
  }),
  hasFiles: (element: any) => {
    if (element?.type === "file") {
      return {
        files: Array.from(element.files).map((file: File) => ({
          lastModified: file.lastModified,
          name: file.name,
          size: file.size,
          type: file.type,
        })),
      };
    } else {
      return {};
    }
  },
};

function defaultElementTransform(element: Element) {
  try {
    return { boundingClientRect: {...element.getBoundingClientRect()} };
  } catch {
    return {}
  }
}

const elementTagCategories: any = {
  hasValue: [
    "BUTTON",
    "INPUT",
    "OPTION",
    "LI",
    "METER",
    "PROGRESS",
    "PARAM",
    "SELECT",
    "TEXTAREA",
  ],
  hasCurrentTime: ["AUDIO", "VIDEO"],
  hasFiles: ["INPUT"],
};

const elementTransforms: any = {};

Object.keys(elementTagCategories).forEach((category) => {
  elementTagCategories[category].forEach((type: any) => {
    const transforms =
      elementTransforms[type] || (elementTransforms[type] = []);
    transforms.push(elementTransformCategories[category]);
  });
});

class EventTransformCategories {

  clipboard(event: any) {
    return {
      clipboardData: event.clipboardData,
    }
  }

  composition(event: any) {
    return {
      data: event.data,
    }
  }

  keyboard(event: any) {
    return {
      altKey: event.altKey,
      charCode: event.charCode,
      ctrlKey: event.ctrlKey,
      key: event.key,
      keyCode: event.keyCode,
      locale: event.locale,
      location: event.location,
      metaKey: event.metaKey,
      repeat: event.repeat,
      shiftKey: event.shiftKey,
      which: event.which,
    }
  }

  mouse(event: any) {
    return {
      altKey: event.altKey,
      button: event.button,
      buttons: event.buttons,
      clientX: event.clientX,
      clientY: event.clientY,
      ctrlKey: event.ctrlKey,
      metaKey: event.metaKey,
      pageX: event.pageX,
      pageY: event.pageY,
      screenX: event.screenX,
      screenY: event.screenY,
      shiftKey: event.shiftKey,
    }
  }

  pointer(event: any) {
    return {
      ...this.mouse(event),
      pointerId: event.pointerId,
      width: event.width,
      height: event.height,
      pressure: event.pressure,
      tiltX: event.tiltX,
      tiltY: event.tiltY,
      pointerType: event.pointerType,
      isPrimary: event.isPrimary,
    }
  }

  selection(): any {
    return {
      selectedText: (window as any).getSelection().toString()
    }
  };

  touch(event: any) {
    return {
      altKey: event.altKey,
      ctrlKey: event.ctrlKey,
      metaKey: event.metaKey,
      shiftKey: event.shiftKey,
    }
  }

  ui(event: any) {
    return {
      detail: event.detail,
    }
  }

  wheel(event: any) {
    return {
      deltaMode: event.deltaMode,
      deltaX: event.deltaX,
      deltaY: event.deltaY,
      deltaZ: event.deltaZ,
    }
  }

  animation(event: any) {
    return {
      animationName: event.animationName,
      pseudoElement: event.pseudoElement,
      elapsedTime: event.elapsedTime,
    }
  }

  transition(event: any) {
    return {
      propertyName: event.propertyName,
      pseudoElement: event.pseudoElement,
      elapsedTime: event.elapsedTime,
    }
  }
}

const eventTypeCategories: any = {
  clipboard: ["copy", "cut", "paste"],
  composition: ["compositionend", "compositionstart", "compositionupdate"],
  keyboard: ["keydown", "keypress", "keyup"],
  mouse: [
    "click",
    "contextmenu",
    "doubleclick",
    "drag",
    "dragend",
    "dragenter",
    "dragexit",
    "dragleave",
    "dragover",
    "dragstart",
    "drop",
    "mousedown",
    "mouseenter",
    "mouseleave",
    "mousemove",
    "mouseout",
    "mouseover",
    "mouseup",
  ],
  pointer: [
    "pointerdown",
    "pointermove",
    "pointerup",
    "pointercancel",
    "gotpointercapture",
    "lostpointercapture",
    "pointerenter",
    "pointerleave",
    "pointerover",
    "pointerout",
  ],
  selection: ["select"],
  touch: ["touchcancel", "touchend", "touchmove", "touchstart"],
  ui: ["scroll"],
  wheel: ["wheel"],
  animation: ["animationstart", "animationend", "animationiteration"],
  transition: ["transitionend"],
};

const eventTransforms: any = {};

const eventTransformCategories: any = new EventTransformCategories();

Object.keys(eventTypeCategories).forEach((category) => {
  eventTypeCategories[category].forEach((type: any) => {
    eventTransforms[type] = eventTransformCategories[category];
  });
});
