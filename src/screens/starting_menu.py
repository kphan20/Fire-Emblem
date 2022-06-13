from game import resources
from pyglet.sprite import Sprite
from pyglet.graphics import OrderedGroup
from pyglet.window import key

from .screen import Screen


class MenuItem:
    def __init__(self, screen_width, screen_height, position, on_click, group):
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

    def draw(self):
        self.background_sprite.draw()


class StartingMenu(Screen):
    def __init__(self, width, height):
        self.foreground_group = OrderedGroup(1)
        super().__init__(resources.circle_animation, width, height)
        self.options = [
            MenuItem(
                width,
                height,
                1,
                lambda x: x.initiate_battle_screen(),
                self.foreground_group,
            ),
            MenuItem(
                width, height, 2, lambda x: print("option 1"), self.foreground_group
            ),
        ]
        self.selected_option = 0

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
        # scrolls up
        elif symbol == key.UP:
            length = len(self.options)
            self.selected_option = (self.selected_option - 1 + length) % length
        # scrolls down
        elif symbol == key.DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)

    def draw(self):
        super().draw()
        for option in self.options:
            option.draw()
