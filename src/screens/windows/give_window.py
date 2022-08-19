from pyglet.graphics import OrderedGroup
from game.unit import Character
from .carry_action import CarryActionWindow


class GiveWindow(CarryActionWindow):
    def __init__(
        self,
        group: OrderedGroup,
        text_group: OrderedGroup,
        screen_width: int,
        screen_height: int,
    ) -> None:
        super().__init__(group, text_group)

        self.current_unit_info.position = (
            screen_width - self.current_unit_info.width - 15,
            screen_height - self.current_unit_info.height - 15,
        )
        self.initialize_positions()
        self.pointer.rotation = 90

    def update_current_unit(self, character: Character):
        self.current_unit_label.text = str(character.carried_unit.stats.con)

    def update_target(self, character: Character):
        self.target_label.text = str(character.calc_aid())
