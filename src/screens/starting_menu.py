from typing import List
from game import resources
from pyglet.graphics import OrderedGroup
from pyglet.window import key
from pyglet.text import Label
from pyglet.shapes import Rectangle

from .screen import ImageScreen
from extensions import GBASprite as Sprite


class MenuItem:
    def __init__(self, screen_width, screen_height, position, on_click, group, text):
        img = resources.menu_option
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        self.background_sprite = Sprite(resources.menu_option, group=group)
        self.background_sprite.scale_x = 16
        self.background_sprite.scale_y = 4
        self.background_sprite.x = screen_width // 2
        self.background_sprite.y = (
            screen_height - position * self.background_sprite.height
        )
        self.on_click = on_click
        label_x, label_y = self.background_sprite.position
        self.label = Label(
            text, anchor_x="center", anchor_y="center", x=label_x, y=label_y
        )

    def draw(self):
        self.background_sprite.draw()
        self.label.draw()


class StartingMenu(ImageScreen):
    def __init__(self, width, height):
        self.selector_group = OrderedGroup(0)
        self.foreground_group = OrderedGroup(1)
        super().__init__(resources.circle_animation, width, height)
        self.options: List[MenuItem] = [
            MenuItem(
                width,
                height,
                1,
                lambda x: x.initiate_battle_screen(),
                self.foreground_group,
                "Battle Screen",
            ),
            MenuItem(
                width,
                height,
                2,
                lambda x: print("Options"),
                self.foreground_group,
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
            self.options[self.selected_option].on_click(self)
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
