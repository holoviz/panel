import { render } from "preact";
import { useCallback } from "preact/hooks";
import { html } from "htm/preact";
import { div } from "@bokehjs/core/dom";
import { isArray, isString } from "@bokehjs/core/util/types";
import { dict_to_records } from "./data";
import { serializeEvent } from "./event-to-object";
import { DOMEvent, htmlDecode } from "./html";
import { HTMLBox, HTMLBoxView } from "./layout";
function serialize_attrs(attrs) {
    const serialized = {};
    for (const attr in attrs) {
        let value = attrs[attr];
        if (!isString(value)) {
        }
        else if (value !== "" && (value === "NaN" || !isNaN(Number(value)))) {
            value = Number(value);
        }
        else if (value === "false" || value === "true") {
            value = value === "true" ? true : false;
        }
        serialized[attr] = value;
    }
    return serialized;
}
function escapeRegex(string) {
    return string.replace(/[-\/\\^$*+?.()|[\]]/g, "\\$&");
}
function extractToken(template, str, tokens) {
    const tokenMapping = {};
    for (const match of tokens) {
        tokenMapping[`{${match}}`] = "(.*)";
    }
    const tokenList = [];
    let regexpTemplate = `^${escapeRegex(template)}$`;
    // Find the order of the tokens
    let i, tokenIndex, tokenEntry;
    for (const m in tokenMapping) {
        tokenIndex = template.indexOf(m);
        // Token found
        if (tokenIndex > -1) {
            regexpTemplate = regexpTemplate.replace(m, tokenMapping[m]);
            tokenEntry = {
                index: tokenIndex,
                token: m,
            };
            for (i = 0; i < tokenList.length && tokenList[i].index < tokenIndex; i++) {
                ;
            }
            // Insert it at index i
            if (i < tokenList.length) {
                tokenList.splice(i, 0, tokenEntry);
            }
            else {
                tokenList.push(tokenEntry);
            }
        }
    }
    regexpTemplate = regexpTemplate.replace(/\{[^{}]+\}/g, ".*");
    const match = new RegExp(regexpTemplate).exec(str);
    let result = null;
    if (match) {
        result = {};
        // Find your token entry
        for (i = 0; i < tokenList.length; i++) {
            result[tokenList[i].token.slice(1, -1)] = match[i + 1];
        }
    }
    return result;
}
function element_lookup(root, el_id) {
    let el = root.getElementById(el_id);
    if (el == null) {
        el = document.getElementById(el_id);
    }
    return el;
}
export class ReactiveHTMLView extends HTMLBoxView {
    static __name__ = "ReactiveHTMLView";
    html;
    container;
    _parent = null;
    _changing = false;
    _event_listeners = {};
    _mutation_observers = [];
    _script_fns = {};
    _state = {};
    initialize() {
        super.initialize();
        this.html = htmlDecode(this.model.html) || this.model.html;
    }
    _recursive_connect(model, update_children, path) {
        for (const prop in model.properties) {
            let subpath;
            if (path.length) {
                subpath = `${path}.${prop}`;
            }
            else {
                subpath = prop;
            }
            const obj = model[prop];
            if (obj == null) {
                continue;
            }
            if (obj.properties != null) {
                this._recursive_connect(obj, true, subpath);
            }
            this.on_change(model.properties[prop], () => {
                if (update_children) {
                    for (const node in this.model.children) {
                        if (this.model.children[node] == prop) {
                            let children = model[prop];
                            if (!isArray(children)) {
                                children = [children];
                            }
                            this._render_node(node, children);
                            return;
                        }
                    }
                }
                if (!this._changing) {
                    this._update(subpath);
                }
            });
        }
    }
    connect_signals() {
        super.connect_signals();
        const { children, events } = this.model.properties;
        this.on_change(children, async () => {
            this.html = htmlDecode(this.model.html) || this.model.html;
            await this.build_child_views();
            this.invalidate_render();
        });
        this._recursive_connect(this.model.data, true, "");
        this.on_change(events, () => {
            this._remove_event_listeners();
            this._setup_event_listeners();
        });
        this.connect_scripts();
    }
    connect_scripts() {
        const id = this.model.data.id;
        for (const prop in this.model.scripts) {
            const scripts = this.model.scripts[prop];
            let data_model = this.model.data;
            let attr;
            if (prop.indexOf(".") >= 0) {
                const path = prop.split(".");
                attr = path[path.length - 1];
                for (const p of path.slice(0, -1)) {
                    data_model = data_model[p];
                }
            }
            else {
                attr = prop;
            }
            for (const script of scripts) {
                const decoded_script = htmlDecode(script) || script;
                const script_fn = this._render_script(decoded_script, id);
                this._script_fns[prop] = script_fn;
                const property = data_model.properties[attr];
                if (property == null) {
                    continue;
                }
                const is_event_param = this.model.event_params.includes(prop);
                this.on_change(property, () => {
                    if (!this._changing && !(is_event_param && !data_model[prop])) {
                        this.run_script(prop);
                        if (is_event_param) {
                            data_model.setv({ [prop]: false });
                        }
                    }
                });
            }
        }
    }
    run_script(property, silent = false) {
        const script_fn = this._script_fns[property];
        if (script_fn === undefined) {
            if (!silent) {
                console.log(`Script '${property}' could not be found.`);
            }
            return;
        }
        const this_obj = {
            get_records: (property, index) => this.get_records(property, index),
        };
        for (const name in this._script_fns) {
            this_obj[name] = () => this.run_script(name);
        }
        return script_fn(this.model, this.model.data, this._state, this, (s) => this.run_script(s), this_obj);
    }
    get_records(property, index = true) {
        return dict_to_records(this.model.data[property], index);
    }
    disconnect_signals() {
        super.disconnect_signals();
        this._remove_event_listeners();
        this._remove_mutation_observers();
    }
    remove() {
        this.run_script("remove", true);
        super.remove();
    }
    get child_models() {
        const models = [];
        for (const parent in this.model.children) {
            for (const model of this.model.children[parent]) {
                if (!isString(model)) {
                    models.push(model);
                }
            }
        }
        return models;
    }
    _after_layout() {
        this.run_script("after_layout", true);
    }
    render() {
        this.empty();
        this._update_stylesheets();
        this._update_css_classes();
        this._apply_styles();
        this._apply_visible();
        this.container = div({ style: "display: contents;" });
        this.shadow_el.append(this.container);
        this._update();
        this._render_children();
        this._setup_mutation_observers();
        this._setup_event_listeners();
        this.run_script("render", true);
    }
    _send_event(elname, attr, event) {
        const serialized = serializeEvent(event);
        serialized.type = attr;
        for (const key in serialized) {
            if (serialized[key] === undefined) {
                delete serialized[key];
            }
        }
        this.model.trigger_event(new DOMEvent(elname, serialized));
    }
    _render_child(model, el) {
        const view = this._child_views.get(model);
        if (view == null) {
            el.innerHTML = htmlDecode(model) || model;
        }
        else {
            el.appendChild(view.el);
            view.render();
            view.after_render();
        }
    }
    _render_node(node, children) {
        const id = this.model.data.id;
        if (this.model.looped.indexOf(node) > -1) {
            for (let i = 0; i < children.length; i++) {
                const el = element_lookup(this.shadow_el, `${node}-${i}-${id}`);
                if (el == null) {
                    console.warn(`DOM node '${node}-${i}-${id}' could not be found. Cannot render children.`);
                    continue;
                }
                this._render_child(children[i], el);
            }
        }
        else {
            const el = element_lookup(this.shadow_el, `${node}-${id}`);
            if (el == null) {
                console.warn(`DOM node '${node}-${id}' could not be found. Cannot render children.`);
                return;
            }
            for (const child of children) {
                this._render_child(child, el);
            }
        }
    }
    _render_children() {
        for (const node in this.model.children) {
            let children = this.model.children[node];
            if (isString(children)) {
                children = this.model.data[children];
                if (!isArray(children)) {
                    children = [children];
                }
            }
            this._render_node(node, children);
        }
    }
    _render_html(literal, state = {}) {
        let htm = literal.replace(/[`]/g, "\\$&");
        let callbacks = "";
        const methods = [];
        for (const elname in this.model.callbacks) {
            for (const callback of this.model.callbacks[elname]) {
                const [cb, method] = callback;
                let definition;
                htm = htm.replaceAll(`\${${method}}`, `$--{${method}}`);
                if (method.startsWith("script(")) {
                    const meth = (method
                        .replace("('", "_").replace("')", "")
                        .replace('("', "_").replace('")', "")
                        .replace("-", "_"));
                    const script_name = meth.replaceAll("script_", "");
                    htm = htm.replaceAll(method, meth);
                    definition = `
          const ${meth} = (event) => {
            view._state.event = event
            view.run_script("${script_name}")
            delete view._state.event
          }
          `;
                }
                else {
                    definition = `
          const ${method} = (event) => {
            let elname = "${elname}"
            if (RegExp("\{\{.*loop\.index.*\}\}").test(elname)) {
              const pattern = RegExp(elname.replace(/\{\{(.+?)\}\}/g, String.fromCharCode(92) + "d+"))
              for (const p of event.path) {
                if (pattern.exec(p.id) != null) {
                  elname = p.id.split("-").slice(null, -1).join("-")
                  break
                }
              }
            }
            view._send_event(elname, "${cb}", event)
          }
          `;
                }
                if (methods.indexOf(method) > -1) {
                    continue;
                }
                methods.push(method);
                callbacks = callbacks + definition;
            }
        }
        htm = (htm
            .replaceAll("${model.", "$-{model.")
            .replaceAll("${", "${data.")
            .replaceAll("$-{model.", "${model.")
            .replaceAll("$--{", "${"));
        return new Function("view, model, data, state, html, useCallback", `${callbacks}return html\`${htm}\`;`)(this, this.model, this.model.data, state, html, useCallback);
    }
    _render_script(literal, id) {
        const scripts = [];
        for (const elname of this.model.nodes) {
            const elvar = elname.replace("-", "_");
            if (literal.indexOf(elvar) === -1) {
                continue;
            }
            const script = `
      let ${elvar} = view.shadow_el.getElementById('${elname}-${id}')
      if (${elvar} == null)
        ${elvar} = document.getElementById('${elname}-${id}')
      if (${elvar} == null) {
        console.warn("DOM node '${elname}' could not be found. Cannot execute callback.")
        return
      }
      `;
            scripts.push(script);
        }
        const event = `
    let event = null
    if (state.event !== undefined) {
      event = state.event
    }
    `;
        scripts.push(event);
        scripts.push(literal);
        return new Function("model, data, state, view, script, self", scripts.join("\n"));
    }
    _remove_mutation_observers() {
        for (const observer of this._mutation_observers) {
            observer.disconnect();
        }
        this._mutation_observers = [];
    }
    _setup_mutation_observers() {
        const id = this.model.data.id;
        for (const name in this.model.attrs) {
            const el = element_lookup(this.shadow_el, `${name}-${id}`);
            if (el == null) {
                console.warn(`DOM node '${name}-${id}' could not be found. Cannot set up MutationObserver.`);
                continue;
            }
            const observer = new MutationObserver(() => {
                this._update_model(el, name);
            });
            observer.observe(el, { attributes: true });
            this._mutation_observers.push(observer);
        }
    }
    _remove_event_listeners() {
        const id = this.model.data.id;
        for (const node in this._event_listeners) {
            const el = element_lookup(this.shadow_el, `${node}-${id}`);
            if (el == null) {
                continue;
            }
            for (const event_name in this._event_listeners[node]) {
                const event_callback = this._event_listeners[node][event_name];
                el.removeEventListener(event_name, event_callback);
            }
        }
        this._event_listeners = {};
    }
    _setup_event_listeners() {
        const id = this.model.data.id;
        for (const node in this.model.events) {
            const el = element_lookup(this.shadow_el, `${node}-${id}`);
            if (el == null) {
                console.warn(`DOM node '${node}-${id}' could not be found. Cannot subscribe to DOM events.`);
                continue;
            }
            const node_events = this.model.events[node];
            for (const event_name in node_events) {
                const event_callback = (event) => {
                    this._send_event(node, event_name, event);
                    if (node in this.model.attrs && node_events[event_name]) {
                        this._update_model(el, node);
                    }
                };
                el.addEventListener(event_name, event_callback);
                if (!(node in this._event_listeners)) {
                    this._event_listeners[node] = {};
                }
                this._event_listeners[node][event_name] = event_callback;
            }
        }
    }
    _update(property = null) {
        if (property == null || (this.html.indexOf(`\${${property}}`) > -1)) {
            const rendered = this._render_html(this.html);
            if (rendered == null) {
                return;
            }
            try {
                this._changing = true;
                render(rendered, this.container);
            }
            finally {
                this._changing = false;
            }
        }
    }
    _update_model(el, name) {
        if (this._changing) {
            return;
        }
        const attrs = {};
        for (const attr_info of this.model.attrs[name]) {
            const [attr, tokens, template] = attr_info;
            let value = attr === "children" ? el.innerHTML : el[attr];
            if (tokens.length === 1 && (`{${tokens[0]}}` === template)) {
                attrs[tokens[0]] = value;
            }
            else if (isString(value)) {
                value = extractToken(template, value, tokens);
                if (value == null) {
                    console.warn(`Could not resolve parameters in ${name} element ${attr} attribute value ${value}.`);
                }
                else {
                    for (const param in value) {
                        if (value[param] === undefined) {
                            console.warn(`Could not resolve ${param} in ${name} element ${attr} attribute value ${value}.`);
                        }
                        else {
                            attrs[param] = value[param];
                        }
                    }
                }
            }
        }
        try {
            this._changing = true;
            this.model.data.setv(serialize_attrs(attrs));
        }
        catch {
            console.log("Could not serialize", attrs);
        }
        finally {
            this._changing = false;
        }
    }
}
export class ReactiveHTML extends HTMLBox {
    static __name__ = "ReactiveHTML";
    constructor(attrs) {
        super(attrs);
    }
    static __module__ = "panel.models.reactive_html";
    static {
        this.prototype.default_view = ReactiveHTMLView;
        this.define(({ List, Any, Str }) => ({
            attrs: [Any, {}],
            callbacks: [Any, {}],
            children: [Any, {}],
            data: [Any],
            event_params: [List(Str), []],
            events: [Any, {}],
            html: [Str, ""],
            looped: [List(Str), []],
            nodes: [List(Str), []],
            scripts: [Any, {}],
        }));
    }
}
//# sourceMappingURL=reactive_html.js.map