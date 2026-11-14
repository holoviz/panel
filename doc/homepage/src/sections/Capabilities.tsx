import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'

import {Section, type Band} from '../components/Section'
import {capabilities} from '../content/site'

/**
 * Label left, detail right, one row each: the same row rhythm as the hero's code strip, so
 * the page keeps a single reading pattern instead of introducing a card grid here.
 */
export function Capabilities({wash}: Band) {
  return (
    <Section
      wash={wash}
      id="capabilities"
      title="Extend your app"
      lede="Handle live data, add custom interfaces and manage access to your app. The guides below cover these features in detail."
    >
      <Box sx={{borderTop: '1px solid', borderColor: 'divider'}}>
        {capabilities.map((item) => (
          <Box
            key={item.title}
            component="a"
            href={item.href}
            sx={{
              display: 'grid',
              gridTemplateColumns: {xs: '1fr', md: '20rem 1fr'},
              gap: {xs: 0.75, md: 5},
              py: {xs: 2.5, md: 3},
              textDecoration: 'none',
              color: 'inherit',
              // Rules span the content width, the same as the top rule, so no hover wash that
              // would need padding past the text edge.
              borderBottom: '1px solid',
              borderColor: 'divider',
              '&:hover .cap-title': {color: 'primary.main'},
            }}
          >
            <Typography
              variant="h4"
              component="h3"
              className="cap-title"
              sx={{transition: 'color 160ms ease'}}
            >
              {item.title}
            </Typography>
            <Typography variant="body2" sx={{color: 'text.secondary', maxWidth: '46rem'}}>
              {item.body}
            </Typography>
          </Box>
        ))}
      </Box>
    </Section>
  )
}
