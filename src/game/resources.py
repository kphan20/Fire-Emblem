import pyglet
from os import listdir


# executes from intro.py directory location, not resources.py
pyglet.resource.path = ["../resources"]
pyglet.resource.reindex()

# Retrieves base images from folder
images = listdir("../resources/characters")
tilesets = listdir("../resources/terrain")
menu_items = listdir("../resources/menu")

# Stores resources related to the menus
circle_animation = pyglet.resource.animation("menu/startmenubackground.gif")

# Current player placeholder image
player_image = pyglet.resource.image("characters/eliwoodpromoted.png")

# Creates tileset grid
tileset = pyglet.resource.image("terrain/" + tilesets[0])
tileset_grid = pyglet.image.ImageGrid(tileset, 32, 32)
tileset_texture_grid = tileset_grid.get_texture_sequence()
testing_grid = tileset_texture_grid[960]

# Other testing resources
starting_screen = pyglet.resource.animation("menu/resizedtitlescreen.gif")
# starting_screen = pyglet.resource.image("maxresdefault.jpg")
source = pyglet.resource.media("music/01-Fire-Emblem-Theme.mp3")

eliwood_animations = listdir("../resources/animation/eliwood attack")
frames = [
    pyglet.resource.image("animation/eliwood attack/" + file_name)
    for file_name in eliwood_animations
]
eliwood_animation = pyglet.image.Animation.from_image_sequence(
    frames, duration=0.1, loop=True
)

tile_selector = listdir("../resources/animation/tile selector")
frames = [
    pyglet.resource.image("animation/tile selector/" + file_name)
    for file_name in tile_selector
]
tile_selector_animation = pyglet.image.Animation.from_image_sequence(
    frames, duration=0.2, loop=True
)

tile_selector = listdir("../resources/animation/tile selector attack")
frames = [
    pyglet.resource.image("animation/tile selector attack/" + file_name)
    for file_name in tile_selector
]
tile_selector_attack_animation = pyglet.image.Animation.from_image_sequence(
    frames, duration=0.2, loop=True
)

path_arrows = listdir("../resources/gameplayui/patharrows")
path_arrows_dict = dict(
    (name.split(".")[0], pyglet.resource.image(f"gameplayui/patharrows/{name}"))
    for name in path_arrows
)
for image in path_arrows_dict.values():
    print(type(image))

menu_option = pyglet.resource.image("menu/menu option.png")
# Alternative method of retrieving tile sprite from tileset
# from utils import TILE_SIZE
# tile = tileset.get_region(x=TILE_SIZE * 10, y=TILE_SIZE * 20, width=TILE_SIZE, height=TILE_SIZE)
# tile2 = tileset.get_region(x=TILE_SIZE * 20, y =TILE_SIZE * 5, width = TILE_SIZE, height=TILE_SIZE)

overworld = pyglet.resource.image("characters/eliwoodoverworld.png")
overworld_seq = pyglet.image.ImageGrid(overworld, 3, 1)
overworld_anim = pyglet.image.Animation.from_image_sequence(overworld_seq, duration=0.5)

combat_menu = pyglet.resource.image("gameplayui/combat_info.png")

menu_hand = pyglet.resource.image("gameplayui/menu_hand.png")

unit_menu = pyglet.resource.image("gameplayui/test4.png")

carry_box = pyglet.resource.image("gameplayui/carry_box.png")
