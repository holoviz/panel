declare module "json-formatter-js";
declare module "@luma.gl/constants";
declare module "underscore.template" {
  export const _: {
    template(template: string): (context: {[key: string]: unknown}) => string
  }
}
