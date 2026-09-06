import Box from '@mui/material/Box'
import Link from '@mui/material/Link'
import Typography from '@mui/material/Typography'

import {Section, type Band} from '../components/Section'
import {DOCS, gallery} from '../content/site'

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
          gridTemplateColumns: {xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)'},
          columnGap: {xs: 3, md: 3},
          rowGap: {xs: 3.5, md: 4},
        }}
      >
        {gallery.map((app) => (
          <Box
            key={app.name}
            component="a"
            href={app.href}
            sx={{
              textDecoration: 'none',
              color: 'inherit',
              display: 'flex',
              flexDirection: 'column',
              gap: 1.25,
              '&:hover .shot-title': {color: 'primary.main'},
            }}
          >
            <Box
              component="img"
              src={app.image}
              alt={`Screenshot of the ${app.title} app`}
              loading="lazy"
              decoding="async"
              sx={{
                display: 'block',
                width: '100%',
                // The thumbnails are square; 4:3 trims the bottom quarter, which on an app
                // screenshot is usually whitespace below the plot.
                aspectRatio: '4 / 3',
                objectFit: 'cover',
                objectPosition: 'top center',
                backgroundColor: 'background.paper',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
              }}
            />
            <Box>
              <Typography
                component="h3"
                className="shot-title"
                sx={{fontSize: '1rem', fontWeight: 600, transition: 'color 160ms ease'}}
              >
                {app.title}
              </Typography>
              <Typography variant="caption" component="p" sx={{color: 'text.secondary', mt: 0.25}}>
                {app.note}
              </Typography>
            </Box>
          </Box>
        ))}
      </Box>
      <Link href={`${DOCS}/gallery/index.html`} sx={{display: 'inline-block', mt: 4.5}}>
        Browse all examples
      </Link>
    </Section>
  )
}
