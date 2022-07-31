from pyglet.graphics import Batch, OrderedGroup
from pyglet.window import key
from pyglet.sprite import Sprite

from game import resources
from game.item import WeaponType
from game.unit import *
from game.unit_info import SupportBonuses
from game.affinity import get_affinity_bonus
from .screen import Screen


def four_direction_decorator(func):
    """Convenience decorator for algorithms requiring searching in four directions

    Args:
        func (function): Function to be executed four times
    """

    def wrapper(x, y, *args, **kwargs):
        # One function in path_finder requires the returned values
        returned_values = [
            func(x + 1, y, *args, **kwargs),
            func(x - 1, y, *args, **kwargs),
            func(x, y + 1, *args, **kwargs),
            func(x, y - 1, *args, **kwargs),
        ]
        return returned_values

    return wrapper


import utils

# for path_finder method

# Used to retrieve the coordinates of the tiles in the path
# 0, 1, 2, 3 represents right, left, up, down respectively
coord_dict = {
    0: lambda x, y: (x + 1, y),
    1: lambda x, y: (x - 1, y),
    2: lambda x, y: (x, y + 1),
    3: lambda x, y: (x, y - 1),
}
path_resources = resources.path_arrows_dict
arrow_dict = {
    (0, 0): "straightHorizontal",
    (0, 2): "elbowLeftUp",
    (0, 3): "elbowLeftDown",
    (1, 1): "straightHorizontal",
    (1, 2): "elbowRightUp",
    (1, 3): "elbowRightDown",
    (2, 0): "elbowRightDown",
    (2, 1): "elbowLeftDown",
    (2, 2): "straightVertical",
    (3, 0): "elbowRightUp",
    (3, 1): "elbowLeftUp",
    (3, 3): "straightVertical",
}
arrow_head_list = [
    "arrowLeft",
    "arrowRight",
    "arrowDown",
    "arrowUp",
]
arrow_image_config = {
    "straightHorizontal": (80, 40, 40, 20),
    "straightVertical": (40, 80, 20, 40),
    "elbowLeftUp": (60, 60, 40, 20),
    "elbowLeftDown": (60, 60, 40, 40),
    "elbowRightUp": (60, 60, 20, 20),
    "elbowRightDown": (60, 60, 20, 40),
    "arrowLeft": (40, 80, 0, 40),
    "arrowRight": (40, 80, 40, 40),
    "arrowDown": (80, 40, 40, 0),
    "arrowUp": (80, 40, 40, 40),
}
rootConfig = {
    "rootLeft": (40, 20),
    "rootRight": (0, 20),
    "rootUp": (20, 0),
    "rootDown": (20, 40),
}

# on_key_press
arrow_key_dict = {
    key.RIGHT: lambda x, y: (x + 1, y),
    key.LEFT: lambda x, y: (x - 1, y),
    key.UP: lambda x, y: (x, y + 1),
    key.DOWN: lambda x, y: (x, y - 1),
}


