import createCache from '@emotion/cache'
import {CacheProvider} from '@emotion/react'
import createEmotionServer from '@emotion/server/create-instance'
import {renderToString} from 'react-dom/server'

import {App} from './App'

/**
 * Renders the page to markup at build time. The homepage is static, so shipping HTML rather
 * than an empty div means the headline and the hero are painted before React loads, and
 * crawlers see the copy without executing anything.
 */
export function render() {
  const cache = createCache({key: 'css'})
  const {extractCriticalToChunks, constructStyleTagsFromChunks} = createEmotionServer(cache)

  const html = renderToString(
    <CacheProvider value={cache}>
      <App />
    </CacheProvider>,
  )

  const {styles} = extractCriticalToChunks(html)
  return {html, head: constructStyleTagsFromChunks({html, styles})}
}
