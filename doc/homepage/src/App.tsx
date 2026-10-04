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
        How updates work, then real apps as proof before the longer argument about how the code
        grows and ships. Sections alternate between the white page and a washed band, so the
        reader always knows where one ended.
      */}
      <main>
        <Hero />
        <Execution wash />
        <Gallery />
        <Growth wash />
        <Paths />
        <Panes wash />
        <Components />
        <Capabilities wash />
        <Adoption />
      </main>
      <Footer />
    </ThemeProvider>
  )
}
