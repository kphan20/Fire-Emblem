import pyglet
from game import resources
import random

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
def generate_map_tiles(map_width, map_height, batch, group, screen_tile_width, screen_tile_height):
    map_arr = []
    # Change for debug purposes
    offset_x = 0
    offset_y = 0
    # screen_tile_width += 1
    # screen_tile_height += 1
    for y in range(map_height):
        row = []
        for x in range(map_width):
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
def generate_test_list(x, y):
    return [random.randint(0, 1023) for bruh in range(x * y)]
def test_generate_map_tiles(map_width, map_height, batch, group, screen_tile_width, screen_tile_height, map_bruh):
    map_arr = []
    # Change for debug purposes
    offset_x = 0
    offset_y = 0
    current_tile = 0
    for y in range(map_height):
        row = []
        for x in range(map_width):
            tile_index = map_bruh[current_tile]
            if y <= screen_tile_height and x <= screen_tile_width:
                row.append(Tile(resources.tileset_texture_grid[tile_index], offset_x, offset_y, batch, group, 0))
            else:
                row.append(Tile(resources.tileset_texture_grid[tile_index], offset_x, offset_y, None, group, 0))
            offset_x += TILE_SIZE * TILE_SCALE
            current_tile += 1
        offset_x = 0
        offset_y += TILE_SIZE * TILE_SCALE
        map_arr.append(row)
    return map_arr
def generate_teams(units):
    teams = {}
    for unit in units:
        team = unit.team
        if teams.get(team):
            teams[team].append(unit)
        else:
            teams[team] = [unit]
    return teams