import Box from '@mui/material/Box'
import Container from '@mui/material/Container'
import Link from '@mui/material/Link'
import Typography from '@mui/material/Typography'

import {Logo} from '../components/Logo'
import {footerColumns, GITHUB, social} from '../content/site'

export function Footer() {
  return (
    <Box
      component="footer"
      sx={{borderTop: '1px solid', borderColor: 'divider', pt: {xs: 6, md: 8}, pb: 5}}
    >
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: {xs: '1fr', sm: 'repeat(2, 1fr)', md: '1.4fr repeat(4, 1fr)'},
            columnGap: 4,
            rowGap: 5,
          }}
        >
          <Box>
            <Box
              sx={{
                display: 'inline-flex',
                color: 'primary.main',
                '--Logo-knockout': 'var(--mui-palette-background-default)',
              }}
            >
              <Logo size={24} title="Panel" />
            </Box>
            <Typography variant="body2" sx={{mt: 1.75, color: 'text.secondary', maxWidth: '22rem'}}>
              Panel is part of HoloViz, a set of Python tools for working with data.
            </Typography>
            <Box sx={{display: 'flex', gap: 2, mt: 2}}>
              {social.map((item) => (
                <Link key={item.label} href={item.href} variant="body2" sx={{color: 'text.secondary'}}>
                  {item.label}
                </Link>
              ))}
            </Box>
          </Box>
          {footerColumns.map((column) => (
            <Box key={column.heading}>
              <Typography sx={{fontSize: '0.875rem', fontWeight: 600, mb: 1.5}}>
                {column.heading}
              </Typography>
              <Box sx={{display: 'flex', flexDirection: 'column', gap: 1}}>
                {column.links.map((link) => (
                  <Link
                    key={link.label}
                    href={link.href}
                    variant="body2"
                    sx={{color: 'text.secondary', '&:hover': {color: 'text.primary'}}}
                  >
                    {link.label}
                  </Link>
                ))}
              </Box>
            </Box>
          ))}
        </Box>
        <Typography
          variant="caption"
          component="p"
          sx={{mt: {xs: 5, md: 7}, pt: 3, borderTop: '1px solid', borderColor: 'divider', color: 'text.secondary'}}
        >
          © HoloViz contributors, 2018 onward.{' '}
          <Link href={`${GITHUB}/blob/main/LICENSE.txt`} sx={{color: 'inherit', textDecoration: 'underline'}}>
            Licence
          </Link>
        </Typography>
      </Container>
    </Box>
  )
}
