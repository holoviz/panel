import pytest

from panel.widgets.icon import ToggleIcon


class TestToggleIcon:

    def test_init(self):
        icon = ToggleIcon()
        assert icon.icon_name == "heart"
        assert icon.active_icon_name == ""
        assert not icon.value

    def test_custom_values(self):
        icon = ToggleIcon(icon_name="thumb-down", active_icon_name="thumb-up", value=True)
        assert icon.icon_name == "thumb-down"
        assert icon.active_icon_name == "thumb-up"
        assert icon.value

    def test_empty_icon_name(self):
        with pytest.raises(ValueError, match="The icon_name parameter must not "):
            ToggleIcon(icon_name="")
