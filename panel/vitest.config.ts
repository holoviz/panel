import {defineConfig} from "vitest/config"
import path from "path"

export default defineConfig({
  test: {
    environment: "jsdom",
    include: ["__tests__/**/*.test.ts"],
    globals: true,
  },
  resolve: {
    alias: {
      // Redirect the reactive_esm import to a lightweight stub
      "./reactive_esm": path.resolve(__dirname, "__tests__/mocks/reactive_esm.ts"),
      // Bokeh path aliases — not needed for our tests but prevents import errors
      "@bokehjs/core/properties": path.resolve(__dirname, "__tests__/mocks/bokeh_stubs.ts"),
      "@bokehjs/core/bokeh_events": path.resolve(__dirname, "__tests__/mocks/bokeh_stubs.ts"),
      "@bokehjs/core/dom": path.resolve(__dirname, "__tests__/mocks/bokeh_stubs.ts"),
      "@bokehjs/core/kinds": path.resolve(__dirname, "__tests__/mocks/bokeh_stubs.ts"),
      "@bokehjs/core/types": path.resolve(__dirname, "__tests__/mocks/bokeh_stubs.ts"),
      "@bokehjs/models/layouts/layout_dom": path.resolve(__dirname, "__tests__/mocks/bokeh_stubs.ts"),
      "@bokehjs/models/ui/ui_element": path.resolve(__dirname, "__tests__/mocks/bokeh_stubs.ts"),
      "@bokehjs/core/util/types": path.resolve(__dirname, "__tests__/mocks/bokeh_stubs.ts"),
      "sucrase": path.resolve(__dirname, "__tests__/mocks/bokeh_stubs.ts"),
    },
  },
})
