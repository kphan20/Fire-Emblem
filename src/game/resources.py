import pyglet
from os import listdir
from utils import TILE_SIZE

#executes from intro.py directory location, not resources.py
pyglet.resource.path = ['../resources']
pyglet.resource.reindex()

images = listdir('../resources/characters')
tilesets = listdir('../resources/terrain')
print(images)
player_image = pyglet.resource.image('characters/' + images[0])
tileset = pyglet.resource.image('terrain/' + tilesets[0])

tile = tileset.get_region(x=TILE_SIZE * 10, y=TILE_SIZE * 20, width=TILE_SIZE, height=TILE_SIZE)

starting_screen = pyglet.resource.image('maxresdefault.jpg')
source = pyglet.resource.media('music/01-Fire-Emblem-Theme.mp3')