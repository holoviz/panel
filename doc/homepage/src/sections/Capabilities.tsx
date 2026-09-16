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
      title="The parts that usually make you leave"
      lede="Streaming, custom front-end code, offline builds and auth are the points where a prototyping tool normally hands you back to a web framework. Each of these has a how-to guide behind it."
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
              px: {xs: 0, md: 2},
              mx: {xs: 0, md: -2},
              py: {xs: 2.5, md: 3},
              textDecoration: 'none',
              color: 'inherit',
              borderBottom: '1px solid',
              borderColor: 'divider',
              transition: 'background-color 160ms ease',
              '&:hover': {backgroundColor: 'action.hover'},
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
