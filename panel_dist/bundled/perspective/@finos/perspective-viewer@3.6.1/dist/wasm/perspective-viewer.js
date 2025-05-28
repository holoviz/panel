import { PerspectiveViewNotFoundError } from './snippets/perspective-js-c50405f7b4339db9/inline0.js';
import { ClipboardItem } from './snippets/perspective-viewer-56aad64d21b793af/inline0.js';
import { IntersectionObserver } from './snippets/perspective-viewer-56aad64d21b793af/inline1.js';
import { ResizeObserver } from './snippets/perspective-viewer-56aad64d21b793af/inline2.js';
import { bootstrap } from './snippets/perspective-viewer-56aad64d21b793af/inline3.js';
import { psp } from './snippets/perspective-viewer-56aad64d21b793af/inline4.js';

let wasm;

const heap = new Array(128).fill(undefined);

heap.push(undefined, null, true, false);

function getObject(idx) { return heap[idx]; }

let WASM_VECTOR_LEN = 0;

let cachedUint8ArrayMemory0 = null;

function getUint8ArrayMemory0() {
    if (cachedUint8ArrayMemory0 === null || cachedUint8ArrayMemory0.byteLength === 0) {
        cachedUint8ArrayMemory0 = new Uint8Array(wasm.memory.buffer);
    }
    return cachedUint8ArrayMemory0;
}

const cachedTextEncoder = (typeof TextEncoder !== 'undefined' ? new TextEncoder('utf-8') : { encode: () => { throw Error('TextEncoder not available') } } );

const encodeString = function (arg, view) {
    return cachedTextEncoder.encodeInto(arg, view);
};

function passStringToWasm0(arg, malloc, realloc) {

    if (realloc === undefined) {
        const buf = cachedTextEncoder.encode(arg);
        const ptr = malloc(buf.length, 1) >>> 0;
        getUint8ArrayMemory0().subarray(ptr, ptr + buf.length).set(buf);
        WASM_VECTOR_LEN = buf.length;
        return ptr;
    }

    let len = arg.length;
    let ptr = malloc(len, 1) >>> 0;

    const mem = getUint8ArrayMemory0();

    let offset = 0;

    for (; offset < len; offset++) {
        const code = arg.charCodeAt(offset);
        if (code > 0x7F) break;
        mem[ptr + offset] = code;
    }

    if (offset !== len) {
        if (offset !== 0) {
            arg = arg.slice(offset);
        }
        ptr = realloc(ptr, len, len = offset + arg.length * 3, 1) >>> 0;
        const view = getUint8ArrayMemory0().subarray(ptr + offset, ptr + len);
        const ret = encodeString(arg, view);

        offset += ret.written;
        ptr = realloc(ptr, len, offset, 1) >>> 0;
    }

    WASM_VECTOR_LEN = offset;
    return ptr;
}

let cachedDataViewMemory0 = null;

function getDataViewMemory0() {
    if (cachedDataViewMemory0 === null || cachedDataViewMemory0.buffer.detached === true || (cachedDataViewMemory0.buffer.detached === undefined && cachedDataViewMemory0.buffer !== wasm.memory.buffer)) {
        cachedDataViewMemory0 = new DataView(wasm.memory.buffer);
    }
    return cachedDataViewMemory0;
}

function isLikeNone(x) {
    return x === undefined || x === null;
}

let heap_next = heap.length;

function addHeapObject(obj) {
    if (heap_next === heap.length) heap.push(heap.length + 1);
    const idx = heap_next;
    heap_next = heap[idx];

    heap[idx] = obj;
    return idx;
}

const cachedTextDecoder = (typeof TextDecoder !== 'undefined' ? new TextDecoder('utf-8', { ignoreBOM: true, fatal: true }) : { decode: () => { throw Error('TextDecoder not available') } } );

if (typeof TextDecoder !== 'undefined') { cachedTextDecoder.decode(); };

function getStringFromWasm0(ptr, len) {
    ptr = ptr >>> 0;
    return cachedTextDecoder.decode(getUint8ArrayMemory0().subarray(ptr, ptr + len));
}

function handleError(f, args) {
    try {
        return f.apply(this, args);
    } catch (e) {
        wasm.__wbindgen_export_2(addHeapObject(e));
    }
}

function dropObject(idx) {
    if (idx < 132) return;
    heap[idx] = heap_next;
    heap_next = idx;
}

function takeObject(idx) {
    const ret = getObject(idx);
    dropObject(idx);
    return ret;
}

function getArrayJsValueFromWasm0(ptr, len) {
    ptr = ptr >>> 0;
    const mem = getDataViewMemory0();
    const result = [];
    for (let i = ptr; i < ptr + 4 * len; i += 4) {
        result.push(takeObject(mem.getUint32(i, true)));
    }
    return result;
}

const CLOSURE_DTORS = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(state => {
    wasm.__wbindgen_export_4.get(state.dtor)(state.a, state.b)
});

function makeClosure(arg0, arg1, dtor, f) {
    const state = { a: arg0, b: arg1, cnt: 1, dtor };
    const real = (...args) => {
        // First up with a closure we increment the internal reference
        // count. This ensures that the Rust closure environment won't
        // be deallocated while we're invoking it.
        state.cnt++;
        try {
            return f(state.a, state.b, ...args);
        } finally {
            if (--state.cnt === 0) {
                wasm.__wbindgen_export_4.get(state.dtor)(state.a, state.b);
                state.a = 0;
                CLOSURE_DTORS.unregister(state);
            }
        }
    };
    real.original = state;
    CLOSURE_DTORS.register(real, state, state);
    return real;
}

function makeMutClosure(arg0, arg1, dtor, f) {
    const state = { a: arg0, b: arg1, cnt: 1, dtor };
    const real = (...args) => {
        // First up with a closure we increment the internal reference
        // count. This ensures that the Rust closure environment won't
        // be deallocated while we're invoking it.
        state.cnt++;
        const a = state.a;
        state.a = 0;
        try {
            return f(a, state.b, ...args);
        } finally {
            if (--state.cnt === 0) {
                wasm.__wbindgen_export_4.get(state.dtor)(a, state.b);
                CLOSURE_DTORS.unregister(state);
            } else {
                state.a = a;
            }
        }
    };
    real.original = state;
    CLOSURE_DTORS.register(real, state, state);
    return real;
}

function debugString(val) {
    // primitive types
    const type = typeof val;
    if (type == 'number' || type == 'boolean' || val == null) {
        return  `${val}`;
    }
    if (type == 'string') {
        return `"${val}"`;
    }
    if (type == 'symbol') {
        const description = val.description;
        if (description == null) {
            return 'Symbol';
        } else {
            return `Symbol(${description})`;
        }
    }
    if (type == 'function') {
        const name = val.name;
        if (typeof name == 'string' && name.length > 0) {
            return `Function(${name})`;
        } else {
            return 'Function';
        }
    }
    // objects
    if (Array.isArray(val)) {
        const length = val.length;
        let debug = '[';
        if (length > 0) {
            debug += debugString(val[0]);
        }
        for(let i = 1; i < length; i++) {
            debug += ', ' + debugString(val[i]);
        }
        debug += ']';
        return debug;
    }
    // Test for built-in
    const builtInMatches = /\[object ([^\]]+)\]/.exec(toString.call(val));
    let className;
    if (builtInMatches && builtInMatches.length > 1) {
        className = builtInMatches[1];
    } else {
        // Failed to match the standard '[object ClassName]'
        return toString.call(val);
    }
    if (className == 'Object') {
        // we're a user defined class or Object
        // JSON.stringify avoids problems with cycles, and is generally much
        // easier than looping through ownProperties of `val`.
        try {
            return 'Object(' + JSON.stringify(val) + ')';
        } catch (_) {
            return 'Object';
        }
    }
    // errors
    if (val instanceof Error) {
        return `${val.name}: ${val.message}\n${val.stack}`;
    }
    // TODO we could test for more things here, like `Set`s and `Map`s.
    return className;
}

function _assertClass(instance, klass) {
    if (!(instance instanceof klass)) {
        throw new Error(`expected instance of ${klass.name}`);
    }
}

function passArrayJsValueToWasm0(array, malloc) {
    const ptr = malloc(array.length * 4, 4) >>> 0;
    const mem = getDataViewMemory0();
    for (let i = 0; i < array.length; i++) {
        mem.setUint32(ptr + 4 * i, addHeapObject(array[i]), true);
    }
    WASM_VECTOR_LEN = array.length;
    return ptr;
}
/**
 * Register a plugin globally.
 * @param {string} name
 */
export function registerPlugin(name) {
    const ptr0 = passStringToWasm0(name, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
    const len0 = WASM_VECTOR_LEN;
    wasm.registerPlugin(ptr0, len0);
}

/**
 * Register this crate's Custom Elements in the browser's current session.
 *
 * This must occur before calling any public API methods on these Custom
 * Elements from JavaScript, as the methods themselves won't be defined yet.
 * By default, this crate does not register `PerspectiveViewerElement` (as to
 * preserve backwards-compatible synchronous API).
 */
export function init() {
    wasm.init();
}

let stack_pointer = 128;

function addBorrowedObject(obj) {
    if (stack_pointer == 1) throw new Error('out of js stack');
    heap[--stack_pointer] = obj;
    return stack_pointer;
}
function __wbg_adapter_52(arg0, arg1, arg2) {
    wasm.__wbindgen_export_5(arg0, arg1, addHeapObject(arg2));
}

function __wbg_adapter_55(arg0, arg1, arg2) {
    wasm.__wbindgen_export_6(arg0, arg1, addHeapObject(arg2));
}

function __wbg_adapter_60(arg0, arg1) {
    try {
        const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
        wasm.__wbindgen_export_7(retptr, arg0, arg1);
        var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
        var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
        if (r1) {
            throw takeObject(r0);
        }
    } finally {
        wasm.__wbindgen_add_to_stack_pointer(16);
    }
}

function __wbg_adapter_65(arg0, arg1) {
    const ret = wasm.__wbindgen_export_8(arg0, arg1);
    return takeObject(ret);
}

function __wbg_adapter_68(arg0, arg1, arg2) {
    try {
        wasm.__wbindgen_export_9(arg0, arg1, addBorrowedObject(arg2));
    } finally {
        heap[stack_pointer++] = undefined;
    }
}

function __wbg_adapter_71(arg0, arg1) {
    wasm.__wbindgen_export_10(arg0, arg1);
}

function __wbg_adapter_74(arg0, arg1, arg2) {
    wasm.__wbindgen_export_11(arg0, arg1, addHeapObject(arg2));
}

function __wbg_adapter_734(arg0, arg1, arg2, arg3) {
    wasm.__wbindgen_export_12(arg0, arg1, addHeapObject(arg2), addHeapObject(arg3));
}

const ClientFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_client_free(ptr >>> 0, 1));

export class Client {

