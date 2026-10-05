import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography'

import {CodeBlock} from '../components/CodeBlock'
import {Prose} from '../components/Prose'
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
      title="From development to deployment"
      lede="Work in a notebook or your preferred editor, then deploy the same app for others to use."
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
            key={path.title}
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
              <Typography variant="h3" component="h3">
                {path.title}
              </Typography>
            </Box>
            <Typography variant="body2" sx={{color: 'text.secondary'}}>
              <Prose text={path.body} />
            </Typography>
            {/* The label sits above the rule so the three rules stay level across columns. */}
            <Box sx={{mt: 'auto'}}>
              {'codeLabel' in path && (
                <Typography variant="body2" sx={{color: 'text.secondary', mb: 1}}>
                  {path.codeLabel}
                </Typography>
              )}
              <CodeBlock source={path.code} sx={{pt: 2, borderTop: '1px solid', borderColor: 'divider'}} />
            </Box>
          </Box>
        ))}
      </Box>
    </Section>
  )
}
