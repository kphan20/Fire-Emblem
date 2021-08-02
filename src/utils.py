import pyglet
from game import resources

TILE_SIZE = 16
TILE_SCALE = 5

BLUE_TINT=(10, 100, 255)
RED_TINT=(255, 0, 50)
NORMAL_TINT=(255, 255, 255)
class Tile(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, batch, group):
        super().__init__(img=img, x=x, y=y, batch=batch, group=group)
        self.scale= TILE_SCALE
        self.character = None
        self.arrow = None
    def change_tint(self, color):
        self.color = color
    def set_character(self, character):
        self.character = character
        self.character.position = (self.x, self.y)
    def draw(self):
        super().draw()
        self.character.draw()
def generate_map_tiles(batch, group):
    map_arr = []
    # Change for debug purposes
    offset_x = 0
    offset_y = 0
    for y in range(11):
        row = []
        for x in range(20):
            row.append(Tile(resources.tile, offset_x, offset_y, batch, group))
            offset_x += TILE_SIZE * TILE_SCALE
        offset_x = 0
        offset_y += TILE_SIZE * TILE_SCALE
        map_arr.append(row)
    return map_arr