    static __wrap(ptr) {
        ptr = ptr >>> 0;
        const obj = Object.create(Client.prototype);
        obj.__wbg_ptr = ptr;
        ClientFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }

    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ClientFinalization.unregister(this);
        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_client_free(ptr, 0);
    }
    /**
     * @returns {string}
     */
    __getClassname() {
        let deferred1_0;
        let deferred1_1;
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.client___getClassname(retptr, this.__wbg_ptr);
            var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
            var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
            deferred1_0 = r0;
            deferred1_1 = r1;
            return getStringFromWasm0(r0, r1);
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
            wasm.__wbindgen_export_3(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @param {Function} send_request
     * @param {Function | null} [close]
     */
    constructor(send_request, close) {
        const ret = wasm.client_new(addHeapObject(send_request), isLikeNone(close) ? 0 : addHeapObject(close));
        this.__wbg_ptr = ret >>> 0;
        ClientFinalization.register(this, this.__wbg_ptr, this);
        return this;
    }
    /**
     * @param {Function} on_response
     * @returns {ProxySession}
     */
    new_proxy_session(on_response) {
        try {
            const ret = wasm.client_new_proxy_session(this.__wbg_ptr, addBorrowedObject(on_response));
            return ProxySession.__wrap(ret);
        } finally {
            heap[stack_pointer++] = undefined;
        }
    }
    /**
     * @returns {Promise<void>}
     */
    init() {
        const ret = wasm.client_init(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @param {any} value
     * @returns {Promise<void>}
     */
    handle_response(value) {
        const ret = wasm.client_handle_response(this.__wbg_ptr, addHeapObject(value));
        return takeObject(ret);
    }
    /**
     * @param {string | null} [error]
     * @param {Function | null} [reconnect]
     * @returns {Promise<void>}
     */
    handle_error(error, reconnect) {
        var ptr0 = isLikeNone(error) ? 0 : passStringToWasm0(error, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        var len0 = WASM_VECTOR_LEN;
        const ret = wasm.client_handle_error(this.__wbg_ptr, ptr0, len0, isLikeNone(reconnect) ? 0 : addHeapObject(reconnect));
        return takeObject(ret);
    }
    /**
     * @param {Function} callback
     * @returns {Promise<number>}
     */
    on_error(callback) {
        const ret = wasm.client_on_error(this.__wbg_ptr, addHeapObject(callback));
        return takeObject(ret);
    }
    /**
     * @param {string | ArrayBuffer | Record<string, unknown[]> | Record<string, unknown>[]} value
     * @param {TableInitOptions | null} [options]
     * @returns {Promise<Table>}
     */
    table(value, options) {
        const ret = wasm.client_table(this.__wbg_ptr, addHeapObject(value), isLikeNone(options) ? 0 : addHeapObject(options));
        return takeObject(ret);
    }
    /**
     * @returns {any}
     */
    terminate() {
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.client_terminate(retptr, this.__wbg_ptr);
            var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
            var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
            var r2 = getDataViewMemory0().getInt32(retptr + 4 * 2, true);
            if (r2) {
                throw takeObject(r1);
            }
            return takeObject(r0);
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
        }
    }
    /**
     * @param {string} entity_id
     * @returns {Promise<Table>}
     */
    open_table(entity_id) {
        const ptr0 = passStringToWasm0(entity_id, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.client_open_table(this.__wbg_ptr, ptr0, len0);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    get_hosted_table_names() {
        const ret = wasm.client_get_hosted_table_names(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @param {Function} on_update_js
     * @returns {Promise<number>}
     */
    on_hosted_tables_update(on_update_js) {
        const ret = wasm.client_on_hosted_tables_update(this.__wbg_ptr, addHeapObject(on_update_js));
        return takeObject(ret);
    }
    /**
     * @param {number} update_id
     * @returns {Promise<void>}
     */
    remove_hosted_tables_update(update_id) {
        const ret = wasm.client_remove_hosted_tables_update(this.__wbg_ptr, update_id);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    system_info() {
        const ret = wasm.client_system_info(this.__wbg_ptr);
        return takeObject(ret);
    }
}

const ColumnDropDownElementFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_columndropdownelement_free(ptr >>> 0, 1));

export class ColumnDropDownElement {

    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ColumnDropDownElementFinalization.unregister(this);
        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_columndropdownelement_free(ptr, 0);
    }
}

const CopyDropDownMenuElementFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_copydropdownmenuelement_free(ptr >>> 0, 1));

export class CopyDropDownMenuElement {

    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        CopyDropDownMenuElementFinalization.unregister(this);
        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_copydropdownmenuelement_free(ptr, 0);
    }
    /**
     * @param {HTMLElement} elem
     */
    constructor(elem) {
        const ret = wasm.copydropdownmenuelement_new(addHeapObject(elem));
        this.__wbg_ptr = ret >>> 0;
        CopyDropDownMenuElementFinalization.register(this, this.__wbg_ptr, this);
        return this;
    }
    /**
     * @param {HTMLElement} target
     */
    open(target) {
        wasm.copydropdownmenuelement_open(this.__wbg_ptr, addHeapObject(target));
    }
    hide() {
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.copydropdownmenuelement_hide(retptr, this.__wbg_ptr);
            var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
            var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
            if (r1) {
                throw takeObject(r0);
            }
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
        }
    }
    /**
     * Internal Only.
     *
     * Set this custom element model's raw pointer.
     * @param {PerspectiveViewerElement} parent
     */
    set_model(parent) {
        _assertClass(parent, PerspectiveViewerElement);
        wasm.copydropdownmenuelement_set_model(this.__wbg_ptr, parent.__wbg_ptr);
    }
    connected_callback() {
        wasm.copydropdownmenuelement_connected_callback(this.__wbg_ptr);
    }
}

const ExportDropDownMenuElementFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_exportdropdownmenuelement_free(ptr >>> 0, 1));

export class ExportDropDownMenuElement {

    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ExportDropDownMenuElementFinalization.unregister(this);
        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_exportdropdownmenuelement_free(ptr, 0);
    }
    /**
     * @param {HTMLElement} elem
     */
    constructor(elem) {
        const ret = wasm.copydropdownmenuelement_new(addHeapObject(elem));
        this.__wbg_ptr = ret >>> 0;
        ExportDropDownMenuElementFinalization.register(this, this.__wbg_ptr, this);
        return this;
    }
    /**
     * @param {HTMLElement} target
     */
    open(target) {
        wasm.exportdropdownmenuelement_open(this.__wbg_ptr, addHeapObject(target));
    }
    hide() {
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.exportdropdownmenuelement_hide(retptr, this.__wbg_ptr);
            var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
            var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
            if (r1) {
                throw takeObject(r0);
            }
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
        }
    }
    /**
     * Internal Only.
     *
     * Set this custom element model's raw pointer.
     * @param {PerspectiveViewerElement} parent
     */
    set_model(parent) {
        _assertClass(parent, PerspectiveViewerElement);
        wasm.exportdropdownmenuelement_set_model(this.__wbg_ptr, parent.__wbg_ptr);
    }
    connected_callback() {
        wasm.copydropdownmenuelement_connected_callback(this.__wbg_ptr);
    }
}

const FilterDropDownElementFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_filterdropdownelement_free(ptr >>> 0, 1));

export class FilterDropDownElement {

    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        FilterDropDownElementFinalization.unregister(this);
        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_filterdropdownelement_free(ptr, 0);
    }
}

const FunctionDropDownElementFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_functiondropdownelement_free(ptr >>> 0, 1));

export class FunctionDropDownElement {

    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        FunctionDropDownElementFinalization.unregister(this);
        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_functiondropdownelement_free(ptr, 0);
    }
}

const PerspectiveDebugPluginElementFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_perspectivedebugpluginelement_free(ptr >>> 0, 1));
/**
 * The `<perspective-viewer-plugin>` element.
 *
 * The default perspective plugin which is registered and activated
 * automcatically when a `<perspective-viewer>` is loaded without plugins.
 * While you will not typically instantiate this class directly, it is simple
 * enough to function as a good "default" plugin implementation which can be
 * extended to create custom plugins.
 *
 * # Example
 * ```javascript
 * class MyPlugin extends customElements.get("perspective-viewer-plugin") {
 *    // Custom plugin overrides
 * }
 * ```
 */
