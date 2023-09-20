import param

import panel as pn


class RoomPage(param.Parameterized):
    fan_speed = param.Number(default=1, bounds=(0, 1))
    lights_on = param.Boolean(default=False)

    def panel(self):
        return pn.Param(self, show_name=False)

    def _sync(self):
        pn.state.location.sync(self)

    def _unsync(self):
        pn.state.location.unsync(self)


class ControlCenter(param.Parameterized):
    room = param.Selector(objects=["Engine Room", "Office Room"])

    def __init__(self, **params):
        super().__init__(**params)
        self._room_pages = {
            "Engine Room": RoomPage(fan_speed=1, lights_on=False),
            "Office Room": RoomPage(fan_speed=0.5, lights_on=True),
        }
        self._last_page = None

        sidebar = pn.Column(self.param.room)
        self.main = pn.Column()
        self.template = pn.template.FastListTemplate(
            title="Control Center",
            sidebar=[sidebar],
            main=[self.main],
        )

        self.param.trigger("room")

    @param.depends("room", watch=True)
    def _update_page(self):
        if self._last_page is not None:
            self._last_page._unsync()

        room_page = self._room_pages[self.room]
        room_page._sync()
        self.main.objects = [room_page.panel()]

        self._last_page = room_page

    def panel(self):
        return self.template


control_center = ControlCenter()
control_center.panel().servable()
