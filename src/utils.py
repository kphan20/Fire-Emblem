import pyglet
from game import resources
import random
import json
import os

dirname = os.path.dirname(__file__)

TILE_SIZE = 16
TILE_SCALE = 5

CAMERA_EDGE = 2

SELECTOR_SIZE = 24

BLUE_TINT=(10, 100, 255)
RED_TINT=(255, 0, 50)
GREEN_TINT=(0, 255, 255)
NORMAL_TINT=(255, 255, 255)

S_RANK = 5
DOUBLING_CONST = 4

map_dimensions = {'width': 22, 'height': 15}

class Tile(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, batch, group, tile_type):
        # The sprite is currently still anchored in its bottom left corner
        super().__init__(img=img, x=x, y=y, batch=batch, group=group)
        self.scale= TILE_SCALE
        self.tile_type = tile_type
        self.character = None
        self.arrow = None
        
    def change_tint(self, color):
        """Changes RGB of tile sprite

        Args:
            color (tuple[int]): Tuple representing new RGB values
        """
        self.color = color
        
    def set_character(self, character):
        """Adds character to tile and positions them correctly

        Args:
            character (Character): Character class object
        """
        self.character = character
        self.character.position = (self.x, self.y)
        
    def set_arrow(self, arrow):
        self.arrow = arrow
        self.arrow.position = (self.x + self.width // 2, self.y + self.height // 2)
        
    def shift_tile(self, shift_x, shift_y):
        """Shifts the tile position to new x and y

        Args:
            shift_x (int): New x coordinate
            shift_y (int): New y coordinate
        """
        new_position = (shift_x, shift_y)
        self.position = new_position
        if self.character:
            self.character.position = new_position
        if self.arrow:
            self.arrow.position = (shift_x + 0.5 * TILE_SIZE * TILE_SCALE, shift_y + 0.5 * TILE_SIZE * TILE_SCALE)
            
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

map_list = generate_test_list(map_dimensions['width'], map_dimensions['height'])
def update_map_info(text_file):
    """Retrieves data about map from text file (info is separated by spaces)

    Args:
        text_file (str): File name
    """
    global map_dimensions, map_list
    with open(text_file, 'r') as f:
        data = f.readline().split(' ')
        try:
            map_dimensions = {'width': int(data[0]), 'height': int(data[1])}
            map_list = json.loads(r'{}'.format(data[2]))
        except json.decoder.JSONDecodeError:
            print('decode error')
        
#update_map_info(os.path.join(dirname, './test_files/test (1).txt'))        
def test_generate_map_tiles(map, batch, group, screen_tile_width, screen_tile_height):
    """Generates tile map array from file and sets the initial ones on screen visible

    Args:
        map (str): Contains relative path to map file
        batch (Batch): Batch object used to render only the visible tiles on screen
        group (Group): Sets tiles to the lowest draw layer
        screen_tile_width (int): Current screen width
        screen_tile_height (int): Current screen height

    Returns:
        list[Tile]: List with all the map tiles
    """
    #update_map_info(os.path.join(dirname, map))
    
    # Testing code
    map_dimensions['height'] = 15
    map_dimensions['width'] = 100
    map_list = generate_test_list(25, 15)
    
    map_list = [291 for x in range(map_dimensions['width'] * map_dimensions['height'])]
    map_arr = []
    # Change for debug purposes
    offset_x = 0
    offset_y = 0
    current_tile = 0
    for y in range(map_dimensions['height']):
        row = []
        for x in range(map_dimensions['width']):
            tile_index = map_list[current_tile]
            if y <= screen_tile_height and x <= screen_tile_width:
                row.append(Tile(resources.tileset_texture_grid[tile_index], offset_x, offset_y, batch, group, 0))
            else:
                row.append(Tile(resources.tileset_texture_grid[tile_index], offset_x, offset_y, None, group, 0))
            offset_x += TILE_SIZE * TILE_SCALE
            current_tile += 1
        offset_x = 0
        offset_y += TILE_SIZE * TILE_SCALE
        map_arr.append(row)
        
    # Testing code
    map_arr[5][5].tile_type = 1
    map_arr[3][4].tile_type = 1
    map_arr[4][3].tile_type = 1
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