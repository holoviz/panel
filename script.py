import pandas as pd
from panel.widgets import Tabulator

value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
tabulator = Tabulator(value=value)
patch_value = pd.Series({"index": 1, "x": 4, "y": "d"})
tabulator.patch(patch_value)
print(tabulator.value.to_dict("list"))