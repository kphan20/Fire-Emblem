import pyglet
from pyglet.libs.win32.constants import INFINITE
from pyglet.window import key
from game import resources
from game.units import *
import utils
import math

CONTINUOUS_ARROWS = False
BORDERS = False
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
    """Convenienve decorator for algorithms requiring searching in four directions"""
    def wrapper(x, y, *args, **kwargs):
        returned_values = [
        func(x + 1, y, *args, **kwargs),
        func(x - 1, y, *args, **kwargs),
        func(x, y + 1, *args, **kwargs),
        func(x, y - 1, *args, **kwargs)]
        return returned_values
    return wrapper

class Window(pyglet.window.Window):
    def __init__(self):
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
        self.tiles=utils.generate_map_tiles(self.batch, self.background, self.screen_tile_width, self.screen_tile_height)

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
        self.tiles[5][4].set_character(self.test_character2)
        self.tiles[0][4].set_character(self.test_character3)
        
        # Used for when a character is selecting attacks
        self.attack_view = None
        self.available_enemies = []
        # Denotes units that are currently being viewed/moved
        self.selected_unit = None
        self.selected_enemy = None # Make this an index of available_enemies
        # Stores available moves for selected unit
        self.current_moves = None
        
        # Used for move/attack selection
        self.selected_x = 0
        self.selected_y = 0
        
        self.key_handler = key.KeyStateHandler()
    def remove_tiles_from_batch(self, tile_arr):
        for tile in tile_arr:
            tile.batch = None
            if tile.character:
                tile.character.batch = None
    def add_tiles_to_batch(self, tile_arr):
        for tile in tile_arr:
            tile.batch = self.batch
            if tile.character:
                tile.character.batch = self.batch
    def generate_empty_array(self):
        tile_arr = self.tiles
        width = len(tile_arr[0])
        height = len(tile_arr)
        return [[0 for x in range(width)] for x in range(height)]
    
    def reset_tiles(self):
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                self.tiles[y][x].change_tint(utils.NORMAL_TINT)
    
    def fill_attacks(self, current_x, current_y, attack_range, filler):
            if attack_range <= 0 or current_x < 0 or current_x >= len(filler[0]) or current_y < 0 or current_y >= len(filler):
                return
            if filler[current_y][current_x] <= 0 and filler[current_y][current_x] > -attack_range:
                filler[current_y][current_x] = -attack_range
                self.fill_attacks(current_x + 1, current_y, attack_range - 1, filler)
                self.fill_attacks(current_x - 1, current_y, attack_range - 1, filler)
                self.fill_attacks(current_x, current_y + 1, attack_range - 1, filler)
                self.fill_attacks(current_x, current_y - 1, attack_range - 1, filler)
    
    def move_finder(self, current_x, current_y, max_move, attack_range):
        #assuming rectangular map
        tile_arr = self.tiles
        filler = self.generate_empty_array()
        terrain_cost = self.test_character.class_type.terrain_cost
        # Sets first square to large value to prevent backtracking to start square
        max_move += 1
        filler[current_y][current_x] = max_move
        @four_direction_decorator
        def fill_move(current_x, current_y, max_move, filler):
            if current_x < 0 or current_x >= len(filler[0]) or current_y < 0 or current_y >= len(filler):
                return
            if tile_arr[current_y][current_x].character and tile_arr[current_y][current_x].character.team != 0:
                max_move = 0
            else:
                move_cost = terrain_cost[tile_arr[current_y][current_x].tile_type]
                max_move = max_move - move_cost
            if filler[current_y][current_x] >= max_move and filler[current_y][current_x] > 0:
                return
            if max_move > 0:
                filler[current_y][current_x] = max_move
                fill_move(current_x, current_y, max_move, filler)
            else:
                self.fill_attacks(current_x, current_y, attack_range, filler)
                return
        fill_move(current_x, current_y, max_move, filler)
        return filler

    def color_tiles(self, filler):
        width = len(filler[0])
        for y in range(len(filler)):
            for x in range(width):
                tile = filler[y][x]
                if tile > 0:
                    self.tiles[y][x].change_tint(utils.BLUE_TINT)
                elif tile < 0:
                    self.tiles[y][x].change_tint(utils.RED_TINT)

    def color_attack_tiles(self, attack_range):
        filler = self.generate_empty_array()
        self.fill_attacks(self.current_x, self.current_y, attack_range + 1, filler) # change this to current
        self.color_tiles(filler)
        return filler
    
    def find_enemies_in_range(self, filler):
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
            x_coordinate, y_coordinate = destination_x, destination_y
            path = []
            path.append((x_coordinate, y_coordinate))
            while x_coordinate != self.selected_x or y_coordinate != self.selected_y:
                tile_values = check(x_coordinate, y_coordinate)
                # Retrives largest value and retrieves its tile coordinates
                new_coordinates = coord_dict[tile_values.index(max(tile_values))](x_coordinate, y_coordinate)
                path.append(new_coordinates[:])
                x_coordinate, y_coordinate = new_coordinates
            path.reverse()
            return path
        return "outside of range"
    
    def draw_path(self, path):
        for point in path:
            self.tiles[point[1]][point[0]].change_tint(utils.GREEN_TINT)
            
    def path_testing(self):
        self.reset_tiles()
        self.draw_range(self.test_character)
        path = self.path_finder(self.current_x, self.current_y, self.current_moves) # change this to current
        if type(path) != str: # add bounds conditions
            self.draw_path(path)
            
    def reset_unit(self):
        self.selected_unit = None
        self.attack_view = None
        self.selected_enemy = None
        self.available_enemies = []

    def testing(self):
        print ('Step')
        print(self.current_x, self.current_y)
        print(self.starting_x, self.starting_y)
        
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
                        self.current_moves = self.draw_range(character)
                        self.selected_unit = character
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
                    if self.current_moves[self.current_y][self.current_x] > 0: # change to current
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
                    self.tiles[self.current_y][self.current_x].set_character(self.selected_unit)
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
    # Testing method     
    # def character_move(self):
    #     self.tiles[self.current_y][self.current_x].set_character(self.test_character)
    #     self.tiles[self.current_y][self.current_x].change_tint(utils.BLUE_TINT)
    #     self.color_tiles(self.move_finder(self.current_x, self.current_y, 3, 1))
    def draw_range(self, character):
        moves = self.move_finder(self.selected_x, self.selected_y, 8, 1)
        self.color_tiles(moves)
        return moves
    
    def camera_bounds(self, direction):
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
        elif direction == key.RIGHT:
            right_edge_check = self.current_x == len(self.tiles[0]) - 2
            if not right_edge_check and camera_x_position >= self.screen_tile_width - 1:
                #self.current_x += 1
                if self.starting_x + self.screen_tile_width < len(self.tiles[0]) - 1:
                    self.starting_x += 1
                if self.starting_x + self.screen_tile_width <= len(self.tiles[0]) - 1:
                    # remove original starting column
                    self.remove_tiles_from_batch([tiles[self.starting_x - 1] for tiles in self.tiles])
                    # add column just beyond previous edge of the screen
                    self.add_tiles_to_batch([tiles[self.starting_x + self.screen_tile_width] for tiles in self.tiles])
        elif direction == key.UP:
            upper_edge_check = self.starting_y == len(self.tiles) - 2
            if not upper_edge_check and camera_y_position >= self.screen_tile_height - 1:
                #self.current_y += 1
                if self.starting_y + self.screen_tile_height < len(self.tiles) - 1:
                    self.starting_y += 1
                if self.starting_y + self.screen_tile_height <= len(self.tiles) - 1:
                    #self.starting_y += 1
                    self.remove_tiles_from_batch([tile for tile in self.tiles[self.starting_y - 1]])
                    self.add_tiles_to_batch([tile for tile in self.tiles[self.starting_y + self.screen_tile_height]])
                else:
                    return
        elif direction == key.DOWN:
            bottom_edge_check = self.starting_y == 0
            if not bottom_edge_check and camera_y_position <= 1:# or camera_y_position == 1 or camera_y_position == self.screen_tile_height:
                #self.current_y -= 1
                self.starting_y -= 1
                self.remove_tiles_from_batch([tile for tile in self.tiles[self.starting_y + self.screen_tile_height + 1]])
                self.add_tiles_to_batch([tile for tile in self.tiles[self.starting_y]])
        offset_x = 0
        offset_y = 0
        for y in range(self.screen_tile_height + 1):
            for x in range(self.screen_tile_width + 1):
                self.tiles[y + self.starting_y][x + self.starting_x].shift_tile(offset_x, offset_y)
                offset_x += utils.TILE_SIZE * utils.TILE_SCALE
            offset_x = 0
            offset_y += utils.TILE_SIZE * utils.TILE_SCALE
            
    def bounds(self, list, index):
        if index == len(list):
            return index - 1
        if index < 0:
            return 0
        return index
    
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
        self.current_x += change_x
        self.current_y += change_y
        self.reset_tiles()
        self.tiles[self.current_y][self.current_x].change_tint(utils.GREEN_TINT)

if __name__ == '__main__':
    window = Window()
    if CONTINUOUS_ARROWS:
        window.push_handlers(window.key_handler)
        pyglet.clock.schedule_interval(window.check_arrow_keys, 1/10)
    pyglet.app.run()

