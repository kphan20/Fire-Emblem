import pyglet
from screens import Screen, StartingScreen, StartingMenu, BattleScreen
from game import resources


class Window(pyglet.window.Window):
    def __init__(self, battle_screen_test=False):
        super().__init__(
            width=resources.starting_screen.get_max_width(),
            height=resources.starting_screen.get_max_height(),
            # fullscreen=True,
        )
        self.current_screen = StartingScreen(
            resources.starting_screen.get_max_width(),
            resources.starting_screen.get_max_height(),
        )
        if battle_screen_test:
            self.current_screen = BattleScreen(self.width, self.height)
        # display = pyglet.canvas.Display().get_default_screen()
        # self.background = pyglet.image.SolidColorImagePattern().create_image(
        #     display.width, display.height
        # )
        if not battle_screen_test:
            self.current_screen.push_handlers(self)
        self.push_handlers(self.current_screen)

    def change_screen(self, new_screen: Screen):
        if self.current_screen:
            self.current_screen.pop_handlers()
            self.pop_handlers()
        self.current_screen = new_screen
        if hasattr(new_screen, "event_types"):
            new_screen.push_handlers(self)
        self.push_handlers(new_screen)

    # define these outside of class and attach them on module level
    def on_starting_screen_init(self):
        new_screen = StartingScreen(self.width, self.height)
        self.change_screen(new_screen)

    def on_starting_menu_init(self):
        new_screen = StartingMenu(self.width, self.height)
        self.change_screen(new_screen)

    def on_battle_screen_init(self):
        new_screen = BattleScreen(self.width, self.height)
        self.change_screen(new_screen)

    def update(self, _):
        self.current_screen.update()

    def on_draw(self):
        self.clear()
        # self.background.blit(0, 0)
        self.current_screen.draw()


window = Window(True)
pyglet.clock.schedule_interval(window.update, 1 / 10)
pyglet.app.run()
