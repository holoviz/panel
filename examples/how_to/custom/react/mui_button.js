import Button from '@mui/material/Button?deps=react@18.2.0';

export function MuiButton({ model }) {
  const [label] = model.useState("label")
  const [variant] = model.useState("variant")
  return <Button variant={variant}>{label || 'Foo'}</Button>
}

export default { render: MuiButton }
