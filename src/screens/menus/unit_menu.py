from pyglet.sprite import Sprite
from pyglet.graphics import Group, Batch
from game import resources


class UnitMenu(Sprite):
    def __init__(self, group: Group):
        super().__init__(resources.unit_menu, group=group)

    def set_batch(self, batch: Batch):
        self.batch = batch
