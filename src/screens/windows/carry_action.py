from pyglet.graphics import Batch, OrderedGroup
from extensions import GBASprite as Sprite
from game import resources
from game.unit import Character


class CarryActionWindow:
    def __init__(
        self,
        group: OrderedGroup,
        text_group: OrderedGroup,
    ) -> None:
        self.current_unit_info = Sprite(resources.carry_box, group=group)
        self.target = Sprite(resources.carry_box, group=group)
        self.pointer = Sprite(resources.menu_hand, group=text_group)
        self.current_unit_info.scale = 0.5
        self.target.scale = 0.5

    def initialize_positions(self):
        self.target.position = (
            self.current_unit_info.x,
            self.current_unit_info.y - self.target.height - 30,
        )

        self.pointer.position = (
            self.target.x + self.target.width // 2,
            self.current_unit_info.y - self.pointer.height - 15,
        )

    def set_batch(self, batch: Batch):
        self.current_unit_info.batch = batch
        self.target.batch = batch
        self.pointer.batch = batch

    def update_target(self, character: Character):
        pass
