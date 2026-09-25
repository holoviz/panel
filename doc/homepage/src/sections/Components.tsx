import Box from '@mui/material/Box'
import Link from '@mui/material/Link'
import Typography from '@mui/material/Typography'

import {Section, type Band} from '../components/Section'
import {components} from '../content/site'
import {tokens} from '../theme'

/**
 * A dozen of the reference gallery's own thumbnails, linked to the pages they came from.
 *
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
          gridTemplateColumns: {xs: 'repeat(2, 1fr)', sm: 'repeat(3, 1fr)', md: 'repeat(4, 1fr)'},
          gap: {xs: 2, md: 3},
        }}
      >
        {components.items.map((item) => (
          <Box
            key={item.name}
            component="a"
            href={item.href}
            sx={{
              textDecoration: 'none',
              color: 'inherit',
              display: 'flex',
              flexDirection: 'column',
              '&:hover .component-name': {color: 'primary.main'},
            }}
          >
            <Box
              component="img"
              src={item.image}
              alt={`The ${item.name} component`}
              width={500}
              height={500}
              loading="lazy"
              decoding="async"
              sx={{
                display: 'block',
                width: '100%',
                // The width and height attributes above reserve the space before the image
                // loads, but they also set a presentational height that would beat the
                // aspect ratio, so the height has to be handed back to CSS explicitly.
                height: 'auto',
                // The thumbnails are square with the component sitting in the upper middle
                // and transparent padding around it. Cropping to 4:3, biased towards the top,
                // trims most of that padding without cutting into the component itself.
                aspectRatio: '4 / 3',
                objectFit: 'cover',
                objectPosition: '50% 30%',
                // Light screenshots with transparent padding, so the plate stays white even
                // in dark mode. See sections/Panes.tsx.
                backgroundColor: tokens.white,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
              }}
            />
            <Typography
              component="h3"
              className="component-name"
              sx={{mt: 1.25, fontSize: '0.9375rem', fontWeight: 600, transition: 'color 160ms ease'}}
            >
              {item.name}
            </Typography>
            <Typography variant="caption" component="p" sx={{color: 'text.secondary', mt: 0.25}}>
              {item.note}
            </Typography>
          </Box>
        ))}
      </Box>
      <Link href={components.link.href} sx={{display: 'inline-block', mt: 4.5}}>
        {components.link.label}
      </Link>
    </Section>
  )
}
