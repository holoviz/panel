import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Typography from '@mui/material/Typography'

import {Section, type Band} from '../components/Section'
import {adoption, DOCS, GITHUB} from '../content/site'

export function Adoption({wash}: Band) {
  return (
    <Section id="community" wash={wash}>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {xs: '1fr', md: '1fr 1fr'},
          columnGap: {md: 8},
          rowGap: 4,
        }}
      >
        <Box>
          <Typography variant="h2" component="h2" sx={{fontSize: {xs: '1.625rem', md: '2rem'}}}>
            {adoption.title}
          </Typography>
          <Typography variant="body1" sx={{mt: 2, color: 'text.secondary', maxWidth: '34rem'}}>
            {adoption.body}
          </Typography>
          <Box sx={{display: 'flex', flexWrap: 'wrap', gap: 1.5, mt: 3.5}}>
            <Button variant="contained" size="large" href={`${DOCS}/getting_started/index.html`}>
              Get started
            </Button>
            <Button
              size="large"
              variant="outlined"
              href={GITHUB}
              sx={{color: 'text.primary', borderColor: 'divider'}}
            >
              Read the source
            </Button>
          </Box>
        </Box>
        <Box
          component="dl"
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '1px',
            backgroundColor: 'divider',
            borderBlock: '1px solid',
            borderColor: 'divider',
            alignSelf: 'start',
            m: 0,
          }}
        >
          {adoption.stats.map((stat) => (
            <Box
              key={stat.label}
              sx={{
                backgroundColor: 'background.default',
                px: 2.5,
                py: 2.5,
                // Term before description in the markup, value above label on the screen.
                display: 'flex',
                flexDirection: 'column-reverse',
              }}
            >
              <Box component="dt" sx={{mt: 0.5, fontSize: '0.8125rem', color: 'text.secondary'}}>
                {stat.label}
              </Box>
              <Box component="dd" sx={{m: 0, fontSize: '1.625rem', fontWeight: 650, letterSpacing: '-0.02em'}}>
                {stat.value}
              </Box>
            </Box>
          ))}
        </Box>
      </Box>
    </Section>
  )
}
