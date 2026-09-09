import Box from '@mui/material/Box'
import type {SxProps, Theme} from '@mui/material/styles'
import {Fragment} from 'react'

import {monoFamily} from '../theme'

/**
 * Python highlighting, by hand.
 *
 * A real highlighter (Prism, Shiki, highlight.js) is 40kB to 300kB for the six snippets on
 * this page, and every off-the-shelf theme brings its own palette, which would put five
 * colours the logo does not contain into the middle of the page. This covers the subset
 * Python snippets actually use, in the page's own three colours.
 */

const KEYWORDS = new Set([
  'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del',
  'elif', 'else', 'except', 'False', 'finally', 'for', 'from', 'global', 'if', 'import',
  'in', 'is', 'lambda', 'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True',
  'try', 'while', 'with', 'yield',
])

type Kind = 'plain' | 'keyword' | 'string' | 'comment' | 'number' | 'call'

const TOKEN = /("""[\s\S]*?"""|'''[\s\S]*?'''|"[^"\n]*"|'[^'\n]*'|#[^\n]*|\b\d[\d_.]*\b|[A-Za-z_][A-Za-z0-9_]*|\s+|[^\sA-Za-z0-9_])/g

function classify(token: string, next: string): Kind {
  const head = token[0]
  if (head === '#') return 'comment'
  if (head === '"' || head === "'") return 'string'
  if (head >= '0' && head <= '9') return 'number'
  if (KEYWORDS.has(token)) return 'keyword'
  if (/^[A-Za-z_]/.test(token) && next === '(') return 'call'
  return 'plain'
}

function tokenize(source: string) {
  const raw = source.match(TOKEN) ?? [source]
  const out: {text: string; kind: Kind}[] = []
  for (let i = 0; i < raw.length; i++) {
    // Look past whitespace so `serve (x)` still reads as a call.
    let j = i + 1
    while (j < raw.length && /^\s+$/.test(raw[j])) j++
    const kind = classify(raw[i], raw[j] ?? '')
    const last = out[out.length - 1]
    if (last && last.kind === kind) last.text += raw[i]
    else out.push({text: raw[i], kind})
  }
  return out
}

const COLOURS: Record<Kind, string | undefined> = {
  plain: undefined,
  keyword: 'var(--code-keyword)',
  string: 'var(--code-string)',
  comment: 'var(--code-comment)',
  number: 'var(--code-string)',
  call: 'var(--code-call)',
}

export function Code({source}: {source: string}) {
  return (
    <>
      {tokenize(source).map((t, i) => (
        <Fragment key={i}>
          {t.kind === 'plain' ? t.text : <Box component="span" sx={{color: COLOURS[t.kind]}}>{t.text}</Box>}
        </Fragment>
      ))}
    </>
  )
}

export function CodeBlock({
  source,
  sx,
  fontSize = '0.875rem',
}: {
  source: string
  sx?: SxProps<Theme>
  fontSize?: string | Record<string, string>
}) {
  return (
    <Box
      component="pre"
      sx={[
        {
          m: 0,
          fontFamily: monoFamily,
          fontSize,
          lineHeight: 1.75,
          color: 'text.primary',
          overflowX: 'auto',
          tabSize: 4,
        },
        ...(Array.isArray(sx) ? sx : [sx]),
      ]}
    >
      <code>
        <Code source={source} />
      </code>
    </Box>
  )
}