export class PerspectiveDebugPluginElement {

    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        PerspectiveDebugPluginElementFinalization.unregister(this);
        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_perspectivedebugpluginelement_free(ptr, 0);
    }
    /**
     * @param {HTMLElement} elem
     */
    constructor(elem) {
        const ret = wasm.perspectivedebugpluginelement_new(addHeapObject(elem));
        this.__wbg_ptr = ret >>> 0;
        PerspectiveDebugPluginElementFinalization.register(this, this.__wbg_ptr, this);
        return this;
    }
    /**
     * @returns {string}
     */
    get name() {
        let deferred1_0;
        let deferred1_1;
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.perspectivedebugpluginelement_name(retptr, this.__wbg_ptr);
            var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
            var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
            deferred1_0 = r0;
            deferred1_1 = r1;
            return getStringFromWasm0(r0, r1);
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
            wasm.__wbindgen_export_3(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {string}
     */
    get select_mode() {
        let deferred1_0;
        let deferred1_1;
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.perspectivedebugpluginelement_select_mode(retptr, this.__wbg_ptr);
            var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
            var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
            deferred1_0 = r0;
            deferred1_1 = r1;
            return getStringFromWasm0(r0, r1);
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
            wasm.__wbindgen_export_3(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {any}
     */
    get min_config_columns() {
        const ret = wasm.perspectivedebugpluginelement_config_column_names(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {any}
     */
    get config_column_names() {
        const ret = wasm.perspectivedebugpluginelement_config_column_names(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @param {View} view
     * @returns {Promise<any>}
     */
    update(view) {
        _assertClass(view, View);
        const ret = wasm.perspectivedebugpluginelement_draw(this.__wbg_ptr, view.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * # Notes
     *
     * When you pass a `wasm_bindgen` wrapped type _into_ Rust, it acts like a
     * move. Ergo, if you replace the `&` in the `view` argument, the JS copy
     * of the `View` will be invalid
     * @param {View} view
     * @returns {Promise<any>}
     */
    draw(view) {
        _assertClass(view, View);
        const ret = wasm.perspectivedebugpluginelement_draw(this.__wbg_ptr, view.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    clear() {
        const ret = wasm.perspectivedebugpluginelement_clear(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    resize() {
        const ret = wasm.perspectivedebugpluginelement_clear(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    restyle() {
        const ret = wasm.perspectivedebugpluginelement_clear(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    save() {
        const ret = wasm.perspectivedebugpluginelement_clear(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    restore() {
        const ret = wasm.perspectivedebugpluginelement_clear(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    delete() {
        const ret = wasm.perspectivedebugpluginelement_clear(this.__wbg_ptr);
        return takeObject(ret);
    }
    connectedCallback() {
        wasm.perspectivedebugpluginelement_connectedCallback(this.__wbg_ptr);
    }
}

const PerspectiveViewerElementFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_perspectiveviewerelement_free(ptr >>> 0, 1));
/**
 * The `<perspective-viewer>` custom element.
 *
 * # JavaScript Examples
 *
 * Create a new `<perspective-viewer>`:
 *
 * ```javascript
 * const viewer = document.createElement("perspective-viewer");
 * window.body.appendChild(viewer);
 * ```
 */
export class PerspectiveViewerElement {

    static __wrap(ptr) {
        ptr = ptr >>> 0;
        const obj = Object.create(PerspectiveViewerElement.prototype);
        obj.__wbg_ptr = ptr;
        PerspectiveViewerElementFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }

    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        PerspectiveViewerElementFinalization.unregister(this);
        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_perspectiveviewerelement_free(ptr, 0);
    }
    /**
     * @param {HTMLElement} elem
     */
    constructor(elem) {
        const ret = wasm.perspectiveviewerelement_new(addHeapObject(elem));
        this.__wbg_ptr = ret >>> 0;
        PerspectiveViewerElementFinalization.register(this, this.__wbg_ptr, this);
        return this;
    }
    connectedCallback() {
        wasm.perspectiveviewerelement_connectedCallback(this.__wbg_ptr);
    }
    /**
     * Loads a [`Table`] (or rather, a Javascript `Promise` which returns a
     * [`Table`]) in this viewer.
     *
     * When [`PerspectiveViewerElement::load`] resolves, the first frame of the
     * UI + visualization is guaranteed to have been drawn. Awaiting the result
     * of this method in a `try`/`catch` block will capture any errors
     * thrown during the loading process, or from the [`Table`] `Promise`
     * itself.
     *
     * A [`Table`] can be created using the
     * [`@finos/perspective`](https://www.npmjs.com/package/@finos/perspective)
     * library from NPM (see [`perspective_js`] documentation for details).
     *
     * # JavaScript Examples
     *
     * ```javascript
     * import perspective from "@finos/perspective";
     *
     * const worker = await perspective.worker();
     * viewer.load(worker.table("x,y\n1,2"));
     * ```
     * @param {any} table
     * @returns {Promise<any>}
     */
    load(table) {
        const ret = wasm.perspectiveviewerelement_load(this.__wbg_ptr, addHeapObject(table));
        return takeObject(ret);
    }
    /**
     * Delete the internal [`View`] and all associated state, rendering this
     * `<perspective-viewer>` unusable and freeing all associated resources.
     * Does not delete the supplied [`Table`] (as this is constructed by the
     * callee).
     *
     * <div class="warning">
     *
     * Allowing a `<perspective-viewer>` to be garbage-collected
     * without calling [`PerspectiveViewerElement::delete`] will leak WASM
     * memory!
     *
     * </div>
     *
     * # JavaScript Examples
     *
     * ```javascript
     * await viewer.delete();
     * ```
     * @returns {Promise<any>}
     */
    delete() {
        const ret = wasm.perspectiveviewerelement_delete(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Get the underlying [`View`] for this viewer.
     *
     * Use this method to get promgrammatic access to the [`View`] as currently
     * configured by the user, for e.g. serializing as an
     * [Apache Arrow](https://arrow.apache.org/) before passing to another
     * library.
     *
     * The [`View`] returned by this method is owned by the
     * [`PerspectiveViewerElement`] and may be _invalidated_ by
     * [`View::delete`] at any time. Plugins which rely on this [`View`] for
     * their [`HTMLPerspectiveViewerPluginElement::draw`] implementations
     * should treat this condition as a _cancellation_ by silently aborting on
     * "View already deleted" errors from method calls.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * const view = await viewer.getView();
     * ```
     * @returns {Promise<any>}
     */
    getView() {
        const ret = wasm.perspectiveviewerelement_getView(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Get the underlying [`Table`] for this viewer (as passed to
     * [`PerspectiveViewerElement::load`]).
     *
     * # Arguments
     *
     * - `wait_for_table` - whether to wait for
     *   [`PerspectiveViewerElement::load`] to be called, or fail immediately
     *   if [`PerspectiveViewerElement::load`] has not yet been called.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * const table = await viewer.getTable();
     * ```
     * @param {boolean | null} [wait_for_table]
     * @returns {Promise<any>}
     */
    getTable(wait_for_table) {
        const ret = wasm.perspectiveviewerelement_getTable(this.__wbg_ptr, isLikeNone(wait_for_table) ? 0xFFFFFF : wait_for_table ? 1 : 0);
        return takeObject(ret);
    }
    /**
     * Get render statistics. Some fields of the returned stats object are
     * relative to the last time [`PerspectiveViewerElement::getRenderStats`]
     * was called, ergo calling this method resets these fields.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * const {virtual_fps, actual_fps} = await viewer.getRenderStats();
     * ```
     * @returns {any}
     */
    getRenderStats() {
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.perspectiveviewerelement_getRenderStats(retptr, this.__wbg_ptr);
            var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
            var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
            var r2 = getDataViewMemory0().getInt32(retptr + 4 * 2, true);
            if (r2) {
                throw takeObject(r1);
            }
            return takeObject(r0);
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
        }
    }
    /**
     * Flush any pending modifications to this `<perspective-viewer>`.  Since
     * `<perspective-viewer>`'s API is almost entirely `async`, it may take
     * some milliseconds before any user-initiated changes to the [`View`]
     * affects the rendered element.  If you want to make sure all pending
     * actions have been rendered, call and await [`Self::flush`].
     *
     * [`Self::flush`] will resolve immediately if there is no [`Table`] set.
     *
     * # JavaScript Examples
     *
     * In this example, [`Self::restore`] is called without `await`, but the
     * eventual render which results from this call can still be awaited by
     * immediately awaiting [`Self::flush`] instead.
     *
     * ```javascript
     * viewer.restore(config);
     * await viewer.flush();
     * ```
     * @returns {Promise<any>}
     */
    flush() {
        const ret = wasm.perspectiveviewerelement_flush(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Restores this element from a full/partial
     * [`perspective_js::JsViewConfig`].
     *
     * One of the best ways to use [`Self::restore`] is by first configuring
     * a `<perspective-viewer>` as you wish, then using either the `Debug`
     * panel or "Copy" -> "config.json" from the toolbar menu to snapshot
     * the [`Self::restore`] argument as JSON.
     *
     * # Arguments
     *
     * - `update` - The config to restore to, as returned by [`Self::save`] in
     *   either "json", "string" or "arraybuffer" format.
     *
     * # JavaScript Examples
     *
     * Apply a `group_by` to the current [`View`], without modifying/resetting
     * other fields:
     *
     * ```javascript
     * await viewer.restore({group_by: ["State"]});
     * ```
     * @param {any} update
     * @returns {Promise<any>}
     */
    restore(update) {
        const ret = wasm.perspectiveviewerelement_restore(this.__wbg_ptr, addHeapObject(update));
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    resetError() {
        const ret = wasm.perspectiveviewerelement_resetError(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Save this element to serialized state object, one which can be restored
     * via the [`Self::restore`] method.
     *
     * # Arguments
     *
     * - `format` - Supports "json" (default), "arraybuffer" or "string".
     *
     * # JavaScript Examples
     *
     * Get the current `group_by` setting:
     *
     * ```javascript
     * const {group_by} = await viewer.restore();
     * ```
     *
     * Reset workflow attached to an external button `myResetButton`:
     *
     * ```javascript
     * const token = await viewer.save();
     * myResetButton.addEventListener("clien", async () => {
     *     await viewer.restore(token);
     * });
     * ```
     * @param {string | null} [format]
     * @returns {Promise<any>}
     */
    save(format) {
        var ptr0 = isLikeNone(format) ? 0 : passStringToWasm0(format, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        var len0 = WASM_VECTOR_LEN;
        const ret = wasm.perspectiveviewerelement_save(this.__wbg_ptr, ptr0, len0);
        return takeObject(ret);
    }
    /**
     * Download this viewer's internal [`View`] data as a `.csv` file.
     *
     * # Arguments
     *
     * - `flat` - Whether to use the current [`perspective_js::JsViewConfig`]
     *   to generate this data, or use the default.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * myDownloadButton.addEventListener("click", async () => {
     *     await viewer.download();
     * })
     * ```
     * @param {boolean | null} [flat]
     * @returns {Promise<any>}
     */
    download(flat) {
        const ret = wasm.perspectiveviewerelement_download(this.__wbg_ptr, isLikeNone(flat) ? 0xFFFFFF : flat ? 1 : 0);
        return takeObject(ret);
    }
    /**
     * Copy this viewer's `View` or `Table` data as CSV to the system
     * clipboard.
     *
     * # Arguments
     *
     * - `method` - The `ExportMethod` (serialized as a `String`) to use to
     *   render the data to the Clipboard.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * myDownloadButton.addEventListener("click", async () => {
     *     await viewer.copy();
     * })
     * ```
     * @param {string | null} [method]
     * @returns {Promise<any>}
     */
    copy(method) {
        const ret = wasm.perspectiveviewerelement_copy(this.__wbg_ptr, isLikeNone(method) ? 0 : addHeapObject(method));
        return takeObject(ret);
    }
    /**
     * Reset the viewer's `ViewerConfig` to the default.
     *
     * # Arguments
     *
     * - `reset_all` - If set, will clear expressions and column settings as
     *   well.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * await viewer.reset();
     * ```
     * @param {boolean | null} [reset_all]
     * @returns {Promise<any>}
     */
    reset(reset_all) {
        const ret = wasm.perspectiveviewerelement_reset(this.__wbg_ptr, isLikeNone(reset_all) ? 0xFFFFFF : reset_all ? 1 : 0);
        return takeObject(ret);
    }
    /**
     * Recalculate the viewer's dimensions and redraw.
     *
     * Use this method to tell `<perspective-viewer>` its dimensions have
     * changed when auto-size mode has been disabled via [`Self::setAutoSize`].
     * [`Self::resize`] resolves when the resize-initiated redraw of this
     * element has completed.
     *
     * # Arguments
     *
     * - `force` - If [`Self::resize`] is called with `false` or without an
     *   argument, and _auto-size_ mode is enabled via [`Self::setAutoSize`],
     *   [`Self::resize`] will log a warning and auto-disable auto-size mode.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * await viewer.resize(true)
     * ```
     * @param {boolean | null} [force]
     * @returns {Promise<any>}
     */
    resize(force) {
        const ret = wasm.perspectiveviewerelement_resize(this.__wbg_ptr, isLikeNone(force) ? 0xFFFFFF : force ? 1 : 0);
        return takeObject(ret);
    }
    /**
     * Sets the auto-size behavior of this component.
     *
     * When `true`, this `<perspective-viewer>` will register a
     * `ResizeObserver` on itself and call [`Self::resize`] whenever its own
     * dimensions change. However, when embedded in a larger application
     * context, you may want to call [`Self::resize`] manually to avoid
     * over-rendering; in this case auto-sizing can be disabled via this
     * method. Auto-size behavior is enabled by default.
     *
     * # Arguments
     *
     * - `autosize` - Whether to enable `auto-size` behavior or not.
     *
     * # JavaScript Examples
     *
     * Disable auto-size behavior:
     *
     * ```javascript
     * viewer.setAutoSize(false);
     * ```
     * @param {boolean} autosize
     */
    setAutoSize(autosize) {
        wasm.perspectiveviewerelement_setAutoSize(this.__wbg_ptr, autosize);
    }
    /**
     * Sets the auto-pause behavior of this component.
     *
     * When `true`, this `<perspective-viewer>` will register an
     * `IntersectionObserver` on itself and subsequently skip rendering
     * whenever its viewport visibility changes. Auto-pause is enabled by
     * default.
     *
     * # Arguments
     *
     * - `autopause` Whether to enable `auto-pause` behavior or not.
     *
     * # JavaScript Examples
     *
     * Disable auto-size behavior:
     *
     * ```javascript
     * viewer.setAutoPause(false);
     * ```
     * @param {boolean} autopause
     */
    setAutoPause(autopause) {
        wasm.perspectiveviewerelement_setAutoPause(this.__wbg_ptr, autopause);
    }
    /**
     * Return a [`perspective_js::JsViewWindow`] for the currently selected
     * region.
     * @returns {ViewWindow | undefined}
     */
    getSelection() {
        const ret = wasm.perspectiveviewerelement_getSelection(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Set the selection [`perspective_js::JsViewWindow`] for this element.
     * @param {ViewWindow | null} [window]
     */
    setSelection(window) {
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.perspectiveviewerelement_setSelection(retptr, this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
            var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
            var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
            if (r1) {
                throw takeObject(r0);
            }
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
        }
    }
    /**
     * Get this viewer's edit port for the currently loaded [`Table`] (see
     * [`Table::update`] for details on ports).
     * @returns {number}
     */
    getEditPort() {
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.perspectiveviewerelement_getEditPort(retptr, this.__wbg_ptr);
            var r0 = getDataViewMemory0().getFloat64(retptr + 8 * 0, true);
            var r2 = getDataViewMemory0().getInt32(retptr + 4 * 2, true);
            var r3 = getDataViewMemory0().getInt32(retptr + 4 * 3, true);
            if (r3) {
                throw takeObject(r2);
            }
            return r0;
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
        }
    }
    /**
     * Restyle all plugins from current document.
     *
     * <div class="warning">
     *
     * [`Self::restyleElement`] _must_ be called for many runtime changes to
     * CSS properties to be reflected in an already-rendered
     * `<perspective-viewer>`.
     *
     * </div>
     *
     * # JavaScript Examples
     *
     * ```javascript
     * viewer.style = "--icon--color: red";
     * await viewer.restyleElement();
     * ```
     * @returns {Promise<any>}
     */
    restyleElement() {
        const ret = wasm.perspectiveviewerelement_restyleElement(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Set the available theme names available in the status bar UI.
     *
     * Calling [`Self::resetThemes`] may cause the current theme to switch,
     * if e.g. the new theme set does not contain the current theme.
     *
     * # JavaScript Examples
     *
     * Restrict `<perspective-viewer>` theme options to _only_ default light
     * and dark themes, regardless of what is auto-detected from the page's
     * CSS:
     *
     * ```javascript
     * viewer.resetThemes(["Pro Light", "Pro Dark"])
     * ```
     * @param {any[] | null} [themes]
     * @returns {Promise<any>}
     */
    resetThemes(themes) {
        var ptr0 = isLikeNone(themes) ? 0 : passArrayJsValueToWasm0(themes, wasm.__wbindgen_export_0);
        var len0 = WASM_VECTOR_LEN;
        const ret = wasm.perspectiveviewerelement_resetThemes(this.__wbg_ptr, ptr0, len0);
        return takeObject(ret);
    }
    /**
     * Determines the render throttling behavior. Can be an integer, for
     * millisecond window to throttle render event; or, if `None`, adaptive
     * throttling will be calculated from the measured render time of the
     * last 5 frames.
     *
     * # Arguments
     *
     * - `throttle` - The throttle rate in milliseconds (f64), or `None` for
     *   adaptive throttling.
     *
     * # JavaScript Examples
     *
     * Only draws at most 1 frame/sec:
     *
     * ```rust
     * viewer.setThrottle(1000);
     * ```
     * @param {number | null} [val]
     */
    setThrottle(val) {
        wasm.perspectiveviewerelement_setThrottle(this.__wbg_ptr, !isLikeNone(val), isLikeNone(val) ? 0 : val);
    }
    /**
     * Toggle (or force) the config panel open/closed.
     *
     * # Arguments
     *
     * - `force` - Force the state of the panel open or closed, or `None` to
     *   toggle.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * await viewer.toggleConfig();
     * ```
     * @param {boolean | null} [force]
     * @returns {Promise<any>}
     */
    toggleConfig(force) {
        const ret = wasm.perspectiveviewerelement_toggleConfig(this.__wbg_ptr, isLikeNone(force) ? 0xFFFFFF : force ? 1 : 0);
        return takeObject(ret);
    }
    /**
     * Get an `Array` of all of the plugin custom elements registered for this
     * element. This may not include plugins which called
     * [`registerPlugin`] after the host has rendered for the first time.
     * @returns {Array<any>}
     */
    getAllPlugins() {
        const ret = wasm.perspectiveviewerelement_getAllPlugins(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Gets a plugin Custom Element with the `name` field, or get the active
     * plugin if no `name` is provided.
     *
     * # Arguments
     *
     * - `name` - The `name` property of a perspective plugin Custom Element,
     *   or `None` for the active plugin's Custom Element.
     * @param {string | null} [name]
     * @returns {any}
     */
    getPlugin(name) {
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            var ptr0 = isLikeNone(name) ? 0 : passStringToWasm0(name, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
            var len0 = WASM_VECTOR_LEN;
            wasm.perspectiveviewerelement_getPlugin(retptr, this.__wbg_ptr, ptr0, len0);
            var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
            var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
            var r2 = getDataViewMemory0().getInt32(retptr + 4 * 2, true);
            if (r2) {
                throw takeObject(r1);
            }
            return takeObject(r0);
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
        }
    }
    /**
     * Create a new JavaScript Heap reference for this model instance.
     * @returns {PerspectiveViewerElement}
     */
    get_model() {
        const ret = wasm.perspectiveviewerelement_get_model(this.__wbg_ptr);
        return PerspectiveViewerElement.__wrap(ret);
    }
    /**
     * Asynchronously opens the column settings for a specific column.
     * When finished, the `<perspective-viewer>` element will emit a
     * "perspective-toggle-column-settings" CustomEvent.
     * The event's details property has two fields: `{open: bool, column_name?:
     * string}`. The CustomEvent is also fired whenever the user toggles the
     * sidebar manually.
     * @param {string} column_name
     * @returns {Promise<any>}
     */
    toggleColumnSettings(column_name) {
        const ptr0 = passStringToWasm0(column_name, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.perspectiveviewerelement_toggleColumnSettings(this.__wbg_ptr, ptr0, len0);
        return takeObject(ret);
    }
    /**
     * Force open the settings for a particular column. Pass `null` to close
     * the column settings panel. See [`Self::toggleColumnSettings`] for more.
     * @param {string | null} [column_name]
     * @param {boolean | null} [toggle]
     * @returns {Promise<any>}
     */
    openColumnSettings(column_name, toggle) {
        var ptr0 = isLikeNone(column_name) ? 0 : passStringToWasm0(column_name, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        var len0 = WASM_VECTOR_LEN;
        const ret = wasm.perspectiveviewerelement_openColumnSettings(this.__wbg_ptr, ptr0, len0, isLikeNone(toggle) ? 0xFFFFFF : toggle ? 1 : 0);
        return takeObject(ret);
    }
}

const ProxySessionFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_proxysession_free(ptr >>> 0, 1));

export class ProxySession {

    static __wrap(ptr) {
        ptr = ptr >>> 0;
        const obj = Object.create(ProxySession.prototype);
        obj.__wbg_ptr = ptr;
        ProxySessionFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }

    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ProxySessionFinalization.unregister(this);
        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_proxysession_free(ptr, 0);
    }
    /**
     * @param {Client} client
     * @param {Function} on_response
     */
    constructor(client, on_response) {
        try {
            _assertClass(client, Client);
            const ret = wasm.client_new_proxy_session(client.__wbg_ptr, addBorrowedObject(on_response));
            this.__wbg_ptr = ret >>> 0;
            ProxySessionFinalization.register(this, this.__wbg_ptr, this);
            return this;
        } finally {
            heap[stack_pointer++] = undefined;
        }
    }
    /**
     * @param {any} value
     * @returns {Promise<void>}
     */
    handle_request(value) {
        const ret = wasm.proxysession_handle_request(this.__wbg_ptr, addHeapObject(value));
        return takeObject(ret);
    }
    /**
     * @returns {Promise<void>}
     */
    poll() {
        const ret = wasm.proxysession_poll(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<void>}
     */
    close() {
        const ptr = this.__destroy_into_raw();
        const ret = wasm.proxysession_close(ptr);
        return takeObject(ret);
    }
}

const TableFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_table_free(ptr >>> 0, 1));

export class Table {

    static __wrap(ptr) {
        ptr = ptr >>> 0;
        const obj = Object.create(Table.prototype);
        obj.__wbg_ptr = ptr;
        TableFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }

    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        TableFinalization.unregister(this);
        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_table_free(ptr, 0);
    }
    /**
     * @returns {string}
     */
    __getClassname() {
        let deferred1_0;
        let deferred1_1;
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.table___getClassname(retptr, this.__wbg_ptr);
            var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
            var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
            deferred1_0 = r0;
            deferred1_1 = r1;
            return getStringFromWasm0(r0, r1);
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
            wasm.__wbindgen_export_3(deferred1_0, deferred1_1, 1);
        }
    }
    /**
     * @returns {Promise<string | undefined>}
     */
    get_index() {
        const ret = wasm.table_get_index(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<Client>}
     */
    get_client() {
        const ret = wasm.table_get_client(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<string>}
     */
    get_name() {
        const ret = wasm.table_get_name(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<number | undefined>}
     */
    get_limit() {
        const ret = wasm.table_get_limit(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<void>}
     */
    clear() {
        const ret = wasm.table_clear(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<void>}
     */
    delete() {
        const ret = wasm.table_delete(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<number>}
     */
    size() {
        const ret = wasm.table_size(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    schema() {
        const ret = wasm.table_schema(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    columns() {
        const ret = wasm.table_columns(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<number>}
     */
    make_port() {
        const ret = wasm.table_make_port(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @param {Function} on_delete
     * @returns {Promise<number>}
     */
    on_delete(on_delete) {
        const ret = wasm.table_on_delete(this.__wbg_ptr, addHeapObject(on_delete));
        return takeObject(ret);
    }
    /**
     * @param {number} callback_id
     * @returns {Promise<any>}
     */
    remove_delete(callback_id) {
        const ret = wasm.table_remove_delete(this.__wbg_ptr, callback_id);
        return takeObject(ret);
    }
    /**
     * @param {any} value
     * @param {UpdateOptions | null} [options]
     * @returns {Promise<void>}
     */
    remove(value, options) {
        const ret = wasm.table_remove(this.__wbg_ptr, addHeapObject(value), isLikeNone(options) ? 0 : addHeapObject(options));
        return takeObject(ret);
    }
    /**
     * @param {any} input
     * @param {UpdateOptions | null} [options]
     * @returns {Promise<void>}
     */
    replace(input, options) {
        const ret = wasm.table_replace(this.__wbg_ptr, addHeapObject(input), isLikeNone(options) ? 0 : addHeapObject(options));
        return takeObject(ret);
    }
    /**
     * @param {string | ArrayBuffer | Record<string, unknown[]> | Record<string, unknown>[]} input
     * @param {UpdateOptions | null} [options]
     * @returns {Promise<void>}
     */
    update(input, options) {
        const ret = wasm.table_update(this.__wbg_ptr, addHeapObject(input), isLikeNone(options) ? 0 : addHeapObject(options));
        return takeObject(ret);
    }
    /**
     * @param {ViewConfigUpdate | null} [config]
     * @returns {Promise<View>}
     */
    view(config) {
        const ret = wasm.table_view(this.__wbg_ptr, isLikeNone(config) ? 0 : addHeapObject(config));
        return takeObject(ret);
    }
    /**
     * @param {any} exprs
     * @returns {Promise<any>}
     */
    validate_expressions(exprs) {
        const ret = wasm.table_validate_expressions(this.__wbg_ptr, addHeapObject(exprs));
        return takeObject(ret);
    }
}

const ViewFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_view_free(ptr >>> 0, 1));

export class View {

    static __wrap(ptr) {
        ptr = ptr >>> 0;
        const obj = Object.create(View.prototype);
        obj.__wbg_ptr = ptr;
        ViewFinalization.register(obj, obj.__wbg_ptr, obj);
        return obj;
    }

    static __unwrap(jsValue) {
        if (!(jsValue instanceof View)) {
            return 0;
        }
        return jsValue.__destroy_into_raw();
    }

    __destroy_into_raw() {
        const ptr = this.__wbg_ptr;
        this.__wbg_ptr = 0;
        ViewFinalization.unregister(this);
        return ptr;
    }

    free() {
        const ptr = this.__destroy_into_raw();
        wasm.__wbg_view_free(ptr, 0);
    }
    /**
     * @returns {View}
     */
    __get_model() {
        const ret = wasm.view___get_model(this.__wbg_ptr);
        return View.__wrap(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    column_paths() {
        const ret = wasm.view_column_paths(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<void>}
     */
    delete() {
        const ret = wasm.view_delete(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    dimensions() {
        const ret = wasm.view_dimensions(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    expression_schema() {
        const ret = wasm.view_expression_schema(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    get_config() {
        const ret = wasm.view_get_config(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @param {string} name
     * @returns {Promise<Array<any>>}
     */
    get_min_max(name) {
        const ptr0 = passStringToWasm0(name, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len0 = WASM_VECTOR_LEN;
        const ret = wasm.view_get_min_max(this.__wbg_ptr, ptr0, len0);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<number>}
     */
    num_rows() {
        const ret = wasm.view_num_rows(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @returns {Promise<any>}
     */
    schema() {
        const ret = wasm.view_schema(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @param {ViewWindow | null} [window]
     * @returns {Promise<ArrayBuffer>}
     */
    to_arrow(window) {
        const ret = wasm.view_to_arrow(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * @param {ViewWindow | null} [window]
     * @returns {Promise<string>}
     */
    to_columns_string(window) {
        const ret = wasm.view_to_columns_string(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * @param {ViewWindow | null} [window]
     * @returns {Promise<object>}
     */
    to_columns(window) {
        const ret = wasm.view_to_columns(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * @param {ViewWindow | null} [window]
     * @returns {Promise<string>}
     */
    to_json_string(window) {
        const ret = wasm.view_to_json_string(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * @param {ViewWindow | null} [window]
     * @returns {Promise<Array<any>>}
     */
    to_json(window) {
        const ret = wasm.view_to_json(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * @param {ViewWindow | null} [window]
     * @returns {Promise<string>}
     */
    to_ndjson(window) {
        const ret = wasm.view_to_ndjson(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * @param {ViewWindow | null} [window]
     * @returns {Promise<string>}
     */
    to_csv(window) {
        const ret = wasm.view_to_csv(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * @param {Function} on_update_js
     * @param {OnUpdateOptions | null} [options]
     * @returns {Promise<number>}
     */
    on_update(on_update_js, options) {
        const ret = wasm.view_on_update(this.__wbg_ptr, addHeapObject(on_update_js), isLikeNone(options) ? 0 : addHeapObject(options));
        return takeObject(ret);
    }
    /**
     * @param {number} callback_id
     * @returns {Promise<void>}
     */
    remove_update(callback_id) {
        const ret = wasm.view_remove_update(this.__wbg_ptr, callback_id);
        return takeObject(ret);
    }
    /**
     * @param {Function} on_delete
     * @returns {Promise<number>}
     */
    on_delete(on_delete) {
        const ret = wasm.view_on_delete(this.__wbg_ptr, addHeapObject(on_delete));
        return takeObject(ret);
    }
    /**
     * @returns {Promise<number>}
     */
    num_columns() {
        const ret = wasm.view_num_columns(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * @param {number} callback_id
     * @returns {Promise<any>}
     */
    remove_delete(callback_id) {
        const ret = wasm.view_remove_delete(this.__wbg_ptr, callback_id);
        return takeObject(ret);
    }
    /**
     * @param {number} row_index
     * @returns {Promise<number>}
     */
    collapse(row_index) {
        const ret = wasm.view_collapse(this.__wbg_ptr, row_index);
        return takeObject(ret);
    }
    /**
     * @param {number} row_index
     * @returns {Promise<number>}
     */
    expand(row_index) {
        const ret = wasm.view_expand(this.__wbg_ptr, row_index);
        return takeObject(ret);
    }
    /**
     * @param {number} depth
     * @returns {Promise<void>}
     */
    set_depth(depth) {
        const ret = wasm.view_set_depth(this.__wbg_ptr, depth);
        return takeObject(ret);
    }
}

async function __wbg_load(module, imports) {
    if (typeof Response === 'function' && module instanceof Response) {
        if (typeof WebAssembly.instantiateStreaming === 'function') {
            try {
                return await WebAssembly.instantiateStreaming(module, imports);

            } catch (e) {
                if (module.headers.get('Content-Type') != 'application/wasm') {
                    console.warn("`WebAssembly.instantiateStreaming` failed because your server does not serve Wasm with `application/wasm` MIME type. Falling back to `WebAssembly.instantiate` which is slower. Original error:\n", e);

                } else {
                    throw e;
                }
            }
        }

        const bytes = await module.arrayBuffer();
        return await WebAssembly.instantiate(bytes, imports);

    } else {
        const instance = await WebAssembly.instantiate(module, imports);

        if (instance instanceof WebAssembly.Instance) {
            return { instance, module };

        } else {
            return instance;
        }
    }
}

function __wbg_get_imports() {
    const imports = {};
    imports.wbg = {};
    imports.wbg.__wbg_String_8f0eb39a4a4c2f66 = function(arg0, arg1) {
        const ret = String(getObject(arg1));
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_activeElement_269d90df98fa48af = function(arg0) {
        const ret = getObject(arg0).activeElement;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_addEventListener_086f56364d0f5f32 = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        getObject(arg0).addEventListener(getStringFromWasm0(arg1, arg2), getObject(arg3), getObject(arg4));
    }, arguments) };
    imports.wbg.__wbg_addEventListener_435e8c1f21f457b2 = function() { return handleError(function (arg0, arg1, arg2, arg3) {
        getObject(arg0).addEventListener(getStringFromWasm0(arg1, arg2), getObject(arg3));
    }, arguments) };
    imports.wbg.__wbg_add_8b20bdf6a0133c8d = function() { return handleError(function (arg0, arg1) {
        getObject(arg0).add(...getObject(arg1));
    }, arguments) };
    imports.wbg.__wbg_add_ad1d1783e738a5e9 = function() { return handleError(function (arg0, arg1, arg2) {
        getObject(arg0).add(getStringFromWasm0(arg1, arg2));
    }, arguments) };
    imports.wbg.__wbg_appendChild_7c5825d692053033 = function() { return handleError(function (arg0, arg1) {
        const ret = getObject(arg0).appendChild(getObject(arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_apply_9bb7fe8fff013a3f = function() { return handleError(function (arg0, arg1, arg2) {
        const ret = Reflect.apply(getObject(arg0), getObject(arg1), getObject(arg2));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_at_1abf0efc31a7fc6e = function(arg0, arg1) {
        const ret = getObject(arg0).at(arg1);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_attachShadow_ca706fa989deead3 = function() { return handleError(function (arg0, arg1) {
        const ret = getObject(arg0).attachShadow(getObject(arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_blur_d1200a579e3ccf9a = function() { return handleError(function (arg0) {
        getObject(arg0).blur();
    }, arguments) };
    imports.wbg.__wbg_body_a988e82424f68da9 = function(arg0) {
        const ret = getObject(arg0).body;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_bootstrap_ab0a742546b8edb0 = function(arg0, arg1, arg2, arg3, arg4, arg5) {
        const ret = bootstrap(getObject(arg0), getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4), takeObject(arg5));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_bubbles_7b5f623fa401eb0d = function(arg0) {
        const ret = getObject(arg0).bubbles;
        return ret;
    };
    imports.wbg.__wbg_buffer_bacd7706db793204 = function(arg0) {
        const ret = getObject(arg0).buffer;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_buffer_ef9774282e5dab94 = function(arg0) {
        const ret = getObject(arg0).buffer;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_button_cf393fc0a7773ee4 = function(arg0) {
        const ret = getObject(arg0).button;
        return ret;
    };
    imports.wbg.__wbg_byteLength_d52de988f95295b2 = function(arg0) {
        const ret = getObject(arg0).byteLength;
        return ret;
    };
    imports.wbg.__wbg_byteOffset_7fca107d7d193694 = function(arg0) {
        const ret = getObject(arg0).byteOffset;
        return ret;
    };
    imports.wbg.__wbg_cachekey_57601dac16343711 = function(arg0) {
        const ret = getObject(arg0).__yew_subtree_cache_key;
        return isLikeNone(ret) ? 0x100000001 : (ret) >>> 0;
    };
    imports.wbg.__wbg_call_0ad083564791763a = function() { return handleError(function (arg0, arg1) {
        const ret = getObject(arg0).call(getObject(arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_call_a34b6b4765f27be0 = function() { return handleError(function (arg0, arg1, arg2) {
        const ret = getObject(arg0).call(getObject(arg1), getObject(arg2));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_call_efe5a4db7065d1a2 = function() { return handleError(function (arg0, arg1, arg2, arg3) {
        const ret = getObject(arg0).call(getObject(arg1), getObject(arg2), getObject(arg3));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_cancelBubble_65c441507f8e665c = function(arg0) {
        const ret = getObject(arg0).cancelBubble;
        return ret;
    };
    imports.wbg.__wbg_canrendercolumnstyles_98006f96e6d73d7f = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        const ret = getObject(arg0).can_render_column_styles(getStringFromWasm0(arg1, arg2), arg3 === 0 ? undefined : getStringFromWasm0(arg3, arg4));
        return ret;
    }, arguments) };
    imports.wbg.__wbg_category_91400150136760fd = function(arg0, arg1) {
        const ret = getObject(arg1).category;
        var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        var len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_checked_e73ad150b9e38836 = function(arg0) {
        const ret = getObject(arg0).checked;
        return ret;
    };
    imports.wbg.__wbg_childNodes_03488c474413d1aa = function(arg0) {
        const ret = getObject(arg0).childNodes;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_children_f2103fad05de8500 = function(arg0) {
        const ret = getObject(arg0).children;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_classList_416e8612217ee162 = function(arg0) {
        const ret = getObject(arg0).classList;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_click_5c8cca1c6a10688c = function(arg0) {
        getObject(arg0).click();
    };
    imports.wbg.__wbg_clientHeight_64024d24c91afc9c = function(arg0) {
        const ret = getObject(arg0).clientHeight;
        return ret;
    };
    imports.wbg.__wbg_clientWidth_56ad62b4cfb4eb50 = function(arg0) {
        const ret = getObject(arg0).clientWidth;
        return ret;
    };
    imports.wbg.__wbg_clientX_3a92ca49f9e276d1 = function(arg0) {
        const ret = getObject(arg0).clientX;
        return ret;
    };
    imports.wbg.__wbg_clientY_8cf1e863a2e20fba = function(arg0) {
        const ret = getObject(arg0).clientY;
        return ret;
    };
    imports.wbg.__wbg_client_new = function(arg0) {
        const ret = Client.__wrap(arg0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_clipboard_87e941cdb1e85669 = function(arg0) {
        const ret = getObject(arg0).clipboard;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_cloneNode_007df7834aaa05c7 = function() { return handleError(function (arg0, arg1) {
        const ret = getObject(arg0).cloneNode(arg1 !== 0);
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_cloneNode_953136fba5daff6c = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).cloneNode();
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_columnstylecontrols_7a3ce3a47fcc7cbe = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        const ret = getObject(arg0).column_style_controls(getStringFromWasm0(arg1, arg2), arg3 === 0 ? undefined : getStringFromWasm0(arg3, arg4));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_composedPath_2bc173ac38e0a20e = function(arg0) {
        const ret = getObject(arg0).composedPath();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_configcolumnnames_add624771ee4a2ed = function(arg0) {
        const ret = getObject(arg0).config_column_names;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_contains_c317a65dc27794f3 = function(arg0, arg1) {
        const ret = getObject(arg0).contains(getObject(arg1));
        return ret;
    };
    imports.wbg.__wbg_contentRect_7e651226982a3f4f = function(arg0) {
        const ret = getObject(arg0).contentRect;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_createElementNS_76b20f860b18ad4e = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        const ret = getObject(arg0).createElementNS(arg1 === 0 ? undefined : getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_createElement_32c287e69e603e7e = function() { return handleError(function (arg0, arg1, arg2) {
        const ret = getObject(arg0).createElement(getStringFromWasm0(arg1, arg2));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_createObjectURL_79d470fef236d558 = function() { return handleError(function (arg0, arg1) {
        const ret = URL.createObjectURL(getObject(arg1));
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    }, arguments) };
    imports.wbg.__wbg_createTextNode_42cc1e035e528436 = function(arg0, arg1, arg2) {
        const ret = getObject(arg0).createTextNode(getStringFromWasm0(arg1, arg2));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_crypto_ed58b8e10a292839 = function(arg0) {
        const ret = getObject(arg0).crypto;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_cssRules_ccbd5a21d1b3a12b = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).cssRules;
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_dataTransfer_0dfb0466f6be620c = function(arg0) {
        const ret = getObject(arg0).dataTransfer;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_dataset_9555caf70b9cb0c1 = function(arg0) {
        const ret = getObject(arg0).dataset;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_debug_338493c12960e4a7 = function(arg0) {
        console.debug(getObject(arg0));
    };
    imports.wbg.__wbg_debug_f201c091a5d2019b = function(arg0, arg1, arg2, arg3) {
        console.debug(getObject(arg0), getObject(arg1), getObject(arg2), getObject(arg3));
    };
    imports.wbg.__wbg_delete_3484391133f24f74 = function(arg0) {
        getObject(arg0).delete();
    };
    imports.wbg.__wbg_delete_70d7e592a3a49c16 = function(arg0, arg1, arg2) {
        delete getObject(arg0)[getStringFromWasm0(arg1, arg2)];
    };
    imports.wbg.__wbg_dispatchEvent_68c6f2105f6be0f6 = function() { return handleError(function (arg0, arg1) {
        const ret = getObject(arg0).dispatchEvent(getObject(arg1));
        return ret;
    }, arguments) };
    imports.wbg.__wbg_document_da63b92bac45c6f9 = function(arg0) {
        const ret = getObject(arg0).document;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_done_f4c254830a095eaf = function(arg0) {
        const ret = getObject(arg0).done;
        return ret;
    };
    imports.wbg.__wbg_draw_581118fb01e53d16 = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        const ret = getObject(arg0).draw(View.__wrap(arg1), arg2 === 0x100000001 ? undefined : arg2, arg3 === 0x100000001 ? undefined : arg3, arg4 !== 0);
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_entries_83beb641792ccb9c = function(arg0) {
        const ret = Object.entries(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_error_3c7d958458bf649b = function(arg0, arg1) {
        var v0 = getArrayJsValueFromWasm0(arg0, arg1).slice();
        wasm.__wbindgen_export_3(arg0, arg1 * 4, 4);
        console.error(...v0);
    };
    imports.wbg.__wbg_error_7534b8e9a36f1ab4 = function(arg0, arg1) {
        let deferred0_0;
        let deferred0_1;
        try {
            deferred0_0 = arg0;
            deferred0_1 = arg1;
            console.error(getStringFromWasm0(arg0, arg1));
        } finally {
            wasm.__wbindgen_export_3(deferred0_0, deferred0_1, 1);
        }
    };
    imports.wbg.__wbg_error_852b114509bed301 = function(arg0) {
        console.error(getObject(arg0));
    };
    imports.wbg.__wbg_error_94252a8e90b35b8e = function(arg0, arg1, arg2, arg3) {
        console.error(getObject(arg0), getObject(arg1), getObject(arg2), getObject(arg3));
    };
    imports.wbg.__wbg_error_afd05d3fc1f414ce = function(arg0, arg1) {
        console.error(getObject(arg0), getObject(arg1));
    };
    imports.wbg.__wbg_family_df8406822a165a00 = function(arg0, arg1) {
        const ret = getObject(arg1).family;
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_focus_4118597a9430279f = function() { return handleError(function (arg0) {
        getObject(arg0).focus();
    }, arguments) };
    imports.wbg.__wbg_fonts_5e9775f930f6db58 = function(arg0) {
        const ret = getObject(arg0).fonts;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_format_dd85a05737f53b26 = function(arg0) {
        const ret = getObject(arg0).format;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_from_3aa0fcaa8eef0104 = function(arg0) {
        const ret = Array.from(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_getAttribute_8ea59c069aa8c40f = function(arg0, arg1, arg2, arg3) {
        const ret = getObject(arg1).getAttribute(getStringFromWasm0(arg2, arg3));
        var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        var len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_getBoundingClientRect_d38f67f3e23939f4 = function(arg0) {
        const ret = getObject(arg0).getBoundingClientRect();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_getComputedStyle_bd01b85926809933 = function() { return handleError(function (arg0, arg1) {
        const ret = getObject(arg0).getComputedStyle(getObject(arg1));
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_getEntriesByName_6fb8ccc67553373f = function(arg0, arg1, arg2, arg3, arg4) {
        const ret = getObject(arg0).getEntriesByName(getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_getPropertyValue_b51d619f0b96c87f = function() { return handleError(function (arg0, arg1, arg2, arg3) {
        const ret = getObject(arg1).getPropertyValue(getStringFromWasm0(arg2, arg3));
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    }, arguments) };
    imports.wbg.__wbg_getRandomValues_bcb4912f16000dc4 = function() { return handleError(function (arg0, arg1) {
        getObject(arg0).getRandomValues(getObject(arg1));
    }, arguments) };
    imports.wbg.__wbg_getRootNode_440e85dffade7eea = function(arg0) {
        const ret = getObject(arg0).getRootNode();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_getTimezoneOffset_6c191e41297e5a8e = function(arg0) {
        const ret = getObject(arg0).getTimezoneOffset();
        return ret;
    };
    imports.wbg.__wbg_get_0c3cc364764a0b98 = function(arg0, arg1) {
        const ret = getObject(arg0)[arg1 >>> 0];
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_get_0c9db6b3aed90006 = function(arg0, arg1, arg2, arg3) {
        const ret = getObject(arg1)[getStringFromWasm0(arg2, arg3)];
        var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        var len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_get_977cbaa63dc20090 = function(arg0, arg1, arg2) {
        const ret = getObject(arg0)[getStringFromWasm0(arg1, arg2)];
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_get_b996a12be035ef4f = function() { return handleError(function (arg0, arg1) {
        const ret = Reflect.get(getObject(arg0), getObject(arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_getwithindex_bc07b6cede524990 = function(arg0, arg1) {
        const ret = getObject(arg0)[arg1 >>> 0];
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_getwithrefkey_1dc361bd10053bfe = function(arg0, arg1) {
        const ret = getObject(arg0)[getObject(arg1)];
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_globalThis_6b4d52a0b6aaeaea = function() { return handleError(function () {
        const ret = globalThis.globalThis;
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_global_49324ce12193de77 = function() { return handleError(function () {
        const ret = global.global;
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_hasAttribute_ca243798c4c52fb7 = function(arg0, arg1, arg2) {
        const ret = getObject(arg0).hasAttribute(getStringFromWasm0(arg1, arg2));
        return ret;
    };
    imports.wbg.__wbg_has_bdec43a5ed4cb454 = function() { return handleError(function (arg0, arg1) {
        const ret = Reflect.has(getObject(arg0), getObject(arg1));
        return ret;
    }, arguments) };
    imports.wbg.__wbg_height_3adc8837b185fd29 = function(arg0) {
        const ret = getObject(arg0).height;
        return ret;
    };
    imports.wbg.__wbg_height_62d7d52d37fd0599 = function(arg0) {
        const ret = getObject(arg0).height;
        return ret;
    };
    imports.wbg.__wbg_host_407669ea45f72362 = function(arg0) {
        const ret = getObject(arg0).host;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_info_493696cc38ae1ad0 = function(arg0, arg1, arg2, arg3) {
        console.info(getObject(arg0), getObject(arg1), getObject(arg2), getObject(arg3));
    };
    imports.wbg.__wbg_info_6c1abe3d4e1ae962 = function(arg0) {
        console.info(getObject(arg0));
    };
    imports.wbg.__wbg_innerHeight_fb3ea713a47ae687 = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).innerHeight;
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_innerWidth_8d8ddfaffc5a3230 = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).innerWidth;
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_insertBefore_332a5bd77aff0101 = function() { return handleError(function (arg0, arg1, arg2) {
        const ret = getObject(arg0).insertBefore(getObject(arg1), getObject(arg2));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_instanceof_ArrayBuffer_ff40e55b5978e215 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof ArrayBuffer;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Array_23bc22ecdd4608e6 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Array;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_CssStyleRule_834b6a5dc7cf5b86 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof CSSStyleRule;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Element_45bdeb22e5f6babd = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Element;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_FontFace_d2c93c7cd45276b1 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof FontFace;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Map_0f3f3653f757ced1 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Map;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Object_9108547bac1f91b1 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Object;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_PerspectiveViewNotFoundError_60dcfde6b88be790 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof PerspectiveViewNotFoundError;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Promise_55724f650224c9ed = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Promise;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_ShadowRoot_832cd6adaa07105a = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof ShadowRoot;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Uint8Array_db97368f94b1373f = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Uint8Array;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Window_311934805c10047c = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Window;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_isArray_8738f1062fa88586 = function(arg0) {
        const ret = Array.isArray(getObject(arg0));
        return ret;
    };
    imports.wbg.__wbg_isConnected_7b81a95a86664699 = function(arg0) {
        const ret = getObject(arg0).isConnected;
        return ret;
    };
    imports.wbg.__wbg_isIntersecting_80c3e3214ca38ec2 = function(arg0) {
        const ret = getObject(arg0).isIntersecting;
        return ret;
    };
    imports.wbg.__wbg_isSafeInteger_a1b3e0811faecf2f = function(arg0) {
        const ret = Number.isSafeInteger(getObject(arg0));
        return ret;
    };
    imports.wbg.__wbg_is_d6c5f207fac5a36c = function(arg0, arg1) {
        const ret = Object.is(getObject(arg0), getObject(arg1));
        return ret;
    };
    imports.wbg.__wbg_item_5ead4800ef53b575 = function(arg0, arg1) {
        const ret = getObject(arg0).item(arg1 >>> 0);
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_item_85ec4ec73ec46f50 = function(arg0, arg1) {
        const ret = getObject(arg0).item(arg1 >>> 0);
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_item_b8ff6623bcb82860 = function(arg0, arg1) {
        const ret = getObject(arg0).item(arg1 >>> 0);
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_item_f0a3d07d29e8ca08 = function(arg0, arg1, arg2) {
        const ret = getObject(arg1).item(arg2 >>> 0);
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_iterator_c0c688f37fa815e6 = function() {
        const ret = Symbol.iterator;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_keyCode_10de39848ccf36f5 = function(arg0) {
        const ret = getObject(arg0).keyCode;
        return ret;
    };
    imports.wbg.__wbg_key_b6f8a6b04de6624f = function(arg0, arg1) {
        const ret = getObject(arg1).key;
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_keys_45b15edb4089351e = function(arg0) {
        const ret = Object.keys(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_languages_491c6d0833be0219 = function(arg0) {
        const ret = getObject(arg0).languages;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_lastChild_560693bae51c9627 = function(arg0) {
        const ret = getObject(arg0).lastChild;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_left_bbc85c05eb704107 = function(arg0) {
        const ret = getObject(arg0).left;
        return ret;
    };
    imports.wbg.__wbg_length_0f5a275f7c2091d8 = function(arg0) {
        const ret = getObject(arg0).length;
        return ret;
    };
    imports.wbg.__wbg_length_12246a78d2f65d3a = function(arg0) {
        const ret = getObject(arg0).length;
        return ret;
    };
    imports.wbg.__wbg_length_c24da17096edfe57 = function(arg0) {
        const ret = getObject(arg0).length;
        return ret;
    };
    imports.wbg.__wbg_length_cd70c82cb6e23144 = function(arg0) {
        const ret = getObject(arg0).length;
        return ret;
    };
    imports.wbg.__wbg_length_ea896428bb1146cc = function(arg0) {
        const ret = getObject(arg0).length;
        return ret;
    };
    imports.wbg.__wbg_listenerid_ed1678830a5b97ec = function(arg0) {
        const ret = getObject(arg0).__yew_listener_id;
        return isLikeNone(ret) ? 0x100000001 : (ret) >>> 0;
    };
    imports.wbg.__wbg_loaded_9979a254f4c4a18a = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).loaded;
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_mark_2e459508e2ea726f = function() { return handleError(function (arg0, arg1, arg2) {
        getObject(arg0).mark(getStringFromWasm0(arg1, arg2));
    }, arguments) };
    imports.wbg.__wbg_matches_bc60960a81f65a74 = function() { return handleError(function (arg0, arg1, arg2) {
        const ret = getObject(arg0).matches(getStringFromWasm0(arg1, arg2));
        return ret;
    }, arguments) };
    imports.wbg.__wbg_maxcells_06431bff2fc0ce73 = function(arg0) {
        const ret = getObject(arg0).max_cells;
        return isLikeNone(ret) ? 0x100000001 : (ret) >>> 0;
    };
    imports.wbg.__wbg_maxcolumns_8559785340e9f34e = function(arg0) {
        const ret = getObject(arg0).max_columns;
        return isLikeNone(ret) ? 0x100000001 : (ret) >>> 0;
    };
    imports.wbg.__wbg_measure_590e79f6f28bcf70 = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        getObject(arg0).measure(getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
    }, arguments) };
    imports.wbg.__wbg_minconfigcolumns_58b37d4742785fd6 = function(arg0) {
        const ret = getObject(arg0).min_config_columns;
        return isLikeNone(ret) ? 0x100000001 : (ret) >>> 0;
    };
    imports.wbg.__wbg_msCrypto_0a36e2ec3a343d26 = function(arg0) {
        const ret = getObject(arg0).msCrypto;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_name_85f347585a55480b = function(arg0, arg1) {
        const ret = getObject(arg1).name;
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_namespaceURI_a9c6c7804266ee35 = function(arg0, arg1) {
        const ret = getObject(arg1).namespaceURI;
        var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        var len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_navigator_f1fcfe352aad9c4a = function(arg0) {
        const ret = getObject(arg0).navigator;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_26adb8246e7da825 = function() { return handleError(function (arg0, arg1) {
        const ret = new CustomEvent(getStringFromWasm0(arg0, arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_new_4724eedfa9354ef5 = function() {
        const ret = new PerspectiveViewNotFoundError();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_48356ba0d6432058 = function(arg0) {
        const ret = new IntersectionObserver(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_4df4d23a555db943 = function(arg0, arg1) {
        const ret = new Intl.NumberFormat(getObject(arg0), getObject(arg1));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_51701ca96a28bcfb = function(arg0) {
        const ret = new ClipboardItem(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_518e2184725aa711 = function() {
        const ret = new Map();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_59845962d1127937 = function(arg0) {
        const ret = new Uint8Array(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_64f7ad5aa7fe5e65 = function() { return handleError(function (arg0, arg1) {
        const ret = new InputEvent(getStringFromWasm0(arg0, arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_new_67abf4a77618ee3e = function() {
        const ret = new Object();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_7f6cdb425945ba92 = function(arg0, arg1) {
        const ret = new Intl.DateTimeFormat(getObject(arg0), getObject(arg1));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_8a6f238a6ece86ea = function() {
        const ret = new Error();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_9cd5e8b25854d0fd = function(arg0) {
        const ret = new ResizeObserver(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_a96f21efc59c18b1 = function(arg0) {
        const ret = new Date(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_ac7361beaf933ba6 = function(arg0, arg1) {
        try {
            var state0 = {a: arg0, b: arg1};
            var cb0 = (arg0, arg1) => {
                const a = state0.a;
                state0.a = 0;
                try {
                    return __wbg_adapter_734(a, state0.b, arg0, arg1);
                } finally {
                    state0.a = a;
                }
            };
            const ret = new Promise(cb0);
            return addHeapObject(ret);
        } finally {
            state0.a = state0.b = 0;
        }
    };
    imports.wbg.__wbg_new_e2d07398d7689006 = function() {
        const ret = new Array();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_newnoargs_a136448eeb7d48ac = function(arg0, arg1) {
        const ret = new Function(getStringFromWasm0(arg0, arg1));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_newwithbyteoffsetandlength_84908302a4c137cf = function(arg0, arg1, arg2) {
        const ret = new Uint8Array(getObject(arg0), arg1 >>> 0, arg2 >>> 0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_newwitheventinitdict_694b539bc4f40c3d = function() { return handleError(function (arg0, arg1, arg2) {
        const ret = new CustomEvent(getStringFromWasm0(arg0, arg1), getObject(arg2));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_newwithlength_4c216eaaf23f2f9a = function(arg0) {
        const ret = new Uint8Array(arg0 >>> 0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_newwithstrsequenceandoptions_7f10a04698e1ea40 = function() { return handleError(function (arg0, arg1) {
        const ret = new Blob(getObject(arg0), getObject(arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_newwithu8arraysequence_bd1e90bbc7b7a251 = function() { return handleError(function (arg0) {
        const ret = new Blob(getObject(arg0));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_nextSibling_e8b3016fe0fc3483 = function(arg0) {
        const ret = getObject(arg0).nextSibling;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_next_54bce2e56cc36c18 = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).next();
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_next_928df8c15fc0c9b0 = function(arg0) {
        const ret = getObject(arg0).next;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_next_9dc0926f351c7090 = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).next();
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_node_02999533c4ea02e3 = function(arg0) {
        const ret = getObject(arg0).node;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_now_c893509b6d04fa0d = function(arg0) {
        const ret = getObject(arg0).now();
        return ret;
    };
    imports.wbg.__wbg_observe_590b32b952c3fc25 = function(arg0, arg1) {
        getObject(arg0).observe(getObject(arg1));
    };
    imports.wbg.__wbg_observe_d6cd5cbdf51c88bc = function(arg0, arg1) {
        getObject(arg0).observe(getObject(arg1));
    };
    imports.wbg.__wbg_offsetHeight_6f7ddbf328e832e5 = function(arg0) {
        const ret = getObject(arg0).offsetHeight;
        return ret;
    };
    imports.wbg.__wbg_offsetParent_c61271df2ccb206b = function(arg0) {
        const ret = getObject(arg0).offsetParent;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_offsetWidth_e088bf6f4329d827 = function(arg0) {
        const ret = getObject(arg0).offsetWidth;
        return ret;
    };
    imports.wbg.__wbg_offsetX_735d4365b41503ea = function(arg0) {
        const ret = getObject(arg0).offsetX;
        return ret;
    };
    imports.wbg.__wbg_offsetY_b425bca937dc0468 = function(arg0) {
        const ret = getObject(arg0).offsetY;
        return ret;
    };
    imports.wbg.__wbg_parentElement_d1f33e17ed9af17f = function(arg0) {
        const ret = getObject(arg0).parentElement;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_parentNode_632569c5424d986d = function(arg0) {
        const ret = getObject(arg0).parentNode;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_parse_bd09af51fd7dd576 = function() { return handleError(function (arg0, arg1) {
        const ret = JSON.parse(getStringFromWasm0(arg0, arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_performance_69882c3bda965f91 = function(arg0) {
        const ret = getObject(arg0).performance;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_pointerId_d196f4d67d3e19aa = function(arg0) {
        const ret = getObject(arg0).pointerId;
        return ret;
    };
    imports.wbg.__wbg_preventDefault_ce5728083bec4f8d = function(arg0) {
        getObject(arg0).preventDefault();
    };
    imports.wbg.__wbg_priority_29dea5c2eb049377 = function(arg0) {
        const ret = getObject(arg0).priority;
        return isLikeNone(ret) ? 0x100000001 : (ret) >> 0;
    };
    imports.wbg.__wbg_process_5c1d670bc53614b8 = function(arg0) {
        const ret = getObject(arg0).process;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_push_e7d7247e69dad3ee = function(arg0, arg1) {
        const ret = getObject(arg0).push(getObject(arg1));
        return ret;
    };
    imports.wbg.__wbg_queueMicrotask_6808622725a52272 = function(arg0) {
        const ret = getObject(arg0).queueMicrotask;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_queueMicrotask_ef0e86b0263a71ee = function(arg0) {
        queueMicrotask(getObject(arg0));
    };
    imports.wbg.__wbg_randomFillSync_ab2cfe79ebbf2740 = function() { return handleError(function (arg0, arg1) {
        getObject(arg0).randomFillSync(takeObject(arg1));
    }, arguments) };
    imports.wbg.__wbg_readText_cf819cfa16a76536 = function(arg0) {
        const ret = getObject(arg0).readText();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_readyState_905c1c6b522c366a = function(arg0, arg1) {
        const ret = getObject(arg1).readyState;
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_reject_fd3a67e45841ae99 = function(arg0) {
        const ret = Promise.reject(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_relatedTarget_959a1a6780f8c225 = function(arg0) {
        const ret = getObject(arg0).relatedTarget;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_releasePointerCapture_d85ea7bd3c2e3d60 = function() { return handleError(function (arg0, arg1) {
        getObject(arg0).releasePointerCapture(arg1);
    }, arguments) };
    imports.wbg.__wbg_removeAttribute_b92a081e598114ec = function() { return handleError(function (arg0, arg1, arg2) {
        getObject(arg0).removeAttribute(getStringFromWasm0(arg1, arg2));
    }, arguments) };
    imports.wbg.__wbg_removeChild_1a90fe3c463c9fa4 = function() { return handleError(function (arg0, arg1) {
        const ret = getObject(arg0).removeChild(getObject(arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_removeEventListener_a689e1d3f78c8d6c = function() { return handleError(function (arg0, arg1, arg2, arg3) {
        getObject(arg0).removeEventListener(getStringFromWasm0(arg1, arg2), getObject(arg3));
    }, arguments) };
    imports.wbg.__wbg_remove_e7b8fe94708f369e = function() { return handleError(function (arg0, arg1, arg2) {
        getObject(arg0).remove(getStringFromWasm0(arg1, arg2));
    }, arguments) };
    imports.wbg.__wbg_remove_fa057e80ce79f92a = function() { return handleError(function (arg0, arg1) {
        getObject(arg0).remove(...getObject(arg1));
    }, arguments) };
    imports.wbg.__wbg_renderwarning_e1311e93a3f5b5ba = function(arg0) {
        const ret = getObject(arg0).render_warning;
        return isLikeNone(ret) ? 0xFFFFFF : ret ? 1 : 0;
    };
    imports.wbg.__wbg_requestAnimationFrame_10b343047ff65a80 = function() { return handleError(function (arg0, arg1) {
        const ret = getObject(arg0).requestAnimationFrame(getObject(arg1));
        return ret;
    }, arguments) };
    imports.wbg.__wbg_require_79b1e9274cde3c87 = function() { return handleError(function () {
        const ret = module.require;
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_resize_6a556c8c25659a4b = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).resize();
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_resolve_267ff08e7e1d2ce4 = function(arg0) {
        const ret = Promise.resolve(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_resolvedOptions_73d48ef2e9b809e1 = function(arg0) {
        const ret = getObject(arg0).resolvedOptions();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_restore_659bbb0305053a8f = function() { return handleError(function (arg0, arg1, arg2) {
        getObject(arg0).restore(getObject(arg1), getObject(arg2));
    }, arguments) };
    imports.wbg.__wbg_restyle_12ea88fa62356525 = function() { return handleError(function (arg0, arg1) {
        const ret = getObject(arg0).restyle(View.__wrap(arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_save_3c5e3b59ea953b36 = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).save();
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_scrollLeft_934a89309c2e35fd = function(arg0) {
        const ret = getObject(arg0).scrollLeft;
        return ret;
    };
    imports.wbg.__wbg_scrollTop_124f7d558dd2b1d6 = function(arg0) {
        const ret = getObject(arg0).scrollTop;
        return ret;
    };
    imports.wbg.__wbg_scrollTop_baf3b0588ba6af47 = function(arg0) {
        const ret = getObject(arg0).scrollTop;
        return ret;
    };
    imports.wbg.__wbg_selectedIndex_3bf09c0e613c15b4 = function(arg0) {
        const ret = getObject(arg0).selectedIndex;
        return ret;
    };
    imports.wbg.__wbg_selectionEnd_993c6c28b2c8e8b3 = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).selectionEnd;
        return isLikeNone(ret) ? 0x100000001 : (ret) >>> 0;
    }, arguments) };
    imports.wbg.__wbg_selectionStart_dda3ffa187132b73 = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).selectionStart;
        return isLikeNone(ret) ? 0x100000001 : (ret) >>> 0;
    }, arguments) };
    imports.wbg.__wbg_selectmode_dfd8ac137ecb8997 = function(arg0) {
        const ret = getObject(arg0).select_mode;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_selectorText_733f92b3cf56a498 = function(arg0, arg1) {
        const ret = getObject(arg1).selectorText;
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_self_cca3ca60d61220f4 = function() { return handleError(function () {
        const ret = self.self;
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_setAttribute_36e2856decdf83a1 = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        getObject(arg0).setAttribute(getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
    }, arguments) };
    imports.wbg.__wbg_setData_3ae346344c1965c4 = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        getObject(arg0).setData(getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
    }, arguments) };
    imports.wbg.__wbg_setDragImage_40c5bf975f17f344 = function(arg0, arg1, arg2, arg3) {
        getObject(arg0).setDragImage(getObject(arg1), arg2, arg3);
    };
    imports.wbg.__wbg_setPointerCapture_57a3ac98f83ead92 = function() { return handleError(function (arg0, arg1) {
        getObject(arg0).setPointerCapture(arg1);
    }, arguments) };
    imports.wbg.__wbg_setProperty_ee6f9ed1d8596887 = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        getObject(arg0).setProperty(getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
    }, arguments) };
    imports.wbg.__wbg_setSelectionRange_5c44940b58375825 = function() { return handleError(function (arg0, arg1, arg2) {
        getObject(arg0).setSelectionRange(arg1 >>> 0, arg2 >>> 0);
    }, arguments) };
    imports.wbg.__wbg_setTimeout_3252f08858c90488 = function() { return handleError(function (arg0, arg1, arg2) {
        const ret = getObject(arg0).setTimeout(getObject(arg1), arg2);
        return ret;
    }, arguments) };
    imports.wbg.__wbg_set_1b50d2de855a9d50 = function() { return handleError(function (arg0, arg1, arg2) {
        const ret = Reflect.set(getObject(arg0), getObject(arg1), getObject(arg2));
        return ret;
    }, arguments) };
    imports.wbg.__wbg_set_34625a88f2c05a3b = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        getObject(arg0)[getStringFromWasm0(arg1, arg2)] = getStringFromWasm0(arg3, arg4);
    }, arguments) };
    imports.wbg.__wbg_set_393f510a6b7e9da5 = function(arg0, arg1, arg2) {
        const ret = getObject(arg0).set(getObject(arg1), getObject(arg2));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_set_3f1d0b984ed272ed = function(arg0, arg1, arg2) {
        getObject(arg0)[takeObject(arg1)] = takeObject(arg2);
    };
    imports.wbg.__wbg_set_5deee49b10b2b780 = function(arg0, arg1, arg2) {
        getObject(arg0).set(getObject(arg1), arg2 >>> 0);
    };
    imports.wbg.__wbg_set_93ba9407b5476ec6 = function(arg0, arg1, arg2) {
        getObject(arg0)[arg1 >>> 0] = takeObject(arg2);
    };
    imports.wbg.__wbg_setcachekey_bb5f908a0e3ee714 = function(arg0, arg1) {
        getObject(arg0).__yew_subtree_cache_key = arg1 >>> 0;
    };
    imports.wbg.__wbg_setchecked_ee957125854726c5 = function(arg0, arg1) {
        getObject(arg0).checked = arg1 !== 0;
    };
    imports.wbg.__wbg_setdropEffect_49981812b43d66c7 = function(arg0, arg1, arg2) {
        getObject(arg0).dropEffect = getStringFromWasm0(arg1, arg2);
    };
    imports.wbg.__wbg_setinnerHTML_1f5ad3b02760ea31 = function(arg0, arg1, arg2) {
        getObject(arg0).innerHTML = getStringFromWasm0(arg1, arg2);
    };
    imports.wbg.__wbg_setlistenerid_3d14d37a42484593 = function(arg0, arg1) {
        getObject(arg0).__yew_listener_id = arg1 >>> 0;
    };
    imports.wbg.__wbg_setnodeValue_9abe578fc2812b11 = function(arg0, arg1, arg2) {
        getObject(arg0).nodeValue = arg1 === 0 ? undefined : getStringFromWasm0(arg1, arg2);
    };
    imports.wbg.__wbg_setrenderwarning_c29c90e07cc73c80 = function(arg0, arg1) {
        getObject(arg0).render_warning = arg1 !== 0;
    };
    imports.wbg.__wbg_setscrollLeft_93a4a75faf94192b = function(arg0, arg1) {
        getObject(arg0).scrollLeft = arg1;
    };
    imports.wbg.__wbg_setscrollTop_54568fa2c9b61ee9 = function(arg0, arg1) {
        getObject(arg0).scrollTop = arg1;
    };
    imports.wbg.__wbg_setselectionEnd_4df31af04121bb04 = function() { return handleError(function (arg0, arg1) {
        getObject(arg0).selectionEnd = arg1 === 0x100000001 ? undefined : arg1;
    }, arguments) };
    imports.wbg.__wbg_setselectionStart_9c20762a6ae83185 = function() { return handleError(function (arg0, arg1) {
        getObject(arg0).selectionStart = arg1 === 0x100000001 ? undefined : arg1;
    }, arguments) };
    imports.wbg.__wbg_setsubtreeid_32b8ceff55862e29 = function(arg0, arg1) {
        getObject(arg0).__yew_subtree_id = arg1 >>> 0;
    };
    imports.wbg.__wbg_settextContent_60379b5916721a69 = function(arg0, arg1, arg2) {
        getObject(arg0).textContent = arg1 === 0 ? undefined : getStringFromWasm0(arg1, arg2);
    };
    imports.wbg.__wbg_setvalue_34a21ed1993f58ef = function(arg0, arg1, arg2) {
        getObject(arg0).value = getStringFromWasm0(arg1, arg2);
    };
    imports.wbg.__wbg_setvalue_4e6fc1110a966527 = function(arg0, arg1, arg2) {
        getObject(arg0).value = getStringFromWasm0(arg1, arg2);
    };
    imports.wbg.__wbg_setvalue_fc0b0c122b07f8a1 = function(arg0, arg1, arg2) {
        getObject(arg0).value = getStringFromWasm0(arg1, arg2);
    };
    imports.wbg.__wbg_shiftKey_528456f6a6ebf1a9 = function(arg0) {
        const ret = getObject(arg0).shiftKey;
        return ret;
    };
    imports.wbg.__wbg_shiftKey_b2a22adb435e27b7 = function(arg0) {
        const ret = getObject(arg0).shiftKey;
        return ret;
    };
    imports.wbg.__wbg_slice_1ce88459a1591604 = function(arg0, arg1, arg2) {
        const ret = getObject(arg0).slice(arg1 >>> 0, arg2 >>> 0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_stack_0ed75d68575b0f3c = function(arg0, arg1) {
        const ret = getObject(arg1).stack;
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_startTime_06f7b6aebc293aff = function(arg0) {
        const ret = getObject(arg0).startTime;
        return ret;
    };
    imports.wbg.__wbg_static_accessor_PSP_0e6ea4dea6e159fc = function() {
        const ret = psp;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_stopPropagation_6c4309fb9ac23f6a = function(arg0) {
        getObject(arg0).stopPropagation();
    };
    imports.wbg.__wbg_stringify_7330cbd04ec4c682 = function() { return handleError(function (arg0, arg1, arg2) {
        const ret = JSON.stringify(getObject(arg0), getObject(arg1), getObject(arg2));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_stringify_841980d1bf485619 = function() { return handleError(function (arg0) {
        const ret = JSON.stringify(getObject(arg0));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_styleSheets_4e820fe7b798a1dd = function(arg0) {
        const ret = getObject(arg0).styleSheets;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_style_440caa6047a3adbd = function(arg0) {
        const ret = getObject(arg0).style;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_style_920c711d96eb2e5e = function(arg0) {
        const ret = getObject(arg0).style;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_subarray_2dc34705c0dc7cdb = function(arg0, arg1, arg2) {
        const ret = getObject(arg0).subarray(arg1 >>> 0, arg2 >>> 0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_subtreeid_e65dfcc52d403fd9 = function(arg0) {
        const ret = getObject(arg0).__yew_subtree_id;
        return isLikeNone(ret) ? 0x100000001 : (ret) >>> 0;
    };
    imports.wbg.__wbg_supportedValuesOf_2b18e168417d7a84 = function(arg0) {
        const ret = Intl.supportedValuesOf(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_table_new = function(arg0) {
        const ret = Table.__wrap(arg0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_tagName_90c0a7a0bd225b11 = function(arg0, arg1) {
        const ret = getObject(arg1).tagName;
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_target_d36cdebe98450ed6 = function(arg0) {
        const ret = getObject(arg0).target;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_then_84907e7a6730461e = function(arg0, arg1) {
        const ret = getObject(arg0).then(getObject(arg1));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_then_db12746ab6cec3f6 = function(arg0, arg1, arg2) {
        const ret = getObject(arg0).then(getObject(arg1), getObject(arg2));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_toString_2a965b6fc5a7e89f = function(arg0) {
        const ret = getObject(arg0).toString();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_toggleAttribute_3981d7b35ee4dc8c = function() { return handleError(function (arg0, arg1, arg2, arg3) {
        const ret = getObject(arg0).toggleAttribute(getStringFromWasm0(arg1, arg2), arg3 !== 0);
        return ret;
    }, arguments) };
    imports.wbg.__wbg_toggle_aa69dd9b5e2ab306 = function() { return handleError(function (arg0, arg1, arg2) {
        const ret = getObject(arg0).toggle(getStringFromWasm0(arg1, arg2));
        return ret;
    }, arguments) };
    imports.wbg.__wbg_top_5e20a889d04709f4 = function(arg0) {
        const ret = getObject(arg0).top;
        return ret;
    };
    imports.wbg.__wbg_trace_04e683e452168e85 = function(arg0, arg1, arg2, arg3) {
        console.trace(getObject(arg0), getObject(arg1), getObject(arg2), getObject(arg3));
    };
    imports.wbg.__wbg_trace_bf1357f2a705e4dd = function(arg0) {
        console.trace(getObject(arg0));
    };
    imports.wbg.__wbg_unobserve_a169010ee6910d14 = function(arg0, arg1) {
        getObject(arg0).unobserve(getObject(arg1));
    };
    imports.wbg.__wbg_unobserve_f35f55c1e1daba05 = function(arg0, arg1) {
        getObject(arg0).unobserve(getObject(arg1));
    };
    imports.wbg.__wbg_update_54359b6f4e118705 = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        const ret = getObject(arg0).update(View.__wrap(arg1), arg2 === 0x100000001 ? undefined : arg2, arg3 === 0x100000001 ? undefined : arg3, arg4 !== 0);
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_valueAsNumber_69abf6d7799e2865 = function(arg0) {
        const ret = getObject(arg0).valueAsNumber;
        return ret;
    };
    imports.wbg.__wbg_value_0eccaeade4025732 = function(arg0, arg1) {
        const ret = getObject(arg1).value;
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_value_51f8a88d4a1805fb = function(arg0) {
        const ret = getObject(arg0).value;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_value_6da0340a74182dc9 = function(arg0, arg1) {
        const ret = getObject(arg1).value;
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_values_4521bea64273acef = function(arg0) {
        const ret = getObject(arg0).values();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_values_9b070f5059e8183e = function(arg0) {
        const ret = Object.values(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_versions_c71aa1626a93e0a1 = function(arg0) {
        const ret = getObject(arg0).versions;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_view_new = function(arg0) {
        const ret = View.__wrap(arg0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_view_unwrap = function(arg0) {
        const ret = View.__unwrap(takeObject(arg0));
        return ret;
    };
    imports.wbg.__wbg_warn_4f29d3e20ba97cd0 = function(arg0, arg1, arg2, arg3) {
        console.warn(getObject(arg0), getObject(arg1), getObject(arg2), getObject(arg3));
    };
    imports.wbg.__wbg_warn_fecc8e96c5e56fb2 = function(arg0) {
        console.warn(getObject(arg0));
    };
    imports.wbg.__wbg_weight_fa07ad59f7c88d78 = function(arg0, arg1) {
        const ret = getObject(arg1).weight;
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_which_aa39f19447dea33e = function(arg0) {
        const ret = getObject(arg0).which;
        return ret;
    };
    imports.wbg.__wbg_width_672ea0f631559cbd = function(arg0) {
        const ret = getObject(arg0).width;
        return ret;
    };
    imports.wbg.__wbg_width_a542376951d8d711 = function(arg0) {
        const ret = getObject(arg0).width;
        return ret;
    };
    imports.wbg.__wbg_window_2aba046d3fc4ad7c = function() { return handleError(function () {
        const ret = window.window;
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_write_83931bdf7161281c = function(arg0, arg1) {
        const ret = getObject(arg0).write(getObject(arg1));
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_as_number = function(arg0) {
        const ret = +getObject(arg0);
        return ret;
    };
    imports.wbg.__wbindgen_bigint_from_i64 = function(arg0) {
        const ret = arg0;
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_bigint_from_u64 = function(arg0) {
        const ret = BigInt.asUintN(64, arg0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_bigint_get_as_i64 = function(arg0, arg1) {
        const v = getObject(arg1);
        const ret = typeof(v) === 'bigint' ? v : undefined;
        getDataViewMemory0().setBigInt64(arg0 + 8 * 1, isLikeNone(ret) ? BigInt(0) : ret, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, !isLikeNone(ret), true);
    };
    imports.wbg.__wbindgen_boolean_get = function(arg0) {
        const v = getObject(arg0);
        const ret = typeof(v) === 'boolean' ? (v ? 1 : 0) : 2;
        return ret;
    };
    imports.wbg.__wbindgen_cb_drop = function(arg0) {
        const obj = takeObject(arg0).original;
        if (obj.cnt-- == 1) {
            obj.a = 0;
            return true;
        }
        const ret = false;
        return ret;
    };
    imports.wbg.__wbindgen_closure_wrapper13944 = function(arg0, arg1, arg2) {
        const ret = makeClosure(arg0, arg1, 3600, __wbg_adapter_65);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_closure_wrapper17147 = function(arg0, arg1, arg2) {
        const ret = makeClosure(arg0, arg1, 4204, __wbg_adapter_68);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_closure_wrapper18076 = function(arg0, arg1, arg2) {
        const ret = makeMutClosure(arg0, arg1, 4296, __wbg_adapter_71);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_closure_wrapper18100 = function(arg0, arg1, arg2) {
        const ret = makeMutClosure(arg0, arg1, 4300, __wbg_adapter_74);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_closure_wrapper5869 = function(arg0, arg1, arg2) {
        const ret = makeClosure(arg0, arg1, 75, __wbg_adapter_52);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_closure_wrapper5871 = function(arg0, arg1, arg2) {
        const ret = makeMutClosure(arg0, arg1, 75, __wbg_adapter_55);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_closure_wrapper5873 = function(arg0, arg1, arg2) {
        const ret = makeClosure(arg0, arg1, 75, __wbg_adapter_52);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_closure_wrapper5875 = function(arg0, arg1, arg2) {
        const ret = makeMutClosure(arg0, arg1, 78, __wbg_adapter_60);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_closure_wrapper5877 = function(arg0, arg1, arg2) {
        const ret = makeMutClosure(arg0, arg1, 75, __wbg_adapter_55);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_debug_string = function(arg0, arg1) {
        const ret = debugString(getObject(arg1));
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbindgen_error_new = function(arg0, arg1) {
        const ret = new Error(getStringFromWasm0(arg0, arg1));
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_in = function(arg0, arg1) {
        const ret = getObject(arg0) in getObject(arg1);
        return ret;
    };
    imports.wbg.__wbindgen_is_bigint = function(arg0) {
        const ret = typeof(getObject(arg0)) === 'bigint';
        return ret;
    };
    imports.wbg.__wbindgen_is_function = function(arg0) {
        const ret = typeof(getObject(arg0)) === 'function';
        return ret;
    };
    imports.wbg.__wbindgen_is_null = function(arg0) {
        const ret = getObject(arg0) === null;
        return ret;
    };
    imports.wbg.__wbindgen_is_object = function(arg0) {
        const val = getObject(arg0);
        const ret = typeof(val) === 'object' && val !== null;
        return ret;
    };
    imports.wbg.__wbindgen_is_string = function(arg0) {
        const ret = typeof(getObject(arg0)) === 'string';
        return ret;
    };
    imports.wbg.__wbindgen_is_undefined = function(arg0) {
        const ret = getObject(arg0) === undefined;
        return ret;
    };
    imports.wbg.__wbindgen_jsval_eq = function(arg0, arg1) {
        const ret = getObject(arg0) === getObject(arg1);
        return ret;
    };
    imports.wbg.__wbindgen_jsval_loose_eq = function(arg0, arg1) {
        const ret = getObject(arg0) == getObject(arg1);
        return ret;
    };
    imports.wbg.__wbindgen_memory = function() {
        const ret = wasm.memory;
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_number_get = function(arg0, arg1) {
        const obj = getObject(arg1);
        const ret = typeof(obj) === 'number' ? obj : undefined;
        getDataViewMemory0().setFloat64(arg0 + 8 * 1, isLikeNone(ret) ? 0 : ret, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, !isLikeNone(ret), true);
    };
    imports.wbg.__wbindgen_number_new = function(arg0) {
        const ret = arg0;
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_object_clone_ref = function(arg0) {
        const ret = getObject(arg0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_object_drop_ref = function(arg0) {
        takeObject(arg0);
    };
    imports.wbg.__wbindgen_string_get = function(arg0, arg1) {
        const obj = getObject(arg1);
        const ret = typeof(obj) === 'string' ? obj : undefined;
        var ptr1 = isLikeNone(ret) ? 0 : passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        var len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbindgen_string_new = function(arg0, arg1) {
        const ret = getStringFromWasm0(arg0, arg1);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_throw = function(arg0, arg1) {
        throw new Error(getStringFromWasm0(arg0, arg1));
    };

    return imports;
}

function __wbg_init_memory(imports, memory) {

}

function __wbg_finalize_init(instance, module) {
    wasm = instance.exports;
    __wbg_init.__wbindgen_wasm_module = module;
    cachedDataViewMemory0 = null;
    cachedUint8ArrayMemory0 = null;



    return wasm;
}

function initSync(module) {
    if (wasm !== undefined) return wasm;


    if (typeof module !== 'undefined') {
        if (Object.getPrototypeOf(module) === Object.prototype) {
            ({module} = module)
        } else {
            console.warn('using deprecated parameters for `initSync()`; pass a single object instead')
        }
    }

    const imports = __wbg_get_imports();

    __wbg_init_memory(imports);

    if (!(module instanceof WebAssembly.Module)) {
        module = new WebAssembly.Module(module);
    }

    const instance = new WebAssembly.Instance(module, imports);

    return __wbg_finalize_init(instance, module);
}

async function __wbg_init(module_or_path) {
    if (wasm !== undefined) return wasm;


    if (typeof module_or_path !== 'undefined') {
        if (Object.getPrototypeOf(module_or_path) === Object.prototype) {
            ({module_or_path} = module_or_path)
        } else {
            console.warn('using deprecated parameters for the initialization function; pass a single object instead')
        }
    }


    const imports = __wbg_get_imports();

    if (typeof module_or_path === 'string' || (typeof Request === 'function' && module_or_path instanceof Request) || (typeof URL === 'function' && module_or_path instanceof URL)) {
        module_or_path = fetch(module_or_path);
    }

    __wbg_init_memory(imports);

    const { instance, module } = await __wbg_load(await module_or_path, imports);

    return __wbg_finalize_init(instance, module);
}

export { initSync };
export default __wbg_init;
