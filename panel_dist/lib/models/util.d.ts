export declare const get: (obj: any, path: string, defaultValue?: any) => any;
export declare function throttle(func: Function, limit: number): any;
export declare function deepCopy(obj: any): any;
export declare function reshape(arr: any[], dim: number[]): any[];
export declare function loadScript(type: string, src: string): Promise<void>;
export declare function ID(): string;
export declare function convertUndefined(obj: any): any;
export declare function formatError(error: SyntaxError, code: string): string;
export declare function find_attributes(text: string, obj: string, ignored: string[]): string[];
export declare function schedule_when(func: () => void, predicate: () => boolean, timeout?: number): void;
export declare const MARK = "--x_x--0_0--";
interface CompileOptions {
    mode?: "expression" | "statement";
    args?: string[];
}
export declare function compileToFunction(code: string, options?: CompileOptions): (...args: any[]) => any;
export declare function transformJsPlaceholders<T>(input: T, options?: CompileOptions): T;
export {};
//# sourceMappingURL=util.d.ts.map