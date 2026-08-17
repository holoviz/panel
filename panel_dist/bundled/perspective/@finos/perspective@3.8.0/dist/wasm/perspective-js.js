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

let heap_next = heap.length;

function addHeapObject(obj) {
    if (heap_next === heap.length) heap.push(heap.length + 1);
    const idx = heap_next;
    heap_next = heap[idx];

    heap[idx] = obj;
    return idx;
}

function handleError(f, args) {
    try {
        return f.apply(this, args);
    } catch (e) {
        wasm.__wbindgen_export_2(addHeapObject(e));
    }
}

const cachedTextDecoder = (typeof TextDecoder !== 'undefined' ? new TextDecoder('utf-8', { ignoreBOM: true, fatal: true }) : { decode: () => { throw Error('TextDecoder not available') } } );

if (typeof TextDecoder !== 'undefined') { cachedTextDecoder.decode(); };

function getStringFromWasm0(ptr, len) {
    ptr = ptr >>> 0;
    return cachedTextDecoder.decode(getUint8ArrayMemory0().subarray(ptr, ptr + len));
}

function getArrayU8FromWasm0(ptr, len) {
    ptr = ptr >>> 0;
    return getUint8ArrayMemory0().subarray(ptr / 1, ptr / 1 + len);
}

function isLikeNone(x) {
    return x === undefined || x === null;
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

const CLOSURE_DTORS = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(state => {
    wasm.__wbindgen_export_4.get(state.dtor)(state.a, state.b)
});

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

let stack_pointer = 128;

function addBorrowedObject(obj) {
    if (stack_pointer == 1) throw new Error('out of js stack');
    heap[--stack_pointer] = obj;
    return stack_pointer;
}

export function init() {
    wasm.init();
}

function __wbg_adapter_50(arg0, arg1) {
    const ret = wasm.__wbindgen_export_5(arg0, arg1);
    return takeObject(ret);
}

function __wbg_adapter_53(arg0, arg1, arg2) {
    wasm.__wbindgen_export_6(arg0, arg1, addHeapObject(arg2));
}

function __wbg_adapter_251(arg0, arg1, arg2, arg3) {
    wasm.__wbindgen_export_7(arg0, arg1, addHeapObject(arg2), addHeapObject(arg3));
}

const ClientFinalization = (typeof FinalizationRegistry === 'undefined')
    ? { register: () => {}, unregister: () => {} }
    : new FinalizationRegistry(ptr => wasm.__wbg_client_free(ptr >>> 0, 1));
/**
 * An instance of a [`Client`] is a connection to a single
 * `perspective_server::Server`, whether locally in-memory or remote over some
 * transport like a WebSocket.
 *
 * The browser and node.js libraries both support the `websocket(url)`
 * constructor, which connects to a remote `perspective_server::Server`
 * instance over a WebSocket transport.
 *
 * In the browser, the `worker()` constructor creates a new Web Worker
 * `perspective_server::Server` and returns a [`Client`] connected to it.
 *
 * In node.js, a pre-instantied [`Client`] connected synhronously to a global
 * singleton `perspective_server::Server` is the default module export.
 *
 * # JavaScript Examples
 *
 * Create a Web Worker `perspective_server::Server` in the browser and return a
 * [`Client`] instance connected for it:
 *
 * ```javascript
 * import perspective from "@finos/perspective";
 * const client = await perspective.worker();
 * ```
 *
 * Create a WebSocket connection to a remote `perspective_server::Server`:
 *
 * ```javascript
 * import perspective from "@finos/perspective";
 * const client = await perspective.websocket("ws://locahost:8080/ws");
 * ```
 *
 * Access the synchronous client in node.js:
 *
 * ```javascript
 * import { default as client } from "@finos/perspective";
 * ```
 */
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
        try {
            const retptr = wasm.__wbindgen_add_to_stack_pointer(-16);
            wasm.client_new(retptr, addHeapObject(send_request), isLikeNone(close) ? 0 : addHeapObject(close));
            var r0 = getDataViewMemory0().getInt32(retptr + 4 * 0, true);
            var r1 = getDataViewMemory0().getInt32(retptr + 4 * 1, true);
            var r2 = getDataViewMemory0().getInt32(retptr + 4 * 2, true);
            if (r2) {
                throw takeObject(r1);
            }
            this.__wbg_ptr = r0 >>> 0;
            ClientFinalization.register(this, this.__wbg_ptr, this);
            return this;
        } finally {
            wasm.__wbindgen_add_to_stack_pointer(16);
        }
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
     * @param {any} value
     * @returns {Promise<void>}
     */
    handle_response(value) {
        const ret = wasm.client_handle_response(this.__wbg_ptr, addHeapObject(value));
        return takeObject(ret);
    }
    /**
     * @param {string} error
     * @param {Function | null} [reconnect]
     * @returns {Promise<void>}
     */
    handle_error(error, reconnect) {
        const ptr0 = passStringToWasm0(error, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len0 = WASM_VECTOR_LEN;
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
     * Creates a new [`Table`] from either a _schema_ or _data_.
     *
     * The [`Client::table`] factory function can be initialized with either a
     * _schema_ (see [`Table::schema`]), or data in one of these formats:
     *
     * - Apache Arrow
     * - CSV
     * - JSON row-oriented
     * - JSON column-oriented
     * - NDJSON
     *
     * When instantiated with _data_, the schema is inferred from this data.
     * While this is convenient, inferrence is sometimes imperfect e.g.
     * when the input is empty, null or ambiguous. For these cases,
     * [`Client::table`] can first be instantiated with a explicit schema.
     *
     * When instantiated with a _schema_, the resulting [`Table`] is empty but
     * with known column names and column types. When subsqeuently
     * populated with [`Table::update`], these columns will be _coerced_ to
     * the schema's type. This behavior can be useful when
     * [`Client::table`]'s column type inferences doesn't work.
     *
     * The resulting [`Table`] is _virtual_, and invoking its methods
     * dispatches events to the `perspective_server::Server` this
     * [`Client`] connects to, where the data is stored and all calculation
     * occurs.
     *
     * # Arguments
     *
     * - `arg` - Either _schema_ or initialization _data_.
     * - `options` - Optional configuration which provides one of:
     *     - `limit` - The max number of rows the resulting [`Table`] can
     *       store.
     *     - `index` - The column name to use as an _index_ column. If this
     *       `Table` is being instantiated by _data_, this column name must be
     *       present in the data.
     *     - `name` - The name of the table. This will be generated if it is
     *       not provided.
     *     - `format` - The explicit format of the input data, can be one of
     *       `"json"`, `"columns"`, `"csv"` or `"arrow"`. This overrides
     *       language-specific type dispatch behavior, which allows stringified
     *       and byte array alternative inputs.
     *
     * # JavaScript Examples
     *
     * Load a CSV from a `string`:
     *
     * ```javascript
     * const table = await client.table("x,y\n1,2\n3,4");
     * ```
     *
     * Load an Arrow from an `ArrayBuffer`:
     *
     * ```javascript
     * import * as fs from "node:fs/promises";
     * const table2 = await client.table(await fs.readFile("superstore.arrow"));
     * ```
     *
     * Load a CSV from a `UInt8Array` (the default for this type is Arrow)
     * using a format override:
     *
     * ```javascript
     * const enc = new TextEncoder();
     * const table = await client.table(enc.encode("x,y\n1,2\n3,4"), {
     *     format: "csv",
     * });
     * ```
     *
     * Create a table with an `index`:
     *
     * ```javascript
     * const table = await client.table(data, { index: "Row ID" });
     * ```
     * @param {string | ArrayBuffer | Record<string, unknown[]> | Record<string, unknown>[]} value
     * @param {TableInitOptions | null} [options]
     * @returns {Promise<Table>}
     */
    table(value, options) {
        const ret = wasm.client_table(this.__wbg_ptr, addHeapObject(value), isLikeNone(options) ? 0 : addHeapObject(options));
        return takeObject(ret);
    }
    /**
     * Terminates this [`Client`], cleaning up any [`crate::View`] handles the
     * [`Client`] has open as well as its callbacks.
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
     * Opens a [`Table`] that is hosted on the `perspective_server::Server`
     * that is connected to this [`Client`].
     *
     * The `name` property of [`TableInitOptions`] is used to identify each
     * [`Table`]. [`Table`] `name`s can be looked up for each [`Client`]
     * via [`Client::get_hosted_table_names`].
     *
     * # JavaScript Examples
     *
     * Get a virtual [`Table`] named "table_one" from this [`Client`]
     *
     * ```javascript
     * const tables = await client.open_table("table_one");
     * ```
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
     * Retrieves the names of all tables that this client has access to.
     *
     * `name` is a string identifier unique to the [`Table`] (per [`Client`]),
     * which can be used in conjunction with [`Client::open_table`] to get
     * a [`Table`] instance without the use of [`Client::table`]
     * constructor directly (e.g., one created by another [`Client`]).
     *
     * # JavaScript Examples
     *
     * ```javascript
     * const tables = await client.get_hosted_table_names();
     * ```
     * @returns {Promise<any>}
     */
    get_hosted_table_names() {
        const ret = wasm.client_get_hosted_table_names(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Register a callback which is invoked whenever [`Client::table`] (on this
     * [`Client`]) or [`Table::delete`] (on a [`Table`] belinging to this
     * [`Client`]) are called.
     * @param {Function} on_update_js
     * @returns {Promise<number>}
     */
    on_hosted_tables_update(on_update_js) {
        const ret = wasm.client_on_hosted_tables_update(this.__wbg_ptr, addHeapObject(on_update_js));
        return takeObject(ret);
    }
    /**
     * Remove a callback previously registered via
     * `Client::on_hosted_tables_update`.
     * @param {number} update_id
     * @returns {Promise<void>}
     */
    remove_hosted_tables_update(update_id) {
        const ret = wasm.client_remove_hosted_tables_update(this.__wbg_ptr, update_id);
        return takeObject(ret);
    }
    /**
     * Provides the [`SystemInfo`] struct, implementation-specific metadata
     * about the [`perspective_server::Server`] runtime such as Memory and
     * CPU usage.
     *
     * For WebAssembly servers, this method includes the WebAssembly heap size.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * const info = await client.system_info();
     * ```
     * @returns {Promise<SystemInfo>}
     */
    system_info() {
        const ret = wasm.client_system_info(this.__wbg_ptr);
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
     * Returns the name of the index column for the table.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * const table = await client.table("x,y\n1,2\n3,4", { index: "x" });
     * const index = table.get_index(); // "x"
     * ```
     * @returns {Promise<string | undefined>}
     */
    get_index() {
        const ret = wasm.table_get_index(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Get a copy of the [`Client`] this [`Table`] came from.
     * @returns {Promise<Client>}
     */
    get_client() {
        const ret = wasm.table_get_client(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Returns the user-specified name for this table, or the auto-generated
     * name if a name was not specified when the table was created.
     * @returns {Promise<string>}
     */
    get_name() {
        const ret = wasm.table_get_name(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Returns the user-specified row limit for this table.
     * @returns {Promise<number | undefined>}
     */
    get_limit() {
        const ret = wasm.table_get_limit(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Removes all the rows in the [`Table`], but preserves everything else
     * including the schema, index, and any callbacks or registered
     * [`View`] instances.
     *
     * Calling [`Table::clear`], like [`Table::update`] and [`Table::remove`],
     * will trigger an update event to any registered listeners via
     * [`View::on_update`].
     * @returns {Promise<void>}
     */
    clear() {
        const ret = wasm.table_clear(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Delete this [`Table`] and cleans up associated resources.
     *
     * [`Table`]s do not stop consuming resources or processing updates when
     * they are garbage collected in their host language - you must call
     * this method to reclaim these.
     *
     * # Arguments
     *
     * - `options` An options dictionary.
     *     - `lazy` Whether to delete this [`Table`] _lazily_. When false (the
     *       default), the delete will occur immediately, assuming it has no
     *       [`View`] instances registered to it (which must be deleted first,
     *       otherwise this method will throw an error). When true, the
     *       [`Table`] will only be marked for deltion once its [`View`]
     *       dependency count reaches 0.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * const table = await client.table("x,y\n1,2\n3,4");
     *
     * // ...
     *
     * await table.delete({ lazy: true });
     * ```
     * @param {DeleteOptions | null} [options]
     * @returns {Promise<void>}
     */
    delete(options) {
        const ptr = this.__destroy_into_raw();
        const ret = wasm.table_delete(ptr, isLikeNone(options) ? 0 : addHeapObject(options));
        return takeObject(ret);
    }
    /**
     * Returns the number of rows in a [`Table`].
     * @returns {Promise<number>}
     */
    size() {
        const ret = wasm.table_size(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Returns a table's [`Schema`], a mapping of column names to column types.
     *
     * The mapping of a [`Table`]'s column names to data types is referred to
     * as a [`Schema`]. Each column has a unique name and a data type, one
     * of:
     *
     * - `"boolean"` - A boolean type
     * - `"date"` - A timesonze-agnostic date type (month/day/year)
     * - `"datetime"` - A millisecond-precision datetime type in the UTC
     *   timezone
     * - `"float"` - A 64 bit float
     * - `"integer"` - A signed 32 bit integer (the integer type supported by
     *   JavaScript)
     * - `"string"` - A [`String`] data type (encoded internally as a
     *   _dictionary_)
     *
     * Note that all [`Table`] columns are _nullable_, regardless of the data
     * type.
     * @returns {Promise<any>}
     */
    schema() {
        const ret = wasm.table_schema(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Returns the column names of this [`Table`] in "natural" order (the
     * ordering implied by the input format).
     *
     *  # JavaScript Examples
     *
     *  ```javascript
     *  const columns = await table.columns();
     *  ```
     * @returns {Promise<any>}
     */
    columns() {
        const ret = wasm.table_columns(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Create a unique channel ID on this [`Table`], which allows
     * `View::on_update` callback calls to be associated with the
     * `Table::update` which caused them.
     * @returns {Promise<number>}
     */
    make_port() {
        const ret = wasm.table_make_port(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Register a callback which is called exactly once, when this [`Table`] is
     * deleted with the [`Table::delete`] method.
     *
     * [`Table::on_delete`] resolves when the subscription message is sent, not
     * when the _delete_ event occurs.
     * @param {Function} on_delete
     * @returns {Promise<any>}
     */
    on_delete(on_delete) {
        const ret = wasm.table_on_delete(this.__wbg_ptr, addHeapObject(on_delete));
        return takeObject(ret);
    }
    /**
     * Removes a listener with a given ID, as returned by a previous call to
     * [`Table::on_delete`].
     * @param {number} callback_id
     * @returns {Promise<any>}
     */
    remove_delete(callback_id) {
        const ret = wasm.table_remove_delete(this.__wbg_ptr, callback_id);
        return takeObject(ret);
    }
    /**
     * Removes rows from this [`Table`] with the `index` column values
     * supplied.
     *
     * # Arguments
     *
     * - `indices` - A list of `index` column values for rows that should be
     *   removed.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * await table.remove([1, 2, 3]);
     * ```
     * @param {any} value
     * @param {UpdateOptions | null} [options]
     * @returns {Promise<void>}
     */
    remove(value, options) {
        const ret = wasm.table_remove(this.__wbg_ptr, addHeapObject(value), isLikeNone(options) ? 0 : addHeapObject(options));
        return takeObject(ret);
    }
    /**
     * Replace all rows in this [`Table`] with the input data, coerced to this
     * [`Table`]'s existing [`perspective_client::Schema`], notifying any
     * derived [`View`] and [`View::on_update`] callbacks.
     *
     * Calling [`Table::replace`] is an easy way to replace _all_ the data in a
     * [`Table`] without losing any derived [`View`] instances or
     * [`View::on_update`] callbacks. [`Table::replace`] does _not_ infer
     * data types like [`Client::table`] does, rather it _coerces_ input
     * data to the `Schema` like [`Table::update`]. If you need a [`Table`]
     * with a different `Schema`, you must create a new one.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * await table.replace("x,y\n1,2");
     * ```
     * @param {any} input
     * @param {UpdateOptions | null} [options]
     * @returns {Promise<void>}
     */
    replace(input, options) {
        const ret = wasm.table_replace(this.__wbg_ptr, addHeapObject(input), isLikeNone(options) ? 0 : addHeapObject(options));
        return takeObject(ret);
    }
    /**
     * Updates the rows of this table and any derived [`View`] instances.
     *
     * Calling [`Table::update`] will trigger the [`View::on_update`] callbacks
     * register to derived [`View`], and the call itself will not resolve until
     * _all_ derived [`View`]'s are notified.
     *
     * When updating a [`Table`] with an `index`, [`Table::update`] supports
     * partial updates, by omitting columns from the update data.
     *
     * # Arguments
     *
     * - `input` - The input data for this [`Table`]. The schema of a [`Table`]
     *   is immutable after creation, so this method cannot be called with a
     *   schema.
     * - `options` - Options for this update step - see [`UpdateOptions`].
     *
     * # JavaScript Examples
     *
     * ```javascript
     * await table.update("x,y\n1,2");
     * ```
     * @param {string | ArrayBuffer | Record<string, unknown[]> | Record<string, unknown>[]} input
     * @param {UpdateOptions | null} [options]
     * @returns {Promise<any>}
     */
    update(input, options) {
        const ret = wasm.table_update(this.__wbg_ptr, addHeapObject(input), isLikeNone(options) ? 0 : addHeapObject(options));
        return takeObject(ret);
    }
    /**
     * Create a new [`View`] from this table with a specified
     * [`ViewConfigUpdate`].
     *
     * See [`View`] struct.
     *
     * # JavaScript Examples
     *
     * ```javascript
     * const view = await table.view({
     *     columns: ["Sales"],
     *     aggregates: { Sales: "sum" },
     *     group_by: ["Region", "Country"],
     *     filter: [["Category", "in", ["Furniture", "Technology"]]],
     * });
     * ```
     * @param {ViewConfigUpdate | null} [config]
     * @returns {Promise<View>}
     */
    view(config) {
        const ret = wasm.table_view(this.__wbg_ptr, isLikeNone(config) ? 0 : addHeapObject(config));
        return takeObject(ret);
    }
    /**
     * Validates the given expressions.
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
/**
 * The [`View`] struct is Perspective's query and serialization interface. It
 * represents a query on the `Table`'s dataset and is always created from an
 * existing `Table` instance via the [`Table::view`] method.
 *
 * [`View`]s are immutable with respect to the arguments provided to the
 * [`Table::view`] method; to change these parameters, you must create a new
 * [`View`] on the same [`Table`]. However, each [`View`] is _live_ with
 * respect to the [`Table`]'s data, and will (within a conflation window)
 * update with the latest state as its parent [`Table`] updates, including
 * incrementally recalculating all aggregates, pivots, filters, etc. [`View`]
 * query parameters are composable, in that each parameter works independently
 * _and_ in conjunction with each other, and there is no limit to the number of
 * pivots, filters, etc. which can be applied.
 */
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
     * Returns an array of strings containing the column paths of the [`View`]
     * without any of the source columns.
     *
     * A column path shows the columns that a given cell belongs to after
     * pivots are applied.
     * @param {ColumnWindow | null} [window]
     * @returns {Promise<any>}
     */
    column_paths(window) {
        const ret = wasm.view_column_paths(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * Delete this [`View`] and clean up all resources associated with it.
     * [`View`] objects do not stop consuming resources or processing
     * updates when they are garbage collected - you must call this method
     * to reclaim these.
     * @returns {Promise<void>}
     */
    delete() {
        const ptr = this.__destroy_into_raw();
        const ret = wasm.view_delete(ptr);
        return takeObject(ret);
    }
    /**
     * Returns this [`View`]'s _dimensions_, row and column count, as well as
     * those of the [`crate::Table`] from which it was derived.
     *
     * - `num_table_rows` - The number of rows in the underlying
     *   [`crate::Table`].
     * - `num_table_columns` - The number of columns in the underlying
     *   [`crate::Table`] (including the `index` column if this
     *   [`crate::Table`] was constructed with one).
     * - `num_view_rows` - The number of rows in this [`View`]. If this
     *   [`View`] has a `group_by` clause, `num_view_rows` will also include
     *   aggregated rows.
     * - `num_view_columns` - The number of columns in this [`View`]. If this
     *   [`View`] has a `split_by` clause, `num_view_columns` will include all
     *   _column paths_, e.g. the number of `columns` clause times the number
     *   of `split_by` groups.
     * @returns {Promise<any>}
     */
    dimensions() {
        const ret = wasm.view_dimensions(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * The expression schema of this [`View`], which contains only the
     * expressions created on this [`View`]. See [`View::schema`] for
     * details.
     * @returns {Promise<any>}
     */
    expression_schema() {
        const ret = wasm.view_expression_schema(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * A copy of the config object passed to the [`Table::view`] method which
     * created this [`View`].
     * @returns {Promise<any>}
     */
    get_config() {
        const ret = wasm.view_get_config(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Calculates the [min, max] of the leaf nodes of a column `column_name`.
     *
     * # Returns
     *
     * A tuple of [min, max], whose types are column and aggregate dependent.
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
     * The number of aggregated rows in this [`View`]. This is affected by the
     * "group_by" configuration parameter supplied to this view's contructor.
     *
     * # Returns
     *
     * The number of aggregated rows.
     * @returns {Promise<number>}
     */
    num_rows() {
        const ret = wasm.view_num_rows(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * The schema of this [`View`].
     *
     * The [`View`] schema differs from the `schema` returned by
     * [`Table::schema`]; it may have different column names due to
     * `expressions` or `columns` configs, or it maye have _different
     * column types_ due to the application og `group_by` and `aggregates`
     * config. You can think of [`Table::schema`] as the _input_ schema and
     * [`View::schema`] as the _output_ schema of a Perspective pipeline.
     * @returns {Promise<any>}
     */
    schema() {
        const ret = wasm.view_schema(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Serializes a [`View`] to the Apache Arrow data format.
     * @param {ViewWindow | null} [window]
     * @returns {Promise<ArrayBuffer>}
     */
    to_arrow(window) {
        const ret = wasm.view_to_arrow(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * Serializes this [`View`] to a string of JSON data. Useful if you want to
     * save additional round trip serialize/deserialize cycles.
     * @param {ViewWindow | null} [window]
     * @returns {Promise<string>}
     */
    to_columns_string(window) {
        const ret = wasm.view_to_columns_string(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * Serializes this [`View`] to JavaScript objects in a column-oriented
     * format.
     * @param {ViewWindow | null} [window]
     * @returns {Promise<object>}
     */
    to_columns(window) {
        const ret = wasm.view_to_columns(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * Render this `View` as a JSON string.
     * @param {ViewWindow | null} [window]
     * @returns {Promise<string>}
     */
    to_json_string(window) {
        const ret = wasm.view_to_json_string(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * Serializes this [`View`] to JavaScript objects in a row-oriented
     * format.
     * @param {ViewWindow | null} [window]
     * @returns {Promise<Array<any>>}
     */
    to_json(window) {
        const ret = wasm.view_to_json(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * Renders this [`View`] as an [NDJSON](https://github.com/ndjson/ndjson-spec)
     * formatted [`String`].
     * @param {ViewWindow | null} [window]
     * @returns {Promise<string>}
     */
    to_ndjson(window) {
        const ret = wasm.view_to_ndjson(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * Serializes this [`View`] to CSV data in a standard format.
     * @param {ViewWindow | null} [window]
     * @returns {Promise<string>}
     */
    to_csv(window) {
        const ret = wasm.view_to_csv(this.__wbg_ptr, isLikeNone(window) ? 0 : addHeapObject(window));
        return takeObject(ret);
    }
    /**
     * Register a callback with this [`View`]. Whenever the view's underlying
     * table emits an update, this callback will be invoked with an object
     * containing `port_id`, indicating which port the update fired on, and
     * optionally `delta`, which is the new data that was updated for each
     * cell or each row.
     *
     * # Arguments
     *
     * - `on_update` - A callback function invoked on update, which receives an
     *   object with two keys: `port_id`, indicating which port the update was
     *   triggered on, and `delta`, whose value is dependent on the mode
     *   parameter.
     * - `options` - If this is provided as `OnUpdateOptions { mode:
     *   Some(OnUpdateMode::Row) }`, then `delta` is an Arrow of the updated
     *   rows. Otherwise `delta` will be [`Option::None`].
     *
     * # JavaScript Examples
     *
     * ```javascript
     * // Attach an `on_update` callback
     * view.on_update((updated) => console.log(updated.port_id));
     * ```
     *
     * ```javascript
     * // `on_update` with row deltas
     * view.on_update((updated) => console.log(updated.delta), { mode: "row" });
     * ```
     * @param {Function} on_update_js
     * @param {OnUpdateOptions | null} [options]
     * @returns {Promise<any>}
     */
    on_update(on_update_js, options) {
        const ret = wasm.view_on_update(this.__wbg_ptr, addHeapObject(on_update_js), isLikeNone(options) ? 0 : addHeapObject(options));
        return takeObject(ret);
    }
    /**
     * Unregister a previously registered update callback with this [`View`].
     *
     * # Arguments
     *
     * - `id` - A callback `id` as returned by a recipricol call to
     *   [`View::on_update`].
     * @param {number} callback_id
     * @returns {Promise<void>}
     */
    remove_update(callback_id) {
        const ret = wasm.view_remove_update(this.__wbg_ptr, callback_id);
        return takeObject(ret);
    }
    /**
     * Register a callback with this [`View`]. Whenever the [`View`] is
     * deleted, this callback will be invoked.
     * @param {Function} on_delete
     * @returns {Promise<any>}
     */
    on_delete(on_delete) {
        const ret = wasm.view_on_delete(this.__wbg_ptr, addHeapObject(on_delete));
        return takeObject(ret);
    }
    /**
     * The number of aggregated columns in this [`View`]. This is affected by
     * the "split_by" configuration parameter supplied to this view's
     * contructor.
     *
     * # Returns
     *
     * The number of aggregated columns.
     * @returns {Promise<number>}
     */
    num_columns() {
        const ret = wasm.view_num_columns(this.__wbg_ptr);
        return takeObject(ret);
    }
    /**
     * Unregister a previously registered [`View::on_delete`] callback.
     * @param {number} callback_id
     * @returns {Promise<any>}
     */
    remove_delete(callback_id) {
        const ret = wasm.view_remove_delete(this.__wbg_ptr, callback_id);
        return takeObject(ret);
    }
    /**
     * Collapses the `group_by` row at `row_index`.
     * @param {number} row_index
     * @returns {Promise<number>}
     */
    collapse(row_index) {
        const ret = wasm.view_collapse(this.__wbg_ptr, row_index);
        return takeObject(ret);
    }
    /**
     * Expand the `group_by` row at `row_index`.
     * @param {number} row_index
     * @returns {Promise<number>}
     */
    expand(row_index) {
        const ret = wasm.view_expand(this.__wbg_ptr, row_index);
        return takeObject(ret);
    }
    /**
     * Set expansion `depth` of the `group_by` tree.
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
    imports.wbg.__wbg_at_7d852dd9f194d43e = function(arg0, arg1) {
        const ret = getObject(arg0).at(arg1);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_buffer_09165b52af8c5237 = function(arg0) {
        const ret = getObject(arg0).buffer;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_buffer_609cc3eee51ed158 = function(arg0) {
        const ret = getObject(arg0).buffer;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_call_672a4d21634d4a24 = function() { return handleError(function (arg0, arg1) {
        const ret = getObject(arg0).call(getObject(arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_call_7cccdd69e0791ae2 = function() { return handleError(function (arg0, arg1, arg2) {
        const ret = getObject(arg0).call(getObject(arg1), getObject(arg2));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_call_833bed5770ea2041 = function() { return handleError(function (arg0, arg1, arg2, arg3) {
        const ret = getObject(arg0).call(getObject(arg1), getObject(arg2), getObject(arg3));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_client_new = function(arg0) {
        const ret = Client.__wrap(arg0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_debug_3cb59063b29f58c1 = function(arg0) {
        console.debug(getObject(arg0));
    };
    imports.wbg.__wbg_debug_e17b51583ca6a632 = function(arg0, arg1, arg2, arg3) {
        console.debug(getObject(arg0), getObject(arg1), getObject(arg2), getObject(arg3));
    };
    imports.wbg.__wbg_done_769e5ede4b31c67b = function(arg0) {
        const ret = getObject(arg0).done;
        return ret;
    };
    imports.wbg.__wbg_entries_3265d4158b33e5dc = function(arg0) {
        const ret = Object.entries(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_error_1004b8c64097413f = function(arg0, arg1) {
        console.error(getObject(arg0), getObject(arg1));
    };
    imports.wbg.__wbg_error_524f506f44df1645 = function(arg0) {
        console.error(getObject(arg0));
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
    imports.wbg.__wbg_error_80de38b3f7cc3c3c = function(arg0, arg1, arg2, arg3) {
        console.error(getObject(arg0), getObject(arg1), getObject(arg2), getObject(arg3));
    };
    imports.wbg.__wbg_from_2a5d3e218e67aa85 = function(arg0) {
        const ret = Array.from(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_getEntriesByName_2a5a14d4b09f36a4 = function(arg0, arg1, arg2, arg3, arg4) {
        const ret = getObject(arg0).getEntriesByName(getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_getRandomValues_21a0191e74d0e1d3 = function() { return handleError(function (arg0, arg1) {
        globalThis.crypto.getRandomValues(getArrayU8FromWasm0(arg0, arg1));
    }, arguments) };
    imports.wbg.__wbg_get_67b2ba62fc30de12 = function() { return handleError(function (arg0, arg1) {
        const ret = Reflect.get(getObject(arg0), getObject(arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_get_74b8744f6a23f4fa = function(arg0, arg1, arg2) {
        const ret = getObject(arg0)[getStringFromWasm0(arg1, arg2)];
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_get_b9b93047fe3cf45b = function(arg0, arg1) {
        const ret = getObject(arg0)[arg1 >>> 0];
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_getwithrefkey_1dc361bd10053bfe = function(arg0, arg1) {
        const ret = getObject(arg0)[getObject(arg1)];
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_has_a5ea9117f258a0ec = function() { return handleError(function (arg0, arg1) {
        const ret = Reflect.has(getObject(arg0), getObject(arg1));
        return ret;
    }, arguments) };
    imports.wbg.__wbg_info_033d8b8a0838f1d3 = function(arg0, arg1, arg2, arg3) {
        console.info(getObject(arg0), getObject(arg1), getObject(arg2), getObject(arg3));
    };
    imports.wbg.__wbg_info_3daf2e093e091b66 = function(arg0) {
        console.info(getObject(arg0));
    };
    imports.wbg.__wbg_instanceof_ArrayBuffer_e14585432e3737fc = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof ArrayBuffer;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Array_6ac07133d621675a = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Array;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Error_4d54113b22d20306 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Error;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Map_f3469ce2244d2430 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Map;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Object_7f2dcef8f78644a4 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Object;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Uint8Array_17156bcf118086a9 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Uint8Array;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_instanceof_Window_def73ea0955fc569 = function(arg0) {
        let result;
        try {
            result = getObject(arg0) instanceof Window;
        } catch (_) {
            result = false;
        }
        const ret = result;
        return ret;
    };
    imports.wbg.__wbg_isArray_a1eab7e0d067391b = function(arg0) {
        const ret = Array.isArray(getObject(arg0));
        return ret;
    };
    imports.wbg.__wbg_isSafeInteger_343e2beeeece1bb0 = function(arg0) {
        const ret = Number.isSafeInteger(getObject(arg0));
        return ret;
    };
    imports.wbg.__wbg_iterator_9a24c88df860dc65 = function() {
        const ret = Symbol.iterator;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_keys_5c77a08ddc2fb8a6 = function(arg0) {
        const ret = Object.keys(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_length_a446193dc22c12f8 = function(arg0) {
        const ret = getObject(arg0).length;
        return ret;
    };
    imports.wbg.__wbg_length_e2d2a49132c1b256 = function(arg0) {
        const ret = getObject(arg0).length;
        return ret;
    };
    imports.wbg.__wbg_mark_001da84b098c950f = function() { return handleError(function (arg0, arg1, arg2) {
        getObject(arg0).mark(getStringFromWasm0(arg1, arg2));
    }, arguments) };
    imports.wbg.__wbg_measure_65e49f8bc0e203a8 = function() { return handleError(function (arg0, arg1, arg2, arg3, arg4) {
        getObject(arg0).measure(getStringFromWasm0(arg1, arg2), getStringFromWasm0(arg3, arg4));
    }, arguments) };
    imports.wbg.__wbg_message_97a2af9b89d693a3 = function(arg0) {
        const ret = getObject(arg0).message;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_23a2665fac83c611 = function(arg0, arg1) {
        try {
            var state0 = {a: arg0, b: arg1};
            var cb0 = (arg0, arg1) => {
                const a = state0.a;
                state0.a = 0;
                try {
                    return __wbg_adapter_251(a, state0.b, arg0, arg1);
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
    imports.wbg.__wbg_new_405e22f390576ce2 = function() {
        const ret = new Object();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_5e0be73521bc8c17 = function() {
        const ret = new Map();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_78feb108b6472713 = function() {
        const ret = new Array();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_8a6f238a6ece86ea = function() {
        const ret = new Error();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_a12002a7f91c75be = function(arg0) {
        const ret = new Uint8Array(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_new_c68d7209be747379 = function(arg0, arg1) {
        const ret = new Error(getStringFromWasm0(arg0, arg1));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_newnoargs_105ed471475aaf50 = function(arg0, arg1) {
        const ret = new Function(getStringFromWasm0(arg0, arg1));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_newwithbyteoffsetandlength_d97e637ebe145a9a = function(arg0, arg1, arg2) {
        const ret = new Uint8Array(getObject(arg0), arg1 >>> 0, arg2 >>> 0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_next_25feadfc0913fea9 = function(arg0) {
        const ret = getObject(arg0).next;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_next_6574e1a8a62d1055 = function() { return handleError(function (arg0) {
        const ret = getObject(arg0).next();
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_now_d18023d54d4e5500 = function(arg0) {
        const ret = getObject(arg0).now();
        return ret;
    };
    imports.wbg.__wbg_parse_def2e24ef1252aff = function() { return handleError(function (arg0, arg1) {
        const ret = JSON.parse(getStringFromWasm0(arg0, arg1));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_performance_c185c0cdc2766575 = function(arg0) {
        const ret = getObject(arg0).performance;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_push_737cfc8c1432c2c6 = function(arg0, arg1) {
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
    imports.wbg.__wbg_reject_b3fcf99063186ff7 = function(arg0) {
        const ret = Promise.reject(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_resolve_4851785c9c5f573d = function(arg0) {
        const ret = Promise.resolve(getObject(arg0));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_set_37837023f3d740e8 = function(arg0, arg1, arg2) {
        getObject(arg0)[arg1 >>> 0] = takeObject(arg2);
    };
    imports.wbg.__wbg_set_3f1d0b984ed272ed = function(arg0, arg1, arg2) {
        getObject(arg0)[takeObject(arg1)] = takeObject(arg2);
    };
    imports.wbg.__wbg_set_65595bdd868b3009 = function(arg0, arg1, arg2) {
        getObject(arg0).set(getObject(arg1), arg2 >>> 0);
    };
    imports.wbg.__wbg_set_8fc6bf8a5b1071d1 = function(arg0, arg1, arg2) {
        const ret = getObject(arg0).set(getObject(arg1), getObject(arg2));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_stack_0ed75d68575b0f3c = function(arg0, arg1) {
        const ret = getObject(arg1).stack;
        const ptr1 = passStringToWasm0(ret, wasm.__wbindgen_export_0, wasm.__wbindgen_export_1);
        const len1 = WASM_VECTOR_LEN;
        getDataViewMemory0().setInt32(arg0 + 4 * 1, len1, true);
        getDataViewMemory0().setInt32(arg0 + 4 * 0, ptr1, true);
    };
    imports.wbg.__wbg_startTime_c051731d0a31602f = function(arg0) {
        const ret = getObject(arg0).startTime;
        return ret;
    };
    imports.wbg.__wbg_static_accessor_GLOBAL_88a902d13a557d07 = function() {
        const ret = typeof global === 'undefined' ? null : global;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_static_accessor_GLOBAL_THIS_56578be7e9f832b0 = function() {
        const ret = typeof globalThis === 'undefined' ? null : globalThis;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_static_accessor_SELF_37c5d418e4bf5819 = function() {
        const ret = typeof self === 'undefined' ? null : self;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_static_accessor_WINDOW_5de37043a91a9c40 = function() {
        const ret = typeof window === 'undefined' ? null : window;
        return isLikeNone(ret) ? 0 : addHeapObject(ret);
    };
    imports.wbg.__wbg_stringify_f7ed6987935b4a24 = function() { return handleError(function (arg0) {
        const ret = JSON.stringify(getObject(arg0));
        return addHeapObject(ret);
    }, arguments) };
    imports.wbg.__wbg_table_new = function(arg0) {
        const ret = Table.__wrap(arg0);
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_then_44b73946d2fb3e7d = function(arg0, arg1) {
        const ret = getObject(arg0).then(getObject(arg1));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_then_48b406749878a531 = function(arg0, arg1, arg2) {
        const ret = getObject(arg0).then(getObject(arg1), getObject(arg2));
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_toString_5285597960676b7b = function(arg0) {
        const ret = getObject(arg0).toString();
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_trace_d12a9ac890a2cbb8 = function(arg0, arg1, arg2, arg3) {
        console.trace(getObject(arg0), getObject(arg1), getObject(arg2), getObject(arg3));
    };
    imports.wbg.__wbg_trace_e758b839df8d34f1 = function(arg0) {
        console.trace(getObject(arg0));
    };
    imports.wbg.__wbg_value_cd1ffa7b1ab794f1 = function(arg0) {
        const ret = getObject(arg0).value;
        return addHeapObject(ret);
    };
    imports.wbg.__wbg_values_fcb8ba8c0aad8b58 = function(arg0) {
        const ret = Object.values(getObject(arg0));
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
    imports.wbg.__wbg_warn_4ca3906c248c47c4 = function(arg0) {
        console.warn(getObject(arg0));
    };
    imports.wbg.__wbg_warn_aaf1f4664a035bd6 = function(arg0, arg1, arg2, arg3) {
        console.warn(getObject(arg0), getObject(arg1), getObject(arg2), getObject(arg3));
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
    imports.wbg.__wbindgen_closure_wrapper3224 = function(arg0, arg1, arg2) {
        const ret = makeMutClosure(arg0, arg1, 468, __wbg_adapter_53);
        return addHeapObject(ret);
    };
    imports.wbg.__wbindgen_closure_wrapper367 = function(arg0, arg1, arg2) {
        const ret = makeClosure(arg0, arg1, 7, __wbg_adapter_50);
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
