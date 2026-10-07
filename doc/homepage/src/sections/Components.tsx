import Box from '@mui/material/Box'
import Link from '@mui/material/Link'

import {Section, type Band} from '../components/Section'
import {Tile} from '../components/Tile'
import {components} from '../content/site'

/**
 * Every tile is a real component with a real page behind it, which is the point: the answer
 * to "can Panel do a terminal, a pivot table, a chat window" is a picture and a link rather
 * than a sentence promising it can.
 */
export function Components({wash}: Band) {
  return (
    <Section id="components" title={components.title} lede={components.lede} wash={wash}>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: 'repeat(2, minmax(0, 1fr))',
            sm: 'repeat(3, minmax(0, 1fr))',
            md: 'repeat(4, minmax(0, 1fr))',
          },
          gap: {xs: 2, md: 3},
        }}
      >
        {components.items.map((item) => (
          <Tile
            key={item.name}
            href={item.href}
            image={item.image}
            alt={`The ${item.name} component`}
            title={item.name}
            caption={item.note}
          />
        ))}
      </Box>
      <Link href={components.link.href} sx={{display: 'inline-block', mt: 4.5}}>
        {components.link.label}
      </Link>
    </Section>
  )
}
