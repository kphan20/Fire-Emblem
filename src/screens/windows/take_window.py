from pyglet.graphics import OrderedGroup
from game.unit import Character
from .carry_action import CarryActionWindow


class TakeWindow(CarryActionWindow):
    def __init__(
        self, group: OrderedGroup, text_group: OrderedGroup, screen_height: int
    ) -> None:
        super().__init__(group, text_group)

        self.current_unit_info.position = (
            15,
            screen_height - self.current_unit_info.height - 15,
        )
        self.initialize_positions()
        self.pointer.rotation = 90

    def update_target(self, character: Character):
        pass
