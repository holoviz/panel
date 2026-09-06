import Box from '@mui/material/Box'
import Link from '@mui/material/Link'
import Tab from '@mui/material/Tab'
import Tabs from '@mui/material/Tabs'
import Typography from '@mui/material/Typography'
import useMediaQuery from '@mui/material/useMediaQuery'
import type {Theme} from '@mui/material/styles'
import {useState} from 'react'

import {Section, type Band} from '../components/Section'
import {panes} from '../content/site'
import {monoFamily, tokens} from '../theme'

/**
 * Pick a library, see what it looks like rendered through Panel.
 *
 * A list of names would say the same thing in less space, but the claim here is visual: what
 * arrives on the page is the library's own output, not a house style applied to it, and you
 * can only see that by looking. The pictures are the reference gallery's own thumbnails, so
 * this section cannot drift away from the docs it points at.
 */
export function Panes({wash}: Band) {
  const [index, setIndex] = useState(0)
  const pane = panes.items[index]
  /**
   * Eleven names stacked vertically fill a phone screen before the picture the list exists to
   * change, so on narrow viewports the list becomes a scrolling row. Tabs takes its
   * orientation as a prop rather than from CSS, hence the media query. It defaults to matching
   * so the prerendered HTML is the wide layout, and the correction on a phone happens during
   * hydration, well before this section scrolls into view.
   */
  const wide = useMediaQuery((theme: Theme) => theme.breakpoints.up('md'), {defaultMatches: true})

  return (
    <Section id="panes" title={panes.title} lede={panes.lede} wash={wash}>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {xs: '1fr', md: '15rem 1fr'},
          columnGap: {md: 6},
          rowGap: 3,
          alignItems: 'start',
        }}
      >
        <Tabs
          orientation={wide ? 'vertical' : 'horizontal'}
          variant="scrollable"
          scrollButtons={false}
          value={index}
          onChange={(_, next) => setIndex(next as number)}
          aria-label="Plotting libraries"
          sx={{
            // Vertical tabs put the indicator on the right edge by default, which would read
            // as pointing away from the list it belongs to.
            ...(wide
              ? {'& .MuiTabs-indicator': {left: 0, right: 'auto', width: 2}, borderLeft: '1px solid'}
              : {borderBottom: '1px solid'}),
            borderColor: 'divider',
            '& .MuiTabs-flexContainer': {alignItems: 'stretch'},
          }}
        >
          {panes.items.map((item, i) => (
            <Tab
              key={item.name}
              id={`pane-tab-${i}`}
              aria-controls="pane-panel"
              label={item.name}
              disableRipple
              sx={{
                textTransform: 'none',
                alignItems: 'flex-start',
                textAlign: 'left',
                whiteSpace: 'nowrap',
                minHeight: 0,
                px: 2,
                py: 1.125,
                fontSize: '0.9375rem',
                fontWeight: 500,
                color: 'text.secondary',
                '&.Mui-selected': {fontWeight: 600},
              }}
            />
          ))}
        </Tabs>

        {/* Capped so the 500px source is never asked to stretch to fill a wide column. */}
        <Box role="tabpanel" id="pane-panel" aria-labelledby={`pane-tab-${index}`} sx={{maxWidth: 680}}>
          <Box
            component="img"
            src={pane.image}
            alt={`A ${pane.name} figure rendered by Panel`}
            decoding="async"
            sx={{
              display: 'block',
              width: '100%',
              // The thumbnails are square. A 4:3 plate with the picture contained rather than
              // cropped fills the column without taking a bite out of somebody's axis labels,
              // and the leftover margin is invisible because the plate is white anyway.
              aspectRatio: '4 / 3',
              objectFit: 'contain',
              // These are screenshots taken against a light background with their padding left
              // transparent, so the plate stays white in both schemes rather than letting the
              // dark page show through the middle of a table.
              backgroundColor: tokens.white,
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 2,
            }}
          />
          <Box
            sx={{
              mt: 2,
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'baseline',
              justifyContent: 'space-between',
              gap: 2,
            }}
          >
            <Typography component="p" sx={{fontFamily: monoFamily, fontSize: '0.9375rem'}}>
              {pane.api}
            </Typography>
            <Link href={pane.href} variant="body2">
              {pane.name} reference
            </Link>
          </Box>
          <Typography variant="body2" sx={{mt: 1, color: 'text.secondary'}}>
            {pane.note}
          </Typography>
        </Box>
      </Box>
    </Section>
  )
}
