import Box from '@mui/material/Box?deps=react@18.2.0';
import Slider from '@mui/material/Slider?deps=react@18.2.0';

export default function DiscreteSlider(props) {
  const [value, setValue] = props.state.value
  const [marks, _] = props.state.marks
  return (
    <Box sx={{ width: 300 }}>
      <Slider
        aria-label="Restricted values"
        defaultValue={value}
	marks={marks}
	step={null}
	valueLabelDisplay="auto"
      />
    </Box>
  );
}

export function render({ state }) {
  return <DiscreteSlider state={state}></App>
}
