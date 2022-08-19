from __future__ import annotations
from typing import List, Tuple, Callable
from pyglet.graphics import OrderedGroup, Batch
from pyglet.text import Label
from game import resources
from extensions import GBASprite as Sprite
from screens.menu_item import MenuItem


class PointerMenuItem(MenuItem):
    def __init__(
        self,
        img,
        x: int,
        y: int,
        on_click: Callable,
        group: OrderedGroup,
        text: str,
    ):
        img.anchor_x = 0
        super().__init__(img, x, y, on_click, group, 5, 2)
        label_x = self.background_sprite.x + 20
        label_y = self.background_sprite.y
        self.label = Label(text, anchor_x="center", x=label_x, y=label_y)

    def draw(self):
        super().draw()
        self.label.draw()

    def set_batch(self, batch: Batch):
        super().set_batch(batch)
        self.label.batch = batch


class PointerMenu(Sprite):
    def __init__(
        self,
        group: OrderedGroup,
        option_group: OrderedGroup,
        screen_width: int,
        screen_height: int,
    ):
        super().__init__(resources.unit_menu, group=group)
        self.position = (
            screen_width - self.width - 25,
            screen_height - self.height - 25,
        )

        self.pointer_sprite = Sprite(resources.menu_hand, group=group)
        self.pointer_sprite.scale = 4
        self.max_x = self.x - self.pointer_sprite.width
        self.pointer_sprite.position = (self.max_x, self.y)
        self.moving_left = True

        self.options: List[PointerMenuItem] = []
        self.option_group = option_group
        self.selected_option = 0

    def set_batch(self, batch: Batch):
        self.batch = batch
        self.pointer_sprite.batch = batch
        for option in self.options:
            option.set_batch(batch)

    def move_pointer_to_selected(self):
        selected_sprite = self.options[self.selected_option].background_sprite
        self.pointer_sprite.y = selected_sprite.y
        print(self.selected_option)

    def move_pointer(self, direction: int):
        length = len(self.options)
        self.selected_option = (self.selected_option + direction + length) % length
        self.move_pointer_to_selected()

    def set_options(self, options: List[Tuple[str, Callable]]):
        actions = []
        for index, option in enumerate(options):
            text, action = option
            item = PointerMenuItem(
                resources.menu_option,
                self.x + 30,
                self.y + self.height - (index + 1) * resources.menu_option.height * 2,
                action,
                self.option_group,
                text,
            )
            actions.append(item)
        self.options = actions
        self.move_pointer_to_selected()

    def execute_option(self):
        self.options[self.selected_option].on_click()
        self.selected_option = 0

    def run_pointer_animation(self):
        p = self.pointer_sprite
        if self.moving_left:
            if p.x <= self.max_x - p.width // 2:
                self.moving_left = False
                return
            p.x -= 2
        else:
            if p.x >= self.max_x:
                self.moving_left = True
                return
            p.x += 2