class BattleScreen(Screen, key.KeyStateHandler):
    def __init__(self, width, height):
        super().__init__(resources.starting_screen, width, height)

        self.ADJUSTED_TILE_SIZE = utils.TILE_SCALE * utils.TILE_SIZE

        # gets number of complete tiles that the player monitor takes up
        self.screen_tile_width = width // self.ADJUSTED_TILE_SIZE
        self.screen_tile_height = height // self.ADJUSTED_TILE_SIZE

        # sprite drawing batches and groups
        self.batch = Batch()
        self.background = OrderedGroup(0)
        self.foreground = OrderedGroup(1)
        self.selector = OrderedGroup(2)

        # coordinates of the cursor/selector
        self.current_x = 0
        self.current_y = 0

        # stores the coordinates of the bottom left of screen
        # used for camera position calculations
        self.bot_left_x = 0
        self.bot_left_y = 0

        # stores 2d array that marks selected character attack range
        self.attack_view = None
        # stores coordinates of enemies in selected character's range
        self.enemies_in_range = []

        # stores unit that player is currently clicked on
        self.selected_unit = None

        self.selected_enemy = None

        # 2d array that marks selected character movement range
        self.current_moves = None

        # coordinates of selected unit
        self.selected_x = 0
        self.selected_y = 0

        # coordinates of selected unit before attack view
        self.selected_starting_x = 0
        self.selected_starting_y = 0

        # coordinates of camera bottom left before attack view
        self.bot_left_starting_x = 0
        self.bot_left_starting_y = 0

        # creates tile selector sprite
        self.tile_selector = Sprite(
            resources.tile_selector_animation, batch=self.batch, group=self.selector
        )
        self.tile_selector.scale = self.ADJUSTED_TILE_SIZE / utils.SELECTOR_SIZE

        # 2d array of Tile objects
        # use generate_map_tiles for testing
        self.tiles = utils.generate_map_tiles(
            None, self.background, self.screen_tile_width, self.screen_tile_height
        )
        for row in range(self.screen_tile_height + 1):
            for col in range(self.screen_tile_width + 1):
                self.tiles[row][col].set_batch(self.batch)

        self.test_character = Character(
            resources.player_image, self.batch, self.foreground
        )
        self.test_character2 = Character(
            resources.player_image, self.batch, self.foreground, team=1
        )
        self.test_character3 = Character(
            resources.player_image, self.batch, self.foreground, team=1
        )
        self.tiles[self.current_x][self.current_y].set_character(self.test_character)
        self.test_character.add_item(
            Weapon(5, 5, WeaponType.SWORD, weapon_range=WeaponRange(3, 10))
        )
        self.tiles[5][4].set_character(self.test_character2)
        self.tiles[4][5].set_character(self.test_character3)

    def generate_empty_array(self):
        """Generates empty 2D array for movement/attack range calculations

        Returns:
            list[list[int]]: 2D array filled with zeroes and is as big as the tilemap
        """
        tile_arr = self.tiles
        width = len(tile_arr[0])
        height = len(tile_arr)
        return [[0 for _ in range(width)] for _ in range(height)]

    def reset_tiles(self):
        """Changes all the tiles on the tilemap back to normal colors"""
        for row in self.tiles:
            for tile in row:
                tile.clear_tile()

    @staticmethod
    def remove_tiles_from_batch(tile_arr):
        """Removes tiles from batch as camera moves

        Args:
            tile_arr (list[Tile]): References to tiles that have gotten out of frame
        """
        for tile in tile_arr:
            tile.set_batch(None)

    def add_tiles_to_batch(self, tile_arr):
        """Adds tiles to batch as camera moves

        Args:
            tile_arr (list[Tile]): References to tiles that just entered frame
        """
        for tile in tile_arr:
            tile.set_batch(self.batch)

    @staticmethod
    def clamp(list, index):
        """Checks if a coordinate is within the boundaries of the tilemap

        Args:
            list (list): List denoting the tilemap column/row being used for camera boundaries
            index (int): Position value being examined

        Returns:
            int: Either the clamped value or the unchanged index value
        """
        if index == len(list):
            return index - 1
        if index < 0:
            return 0
        return index

    def move_finder(self, current_x, current_y, max_move, max_attack_range):
        """Depth first search to fill in a unit's movement range

        Args:
            current_x (int): Current x coordinate being searched
            current_y (int): Current y coordinate being searched
            max_move (int): Movement remaining from current square
            max_attack_range (int): Unit's attack range

        Returns:
            list[list[int]]: 2D array with positive numbers denoting movement range, negative numbers denoting attack range,
            and zero for tiles that are in neither
        """
        # assuming rectangular map
        tile_arr = self.tiles
        filler = self.generate_empty_array()

        # get terrain cost dict of character
        terrain_cost = self.selected_unit.class_type.terrain_cost

        # Sets first square to large value to prevent backtracking to start square
        max_move += 1
        filler[current_y][current_x] = max_move

        @four_direction_decorator
        def fill_move(current_x, current_y, max_move, filler):
            if (
                current_x < 0
                or current_x >= len(filler[0])
                or current_y < 0
                or current_y >= len(filler)
            ):
                return
            # Prevents unit from moving past another unit on a different team
            if (
                tile_arr[current_y][current_x].character
                and tile_arr[current_y][current_x].character.team
                != self.selected_unit.team
            ):  # tile_arr[self.selected_y][self.selected_x].character.team:
                max_move = 0
            else:
                # If no unit or same team unit, then calculate move normally
                move_cost = terrain_cost[tile_arr[current_y][current_x].tile_type]
                max_move = max_move - move_cost
            # Prevents backtracking to squares pointlessly
            if (
                filler[current_y][current_x] >= max_move
                and filler[current_y][current_x] > 0
            ):
                return
            if max_move > 0:
                filler[current_y][current_x] = max_move
                fill_move(current_x, current_y, max_move, filler)
            else:
                # Finds attack range if unit cannot move any further
                self.fill_attacks(current_x, current_y, max_attack_range, filler)
                return

        fill_move(current_x, current_y, max_move, filler)
        return filler

    @staticmethod
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
            BattleScreen.fill_attacks(
                current_x + 1, current_y, attack_range - 1, filler
            )
            BattleScreen.fill_attacks(
                current_x - 1, current_y, attack_range - 1, filler
            )
            BattleScreen.fill_attacks(
                current_x, current_y + 1, attack_range - 1, filler
            )
            BattleScreen.fill_attacks(
                current_x, current_y - 1, attack_range - 1, filler
            )

    def color_tiles(self, filler, min_range=1, max_range=1):
        """Changes the color of the map tiles when a unit is selected

        Args:
            filler (list[list[int]]): 2D array holding valid movement/attack squares
        """
        for y, row in enumerate(filler):
            for x, val in enumerate(row):
                if val > 0:
                    self.tiles[y][x].change_tint(utils.BLUE_TINT)
                elif val < 0 and (val >= -(max_range - min_range + 1)):
                    self.tiles[y][x].change_tint(utils.RED_TINT)

    def color_attack_tiles(self, min_range, max_range):
        """Shows a unit's attack range after they have moved

        Args:
            min_range (int): The minimum distance from which a unit can attack
            max_range (int): The selected unit's max attack range

        Returns:
            [list[list[int]]]: 2D array with attack squares
        """
        filler = self.generate_empty_array()
        self.fill_attacks(
            self.current_x, self.current_y, max_range + 1, filler
        )  # change this to current
        self.color_tiles(filler, min_range, max_range)
        return filler

    def find_enemies_in_range(self, filler, min_range, max_range):
        """Finds the targetable enemies within the selected unit's attack range

        Args:
            filler (list[list[int]]): Holds the selected unit's attack range
        """
        current_team = self.selected_unit.team
        for y, row in enumerate(filler):
            for x, tile in enumerate(row):
                if tile < 0 and tile >= -(max_range - min_range + 1):
                    enemy_check = self.tiles[y][x].character
                    if enemy_check and enemy_check.team != current_team:
                        self.enemies_in_range.append((x, y))

    def path_finder(self, destination_x, destination_y, filler):
        """Finds the path from the selected unit's current location to a destination point

        Args:
            destination_x (int): Destination x coordinate
            destination_y (int): Destination y coordinate
            filler (list[list[int]]): Contains unit's movement range

        Returns:
            list | string: List of tuples with coordinates of path or a string denoting an invalid path
        """

        @four_direction_decorator
        def check(x_coor, y_coor):
            if (
                x_coor < 0
                or x_coor > len(filler[0]) - 1
                or y_coor < 0
                or y_coor > len(filler) - 1
            ):
                return -1
            return filler[y_coor][x_coor]

        def in_screen_bounds(x_coord, y_coord):
            return (
                x_coord >= self.bot_left_x
                and x_coord <= self.bot_left_x + self.screen_tile_width
                and y_coord >= self.bot_left_y
                and y_coord <= self.bot_left_y + self.screen_tile_height
            )

        if filler[destination_y][destination_x] > 0:
            # Starts from destination and backtracks by following the path with the greatest values
            x_coordinate, y_coordinate = destination_x, destination_y
            path = []
            previous_change = None
            # print((destination_x, destination_y))
            # print(self.selected_x, self.selected_y)
            while x_coordinate != self.selected_x or y_coordinate != self.selected_y:
                # Checks right, left, up, and down tiles for their values
                tile_values = check(x_coordinate, y_coordinate)
                # Retrieves largest value index
                next_index = tile_values.index(max(tile_values))
                # next_index corresponds with the directions in coord_dict to calculate next tile
                new_coordinates = coord_dict[next_index](x_coordinate, y_coordinate)
                if previous_change or previous_change == 0:
                    arrow_string = arrow_dict[(previous_change, next_index)]
                else:
                    arrow_string = arrow_head_list[next_index]
                arrow_image = path_resources[arrow_string]
                (
                    arrow_image.width,
                    arrow_image.height,
                    arrow_image.anchor_x,
                    arrow_image.anchor_y,
                ) = arrow_image_config[arrow_string]
                arrow = Sprite(arrow_image, group=self.foreground)
                if in_screen_bounds(x_coordinate, y_coordinate):
                    arrow.batch = self.batch
                path.append((x_coordinate, y_coordinate, arrow))
                x_coordinate, y_coordinate = new_coordinates
                previous_change = next_index

            if previous_change or previous_change == 0:
                if next_index == 0:
                    arrow_string = "rootLeft"
                elif next_index == 1:
                    arrow_string = "rootRight"
                elif next_index == 2:
                    arrow_string = "rootDown"
                else:
                    arrow_string = "rootUp"
                arrow_image = path_resources[arrow_string]
                arrow_image.width, arrow_image.height = (40, 40)
                arrow_image.anchor_x, arrow_image.anchor_y = rootConfig[arrow_string]
                arrow = Sprite(arrow_image, group=self.foreground)
                if in_screen_bounds(x_coordinate, y_coordinate):
                    arrow.batch = self.batch
                path.append((x_coordinate, y_coordinate, arrow))
            elif destination_x != self.selected_x and destination_y != self.selected_y:
                path.append(
                    (
                        x_coordinate,
                        y_coordinate,
                        Sprite(path_resources["rootUp"]),
                    )
                )
            path.reverse()
            return path
        return "outside of range"

    def draw_path(self, path):
        """Changes tile colors in path to green

        Args:
            path (list): List containing path coordinates
        """
        for point in path:
            if point[2]:
                # if point[0] >= self.bot_left_x:
                self.tiles[point[1]][point[0]].set_arrow(point[2])

    def reset_after_select(self):
        """Used to reset class variables after unit selection"""
        self.selected_unit = None
        self.enemies_in_range = []
        self.attack_view = None
        self.selected_enemy = None

    def shift_tiles(self):
        """Redraws tiles after camera pan"""
        offset_x = 0
        offset_y = 0
        offset_size = self.ADJUSTED_TILE_SIZE
        for y in range(self.screen_tile_height):
            for x in range(self.screen_tile_width):
                self.tiles[y + self.bot_left_y][x + self.bot_left_x].shift_tile(
                    offset_x, offset_y
                )
                offset_x += offset_size
            offset_x = 0
            offset_y += offset_size

    def camera_bounds(self, direction):
        camera_x_pos = self.current_x - self.bot_left_x
        camera_y_pos = self.current_y - self.bot_left_y

        if direction == key.LEFT:
            if self.bot_left_x == 0 or camera_x_pos > utils.CAMERA_EDGE - 1:
                return
            self.remove_tiles_from_batch(
                [
                    tiles[self.bot_left_x + self.screen_tile_width - 1]
                    for tiles in self.tiles
                ]
            )
            # moves bottom left to the left 1 tile
            self.bot_left_x -= 1
            self.add_tiles_to_batch(
                [
                    self.tiles[row][self.bot_left_x]
                    for row in range(
                        self.bot_left_y, self.bot_left_y + self.screen_tile_height
                    )
                ]
            )
            self.shift_tiles()
        elif direction == key.RIGHT:
            if (
                # self.current_x == len(self.tiles[0]) - 2 or
                camera_x_pos
                < self.screen_tile_width - utils.CAMERA_EDGE
            ):
                return

            # if screen_tile_width has no remainder, <= edge_check
            # edge_check = len(self.tiles[0]) - 1
            if self.bot_left_x + self.screen_tile_width >= len(self.tiles[0]):
                return
            # if self.bot_left_x + self.screen_tile_width <= edge_check:
            self.bot_left_x += 1

            self.remove_tiles_from_batch(
                [tiles[self.bot_left_x - 1] for tiles in self.tiles]
            )

            self.add_tiles_to_batch(
                [
                    self.tiles[row][self.bot_left_x + self.screen_tile_width - 1]
                    for row in range(
                        self.bot_left_y, self.bot_left_y + self.screen_tile_height
                    )
                ]
            )
            self.shift_tiles()
        elif direction == key.UP:
            if (
                # self.bot_left_y == len(self.tiles) - 2 or
                camera_y_pos
                < self.screen_tile_height - utils.CAMERA_EDGE
            ):
                return
            edge_check = len(self.tiles) - 1
            if self.bot_left_y + self.screen_tile_height >= edge_check + 1:
                return
            # if self.bot_left_y + self.screen_tile_height <= edge_check:
            self.bot_left_y += 1
            self.remove_tiles_from_batch(self.tiles[self.bot_left_y - 1])
            self.add_tiles_to_batch(
                self.tiles[self.bot_left_y + self.screen_tile_height - 1][
                    self.bot_left_x : self.bot_left_x + self.screen_tile_width
                ]
            )
            self.shift_tiles()
        elif direction == key.DOWN:
            if self.bot_left_y == 0 or camera_y_pos > utils.CAMERA_EDGE - 1:
                return
            self.remove_tiles_from_batch(
                self.tiles[self.bot_left_y + self.screen_tile_height - 1]
            )
            self.bot_left_y -= 1
            self.add_tiles_to_batch(
                self.tiles[self.bot_left_y][
                    self.bot_left_x : self.bot_left_x + self.screen_tile_width
                ]
            )
            self.shift_tiles()

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)

        if symbol == key.E:
            if self.selected_unit:
                # handles when a unit has been selected for movement/attack
                if self.attack_view:
                    if self.enemies_in_range:
                        # TODO-handle attacking an enemy here

                        self.tile_selector.image = resources.tile_selector_animation

                    # reset
                    self.reset_tiles()
                    self.reset_after_select()
                    return

                if (
                    self.current_moves[self.current_y][self.current_x] > 0
                    and self.tiles[self.current_y][self.current_x].character is None
                ):
                    # move selected character
                    self.tiles[self.current_y][self.current_x].set_character(
                        self.selected_unit
                    )

                    self.tiles[self.selected_starting_y][
                        self.selected_starting_x
                    ].character = None

                    # updates current character coordinates
                    self.selected_x, self.selected_y = self.current_x, self.current_y

                    # fill in red attack squares
                    self.reset_tiles()

                    weapon_range = self.selected_unit.get_weapon_range()
                    self.attack_view = self.color_attack_tiles(
                        weapon_range.min_range, weapon_range.max_range
                    )
                    self.find_enemies_in_range(
                        self.attack_view, weapon_range.min_range, weapon_range.max_range
                    )
                    if self.enemies_in_range:
                        self.tile_selector.image = (
                            resources.tile_selector_attack_animation
                        )
                        self.selected_enemy = 0
                        enemy_x, enemy_y = self.enemies_in_range[0]
                        tile_size = self.ADJUSTED_TILE_SIZE
                        self.tile_selector.x = (enemy_x - self.bot_left_x) * tile_size
                        self.tile_selector.y = (enemy_y - self.bot_left_y) * tile_size
                    else:
                        # remove coloring if no enemies in range
                        self.reset_tiles()

                    return  # unnecessary
            else:
                # no unit selected

                character = self.tiles[self.current_y][self.current_x].character

                # if character on selected tile
                # TODO-change this to account for teams (don't select enemy units)
                if character:
                    # select character and draw their movement

                    # updates game state
                    self.selected_x, self.selected_y = (
                        self.current_x,
                        self.current_y,
                    )

                    self.selected_starting_x, self.selected_starting_y = (
                        self.current_x,
                        self.current_y,
                    )
                    self.bot_left_starting_x, self.bot_left_starting_y = (
                        self.bot_left_x,
                        self.bot_left_y,
                    )
                    self.selected_unit = character

                    weapon_range = character.get_weapon_range()

                    # TODO-replace with actual character stats
                    self.current_moves = self.move_finder(
                        self.current_x, self.current_y, 8, weapon_range.max_range
                    )
                    self.color_tiles(
                        self.current_moves,
                        weapon_range.min_range,
                        weapon_range.max_range,
                    )
                    return  # unnecessary
            return
        if symbol == key.Q:
            if self.selected_unit:
                # character was moved to new square temporarily
                if self.attack_view:
                    # remove preview of character from tile
                    self.tiles[self.selected_y][self.selected_x].character = None

                    # move selected unit to its original square
                    self.tiles[self.selected_starting_y][
                        self.selected_starting_x
                    ].set_character(self.selected_unit)

                    # resets to normal selector animation
                    self.tile_selector.image = resources.tile_selector_animation

                # move camera to its original position
                # eventually transition to animation
                if (
                    self.bot_left_starting_x != self.bot_left_x
                    or self.bot_left_starting_y != self.bot_left_y
                ):
                    # just going to clear and reset whole screen
                    for row in range(self.screen_tile_height):
                        rowNum = self.bot_left_y + row
                        for col in range(self.screen_tile_width):
                            self.tiles[rowNum][self.bot_left_x + col].set_batch(None)

                    self.bot_left_x, self.bot_left_y = (
                        self.bot_left_starting_x,
                        self.bot_left_starting_y,
                    )
                    for row in range(self.screen_tile_height):
                        rowNum = self.bot_left_y + row
                        for col in range(self.screen_tile_width):
                            self.tiles[rowNum][self.bot_left_x + col].set_batch(
                                self.batch
                            )
                    self.shift_tiles()

                # move selector to original square
                self.current_x, self.current_y = (
                    self.selected_starting_x,
                    self.selected_starting_y,
                )

                tile_size = self.ADJUSTED_TILE_SIZE
                self.tile_selector.x = (self.current_x - self.bot_left_x) * tile_size
                self.tile_selector.y = (self.current_y - self.bot_left_y) * tile_size

                self.reset_after_select()

            # removes markings from tiles
            self.reset_tiles()
            return

    def update_supports_for_unit(self, unit: Character, unit_x, unit_y):
        aff = unit.affinity
        supports = unit.supports.keys()
        bonuses = SupportBonuses()

        x_max, y_max = len(self.tiles[0]), len(self.tiles)

        for x in range(-3, 4):
            abs_x = abs(x)
            for y in range(abs_x - 3, 4 - abs_x):
                tile_x, tile_y = x + unit_x, y + unit_y
                if tile_y >= 0 and tile_y < y_max and tile_x >= 0 and tile_x < x_max:
                    tile_unit = self.tiles[tile_y][tile_x].character
                    if tile_unit in supports:
                        bonuses += (
                            get_affinity_bonus(aff, tile_unit.affinity)
                            * unit.supports[tile_unit]
                        )

        unit.support_bonuses = bonuses

    def draw(self):
        self.batch.draw()

    def update(self):
        options = [key.RIGHT, key.LEFT, key.UP, key.DOWN]
        change_x = 0
        change_y = 0
        for option in options:
            if self[option]:
                change = arrow_key_dict[option](0, 0)
                change_x += change[0]
                change_y += change[1]

        if change_x == 0 and change_y == 0:
            return

        for option in options:
            if self[option]:
                self.camera_bounds(option)
        tile_size = self.ADJUSTED_TILE_SIZE
        if not self.attack_view:
            self.current_x = self.clamp(self.tiles[0], self.current_x + change_x)
            self.current_y = self.clamp(self.tiles, self.current_y + change_y)
            self.tile_selector.x = (self.current_x - self.bot_left_x) * tile_size
            self.tile_selector.y = (self.current_y - self.bot_left_y) * tile_size
            # draws path if not attacking and unit is selected
            if self.selected_unit:
                if self.current_moves[self.current_y][self.current_x] > 0:
                    self.reset_tiles()
                    weapon_range = self.selected_unit.get_weapon_range()
                    self.color_tiles(
                        self.current_moves,
                        weapon_range.min_range,
                        weapon_range.max_range,
                    )
                    self.draw_path(
                        self.path_finder(
                            self.current_x, self.current_y, self.current_moves
                        )
                    )
        elif self.enemies_in_range:
            scroll_direction = change_x + change_y
            scroll_direction /= abs(scroll_direction)

            # TODO-consider if scroll_direction != 0:
            self.selected_enemy += int(scroll_direction)
            num_enemies = len(self.enemies_in_range)
            self.selected_enemy = (self.selected_enemy + num_enemies) % num_enemies

            enemy_x, enemy_y = self.enemies_in_range[self.selected_enemy]
            self.tile_selector.x = (enemy_x - self.bot_left_x) * tile_size
            self.tile_selector.y = (enemy_y - self.bot_left_y) * tile_size
