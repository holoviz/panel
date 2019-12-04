import panel as pn
import numpy as np

axes = dict(
    origin = [10, 0, -5],
    xticks = np.linspace(-10,10,5),
    yticks = np.linspace(0,12,11),
    zticks = np.linspace(-5,5,5),
)
dragon = pn.pane.VTK('https://raw.githubusercontent.com/Kitware/vtk-js/master/Data/StanfordDragon.vtkjs',
                     sizing_mode='stretch_width', height=400, enable_keybindings=True, orientation_widget=True,
                     serialize_on_instantiation=True, axes=axes)
dragon.show()
