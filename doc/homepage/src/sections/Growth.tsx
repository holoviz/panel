import Box from '@mui/material/Box'
import Link from '@mui/material/Link'
import Typography from '@mui/material/Typography'

import {CodeBlock} from '../components/CodeBlock'
import {Section, type Band} from '../components/Section'
import {growth} from '../content/site'
import {surfaces} from '../theme'

/**
 * Three sizes of the same app, left to right. Not numbered: the reader picks the one that
 * matches what they are building rather than walking through all three, so a numbered
 * treatment would promise a sequence that is not there. Each snippet is a little taller than
 * the last, which does the growing without a label saying so.
 */
export function Growth({wash}: Band) {
  return (
    <Section id="growth" title={growth.title} lede={growth.lede} wash={wash}>
      <Box
        sx={{
          display: 'grid',
          // minmax(0, …) rather than 1fr: a `pre` reports its longest line as min-content,
          // which would push the track wider than the container instead of scrolling.
          gridTemplateColumns: {xs: 'minmax(0, 1fr)', md: 'repeat(3, minmax(0, 1fr))'},
          columnGap: {md: 4},
          rowGap: 5,
          alignItems: 'start',
        }}
      >
        {growth.stages.map((stage) => (
          <Box key={stage.title} sx={{display: 'flex', flexDirection: 'column', gap: 1.5}}>
            <Typography variant="h3" component="h3" sx={{fontSize: '1.25rem'}}>
              {stage.title}
            </Typography>
            <Typography variant="body2" sx={{color: 'text.secondary'}}>
              {stage.body}
            </Typography>
            <CodeBlock
              source={stage.code}
              fontSize={{xs: '0.8125rem', md: '0.8125rem'}}
              sx={{
                mt: 0.5,
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
      <Link href={growth.link.href} sx={{display: 'inline-block', mt: 4.5}}>
        {growth.link.label}
      </Link>
    </Section>
  )
}
