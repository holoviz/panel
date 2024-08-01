import confetti from "canvas-confetti";
import Button from '@mui/material/Button?deps=react@18.2.0&no-bundle';

function App(props) {
  const [color, setColor] = props.state.color
  const [text, setText ] = props.state.text
  const [celebrate, setCelebrate] = props.state.celebrate

  React.useEffect(() => confetti(), [celebrate])
  const style = {color: color}
  return (
    <>
      <h1 style={style}>{text}</h1>
      {props.child}
      <input
        value={text}
        onChange={e => setText(e.target.value)}
      />
      <Button variant="contained">Hello world</Button>
      <button onClick={() => confetti()}>Click me!</button>
    </>
  );
}

export function render({ state, el, children, view }) {
  return (
      <App state={state} child={children.child}/>
  )
}
