import pyglet
from game import resources

TILE_SIZE = 16
TILE_SCALE = 5

BLUE_TINT=(10, 100, 255)
RED_TINT=(255, 0, 50)
GREEN_TINT=(0, 255, 255)
NORMAL_TINT=(255, 255, 255)

S_RANK = 5
DOUBLING_CONST = 4

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
    def shift_tile(self, shift_x, shift_y):
        new_position = (shift_x, shift_y)
        self.position = new_position
        character = self.character
        if character:
            character.position = new_position
    def draw(self):
        super().draw()
        self.character.draw()
def generate_map_tiles(batch, group, screen_tile_width, screen_tile_height):
    map_arr = []
    # Change for debug purposes
    offset_x = 0
    offset_y = 0
    # screen_tile_width += 1
    # screen_tile_height += 1
    for y in range(15):
        row = []
        for x in range(22):
            if y <= screen_tile_height and x <= screen_tile_width:
                row.append(Tile(resources.testing_grid, offset_x, offset_y, batch, group, 0))
            else:
                row.append(Tile(resources.testing_grid, offset_x, offset_y, None, group, 0))
            offset_x += TILE_SIZE * TILE_SCALE
        offset_x = 0
        offset_y += TILE_SIZE * TILE_SCALE
        map_arr.append(row)
    map_arr[5][5].tile_type = 1
    map_arr[3][4].tile_type = 1
    map_arr[4][3].tile_type = 1
    map_arr[5][5].img = resources.tile2
    return map_arr