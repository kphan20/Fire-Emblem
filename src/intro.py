import pyglet
from pyglet.window import key, mouse
#pyglet .media .app .text .input
import pyglet.canvas as canvas
import pyglet.graphics
import random
from game import resources
from tile import Tile
from utils import TILE_SIZE
class ScreenLabel:
    def __init__(self):
        self.label=pyglet.text.Label('Hello, world', x=window.width//2, y=window.height//2, anchor_x='center', anchor_y='center')
        self.fullscreen_toggle = True
    def changeLabel(self, newLabel):
        self.label=newLabel
    def toggle_fullscreen(self):
        self.fullscreen_toggle = not self.fullscreen_toggle
        return self.fullscreen_toggle

player_sprite = pyglet.sprite.Sprite(img=resources.tile, x=400, y=300)
class MovingSprite(pyglet.sprite.Sprite):
    def __init__(self, max_x, max_y):
        super().__init__(img=resources.player_image, x=400, y=300)
        self.vel_x, self.vel_y = 0.0, 0.0
        self.max_x, self.max_y = max_x, max_y
        self.key_handler = key.KeyStateHandler()
    def check_bounds(self):
        if self.x > self.max_x:
            self.x -= self.max_x
        elif self.x < 0:
            self.x = max_x
        if self.y > self.max_y:
            self.y -= self.max_y
        elif self.y < 0:
            self.y = max_y
    def update(self, dt):
        if self.key_handler[key.RIGHT]:
            self.vel_x += 20.0
        if self.key_handler[key.LEFT]:
            self.vel_x -= 20.0
        if not(self.key_handler[key.RIGHT] or self.key_handler[key.LEFT]):
            self.vel_x += -self.vel_x / 20
        if self.key_handler[key.UP]:
            self.vel_y += 20.0
        if self.key_handler[key.DOWN]:
            self.vel_y -= 20.0
        if not(self.key_handler[key.UP] or self.key_handler[key.DOWN]):
            self.vel_y += -self.vel_y / 20
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        self.check_bounds()

screens = canvas.get_display()
screens = screens.get_screens()
fullscreen_toggle = True
window = pyglet.window.Window(fullscreen=fullscreen_toggle, screen=screens[-1])
window1 = pyglet.window.Window(fullscreen=fullscreen_toggle, screen=screens[-1])

#window.set_icon(...images)
#window.push_handlers(key.KeyStateHandler())
#window.set_mouse_visible()
#window.set_exclusive_mouse(True) prevents mouse from leaving window and being visible; x and y irrelevant
max_x, max_y = window.get_size()
labelObj = ScreenLabel()
label = pyglet.text.Label('Hello, world', x=window.width//2, y=window.height//2, anchor_x='center', anchor_y='center')
player_character = MovingSprite(max_x, max_y)
batch = pyglet.graphics.Batch()
offset_x = 100
offset_y = 100
tiles = []
print(type(resources.tile))
for x in range(5):
    for y in range(5):
        tiles.append(Tile(resources.tile, offset_x, offset_y,batch))#pyglet.shapes.Rectangle(x=offset_x, y=offset_y, width=TILE_SIZE, height=TILE_SIZE,color=(50, 50, 59), batch=batch))
        offset_y += TILE_SIZE
    offset_y = 100
    offset_x += TILE_SIZE
@window.event
def on_draw():
    window.clear()
    labelObj.label.draw()
    player_character.draw()
    player_sprite.draw()
    batch.draw()
@window1.event
def on_draw():
    window.clear()
#def on_text(text): for chat input rather than movement/game controls
#def on_text_motion(motion): for key holding (prolly for movement through text)
#def on_mouse_motion(x, y, dx, dy):
#def on_mouse_release(x, y, button,modifiers):
#def on_mouse_drag(x, y, dx, dy, buttons, modifiers)
#def on_mouse_scroll(x, y, scroll_x, scroll_y)
@window.event
def on_mouse_press(x, y, button, modifiers):
    global fullscreen_toggle
    fullscreen_toggle = not fullscreen_toggle
    if button == mouse.LEFT:
        window.set_fullscreen(labelObj.toggle_fullscreen())
    else:
        labelObj.changeLabel(pyglet.text.Label(str(random.randint(1, 10)), x=window.width//2, y=window.height//2, anchor_x='center', anchor_y='center'))
@window.event
def on_key_press(symbol, modifiers):
    print(symbol)
    if symbol == key.A:
        labelObj.changeLabel(pyglet.text.Label(str(random.randint(1, 10)), x=window.width//2, y=window.height//2, anchor_x='center', anchor_y='center'))
        #window.clear()
    if symbol == key.S and modifiers:
        pyglet.app.exit()
    if symbol == key.D:
        global player_sprite
        player_sprite.x += 50
@window.event
def on_resize(width, height):
    pass
# event_logger = pyglet.window.event.WindowEventLogger()
# window.push_handlers(event_logger)
window.push_handlers(player_character.key_handler)
def update():
    player_character.update()
    
    
pyglet.clock.schedule_interval(player_character.update, 1/120.0)
pyglet.app.run()