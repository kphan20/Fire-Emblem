import pyglet
from pyglet.libs.win32.constants import INFINITE
from pyglet.window import key
from game import resources
from game.units import *
import utils
import math

CONTINUOUS_ARROWS = True
BORDERS = False
map_string = './test_files/test (1).txt'
#Make config object for window
# pyglet.options['search_local_libs'] = True
source = resources.source
source.play()

class StartingScreen(pyglet.sprite.Sprite):
    def __init__(self, img):
        super().__init__(img=img)
class StartingMenu(pyglet.sprite.Sprite):
    def __init__(self):
        super().__init__(img=resources.animation)

def four_direction_decorator(func):
    """Convenience decorator for algorithms requiring searching in four directions"""
    def wrapper(x, y, *args, **kwargs):
        returned_values = [
        func(x + 1, y, *args, **kwargs),
        func(x - 1, y, *args, **kwargs),
        func(x, y + 1, *args, **kwargs),
        func(x, y - 1, *args, **kwargs)]
        return returned_values
    return wrapper

class Window(pyglet.window.Window):
    def __init__(self, map):
        super().__init__(fullscreen=True)#width=500, height=500)
        # Used to resize starting screen image
        starting_image = resources.starting_screen
        starting_image.width, starting_image.height = self.get_size()
        
        # screen width and height in terms of complete tiles
        self.screen_tile_width = starting_image.width // (utils.TILE_SCALE * utils.TILE_SIZE)
        self.screen_tile_height = starting_image.height // (utils.TILE_SCALE * utils.TILE_SIZE)
        if BORDERS:
            tile_size = utils.TILE_SIZE * utils.TILE_SCALE
            self.set_fullscreen(width=self.screen_tile_width * tile_size, height=self.screen_tile_height * tile_size)
        self.current_screen = None# StartingScreen(img=starting_image)
        
        # Batch all sprites that need to be drawn
        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        self.tiles = utils.test_generate_map_tiles(map, self.batch, self.background, self.screen_tile_width, self.screen_tile_height)
        #self.tiles=utils.generate_map_tiles(map['width'], map['height'], self.batch, self.background, self.screen_tile_width, self.screen_tile_height)

        # Represents position of cursor; in some cases, represents original position of unit
        self.current_x= 0
        self.current_y = 0
        
        self.previous_color = None
        # These will hold the coordinates of the bottom left corner of the screen
        # Will be used for camera movement calculations
        self.starting_x = self.current_x
        self.starting_y = self.current_y
        
        # Will potentially be used to hold all characters on the map
        #self.characters = []
        
        # Testing characters
        self.test_character = Character(resources.player_image, self.batch, self.foreground)
        self.test_character2 = Character(resources.player_image, self.batch, self.foreground, 1)
        self.test_character3 = Character(resources.player_image, self.batch, self.foreground, 1)
        self.tiles[self.current_x][self.current_y].set_character(self.test_character)
        # self.tiles[5][4].set_character(self.test_character2)
        # self.tiles[0][4].set_character(self.test_character3)
        
        # Used for when a character is selecting attacks
        self.attack_view = None
        self.available_enemies = []
        # Denotes units that are currently being viewed/moved
        self.selected_unit = None # Actual reference to Character object
        self.selected_enemy = None # Make this an index of available_enemies
        # Stores available moves for selected unit
        self.current_moves = None
        
        # Used for move/attack selection
        self.selected_x = 0
        self.selected_y = 0
        
        self.key_handler = key.KeyStateHandler()
    def generate_empty_array(self):
        """Generates empty 2D array for movement/attack range calculations

        Returns:
            list[list[int]]: 2D array filled with zeroes and is as big as the tilemap
        """
        tile_arr = self.tiles
        width = len(tile_arr[0])
        height = len(tile_arr)
        return [[0 for x in range(width)] for x in range(height)]
    
    def reset_tiles(self):
        """Changes all the tiles on the tilemap back to normal colors
        """
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                self.tiles[y][x].change_tint(utils.NORMAL_TINT)
                
    def remove_tiles_from_batch(self, tile_arr):
        """Removes tiles from batch as camera moves

        Args:
            tile_arr (list[Tile]): References to tiles that have gotten out of frame
        """
        for tile in tile_arr:
            tile.batch = None
            if tile.character:
                tile.character.batch = None
                
    def add_tiles_to_batch(self, tile_arr):
        """Adds tiles to batch as camera moves

        Args:
            tile_arr (list[Tile]): References to tiles that just entered frame
        """
        for tile in tile_arr:
            tile.batch = self.batch
            if tile.character:
                tile.character.batch = self.batch
    
    def bounds(self, list, index):
        """Checks if a coordinate is within the boundaries of the tilemap

        Args:
            list (list): List denoting the tilemap column/row being used for camera boundaries
            index (int): Position value being examined

        Returns:
            int: Either the bounds values or the unchanged index value
        """
        if index == len(list):
            return index - 1
        if index < 0:
            return 0
        return index
    
    def fill_attacks(self, current_x, current_y, attack_range, filler):
        """Depth first search to fill in a unit's attack range

        Args:
            current_x (int): Current x coordinate being searched
            current_y (int): Current y coordinate being searched
            attack_range (int): Attack range remaining on search
            filler (list[list[int]]): Keeps track of results
        """
        if attack_range <= 0 or current_x < 0 or current_x >= len(filler[0]) or current_y < 0 or current_y >= len(filler):
            return
        # Negative squares denote attack squares at border of movement range
        # Checks if the value on the square is greater than the remaining attack range before continuing search
        if filler[current_y][current_x] <= 0 and filler[current_y][current_x] > -attack_range:
            filler[current_y][current_x] = -attack_range
            self.fill_attacks(current_x + 1, current_y, attack_range - 1, filler)
            self.fill_attacks(current_x - 1, current_y, attack_range - 1, filler)
            self.fill_attacks(current_x, current_y + 1, attack_range - 1, filler)
            self.fill_attacks(current_x, current_y - 1, attack_range - 1, filler)
    
    def move_finder(self, current_x, current_y, max_move, attack_range):
        """Depth first search to fill in a unit's movement range

        Args:
            current_x (int): Current x coordinate being searched
            current_y (int): Current y coordinate being searched
            max_move (int): Movement remaining from current square
            attack_range (int): Unit's attack range

        Returns:
            list[list[int]]: 2D array with positive numbers denoting movement range, negative numbers denoting attack range,
            and zero for tiles that are in neither
        """
        #assuming rectangular map
        tile_arr = self.tiles
        filler = self.generate_empty_array()
        terrain_cost = self.selected_unit.class_type.terrain_cost
        # Sets first square to large value to prevent backtracking to start square
        max_move += 1
        filler[current_y][current_x] = max_move
        @four_direction_decorator
        def fill_move(current_x, current_y, max_move, filler):
            if current_x < 0 or current_x >= len(filler[0]) or current_y < 0 or current_y >= len(filler):
                return
            # Prevents unit from moving past another unit on a different team
            if tile_arr[current_y][current_x].character and tile_arr[current_y][current_x].character.team != tile_arr[self.selected_y][self.selected_x].character.team:
                max_move = 0
            else:
                # If no unit or same team unit, then calculate move normally
                move_cost = terrain_cost[tile_arr[current_y][current_x].tile_type]
                max_move = max_move - move_cost
            # Prevents backtracking to squares pointlessly
            if filler[current_y][current_x] >= max_move and filler[current_y][current_x] > 0:
                return
            if max_move > 0:
                filler[current_y][current_x] = max_move
                fill_move(current_x, current_y, max_move, filler)
            else:
                # Finds attack range if unit cannot move any further
                self.fill_attacks(current_x, current_y, attack_range, filler)
                return
        fill_move(current_x, current_y, max_move, filler)
        return filler

    def color_tiles(self, filler):
        """Changes the color of the map tiles when a unit is selected

        Args:
            filler (list[list[int]]): 2D array holding valid movement/attack squares
        """
        width = len(filler[0])
        for y in range(len(filler)):
            for x in range(width):
                tile = filler[y][x]
                if tile > 0:
                    self.tiles[y][x].change_tint(utils.BLUE_TINT)
                elif tile < 0:
                    self.tiles[y][x].change_tint(utils.RED_TINT)

    def color_attack_tiles(self, attack_range):
        """Shows a unit's attack range after they have moved

        Args:
            attack_range (int): The selected unit's attack range

        Returns:
            [list[list[int]]]: 2D array with attack squares
        """
        filler = self.generate_empty_array()
        self.fill_attacks(self.current_x, self.current_y, attack_range + 1, filler) # change this to current
        self.color_tiles(filler)
        return filler
    
    def find_enemies_in_range(self, filler):
        """Finds the targetable enemies within the selected unit's attack range

        Args:
            filler (list[list[int]]): Holds the selected unit's attack range
        """
        current_team = self.selected_unit.team
        for y in range(len(filler)):
            for x in range(len(filler[0])):
                tile = filler[y][x]
                if tile < 0:
                    enemy_check = self.tiles[y][x].character
                    if enemy_check and enemy_check.team != current_team:
                        self.available_enemies.append((x, y))
        if self.available_enemies:
            self.selected_enemy = 0
        
    def path_finder(self, destination_x, destination_y, filler):
        """Finds the path from the selected unit's current location to a destination point

        Args:
            destination_x (int): Destination x coordinate
            destination_y (int): Destination y coordinate
            filler (list[list[int]]): Contains unit's movement range

        Returns:
            list | string: List of tuples with coordinates of path or a string denoting an invalid path
        """
        # Used to retrieve the coordinates of the tiles in the path
        coord_dict = {0: lambda x, y: (x + 1, y),
                      1: lambda x, y: (x - 1, y),
                      2: lambda x, y: (x, y + 1),
                      3: lambda x, y: (x, y - 1)}
        @four_direction_decorator
        def check(x_coor, y_coor):
            if x_coor < 0 or x_coor > len(filler[0]) - 1 or y_coor < 0 or y_coor > len(filler) - 1:
                return -1
            return filler[y_coor][x_coor]
        if filler[destination_y][destination_x] > 0:
            # Starts from destination and backtracks by following the path with the greatest values
            x_coordinate, y_coordinate = destination_x, destination_y
            path = []
            path.append((x_coordinate, y_coordinate))
            while x_coordinate != self.selected_x or y_coordinate != self.selected_y:
                # Checks right, left, up, and down tiles for their values
                tile_values = check(x_coordinate, y_coordinate)
                # Retrieves largest value and retrieves its tile coordinates
                new_coordinates = coord_dict[tile_values.index(max(tile_values))](x_coordinate, y_coordinate)
                path.append(new_coordinates[:])
                x_coordinate, y_coordinate = new_coordinates
            path.reverse()
            return path
        return "outside of range"
    
    def draw_path(self, path):
        """Changes tile colors in path to green

        Args:
            path (list): List containing path coordinates
        """
        for point in path:
            self.tiles[point[1]][point[0]].change_tint(utils.GREEN_TINT)
            
    def path_testing(self):
        self.reset_tiles()
        self.draw_range(self.test_character)
        path = self.path_finder(self.current_x, self.current_y, self.current_moves) # change this to current
        if type(path) != str: # add bounds conditions
            self.draw_path(path)
            
    def reset_unit(self):
        """Used to reset class variables after unit selection
        """
        self.selected_unit = None
        self.attack_view = None
        self.selected_enemy = None
        self.available_enemies = []

    def testing(self):
        print ('Step')
        print(self.current_x, self.current_y)
        print(self.starting_x, self.starting_y)
        
    def shift_tiles(self):
        """Redraws tiles after camera pan"""
        offset_x = 0
        offset_y = 0
        for y in range(self.screen_tile_height + 1):
            for x in range(self.screen_tile_width + 1):
                self.tiles[y + self.starting_y][x + self.starting_x].shift_tile(offset_x, offset_y)
                offset_x += utils.TILE_SIZE * utils.TILE_SCALE
            offset_x = 0
            offset_y += utils.TILE_SIZE * utils.TILE_SCALE
            
    def camera_bounds(self, direction):
        """Redraws visible tiles depending on camera pan direction

        Args:
            direction (int): Constant correlating to pyglet key constants
        """
        camera_x_position = self.current_x - self.starting_x
        camera_y_position = self.current_y - self.starting_y
        if direction == key.LEFT:
            left_edge_check = self.starting_x == 0
            if not left_edge_check and camera_x_position <= 1:# or camera_y_position == 1 or camera_y_position == self.screen_tile_height:
                #self.current_x -= 1
                self.starting_x -= 1
                # remove tiles that were previously on the edge of the screen
                self.remove_tiles_from_batch([tiles[self.starting_x + self.screen_tile_width + 1] for tiles in self.tiles])
                # add tiles that were previously to the left of the starting point (current x column due to decrement)
                self.add_tiles_to_batch([tiles[self.starting_x] for tiles in self.tiles])
                self.shift_tiles()
        elif direction == key.RIGHT:
            right_edge_check = self.current_x == len(self.tiles[0]) - 2
            if not right_edge_check and camera_x_position >= self.screen_tile_width - 1:
                #self.current_x += 1
                edge_check = len(self.tiles[0]) - 1
                if self.starting_x + self.screen_tile_width < edge_check:
                    self.starting_x += 1
                if self.starting_x + self.screen_tile_width <= edge_check:
                    # remove original starting column
                    self.remove_tiles_from_batch([tiles[self.starting_x - 1] for tiles in self.tiles])
                    # add column just beyond previous edge of the screen
                    self.add_tiles_to_batch([tiles[self.starting_x + self.screen_tile_width] for tiles in self.tiles])
                    self.shift_tiles()
        elif direction == key.UP:
            upper_edge_check = self.starting_y == len(self.tiles) - 2
            if not upper_edge_check and camera_y_position >= self.screen_tile_height - 1:
                #self.current_y += 1
                edge_check = len(self.tiles) - 1
                if self.starting_y + self.screen_tile_height < edge_check:
                    self.starting_y += 1
                if self.starting_y + self.screen_tile_height <= edge_check:
                    #self.starting_y += 1
                    self.remove_tiles_from_batch([tile for tile in self.tiles[self.starting_y - 1]])
                    self.add_tiles_to_batch([tile for tile in self.tiles[self.starting_y + self.screen_tile_height]])
                    self.shift_tiles()
        elif direction == key.DOWN:
            bottom_edge_check = self.starting_y == 0
            if not bottom_edge_check and camera_y_position <= 1:# or camera_y_position == 1 or camera_y_position == self.screen_tile_height:
                #self.current_y -= 1
                self.starting_y -= 1
                self.remove_tiles_from_batch([tile for tile in self.tiles[self.starting_y + self.screen_tile_height + 1]])
                self.add_tiles_to_batch([tile for tile in self.tiles[self.starting_y]])
                self.shift_tiles()
                   
    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        self.testing()
        arrow_key_dict = {key.RIGHT: lambda x, y: (x + 1, y),
                key.LEFT: lambda x, y: (x - 1, y),
                key.UP: lambda x, y: (x, y + 1),
                key.DOWN: lambda x, y: (x, y - 1)}
        if self.current_screen:
            if symbol==key.E:
                if isinstance(self.current_screen, StartingScreen):
                    self.current_screen=StartingMenu()
                    return
                if isinstance(self.current_screen, StartingMenu):
                    self.current_screen=None#Tile(img=resources.tile, x=100,y=100, batch=self.batch)#TileScreen(self.batch)
        else:
            # Using E as the selection button
            if symbol==key.E:
                # Handles selection outside of character focus
                if not self.selected_unit:
                    character = self.tiles[self.current_y][self.current_x].character
                    # If selecting a square with a character, show that characters movement range and focuses on that unit
                    if character:
                        self.selected_x, self.selected_y = self.current_x, self.current_y
                        self.selected_unit = character
                        self.current_moves = self.draw_range(character)
                        
                # Handles selection when a unit if being focused on
                else:
                    # Handles behavior if focused character has moved and can attack
                    if self.attack_view:
                        # Attack
                        if self.selected_enemy is not None:
                            attack = self.selected_unit.attack_power(5)
                            enemy_x, enemy_y = self.available_enemies[self.selected_enemy]
                            enemy = self.tiles[enemy_y][enemy_x].character
                            if attack > enemy.stats.hp:
                                self.tiles[enemy_y][enemy_x].character = None
                                enemy.delete()
                        # For testing purposes
                        self.reset_tiles()
                        #self.current_x, self.current_y = self.selected_x, self.selected_y # deletion
                        self.reset_unit()
                        self.tiles[self.current_y][self.current_x].change_tint(utils.GREEN_TINT)
                        return
                    # Handles actual movement of character
                    if self.current_moves[self.current_y][self.current_x] > 0 and self.tiles[self.current_y][self.current_x].character is None: # change to current
                        self.tiles[self.selected_y][self.selected_x].character= None
                        self.tiles[self.current_y][self.current_x].set_character(self.selected_unit)  # changes these two lines around 
                        #self.selected_unit = None
                        #self.current_x, self.current_y = self.selected_x, self.selected_y
                        self.reset_tiles()
                        self.attack_view = self.color_attack_tiles(1)
                        self.find_enemies_in_range(self.attack_view)
                        if self.available_enemies:
                            enemy_x, enemy_y = self.available_enemies[0]
                            self.tiles[enemy_y][enemy_x].change_tint(utils.GREEN_TINT)
                        return
                return
            if symbol == key.Q:
                if self.selected_unit:                    
                    #self.tiles[self.selected_y][self.selected_x].character = None # Going to have to make this set selected to none
                    #self.selected_x, self.selected_y = self.current_x, self.current_y # set current to selected
                    self.tiles[self.current_y][self.current_x].character = None
                    self.current_x, self.current_y = self.selected_x, self.selected_y
                    self.tiles[self.selected_y][self.selected_x].set_character(self.selected_unit)
                    self.selected_x = None
                    self.selected_y = None
                    self.reset_unit()
                self.reset_tiles()
                self.tiles[self.current_y][self.current_x].change_tint(utils.GREEN_TINT)
                return
            if arrow_key_dict.get(symbol):
                if self.selected_unit:
                    if self.attack_view:
                        if self.available_enemies:
                            self.color_attack_tiles(1)
                            # Use scroll_direction to calculate index in self.available_enemies
                            scroll_direction = sum(arrow_key_dict[symbol](0, 0))
                            self.selected_enemy += scroll_direction
                            length_check = len(self.available_enemies)
                            if self.selected_enemy == len(self.available_enemies):
                                self.selected_enemy = 0
                            elif self.selected_enemy == -(length_check + 1):
                                self.selected_enemy = length_check - 1
                            enemy_x, enemy_y = self.available_enemies[self.selected_enemy]
                            self.tiles[enemy_y][enemy_x].change_tint(utils.GREEN_TINT)
                        return # could use else instead; prevents path finding behavior when attacking enemy
                    #self.selected_x, self.selected_y = arrow_key_dict[symbol](self.selected_x, self.selected_y) # change this to current
                    if not CONTINUOUS_ARROWS:
                        if self.previous_color:
                            self.tiles[self.current_y][self.current_x].change_tint(self.previous_color)
                        if not CONTINUOUS_ARROWS:
                            self.current_x, self.current_y = arrow_key_dict[symbol](self.current_x, self.current_y)
                        if self.current_moves[self.current_y][self.current_x] > 0:
                            self.previous_color = None
                            self.path_testing() # going to have to implement different logic to check for bounds of camera
                        else:
                            current_tile = self.tiles[self.current_y][self.current_x]
                            self.previous_color = current_tile.color
                            current_tile.change_tint(utils.GREEN_TINT)
                else:
                    self.reset_tiles()
                    if not CONTINUOUS_ARROWS:
                        self.current_x, self.current_y = arrow_key_dict[symbol](self.current_x, self.current_y)
                self.camera_bounds(symbol)
                self.current_y = self.bounds(self.tiles, self.current_y)
                self.current_x = self.bounds(self.tiles[self.current_y], self.current_x)
                self.tiles[self.current_y][self.current_x].change_tint(utils.GREEN_TINT)
                return
    def draw_range(self, character):
        moves = self.move_finder(self.selected_x, self.selected_y, 8, 1)
        self.color_tiles(moves)
        return moves
    
    def on_draw(self):
        self.clear()
        #self.batch.draw()
        if self.current_screen:
            self.current_screen.draw()
        else:
            self.batch.draw()
        #self.test.draw()
    def check_arrow_keys(self, _):
        options = [key.RIGHT, key.LEFT, key.UP, key.DOWN]
        arrow_key_dict = {key.RIGHT: lambda x, y: (x + 1, y),
                key.LEFT: lambda x, y: (x - 1, y),
                key.UP: lambda x, y: (x, y + 1),
                key.DOWN: lambda x, y: (x, y - 1)}
        change_x = 0
        change_y = 0
        for option in options:
            if self.key_handler[option]:
                change = arrow_key_dict[option](0, 0)
                change_x += change[0]
                change_y += change[1]
        # if not self.previous_color:
        #     self.tiles[self.current_y][self.current_x].change_tint(utils.NORMAL_TINT)
        # else:
        #     self.tiles[self.current_y][self.current_x].change_tint(self.previous_color)
        current_tile = self.tiles[self.current_y][self.current_x]
        self.current_x += change_x
        self.current_y += change_y
        for option in options:
            if self.key_handler[option]:
                self.camera_bounds(option)
        self.current_x = self.bounds(self.tiles[0], self.current_x)
        self.current_y = self.bounds(self.tiles, self.current_y)
        if self.selected_unit:
            if self.previous_color:
               current_tile.change_tint(self.previous_color)
            if self.current_moves[self.current_y][self.current_x] > 0:
                self.previous_color = None
                self.path_testing()
            else:
                current_tile = self.tiles[self.current_y][self.current_x]
                self.previous_color = current_tile.color
                current_tile.change_tint(utils.GREEN_TINT)
        else:
            current_tile.change_tint(utils.NORMAL_TINT)

        #self.reset_tiles()
            self.tiles[self.current_y][self.current_x].change_tint(utils.GREEN_TINT)

if __name__ == '__main__':
    window = Window(map_string)
    if CONTINUOUS_ARROWS:
        window.push_handlers(window.key_handler)
        pyglet.clock.schedule_interval(window.check_arrow_keys, 1/10)
    pyglet.app.run()

