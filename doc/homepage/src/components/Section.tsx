import Box from '@mui/material/Box'
import Container from '@mui/material/Container'
import type {SxProps, Theme} from '@mui/material/styles'
import Typography from '@mui/material/Typography'
import type {ReactNode} from 'react'

import {surfaces} from '../theme'

/**
 * Whether a section sits on a washed band. Decided by the page order in App.tsx rather than
 * by the section itself, so the alternation is legible in one place.
 */
export type Band = {wash?: boolean}

/**
 * Sections alternate between the white page and a washed band. A band carries its own edges
 * and a plain section is separated by a hairline, so consecutive sections never need both.
 */
export function Section({
  id,
  title,
  lede,
  children,
  rule = true,
  wash = false,
  sx,
}: {
  id?: string
  title?: string
  lede?: string
  children: ReactNode
  rule?: boolean
  wash?: boolean
  sx?: SxProps<Theme>
}) {
  return (
    <Box
      component="section"
      id={id}
      sx={[
        {
          backgroundColor: wash ? surfaces.wash : 'transparent',
          borderTop: wash || rule ? '1px solid' : 0,
          borderBottom: wash ? '1px solid' : 0,
          borderColor: 'divider',
          py: {xs: 7, md: 11},
        },
        ...(Array.isArray(sx) ? sx : [sx]),
      ]}
    >
      <Container maxWidth="lg">
        {title && (
          <Box sx={{maxWidth: '46rem', mb: {xs: 4.5, md: 6.5}}}>
            <Typography variant="h2" component="h2">
              {title}
            </Typography>
            {lede && (
              <Typography variant="body1" sx={{mt: 2, color: 'text.secondary', maxWidth: '38rem'}}>
                {lede}
              </Typography>
            )}
          </Box>
        )}
        {children}
      </Container>
    </Box>
  )
}
