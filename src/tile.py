from pyglet import sprite
from utils import TILE_SIZE

class Tile:
    def __init__(self, img,x, y, batch=None):
        self.sprite = sprite.Sprite(img=img,x=x, y=y, batch=batch)
        self.sprite.scale = 14