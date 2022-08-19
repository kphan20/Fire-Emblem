from pyglet.graphics import Batch, OrderedGroup
from pyglet.text import Label
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
        self.pointer.image.anchor_x = self.pointer.width // 2
        self.pointer.image.anchor_y = self.pointer.height // 2
        self.pointer.scale = 4
        self.current_unit_info.scale = 0.5
        self.target.scale = 0.5
        self.current_unit_label = Label(group=OrderedGroup(text_group.order + 1))
        self.target_label = Label(group=OrderedGroup(text_group.order + 1))

    def initialize_positions(self):
        self.target.position = (
            self.current_unit_info.x,
            self.current_unit_info.y - self.target.height - self.pointer.height + 15,
        )

        self.pointer.position = (
            self.target.x + self.target.width // 2,
            self.current_unit_info.y - self.pointer.height // 2 + 10,
        )
        self.current_unit_label.position = self.current_unit_info.position
        self.target_label.position = self.target.position

    def set_batch(self, batch: Batch):
        self.current_unit_info.batch = batch
        self.target.batch = batch
        self.pointer.batch = batch
        self.current_unit_label.batch = batch
        self.target_label.batch = batch

    def update_current_unit(self, character: Character):
        pass

    def update_target(self, character: Character):
        pass
