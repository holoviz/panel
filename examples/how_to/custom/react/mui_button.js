import Button from '@mui/material/Button?deps=react@18.2.0';

export function MuiButton({ state }) {
  const [label, _] = state.label
  const [variant, __] = state.variant
  return <Button variant={variant}>{label || 'Foo'}</Button>
}

export default { render: MuiButton }
