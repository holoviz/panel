import CssBaseline from '@mui/material/CssBaseline'
import InitColorSchemeScript from '@mui/material/InitColorSchemeScript'
import {ThemeProvider} from '@mui/material/styles'

import {Adoption} from './sections/Adoption'
import {Capabilities} from './sections/Capabilities'
import {Components} from './sections/Components'
import {Execution} from './sections/Execution'
import {Footer} from './sections/Footer'
import {Gallery} from './sections/Gallery'
import {Growth} from './sections/Growth'
import {Header} from './sections/Header'
import {Hero} from './sections/Hero'
import {Panes} from './sections/Panes'
import {Paths} from './sections/Paths'
import {theme} from './theme'

export function App() {
  return (
    <ThemeProvider theme={theme} defaultMode="system">
      <InitColorSchemeScript attribute="data-color-scheme" defaultMode="system" />
      <CssBaseline />
      <Header />
      {/*
        The argument follows the headline: how updates work, then how the code grows, then how
        it ships. Sections alternate between the white page and a washed band, so the reader
        always knows where one ended.
      */}
      <main>
        <Hero />
        <Execution wash />
        <Growth />
        <Paths wash />
        <Panes />
        <Components wash />
        <Capabilities />
        <Gallery wash />
        <Adoption />
      </main>
      <Footer />
    </ThemeProvider>
  )
}
