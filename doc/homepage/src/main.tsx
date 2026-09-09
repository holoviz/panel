import createCache from '@emotion/cache'
import {CacheProvider} from '@emotion/react'
import {StrictMode} from 'react'
import {hydrateRoot} from 'react-dom/client'

import {App} from './App'

const cache = createCache({key: 'css'})

hydrateRoot(
  document.getElementById('root')!,
  <StrictMode>
    <CacheProvider value={cache}>
      <App />
    </CacheProvider>
  </StrictMode>,
)
