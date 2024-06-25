import param

from panel.pane.placeholder import Placeholder
from panel.widgets import IntInput


class TestPlaceholder:

    def test_update_object(self):
        placeholder = Placeholder("Idle")
        placeholder.object = "Running..."
        assert placeholder.object == "Running..."
        placeholder.object = "New"
        assert placeholder.object == "New"

    def test_enter_exit(self):
        placeholder = Placeholder("⏳ Idle")
        with placeholder:
            placeholder.object = "🏃 Running..."
            assert placeholder.object == "🏃 Running..."
            placeholder.object = "🚶 Walking..."
            assert placeholder.object == "🚶 Walking..."
        assert placeholder.object == "⏳ Idle"

    def test_param_ref(self):
        int_input = IntInput(name="IntInput", start=1, end=10, value=5)
        placeholder = Placeholder(int_input.param.value)
        assert isinstance(placeholder.object, param.Integer)
