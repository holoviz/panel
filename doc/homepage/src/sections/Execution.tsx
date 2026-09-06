import Box from '@mui/material/Box'
import Link from '@mui/material/Link'
import Typography from '@mui/material/Typography'

import {Section, type Band} from '../components/Section'
import {execution} from '../content/site'
import {monoFamily} from '../theme'

/**
 * The same five-block app, traced twice, after one widget moves.
 *
 * A filled block ran again and an outlined one did not, which is the whole argument: the
 * left column lights up completely for a change that could only have affected two blocks.
 * Both columns list the same blocks in the same order, so the only difference between them
 * is the fill, and each block says which it is rather than deferring to a legend.
 */
export function Execution({wash}: Band) {
  return (
    <Section id="execution" title={execution.title} lede={execution.lede} wash={wash}>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {xs: '1fr', md: 'repeat(2, 1fr)'},
          gap: {xs: 3, md: 4},
          alignItems: 'start',
        }}
      >
        {execution.traces.map((trace) => (
          <Box
            key={trace.id}
            data-trace={trace.id}
            sx={{
              backgroundColor: 'background.paper',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 2,
              p: {xs: 2.5, md: 3},
            }}
          >
            <Typography component="h3" sx={{fontSize: '1rem', fontWeight: 600}}>
              {trace.label}
            </Typography>
            <Box
              sx={{
                mt: 2,
                mb: 1.5,
                pb: 1.5,
                borderBottom: '1px dashed',
                borderColor: 'divider',
                fontFamily: monoFamily,
                fontSize: '0.8125rem',
                color: 'text.secondary',
              }}
            >
              window = 30 → 45
            </Box>
            <Box sx={{display: 'flex', flexDirection: 'column', gap: 1}}>
              {execution.blocks.map((block, i) => {
                const runs = trace.runs.includes(i)
                return (
                  <Box
                    key={block}
                    data-block=""
                    data-runs={runs || undefined}
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      gap: 2,
                      px: 1.75,
                      py: 1.25,
                      borderRadius: 1,
                      fontSize: '0.875rem',
                      border: '1px solid',
                      ...(runs
                        ? {
                            backgroundColor: 'primary.main',
                            borderColor: 'primary.main',
                            color: 'primary.contrastText',
                            fontWeight: 550,
                          }
                        : {
                            borderStyle: 'dashed',
                            borderColor: 'divider',
                            color: 'text.secondary',
                          }),
                    }}
                  >
                    <Box component="span" sx={{fontFamily: monoFamily}}>
                      {block}
                    </Box>
                    <Box component="span" sx={{fontSize: '0.75rem', opacity: runs ? 0.8 : 1}}>
                      {runs ? 'runs again' : 'untouched'}
                    </Box>
                  </Box>
                )
              })}
            </Box>
            <Typography variant="body2" sx={{mt: 2, color: 'text.secondary'}}>
              {trace.note}
            </Typography>
          </Box>
        ))}
      </Box>
      <Link href={execution.link.href} sx={{display: 'inline-block', mt: 4}}>
        {execution.link.label}
      </Link>
    </Section>
  )
}
