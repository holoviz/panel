import Box from '@mui/material/Box'
import Link from '@mui/material/Link'
import Typography from '@mui/material/Typography'

import {CodeBlock} from '../components/CodeBlock'
import {Prose} from '../components/Prose'
import {Section, type Band} from '../components/Section'
import {growth} from '../content/site'
import {surfaces} from '../theme'

/**
 * Three sizes of the same app, one row each, prose beside code. Not numbered: the reader
 * picks the one that matches what they are building rather than walking through all three.
 * Each snippet is a little taller than the last, which does the growing without a label
 * saying so. Rows rather than columns because a third of the container is too narrow for a
 * class body to fit without scrolling.
 */
export function Growth({wash}: Band) {
  return (
    <Section id="growth" title={growth.title} lede={growth.lede} wash={wash}>
      <Box sx={{display: 'flex', flexDirection: 'column', gap: {xs: 5, md: 4}}}>
        {growth.stages.map((stage) => (
          <Box
            key={stage.title}
            data-growth-stage=""
            sx={{
              display: 'grid',
              // minmax(0, …) rather than 1fr: a `pre` reports its longest line as min-content,
              // which would push the track wider than the container instead of wrapping.
              gridTemplateColumns: {xs: 'minmax(0, 1fr)', md: '22rem minmax(0, 1fr)'},
              columnGap: 5,
              rowGap: 1.5,
              alignItems: 'start',
            }}
          >
            <Box sx={{display: 'flex', flexDirection: 'column', gap: 1.5}}>
              <Typography variant="h3" component="h3" sx={{fontSize: '1.25rem'}}>
                {stage.title}
              </Typography>
              <Typography variant="body2" sx={{color: 'text.secondary'}}>
                <Prose text={stage.body} />
              </Typography>
            </Box>
            <CodeBlock
              source={stage.code}
              wrap
              fontSize={{xs: '0.8125rem', md: '0.875rem'}}
              sx={{
                mt: {xs: 0.5, md: 0},
                backgroundColor: surfaces.code,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                p: 2.25,
              }}
            />
          </Box>
        ))}
      </Box>
      <Typography variant="body1" data-growth-ceiling="" sx={{mt: {xs: 5, md: 6}, color: 'text.secondary', maxWidth: '46rem'}}>
        {growth.ceiling}
      </Typography>
      <Link href={growth.link.href} sx={{display: 'block', width: 'fit-content', mt: 3}}>
        {growth.link.label}
      </Link>
    </Section>
  )
}
