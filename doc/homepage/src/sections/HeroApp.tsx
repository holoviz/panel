import Box from '@mui/material/Box'
import Slider from '@mui/material/Slider'
import ToggleButton from '@mui/material/ToggleButton'
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup'
import Typography from '@mui/material/Typography'
import {useMemo} from 'react'

import type {HeroKey} from '../content/site'
import {chartGeometry} from '../lib/series'
import {monoFamily, tokens} from '../theme'

export interface HeroState {
  window: number
  sigma: number
  ticker: string
}

const TICKERS = ['AAPL', 'MSFT', 'NVDA']
const KNOCKOUT = tokens.mist

/**
 * The hero is Panel's logo mark at page width, and it works.
 *
 * Controls on the left, result on the right, both knocked out of a blue field exactly as
 * the mark is. It is built from MUI components and an inline SVG rather than an iframe to
 * a deployed app or an in-page Pyodide runtime: the first would make the most important
 * element on the page depend on a demo deployment staying up, and the second costs ten
 * megabytes before anything appears.
 */
export function HeroApp({
  state,
  onChange,
  active,
  onHover,
}: {
  state: HeroState
  onChange: (next: Partial<HeroState>) => void
  active: HeroKey | null
  onHover: (key: HeroKey | null) => void
}) {
  const geometry = useMemo(
    () => chartGeometry(state.ticker, state.sigma, state.window),
    [state.ticker, state.sigma, state.window],
  )

  // Hovering a line of the code below steps back the parts of the app that line did not
  // produce. Receding the rest rather than outlining the match keeps the emphasis inside
  // the panes, where an inset hairline in the knockout grey would be lost against the blue.
  // The layout line produced all of it, so nothing recedes for that one.
  const recede = (key: HeroKey) => ({
    opacity: active && active !== 'layout' && active !== key ? 0.32 : 1,
    transition: 'opacity 200ms ease',
  })

  return (
    <Box
      data-hero-region="layout"
      onMouseLeave={() => onHover(null)}
      sx={{
        display: 'grid',
        gridTemplateColumns: {xs: '1fr', md: 'minmax(230px, 19rem) 1fr'},
        borderRadius: 3.5,
        overflow: 'hidden',
        bgcolor: tokens.panel,
        // Both panes are saturated blue, so the accent-coloured focus ring would disappear
        // into them. Everything focusable inside the app rings in the knockout grey instead.
        '--focus-ring': KNOCKOUT,
      }}
    >
      <Box
        data-hero-region="widgets"
        onMouseEnter={() => onHover('widgets')}
        sx={{
          bgcolor: tokens.panelDeep,
          color: KNOCKOUT,
          px: {xs: 2.5, md: 3},
          py: {xs: 3, md: 3.5},
          display: 'flex',
          flexDirection: 'column',
          gap: 3.25,
          ...recede('widgets'),
        }}
      >
        <ControlLabel label="Window" value={`${state.window} days`} />
        <Slider
          value={state.window}
          min={5}
          max={90}
          onChange={(_, v) => onChange({window: v as number})}
          aria-label="Smoothing window in days"
          sx={sliderSx}
        />

        <ControlLabel label="Volatility" value={state.sigma.toFixed(1)} />
        <Slider
          value={state.sigma}
          min={0.2}
          max={3}
          step={0.1}
          onChange={(_, v) => onChange({sigma: v as number})}
          aria-label="Volatility"
          sx={sliderSx}
        />

        <Box sx={{mt: 'auto'}}>
          <ControlLabel label="Series" />
          <ToggleButtonGroup
            exclusive
            fullWidth
            size="small"
            value={state.ticker}
            onChange={(_, v) => v && onChange({ticker: v as string})}
            aria-label="Series"
            sx={{
              mt: 1.25,
              '& .MuiToggleButton-root': {
                color: 'rgba(238,238,238,0.72)',
                borderColor: 'rgba(238,238,238,0.34)',
                fontFamily: monoFamily,
                fontSize: '0.8125rem',
                letterSpacing: '0.01em',
                py: 0.6,
              },
              '& .MuiToggleButton-root.Mui-selected': {
                color: tokens.panelDeep,
                bgcolor: KNOCKOUT,
                '&:hover': {bgcolor: KNOCKOUT},
              },
            }}
          >
            {TICKERS.map((t) => (
              <ToggleButton key={t} value={t}>
                {t}
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
        </Box>
      </Box>

      <Box
        data-hero-region="bind"
        onMouseEnter={() => onHover('bind')}
        sx={{
          position: 'relative',
          px: {xs: 1, md: 1.5},
          pt: {xs: 2.5, md: 3},
          pb: {xs: 1, md: 1.5},
          minHeight: {xs: 220, md: 300},
          ...recede('bind'),
        }}
      >
        <Box
          sx={{
            display: 'flex',
            gap: 2.5,
            px: 1.5,
            mb: 0.5,
            color: 'rgba(238,238,238,0.82)',
            fontSize: '0.8125rem',
            fontWeight: 500,
          }}
        >
          <LegendItem faint>observed</LegendItem>
          <LegendItem>{state.window} day mean</LegendItem>
        </Box>
        <Box
          component="svg"
          viewBox={`0 0 ${geometry.width} ${geometry.height}`}
          preserveAspectRatio="none"
          role="img"
          aria-label={`Simulated ${state.ticker} series with a ${state.window} day moving average at volatility ${state.sigma.toFixed(1)}`}
          sx={{display: 'block', width: '100%', height: {xs: 190, md: 260}}}
        >
          <line
            x1={0}
            x2={geometry.width}
            y1={geometry.zero}
            y2={geometry.zero}
            stroke={KNOCKOUT}
            strokeOpacity={0.28}
            strokeWidth={1.5}
            strokeDasharray="2 6"
          />
          <path d={geometry.raw} fill="none" stroke={KNOCKOUT} strokeOpacity={0.42} strokeWidth={2} />
          <Box
            component="path"
            d={geometry.smooth}
            fill="none"
            stroke={KNOCKOUT}
            strokeWidth={5}
            strokeLinecap="round"
            strokeLinejoin="round"
            pathLength={1}
            sx={{
              // The single piece of motion on the page that nobody asked for: the curve
              // draws itself once, the way the logo's curve would if it were drawn.
              strokeDasharray: 1,
              animation: 'panel-draw 1100ms cubic-bezier(0.22, 0.61, 0.36, 1) both',
              '@keyframes panel-draw': {
                from: {strokeDashoffset: 1},
                to: {strokeDashoffset: 0},
              },
            }}
          />
        </Box>
      </Box>
    </Box>
  )
}

const sliderSx = {
  color: KNOCKOUT,
  mt: -1.5,
  py: 1.25,
  '& .MuiSlider-rail': {opacity: 0.32},
  '& .MuiSlider-thumb': {
    width: 18,
    height: 18,
    '&:hover, &.Mui-focusVisible': {boxShadow: '0 0 0 7px rgba(238,238,238,0.2)'},
  },
} as const

function ControlLabel({label, value}: {label: string; value?: string}) {
  return (
    <Box sx={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline'}}>
      <Typography component="span" sx={{fontSize: '0.9375rem', fontWeight: 550}}>
        {label}
      </Typography>
      {value && (
        <Typography
          component="span"
          sx={{fontFamily: monoFamily, fontSize: '0.8125rem', color: 'rgba(238,238,238,0.72)'}}
        >
          {value}
        </Typography>
      )}
    </Box>
  )
}

function LegendItem({children, faint}: {children: React.ReactNode; faint?: boolean}) {
  return (
    <Box component="span" sx={{display: 'inline-flex', alignItems: 'center', gap: 0.875}}>
      <Box
        component="span"
        sx={{
          width: 18,
          height: faint ? 2 : 4,
          borderRadius: 2,
          bgcolor: KNOCKOUT,
          opacity: faint ? 0.42 : 1,
        }}
      />
      {children}
    </Box>
  )
}
