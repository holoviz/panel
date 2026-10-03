import Box from '@mui/material/Box'
import Link from '@mui/material/Link'
import Typography from '@mui/material/Typography'

import {Section, type Band} from '../components/Section'
import {Tile} from '../components/Tile'
import {panes} from '../content/site'
import {monoFamily} from '../theme'

/**
 * The claim is visual: what arrives on the page is the library's own output, not a house
 * style applied to it, so every library gets a picture at once rather than one at a time.
 */
export function Panes({wash}: Band) {
  return (
    <Section id="panes" title={panes.title} lede={panes.lede} wash={wash}>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {xs: 'repeat(2, minmax(0, 1fr))', md: 'repeat(4, minmax(0, 1fr))'},
          gap: {xs: 2, md: 3},
        }}
      >
        {panes.items.map((pane) => (
          <Tile
            key={pane.name}
            href={pane.href}
            image={pane.image}
            alt={`A ${pane.name} figure rendered by Panel`}
            title={pane.name}
            caption={
              <>
                <Box component="span" sx={{fontFamily: monoFamily, display: 'block'}}>
                  {pane.api}
                </Box>
                {pane.note}
              </>
            }
          />
        ))}
      </Box>
      <Typography variant="body2" sx={{mt: 4, color: 'text.secondary'}}>
        Also{' '}
        {panes.more.map((item, i) => (
          <span key={item.name}>
            {i > 0 && (i === panes.more.length - 1 ? ' and ' : ', ')}
            <Link href={item.href}>{item.name}</Link>
          </span>
        ))}
        , plus anything with a <Box component="code" sx={{fontFamily: monoFamily}}>_repr_html_</Box>.
      </Typography>
    </Section>
  )
}
