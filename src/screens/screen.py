from pyglet.event import EventDispatcher
from pyglet.graphics import OrderedGroup
from pyglet.sprite import Sprite
import utils


class Screen(EventDispatcher):
    def initiate_starting_screen(self):
        self.dispatch_event("on_starting_screen_init")

    def initiate_starting_menu(self):
        self.dispatch_event("on_starting_menu_init")

    def initiate_battle_screen(cls):
        cls.dispatch_event("on_battle_screen_init")

    def draw(self):
        pass

    def update(self):
        pass


class ImageScreen(Screen):
    def __init__(self, background, width, height):
        for frame in background.frames:
            frame.image.width = width
            frame.image.height = height
        self.background_group = OrderedGroup(0)
        self.background = Sprite(background, group=self.background_group)
        utils.set_texture_mag_filter(self.background._texture)

    def draw(self):
        self.background.draw()
