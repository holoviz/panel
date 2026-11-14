import react from '@vitejs/plugin-react'
import {defineConfig} from 'vite'

// Every hashed asset lands under /_home/ so the Lambda@Edge redirector can pass the
// homepage through with a single prefix check instead of an allowlist of directory
// names that collide with what Sphinx builds. See plans/docs-homepage-and-versioning.md.
export default defineConfig({
  base: '/',
  plugins: [react()],
  build: {
    assetsDir: '_home',
    sourcemap: true,
    target: 'es2022',
  },
})
