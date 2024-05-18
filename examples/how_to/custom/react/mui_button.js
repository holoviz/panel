import Button from '@mui/material/Button?deps=react@18.2.0';

function App(props) {
  const [label, _] = props.state.label
  const [variant, __] = props.state.variant
  return (
    <>
      <Button variant={variant}>{label || 'Foo'}</Button>
    </>
  )
}

export function render({ state }) {
  return <App state={state}></App>
}
