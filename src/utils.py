import pyglet
from game import resources

TILE_SIZE = 16
TILE_SCALE = 5

BLUE_TINT=(10, 100, 255)
RED_TINT=(255, 0, 50)
GREEN_TINT=(0, 255, 255)
NORMAL_TINT=(255, 255, 255)
class Tile(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, batch, group, tile_type):
        super().__init__(img=img, x=x, y=y, batch=batch, group=group)
        self.scale= TILE_SCALE
        self.tile_type = tile_type
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
        for x in range(100):
            row.append(Tile(resources.tile, offset_x, offset_y, batch, group, 0))
            offset_x += TILE_SIZE * TILE_SCALE
        offset_x = 0
        offset_y += TILE_SIZE * TILE_SCALE
        map_arr.append(row)
    map_arr[5][5].tile_type = 1
    map_arr[3][4].tile_type = 1
    map_arr[4][3].tile_type = 1
    map_arr[5][5].img = resources.tile2
    return map_arr