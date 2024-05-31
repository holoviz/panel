import Box from '@mui/material/Box?deps=react@18.2.0';
import Slider from '@mui/material/Slider?deps=react@18.2.0';

function DiscreteSlider({ state }) {
  const [value, setValue] = state.value
  const [marks, _] = state.marks
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

export default { render: DiscreteSlider }
