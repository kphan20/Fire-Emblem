import pyglet
from game import resources, unit
from extensions import GBASprite
import random
from utils import TILE_SCALE, TILE_SIZE, NORMAL_TINT

map_dimensions = {"width": 22, "height": 15}


class Tile(GBASprite):
    def __init__(self, img, x, y, batch, group, tile_type):
        # The sprite is currently still anchored in its bottom left corner
        super().__init__(img=img, x=x, y=y, batch=batch, group=group)

        self.scale = TILE_SCALE
        self.tile_type = tile_type
        self.character = None
        self.arrow = None
        self.test_group = pyglet.graphics.OrderedGroup(2)
        self.text = pyglet.text.Label(
            f"{x / (TILE_SCALE * TILE_SIZE)}, {y / (TILE_SCALE * TILE_SIZE)}",
            font_name="Times New Roman",
            font_size=10,
            x=x,
            y=y,
            batch=batch,
            group=self.test_group,
        )

    def change_tint(self, color):
        """Changes RGB of tile sprite

        Args:
            color (tuple[int]): Tuple representing new RGB values
        """
        self.color = color

    def set_character(self, character: unit.Character):
        """Adds character to tile and positions them correctly

        Args:
            character (Character): Character class object
        """
        self.character = character
        self.character.position = (self.x, self.y)
        self.character.batch = self.batch

    def set_arrow(self, arrow):
        self.arrow = arrow
        self.arrow.position = (self.x + self.width // 2, self.y + self.height // 2)
        self.arrow.batch = self.batch

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
            self.arrow.position = (
                shift_x + 0.5 * TILE_SIZE * TILE_SCALE,
                shift_y + 0.5 * TILE_SIZE * TILE_SCALE,
            )
        self.text.position = new_position

    def clear_tile(self):
        """Removes any temporary elements drawn on tile"""
        self.arrow = None
        self.color = NORMAL_TINT

    def set_batch(self, batch):
        self.batch = batch
        if self.character:
            self.character.batch = batch
        if self.arrow:
            self.arrow.batch = batch
        self.text.batch = batch

    def draw(self):
        # super().draw()
        self.character.draw()
        # self.text.draw()


def generate_map_tiles(
    batch, group, screen_tile_width, screen_tile_height
) -> list[list[Tile]]:
    """
    Loads testing map into 2D array of tiles
    Args:
        batch (pyglet.graphics.Batch): drawing window's batch group
        group (pyglet.graphics.OrderedGroup): tile's group
        screen_tile_width (int): screen's width in tiles
        screen_tile_height (int): screen's height in tiles

    Returns:
        list[list[Tile]]: map in Tile objects
    """
    map_arr = []
    # Change for debug purposes
    offset_x = 0
    offset_y = 0
    # screen_tile_width += 1
    # screen_tile_height += 1
    for y in range(map_dimensions["height"]):
        row = []
        for x in range(map_dimensions["width"]):
            if y <= screen_tile_height and x <= screen_tile_width:
                row.append(
                    Tile(resources.testing_grid, offset_x, offset_y, batch, group, 0)
                )
            else:
                row.append(
                    Tile(resources.testing_grid, offset_x, offset_y, None, group, 0)
                )
            offset_x += TILE_SIZE * TILE_SCALE
        offset_x = 0
        offset_y += TILE_SIZE * TILE_SCALE
        map_arr.append(row)
    map_arr[5][5].tile_type = 1
    map_arr[3][4].tile_type = 1
    map_arr[4][3].tile_type = 1
    return map_arr


def generate_test_list(x, y):
    return [random.randint(0, 1023) for bruh in range(x * y)]


# update_map_info(os.path.join(dirname, './test_files/test (1).txt'))
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
    # update_map_info(os.path.join(dirname, map))

    # Testing code
    map_dimensions["height"] = 25
    map_dimensions["width"] = 100
    map_list = generate_test_list(map_dimensions["height"], map_dimensions["width"])

    # map_list = [291 for x in range(map_dimensions['width'] * map_dimensions['height'])]
    map_arr = []
    # Change for debug purposes
    offset_x = 0
    offset_y = 0
    current_tile = 0
    for y in range(map_dimensions["height"]):
        row = []
        for x in range(map_dimensions["width"]):
            tile_index = map_list[current_tile]
            if y <= screen_tile_height and x <= screen_tile_width:
                row.append(
                    Tile(
                        resources.tileset_texture_grid[tile_index],
                        offset_x,
                        offset_y,
                        batch,
                        group,
                        0,
                    )
                )
            else:
                row.append(
                    Tile(
                        resources.tileset_texture_grid[tile_index],
                        offset_x,
                        offset_y,
                        None,
                        group,
                        0,
                    )
                )
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
