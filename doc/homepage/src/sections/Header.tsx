import DarkModeIcon from '@mui/icons-material/DarkModeOutlined'
import GitHubIcon from '@mui/icons-material/GitHub'
import LightModeIcon from '@mui/icons-material/LightModeOutlined'
import MenuIcon from '@mui/icons-material/Menu'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import Container from '@mui/material/Container'
import Divider from '@mui/material/Divider'
import Drawer from '@mui/material/Drawer'
import IconButton from '@mui/material/IconButton'
import Link from '@mui/material/Link'
import {useColorScheme} from '@mui/material/styles'
import Typography from '@mui/material/Typography'
import {useState} from 'react'

import {Logo} from '../components/Logo'
import {DOCS, GITHUB, nav} from '../content/site'

export function Header() {
  const [open, setOpen] = useState(false)

  return (
    <Box
      component="header"
      sx={{
        position: 'sticky',
        top: 0,
        zIndex: 10,
        borderBottom: '1px solid',
        borderColor: 'divider',
        backgroundColor: 'background.default',
      }}
    >
      <Container
        maxWidth="lg"
        sx={{display: 'flex', alignItems: 'center', gap: {xs: 1, md: 3}, height: 62}}
      >
        <Link
          href="/"
          sx={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 1.25,
            color: 'primary.main',
            '--Logo-knockout': 'var(--mui-palette-background-default)',
            flexShrink: 0,
          }}
        >
          <Logo size={22} title="Panel" />
          <Typography
            component="span"
            sx={{fontSize: '1.1875rem', fontWeight: 650, letterSpacing: '-0.02em', color: 'text.primary'}}
          >
            Panel
          </Typography>
        </Link>

        <Box
          component="nav"
          aria-label="Documentation"
          sx={{display: {xs: 'none', md: 'flex'}, gap: 2.75, ml: 2}}
        >
          {nav.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              sx={{fontSize: '0.9375rem', color: 'text.secondary', '&:hover': {color: 'text.primary'}}}
            >
              {item.label}
            </Link>
          ))}
        </Box>

        <Box sx={{flex: 1}} />

        <SchemeToggle />
        <IconButton
          href={GITHUB}
          aria-label="Panel on GitHub"
          size="small"
          sx={{color: 'text.secondary'}}
        >
          <GitHubIcon fontSize="small" />
        </IconButton>
        <Button
          variant="contained"
          size="small"
          href={`${DOCS}/getting_started/index.html`}
          sx={{display: {xs: 'none', sm: 'inline-flex'}}}
        >
          Get started
        </Button>
        <IconButton
          onClick={() => setOpen(true)}
          aria-label="Open menu"
          size="small"
          sx={{display: {md: 'none'}, color: 'text.secondary'}}
        >
          <MenuIcon />
        </IconButton>
      </Container>

      <Drawer anchor="right" open={open} onClose={() => setOpen(false)}>
        <Box sx={{width: 260, py: 2}} onClick={() => setOpen(false)}>
          {nav.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              sx={{display: 'block', px: 3, py: 1.5, color: 'text.primary'}}
            >
              {item.label}
            </Link>
          ))}
          <Divider sx={{my: 1.5}} />
          <Link href={GITHUB} sx={{display: 'block', px: 3, py: 1.5, color: 'text.secondary'}}>
            GitHub
          </Link>
        </Box>
      </Drawer>
    </Box>
  )
}

/**
 * The icon is chosen in CSS rather than from `mode`, because `mode` is unknown while the
 * page is prerendered and reading it here would make the first paint disagree with the
 * markup for anyone whose stored preference is dark.
 */
function SchemeToggle() {
  const {mode, setMode} = useColorScheme()
  const next = mode === 'dark' ? 'light' : 'dark'

  return (
    <IconButton
      onClick={() => setMode(next)}
      aria-label="Switch colour scheme"
      size="small"
      sx={{color: 'text.secondary'}}
    >
      <Box sx={{display: 'inline-flex', 'html[data-color-scheme="dark"] &': {display: 'none'}}}>
        <DarkModeIcon fontSize="small" />
      </Box>
      <Box sx={{display: 'none', 'html[data-color-scheme="dark"] &': {display: 'inline-flex'}}}>
        <LightModeIcon fontSize="small" />
      </Box>
    </IconButton>
  )
}
