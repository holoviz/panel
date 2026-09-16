import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Container from '@mui/material/Container'
import Typography from '@mui/material/Typography'
import {useMemo, useState} from 'react'

import {CodeBlock} from '../components/CodeBlock'
import {InstallCommand} from '../components/InstallCommand'
import type {HeroKey} from '../content/site'
import {hero, heroCode, heroRegions} from '../content/site'
import {surfaces} from '../theme'
import {HeroApp, type HeroState} from './HeroApp'

/** Consecutive lines sharing a key become one row, so the code and the app line up by row. */
function useCodeRows() {
  return useMemo(() => {
    const rows: {key: HeroKey | null; source: string}[] = []
    for (const line of heroCode) {
      const last = rows[rows.length - 1]
      if (last && last.key === line.key) last.source += `\n${line.text}`
      else rows.push({key: line.key, source: line.text})
    }
    return rows
      .map((r) => ({...r, source: r.source.replace(/^\n+|\n+$/g, '')}))
      .filter((r) => r.source.length > 0)
  }, [])
}

export function Hero() {
  const [state, setState] = useState<HeroState>({window: 30, sigma: 1, ticker: 'AAPL'})
  const [active, setActive] = useState<HeroKey | null>(null)
  const rows = useCodeRows()

  return (
    <Box component="section" sx={{pt: {xs: 6, md: 9}, pb: {xs: 7, md: 10}}}>
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: {xs: '1fr', md: '1.1fr 0.9fr'},
            columnGap: {md: 8},
            rowGap: 3.5,
            alignItems: 'start',
          }}
        >
          <Typography variant="h1" component="h1" sx={{maxWidth: '24ch'}}>
            {hero.title}
          </Typography>
          {/*
            The headline is set at a line height of 1.02, so its first cap sits further below the
            top of its box than the lede's does. Nudging the column down puts the two first lines
            on the same optical edge rather than the same box edge.
          */}
          <Box sx={{pt: {md: 1.25}}}>
            <Typography variant="body1" sx={{color: 'text.secondary', maxWidth: '38rem'}}>
              {hero.lede}
            </Typography>
            <Box sx={{display: 'flex', flexWrap: 'wrap', gap: 1.5, mt: 3.5, alignItems: 'center'}}>
              <Button variant="contained" size="large" href={hero.primary.href}>
                {hero.primary.label}
              </Button>
              <Button
                size="large"
                variant="outlined"
                href={hero.secondary.href}
                sx={{color: 'text.primary', borderColor: 'divider'}}
              >
                {hero.secondary.label}
              </Button>
            </Box>
            <Box sx={{mt: 2.5, maxWidth: '30rem'}}>
              <InstallCommand commands={{pip: hero.install, conda: hero.installConda}} />
            </Box>
          </Box>
        </Box>

        <Box sx={{mt: {xs: 6, md: 8}}}>
          <HeroApp state={state} onChange={(next) => setState((s) => ({...s, ...next}))} active={active} onHover={setActive} />
        </Box>

        <Box
          sx={{
            mt: 3,
            bgcolor: surfaces.code,
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 2,
            overflow: 'hidden',
          }}
        >
          {rows.map((row, i) => (
            <Box
              key={i}
              data-hero-row={row.key ?? 'setup'}
              onMouseEnter={() => row.key && setActive(row.key)}
              onMouseLeave={() => setActive(null)}
              sx={{
                display: 'grid',
                gridTemplateColumns: {xs: '1fr', md: '15rem minmax(0, 1fr)'},
                gap: {xs: 0.75, md: 3},
                px: {xs: 2, md: 3},
                py: {xs: 2, md: 2.25},
                borderTop: i === 0 ? 0 : '1px solid',
                borderColor: 'divider',
                backgroundColor: row.key && active === row.key ? 'action.hover' : 'transparent',
                transition: 'background-color 160ms ease',
              }}
            >
              <Typography
                variant="body2"
                sx={{
                  color: row.key && active === row.key ? 'primary.main' : 'text.secondary',
                  transition: 'color 160ms ease',
                }}
              >
                {row.key ? heroRegions[row.key] : 'Two imports and one line of setup.'}
              </Typography>
              <CodeBlock source={row.source} fontSize={{xs: '0.8125rem', md: '0.875rem'}} />
            </Box>
          ))}
        </Box>
      </Container>
    </Box>
  )
}
