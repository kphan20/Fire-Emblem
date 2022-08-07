from typing import List
from game.tile import Tile
from pyglet.graphics import Batch
import utils
from game.unit import Character
from game.unit_info import SupportBonuses
from game.affinity import get_affinity_bonus

# Stores methods that involve traversing/interacting with the tile array


def generate_empty_array(tile_arr):
    """Generates empty 2D array for movement/attack range calculations

    Returns:
        list[list[int]]: 2D array filled with zeroes and is as big as the tilemap
    """
    width = len(tile_arr[0])
    height = len(tile_arr)
    return [[0 for _ in range(width)] for _ in range(height)]


def reset_tiles(tiles: List[List[Tile]]):
    """Changes all the tiles on the tilemap back to normal colors"""
    for row in tiles:
        for tile in row:
            tile.clear_tile()


def remove_tiles_from_batch(tile_arr: List[Tile]):
    """Removes tiles from batch as camera moves

    Args:
        tile_arr (list[Tile]): References to tiles that have gotten out of frame
    """
    for tile in tile_arr:
        tile.set_batch(None)


def add_tiles_to_batch(batch: Batch, tile_arr: List[Tile]):
    """Adds tiles to batch as camera moves

    Args:
        tile_arr (list[Tile]): References to tiles that just entered frame
    """
    for tile in tile_arr:
        tile.set_batch(batch)


def color_tiles(
    tiles: List[List[Tile]], filler: List[List[int]], min_range=1, max_range=1
):
    """Changes the color of the map tiles when a unit is selected

    Args:
        filler (list[list[int]]): 2D array holding valid movement/attack squares
    """
    for y, row in enumerate(filler):
        for x, val in enumerate(row):
            if val > 0:
                tiles[y][x].change_tint(utils.BLUE_TINT)
            elif val < 0 and (val >= -(max_range - min_range + 1)):
                tiles[y][x].change_tint(utils.RED_TINT)


def fill_attacks(current_x, current_y, attack_range, filler):
    """Depth first search to fill in a unit's attack range

    Args:
        current_x (int): Current x coordinate being searched
        current_y (int): Current y coordinate being searched
        attack_range (int): Attack range remaining on search
        filler (list[list[int]]): Keeps track of results
    """
    if (
        attack_range <= 0
        or current_x < 0
        or current_x >= len(filler[0])
        or current_y < 0
        or current_y >= len(filler)
    ):
        return
    # Negative squares denote attack squares at border of movement range
    # Checks if the value on the square is greater than the remaining attack range before continuing search
    if (
        filler[current_y][current_x] <= 0
        and filler[current_y][current_x] > -attack_range
    ):
        filler[current_y][current_x] = -attack_range
        fill_attacks(current_x + 1, current_y, attack_range - 1, filler)
        fill_attacks(current_x - 1, current_y, attack_range - 1, filler)
        fill_attacks(current_x, current_y + 1, attack_range - 1, filler)
        fill_attacks(current_x, current_y - 1, attack_range - 1, filler)


def find_enemies_in_range(
    selected_unit: Character, tiles: List[List[Tile]], filler, min_range, max_range
):
    """Finds the targetable enemies within the selected unit's attack range

    Args:
        filler (list[list[int]]): Holds the selected unit's attack range
    """
    current_team = selected_unit.team
    enemies_in_range = []
    for y, row in enumerate(filler):
        for x, tile in enumerate(row):
            if tile < 0 and tile >= -(max_range - min_range + 1):
                enemy_check = tiles[y][x].character
                if enemy_check and enemy_check.team != current_team:
                    enemies_in_range.append((x, y))
    return enemies_in_range


def draw_path(tiles: List[List[Tile]], path):
    """Changes tile colors in path to green

    Args:
        path (list): List containing path coordinates
    """
    for point in path:
        if point[2]:
            tiles[point[1]][point[0]].set_arrow(point[2])


def update_supports_for_unit(tiles: List[List[Tile]], unit: Character, unit_x, unit_y):
    aff = unit.affinity
    supports = unit.supports.keys()
    bonuses = SupportBonuses()

    x_max, y_max = len(tiles[0]), len(tiles)

    for x in range(-3, 4):
        abs_x = abs(x)
        for y in range(abs_x - 3, 4 - abs_x):
            tile_x, tile_y = x + unit_x, y + unit_y
            if tile_y >= 0 and tile_y < y_max and tile_x >= 0 and tile_x < x_max:
                tile_unit = tiles[tile_y][tile_x].character
                if tile_unit in supports:
                    bonuses += (
                        get_affinity_bonus(aff, tile_unit.affinity)
                        * unit.supports[tile_unit]
                    )

    unit.support_bonuses = bonuses
