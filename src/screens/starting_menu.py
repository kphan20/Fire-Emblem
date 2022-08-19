from typing import Callable, List
from game import resources
from pyglet.graphics import OrderedGroup, Batch
from pyglet.window import key
from pyglet.text import Label
from pyglet.shapes import Rectangle

from .screen import ImageScreen
from .menu_item import MenuItem


class StartingMenuItem(MenuItem):
    def __init__(
        self,
        on_click: Callable,
        group: OrderedGroup,
        screen_width: int,
        screen_height: int,
        position: int,
        text: str,
    ):
        img = resources.menu_option
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        super().__init__(
            img,
            screen_width // 2,
            screen_height - position * img.height * 4,
            on_click,
            group,
            16,
            4,
        )

        label_x, label_y = self.background_sprite.position
        self.label = Label(
            text, anchor_x="center", anchor_y="center", x=label_x, y=label_y
        )

    def draw(self):
        super().draw()
        self.label.draw()

    def set_batch(self, batch: Batch):
        super().set_batch(batch)
        self.label.batch = batch


class StartingMenu(ImageScreen):
    def __init__(self, width, height):
        self.selector_group = OrderedGroup(0)
        self.foreground_group = OrderedGroup(1)
        super().__init__(resources.circle_animation, width, height)
        self.options: List[MenuItem] = [
            StartingMenuItem(
                self.initiate_battle_screen,
                self.foreground_group,
                width,
                height,
                1,
                "Battle Screen",
            ),
            StartingMenuItem(
                lambda x: print("Options"),
                self.foreground_group,
                width,
                height,
                2,
                "Options",
            ),
        ]
        self.selected_option = 0
        option_sprite = self.options[0].background_sprite
        self.selector = Rectangle(
            option_sprite.x,
            option_sprite.y,
            option_sprite.width,
            option_sprite.height,
            color=(255, 0, 0),
            group=self.selector_group,
        )
        self.selector.anchor_position = (
            self.selector.width // 2,
            self.selector.height // 2,
        )

        self.register_event_type("on_starting_screen_init")
        self.register_event_type("on_battle_screen_init")

    def on_key_press(self, symbol, modifiers):
        # selects option
        if symbol == key.E:
            # implement change screen wrapper function
            self.options[self.selected_option].on_click()
            return
        elif symbol == key.Q:
            self.initiate_starting_screen()
            return
        # scrolls up
        elif symbol == key.UP:
            length = len(self.options)
            self.selected_option = (self.selected_option - 1 + length) % length
        # scrolls down
        elif symbol == key.DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)

        self.selector.position = self.options[
            self.selected_option
        ].background_sprite.position

    def draw(self):
        super().draw()
        self.selector.draw()
        for option in self.options:
            option.draw()
