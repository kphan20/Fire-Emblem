from typing import List
from collections import OrderedDict
from pyglet.graphics import Batch, OrderedGroup
from pyglet.window import key

from extensions import GBASprite as Sprite
from game import resources
from game.item import WeaponType
from game.unit import Character, Weapon, WeaponRange
from game.game_formulas import (
    damage_calc,
    accuracy_calc,
    determine_hit,
    crit_accuracy_calc,
)
from game.tile import generate_map_tiles
from game.affinity import Affinity
from game.unit_info import Stats
from .screen import Screen
from .battle_screen_helpers.tile_helpers import (
    generate_empty_array,
    reset_tiles,
    remove_tiles_from_batch,
    add_tiles_to_batch,
    color_tiles,
    fill_attacks,
    find_enemies_in_range,
    draw_path,
    update_supports_for_unit,
)
from .battle_screen_helpers.pathfinder_helpers import (
    four_direction_decorator,
    coord_dict,
    path_resources,
    arrow_dict,
    arrow_head_list,
    arrow_image_config,
    root_config,
    arrow_key_dict,
)
from .battle_screen_helpers.viewstate import ViewState
from .windows import (
    CombatMenu,
    PointerMenu,
    RescueWindow,
    TakeWindow,
    GiveWindow,
    CarryActionWindow,
)
import utils


no_scroll_viewstates = {
    ViewState.OPTION_MENU,
    ViewState.WEAPON_SELECTION,
    ViewState.TURN_MENU,
    ViewState.INVENTORY_MENU,
}

fixed_scroll_viewstates = {
    ViewState.TAKE_MENU,
    ViewState.GIVE_MENU,
    ViewState.DROP_MENU,
    ViewState.RESCUE_MENU,
    ViewState.ATTACK_SELECTION,
}


