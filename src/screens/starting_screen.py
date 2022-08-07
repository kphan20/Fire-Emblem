from .screen import ImageScreen
from game import resources
from pyglet.window import key


class StartingScreen(ImageScreen):
    def __init__(self, width, height):
        super().__init__(resources.starting_screen, width, height)
        self.register_event_type("on_starting_menu_init")

    def on_key_press(self, symbol, modifiers):
        if symbol == key.E:
            self.initiate_starting_menu()
