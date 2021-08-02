import pyglet
from pyglet.libs.win32.constants import INFINITE
from pyglet.window import key
from game import resources
import utils
import math
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
class WeaponClass():
    pass
class Stats():
    """Can double as growths object"""
    __slots__=('level', 'hp', 'str', 'skl', 'spd', 'lck', 'def_', 'res', 'con', 'mov')
    def __init__(self, level, hp, str, skl, spd, lck, def_, res, con, mov):
        self.level = level
        self.hp = hp
        self.str = str
        self.skl = skl
        self.spd = spd
        self.lck = lck
        self.def_ = def_
        self.res = res
        self.con = con
        self.mov = mov
        
class Character(pyglet.sprite.Sprite):
    def __init__(self, img, batch, group, team=0):
        super().__init__(img=img, batch=batch, group=group)
        
        
        # Used for game classes (eg. paladin, assassin, etc.)
        self.class_type = Class({0: 1, 1: 3})
        # Can be pulled from class_type
        self.valid_weapons = []
        
        # Individual based stats
        #self.battle_sprite = pyglet.sprite.Sprite() # used for battle animation
        self.stats = {}
        self.weapons = []
        self.growths = {}
        self.team = team # Probably use ints for team numbers
        self.carried_unit = None

class Class:
    __slots__ =('terrain_cost')
    def __init__(self, terrain_cost):
        self.terrain_cost = terrain_cost

class TileScreen():
    def __init__(self, batch):
        batch.draw()
def four_direction_decorator(func):
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
        starting_image = resources.starting_screen
        starting_image.width, starting_image.height = self.get_size()
        self.current_screen = StartingScreen(img=starting_image)
        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        self.tiles=utils.generate_map_tiles(self.batch, self.background)
        print(self.tiles[5][5].tile_type)
        self.current_x= 0
        self.current_y = 0
        #self.characters = []
        self.test_character = Character(resources.player_image, self.batch, self.foreground)
        self.test_character2 = Character(resources.player_image, self.batch, self.foreground, 1)
        self.test_character3 = Character(resources.player_image, self.batch, self.foreground, 1)
        self.tiles[self.current_x][self.current_y].set_character(self.test_character)
        self.tiles[5][4].set_character(self.test_character2)
        self.tiles[0][4].set_character(self.test_character3)
        self.character_view = False
        self.current_moves = None
        self.selected_x = 0
        self.selected_y = 0
    def reset_tiles(self):
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                self.tiles[y][x].change_tint(utils.NORMAL_TINT)
    def move_finder(self, current_x, current_y, max_move, attack_range):
        #assuming rectangular map
        width = len(self.tiles[0])
        height = len(self.tiles)
        filler = [[0 for x in range(width)] for x in range(height)]
        terrain_cost = self.test_character.class_type.terrain_cost
        # Sets first square to large value to prevent backtracking to start square
        max_move += 1
        filler[current_y][current_x] = max_move
        @four_direction_decorator
        def fill_move(current_x, current_y, max_move, filler):
            if current_x < 0 or current_x >= len(filler[0]) or current_y < 0 or current_y >= len(filler):
                return
            if self.tiles[current_y][current_x].character and self.tiles[current_y][current_x].character.team != 0:
                max_move = 0
            else:
                move_cost = terrain_cost[self.tiles[current_y][current_x].tile_type]
                max_move = max_move - move_cost
            if filler[current_y][current_x] >= max_move and filler[current_y][current_x] > 0:
                return
            if max_move > 0:
                filler[current_y][current_x] = max_move
                fill_move(current_x, current_y, max_move, filler)
            else:
                fill_attacks(current_x, current_y, attack_range, filler)
                return
        def fill_attacks(current_x, current_y, attack_range, filler):
            if attack_range <= 0 or current_x < 0 or current_x >= len(filler[0]) or current_y < 0 or current_y >= len(filler):
                return
            if filler[current_y][current_x] <= 0 and filler[current_y][current_x] > -attack_range:
                filler[current_y][current_x] = -attack_range
                fill_attacks(current_x + 1, current_y, attack_range - 1, filler)
                fill_attacks(current_x - 1, current_y, attack_range - 1, filler)
                fill_attacks(current_x, current_y + 1, attack_range - 1, filler)
                fill_attacks(current_x, current_y - 1, attack_range - 1, filler)
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
            while x_coordinate != self.current_x or y_coordinate != self.current_y:
                tile_values = check(x_coordinate, y_coordinate)
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
        path = self.path_finder(self.selected_x, self.selected_y, self.current_moves)
        if type(path) != str:
            self.draw_path(path)
        print(path)
    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        coord_dict = {key.RIGHT: lambda x, y: (x + 1, y),
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
            if symbol==key.E:
                character = self.tiles[self.current_y][self.current_x].character
                if character:
                    self.current_moves = self.draw_range(self.test_character)
                    self.selected_x, self.selected_y = self.current_x, self.current_y
                    self.character_view = True
                return
            if symbol == key.Q:
                self.character_view = False
                self.reset_tiles()
                return
            if coord_dict.get(symbol):
                if self.character_view:
                    self.selected_x, self.selected_y = coord_dict[symbol](self.selected_x, self.selected_y)
                    self.path_testing()
                else:
                    self.reset_tiles()
                    self.current_x, self.current_y = coord_dict[symbol](self.current_x, self.current_y)
                    self.current_x = self.bounds(self.tiles[self.current_y], self.current_x)
                    self.tiles[self.current_y][self.current_x].change_tint(utils.GREEN_TINT)
                return
                    
    def character_move(self):
        self.tiles[self.current_y][self.current_x].set_character(self.test_character)
        self.tiles[self.current_y][self.current_x].change_tint(utils.BLUE_TINT)
        
        self.color_tiles(self.move_finder(self.current_x, self.current_y, 3, 1))
    def draw_range(self, character):
        moves = self.move_finder(self.current_x, self.current_y, 8, 1)
        self.color_tiles(moves)
        return moves
    def bounds(self, list, index):
        if index == len(list):
            return 0
        if index < 0:
            return len(list) - 1
        return index
    def on_draw(self):
        self.clear()
        #self.batch.draw()
        if self.current_screen:
            self.current_screen.draw()
        else:
            self.batch.draw()
        #self.test.draw()

if __name__ == '__main__':
    window = Window()
    pyglet.app.run()