class BattleScreen(Screen, key.KeyStateHandler):
    def __init__(self, width, height):
        super().__init__()

        self.ADJUSTED_TILE_SIZE = utils.TILE_SCALE * utils.TILE_SIZE

        # gets number of complete tiles that the player monitor takes up
        self.screen_tile_width = width // self.ADJUSTED_TILE_SIZE
        self.screen_tile_height = height // self.ADJUSTED_TILE_SIZE

        # sprite drawing batches and groups
        self.batch = Batch()
        self.background = OrderedGroup(0)
        self.foreground = OrderedGroup(1)
        self.selector = OrderedGroup(2)
        self.menu = OrderedGroup(3)
        self.text = OrderedGroup(4)

        self.forecast_menu_sprite = CombatMenu(self.menu, self.text, width, height)

        self.option_menu_sprite = PointerMenu(self.menu, self.text, width, height)

        self.rescue_menu_sprite = RescueWindow(self.menu, self.text, width, height)

        self.give_menu_sprite = GiveWindow(self.menu, self.text, width, height)

        self.take_menu_sprite = TakeWindow(self.menu, self.text, height)

        self.inventory_menu_sprite = PointerMenu(self.menu, self.text, width, height)

        self.trade_menu_sprite = PointerMenu(self.menu, self.text, width, height)

        self.weapon_menu_sprite = PointerMenu(self.menu, self.text, width, height)

        self.turn_menu_sprite = PointerMenu(self.menu, self.text, width, height)

        self.current_view = ViewState.NOTHING_SELECTED

        # coordinates of the cursor/selector
        self.current_x = 0
        self.current_y = 0

        # stores the coordinates of the bottom left of screen
        # used for camera position calculations
        self.bot_left_x = 0
        self.bot_left_y = 0

        # stores coordinates of enemies in selected character's range
        self.enemies_in_range = []
        # TODO consider combining the next three arrays
        self.rescue_in_range = []
        self.take_in_range = []
        self.give_in_range = []
        self.drop_in_range = []
        self.trade_in_range = []

        # stores unit that player is currently clicked on
        self.selected_unit: Character = None

        # index of selected enemy
        self.selected_enemy = None
        self.selected_rescue = None
        self.selected_take = None
        self.selected_give = None
        self.selected_drop = None
        self.selected_trade = None

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
        self.tiles = generate_map_tiles(
            None, self.background, self.screen_tile_width, self.screen_tile_height
        )
        for row in range(self.screen_tile_height + 1):
            for col in range(self.screen_tile_width + 1):
                self.tiles[row][col].set_batch(self.batch)

        self.test_character = Character(
            resources.overworld_anim,
            self.batch,
            self.foreground,
            affinity=Affinity.FIRE,
            stats=Stats(con=4),
        )
        self.test_character2 = Character(
            resources.player_image,
            self.batch,
            self.foreground,
            team=0,
            supports={self.test_character: 3},
        )
        self.test_character3 = Character(
            resources.player_image, self.batch, self.foreground, team=1
        )
        self.test_character4 = Character(
            resources.overworld_anim, self.batch, self.foreground, stats=Stats(con=1)
        )
        self.tiles[self.current_y][self.current_x].set_character(self.test_character)
        self.test_character.add_item(
            Weapon(
                5,
                5,
                WeaponType.SWORD,
                might=1,
                weapon_range=WeaponRange(1, 1),
                hit=100,
            )
        )
        self.test_character3.add_item(
            Weapon(
                5,
                5,
                WeaponType.SWORD,
                might=1,
                weapon_range=WeaponRange(1, 1),
                hit=100,
            )
        )
        self.tiles[5][4].set_character(self.test_character2)
        self.tiles[4][5].set_character(self.test_character3)
        self.tiles[3][4].set_character(self.test_character4)

        # TODO- initialize team order
        self.teams: OrderedDict[int, List[Character]] = OrderedDict()
        self.characters = [
            self.test_character,
            self.test_character2,
            self.test_character3,
            self.test_character4,
        ]
        for character in self.characters:
            team = self.teams.setdefault(character.team, [])
            team.append(character)

        self.get_next_team()

    def get_next_team(self) -> None:
        """
        Ends the turn and prepares the next team that is up
        """
        self.current_team, self.current_units = self.teams.popitem(last=False)
        self.fresh_units = set(
            unit for unit in self.current_units if not unit.is_carried
        )
        for unit in self.fresh_units:
            unit.refresh()
        print(self.fresh_units)

    @staticmethod
    def clamp(list: List, index: int) -> int:
        """
        Checks if a coordinate is within the boundaries of the tilemap

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

    def move_finder(
        self, current_x: int, current_y: int, max_move: int, max_attack_range: int
    ):
        """
        Depth first search to fill in a unit's movement range

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
        filler = generate_empty_array(self.tiles)

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
                fill_attacks(current_x, current_y, max_attack_range, filler)
                return

        fill_move(current_x, current_y, max_move, filler)
        return filler

    def path_finder(
        self, destination_x: int, destination_y: int, filler: List[List[int]]
    ):
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
                arrow_image.anchor_x, arrow_image.anchor_y = root_config[arrow_string]
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
        # TODO change this
        return "outside of range"

    def reset_after_select(self) -> None:
        """Used to reset class variables after unit selection"""
        self.selected_unit = None
        self.enemies_in_range = []
        self.selected_enemy = None

    def shift_tiles(self) -> None:
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

    @staticmethod
    def perform_attack(attacking_unit: Character, attacked_unit: Character) -> bool:
        """
        Conducts attempted attack between two characters

        Args:
            attacking_unit (Character): attacking unit
            attacked_unit (Character): attacked unit

        Returns:
            bool: whether or not the attacked unit dies
        """
        acc = accuracy_calc(attacking_unit, attacked_unit, 0)
        if determine_hit(acc):
            crit_acc = crit_accuracy_calc(attacking_unit, attacked_unit)
            damage = damage_calc(
                attacking_unit, attacked_unit, is_crit=determine_hit(crit_acc)
            )
            return attacked_unit.take_damage(damage)
        return False

    def camera_bounds(self, direction: key) -> None:
        """
        Sets camera placement based on input

        Args:
            direction (key): movement key being pressed
        """
        camera_x_pos = self.current_x - self.bot_left_x
        camera_y_pos = self.current_y - self.bot_left_y

        if direction == key.LEFT:
            if self.bot_left_x == 0 or camera_x_pos > utils.CAMERA_EDGE - 1:
                return
            remove_tiles_from_batch(
                [
                    tiles[self.bot_left_x + self.screen_tile_width - 1]
                    for tiles in self.tiles
                ]
            )
            # moves bottom left to the left 1 tile
            self.bot_left_x -= 1
            add_tiles_to_batch(
                self.batch,
                [
                    self.tiles[row][self.bot_left_x]
                    for row in range(
                        self.bot_left_y, self.bot_left_y + self.screen_tile_height
                    )
                ],
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

            remove_tiles_from_batch(
                [tiles[self.bot_left_x - 1] for tiles in self.tiles]
            )

            add_tiles_to_batch(
                self.batch,
                [
                    self.tiles[row][self.bot_left_x + self.screen_tile_width - 1]
                    for row in range(
                        self.bot_left_y, self.bot_left_y + self.screen_tile_height
                    )
                ],
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
            remove_tiles_from_batch(self.tiles[self.bot_left_y - 1])
            add_tiles_to_batch(
                self.batch,
                self.tiles[self.bot_left_y + self.screen_tile_height - 1][
                    self.bot_left_x : self.bot_left_x + self.screen_tile_width
                ],
            )
            self.shift_tiles()
        elif direction == key.DOWN:
            if self.bot_left_y == 0 or camera_y_pos > utils.CAMERA_EDGE - 1:
                return
            remove_tiles_from_batch(
                self.tiles[self.bot_left_y + self.screen_tile_height - 1]
            )
            self.bot_left_y -= 1
            add_tiles_to_batch(
                self.batch,
                self.tiles[self.bot_left_y][
                    self.bot_left_x : self.bot_left_x + self.screen_tile_width
                ],
            )
            self.shift_tiles()

    def move_tile_selector(self, new_x: int, new_y: int) -> None:
        """
        Takes tile coordinates and moves tile selector to that tile
        relative to camera position
        """
        self.tile_selector.x = (new_x - self.bot_left_x) * self.ADJUSTED_TILE_SIZE
        self.tile_selector.y = (new_y - self.bot_left_y) * self.ADJUSTED_TILE_SIZE

    def draw_unit_movement(self) -> None:
        """
        Colors tiles during movement selection
        """
        weapon_range = self.selected_unit.get_weapon_range()
        self.current_moves = self.move_finder(
            self.current_x,
            self.current_y,
            8,  # self.selected_unit.stats.mov,
            weapon_range.max_range,
        )
        color_tiles(
            self.tiles,
            self.current_moves,
            weapon_range.min_range,
            weapon_range.max_range,
        )

    def reset_to_movement(self) -> None:
        """
        Resets tiles and camera to movement selection
        """
        # TODO remove this later
        self.reset_camera()

        self.option_menu_sprite.set_batch(None)

        # remove preview of character from tile
        self.tiles[self.selected_y][self.selected_x].character = None

        # move selected unit to its original square
        self.tiles[self.selected_starting_y][self.selected_starting_x].set_character(
            self.selected_unit
        )

        # resets to normal selector animation
        self.tile_selector.image = resources.tile_selector_animation

        self.current_x, self.current_y = (
            self.selected_starting_x,
            self.selected_starting_y,
        )
        self.selected_x, self.selected_y = (
            self.selected_starting_x,
            self.selected_starting_y,
        )

        self.tile_selector.batch = self.batch
        self.move_tile_selector(self.current_x, self.current_y)

        temp = self.selected_unit

        self.reset_after_select()
        # removes markings from tiles
        reset_tiles(self.tiles)

        self.selected_unit = temp
        self.draw_unit_movement()
        self.current_view = ViewState.MOVEMENT

    def reset_camera(self) -> None:
        """move camera to its original position"""
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
                    self.tiles[rowNum][self.bot_left_x + col].set_batch(self.batch)
            self.shift_tiles()

    def get_combat_forecast(self) -> None:
        """
        Gets predictive info for combat between two characters
        """

        update_supports_for_unit(
            self.tiles,
            self.selected_unit,
            self.current_x,
            self.current_y,
        )
        enemy_x, enemy_y, can_counter = self.enemies_in_range[self.selected_enemy]
        enemy = self.tiles[enemy_y][enemy_x].character

        update_supports_for_unit(self.tiles, enemy, enemy_x, enemy_y)
        self.forecast_menu_sprite.update_text_with_characters(
            self.selected_unit,
            enemy,
            can_counter,
        )

    def move_tile_selector_to_enemy(self):
        enemy_x, enemy_y, _ = self.enemies_in_range[self.selected_enemy]
        self.move_tile_selector(enemy_x, enemy_y)

    def move_tile_selector_to_target(self, coord_arr: List, ind: int):
        tile_x, tile_y = coord_arr[ind]
        self.move_tile_selector(tile_x, tile_y)

    def handle_option_clicked(
        self, coord_arr: List, ind: int, sprite: PointerMenu = None
    ):
        self.tile_selector.image = resources.tile_selector_attack_animation
        self.tile_selector.batch = self.batch
        self.move_tile_selector_to_target(coord_arr, ind)
        self.option_menu_sprite.set_batch(None)
        if sprite:
            sprite.set_batch(self.batch)

    def end_turn(self):
        self.teams[self.current_team] = self.current_units
        self.get_next_team()

    def unit_was_moved(self):
        # reset
        if self.selected_unit:
            self.fresh_units.discard(self.selected_unit)
            self.selected_unit.character_moved()
        if len(self.fresh_units) == 0:
            self.end_turn()
        self.current_view = ViewState.NOTHING_SELECTED

    def update_carry_menu(self, coord_arr: List, ind: int, sprite: CarryActionWindow):
        tile_x, tile_y = coord_arr[ind]
        sprite.update_current_unit(self.selected_unit)
        sprite.update_target(self.tiles[tile_y][tile_x].character)

    def attack_option(self):
        self.option_menu_sprite.set_batch(None)
        self.weapon_menu_sprite.set_batch(self.batch)
        self.current_view = ViewState.WEAPON_SELECTION

    def staff_option(self):
        # TODO implement
        pass

    def rescue_option(self):
        self.current_view = ViewState.RESCUE_MENU
        self.selected_rescue = 0
        self.handle_option_clicked(
            self.rescue_in_range, self.selected_rescue, self.rescue_menu_sprite
        )
        self.update_carry_menu(self.rescue_in_range, 0, self.rescue_menu_sprite)

    def take_option(self):
        self.current_view = ViewState.TAKE_MENU
        self.selected_take = 0
        self.handle_option_clicked(
            self.take_in_range, self.selected_take, self.take_menu_sprite
        )
        self.update_carry_menu(self.take_in_range, 0, self.take_menu_sprite)

    def give_option(self):
        self.current_view = ViewState.GIVE_MENU
        self.selected_give = 0
        self.handle_option_clicked(
            self.give_in_range, self.selected_give, self.give_menu_sprite
        )
        self.update_carry_menu(self.give_in_range, 0, self.give_menu_sprite)

    def drop_option(self):
        self.current_view = ViewState.DROP_MENU
        self.selected_drop = 0
        self.handle_option_clicked(
            self.drop_in_range,
            self.selected_drop,  # self.drop_menu_sprite
        )

    def item_option(self):
        self.current_view = ViewState.INVENTORY_MENU
        self.option_menu_sprite.set_batch(None)
        self.inventory_menu_sprite.set_batch(self.batch)

    def trade_option(self):
        self.current_view = ViewState.TRADE_SELECTION
        self.selected_trade = 0
        self.handle_option_clicked(
            self.trade_in_range, self.selected_trade, self.trade_menu_sprite
        )

    def wait_option(self):
        self.option_menu_sprite.set_batch(None)
        self.tile_selector.batch = self.batch
        self.tile_selector.image = resources.tile_selector_animation
        self.unit_was_moved()
        reset_tiles(self.tiles)
        self.reset_after_select()

    def can_rescue(self):
        self.rescue_in_range = []
        if self.selected_unit.carried_unit:
            return False

        @four_direction_decorator
        def get_ally_neighbors(x, y):
            if x < 0 or x >= len(self.tiles[0]) or y < 0 or y >= len(self.tiles):
                return
            neighbor = self.tiles[y][x].character
            if not neighbor:
                return
            if self.selected_unit.team != neighbor.team:
                return
            aid = self.selected_unit.calc_aid()
            print(aid)
            if not neighbor.carried_unit and neighbor.stats.con <= aid:
                self.rescue_in_range.append((x, y))

        get_ally_neighbors(self.current_x, self.current_y)
        return len(self.rescue_in_range) > 0

    def can_take(self):
        self.take_in_range = []
        if self.selected_unit.carried_unit:
            return False

        @four_direction_decorator
        def get_carrying_neighbors(x, y):
            if x < 0 or x >= len(self.tiles[0]) or y < 0 or y >= len(self.tiles):
                return
            neighbor = self.tiles[y][x].character
            if not neighbor:
                return
            if self.selected_unit.team != neighbor.team:
                return
            aid = self.selected_unit.calc_aid()
            if neighbor.carried_unit and neighbor.carried_unit.stats.con <= aid:
                self.take_in_range.append((x, y))

        get_carrying_neighbors(self.current_x, self.current_y)
        return len(self.take_in_range) > 0

    def can_give(self):
        self.give_in_range = []
        if not self.selected_unit.carried_unit:
            return False

        @four_direction_decorator
        def get_free_neighbor(x, y):
            if x < 0 or x >= len(self.tiles[0]) or y < 0 or y >= len(self.tiles):
                return
            neighbor = self.tiles[y][x].character
            if not neighbor:
                return
            if self.selected_unit.team != neighbor.team:
                return
            aid = neighbor.calc_aid()
            if (
                not neighbor.carried_unit
                and self.selected_unit.carried_unit.stats.con <= aid
            ):
                self.give_in_range.append((x, y))

        get_free_neighbor(self.current_x, self.current_y)
        return len(self.give_in_range) > 0

    def can_drop(self):
        self.drop_in_range = []
        if not self.selected_unit.carried_unit:
            return False

        @four_direction_decorator
        def get_valid_squares(x, y):
            if x < 0 or x >= len(self.tiles[0]) or y < 0 or y >= len(self.tiles):
                return

            tile = self.tiles[y][x]
            # TODO see if I handle terrain the same way
            if (
                not tile.character
                and tile.tile_type
                in self.selected_unit.carried_unit.class_type.terrain_cost
            ):
                self.drop_in_range.append((x, y))

        get_valid_squares(self.current_x, self.current_y)
        return len(self.drop_in_range) > 0

    def can_trade(self):
        self.trade_in_range = []

        @four_direction_decorator
        def get_ally_neighbors(x, y):
            if x < 0 or x >= len(self.tiles[0]) or y < 0 or y >= len(self.tiles):
                return
            neighbor = self.tiles[y][x].character
            if neighbor is not None and self.selected_unit.team == neighbor.team:
                self.trade_in_range.append((x, y))

        get_ally_neighbors(self.current_x, self.current_y)
        return len(self.trade_in_range) > 0

    def get_options(self, can_attack: bool, can_staff: bool):
        # TODO implement can_staff
        options = []
        if can_attack:
            options.append(("Attack", self.attack_option))
        if can_staff:
            options.append(("Staff", self.staff_option))
        if self.can_rescue():
            options.append(("Rescue", self.rescue_option))
        if self.can_take():
            options.append(("Take", self.take_option))
        if self.can_give():
            options.append(("Give", self.give_option))
        if self.can_drop():
            options.append(("Drop", self.drop_option))
        options.append(("Item", self.item_option))
        if self.can_trade():
            options.append(("Trade", self.trade_option))
        options.append(("Wait", self.wait_option))
        return options

    # TODO change type hint to base class once its created
    def reset_to_option_menu(self, prev_menu: PointerMenu = None):
        self.tile_selector.batch = None
        if prev_menu:
            prev_menu.set_batch(None)
        self.option_menu_sprite.set_batch(self.batch)
        self.current_view = ViewState.OPTION_MENU

    def action_complete(self, carried_unit: Character, prev_menu: PointerMenu = None):
        if prev_menu:
            prev_menu.set_batch(None)
        carried_unit.character_moved()
        self.tile_selector.image = resources.tile_selector_animation
        self.move_tile_selector(self.selected_x, self.selected_y)
        self.current_x, self.current_y = self.selected_x, self.selected_y
        # TODO consider reset after select
        # do i NEED to reset these variables given the new viewstate architecture?
        self.selected_unit = None

    def handle_drop(self, dropped_unit: Character, dest_x: int, dest_y: int):
        self.tiles[dest_y][dest_x].set_character(dropped_unit)
        dropped_unit.is_carried = False
        dropped_unit.character_moved()

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)

        if self.current_view == ViewState.NOTHING_SELECTED:
            if symbol == key.E:
                character = self.tiles[self.current_y][self.current_x].character

                if character and character in self.fresh_units:
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

                    self.draw_unit_movement()
                    self.current_view = ViewState.MOVEMENT
                else:
                    self.turn_menu_sprite.set_batch(self.batch)
                    self.current_view = ViewState.TURN_MENU

        elif self.current_view == ViewState.TURN_MENU:
            if symbol == key.E:
                # TODO this is currently the end turn functionality
                self.end_turn()
                self.turn_menu_sprite.set_batch(None)
                self.current_view = ViewState.NOTHING_SELECTED
            elif symbol == key.Q:
                self.turn_menu_sprite.set_batch(None)
                self.current_view = ViewState.NOTHING_SELECTED

        elif self.current_view == ViewState.MOVEMENT:
            if symbol == key.E:
                # TODO reimplement camera reset to only be on movement view
                if self.current_moves[self.current_y][self.current_x] > 0 and (
                    self.tiles[self.current_y][self.current_x].character is None
                    or self.tiles[self.current_y][self.current_x].character
                    is self.selected_unit
                ):

                    self.tiles[self.selected_starting_y][
                        self.selected_starting_x
                    ].character = None

                    # move selected character
                    self.tiles[self.current_y][self.current_x].set_character(
                        self.selected_unit
                    )

                    # updates current character coordinates
                    self.selected_x, self.selected_y = self.current_x, self.current_y

                    # fill in red attack squares
                    reset_tiles(self.tiles)

                    weapon_range = self.selected_unit.get_weapon_range()

                    # TODO implement searching for enemies in range with multiple weapons
                    self.enemies_in_range = find_enemies_in_range(
                        self.selected_unit,
                        self.tiles,
                        self.current_x,
                        self.current_y,
                        weapon_range.min_range,
                        weapon_range.max_range,
                    )
                    if not self.enemies_in_range:
                        # remove coloring if no enemies in range
                        reset_tiles(self.tiles)
                    options = self.get_options(self.enemies_in_range, False)
                    self.option_menu_sprite.set_options(options)
                    self.option_menu_sprite.set_batch(self.batch)
                    self.tile_selector.batch = None
                    self.current_view = ViewState.OPTION_MENU
            elif symbol == key.Q:
                self.reset_camera()
                # move selector to original square
                self.current_x, self.current_y = (
                    self.selected_starting_x,
                    self.selected_starting_y,
                )

                self.move_tile_selector(self.current_x, self.current_y)

                self.reset_after_select()

                # removes markings from tiles
                reset_tiles(self.tiles)

                self.current_view = ViewState.NOTHING_SELECTED

        elif self.current_view == ViewState.OPTION_MENU:
            if symbol == key.E:
                self.option_menu_sprite.execute_option()
            elif symbol == key.Q:
                self.reset_to_movement()
            elif symbol == key.UP:
                self.option_menu_sprite.move_pointer(-1)
            elif symbol == key.DOWN:
                self.option_menu_sprite.move_pointer(1)

        elif self.current_view == ViewState.RESCUE_MENU:
            if symbol == key.E:
                ally_x, ally_y = self.rescue_in_range[self.selected_rescue]
                tile = self.tiles[ally_y][ally_x]
                neighbor = tile.character
                self.selected_unit.carry_unit(neighbor)
                neighbor.batch = None
                tile.character = None
                # TODO handle canto
                self.fresh_units.discard(neighbor)
                self.unit_was_moved()

                self.action_complete(neighbor, self.rescue_menu_sprite)

            elif symbol == key.Q:
                self.reset_to_option_menu(self.rescue_menu_sprite)

        elif self.current_view == ViewState.TAKE_MENU:
            if symbol == key.E:
                ally_x, ally_y = self.take_in_range[self.selected_take]
                neighbor = self.tiles[ally_y][ally_x].character
                self.selected_unit.carry_unit(neighbor.carried_unit)
                neighbor.carried_unit = None
                self.unit_was_moved()

                self.action_complete(
                    self.selected_unit.carried_unit, self.take_menu_sprite
                )
            elif symbol == key.Q:
                self.reset_to_option_menu(self.take_menu_sprite)

        elif self.current_view == ViewState.GIVE_MENU:
            if symbol == key.E:
                ally_x, ally_y = self.give_in_range[self.selected_give]
                neighbor = self.tiles[ally_y][ally_x].character
                neighbor.carry_unit(self.selected_unit.carried_unit)
                self.selected_unit.carried_unit = None
                self.unit_was_moved()

                self.action_complete(neighbor.carried_unit, self.give_menu_sprite)
            elif symbol == key.Q:
                self.reset_to_option_menu(self.give_menu_sprite)

        elif self.current_view == ViewState.DROP_MENU:
            if symbol == key.E:
                tile_x, tile_y = self.drop_in_range[self.selected_drop]
                dropped_unit = self.selected_unit.carried_unit
                self.handle_drop(dropped_unit, tile_x, tile_y)
                self.selected_unit.carried_unit = None
                self.unit_was_moved()

                # TODO figure out how to handle drop menu
                self.action_complete(dropped_unit)
            elif symbol == key.Q:
                self.reset_to_option_menu()

        elif self.current_view == ViewState.TRADE_SELECTION:
            if symbol == key.E:
                pass
            elif symbol == key.Q:
                pass

        elif self.current_view == ViewState.TRADE_SELECTED:
            if symbol == key.E:
                pass
            elif symbol == key.Q:
                pass

        elif self.current_view == ViewState.WEAPON_SELECTION:
            if symbol == key.E:

                self.tile_selector.image = resources.tile_selector_attack_animation
                self.tile_selector.batch = self.batch
                self.selected_enemy = 0
                self.move_tile_selector_to_enemy()

                self.weapon_menu_sprite.set_batch(None)
                self.forecast_menu_sprite.set_batch(self.batch)
                self.get_combat_forecast()

                # TODO add changing equipped weapon
                self.current_view = ViewState.ATTACK_SELECTION
            elif symbol == key.Q:
                self.weapon_menu_sprite.set_batch(None)
                self.current_view = ViewState.OPTION_MENU

        elif self.current_view == ViewState.ATTACK_SELECTION:
            if symbol == key.E:
                # TODO-add terrain bonuses

                self.forecast_menu_sprite.set_batch(None)

                enemy_x, enemy_y, can_counter = self.enemies_in_range[
                    self.selected_enemy
                ]
                enemy = self.tiles[enemy_y][enemy_x].character

                if BattleScreen.perform_attack(self.selected_unit, enemy):
                    self.teams[enemy.team].remove(enemy)
                    self.tiles[enemy_y][enemy_x].character = None
                    if enemy.carried_unit:
                        self.handle_drop(enemy.carried_unit, enemy_x, enemy_y)
                    enemy.delete()
                elif can_counter and BattleScreen.perform_attack(
                    enemy, self.selected_unit
                ):
                    self.current_units.remove(self.selected_unit)
                    self.fresh_units.remove(self.selected_unit)
                    self.tiles[self.current_y][self.current_x].character = None
                    if self.selected_unit.carried_unit:
                        self.handle_drop(
                            self.selected_unit.carried_unit,
                            self.current_x,
                            self.current_y,
                        )
                    self.selected_unit.delete()

                self.tile_selector.image = resources.tile_selector_animation
                self.move_tile_selector(
                    self.current_x,
                    self.current_y,
                )

                # reset
                self.unit_was_moved()

                reset_tiles(self.tiles)
                self.reset_after_select()
            elif symbol == key.Q:
                # TODO implement this
                self.tile_selector.batch = None
                self.weapon_menu_sprite.set_batch(self.batch)
                self.forecast_menu_sprite.set_batch(None)

                self.current_view = ViewState.WEAPON_SELECTION
        print(self.current_view)
        return

    def draw(self):
        self.batch.draw()

    def carry_action_update(self, coord_arr: List, ind: int, sprite: CarryActionWindow):
        tile_x, tile_y = coord_arr[ind]
        self.move_tile_selector(tile_x, tile_y)
        sprite.update_target(self.tiles[tile_y][tile_x].character)

    def update(self):
        self.option_menu_sprite.run_pointer_animation()
        if self.current_view in no_scroll_viewstates:
            return
        options = (key.RIGHT, key.LEFT, key.UP, key.DOWN)
        change_x = 0
        change_y = 0
        for option in options:
            if self[option]:
                change = arrow_key_dict[option]
                change_x += change[0]
                change_y += change[1]

        if change_x == 0 and change_y == 0:
            return

        for option in options:
            if self[option]:
                self.camera_bounds(option)

        if self.current_view not in fixed_scroll_viewstates:
            self.current_x = self.clamp(self.tiles[0], self.current_x + change_x)
            self.current_y = self.clamp(self.tiles, self.current_y + change_y)
            self.move_tile_selector(self.current_x, self.current_y)
            # draws path if not attacking and unit is selected
            if self.current_view == ViewState.MOVEMENT:
                if self.current_moves[self.current_y][self.current_x] > 0:
                    reset_tiles(self.tiles)
                    weapon_range = self.selected_unit.get_weapon_range()
                    color_tiles(
                        self.tiles,
                        self.current_moves,
                        weapon_range.min_range,
                        weapon_range.max_range,
                    )
                    draw_path(
                        self.tiles,
                        self.path_finder(
                            self.current_x, self.current_y, self.current_moves
                        ),
                    )
        else:
            scroll_direction = change_x + change_y
            scroll_direction /= abs(scroll_direction)
            scroll_direction = int(scroll_direction)

            if self.current_view == ViewState.ATTACK_SELECTION:
                num_enemies = len(self.enemies_in_range)
                self.selected_enemy = (
                    self.selected_enemy + scroll_direction + num_enemies
                ) % num_enemies

                self.move_tile_selector_to_enemy()

                self.get_combat_forecast()
            elif self.current_view == ViewState.RESCUE_MENU:
                num_rescue = len(self.rescue_in_range)
                self.selected_rescue = (
                    self.selected_rescue + scroll_direction + num_rescue
                ) % num_rescue

                self.carry_action_update(
                    self.rescue_in_range, self.selected_rescue, self.rescue_menu_sprite
                )
            elif self.current_view == ViewState.GIVE_MENU:
                num_give = len(self.give_in_range)
                self.selected_give = (
                    self.selected_give + scroll_direction + num_give
                ) % num_give

                self.carry_action_update(
                    self.give_in_range, self.selected_give, self.give_menu_sprite
                )
            elif self.current_view == ViewState.TAKE_MENU:
                num_take = len(self.take_in_range)
                self.selected_take = (
                    self.selected_take + scroll_direction + num_take
                ) % num_take

                self.carry_action_update(
                    self.take_in_range, self.selected_take, self.take_menu_sprite
                )
            elif self.current_view == ViewState.DROP_MENU:
                num_drop = len(self.drop_in_range)
                self.selected_drop = (
                    self.selected_drop + scroll_direction + num_drop
                ) % num_drop

                self.move_tile_selector_to_target(
                    self.drop_in_range, self.selected_drop
                )
