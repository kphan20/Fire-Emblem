from pyglet.event import EventDispatcher
from pyglet.graphics import OrderedGroup
from pyglet.sprite import Sprite


class Screen(EventDispatcher):
    def __init__(self, background, width, height):
        for frame in background.frames:
            frame.image.width = width
            frame.image.height = height
        self.background_group = OrderedGroup(0)
        self.background = Sprite(background, group=self.background_group)

    def initiate_starting_screen(self):
        self.dispatch_event("on_starting_screen_init")

    def initiate_starting_menu(self):
        self.dispatch_event("on_starting_menu_init")

    def initiate_battle_screen(cls):
        cls.dispatch_event("on_battle_screen_init")

    def draw(self):
        self.background.draw()

    def update(self):
        pass
