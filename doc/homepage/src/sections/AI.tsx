import Box from '@mui/material/Box'
import Link from '@mui/material/Link'
import Typography from '@mui/material/Typography'

import {CodeBlock} from '../components/CodeBlock'
import {Section, type Band} from '../components/Section'
import {ai} from '../content/site'
import {surfaces} from '../theme'

/**
 * The two sides of the app in two columns, and the copilot screenshot below at full width,
 * where the moved widgets and the chat are legible.
 */
export function AI({wash}: Band) {
  return (
    <Section id="ai" title={ai.title} lede={ai.lede} wash={wash}>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {xs: 'minmax(0, 1fr)', md: 'repeat(2, minmax(0, 1fr))'},
          columnGap: 5,
          rowGap: 6,
        }}
      >
        {ai.items.map((item) => (
          <Box key={item.id} data-ai={item.id} sx={{display: 'flex', flexDirection: 'column', gap: 1.5, minWidth: 0}}>
            <Typography variant="body2" sx={{color: 'text.secondary'}}>
              {item.step}
            </Typography>
            <Typography variant="h3" component="h3">
              {item.title}
            </Typography>
            <Typography variant="body2" sx={{color: 'text.secondary'}}>
              {item.body}
            </Typography>
            <CodeBlock
              source={item.code}
              wrap
              fontSize="0.8125rem"
              sx={{
                mt: 1,
                backgroundColor: surfaces.code,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                p: 2.25,
              }}
            />
            <Link href={item.link.href}>{item.link.label}</Link>
          </Box>
        ))}
      </Box>
      <Box component="figure" data-ai="screenshot" sx={{m: 0, mt: {xs: 5, md: 6}}}>
        <Box
          component="img"
          src={ai.screenshot.image}
          alt="Lumen's penguin copilot: a chat drawer beside a dashboard whose filters and axes it has just changed"
          width={1440}
          height={900}
          loading="lazy"
          decoding="async"
          sx={{
            display: 'block',
            width: '100%',
            height: 'auto',
            aspectRatio: '16 / 10',
            backgroundColor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
          }}
        />
        <Typography variant="caption" component="figcaption" sx={{display: 'block', mt: 1.25, color: 'text.secondary'}}>
          {ai.screenshot.caption}
        </Typography>
      </Box>
    </Section>
  )
}
