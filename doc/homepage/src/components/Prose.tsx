import Box from '@mui/material/Box'

import {monoFamily} from '../theme'

/** Renders `backticked` spans of a copy string as inline code, so site.ts can stay plain strings. */
export function Prose({text}: {text: string}) {
  return (
    <>
      {text.split('`').map((part, i) =>
        i % 2 ? (
          <Box key={i} component="code" sx={{fontFamily: monoFamily, fontSize: '0.9em'}}>
            {part}
          </Box>
        ) : (
          part
        ),
      )}
    </>
  )
}
