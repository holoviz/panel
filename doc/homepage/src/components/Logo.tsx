/**
 * Panel's logo mark, redrawn as inline SVG so it takes its colour from the surrounding
 * text and needs no light/dark asset pair.
 *
 * The mark is two rounded panes, sliders on the left and a curve on the right, and it is
 * the source of this page's whole layout language.
 */
export function Logo({size = 26, title}: {size?: number; title?: string}) {
  return (
    <svg
      viewBox="0 0 512 240"
      height={size}
      width={(size * 512) / 240}
      role={title ? 'img' : 'presentation'}
      aria-label={title}
      aria-hidden={title ? undefined : true}
      focusable="false"
    >
      <rect x="0" y="0" width="240" height="240" rx="30" fill="currentColor" />
      <g fill="var(--Logo-knockout, #eeeeee)">
        <rect x="36" y="52" width="168" height="16" rx="8" />
        <circle cx="82" cy="60" r="21" />
        <rect x="36" y="112" width="168" height="16" rx="8" />
        <circle cx="158" cy="120" r="21" />
        <rect x="36" y="172" width="168" height="16" rx="8" />
        <circle cx="82" cy="180" r="21" />
      </g>
      <rect x="272" y="0" width="240" height="240" rx="30" fill="currentColor" />
      <path
        d="M300 186 L312 152 L322 178 L332 132 L344 148 L356 96 L366 54 L376 88 L386 62 L396 118 L406 100 L416 140 L426 116 L436 150 L448 128 L460 172 L472 150 L484 168"
        fill="none"
        stroke="var(--Logo-knockout, #eeeeee)"
        strokeWidth="20"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
