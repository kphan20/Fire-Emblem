import pyglet
import pyglet
from pyglet.window import key
from game import resources
from utils import *
#Make config object for window
#pyglet.options['search_local_libs'] = True
source = resources.source
source.play()
class StartingScreen(pyglet.sprite.Sprite):
    def __init__(self, img):
        super().__init__(img=img)
class StartingMenu(pyglet.sprite.Sprite):
    def __init__(self):
        super().__init__(img=resources.player_image)
class Character(pyglet.sprite.Sprite):
    def __init__(self, img, batch, group):
        super().__init__(img=img, batch=batch, group=group)
class Tile(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, batch, group):
        super().__init__(img=img, x=x, y=y, batch=batch, group=group)
        self.scale= TILE_SCALE
        self.character = None
        self.arrow = None
    def change_tint(self, color):
        self.color = color
    def set_character(self, character):
        self.character = character
        self.character.position = (self.x, self.y)
    def draw(self):
        super().draw()
        self.character.draw()
class TileScreen():
    def __init__(self, batch):
        batch.draw()

class Window(pyglet.window.Window):
    def __init__(self):
        super().__init__(fullscreen=True)#width=500, height=500)
        starting_image = resources.starting_screen
        starting_image.width, starting_image.height = self.get_size()
        self.current_screen = None#StartingScreen(img=starting_image)
        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)
        offset_x = 100
        offset_y = 100
        self.tiles=[]
        for x in range(5):
            row = []
            for y in range(5):
                row.append(Tile(resources.tile, offset_x, offset_y, self.batch, group=self.background))
                offset_x += TILE_SIZE * TILE_SCALE
            offset_x = 100
            offset_y += TILE_SIZE * TILE_SCALE
            self.tiles.append(row)
        self.current_x= 0
        self.current_y = 0
        #self.characters = []
        self.test_character = Character(resources.player_image, self.batch, self.foreground)
        self.tiles[self.current_x][self.current_y].set_character(self.test_character)

    def move_finder(self, current_x, current_y, max_move, attack_range):
        #assuming rectangular map
        width = len(self.tiles[0])
        height = len(self.tiles)
        filler = [[0 for x in range(width)] for x in range(height)]
        self.fill_move(current_x, current_y, max_move, filler)
        #self.fill_attacks(current_x, current_y, attack_range, filler)
        return filler
    def reset_tiles(self):
        for y in range(len(self.tiles)):
            for x in range(len(self.tiles[0])):
                self.tiles[y][x].change_tint(NORMAL_TINT)
    def color_tiles(self, filler):
        width = len(filler[0])
        for y in range(len(filler)):
            for x in range(width):
                if filler[y][x] > 0:
                    self.tiles[y][x].change_tint(BLUE_TINT)
                elif filler[y][x] < 0:
                    self.tiles[y][x].change_tint(RED_TINT)
    def fill_move(self, current_x, current_y, maxMove, filler):
        if current_x < 0 or current_x > len(filler[0]) or current_y < 0 or current_y > len(filler):
            return
        try:
            if filler[current_y][current_x] < maxMove:
                filler[current_y][current_x] = maxMove
        except:
            print(current_x)
            print(current_y)
        if maxMove == 1:
            return
        self.fill_move(current_x + 1, current_y, maxMove - 1, filler)
        self.fill_move(current_x - 1, current_y, maxMove - 1, filler)
        self.fill_move(current_x, current_y + 1, maxMove - 1, filler)
        self.fill_move(current_x, current_y - 1, maxMove - 1, filler)
    def fill_attacks(self, current_x, current_y, attack_range, filler):
        if current_x < 0 or current_x > len(filler[0]) or current_y < 0 or current_y > len(filler):
            return
        if filler[current_y][current_x] == 1:
            self.attack_helper(current_x + 1, current_y, attack_range, filler)
            self.attack_helper(current_x - 1, current_y, attack_range, filler)
            self.attack_helper(current_x, current_y + 1, attack_range, filler)
            self.attack_helper(current_x, current_y - 1, attack_range, filler)
        else:
            self.fill_attacks(current_x + 1, current_y, attack_range, filler)
            self.fill_attacks(current_x - 1, current_y, attack_range, filler)
            self.fill_attacks(current_x, current_y + 1, attack_range, filler)
            self.fill_attacks(current_x, current_y - 1, attack_range, filler)
    def attack_helper(self, current_x, current_y, attack_range, filler):
        if attack_range == 0 or current_x < 0 or current_x > len(filler[0]) or current_y < 0 or current_y > len(filler):
            return
        if filler[current_y][current_x] == 0 or (filler[current_y][current_x] < 0 and filler[current_y][current_x] > -attack_range):
            filler[current_y][current_x] = -attack_range
            self.attack_helper(current_x + 1, current_y, attack_range - 1, filler)
            self.attack_helper(current_x - 1, current_y, attack_range - 1, filler)
            self.attack_helper(current_x, current_y + 1, attack_range - 1, filler)
            self.attack_helper(current_x, current_y - 1, attack_range - 1, filler)
    
    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        if self.current_screen:
            if symbol==key.RIGHT:
                print('success')
            if symbol==key.E:
                if isinstance(self.current_screen, StartingScreen):
                    self.current_screen=StartingMenu()
                    # self.clear()
                    # self.current_screen.draw()
                    return
                if isinstance(self.current_screen, StartingMenu):
                    self.current_screen=None#Tile(img=resources.tile, x=100,y=100, batch=self.batch)#TileScreen(self.batch)
        else:
            if symbol==key.RIGHT:
                self.reset_tiles()
                self.tiles[self.current_y][self.current_x].character = None
                self.current_x += 1
                self.current_x = self.bounds(self.tiles[self.current_y], self.current_x)
                self.character_move()
            if symbol==key.LEFT:
                self.reset_tiles()
                self.tiles[self.current_y][self.current_x].character = None
                self.current_x -= 1
                self.current_x = self.bounds(self.tiles[self.current_y], self.current_x)
                self.character_move()
            if symbol==key.UP:
                self.reset_tiles()
                self.tiles[self.current_y][self.current_x].character = None
                self.current_y += 1
                self.current_y = self.bounds(self.tiles, self.current_y)
                self.character_move()
            if symbol==key.DOWN:
                self.reset_tiles()
                self.tiles[self.current_y][self.current_x].character = None
                self.current_y -= 1
                self.current_y = self.bounds(self.tiles, self.current_y)
                self.character_move()
    def character_move(self):
        self.tiles[self.current_y][self.current_x].set_character(self.test_character)
        self.tiles[self.current_y][self.current_x].change_tint(BLUE_TINT)
        self.color_tiles(self.move_finder(self.current_x, self.current_y, 3, 1))
    def bounds(self, list, index):
        if index == len(list):
            return 0
        if index < 0:
            return len(list) - 1
        return index
    def on_draw(self):
        self.clear()
        self.batch.draw()
        # if self.current_screen:
        #     self.current_screen.draw()
        # else:
        #     self.batch.draw()
        #self.test.draw()

if __name__ == '__main__':
    window = Window()
    pyglet.app.run()

