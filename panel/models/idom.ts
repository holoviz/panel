import {render, createContext} from 'preact';
import {useState, useEffect, useContext, useRef, useCallback} from 'preact/hooks';
import {html} from 'htm/preact';
import {applyPatch, getValueByPointer} from 'fast-json-patch';

import * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import {PanelHTMLBoxView} from "./layout"
import {serializeEvent} from "./event-to-object"

const LayoutConfigContext = createContext({});

export function mountLayout(
  mountElement: any,
  saveUpdateHook: any,
  sendEvent: any,
  importSourceUrl: string
) {
  render(
    html`
      <${Layout}
        saveUpdateHook=${saveUpdateHook}
        sendEvent=${sendEvent}
        importSourceUrl=${importSourceUrl}
      />
    `,
    mountElement
  );
}

export default function Layout({ saveUpdateHook, sendEvent, importSourceUrl }: { saveUpdateHook: any, sendEvent: any, importSourceUrl: string } ) {
  const [model, patchModel] = useInplaceJsonPatch({});

  useEffect(() => saveUpdateHook(patchModel), [patchModel]);

  if (model.tagName) {
    return html`
      <${LayoutConfigContext.Provider}
        value=${{
          sendEvent: sendEvent,
          importSourceUrl: importSourceUrl,
        }}
      >
        <${Element} model=${model} />
      <//>
    `;
  } else {
    return html`<div />`;
  }
}

function Element({ model }: { model: any }) {
  if (model.importSource) {
    return html`<${ImportedElement} model=${model} />`;
  } else {
    return html`<${StandardElement} model=${model} />`;
  }
}

function ImportedElement({ model }: { model: any }) {
  const config: any = useContext(LayoutConfigContext);
  const module = useLazyModule(
    model.importSource.source,
    config.importSourceUrl
  );
  if (module) {
    const cmpt = getPathProperty(module, model.tagName);
    const children = elementChildren(model);
    const attributes = elementAttributes(model, config.sendEvent);
    return html`<${cmpt} ...${attributes}>${children}<//>`;
  } else {
    const fallback = model.importSource.fallback;
    if (!fallback) {
      return html`<div />`;
    }
    switch (typeof fallback) {
      case "object":
        return html`<${Element} model=${fallback} />`;
      case "string":
        return html`<div>${fallback}</div>`;
      default:
        return null
    }
  }
}

function StandardElement({ model }: { model: any }) {
  const config: any = useContext(LayoutConfigContext);
  const children = elementChildren(model);
  const attributes = elementAttributes(model, config.sendEvent);
  if (model.children && model.children.length) {
    return html`<${model.tagName} ...${attributes}>${children}<//>`;
  } else {
    return html`<${model.tagName} ...${attributes} />`;
  }
}

function elementChildren(model: any) {
  if (!model.children) {
    return [];
  } else {
    return model.children.map((child: any) => {
      switch (typeof child) {
        case "object":
          return html`<${Element} model=${child} />`;
        case "string":
          return child;
        default:
          return null;
      }
    });
  }
}

function elementAttributes(model: any, sendEvent: any) {
  const attributes = Object.assign({}, model.attributes);

  if (model.eventHandlers) {
    Object.keys(model.eventHandlers).forEach((eventName) => {
      const eventSpec = model.eventHandlers[eventName];
      attributes[eventName] = eventHandler(sendEvent, eventSpec);
    });
  }

  return attributes;
}

function eventHandler(sendEvent: any, eventSpec: any) {
  return function (): Promise<void> {
    const data = Array.from(arguments).map((value) => {
      if (typeof value === "object") {
        if (eventSpec["preventDefault"]) {
          value.preventDefault();
        }
        if (eventSpec["stopPropagation"]) {
          value.stopPropagation();
        }
        return serializeEvent(value);
      } else {
        return value;
      }
    });
    return new Promise((resolve: any) => {
      const msg = {
        data: data,
        target: eventSpec["target"],
      };
      sendEvent(msg);
      resolve(msg);
    });
  };
}

function useLazyModule(source: string, sourceUrlBase: string = "") {
  const [module, setModule] = useState(null);
  if (!module) {
    // use eval() to avoid weird build behavior by bundlers like Webpack
    eval(`import("${joinUrl(sourceUrlBase, source)}")`).then(setModule);
  }
  return module;
}

function getPathProperty(obj: any, prop: string) {
  // properties may be dot seperated strings
  const path = prop.split(".");
  const firstProp: any = path.shift();
  let value = obj[firstProp];
  for (let i = 0; i < path.length; i++) {
    value = value[path[i]];
  }
  return value;
}

function useInplaceJsonPatch(doc: any) {
  const ref = useRef(doc);
  const forceUpdate = useForceUpdate();

  const applyPatch = useCallback(
    (path: any, patch: any) => {
      applyPatchInplace(ref.current, path, patch);
      forceUpdate();
    },
    [ref, forceUpdate]
  );

  return [ref.current, applyPatch];
}

function applyPatchInplace(doc: any, path: any, patch: any) {
  if (!path) {
    applyPatch(doc, patch);
  } else {
    applyPatch(doc, [
      {
        op: "replace",
        path: path,
        value: applyPatch(
          getValueByPointer(doc, path),
          patch,
          false,
          false
        ).newDocument,
      },
    ]);
  }
}

function useForceUpdate() {
  const [, updateState] = useState({});
  return useCallback(() => updateState({}), []);
}

function joinUrl(base: string, tail: string) {
  return tail.startsWith("./")
    ? (base.endsWith("/") ? base.slice(0, -1) : base) + tail.slice(1)
    : tail;
}

export class IDOMView extends PanelHTMLBoxView {
  model: IDOM
  _update: any

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.event.change, () => {
      this._update(this.model.event.data.path, this.model.event.data.changes);
    })
  }

  render(): void {
    super.render()
    mountLayout(
      this.el,
      (update: any) => this._save_update(update),
      (event: any) => this._send(event),
      this.model.importSourceUrl
    );
  }

  _save_update(update: any): any {
    this._update = update
    console.log(this.model.event.data)
    update(this.model.event.data.path, this.model.event.data.changes);
  }

  _send(event: any): any {
    this.model.msg = event
  }
}

export namespace IDOM {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Markup.Props & {
    event: p.Property<any>
    importSourceUrl: p.Property<string>
    msg: p.Property<any>
  }
}

export interface IDOM extends IDOM.Attrs {}

export class IDOM extends Markup {
  properties: IDOM.Props

  constructor(attrs?: Partial<IDOM.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.idom"

  static init_IDOM(): void {
    this.prototype.default_view = IDOMView
      this.define<IDOM.Props>({
      importSourceUrl: [ p.String, '' ],
      event:    [ p.Any, {} ],
      msg:      [ p.Any, {} ],
    })
  }
}
