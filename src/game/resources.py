import pyglet
from os import listdir
from utils import TILE_SIZE

#executes from intro.py directory location, not resources.py
pyglet.resource.path = ['../resources']
pyglet.resource.reindex()

# Retrieves base images from folder
images = listdir('../resources/characters')
tilesets = listdir('../resources/terrain')
menu_items = listdir('../resources/menu')

# Stores resources related to the menus
circle_animation = pyglet.resource.animation('menu/spinningcircle.gif')

# Current player placeholder image
player_image = pyglet.resource.image('characters/' + images[0])

# Creates tileset grid
tileset = pyglet.resource.image('terrain/' + tilesets[0])
tileset_grid = pyglet.image.ImageGrid(tileset, 32, 32)
tileset_texture_grid = tileset_grid.get_texture_sequence()
testing_grid = tileset_texture_grid[960]

# Alternative method of retrieving tile sprite from tileset
tile = tileset.get_region(x=TILE_SIZE * 10, y=TILE_SIZE * 20, width=TILE_SIZE, height=TILE_SIZE)
tile2 = tileset.get_region(x=TILE_SIZE * 20, y =TILE_SIZE * 5, width = TILE_SIZE, height=TILE_SIZE)

# Other testing resources
starting_screen = pyglet.resource.image('maxresdefault.jpg')
source = pyglet.resource.media('music/01-Fire-Emblem-Theme.mp3')

animations = listdir('../resources/animation')
frames = [pyglet.resource.image('animation/' + animations[x]) for x in range(len(animations))]
animation = pyglet.image.Animation.from_image_sequence(frames, duration=0.1, loop=True)