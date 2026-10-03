import Box from '@mui/material/Box'
import Link from '@mui/material/Link'
import Typography from '@mui/material/Typography'

import {Section, type Band} from '../components/Section'
import {DOCS, gallery} from '../content/site'

/**
 * Whole-window screenshots, so the first entry gets two columns and two rows and the reader
 * sees one app at a size where its controls are legible. On wide screens the featured image
 * stretches to the height of the two tiles beside it, cropping from the bottom, so the two
 * columns end on the same line whatever the caption lengths.
 */
export function Gallery({wash}: Band) {
  return (
    <Section
      id="examples"
      title="Apps people actually built"
      lede="Every one of these ships with the source that produced it. Read the code, take the parts you need, or run the whole thing yourself."
      wash={wash}
    >
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {xs: 'minmax(0, 1fr)', sm: 'repeat(2, minmax(0, 1fr))', md: 'repeat(3, minmax(0, 1fr))'},
          columnGap: 3,
          rowGap: {xs: 3.5, md: 4},
        }}
      >
        {gallery.map((app, i) => {
          const featured = i === 0
          return (
            <Box
              key={app.name}
              component="a"
              href={app.href}
              data-gallery-app={app.name}
              sx={{
                textDecoration: 'none',
                color: 'inherit',
                display: 'flex',
                flexDirection: 'column',
                gap: 1.25,
                gridColumn: featured ? {sm: 'span 2'} : undefined,
                gridRow: featured ? {md: 'span 2'} : undefined,
                '&:hover .shot-title': {color: 'primary.main'},
                '&:hover img': {borderColor: 'primary.main'},
              }}
            >
              <Box
                component="img"
                src={app.image}
                alt={`Screenshot of the ${app.title} app`}
                width={1440}
                height={900}
                loading={featured ? 'eager' : 'lazy'}
                decoding="async"
                sx={{
                  display: 'block',
                  width: '100%',
                  height: featured ? {xs: 'auto', md: 0} : 'auto',
                  aspectRatio: featured ? {xs: '16 / 10', md: 'auto'} : '16 / 10',
                  flex: featured ? {md: '1 1 0'} : undefined,
                  minHeight: featured ? {md: 0} : undefined,
                  objectFit: 'cover',
                  objectPosition: 'top left',
                  backgroundColor: 'background.paper',
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 1,
                  transition: 'border-color 160ms ease',
                }}
              />
              <Box>
                <Typography
                  component="h3"
                  className="shot-title"
                  sx={{fontSize: featured ? '1.125rem' : '1rem', fontWeight: 600, transition: 'color 160ms ease'}}
                >
                  {app.title}
                </Typography>
                <Typography
                  variant={featured ? 'body2' : 'caption'}
                  component="p"
                  sx={{color: 'text.secondary', mt: 0.25}}
                >
                  {app.note}
                </Typography>
              </Box>
            </Box>
          )
        })}
      </Box>
      <Link href={`${DOCS}/gallery/index.html`} sx={{display: 'inline-block', mt: 4.5}}>
        Browse all examples
      </Link>
    </Section>
  )
}
