import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'

import {CodeBlock} from '../components/CodeBlock'
import {Section, type Band} from '../components/Section'
import {paths} from '../content/site'
import {monoFamily} from '../theme'

/**
 * The only numbered section on the page, because notebook to script to production is the
 * one thing here that really is a sequence.
 */
export function Paths({wash}: Band) {
  return (
    <Section
      id="paths"
      title="The same file, from first cell to deploy"
      lede="Panel does not have a notebook mode and a production mode. What changes between them is how you run it."
      wash={wash}
    >
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {xs: 'minmax(0, 1fr)', md: 'repeat(3, minmax(0, 1fr))'},
          columnGap: {md: 5},
          rowGap: 5,
        }}
      >
        {paths.map((path, i) => (
          <Box
            key={path.step}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              gap: 1.5,
              pl: {md: i === 0 ? 0 : 5},
              borderLeft: {xs: 0, md: i === 0 ? 0 : '1px solid'},
              borderColor: 'divider',
            }}
          >
            <Box sx={{display: 'flex', alignItems: 'center', gap: 1.5}}>
              <Box
                component="span"
                sx={{
                  fontFamily: monoFamily,
                  fontSize: '0.8125rem',
                  fontWeight: 500,
                  width: 24,
                  height: 24,
                  borderRadius: '50%',
                  bgcolor: 'primary.main',
                  color: 'primary.contrastText',
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {i + 1}
              </Box>
              <Typography variant="body2" sx={{color: 'text.secondary'}}>
                {path.step}
              </Typography>
            </Box>
            <Typography variant="h3" component="h3">
              {path.title}
            </Typography>
            <Typography variant="body2" sx={{color: 'text.secondary'}}>
              {path.body}
            </Typography>
            <CodeBlock
              source={path.code}
              sx={{
                mt: 'auto',
                pt: 2,
                borderTop: '1px solid',
                borderColor: 'divider',
              }}
            />
          </Box>
        ))}
      </Box>
    </Section>
  )
}
