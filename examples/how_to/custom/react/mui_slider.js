import Box from '@mui/material/Box?deps=react@18.2.0';
import Slider from '@mui/material/Slider?deps=react@18.2.0';

function DiscreteSlider({ model }) {
  const [value, setValue] = model.useState("value")
  const [marks] = model.useState("marks")
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
