import pytest

from panel.widgets.icon import ToggleIcon


class TestToggleIcon:

    def test_init(self):
        icon = ToggleIcon()
        assert icon.icon == "heart"
        assert icon.active_icon == ""
        assert not icon.value

    def test_custom_values(self):
        icon = ToggleIcon(icon="thumb-down", active_icon="thumb-up", value=True)
        assert icon.icon == "thumb-down"
        assert icon.active_icon == "thumb-up"
        assert icon.value

    def test_empty_icon(self):
        with pytest.raises(ValueError, match="The icon parameter must not "):
            ToggleIcon(icon="")

    def test_icon_svg_empty_active_icon(self):
        with pytest.raises(ValueError, match="The active_icon parameter must not "):
            ToggleIcon(icon="<svg></svg>")
