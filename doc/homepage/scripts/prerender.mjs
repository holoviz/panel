import {readFile, writeFile} from 'node:fs/promises'
import {dirname, resolve} from 'node:path'
import {fileURLToPath} from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const template = await readFile(resolve(root, 'dist/index.html'), 'utf8')
const {render} = await import(resolve(root, 'dist-ssr/entry-server.js'))

const {html, head} = render()

for (const marker of ['<!--app-html-->', '<!--app-head-->']) {
  if (!template.includes(marker)) {
    throw new Error(`dist/index.html is missing ${marker}; prerendering would produce a blank page`)
  }
}

const page = template.replace('<!--app-head-->', head).replace('<!--app-html-->', html)

await writeFile(resolve(root, 'dist/index.html'), page)
console.log(`prerendered dist/index.html (${(page.length / 1024).toFixed(1)} kB)`)
