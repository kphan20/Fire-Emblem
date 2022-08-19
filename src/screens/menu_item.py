from typing import Callable
from pyglet.graphics import OrderedGroup, Batch
from extensions import GBASprite as Sprite


class MenuItem:
    def __init__(
        self,
        img,
        x: int,
        y: int,
        on_click: Callable,
        group: OrderedGroup,
        scale_x: int = 1,
        scale_y: int = 1,
    ):
        self.background_sprite = Sprite(img, group=group, x=x, y=y)
        self.background_sprite.scale_x = scale_x
        self.background_sprite.scale_y = scale_y
        self.on_click = on_click

    def draw(self):
        self.background_sprite.draw()

    def set_batch(self, batch: Batch):
        self.background_sprite.batch = batch
