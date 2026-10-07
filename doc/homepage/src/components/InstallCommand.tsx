import CheckIcon from '@mui/icons-material/Check'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import ButtonBase from '@mui/material/ButtonBase'
import {useEffect, useRef, useState} from 'react'

import {monoFamily, surfaces} from '../theme'

const MANAGERS = ['pip', 'conda'] as const
type Manager = (typeof MANAGERS)[number]

export function InstallCommand({commands}: {commands: Record<Manager, string>}) {
  const [manager, setManager] = useState<Manager>('pip')
  const [copied, setCopied] = useState(false)
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined)

  useEffect(() => () => clearTimeout(timer.current), [])

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(commands[manager])
      setCopied(true)
      clearTimeout(timer.current)
      timer.current = setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard access can be refused; the command is selectable either way.
    }
  }

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        bgcolor: surfaces.code,
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 1.5,
        pl: 1,
        pr: 0.5,
        py: 0.5,
        gap: 1,
        minWidth: 0,
      }}
    >
      <Box sx={{display: 'flex', gap: 0.25, flexShrink: 0}}>
        {MANAGERS.map((m) => (
          <ButtonBase
            key={m}
            onClick={() => {
              setManager(m)
              setCopied(false)
            }}
            aria-pressed={manager === m}
            sx={{
              px: 1,
              py: 0.5,
              borderRadius: 1,
              fontFamily: monoFamily,
              fontSize: '0.8125rem',
              color: manager === m ? 'primary.contrastText' : 'text.secondary',
              bgcolor: manager === m ? 'primary.main' : 'transparent',
            }}
          >
            {m}
          </ButtonBase>
        ))}
      </Box>
      <Box
        component="code"
        sx={{
          fontFamily: monoFamily,
          fontSize: {xs: '0.8125rem', sm: '0.875rem'},
          whiteSpace: 'nowrap',
          overflowX: 'auto',
          flex: 1,
          minWidth: 0,
          py: 0.5,
        }}
      >
        {commands[manager]}
      </Box>
      <Button
        onClick={copy}
        size="small"
        startIcon={copied ? <CheckIcon fontSize="small" /> : <ContentCopyIcon fontSize="small" />}
        sx={{flexShrink: 0, color: 'text.secondary', px: 1.25}}
      >
        {copied ? 'Copied' : 'Copy'}
      </Button>
    </Box>
  )
}
